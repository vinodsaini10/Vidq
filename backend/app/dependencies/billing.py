import logging
from typing import Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.billing import Subscription, Plan, PlanFeature, UsageRecord
from app.models.enums import SubscriptionStatus
from app.services.ai.credits import CreditSystem

logger = logging.getLogger(__name__)


async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Subscription:
    """Fetch user's current active subscription or default free subscription"""
    res = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING, SubscriptionStatus.FREE])
        ).order_by(Subscription.created_at.desc())
    )
    sub = res.scalars().first()
    if not sub:
        # Fallback query
        res = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id).order_by(Subscription.created_at.desc())
        )
        sub = res.scalars().first()

    if not sub:
        # Create default Free plan subscription
        res_plan = await db.execute(select(Plan).where(Plan.code == "free"))
        free_plan = res_plan.scalars().first()
        if not free_plan:
            free_plan = Plan(
                name="Free", code="free", description="Free tier",
                price_monthly=0.0, price_yearly=0.0, ai_credits_monthly=50, max_channels=1
            )
            db.add(free_plan)
            await db.flush()

        sub = Subscription(
            user_id=current_user.id,
            plan_id=free_plan.id,
            status=SubscriptionStatus.FREE,
            provider="MANUAL",
            price=0.0,
            currency="USD"
        )
        db.add(sub)
        await db.commit()

    return sub


async def require_active_subscription(
    subscription: Subscription = Depends(get_current_subscription)
) -> Subscription:
    """Guard dependency requiring an active or trialing subscription"""
    if subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING, SubscriptionStatus.FREE]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required. Please renew or upgrade your plan."
        )
    return subscription


def require_feature(feature_code: str):
    """Guard dependency checking feature permission on user's current plan"""
    async def feature_checker(
        current_user: User = Depends(get_current_user),
        subscription: Subscription = Depends(get_current_subscription),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        if not subscription.plan_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature_code}' requires a paid plan upgrade."
            )

        res = await db.execute(
            select(PlanFeature).where(
                PlanFeature.plan_id == subscription.plan_id,
                PlanFeature.feature_code == feature_code
            )
        )
        feat = res.scalars().first()
        if not feat or not feat.enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Your current plan ({subscription.plan.name if subscription.plan else 'Free'}) does not support '{feature_code}'. Please upgrade."
            )
        return current_user

    return feature_checker


def require_usage_limit(metric_key: str, units: int = 1):
    """Guard dependency enforcing usage limits before resource consumption"""
    async def limit_checker(
        current_user: User = Depends(get_current_user),
        subscription: Subscription = Depends(get_current_subscription),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        plan = subscription.plan
        if not plan:
            res_plan = await db.execute(select(Plan).where(Plan.code == "free"))
            plan = res_plan.scalars().first()

        max_limit = 100
        if metric_key in ["max_channels", "youtube_channels"] and plan:
            max_limit = plan.max_channels
        elif plan:
            res = await db.execute(
                select(PlanFeature).where(
                    PlanFeature.plan_id == plan.id,
                    PlanFeature.feature_code == metric_key
                )
            )
            feat = res.scalars().first()
            if not feat or not feat.enabled:
                max_limit = 0
            elif feat.value_limit in ["unlimited", "true", "-1"]:
                max_limit = -1
            else:
                try:
                    max_limit = int(feat.value_limit.split("_")[0])
                except Exception:
                    max_limit = 100

        if max_limit == -1:
            return current_user

        # Fetch recorded usage
        res_rec = await db.execute(
            select(UsageRecord).where(
                UsageRecord.user_id == current_user.id,
                UsageRecord.metric_key == metric_key
            )
        )
        rec = res_rec.scalars().first()
        current_usage = rec.units_used if rec else 0

        if (current_usage + units) > max_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Usage limit reached for {metric_key} ({current_usage}/{max_limit}). Upgrade your subscription for higher limits."
            )
        return current_user

    return limit_checker


def require_remaining_credits(min_credits: int = 1):
    """Guard dependency checking user's AI credits balance"""
    async def credit_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        balance_info = CreditSystem.get_balance_sync(db, current_user.id) if hasattr(CreditSystem, "get_balance_sync") else {"remaining_credits": current_user.ai_credits_max - current_user.ai_credits_used}
        rem = balance_info.get("remaining_credits", 0)
        if rem < min_credits:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient AI credits ({rem} remaining, {min_credits} required). Please top up or upgrade your subscription."
            )
        return current_user

    return credit_checker
