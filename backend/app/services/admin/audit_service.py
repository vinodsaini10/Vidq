import logging
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.admin import AdminAction

logger = logging.getLogger(__name__)


class AuditService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        admin_user_id: Optional[UUID],
        action: str,
        target_resource: str,
        details: Optional[Dict[str, Any]] = None
    ) -> AdminAction:
        """
        Record an administrative action in the audit log table.
        """
        try:
            entry = AdminAction(
                admin_user_id=admin_user_id,
                action=action,
                target_resource=target_resource,
                details=details or {}
            )
            db.add(entry)
            await db.commit()
            await db.refresh(entry)
            return entry
        except Exception as e:
            logger.error(f"Failed to log admin action '{action}' on '{target_resource}': {e}")
            return None
