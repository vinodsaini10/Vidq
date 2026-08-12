from typing import List, Union, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "VidPulse AI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    SECRET_KEY: str = "super-secret-key-change-in-production-environment-32bytes"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # PostgreSQL / Neon Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "vidpulse_db"
    
    # Neon database URL support (e.g., postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vidpulse_db"

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if isinstance(v, str) and v.strip():
            # Auto convert standard Neon / Postgres URL schemes to asyncpg driver
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            return v
        return "postgresql+asyncpg://postgres:postgres@localhost:5432/vidpulse_db"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # AI Engine Configuration
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    AI_DEFAULT_PROVIDER: str = "GEMINI"
    AI_DEFAULT_MODEL: str = "gemini-3.6-flash"
    AI_REQUEST_TIMEOUT: int = 60
    AI_MAX_RETRIES: int = 2
    AI_CACHE_TTL: int = 3600
    AI_ENABLE_FALLBACK: bool = True

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.run.app",
    ]

    # Google & YouTube API Configuration
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/api/v1/youtube/oauth/callback"
    YOUTUBE_API_KEY: str = ""
    GOOGLE_PROJECT_ID: str = ""
    GOOGLE_OAUTH_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/yt-analytics.readonly",
        "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        "https://www.googleapis.com/auth/youtube.force-ssl",
    ]

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@vidpulse.ai"
    EMAILS_FROM_NAME: str = "VidPulse AI Team"

    # Payment Gateways (Stripe & Razorpay)
    STRIPE_SECRET_KEY: str = "sk_test_mock_stripe_key"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_mock_stripe_key"
    STRIPE_WEBHOOK_SECRET: str = "whsec_mock_stripe_secret"
    RAZORPAY_KEY_ID: str = "rzp_test_mock_key"
    RAZORPAY_KEY_SECRET: str = "mock_razorpay_secret"
    RAZORPAY_WEBHOOK_SECRET: str = "mock_webhook_secret"
    RAZORPAY_DEFAULT_INR: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
