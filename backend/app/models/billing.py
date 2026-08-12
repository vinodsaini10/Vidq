import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Integer, Numeric, ForeignKey, JSON, DateTime, Enum as SQLEnum, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel
from app.models.enums import SubscriptionStatus, PaymentStatus, InvoiceStatus


class Plan(BaseModel):
    __tablename__ = "plans"

    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False, index=True)  # free, starter, pro, business, enterprise
    description = Column(Text, nullable=True)
    price_monthly = Column(Numeric(12, 2), default=0.00, nullable=False)
    price_yearly = Column(Numeric(12, 2), default=0.00, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    billing_interval = Column(String(10), default="month", nullable=False)  # month, year
    trial_days = Column(Integer, default=0, nullable=False)
    ai_credits_monthly = Column(Integer, default=50, nullable=False)
    max_channels = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)

    features = relationship("PlanFeature", back_populates="plan", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="plan")


class PlanFeature(BaseModel):
    __tablename__ = "plan_features"

    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    feature_code = Column(String, nullable=False, index=True)
    feature_name = Column(String, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    value_limit = Column(String, nullable=True)  # e.g., "10", "unlimited", "true"
    unit = Column(String, nullable=True)  # e.g., "credits", "channels", "audits"
    period = Column(String, nullable=True)  # "monthly", "daily", "lifetime"

    plan = relationship("Plan", back_populates="features")


class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="SET NULL"), nullable=True)

    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.FREE, nullable=False, index=True)
    provider = Column(String, default="STRIPE", nullable=False)  # STRIPE, RAZORPAY, MANUAL
    stripe_customer_id = Column(String, nullable=True, index=True)
    stripe_subscription_id = Column(String, nullable=True, index=True)
    razorpay_customer_id = Column(String, nullable=True, index=True)
    razorpay_subscription_id = Column(String, nullable=True, index=True)

    price = Column(Numeric(12, 2), default=0.00, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    billing_interval = Column(String(10), default="month", nullable=False)

    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String, nullable=True)

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")


class PaymentCustomer(BaseModel):
    __tablename__ = "payment_customers"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    stripe_customer_id = Column(String, unique=True, nullable=True, index=True)
    razorpay_customer_id = Column(String, unique=True, nullable=True, index=True)
    email = Column(String, nullable=False)


class PaymentMethod(BaseModel):
    __tablename__ = "payment_methods"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String, default="STRIPE", nullable=False)
    stripe_payment_method_id = Column(String, nullable=True)
    razorpay_payment_method_id = Column(String, nullable=True)
    card_brand = Column(String, nullable=True)
    card_last4 = Column(String(4), nullable=True)
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)


class Payment(BaseModel):
    __tablename__ = "payments"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True)
    
    provider = Column(String, default="STRIPE", nullable=False)  # STRIPE, RAZORPAY
    stripe_payment_intent_id = Column(String, nullable=True, index=True)
    razorpay_payment_id = Column(String, nullable=True, index=True)
    razorpay_order_id = Column(String, nullable=True, index=True)
    razorpay_signature = Column(String, nullable=True)

    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = Column(String, nullable=True)  # card, netbanking, upi, etc.
    failure_reason = Column(String, nullable=True)
    metadata_json = Column(JSON, default={}, nullable=False)


class Invoice(BaseModel):
    __tablename__ = "invoices"

    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_number = Column(String, unique=True, nullable=False, index=True)
    
    subtotal = Column(Numeric(12, 2), default=0.00, nullable=False)
    tax_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    amount_due = Column(Numeric(12, 2), nullable=False)
    amount_paid = Column(Numeric(12, 2), default=0.00, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.PAID, nullable=False)
    
    invoice_pdf_url = Column(String, nullable=True)
    billing_period_start = Column(DateTime(timezone=True), nullable=True)
    billing_period_end = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)

    subscription = relationship("Subscription", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(BaseModel):
    __tablename__ = "invoice_items"

    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    invoice = relationship("Invoice", back_populates="items")


class Refund(BaseModel):
    __tablename__ = "refunds"

    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    provider_refund_id = Column(String, nullable=True, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String, default="SUCCEEDED", nullable=False)
    reason = Column(String, nullable=True)


class Coupon(BaseModel):
    __tablename__ = "coupons"

    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    discount_type = Column(String(10), default="PERCENT", nullable=False)  # PERCENT, FIXED
    discount_percent = Column(Integer, nullable=True)
    discount_amount = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    duration = Column(String(10), default="ONETIME", nullable=False)  # ONETIME, RECURRING
    max_redemptions = Column(Integer, nullable=True)
    redemptions_count = Column(Integer, default=0, nullable=False)
    min_purchase_amount = Column(Numeric(12, 2), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    redemptions = relationship("CouponRedemption", back_populates="coupon")


class CouponRedemption(BaseModel):
    __tablename__ = "coupon_redemptions"

    coupon_id = Column(UUID(as_uuid=True), ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    discount_applied = Column(Numeric(12, 2), nullable=False)
    redeemed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    coupon = relationship("Coupon", back_populates="redemptions")


class UsageLimit(BaseModel):
    __tablename__ = "usage_limits"

    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    metric_key = Column(String, nullable=False, index=True)  # ai_credits, youtube_channels, video_audits, keyword_searches
    limit_value = Column(Integer, nullable=False)  # -1 for unlimited
    period = Column(String, default="monthly", nullable=False)  # daily, monthly, lifetime
    unit = Column(String, default="units", nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)


class UsageRecord(BaseModel):
    __tablename__ = "usage_records"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_key = Column(String, nullable=False, index=True)
    units_used = Column(Integer, default=1, nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(JSON, default={}, nullable=False)
