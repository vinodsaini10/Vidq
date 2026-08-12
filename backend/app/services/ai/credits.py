import logging
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException

from app.models.user import User

logger = logging.getLogger(__name__)


class CreditSystem:
    """Atomic Credit Deduction and Subscription Plan Enforcement System."""

    PLAN_CREDIT_LIMITS = {
        "FREE_USER": 50,
        "PREMIUM_USER": 2500,
        "STARTER": 500,
        "PRO": 2500,
        "BUSINESS": 5000,
        "ENTERPRISE": 20000,
        "ADMIN": 100000,
        "SUPER_ADMIN": 1000000,
    }

    async def get_user_credits(self, db: AsyncSession, user_id: str) -> dict:
        stmt = select(User).where(User.id == user_id)
        res = await db.execute(stmt)
        user = res.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        role_str = str(user.role.value if hasattr(user.role, "value") else user.role)
        max_credits = user.ai_credits_max or self.PLAN_CREDIT_LIMITS.get(role_str, 50)
        used_credits = user.ai_credits_used or 0
        remaining_credits = max(0, max_credits - used_credits)

        return {
            "user_id": str(user.id),
            "credits_max": max_credits,
            "credits_used": used_credits,
            "credits_remaining": remaining_credits,
            "role": role_str,
        }

    async def check_and_deduct_credits(
        self, db: AsyncSession, user_id: str, credits_required: int = 1
    ) -> bool:
        """Atomically checks and deducts AI credits using SELECT FOR UPDATE to prevent race conditions."""
        stmt = select(User).where(User.id == user_id).with_for_update()
        res = await db.execute(stmt)
        user = res.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        role_str = str(user.role.value if hasattr(user.role, "value") else user.role)
        max_credits = user.ai_credits_max or self.PLAN_CREDIT_LIMITS.get(role_str, 50)
        used_credits = user.ai_credits_used or 0
        remaining = max_credits - used_credits

        if remaining < credits_required:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient AI credits. Required: {credits_required}, Remaining: {remaining}. Please upgrade your subscription.",
            )

        # Atomic deduction
        user.ai_credits_used = used_credits + credits_required
        await db.commit()
        await db.refresh(user)
        return True

    async def refund_credits(self, db: AsyncSession, user_id: str, credits_to_refund: int = 1):
        """Refunds credits in case of AI generation failure."""
        stmt = select(User).where(User.id == user_id).with_for_update()
        res = await db.execute(stmt)
        user = res.scalars().first()

        if user:
            user.ai_credits_used = max(0, (user.ai_credits_used or 0) - credits_to_refund)
            await db.commit()


credit_system = CreditSystem()
