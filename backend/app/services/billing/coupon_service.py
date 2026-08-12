import logging
from typing import Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.billing import Coupon, CouponRedemption
from app.models.auth import User

logger = logging.getLogger(__name__)


class CouponValidationResult:
    def __init__(self, is_valid: bool, discount_amount: float, message: str, coupon: Optional[Coupon] = None):
        self.is_valid = is_valid
        self.discount_amount = discount_amount
        self.message = message
        self.coupon = coupon


class CouponService:
    """
    Manages promotional coupons, validation rules, discount calculations, and redemption logs.
    """

    @staticmethod
    def validate_coupon(db: Session, code: str, purchase_amount: float, user_id: Optional[UUID] = None) -> CouponValidationResult:
        code_clean = code.strip().upper()
        coupon = db.execute(select(Coupon).where(Coupon.code == code_clean)).scalar_one_or_none()

        if not coupon:
            return CouponValidationResult(False, 0.0, "Invalid coupon code.")

        if not coupon.is_active:
            return CouponValidationResult(False, 0.0, "This coupon is inactive.")

        now = datetime.now(timezone.utc)
        if coupon.valid_until and coupon.valid_until < now:
            return CouponValidationResult(False, 0.0, "This coupon has expired.")

        if coupon.max_redemptions and coupon.redemptions_count >= coupon.max_redemptions:
            return CouponValidationResult(False, 0.0, "This coupon has reached its maximum redemption limit.")

        if coupon.min_purchase_amount and purchase_amount < float(coupon.min_purchase_amount):
            return CouponValidationResult(False, 0.0, f"Minimum purchase amount of ${coupon.min_purchase_amount:.2f} required.")

        if user_id:
            existing_user_redemption = db.execute(
                select(CouponRedemption).where(
                    CouponRedemption.coupon_id == coupon.id,
                    CouponRedemption.user_id == user_id
                )
            ).scalar_one_or_none()
            if existing_user_redemption:
                return CouponValidationResult(False, 0.0, "You have already used this coupon.")

        # Calculate discount
        if coupon.discount_type == "PERCENT":
            percent = float(coupon.discount_percent or 0)
            discount = round(purchase_amount * (percent / 100.0), 2)
        else: # FIXED
            discount = float(coupon.discount_amount or 0.0)

        discount = min(discount, purchase_amount)
        return CouponValidationResult(True, discount, "Coupon applied successfully!", coupon)

    @staticmethod
    def redeem_coupon(db: Session, coupon_id: UUID, user_id: UUID, discount_applied: float, subscription_id: Optional[UUID] = None) -> CouponRedemption:
        coupon = db.get(Coupon, coupon_id)
        if coupon:
            coupon.redemptions_count += 1
            db.add(coupon)

        redemption = CouponRedemption(
            coupon_id=coupon_id,
            user_id=user_id,
            subscription_id=subscription_id,
            discount_applied=discount_applied,
            redeemed_at=datetime.now(timezone.utc)
        )
        db.add(redemption)
        db.commit()
        db.refresh(redemption)
        return redemption
