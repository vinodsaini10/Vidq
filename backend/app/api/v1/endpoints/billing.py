import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.billing import get_current_subscription
from app.models.user import User
from app.models.billing import Plan, Subscription, Payment, Invoice, UsageRecord, Coupon
from app.models.enums import SubscriptionStatus, PaymentStatus, InvoiceStatus
from app.schemas.billing import (
    PlanResponseSchema,
    SubscriptionResponseSchema,
    CheckoutSessionRequestSchema,
    CheckoutSessionResponseSchema,
    PortalSessionRequestSchema,
    PortalSessionResponseSchema,
    CancelSubscriptionRequestSchema,
    ChangePlanRequestSchema,
    CouponValidateRequestSchema,
    CouponValidateResponseSchema,
    PaymentResponseSchema,
    InvoiceResponseSchema,
    TopUpCreditsRequest,
)
from app.services.billing.subscription_service import SubscriptionService
from app.services.billing.entitlement_service import EntitlementService
from app.services.billing.coupon_service import CouponService
from app.services.billing.usage_service import UsageService
from app.services.ai.credits import CreditSystem

logger = logging.getLogger(__name__)

router = APIRouter()


# ==========================================
# 1. PUBLIC & PRICING PLANS
# ==========================================

@router.get("/plans", response_model=List[PlanResponseSchema])
async def list_plans(db: AsyncSession = Depends(get_db)):
    """List all active subscription plans with features and limits"""
    result = await db.execute(
        select(Plan).where(Plan.is_active == True).order_by(Plan.display_order.asc())
    )
    plans = result.scalars().all()
    if not plans:
        # Fallback trigger seed
        await db.run_sync(EntitlementService.ensure_default_plans)
        result = await db.execute(
            select(Plan).where(Plan.is_active == True).order_by(Plan.display_order.asc())
        )
        plans = result.scalars().all()
    return plans


# ==========================================
# 2. CURRENT SUBSCRIPTION & ENTITLEMENTS
# ==========================================

@router.get("/subscription")
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve current active subscription, plan capabilities, usage limits, and credit balance"""
    summary = await db.run_sync(lambda sync_db: EntitlementService.get_entitlements_summary(sync_db, current_user.id))
    return summary


@router.get("/current-plan")
async def get_current_plan(
    current_user: User = Depends(get_current_user),
    subscription: Subscription = Depends(get_current_subscription)
):
    """Legacy route compatibility for active plan details"""
    plan = subscription.plan
    rem_credits = current_user.ai_credits_max - current_user.ai_credits_used
    return {
        "activePlan": plan.name if plan else "Free",
        "planCode": plan.code if plan else "free",
        "creditsUsed": current_user.ai_credits_used,
        "creditsMax": current_user.ai_credits_max,
        "creditsRemaining": max(0, rem_credits),
        "status": subscription.status.value,
        "nextBillingDate": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        "priceMonthly": float(plan.price_monthly) if plan else 0.00
    }


# ==========================================
# 3. CHECKOUT & CUSTOMER PORTAL
# ==========================================

@router.post("/checkout", response_model=CheckoutSessionResponseSchema)
async def create_checkout_session(
    req: CheckoutSessionRequestSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a Stripe or Razorpay checkout session for subscription subscription or plan change"""
    try:
        res = await SubscriptionService.create_checkout_session(
            db=db,
            user=current_user,
            plan_code=req.plan_code,
            billing_interval=req.billing_interval,
            provider=req.provider,
            coupon_code=req.coupon_code,
            success_url=req.success_url or "http://localhost:3000/billing?status=success",
            cancel_url=req.cancel_url or "http://localhost:3000/billing?status=cancelled"
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Checkout error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initiate payment checkout")


@router.post("/portal", response_model=PortalSessionResponseSchema)
async def create_customer_portal(
    req: PortalSessionRequestSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate customer management portal link (Stripe / Razorpay)"""
    res = await SubscriptionService.create_portal_session(
        db=db,
        user=current_user,
        return_url=req.return_url or "http://localhost:3000/billing",
        provider=req.provider
    )
    return res


# ==========================================
# 4. SUBSCRIPTION MANAGEMENT
# ==========================================

@router.post("/cancel")
async def cancel_subscription(
    req: CancelSubscriptionRequestSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel subscription at period end or immediately"""
    try:
        sub = await SubscriptionService.cancel_subscription(
            db=db,
            user_id=current_user.id,
            at_period_end=req.at_period_end,
            reason=req.reason
        )
        return {
            "status": "success",
            "message": "Subscription cancellation scheduled at period end." if req.at_period_end else "Subscription canceled immediately.",
            "subscription_id": str(sub.id),
            "cancel_at_period_end": sub.cancel_at_period_end
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/resume")
async def resume_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resume a canceled or pending-cancellation subscription"""
    try:
        sub = await SubscriptionService.resume_subscription(db=db, user_id=current_user.id)
        return {
            "status": "success",
            "message": "Subscription resumed successfully.",
            "subscription_id": str(sub.id)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/change-plan")
async def change_plan(
    req: ChangePlanRequestSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade or downgrade subscription plan"""
    try:
        res = await SubscriptionService.create_checkout_session(
            db=db,
            user=current_user,
            plan_code=req.new_plan_code,
            billing_interval=req.billing_interval,
            provider="STRIPE"
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# 5. PAYMENTS & INVOICES
# ==========================================

@router.get("/payments", response_model=List[PaymentResponseSchema])
async def list_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List payment transaction history"""
    result = await db.execute(
        select(Payment).where(Payment.user_id == current_user.id).order_by(Payment.created_at.desc())
    )
    return result.scalars().all()


@router.get("/invoices", response_model=List[InvoiceResponseSchema])
async def list_invoices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List billing invoices with PDF download links"""
    result = await db.execute(
        select(Invoice).where(Invoice.user_id == current_user.id).order_by(Invoice.created_at.desc())
    )
    return result.scalars().all()


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponseSchema)
async def get_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve single invoice by ID"""
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
    )
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


# ==========================================
# 6. USAGE & CREDITS
# ==========================================

@router.get("/usage")
async def get_usage_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get usage limits and current consumption breakdown"""
    summary = await db.run_sync(lambda sync_db: UsageService.get_user_usage_summary(sync_db, current_user.id))
    return summary


@router.post("/coupons/validate", response_model=CouponValidateResponseSchema)
async def validate_coupon(
    req: CouponValidateRequestSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate promotional coupon code"""
    val_res = await db.run_sync(
        lambda sync_db: CouponService.validate_coupon(sync_db, req.code, req.purchase_amount, current_user.id)
    )
    return CouponValidateResponseSchema(
        is_valid=val_res.is_valid,
        discount_amount=val_res.discount_amount,
        message=val_res.message,
        code=req.code if val_res.is_valid else None,
        discount_type=val_res.coupon.discount_type if val_res.is_valid and val_res.coupon else None
    )


@router.post("/topup")
async def topup_credits(
    req: TopUpCreditsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Top-up AI credit balance"""
    res = await db.run_sync(
        lambda sync_db: CreditSystem.allocate_credits(
            sync_db,
            user_id=current_user.id,
            amount=req.amount,
            reason="Manual credit top-up"
        )
    )
    return {
        "status": "success",
        "addedCredits": req.amount,
        "newBalance": res["remaining_credits"]
    }
