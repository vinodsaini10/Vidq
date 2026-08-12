import logging
from typing import Dict, Any, Optional, Tuple, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.billing import Plan, PlanFeature, Subscription, UsageLimit, UsageRecord
from app.models.auth import User
from app.models.enums import SubscriptionStatus
from app.services.ai.credits import CreditSystem

logger = logging.getLogger(__name__)


DEFAULT_PLANS_DATA = [
    {
        "name": "Free",
        "code": "free",
        "description": "Essential features for new YouTube creators",
        "price_monthly": 0.00,
        "price_yearly": 0.00,
        "trial_days": 0,
        "ai_credits_monthly": 50,
        "max_channels": 1,
        "display_order": 1,
        "features": [
            {"feature_code": "ai_tools", "feature_name": "Basic AI Generator", "enabled": True, "value_limit": "50_credits", "period": "monthly"},
            {"feature_code": "channel_sync", "feature_name": "Channel Sync", "enabled": True, "value_limit": "1", "period": "lifetime"},
            {"feature_code": "analytics", "feature_name": "Basic Analytics", "enabled": True, "value_limit": "7_days", "period": "lifetime"},
            {"feature_code": "video_audit", "feature_name": "Video Audit", "enabled": True, "value_limit": "3", "period": "monthly"},
            {"feature_code": "export", "feature_name": "Data Export", "enabled": False, "value_limit": "0", "period": "lifetime"},
        ]
    },
    {
        "name": "Starter",
        "code": "starter",
        "description": "For growing channels needing AI optimization",
        "price_monthly": 19.00,
        "price_yearly": 190.00,
        "trial_days": 7,
        "ai_credits_monthly": 500,
        "max_channels": 3,
        "display_order": 2,
        "features": [
            {"feature_code": "ai_tools", "feature_name": "Full AI Tools Access", "enabled": True, "value_limit": "500_credits", "period": "monthly"},
            {"feature_code": "channel_sync", "feature_name": "Multiple Channels", "enabled": True, "value_limit": "3", "period": "lifetime"},
            {"feature_code": "analytics", "feature_name": "Advanced Analytics", "enabled": True, "value_limit": "90_days", "period": "lifetime"},
            {"feature_code": "video_audit", "feature_name": "Video Audit", "enabled": True, "value_limit": "25", "period": "monthly"},
            {"feature_code": "competitor_tracking", "feature_name": "Competitor Tracking", "enabled": True, "value_limit": "3", "period": "lifetime"},
            {"feature_code": "export", "feature_name": "PDF & CSV Export", "enabled": True, "value_limit": "unlimited", "period": "lifetime"},
        ]
    },
    {
        "name": "Pro",
        "code": "pro",
        "description": "For full-time creators and professional channels",
        "price_monthly": 49.00,
        "price_yearly": 490.00,
        "trial_days": 14,
        "ai_credits_monthly": 2000,
        "max_channels": 10,
        "display_order": 3,
        "features": [
            {"feature_code": "ai_tools", "feature_name": "Unlimited AI Workflows", "enabled": True, "value_limit": "2000_credits", "period": "monthly"},
            {"feature_code": "channel_sync", "feature_name": "Channel Sync", "enabled": True, "value_limit": "10", "period": "lifetime"},
            {"feature_code": "analytics", "feature_name": "Historical Analytics", "enabled": True, "value_limit": "365_days", "period": "lifetime"},
            {"feature_code": "video_audit", "feature_name": "Video Audit", "enabled": True, "value_limit": "100", "period": "monthly"},
            {"feature_code": "competitor_tracking", "feature_name": "Competitor Tracking", "enabled": True, "value_limit": "10", "period": "lifetime"},
            {"feature_code": "bulk_automation", "feature_name": "Bulk AI Processing", "enabled": True, "value_limit": "true", "period": "lifetime"},
            {"feature_code": "export", "feature_name": "Full Exports", "enabled": True, "value_limit": "unlimited", "period": "lifetime"},
        ]
    },
    {
        "name": "Business",
        "code": "business",
        "description": "For creator studios and agency teams",
        "price_monthly": 149.00,
        "price_yearly": 1490.00,
        "trial_days": 14,
        "ai_credits_monthly": 10000,
        "max_channels": 30,
        "display_order": 4,
        "features": [
            {"feature_code": "ai_tools", "feature_name": "Enterprise AI Speed", "enabled": True, "value_limit": "10000_credits", "period": "monthly"},
            {"feature_code": "channel_sync", "feature_name": "Channel Sync", "enabled": True, "value_limit": "30", "period": "lifetime"},
            {"feature_code": "analytics", "feature_name": "Unrestricted Analytics", "enabled": True, "value_limit": "unlimited", "period": "lifetime"},
            {"feature_code": "video_audit", "feature_name": "Unlimited Audits", "enabled": True, "value_limit": "unlimited", "period": "monthly"},
            {"feature_code": "competitor_tracking", "feature_name": "Competitor Tracking", "enabled": True, "value_limit": "50", "period": "lifetime"},
            {"feature_code": "bulk_automation", "feature_name": "Priority Batch Queues", "enabled": True, "value_limit": "true", "period": "lifetime"},
            {"feature_code": "team_members", "feature_name": "Team Collaboration", "enabled": True, "value_limit": "5", "period": "lifetime"},
            {"feature_code": "api_access", "feature_name": "API Access", "enabled": True, "value_limit": "true", "period": "lifetime"},
        ]
    }
]


class EntitlementService:
    """
    Centralized Entitlement & Limits Engine.
    Guarantees consistent plan checks, feature permissions, and usage limits across all API endpoints.
    """

    @staticmethod
    def ensure_default_plans(db: Session) -> List[Plan]:
        """Seed default plans into DB if missing"""
        existing = db.execute(select(Plan)).scalars().all()
        if existing:
            return list(existing)

        created_plans = []
        for p_data in DEFAULT_PLANS_DATA:
            plan = Plan(
                name=p_data["name"],
                code=p_data["code"],
                description=p_data["description"],
                price_monthly=p_data["price_monthly"],
                price_yearly=p_data["price_yearly"],
                currency="USD",
                billing_interval="month",
                trial_days=p_data["trial_days"],
                ai_credits_monthly=p_data["ai_credits_monthly"],
                max_channels=p_data["max_channels"],
                is_active=True,
                display_order=p_data["display_order"]
            )
            db.add(plan)
            db.flush()

            for feat in p_data.get("features", []):
                pf = PlanFeature(
                    plan_id=plan.id,
                    feature_code=feat["feature_code"],
                    feature_name=feat["feature_name"],
                    enabled=feat["enabled"],
                    value_limit=str(feat.get("value_limit", "")),
                    period=feat.get("period", "monthly")
                )
                db.add(pf)
            created_plans.append(plan)

        db.commit()
        return created_plans

    @staticmethod
    def get_or_create_free_plan(db: Session) -> Plan:
        plan = db.execute(select(Plan).where(Plan.code == "free")).scalar_one_or_none()
        if not plan:
            plans = EntitlementService.ensure_default_plans(db)
            plan = next((p for p in plans if p.code == "free"), plans[0])
        return plan

    @staticmethod
    def get_user_subscription(db: Session, user_id: UUID) -> Subscription:
        """Fetch current active subscription for user or assign default Free subscription"""
        sub = db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING, SubscriptionStatus.PAST_DUE])
            ).order_by(Subscription.created_at.desc())
        ).scalar_one_or_none()

        if not sub:
            # Check for any subscription
            sub = db.execute(
                select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.created_at.desc())
            ).scalar_one_or_none()

        if not sub:
            free_plan = EntitlementService.get_or_create_free_plan(db)
            sub = Subscription(
                user_id=user_id,
                plan_id=free_plan.id,
                status=SubscriptionStatus.FREE,
                provider="MANUAL",
                price=0.00,
                currency="USD",
                billing_interval="month"
            )
            db.add(sub)
            db.commit()
            db.refresh(sub)

        return sub

    @staticmethod
    def can_use_feature(db: Session, user_id: UUID, feature_code: str) -> bool:
        """Check if user's current subscription level grants feature permission"""
        sub = EntitlementService.get_user_subscription(db, user_id)
        if not sub or sub.status in [SubscriptionStatus.CANCELED, SubscriptionStatus.EXPIRED]:
            # Grace check for free plan
            free_plan = EntitlementService.get_or_create_free_plan(db)
            plan_id = free_plan.id
        else:
            plan_id = sub.plan_id or EntitlementService.get_or_create_free_plan(db).id

        feature = db.execute(
            select(PlanFeature).where(
                PlanFeature.plan_id == plan_id,
                PlanFeature.feature_code == feature_code
            )
        ).scalar_one_or_none()

        if not feature:
            return False
        return feature.enabled

    @staticmethod
    def check_limit(db: Session, user_id: UUID, metric_key: str, requested_units: int = 1) -> Tuple[bool, int, int]:
        """
        Check if user has remaining quota for metric_key.
        Returns: (has_capacity: bool, current_usage: int, max_limit: int)
        -1 max_limit signifies unlimited.
        """
        sub = EntitlementService.get_user_subscription(db, user_id)
        plan = sub.plan if sub and sub.plan else EntitlementService.get_or_create_free_plan(db)

        # Check explicit custom user limit override
        custom_limit = db.execute(
            select(UsageLimit).where(
                UsageLimit.user_id == user_id,
                UsageLimit.metric_key == metric_key,
                UsageLimit.enabled == True
            )
        ).scalar_one_or_none()

        if custom_limit:
            max_limit = custom_limit.limit_value
        else:
            # Derive from plan feature or plan attributes
            if metric_key == "max_channels" or metric_key == "youtube_channels":
                max_limit = plan.max_channels
            else:
                feat = db.execute(
                    select(PlanFeature).where(
                        PlanFeature.plan_id == plan.id,
                        PlanFeature.feature_code == metric_key
                    )
                ).scalar_one_or_none()
                if not feat or not feat.enabled:
                    max_limit = 0
                elif feat.value_limit in ["unlimited", "true", "-1"]:
                    max_limit = -1
                else:
                    try:
                        max_limit = int(feat.value_limit.split("_")[0])
                    except (ValueError, AttributeError):
                        max_limit = 100

        if max_limit == -1:
            return True, 0, -1

        # Check recorded usage in usage_records table
        rec = db.execute(
            select(UsageRecord).where(
                UsageRecord.user_id == user_id,
                UsageRecord.metric_key == metric_key
            )
        ).scalar_one_or_none()

        current_usage = rec.units_used if rec else 0
        has_capacity = (current_usage + requested_units) <= max_limit
        return has_capacity, current_usage, max_limit

    @staticmethod
    def get_remaining_ai_credits(db: Session, user_id: UUID) -> Dict[str, int]:
        """Delegate to CreditSystem for atomic credit verification"""
        return CreditSystem.get_balance(db, user_id)

    @staticmethod
    def get_entitlements_summary(db: Session, user_id: UUID) -> Dict[str, Any]:
        """Return full entitlement summary for active user UI dashboard"""
        sub = EntitlementService.get_user_subscription(db, user_id)
        plan = sub.plan if sub and sub.plan else EntitlementService.get_or_create_free_plan(db)
        credits_info = EntitlementService.get_remaining_ai_credits(db, user_id)

        features = db.execute(
            select(PlanFeature).where(PlanFeature.plan_id == plan.id)
        ).scalars().all()

        feature_map = {f.feature_code: {"enabled": f.enabled, "limit": f.value_limit} for f in features}

        return {
            "subscription_id": str(sub.id),
            "status": sub.status.value,
            "provider": sub.provider,
            "cancel_at_period_end": sub.cancel_at_period_end,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
            "plan": {
                "id": str(plan.id),
                "name": plan.name,
                "code": plan.code,
                "price_monthly": float(plan.price_monthly),
                "price_yearly": float(plan.price_yearly),
                "currency": plan.currency,
                "ai_credits_monthly": plan.ai_credits_monthly,
                "max_channels": plan.max_channels
            },
            "credits": credits_info,
            "features": feature_map
        }
