from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class CustomerCreateDTO(BaseModel):
    email: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CustomerDTO(BaseModel):
    customer_id: str
    email: str
    name: Optional[str] = None
    provider: str


class CheckoutSessionCreateDTO(BaseModel):
    customer_id: Optional[str] = None
    user_id: str
    user_email: str
    plan_code: str
    plan_name: str
    amount: float
    currency: str = "USD"
    billing_interval: str = "month"  # month, year
    success_url: str
    cancel_url: str
    coupon_code: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CheckoutSessionDTO(BaseModel):
    session_id: str
    checkout_url: Optional[str] = None
    provider: str
    client_secret: Optional[str] = None
    order_id: Optional[str] = None  # Razorpay order ID
    amount: float
    currency: str


class PortalSessionDTO(BaseModel):
    portal_url: str


class PaymentIntentDTO(BaseModel):
    payment_intent_id: str
    client_secret: Optional[str] = None
    amount: float
    currency: str
    status: str
    provider: str


class SubscriptionDTO(BaseModel):
    subscription_id: str
    customer_id: str
    status: str
    current_period_start: Optional[int] = None
    current_period_end: Optional[int] = None
    cancel_at_period_end: bool = False
    provider: str
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class RefundDTO(BaseModel):
    refund_id: str
    payment_id: str
    amount: float
    currency: str
    status: str
    provider: str


class PaymentGateway(ABC):
    """
    Abstract Payment Gateway providing unified abstraction for Stripe, Razorpay, and Mock providers.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns provider string ('STRIPE', 'RAZORPAY', 'MOCK')"""
        pass

    @abstractmethod
    async def create_customer(self, dto: CustomerCreateDTO) -> CustomerDTO:
        """Create a payment customer record with the provider"""
        pass

    @abstractmethod
    async def create_checkout_session(self, dto: CheckoutSessionCreateDTO) -> CheckoutSessionDTO:
        """Create a hosted or inline checkout session"""
        pass

    @abstractmethod
    async def create_customer_portal(self, customer_id: str, return_url: str) -> PortalSessionDTO:
        """Create a customer management portal session"""
        pass

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> SubscriptionDTO:
        """Cancel a subscription"""
        pass

    @abstractmethod
    async def resume_subscription(self, subscription_id: str) -> SubscriptionDTO:
        """Resume a canceled or pending-cancellation subscription"""
        pass

    @abstractmethod
    async def get_subscription(self, subscription_id: str) -> SubscriptionDTO:
        """Retrieve subscription status directly from provider"""
        pass

    @abstractmethod
    async def create_refund(self, payment_id: str, amount: Optional[float] = None, reason: Optional[str] = None) -> RefundDTO:
        """Process a refund for a payment"""
        pass

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, header_signature: str) -> bool:
        """Verify webhook signature from provider"""
        pass

    @abstractmethod
    def parse_webhook_event(self, payload: bytes, header_signature: str) -> Dict[str, Any]:
        """Parse raw webhook payload into standardized dict structure"""
        pass
