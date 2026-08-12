from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Configure engine kwargs for Neon serverless / SSL
engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
    "pool_pre_ping": True,
    "pool_size": 20,
    "max_overflow": 10,
    "pool_recycle": 1800,
}

# If connecting to Neon or requiring SSL via URL
db_url = settings.DATABASE_URL
if "neon.tech" in db_url or "sslmode=require" in db_url or "ssl=require" in db_url:
    # Ensure ssl query param is properly set for asyncpg if sslmode is passed
    if "sslmode=require" in db_url and "ssl=" not in db_url:
        db_url = db_url.replace("sslmode=require", "ssl=require")

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
