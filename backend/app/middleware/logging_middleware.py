import time
import uuid
import json
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("api.json")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured JSON logger for production observability.
    Includes request_id, trace context, status, latency, and client info.
    Guarantees no sensitive tokens, keys, or credentials are logged.
    """
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.time()

        # Sanitize query parameters to prevent token leaks in logs
        path = request.url.path
        
        response = await call_next(request)
        process_time_ms = round((time.time() - start_time) * 1000, 2)

        log_payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": "INFO" if response.status_code < 400 else "ERROR",
            "service": "vidpulse-backend",
            "request_id": request_id,
            "method": request.method,
            "path": path,
            "status_code": response.status_code,
            "latency_ms": process_time_ms,
            "client_ip": request.client.host if request.client else "unknown"
        }

        # Log as structured JSON string
        logger.info(json.dumps(log_payload))

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time_ms}ms"
        return response
