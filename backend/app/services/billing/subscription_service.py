import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from app.models.billing import (
    Plan, Subscription, PaymentCustomer, Payment, Invoice, InvoiceItem, PaymentMethod
)
from app.models.auth import User
from app.models.enums import SubscriptionStatus, PaymentStatus, InvoiceStatus, UserRole
from app.services.billing.gateways import get_payment_gateway
from app.services.billing.gateways.base import CustomerCreateDTO, CheckoutSessionCreateDTO
from app.services.billing.entitlement_service import EntitlementService
from app.services.billing.coupon_service import CouponService
from app.services.billing.usage_service import UsageService
from app.services.ai.credits import CreditSystem

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    Core Billing, Payment & Subscription Management Engine.
    Handles payment checkout generation, subscription activation via verified provider response,
    plan upgrades/downgrades, dunning, invoices, and credit allocations.
    """

    @staticmethod
    def get_or_create_customer(db: Session, user: User, provider: str = "STRIPE") -> PaymentCustomer:
        """Fetch existing provider customer record or provision new customer with provider gateway"""
        cust = db.execute(
            select(PaymentCustomer).where(PaymentCustomer.user_id == user.id)
        ).scalar_one_or_none()

        if cust:
            return cust

        gateway = get_payment_gateway(provider)
        dto = CustomerCreateDTO(
            email=user.email,
            name=user.full_name or user.email.split("@")[0],
            metadata={"user_id": str(user.id)}
        )
        res = gateway.create_customer(dto)

        cust = PaymentCustomer(
            user_id=user.id,
            email=user.email,
            stripe_customer_id=res.customer_id if provider.upper() == "STRIPE" else None,
            razorpay_customer_id=res.customer_id if provider.upper() == "RAZORPAY" else None
        )
        db.add(cust)
        db.commit()
        db.refresh(cust)
        return cust

    @staticmethod
    async def create_checkout_session(
        db: Session,
        user: User,
        plan_code: str,
        billing_interval: str = "month",
        provider: str = "STRIPE",
        coupon_code: Optional[str] = None,
        success_url: str = "http://localhost:3000/billing?status=success",
        cancel_url: str = "http://localhost:3000/billing?status=cancelled"
    ) -> Dict[str, Any]:
        """Generate provider-backed checkout session without trusting client price"""
        plan = db.execute(select(Plan).where(Plan.code == plan_code)).scalar_one_or_none()
        if not plan:
            raise ValueError(f"Plan '{plan_code}' does not exist.")

        # Calculate exact server-side pricing
        price = float(plan.price_yearly) if billing_interval == "year" else float(plan.price_monthly)

        # Apply coupon if provided
        discount_amount = 0.0
        if coupon_code:
            val_res = CouponService.validate_coupon(db, coupon_code, price, user.id)
            if val_res.is_valid:
                discount_amount = val_res.discount_amount

        final_amount = max(0.0, round(price - discount_amount, 2))

        # Get or create customer
        cust = SubscriptionService.get_or_create_customer(db, user, provider)
        customer_id = cust.stripe_customer_id if provider.upper() == "STRIPE" else cust.razorpay_customer_id

        gateway = get_payment_gateway(provider)
        checkout_dto = CheckoutSessionCreateDTO(
            customer_id=customer_id,
            user_id=str(user.id),
            user_email=user.email,
            plan_code=plan.code,
            plan_name=plan.name,
            amount=final_amount,
            currency=plan.currency,
            billing_interval=billing_interval,
            success_url=success_url,
            cancel_url=cancel_url,
            coupon_code=coupon_code,
            metadata={
                "coupon_code": coupon_code or "",
                "discount_amount": str(discount_amount)
            }
        )

        res = await gateway.create_checkout_session(checkout_dto)
        return {
            "session_id": res.session_id,
            "checkout_url": res.checkout_url,
            "order_id": res.order_id,
            "client_secret": res.client_secret,
            "provider": provider.upper(),
            "plan": {
                "name": plan.name,
                "code": plan.code,
                "amount": final_amount,
                "original_price": price,
                "discount": discount_amount,
                "currency": plan.currency,
                "billing_interval": billing_interval
            }
        }

    @staticmethod
    async def create_portal_session(db: Session, user: User, return_url: str, provider: str = "STRIPE") -> Dict[str, str]:
        """Create customer portal for self-service subscription & invoice management"""
        cust = SubscriptionService.get_or_create_customer(db, user, provider)
        customer_id = cust.stripe_customer_id if provider.upper() == "STRIPE" else cust.razorpay_customer_id
        
        gateway = get_payment_gateway(provider)
        res = await gateway.create_customer_portal(customer_id or "cus_fallback", return_url)
        return {"portal_url": res.portal_url}

    @staticmethod
    def activate_or_upgrade_subscription(
        db: Session,
        user_id: UUID,
        plan_code: str,
        provider: str,
        provider_subscription_id: Optional[str] = None,
        provider_customer_id: Optional[str] = None,
        amount_paid: float = 0.0,
        billing_interval: str = "month",
        payment_intent_id: Optional[str] = None,
        coupon_code: Optional[str] = None
    ) -> Subscription:
        """
        Server-side source of truth for activating or upgrading a paid subscription.
        Called ONLY after verified webhook or signature verification.
        """
        plan = db.execute(select(Plan).where(Plan.code == plan_code)).scalar_one_or_none()
        if not plan:
            plan = EntitlementService.get_or_create_free_plan(db)

        now = datetime.now(timezone.utc)
        period_days = 365 if billing_interval == "year" else 30
        period_end = now + timedelta(days=period_days)

        sub = db.execute(
            select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.created_at.desc())
        ).scalar_one_or_none()

        if not sub:
            sub = Subscription(
                user_id=user_id,
                plan_id=plan.id,
                status=SubscriptionStatus.ACTIVE,
                provider=provider.upper(),
                stripe_customer_id=provider_customer_id if provider.upper() == "STRIPE" else None,
                stripe_subscription_id=provider_subscription_id if provider.upper() == "STRIPE" else None,
                razorpay_customer_id=provider_customer_id if provider.upper() == "RAZORPAY" else None,
                razorpay_subscription_id=provider_subscription_id if provider.upper() == "RAZORPAY" else None,
                price=plan.price_yearly if billing_interval == "year" else plan.price_monthly,
                currency=plan.currency,
                billing_interval=billing_interval,
                current_period_start=now,
                current_period_end=period_end,
                cancel_at_period_end=False
            )
            db.add(sub)
        else:
            sub.plan_id = plan.id
            sub.status = SubscriptionStatus.ACTIVE
            sub.provider = provider.upper()
            if provider.upper() == "STRIPE":
                if provider_customer_id:
                    sub.stripe_customer_id = provider_customer_id
                if provider_subscription_id:
                    sub.stripe_subscription_id = provider_subscription_id
            elif provider.upper() == "RAZORPAY":
                if provider_customer_id:
                    sub.razorpay_customer_id = provider_customer_id
                if provider_subscription_id:
                    sub.razorpay_subscription_id = provider_subscription_id

            sub.price = plan.price_yearly if billing_interval == "year" else plan.price_monthly
            sub.billing_interval = billing_interval
            sub.current_period_start = now
            sub.current_period_end = period_end
            sub.cancel_at_period_end = False
            sub.canceled_at = None

        db.flush()

        # Update User Role
        user = db.get(User, user_id)
        if user:
            if plan.code in ["pro", "business", "enterprise", "starter"]:
                user.role = UserRole.PREMIUM_USER
            elif plan.code == "free":
                user.role = UserRole.FREE_USER
            db.add(user)

        # Allocate AI Credits for the plan
        CreditSystem.allocate_credits(
            db=db,
            user_id=user_id,
            amount=plan.ai_credits_monthly,
            reason=f"Monthly plan allocation for {plan.name} ({billing_interval})"
        )

        # Record Payment Record
        if amount_paid > 0 or payment_intent_id:
            payment = Payment(
                user_id=user_id,
                subscription_id=sub.id,
                provider=provider.upper(),
                stripe_payment_intent_id=payment_intent_id if provider.upper() == "STRIPE" else None,
                razorpay_payment_id=payment_intent_id if provider.upper() == "RAZORPAY" else None,
                amount=amount_paid,
                currency=plan.currency,
                status=PaymentStatus.SUCCEEDED,
                payment_method="card"
            )
            db.add(payment)
            db.flush()

            # Generate Invoice
            inv_num = f"INV-{now.strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
            invoice = Invoice(
                subscription_id=sub.id,
                user_id=user_id,
                invoice_number=inv_num,
                subtotal=amount_paid,
                tax_amount=0.00,
                discount_amount=0.00,
                amount_due=0.00,
                amount_paid=amount_paid,
                total_amount=amount_paid,
                currency=plan.currency,
                status=InvoiceStatus.PAID,
                billing_period_start=now,
                billing_period_end=period_end,
                paid_at=now
            )
            db.add(invoice)
            db.flush()

            inv_item = InvoiceItem(
                invoice_id=invoice.id,
                description=f"{plan.name} Plan Subscription ({billing_interval})",
                amount=amount_paid,
                quantity=1,
                currency=plan.currency
            )
            db.add(inv_item)

        # Redeem coupon if applicable
        if coupon_code:
            coupon_res = CouponService.validate_coupon(db, coupon_code, float(plan.price_monthly), user_id)
            if coupon_res.is_valid and coupon_res.coupon:
                CouponService.redeem_coupon(db, coupon_res.coupon.id, user_id, coupon_res.discount_amount, sub.id)

        # Reset periodic usage records for the new billing cycle
        UsageService.reset_period_usage(db, user_id)

        db.commit()
        db.refresh(sub)
        logger.info(f"Successfully activated/upgraded subscription for user {user_id} to plan {plan.code}")
        return sub

    @staticmethod
    async def cancel_subscription(db: Session, user_id: UUID, at_period_end: bool = True, reason: Optional[str] = None) -> Subscription:
        """Cancel subscription with provider gateway and local DB update"""
        sub = EntitlementService.get_user_subscription(db, user_id)
        if not sub or sub.status in [SubscriptionStatus.CANCELED, SubscriptionStatus.FREE]:
            raise ValueError("No active paid subscription found to cancel.")

        sub_id = sub.stripe_subscription_id or sub.razorpay_subscription_id or str(sub.id)
        gateway = get_payment_gateway(sub.provider)

        await gateway.cancel_subscription(sub_id, at_period_end=at_period_end)

        sub.cancel_at_period_end = at_period_end
        sub.canceled_at = datetime.now(timezone.utc)
        sub.cancellation_reason = reason
        if not at_period_end:
            sub.status = SubscriptionStatus.CANCELED
            free_plan = EntitlementService.get_or_create_free_plan(db)
            sub.plan_id = free_plan.id

        db.commit()
        db.refresh(sub)
        logger.info(f"Canceled subscription for user {user_id} (at_period_end={at_period_end})")
        return sub

    @staticmethod
    async def resume_subscription(db: Session, user_id: UUID) -> Subscription:
        """Resume a canceled or pending-cancellation subscription"""
        sub = EntitlementService.get_user_subscription(db, user_id)
        if not sub or not sub.cancel_at_period_end:
            raise ValueError("Subscription is not pending cancellation.")

        sub_id = sub.stripe_subscription_id or sub.razorpay_subscription_id or str(sub.id)
        gateway = get_payment_gateway(sub.provider)

        await gateway.resume_subscription(sub_id)

        sub.cancel_at_period_end = False
        sub.canceled_at = None
        sub.status = SubscriptionStatus.ACTIVE

        db.commit()
        db.refresh(sub)
        logger.info(f"Resumed subscription for user {user_id}")
        return sub
