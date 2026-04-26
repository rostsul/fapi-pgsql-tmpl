import time
import uuid

from fastapi import Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings
from app.dependencies import redis_client


async def security_middleware(request: Request, call_next: RequestResponseEndpoint) -> Response:
    # OWASP: Request ID для трассировки
    request.state.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # OWASP: Simple Redis Rate Limiting (sliding window)
    client_ip = request.client.host
    key = f"rl:{client_ip}"
    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, 60)
    if current > settings.RATE_LIMIT_PER_MINUTE:
        return Response(status_code=429, content="Too Many Requests")

    start = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start

    # OWASP Security Headers
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

    return response
