import logging
import json
import hashlib
from typing import Dict, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.admin import WebhookEvent
from app.models.auth import User
from app.models.billing import Subscription
from app.models.enums import SubscriptionStatus
from app.services.billing.gateways import get_payment_gateway
from app.services.billing.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


class WebhookProcessor:
    """
    Production Webhook Processing Engine with signature verification,
    event deduplication (idempotency), and provider event dispatching.
    """

    @staticmethod
    def process_webhook_event(
        db: Session,
        provider: str,
        payload_bytes: bytes,
        header_signature: str
    ) -> Tuple[bool, str]:
        provider_clean = provider.strip().upper()
        gateway = get_payment_gateway(provider_clean)

        # 1. Signature Verification
        if not gateway.verify_webhook_signature(payload_bytes, header_signature):
            logger.error(f"Invalid webhook signature for provider {provider_clean}")
            return False, "Invalid signature"

        # 2. Parse Event Payload
        event_dict = gateway.parse_webhook_event(payload_bytes, header_signature)
        if not event_dict:
            return False, "Failed to parse JSON payload"

        # 3. Deduplication / Idempotency Check
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        event_id = event_dict.get("id") or event_dict.get("event") or payload_hash

        existing_event = db.execute(
            select(WebhookEvent).where(
                WebhookEvent.event_type == str(event_dict.get("type") or event_dict.get("event") or "unknown"),
                WebhookEvent.provider == provider_clean,
                WebhookEvent.payload == event_dict
            )
        ).scalar_one_or_none()

        if existing_event and getattr(existing_event, "is_processed", False):
            logger.info(f"Duplicate webhook event {event_id} already processed. Skipping.")
            return True, "Event already processed (idempotent duplicate)"

        # Log incoming webhook
        we = WebhookEvent(
            event_type=str(event_dict.get("type") or event_dict.get("event") or "billing.event"),
            provider=provider_clean,
            payload=event_dict,
            is_processed=False
        )
        db.add(we)
        db.commit()

        # 4. Dispatch Provider Events
        try:
            if provider_clean == "STRIPE":
                WebhookProcessor._handle_stripe_event(db, event_dict)
            elif provider_clean == "RAZORPAY":
                WebhookProcessor._handle_razorpay_event(db, event_dict)

            we.is_processed = True
            db.add(we)
            db.commit()
            return True, "Event processed successfully"
        except Exception as e:
            logger.exception(f"Error processing webhook event {event_id}: {e}")
            db.rollback()
            return False, f"Internal error processing event: {str(e)}"

    @staticmethod
    def _handle_stripe_event(db: Session, event: Dict[str, Any]) -> None:
        event_type = event.get("type", "")
        data_obj = event.get("data", {}).get("object", {})

        logger.info(f"Handling Stripe webhook event: {event_type}")

        if event_type == "checkout.session.completed":
            user_id_str = data_obj.get("client_reference_id") or data_obj.get("metadata", {}).get("user_id")
            plan_code = data_obj.get("metadata", {}).get("plan_code", "starter")
            coupon_code = data_obj.get("metadata", {}).get("coupon_code")
            customer_id = data_obj.get("customer")
            sub_id = data_obj.get("subscription")
            amount_total = float(data_obj.get("amount_total", 0)) / 100.0
            payment_intent = data_obj.get("payment_intent")

            if user_id_str:
                from uuid import UUID
                SubscriptionService.activate_or_upgrade_subscription(
                    db=db,
                    user_id=UUID(user_id_str),
                    plan_code=plan_code,
                    provider="STRIPE",
                    provider_subscription_id=sub_id,
                    provider_customer_id=customer_id,
                    amount_paid=amount_total,
                    payment_intent_id=payment_intent,
                    coupon_code=coupon_code if coupon_code else None
                )

        elif event_type in ["invoice.payment_succeeded"]:
            customer_id = data_obj.get("customer")
            sub_id = data_obj.get("subscription")
            amount_paid = float(data_obj.get("amount_paid", 0)) / 100.0

            sub = db.execute(
                select(Subscription).where(Subscription.stripe_subscription_id == sub_id)
            ).scalar_one_or_none()

            if sub:
                plan = sub.plan
                plan_code = plan.code if plan else "starter"
                SubscriptionService.activate_or_upgrade_subscription(
                    db=db,
                    user_id=sub.user_id,
                    plan_code=plan_code,
                    provider="STRIPE",
                    provider_subscription_id=sub_id,
                    provider_customer_id=customer_id,
                    amount_paid=amount_paid
                )

        elif event_type in ["invoice.payment_failed"]:
            sub_id = data_obj.get("subscription")
            sub = db.execute(
                select(Subscription).where(Subscription.stripe_subscription_id == sub_id)
            ).scalar_one_or_none()
            if sub:
                sub.status = SubscriptionStatus.PAST_DUE
                db.commit()

        elif event_type in ["customer.subscription.deleted"]:
            sub_id = data_obj.get("id")
            sub = db.execute(
                select(Subscription).where(Subscription.stripe_subscription_id == sub_id)
            ).scalar_one_or_none()
            if sub:
                sub.status = SubscriptionStatus.CANCELED
                db.commit()

    @staticmethod
    def _handle_razorpay_event(db: Session, event: Dict[str, Any]) -> None:
        event_type = event.get("event", "")
        payload = event.get("payload", {})

        logger.info(f"Handling Razorpay webhook event: {event_type}")

        if event_type in ["order.paid", "payment.authorized", "payment.captured"]:
            payment_entity = payload.get("payment", {}).get("entity", {})
            notes = payment_entity.get("notes", {})
            user_id_str = notes.get("user_id")
            plan_code = notes.get("plan_code", "starter")
            amount_paid = float(payment_entity.get("amount", 0)) / 100.0
            payment_id = payment_entity.get("id")

            if user_id_str:
                from uuid import UUID
                SubscriptionService.activate_or_upgrade_subscription(
                    db=db,
                    user_id=UUID(user_id_str),
                    plan_code=plan_code,
                    provider="RAZORPAY",
                    provider_subscription_id=payment_entity.get("order_id"),
                    provider_customer_id=payment_entity.get("customer_id"),
                    amount_paid=amount_paid,
                    payment_intent_id=payment_id
                )

        elif event_type in ["subscription.charged"]:
            sub_entity = payload.get("subscription", {}).get("entity", {})
            sub_id = sub_entity.get("id")
            sub = db.execute(
                select(Subscription).where(Subscription.razorpay_subscription_id == sub_id)
            ).scalar_one_or_none()
            if sub:
                plan = sub.plan
                plan_code = plan.code if plan else "starter"
                SubscriptionService.activate_or_upgrade_subscription(
                    db=db,
                    user_id=sub.user_id,
                    plan_code=plan_code,
                    provider="RAZORPAY",
                    provider_subscription_id=sub_id,
                    amount_paid=float(sub.price)
                )

        elif event_type in ["subscription.cancelled", "subscription.completed"]:
            sub_entity = payload.get("subscription", {}).get("entity", {})
            sub_id = sub_entity.get("id")
            sub = db.execute(
                select(Subscription).where(Subscription.razorpay_subscription_id == sub_id)
            ).scalar_one_or_none()
            if sub:
                sub.status = SubscriptionStatus.CANCELED
                db.commit()
