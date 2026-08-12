from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Production security headers middleware.
    Protects against XSS, clickjacking, MIME-type sniffing, and protocol downgrade attacks.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # Enforce HSTS in production environments
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response
