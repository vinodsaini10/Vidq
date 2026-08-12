import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.dependencies.auth import require_role
from app.models.user import User, UserRole
from app.models.billing import (
    Plan, PlanFeature, Subscription, Payment, Invoice, Refund, Coupon, UsageRecord
)
from app.models.admin import WebhookEvent
from app.models.enums import SubscriptionStatus, PaymentStatus, InvoiceStatus
from app.schemas.billing import (
    PlanResponseSchema,
    CouponCreateRequestSchema,
    RefundRequestSchema,
    RefundResponseSchema,
)
from app.services.billing.gateways import get_payment_gateway

logger = logging.getLogger(__name__)

router = APIRouter()
require_admin = require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])


# ==========================================
# 1. PLAN MANAGEMENT
# ==========================================

@router.get("/plans", response_model=List[PlanResponseSchema], dependencies=[Depends(require_admin)])
async def admin_list_plans(db: AsyncSession = Depends(get_db)):
    """List all plans including inactive plans for admin management"""
    result = await db.execute(select(Plan).order_by(Plan.display_order.asc()))
    return result.scalars().all()


@router.post("/plans", response_model=PlanResponseSchema, dependencies=[Depends(require_admin)])
async def admin_create_plan(
    name: str,
    code: str,
    price_monthly: float,
    price_yearly: float,
    ai_credits_monthly: int = 500,
    max_channels: int = 3,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription plan"""
    res = await db.execute(select(Plan).where(Plan.code == code))
    if res.scalars().first():
        raise HTTPException(status_code=400, detail=f"Plan code '{code}' already exists.")

    plan = Plan(
        name=name,
        code=code,
        price_monthly=price_monthly,
        price_yearly=price_yearly,
        ai_credits_monthly=ai_credits_monthly,
        max_channels=max_channels,
        description=description,
        is_active=True
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.patch("/plans/{plan_id}", dependencies=[Depends(require_admin)])
async def admin_update_plan(
    plan_id: UUID,
    name: Optional[str] = None,
    price_monthly: Optional[float] = None,
    price_yearly: Optional[float] = None,
    ai_credits_monthly: Optional[int] = None,
    max_channels: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """Update plan details or pricing"""
    res = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = res.scalars().first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if name is not None:
        plan.name = name
    if price_monthly is not None:
        plan.price_monthly = price_monthly
    if price_yearly is not None:
        plan.price_yearly = price_yearly
    if ai_credits_monthly is not None:
        plan.ai_credits_monthly = ai_credits_monthly
    if max_channels is not None:
        plan.max_channels = max_channels
    if is_active is not None:
        plan.is_active = is_active

    await db.commit()
    await db.refresh(plan)
    return {"status": "success", "plan_id": str(plan.id), "name": plan.name}


# ==========================================
# 2. SUBSCRIPTIONS & REVENUE METRICS
# ==========================================

@router.get("/subscriptions", dependencies=[Depends(require_admin)])
async def admin_list_subscriptions(
    status_filter: Optional[str] = Query(None, alias="status"),
    provider_filter: Optional[str] = Query(None, alias="provider"),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List system-wide user subscriptions with pagination & filtering"""
    query = select(Subscription)
    if status_filter:
        query = query.where(Subscription.status == status_filter.upper())
    if provider_filter:
        query = query.where(Subscription.provider == provider_filter.upper())

    query = query.order_by(Subscription.created_at.desc()).limit(limit).offset(offset)
    res = await db.execute(query)
    subs = res.scalars().all()

    items = []
    for s in subs:
        items.append({
            "id": str(s.id),
            "user_id": str(s.user_id),
            "plan_code": s.plan.code if s.plan else "free",
            "plan_name": s.plan.name if s.plan else "Free",
            "status": s.status.value,
            "provider": s.provider,
            "price": float(s.price),
            "current_period_end": s.current_period_end.isoformat() if s.current_period_end else None,
            "cancel_at_period_end": s.cancel_at_period_end
        })

    return {"subscriptions": items, "count": len(items)}


@router.get("/revenue", dependencies=[Depends(require_admin)])
async def admin_revenue_analytics(db: AsyncSession = Depends(get_db)):
    """
    Revenue Analytics: MRR, ARR, active paid subscribers, total volume processed.
    """
    # Total active paid subscriptions
    res_subs = await db.execute(
        select(Subscription).where(
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
        )
    )
    active_subs = res_subs.scalars().all()

    mrr = sum(
        float(s.price) if s.billing_interval == "month" else float(s.price) / 12.0
        for s in active_subs if s.price > 0
    )
    arr = mrr * 12.0

    # Total succeeded payments sum
    res_payments = await db.execute(
        select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.SUCCEEDED)
    )
    total_revenue = res_payments.scalar() or 0.0

    # Active subscribers by plan code
    plan_counts = {}
    for s in active_subs:
        code = s.plan.code if s.plan else "free"
        plan_counts[code] = plan_counts.get(code, 0) + 1

    return {
        "mrr": round(mrr, 2),
        "arr": round(arr, 2),
        "total_revenue": round(float(total_revenue), 2),
        "active_paid_subscribers": len([s for s in active_subs if s.price > 0]),
        "total_active_subscribers": len(active_subs),
        "subscribers_by_plan": plan_counts
    }


# ==========================================
# 3. PAYMENTS, REFUNDS, & COUPONS
# ==========================================

@router.get("/payments", dependencies=[Depends(require_admin)])
async def admin_list_payments(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """List recent system payment records"""
    res = await db.execute(select(Payment).order_by(Payment.created_at.desc()).limit(limit).offset(offset))
    return res.scalars().all()


@router.post("/refunds", response_model=RefundResponseSchema, dependencies=[Depends(require_admin)])
async def admin_issue_refund(req: RefundRequestSchema, db: AsyncSession = Depends(get_db)):
    """Issue a full or partial refund via payment gateway"""
    res_pay = await db.execute(select(Payment).where(Payment.id == UUID(req.payment_id)))
    payment = res_pay.scalars().first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found.")

    gateway = get_payment_gateway(payment.provider)
    pay_id_str = payment.stripe_payment_intent_id or payment.razorpay_payment_id or str(payment.id)

    refund_dto = await gateway.create_refund(
        payment_id=pay_id_str,
        amount=req.amount,
        reason=req.reason
    )

    refund = Refund(
        payment_id=payment.id,
        provider_refund_id=refund_dto.refund_id,
        amount=refund_dto.amount,
        currency=refund_dto.currency,
        status=refund_dto.status,
        reason=req.reason
    )
    db.add(refund)
    payment.status = PaymentStatus.REFUNDED
    await db.commit()

    return RefundResponseSchema(
        refund_id=refund_dto.refund_id,
        payment_id=str(payment.id),
        amount=refund_dto.amount,
        currency=refund_dto.currency,
        status=refund_dto.status
    )


@router.get("/coupons", dependencies=[Depends(require_admin)])
async def admin_list_coupons(db: AsyncSession = Depends(get_db)):
    """List promotional coupons"""
    res = await db.execute(select(Coupon).order_by(Coupon.created_at.desc()))
    return res.scalars().all()


@router.post("/coupons", dependencies=[Depends(require_admin)])
async def admin_create_coupon(req: CouponCreateRequestSchema, db: AsyncSession = Depends(get_db)):
    """Create a new promotional discount coupon"""
    code_clean = req.code.strip().upper()
    res = await db.execute(select(Coupon).where(Coupon.code == code_clean))
    if res.scalars().first():
        raise HTTPException(status_code=400, detail=f"Coupon code '{code_clean}' already exists.")

    coupon = Coupon(
        code=code_clean,
        name=req.name,
        discount_type=req.discount_type.upper(),
        discount_percent=req.discount_percent,
        discount_amount=req.discount_amount,
        currency=req.currency.upper(),
        duration=req.duration.upper(),
        max_redemptions=req.max_redemptions,
        min_purchase_amount=req.min_purchase_amount,
        valid_until=req.valid_until,
        is_active=True
    )
    db.add(coupon)
    await db.commit()
    await db.refresh(coupon)
    return coupon


@router.get("/webhooks", dependencies=[Depends(require_admin)])
async def admin_list_webhooks(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """List recent received provider webhook events log"""
    res = await db.execute(select(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(limit))
    return res.scalars().all()
