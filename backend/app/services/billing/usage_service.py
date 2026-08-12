import logging
from typing import Dict, Any, Optional, Tuple, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.billing import UsageRecord, UsageLimit
from app.services.billing.entitlement_service import EntitlementService

logger = logging.getLogger(__name__)


class UsageService:
    """
    Usage Metering & Metered Billing Service.
    Records metric usages, checks limit thresholds, and manages billing period resets.
    """

    @staticmethod
    def record_usage(db: Session, user_id: UUID, metric_key: str, units: int = 1, metadata: Optional[Dict[str, Any]] = None) -> UsageRecord:
        """Record usage units consumed for a specified metric_key"""
        rec = db.execute(
            select(UsageRecord).where(
                UsageRecord.user_id == user_id,
                UsageRecord.metric_key == metric_key
            )
        ).scalar_one_or_none()

        if not rec:
            rec = UsageRecord(
                user_id=user_id,
                metric_key=metric_key,
                units_used=units,
                metadata_json=metadata or {}
            )
            db.add(rec)
        else:
            rec.units_used += units
            if metadata:
                rec.metadata_json = {**rec.metadata_json, **metadata}

        db.commit()
        db.refresh(rec)

        # Check for usage warning threshold (80% or 100%)
        has_cap, used, max_lim = EntitlementService.check_limit(db, user_id, metric_key)
        if max_lim > 0:
            percentage = (used / max_lim) * 100
            if percentage >= 100:
                logger.warning(f"User {user_id} reached 100% usage limit for {metric_key} ({used}/{max_lim})")
            elif percentage >= 80:
                logger.info(f"User {user_id} reached {percentage:.0f}% usage limit for {metric_key}")

        return rec

    @staticmethod
    def get_user_usage_summary(db: Session, user_id: UUID) -> List[Dict[str, Any]]:
        """Return user's current usage across key platform metrics"""
        metrics = ["youtube_channels", "video_audits", "keyword_searches", "ai_scripts"]
        records = db.execute(
            select(UsageRecord).where(UsageRecord.user_id == user_id)
        ).scalars().all()

        rec_map = {r.metric_key: r.units_used for r in records}
        summary = []

        for m in metrics:
            has_cap, used, max_lim = EntitlementService.check_limit(db, user_id, m)
            summary.append({
                "metric_key": m,
                "units_used": used,
                "max_limit": max_lim,
                "has_capacity": has_cap,
                "percentage_used": round((used / max_lim) * 100, 1) if max_lim > 0 else (0 if max_lim == -1 else 100)
            })

        return summary

    @staticmethod
    def reset_period_usage(db: Session, user_id: UUID) -> None:
        """Reset periodic metric usage counters (e.g. on monthly subscription renewal)"""
        records = db.execute(
            select(UsageRecord).where(UsageRecord.user_id == user_id)
        ).scalars().all()

        for rec in records:
            # We don't reset channel count (lifetime state) but reset audits/searches/scripts
            if rec.metric_key not in ["youtube_channels", "max_channels"]:
                rec.units_used = 0
                db.add(rec)

        db.commit()
        logger.info(f"Reset period usage counters for user {user_id}")
