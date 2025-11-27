import asyncio
import time
from collections import deque
from typing import Callable, Deque, Dict, Tuple

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class SlidingWindowRateLimiter:
    """
    In-memory sliding window limiter:
      - `limit`: max requests allowed within `window_seconds`
      - `window_seconds`: rolling window size in seconds
    Internals:
      - For each key, we store a deque of request timestamps (monotonic seconds).
      - Old timestamps are evicted on each check.
    """

    def __init__(self, limit: int, window_seconds: float):
        self.limit = int(limit)
        self.window = float(window_seconds)
        self._buckets: Dict[str, Deque[float]] = {}
        self._lock = asyncio.Lock()
        self._last_sweep = time.monotonic()

    def _now(self) -> float:
        return time.monotonic()

    def _evict_older_than(self, dq: Deque[float], cutoff: float) -> None:
        while dq and dq[0] <= cutoff:
            dq.popleft()

    async def allow(self, key: str) -> Tuple[bool, int, float]:
        """
        Returns (allowed, remaining, retry_after_seconds).
        retry_after_seconds = 0 when allowed.
        """
        now = self._now()
        cutoff = now - self.window

        async with self._lock:
            dq = self._buckets.get(key)
            if dq is None:
                dq = self._buckets[key] = deque()

            # Evict old entries
            self._evict_older_than(dq, cutoff)

            if len(dq) < self.limit:
                dq.append(now)
                remaining = self.limit - len(dq)
                self._maybe_sweep(now)
                return True, remaining, 0.0

            # Not allowed: compute when the oldest request will fall out of the window
            oldest = dq[0]
            retry_after = (oldest + self.window) - now
            remaining = 0
            self._maybe_sweep(now)
            return False, remaining, max(0.0, retry_after)

    def _maybe_sweep(self, now: float) -> None:
        # Occasional cleanup to prevent memory growth (once every ~60s)
        if now - self._last_sweep < 60:
            return
        self._last_sweep = now
        cutoff = now - self.window
        to_delete = []
        for key, dq in self._buckets.items():
            self._evict_older_than(dq, cutoff)
            if not dq:
                to_delete.append(key)
        for key in to_delete:
            self._buckets.pop(key, None)


def default_key_func(request: Request) -> str:
    """
    Per-IP + per-path key.
    If you're behind a reverse proxy, consider using X-Forwarded-For (trusted only).
    """
    client_ip = (
        request.headers.get("x-forwarded-for", request.client.host or "unknown")
        .split(",")[0]
        .strip()
    )
    return f"{client_ip}:{request.url.path}"


class SlidingWindowRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        limiter: SlidingWindowRateLimiter,
        key_func: Callable[[Request], str] = default_key_func,
        limit: int = 100,
        window_seconds: float = 60.0,
    ):
        super().__init__(app)
        self.limiter = limiter
        self.key_func = key_func
        self.limit = limit
        self.window = window_seconds

    async def dispatch(self, request: Request, call_next):
        key = self.key_func(request)
        allowed, remaining, retry_after = await self.limiter.allow(key)

        # RFC-compliant Retry-After and informative X-RateLimit-* headers
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(max(0, remaining)),
            # Seconds until the window fully resets for this key
            "X-RateLimit-Reset": str(int(retry_after)),
        }

        if not allowed:
            headers["Retry-After"] = str(int(max(1, round(retry_after))))
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too Many Requests",
                    "retry_after_seconds": round(retry_after, 3),
                },
                headers=headers,
            )

        response = await call_next(request)
        for k, v in headers.items():
            response.headers[k] = v
        return response
