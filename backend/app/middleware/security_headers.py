"""
Production Security Headers Middleware.
Applies hardened HTTP headers to all API responses to protect against XSS, clickjacking, MIME sniffing, and framing.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Applies standardized DevSecOps HTTP response security headers."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        if not settings.SECURITY_HEADERS_ENABLED:
            return response

        # 1. Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 2. Prevent clickjacking by disallowing framing
        response.headers["X-Frame-Options"] = "DENY"

        # 3. Legacy XSS filter activation
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 4. Referrer policy to prevent information leakage
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 5. Restrict unnecessary browser features & hardware sensors
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(), payment=()"

        # 6. Content Security Policy (designed for API and Swagger UI compatibility)
        if not response.headers.get("Content-Security-Policy"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "font-src 'self' data: https://fonts.gstatic.com; "
                "frame-ancestors 'none';"
            )

        return response
