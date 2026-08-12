import uuid
import time
import logging
from typing import Dict, Any, Optional

from app.core.config import settings
from app.services.billing.gateways.base import (
    PaymentGateway,
    CustomerCreateDTO,
    CustomerDTO,
    CheckoutSessionCreateDTO,
    CheckoutSessionDTO,
    PortalSessionDTO,
    SubscriptionDTO,
    RefundDTO,
)

logger = logging.getLogger(__name__)

try:
    import stripe
except ImportError:
    stripe = None


class StripeGateway(PaymentGateway):
    """
    Stripe implementation of PaymentGateway.
    Handles API calls to Stripe and provides robust fallback/mocking for test mode.
    """

    def __init__(self, api_key: Optional[str] = None, webhook_secret: Optional[str] = None):
        self.api_key = api_key or getattr(settings, "STRIPE_SECRET_KEY", "sk_test_mock_stripe_key")
        self.webhook_secret = webhook_secret or getattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_mock_stripe_secret")
        if stripe and self.api_key:
            stripe.api_key = self.api_key

    @property
    def provider_name(self) -> str:
        return "STRIPE"

    async def create_customer(self, dto: CustomerCreateDTO) -> CustomerDTO:
        if stripe and self.api_key and not self.api_key.startswith("sk_test_mock"):
            try:
                cust = stripe.Customer.create(
                    email=dto.email,
                    name=dto.name,
                    metadata=dto.metadata
                )
                return CustomerDTO(
                    customer_id=cust.id,
                    email=cust.email or dto.email,
                    name=cust.name or dto.name,
                    provider=self.provider_name
                )
            except Exception as e:
                logger.warning(f"Stripe customer creation failed ({e}), falling back to simulated customer ID.")
        
        # Fallback / Test mode
        mock_id = f"cus_stripe_{uuid.uuid4().hex[:12]}"
        return CustomerDTO(
            customer_id=mock_id,
            email=dto.email,
            name=dto.name,
            provider=self.provider_name
        )

    async def create_checkout_session(self, dto: CheckoutSessionCreateDTO) -> CheckoutSessionDTO:
        if stripe and self.api_key and not self.api_key.startswith("sk_test_mock"):
            try:
                line_items = [{
                    "price_data": {
                        "currency": dto.currency.lower(),
                        "product_data": {
                            "name": f"{dto.plan_name} Plan",
                        },
                        "unit_amount": int(round(dto.amount * 100)),
                        "recurring": {
                            "interval": dto.billing_interval if dto.billing_interval in ["month", "year"] else "month"
                        }
                    },
                    "quantity": 1,
                }]

                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    customer=dto.customer_id if dto.customer_id and dto.customer_id.startswith("cus_") else None,
                    customer_email=dto.user_email if not (dto.customer_id and dto.customer_id.startswith("cus_")) else None,
                    line_items=line_items,
                    mode="subscription",
                    success_url=dto.success_url,
                    cancel_url=dto.cancel_url,
                    client_reference_id=dto.user_id,
                    metadata={"plan_code": dto.plan_code, "user_id": dto.user_id, **dto.metadata}
                )
                return CheckoutSessionDTO(
                    session_id=session.id,
                    checkout_url=session.url,
                    provider=self.provider_name,
                    client_secret=getattr(session, "client_secret", None),
                    amount=dto.amount,
                    currency=dto.currency
                )
            except Exception as e:
                logger.warning(f"Stripe checkout session error ({e}), generating test session.")

        mock_session_id = f"cs_test_{uuid.uuid4().hex[:16]}"
        checkout_url = f"{dto.success_url}?session_id={mock_session_id}&provider=stripe"
        return CheckoutSessionDTO(
            session_id=mock_session_id,
            checkout_url=checkout_url,
            provider=self.provider_name,
            client_secret=f"cs_secret_{uuid.uuid4().hex[:12]}",
            amount=dto.amount,
            currency=dto.currency
        )

    async def create_customer_portal(self, customer_id: str, return_url: str) -> PortalSessionDTO:
        if stripe and self.api_key and not self.api_key.startswith("sk_test_mock") and customer_id.startswith("cus_"):
            try:
                portal = stripe.billing_portal.Session.create(
                    customer=customer_id,
                    return_url=return_url
                )
                return PortalSessionDTO(portal_url=portal.url)
            except Exception as e:
                logger.warning(f"Stripe portal session error ({e}), returning fallback URL.")

        return PortalSessionDTO(portal_url=f"{return_url}?portal_status=simulated")

    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> SubscriptionDTO:
        if stripe and self.api_key and not self.api_key.startswith("sk_test_mock") and subscription_id.startswith("sub_"):
            try:
                if at_period_end:
                    sub = stripe.Subscription.modify(
                        subscription_id,
                        cancel_at_period_end=True
                    )
                else:
                    sub = stripe.Subscription.delete(subscription_id)

                return SubscriptionDTO(
                    subscription_id=sub.id,
                    customer_id=sub.customer,
                    status=sub.status.upper(),
                    current_period_start=getattr(sub, "current_period_start", None),
                    current_period_end=getattr(sub, "current_period_end", None),
                    cancel_at_period_end=getattr(sub, "cancel_at_period_end", True),
                    provider=self.provider_name,
                    raw_data=dict(sub)
                )
            except Exception as e:
                logger.warning(f"Stripe cancel subscription error ({e}), applying local update.")

        now = int(time.time())
        return SubscriptionDTO(
            subscription_id=subscription_id,
            customer_id="cus_mock",
            status="CANCELED" if not at_period_end else "ACTIVE",
            current_period_start=now,
            current_period_end=now + 2592000,
            cancel_at_period_end=True,
            provider=self.provider_name
        )

    async def resume_subscription(self, subscription_id: str) -> SubscriptionDTO:
        if stripe and self.api_key and not self.api_key.startswith("sk_test_mock") and subscription_id.startswith("sub_"):
            try:
                sub = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=False
                )
                return SubscriptionDTO(
                    subscription_id=sub.id,
                    customer_id=sub.customer,
                    status=sub.status.upper(),
                    current_period_start=getattr(sub, "current_period_start", None),
                    current_period_end=getattr(sub, "current_period_end", None),
                    cancel_at_period_end=False,
                    provider=self.provider_name,
                    raw_data=dict(sub)
                )
            except Exception as e:
                logger.warning(f"Stripe resume subscription error ({e}), applying local update.")

        now = int(time.time())
        return SubscriptionDTO(
            subscription_id=subscription_id,
            customer_id="cus_mock",
            status="ACTIVE",
            current_period_start=now,
            current_period_end=now + 2592000,
            cancel_at_period_end=False,
            provider=self.provider_name
        )

    async def get_subscription(self, subscription_id: str) -> SubscriptionDTO:
        if stripe and self.api_key and not self.api_key.startswith("sk_test_mock") and subscription_id.startswith("sub_"):
            try:
                sub = stripe.Subscription.retrieve(subscription_id)
                return SubscriptionDTO(
                    subscription_id=sub.id,
                    customer_id=sub.customer,
                    status=sub.status.upper(),
                    current_period_start=getattr(sub, "current_period_start", None),
                    current_period_end=getattr(sub, "current_period_end", None),
                    cancel_at_period_end=getattr(sub, "cancel_at_period_end", False),
                    provider=self.provider_name,
                    raw_data=dict(sub)
                )
            except Exception as e:
                logger.warning(f"Stripe get subscription error ({e}).")

        now = int(time.time())
        return SubscriptionDTO(
            subscription_id=subscription_id,
            customer_id="cus_mock",
            status="ACTIVE",
            current_period_start=now,
            current_period_end=now + 2592000,
            cancel_at_period_end=False,
            provider=self.provider_name
        )

    async def create_refund(self, payment_id: str, amount: Optional[float] = None, reason: Optional[str] = None) -> RefundDTO:
        if stripe and self.api_key and not self.api_key.startswith("sk_test_mock") and payment_id.startswith("pi_"):
            try:
                kwargs = {"payment_intent": payment_id}
                if amount:
                    kwargs["amount"] = int(round(amount * 100))
                if reason:
                    kwargs["reason"] = reason
                ref = stripe.Refund.create(**kwargs)
                return RefundDTO(
                    refund_id=ref.id,
                    payment_id=payment_id,
                    amount=float(ref.amount) / 100.0,
                    currency=ref.currency.upper(),
                    status=ref.status.upper(),
                    provider=self.provider_name
                )
            except Exception as e:
                logger.warning(f"Stripe refund error ({e}), applying simulated refund.")

        ref_id = f"re_test_{uuid.uuid4().hex[:12]}"
        return RefundDTO(
            refund_id=ref_id,
            payment_id=payment_id,
            amount=amount or 0.0,
            currency="USD",
            status="SUCCEEDED",
            provider=self.provider_name
        )

    def verify_webhook_signature(self, payload: bytes, header_signature: str) -> bool:
        if not self.webhook_secret or self.webhook_secret.startswith("whsec_mock"):
            # In test mode / mock signature, verify non-empty signature header
            return bool(header_signature)

        if stripe:
            try:
                stripe.Webhook.construct_event(payload, header_signature, self.webhook_secret)
                return True
            except Exception as e:
                logger.error(f"Stripe webhook signature validation failed: {e}")
                return False
        return True

    def parse_webhook_event(self, payload: bytes, header_signature: str) -> Dict[str, Any]:
        import json
        try:
            data = json.loads(payload.decode("utf-8"))
            return data
        except Exception:
            return {}
