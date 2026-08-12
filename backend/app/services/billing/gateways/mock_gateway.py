import uuid
import time
from typing import Dict, Any, Optional

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


class MockGateway(PaymentGateway):
    """
    Mock payment gateway for testing and offline development.
    """

    @property
    def provider_name(self) -> str:
        return "MOCK"

    async def create_customer(self, dto: CustomerCreateDTO) -> CustomerDTO:
        return CustomerDTO(
            customer_id=f"cus_mock_{uuid.uuid4().hex[:10]}",
            email=dto.email,
            name=dto.name,
            provider=self.provider_name
        )

    async def create_checkout_session(self, dto: CheckoutSessionCreateDTO) -> CheckoutSessionDTO:
        session_id = f"cs_mock_{uuid.uuid4().hex[:12]}"
        return CheckoutSessionDTO(
            session_id=session_id,
            checkout_url=f"{dto.success_url}?session_id={session_id}&provider=mock",
            provider=self.provider_name,
            client_secret=f"mock_secret_{uuid.uuid4().hex[:8]}",
            amount=dto.amount,
            currency=dto.currency
        )

    async def create_customer_portal(self, customer_id: str, return_url: str) -> PortalSessionDTO:
        return PortalSessionDTO(portal_url=f"{return_url}?portal=mock")

    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> SubscriptionDTO:
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
        return RefundDTO(
            refund_id=f"re_mock_{uuid.uuid4().hex[:10]}",
            payment_id=payment_id,
            amount=amount or 0.0,
            currency="USD",
            status="SUCCEEDED",
            provider=self.provider_name
        )

    def verify_webhook_signature(self, payload: bytes, header_signature: str) -> bool:
        return True

    def parse_webhook_event(self, payload: bytes, header_signature: str) -> Dict[str, Any]:
        import json
        try:
            return json.loads(payload.decode("utf-8"))
        except Exception:
            return {"type": "mock.event", "data": {}}
