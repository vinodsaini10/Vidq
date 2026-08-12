import logging
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings
from app.services.ai.registry import model_registry

logger = logging.getLogger(__name__)

router = APIRouter()

# Global Prometheus metrics counters & gauges (simulated format output)
METRICS_DATA = {
    "http_requests_total": 0,
    "http_request_errors_total": 0,
    "ai_requests_total": 0,
    "youtube_sync_total": 0,
    "payment_success_total": 0,
    "payment_failure_total": 0
}


def increment_metric(key: str, amount: int = 1):
    if key in METRICS_DATA:
        METRICS_DATA[key] += amount


@router.get("", tags=["Health"])
@router.get("/", tags=["Health"])
async def get_system_health(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check verifying Database, Redis, and Services.
    Secrets are never exposed.
    """
    db_status = "HEALTHY"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "UNHEALTHY"

    redis_status = "HEALTHY"
    try:
        import redis.asyncio as redis
        r = redis.from_url(settings.REDIS_URL or "redis://localhost:6379/0")
        await r.ping()
        await r.close()
    except Exception:
        redis_status = "DEGRADED"

    is_overall_healthy = db_status == "HEALTHY"

    return {
        "status": "UP" if is_overall_healthy else "DEGRADED",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT if hasattr(settings, "ENVIRONMENT") else "production",
        "components": {
            "database": db_status,
            "redis": redis_status,
            "youtube_api": "CONFIGURED" if settings.YOUTUBE_API_KEY else "NOT_CONFIGURED",
            "ai_engine": "READY" if settings.GEMINI_API_KEY or settings.OPENAI_API_KEY else "LIMITED"
        },
        "timestamp": int(time.time())
    }


@router.get("/live", tags=["Health"])
async def get_liveness():
    """
    Kubernetes/Docker liveness probe. Fast 200 OK.
    """
    return {"status": "ALIVE"}


@router.get("/ready", tags=["Health"])
async def get_readiness(db: AsyncSession = Depends(get_db)):
    """
    Kubernetes/Docker readiness probe checking DB availability.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "READY"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready: Database connection error")


@router.get("/database", tags=["Health"])
async def check_database_health(db: AsyncSession = Depends(get_db)):
    """
    Dedicated database health check endpoint.
    """
    start_time = time.time()
    try:
        res = await db.execute(text("SELECT 1"))
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {"status": "HEALTHY", "latency_ms": latency_ms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connectivity failure: {str(e)}")


@router.get("/redis", tags=["Health"])
async def check_redis_health():
    """
    Dedicated Redis health check endpoint.
    """
    try:
        import redis.asyncio as redis
        r = redis.from_url(settings.REDIS_URL or "redis://localhost:6379/0")
        await r.ping()
        await r.close()
        return {"status": "HEALTHY", "connection": "OK"}
    except Exception as e:
        return {"status": "DEGRADED", "detail": "Redis server offline or unreachable"}


@router.get("/youtube", tags=["Health"])
async def check_youtube_health():
    """
    Dedicated YouTube Integration status check.
    """
    has_api_key = bool(settings.YOUTUBE_API_KEY)
    has_oauth = bool(getattr(settings, "GOOGLE_CLIENT_ID", None))
    return {
        "status": "HEALTHY" if has_api_key or has_oauth else "UNCONFIGURED",
        "api_key_configured": has_api_key,
        "oauth_configured": has_oauth
    }


@router.get("/ai", tags=["Health"])
async def check_ai_health():
    """
    Dedicated AI Engine health check.
    """
    registered_models = model_registry.list_models()
    return {
        "status": "HEALTHY" if len(registered_models) > 0 else "LIMITED",
        "registered_models_count": len(registered_models),
        "primary_provider": "Gemini / OpenAI / Ollama"
    }


@router.get("/metrics", tags=["Monitoring"])
async def get_prometheus_metrics():
    """
    Prometheus metrics exposition endpoint.
    """
    metrics_text = f"""# HELP http_requests_total Total HTTP requests processed
# TYPE http_requests_total counter
http_requests_total {METRICS_DATA['http_requests_total']}

# HELP http_request_errors_total Total HTTP request errors
# TYPE http_request_errors_total counter
http_request_errors_total {METRICS_DATA['http_request_errors_total']}

# HELP ai_requests_total Total AI generations performed
# TYPE ai_requests_total counter
ai_requests_total {METRICS_DATA['ai_requests_total']}

# HELP youtube_sync_total Total YouTube channel sync executions
# TYPE youtube_sync_total counter
youtube_sync_total {METRICS_DATA['youtube_sync_total']}

# HELP payment_success_total Total successful subscription payments
# TYPE payment_success_total counter
payment_success_total {METRICS_DATA['payment_success_total']}

# HELP payment_failure_total Total failed subscription payments
# TYPE payment_failure_total counter
payment_failure_total {METRICS_DATA['payment_failure_total']}
"""
    return Response(content=metrics_text, media_type="text/plain")
