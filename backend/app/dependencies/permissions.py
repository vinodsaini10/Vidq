from fastapi import HTTPException, status
from app.models.user import User, UserRole


def check_super_admin(user: User):
    if user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required."
        )


def check_admin(user: User):
    if user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required."
        )
