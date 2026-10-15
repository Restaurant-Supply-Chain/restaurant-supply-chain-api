import math
from collections import deque
from time import monotonic

from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import http_exception_handler


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        if path != "/auth" and not path.startswith("/auth/"):
            return await call_next(request)

        # Count all auth endpoints together, using the connecting client's IP.
        if not hasattr(request.app.state, "auth_requests"):
            request.app.state.auth_requests = {}
        request_times = request.app.state.auth_requests
        now = monotonic()

        # Remove timestamps older than a minute and discard inactive clients.
        for address, timestamps in list(request_times.items()):
            while timestamps and timestamps[0] <= now - 60:
                timestamps.popleft()
            if not timestamps:
                del request_times[address]

        address = request.client.host if request.client else "unknown"
        timestamps = request_times.setdefault(address, deque())
        if len(timestamps) >= 10:
            retry_after = max(1, math.ceil(60 - (now - timestamps[0])))
            error = HTTPException(
                status_code=429,
                detail="Authentication is limited to 10 requests per minute.",
                headers={"Retry-After": str(retry_after)},
            )
            return await http_exception_handler(request, error)

        timestamps.append(now)
        return await call_next(request)
