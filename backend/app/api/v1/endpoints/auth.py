from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    Token,
    RefreshTokenRequest,
    PasswordResetRequest,
)
from app.schemas.user import UserResponse
from app.services.email_service import email_service
from app.services.youtube_service import youtube_service
from app.services.gmail_service import gmail_service
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/google/login")
async def google_login_url():
    """Returns Google OAuth authorization URL for logging in with Gmail / Google account."""
    auth_url = youtube_service.get_authorization_url(state="google_login_flow")
    return {"authorization_url": auth_url}


@router.post("/google/login", response_model=Token)
async def google_login_with_code(code: str, db: AsyncSession = Depends(get_db)):
    """Authenticate or register user using Google OAuth authorization code."""
    try:
        tokens = await youtube_service.exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Google token exchange failed.")

        user_info = await gmail_service.get_user_profile(access_token)
        email = user_info.get("email")
        name = user_info.get("name") or email.split("@")[0] if email else "Google Creator"

        if not email:
            raise HTTPException(status_code=400, detail="Could not retrieve email from Google profile.")

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user:
            # Register new Google User
            user = User(
                email=email,
                hashed_password=get_password_hash("google_oauth_" + email),
                full_name=name,
                youtube_channel_title=f"{name}'s Channel",
                youtube_handle=f"@{name.lower().replace(' ', '')}",
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        access = create_access_token(subject=str(user.id))
        refresh = create_refresh_token(subject=str(user.id))
        return Token(access_token=access, refresh_token=refresh)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google authentication failed: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user


@router.post("/register", response_model=UserResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    user = User(
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        youtube_channel_title=f"{req.full_name}'s Channel",
        youtube_handle=f"@{req.full_name.lower().replace(' ', '')}",
        youtube_subscriber_count=12400
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await email_service.send_welcome_email(user.email, user.full_name)

    return user


@router.post("/login", response_model=Token)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalars().first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    new_access = create_access_token(subject=str(user.id))
    new_refresh = create_refresh_token(subject=str(user.id))

    return Token(access_token=new_access, refresh_token=new_refresh)


@router.post("/forgot-password")
async def forgot_password(req: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalars().first()

    if user:
        reset_token = create_access_token(subject=str(user.id))
        await email_service.send_password_reset_email(user.email, reset_token)

    return {"message": "If the email is registered, password reset instructions have been sent."}
