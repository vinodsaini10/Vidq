from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    plan_name = Column(String, default="Free Creator", nullable=False)  # Free Creator, Pro Creator, Agency Studio
    status = Column(String, default="active", nullable=False)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    price_per_month = Column(Float, default=0.0)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
