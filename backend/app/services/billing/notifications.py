import logging
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from app.models.notifications import Notification
from app.models.enums import NotificationType, NotificationStatus
from app.models.auth import User

logger = logging.getLogger(__name__)


class BillingNotifications:
    """
    Billing & Credit Event Notification Handler.
    Creates in-app notification alerts for payment receipts, credit limits, and subscription changes.
    """

    @staticmethod
    def send_payment_success_notification(db: Session, user_id: UUID, plan_name: str, amount: float) -> None:
        notification = Notification(
            user_id=user_id,
            title="Payment Successful",
            message=f"Thank you! Your payment of ${amount:.2f} for the {plan_name} Plan has been processed.",
            type=NotificationType.MILESTONE,
            status=NotificationStatus.UNREAD
        )
        db.add(notification)
        db.commit()

    @staticmethod
    def send_low_credit_notification(db: Session, user_id: UUID, remaining_credits: int) -> None:
        notification = Notification(
            user_id=user_id,
            title="Low AI Credit Balance",
            message=f"You have {remaining_credits} AI credits remaining. Upgrade your plan to unlock more AI credits.",
            type=NotificationType.AI,
            status=NotificationStatus.UNREAD
        )
        db.add(notification)
        db.commit()

    @staticmethod
    def send_past_due_notification(db: Session, user_id: UUID) -> None:
        notification = Notification(
            user_id=user_id,
            title="Subscription Payment Failed",
            message="Your latest subscription payment failed. Please update your payment method to maintain uninterrupted service.",
            type=NotificationType.ALERT,
            status=NotificationStatus.UNREAD
        )
        db.add(notification)
        db.commit()
