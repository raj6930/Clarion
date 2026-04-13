"""
Security Middleware
Rate limiting, request validation, security headers, and audit logging.
"""

import logging
import time
from collections import defaultdict
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("clarion.security")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token bucket rate limiter per IP + endpoint."""

    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.rpm = requests_per_minute
        self._buckets: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        key = f"{request.client.host}:{request.url.path}"
        now = time.time()
        window = now - 60

        # Clean old entries
        self._buckets[key] = [t for t in self._buckets[key] if t > window]

        if len(self._buckets[key]) >= self.rpm:
            logger.warning(f"Rate limit exceeded: {key}")
            return Response(
                content='{"detail": "Rate limit exceeded. Try again in 60 seconds."}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"},
            )

        self._buckets[key].append(now)
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers.pop("Server", None)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for audit trail."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)

        # Skip health checks from logs
        if request.url.path not in ("/api/v1/health", "/api/v1/health/"):
            logger.info(
                f"{request.method} {request.url.path} → {response.status_code} "
                f"({duration_ms}ms) [{request.client.host}]"
            )

        return response


class InputSanitisationMiddleware(BaseHTTPMiddleware):
    """Basic input validation — reject oversized payloads."""

    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            return Response(
                content='{"detail": "Request body too large. Maximum 10MB."}',
                status_code=413,
                media_type="application/json",
            )
        return await call_next(request)
