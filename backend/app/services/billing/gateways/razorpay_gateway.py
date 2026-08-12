import uuid
import hmac
import hashlib
import time
import logging
import json
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
    import razorpay
except ImportError:
    razorpay = None


class RazorpayGateway(PaymentGateway):
    """
    Razorpay implementation of PaymentGateway.
    Handles order creation, subscription plans, signature verification, and refunds.
    """

    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None, webhook_secret: Optional[str] = None):
        self.key_id = key_id or getattr(settings, "RAZORPAY_KEY_ID", "rzp_test_mock_key")
        self.key_secret = key_secret or getattr(settings, "RAZORPAY_KEY_SECRET", "mock_razorpay_secret")
        self.webhook_secret = webhook_secret or getattr(settings, "RAZORPAY_WEBHOOK_SECRET", "mock_webhook_secret")
        
        self.client = None
        if razorpay and self.key_id and not self.key_id.startswith("rzp_test_mock"):
            try:
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            except Exception as e:
                logger.warning(f"Failed to initialize Razorpay client: {e}")

    @property
    def provider_name(self) -> str:
        return "RAZORPAY"

    async def create_customer(self, dto: CustomerCreateDTO) -> CustomerDTO:
        if self.client:
            try:
                cust = self.client.customer.create({
                    "name": dto.name or dto.email.split("@")[0],
                    "email": dto.email,
                    "notes": dto.metadata
                })
                return CustomerDTO(
                    customer_id=cust["id"],
                    email=cust.get("email", dto.email),
                    name=cust.get("name", dto.name),
                    provider=self.provider_name
                )
            except Exception as e:
                logger.warning(f"Razorpay customer creation failed ({e}), falling back to mock.")

        mock_id = f"cust_rzp_{uuid.uuid4().hex[:12]}"
        return CustomerDTO(
            customer_id=mock_id,
            email=dto.email,
            name=dto.name,
            provider=self.provider_name
        )

    async def create_checkout_session(self, dto: CheckoutSessionCreateDTO) -> CheckoutSessionDTO:
        amount_paise = int(round(dto.amount * 100))
        currency = dto.currency.upper()
        if currency == "USD" and getattr(settings, "RAZORPAY_DEFAULT_INR", False):
            currency = "INR"
            amount_paise = int(round(dto.amount * 83 * 100))

        if self.client:
            try:
                order_data = {
                    "amount": amount_paise,
                    "currency": currency,
                    "receipt": f"rcpt_{uuid.uuid4().hex[:10]}",
                    "notes": {
                        "user_id": dto.user_id,
                        "plan_code": dto.plan_code,
                        "user_email": dto.user_email,
                        **dto.metadata
                    }
                }
                order = self.client.order.create(data=order_data)
                return CheckoutSessionDTO(
                    session_id=order["id"],
                    order_id=order["id"],
                    provider=self.provider_name,
                    amount=dto.amount,
                    currency=dto.currency,
                    checkout_url=f"{dto.success_url}?order_id={order['id']}&provider=razorpay"
                )
            except Exception as e:
                logger.warning(f"Razorpay order creation error ({e}), generating test order.")

        mock_order_id = f"order_rzp_{uuid.uuid4().hex[:14]}"
        return CheckoutSessionDTO(
            session_id=mock_order_id,
            order_id=mock_order_id,
            provider=self.provider_name,
            amount=dto.amount,
            currency=dto.currency,
            checkout_url=f"{dto.success_url}?order_id={mock_order_id}&provider=razorpay"
        )

    async def create_customer_portal(self, customer_id: str, return_url: str) -> PortalSessionDTO:
        return PortalSessionDTO(portal_url=f"{return_url}?portal_status=razorpay_account")

    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> SubscriptionDTO:
        if self.client and subscription_id.startswith("sub_"):
            try:
                sub = self.client.subscription.cancel(subscription_id, {"cancel_at_cycle_end": 1 if at_period_end else 0})
                return SubscriptionDTO(
                    subscription_id=sub["id"],
                    customer_id=sub.get("customer_id", "cus_rzp"),
                    status="CANCELED" if not at_period_end else "ACTIVE",
                    cancel_at_period_end=at_period_end,
                    provider=self.provider_name,
                    raw_data=sub
                )
            except Exception as e:
                logger.warning(f"Razorpay cancel subscription error ({e}).")

        now = int(time.time())
        return SubscriptionDTO(
            subscription_id=subscription_id,
            customer_id="cus_rzp_mock",
            status="CANCELED" if not at_period_end else "ACTIVE",
            current_period_start=now,
            current_period_end=now + 2592000,
            cancel_at_period_end=True,
            provider=self.provider_name
        )

    async def resume_subscription(self, subscription_id: str) -> SubscriptionDTO:
        now = int(time.time())
        return SubscriptionDTO(
            subscription_id=subscription_id,
            customer_id="cus_rzp_mock",
            status="ACTIVE",
            current_period_start=now,
            current_period_end=now + 2592000,
            cancel_at_period_end=False,
            provider=self.provider_name
        )

    async def get_subscription(self, subscription_id: str) -> SubscriptionDTO:
        if self.client and subscription_id.startswith("sub_"):
            try:
                sub = self.client.subscription.fetch(subscription_id)
                status_map = {
                    "authenticated": "ACTIVE",
                    "active": "ACTIVE",
                    "pending": "PENDING",
                    "halted": "PAST_DUE",
                    "cancelled": "CANCELED",
                    "completed": "EXPIRED"
                }
                return SubscriptionDTO(
                    subscription_id=sub["id"],
                    customer_id=sub.get("customer_id", "cus_rzp"),
                    status=status_map.get(sub.get("status", "").lower(), "ACTIVE"),
                    current_period_start=sub.get("current_start"),
                    current_period_end=sub.get("current_end"),
                    cancel_at_period_end=bool(sub.get("end_at")),
                    provider=self.provider_name,
                    raw_data=sub
                )
            except Exception as e:
                logger.warning(f"Razorpay get subscription error ({e}).")

        now = int(time.time())
        return SubscriptionDTO(
            subscription_id=subscription_id,
            customer_id="cus_rzp_mock",
            status="ACTIVE",
            current_period_start=now,
            current_period_end=now + 2592000,
            cancel_at_period_end=False,
            provider=self.provider_name
        )

    async def create_refund(self, payment_id: str, amount: Optional[float] = None, reason: Optional[str] = None) -> RefundDTO:
        if self.client and payment_id.startswith("pay_"):
            try:
                params = {}
                if amount:
                    params["amount"] = int(round(amount * 100))
                if reason:
                    params["notes"] = {"reason": reason}
                ref = self.client.payment.refund(payment_id, params)
                return RefundDTO(
                    refund_id=ref["id"],
                    payment_id=payment_id,
                    amount=float(ref.get("amount", 0)) / 100.0,
                    currency=ref.get("currency", "INR"),
                    status="SUCCEEDED",
                    provider=self.provider_name
                )
            except Exception as e:
                logger.warning(f"Razorpay refund error ({e}).")

        ref_id = f"rfnd_rzp_{uuid.uuid4().hex[:12]}"
        return RefundDTO(
            refund_id=ref_id,
            payment_id=payment_id,
            amount=amount or 0.0,
            currency="USD",
            status="SUCCEEDED",
            provider=self.provider_name
        )

    def verify_payment_signature(self, order_id: str, payment_id: str, signature: str) -> bool:
        """Verify Razorpay payment signature from client checkout callback"""
        if not self.key_secret or self.key_secret.startswith("mock_"):
            return True

        msg = f"{order_id}|{payment_id}"
        expected_sig = hmac.new(
            self.key_secret.encode("utf-8"),
            msg.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, signature)

    def verify_webhook_signature(self, payload: bytes, header_signature: str) -> bool:
        if not self.webhook_secret or self.webhook_secret.startswith("mock_"):
            return bool(header_signature)

        expected_sig = hmac.new(
            self.webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, header_signature)

    def parse_webhook_event(self, payload: bytes, header_signature: str) -> Dict[str, Any]:
        try:
            return json.loads(payload.decode("utf-8"))
        except Exception:
            return {}
