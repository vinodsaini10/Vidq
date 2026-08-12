import logging
from fastapi import APIRouter, Request, Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.billing.webhook_processor import WebhookProcessor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint for Stripe payment events (checkout completed, payment succeeded, etc.)
    """
    if not stripe_signature:
        stripe_signature = "mock_stripe_signature"

    payload_bytes = await request.body()

    success, message = await db.run_sync(
        lambda sync_db: WebhookProcessor.process_webhook_event(
            db=sync_db,
            provider="STRIPE",
            payload_bytes=payload_bytes,
            header_signature=stripe_signature
        )
    )

    if not success and "Invalid signature" in message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return {"status": "ok", "message": message}


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None, alias="x-razorpay-signature"),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint for Razorpay payment events (order.paid, payment.authorized, etc.)
    """
    if not x_razorpay_signature:
        x_razorpay_signature = "mock_razorpay_signature"

    payload_bytes = await request.body()

    success, message = await db.run_sync(
        lambda sync_db: WebhookProcessor.process_webhook_event(
            db=sync_db,
            provider="RAZORPAY",
            payload_bytes=payload_bytes,
            header_signature=x_razorpay_signature
        )
    )

    if not success and "Invalid signature" in message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return {"status": "ok", "message": message}
