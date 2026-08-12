from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PlanFeatureSchema(BaseModel):
    feature_code: str
    feature_name: str
    enabled: bool
    value_limit: Optional[str] = None
    period: Optional[str] = None


class PlanResponseSchema(BaseModel):
    id: str
    name: str
    code: str
    description: Optional[str] = None
    price_monthly: float
    price_yearly: float
    currency: str
    billing_interval: str
    trial_days: int
    ai_credits_monthly: int
    max_channels: int
    is_active: bool
    display_order: int
    features: List[PlanFeatureSchema] = []

    class Config:
        from_attributes = True


class SubscriptionResponseSchema(BaseModel):
    id: str
    user_id: str
    plan_id: Optional[str] = None
    status: str
    provider: str
    price: float
    currency: str
    billing_interval: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool
    canceled_at: Optional[datetime] = None
    plan: Optional[PlanResponseSchema] = None

    class Config:
        from_attributes = True


class CheckoutSessionRequestSchema(BaseModel):
    plan_code: str
    billing_interval: str = Field(default="month", description="month or year")
    provider: str = Field(default="STRIPE", description="STRIPE or RAZORPAY")
    coupon_code: Optional[str] = None
    success_url: Optional[str] = "http://localhost:3000/billing?status=success"
    cancel_url: Optional[str] = "http://localhost:3000/billing?status=cancelled"


class CheckoutSessionResponseSchema(BaseModel):
    session_id: str
    checkout_url: Optional[str] = None
    order_id: Optional[str] = None
    client_secret: Optional[str] = None
    provider: str
    plan: Dict[str, Any]


class PortalSessionRequestSchema(BaseModel):
    provider: str = "STRIPE"
    return_url: Optional[str] = "http://localhost:3000/billing"


class PortalSessionResponseSchema(BaseModel):
    portal_url: str


class CancelSubscriptionRequestSchema(BaseModel):
    at_period_end: bool = True
    reason: Optional[str] = None


class ChangePlanRequestSchema(BaseModel):
    new_plan_code: str
    billing_interval: str = "month"


class CouponValidateRequestSchema(BaseModel):
    code: str
    purchase_amount: float


class CouponValidateResponseSchema(BaseModel):
    is_valid: bool
    discount_amount: float
    message: str
    code: Optional[str] = None
    discount_type: Optional[str] = None


class CouponCreateRequestSchema(BaseModel):
    code: str
    name: str
    discount_type: str = Field(default="PERCENT", description="PERCENT or FIXED")
    discount_percent: Optional[int] = None
    discount_amount: Optional[float] = None
    currency: str = "USD"
    duration: str = Field(default="ONETIME", description="ONETIME or RECURRING")
    max_redemptions: Optional[int] = None
    min_purchase_amount: Optional[float] = None
    valid_until: Optional[datetime] = None


class PaymentResponseSchema(BaseModel):
    id: str
    user_id: str
    amount: float
    currency: str
    status: str
    provider: str
    payment_method: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceItemSchema(BaseModel):
    description: str
    amount: float
    quantity: int
    currency: str


class InvoiceResponseSchema(BaseModel):
    id: str
    invoice_number: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    currency: str
    status: str
    paid_at: Optional[datetime] = None
    invoice_pdf_url: Optional[str] = None
    items: List[InvoiceItemSchema] = []

    class Config:
        from_attributes = True


class RefundRequestSchema(BaseModel):
    payment_id: str
    amount: Optional[float] = None
    reason: Optional[str] = None


class RefundResponseSchema(BaseModel):
    refund_id: str
    payment_id: str
    amount: float
    currency: str
    status: str


class PlanUpgradeRequest(BaseModel):
    plan_id: str


class TopUpCreditsRequest(BaseModel):
    amount: int
