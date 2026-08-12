import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    async def send_welcome_email(self, email: str, full_name: str):
        logger.info(f"Sending welcome email to {email} ({full_name})")
        return True

    async def send_password_reset_email(self, email: str, reset_token: str):
        logger.info(f"Sending password reset token to {email}: {reset_token}")
        return True

    async def send_invoice_email(self, email: str, plan_name: str, amount: float):
        logger.info(f"Sending invoice email to {email} for {plan_name} (${amount})")
        return True


email_service = EmailService()
