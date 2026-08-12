import logging
import asyncio
from datetime import datetime, timedelta, timezone
from celery import shared_task
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.billing import Subscription
from app.models.enums import SubscriptionStatus
from app.services.billing.notifications import BillingNotifications
from app.services.billing.usage_service import UsageService
from app.services.billing.entitlement_service import EntitlementService
from app.services.ai.credits import CreditSystem

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.billing_celery_tasks.check_trial_expirations")
def check_trial_expirations():
    """
    Celery task running daily to check upcoming trial expirations.
    Notifies users 2 days before trial ends, and transitions expired trials to Free/Canceled.
    """
    async def _async_check():
        async with AsyncSessionLocal() as db:
            now = datetime.now(timezone.utc)
            in_two_days = now + timedelta(days=2)

            # 1. Upcoming trial expiration warning
            res_warn = await db.execute(
                select(Subscription).where(
                    Subscription.status == SubscriptionStatus.TRIALING,
                    Subscription.trial_end <= in_two_days,
                    Subscription.trial_end > now
                )
            )
            upcoming = res_warn.scalars().all()
            for sub in upcoming:
                logger.info(f"Trial expiring soon for user {sub.user_id}")

            # 2. Expired trials transition
            res_exp = await db.execute(
                select(Subscription).where(
                    Subscription.status == SubscriptionStatus.TRIALING,
                    Subscription.trial_end <= now
                )
            )
            expired = res_exp.scalars().all()
            for sub in expired:
                free_plan = await db.run_sync(EntitlementService.get_or_create_free_plan)
                sub.status = SubscriptionStatus.FREE
                sub.plan_id = free_plan.id
                db.add(sub)
                logger.info(f"Transitioned trial-expired user {sub.user_id} to Free plan")

            await db.commit()

    return asyncio.run(_async_check())


@shared_task(name="app.tasks.billing_celery_tasks.process_subscription_renewals")
def process_subscription_renewals():
    """
    Celery task to handle subscription renewal cycles, resetting usage limits and allocating monthly AI credits.
    """
    async def _async_renew():
        async with AsyncSessionLocal() as db:
            now = datetime.now(timezone.utc)
            res = await db.execute(
                select(Subscription).where(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.current_period_end <= now
                )
            )
            renewals = res.scalars().all()
            for sub in renewals:
                plan = sub.plan
                if plan:
                    # Allocate monthly credits
                    await db.run_sync(
                        lambda sync_db: CreditSystem.allocate_credits(
                            sync_db,
                            user_id=sub.user_id,
                            amount=plan.ai_credits_monthly,
                            reason=f"Monthly renewal credit allocation for {plan.name}"
                        )
                    )
                    # Reset period usage meters
                    await db.run_sync(
                        lambda sync_db: UsageService.reset_period_usage(sync_db, sub.user_id)
                    )

                    period_days = 365 if sub.billing_interval == "year" else 30
                    sub.current_period_start = now
                    sub.current_period_end = now + timedelta(days=period_days)
                    db.add(sub)
                    logger.info(f"Renewed subscription cycle for user {sub.user_id}")

            await db.commit()

    return asyncio.run(_async_renew())


@shared_task(name="app.tasks.billing_celery_tasks.check_past_due_subscriptions")
def check_past_due_subscriptions():
    """
    Celery task checking past-due subscriptions and issuing dunning notifications.
    """
    async def _async_past_due():
        async with AsyncSessionLocal() as db:
            res = await db.execute(
                select(Subscription).where(Subscription.status == SubscriptionStatus.PAST_DUE)
            )
            past_dues = res.scalars().all()
            for sub in past_dues:
                await db.run_sync(
                    lambda sync_db: BillingNotifications.send_past_due_notification(sync_db, sub.user_id)
                )

    return asyncio.run(_async_past_due())
