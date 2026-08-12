import pytest
import asyncio
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.auth import User, UserProfile
from app.models.enums import UserRole
from app.models.billing import Plan, Subscription
from app.models.youtube import YouTubeChannel, YouTubeVideo


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_database_tables_creation():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    assert True


@pytest.mark.asyncio
async def test_user_creation_and_profile_relationship():
    async with AsyncSessionLocal() as session:
        user = User(
            email="test_user_db@vidpulse.ai",
            hashed_password="hashed_password_sample",
            full_name="Database Tester",
            role=UserRole.FREE_USER
        )
        session.add(user)
        await session.flush()

        profile = UserProfile(
            user_id=user.id,
            bio="Automated integration test profile",
            timezone="UTC"
        )
        session.add(profile)
        await session.commit()

        # Query back
        res = await session.execute(select(User).where(User.id == user.id))
        fetched_user = res.scalars().first()

        assert fetched_user is not None
        assert fetched_user.email == "test_user_db@vidpulse.ai"
        assert fetched_user.profile.bio == "Automated integration test profile"


@pytest.mark.asyncio
async def test_soft_delete_flag():
    async with AsyncSessionLocal() as session:
        user = User(
            email="soft_delete_test@vidpulse.ai",
            hashed_password="hashed_pass_sample",
            full_name="Soft Delete Test"
        )
        session.add(user)
        await session.commit()

        user.is_deleted = True
        await session.commit()

        res = await session.execute(select(User).where(User.id == user.id, User.is_deleted == False))
        active_user = res.scalars().first()

        assert active_user is None
