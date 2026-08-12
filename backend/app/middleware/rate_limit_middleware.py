from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import time

# Simple memory sliding window rate-limiter for basic DDOS prevention
REQUEST_HISTORY = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        if client_ip not in REQUEST_HISTORY:
            REQUEST_HISTORY[client_ip] = []

        # Filter timestamps older than window
        REQUEST_HISTORY[client_ip] = [
            t for t in REQUEST_HISTORY[client_ip] if now - t < self.window_seconds
        ]

        if len(REQUEST_HISTORY[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Rate limit exceeded."},
            )

        REQUEST_HISTORY[client_ip].append(now)
        return await call_next(request)
