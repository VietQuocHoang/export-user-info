import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from middleware.rate_limiter import (SlidingWindowRateLimiter,
                                     SlidingWindowRateLimitMiddleware)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio("asyncio")
async def test_rate_limiter_blocks_and_resets():
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=5)
    current_time = 1000.0

    def fake_now():
        return current_time

    limiter._now = fake_now

    allowed, remaining, retry_after = await limiter.allow("key")
    assert allowed is True
    assert remaining == 1
    assert retry_after == 0.0

    allowed, remaining, retry_after = await limiter.allow("key")
    assert allowed is True
    assert remaining == 0
    assert retry_after == 0.0

    allowed, remaining, retry_after = await limiter.allow("key")
    assert allowed is False
    assert remaining == 0
    assert retry_after == pytest.approx(5.0)

    current_time += 5.1
    allowed, remaining, retry_after = await limiter.allow("key")
    assert allowed is True
    assert remaining == 1
    assert retry_after == 0.0


def build_rate_limited_app(limit=1, window=1.0):
    limiter = SlidingWindowRateLimiter(limit=limit, window_seconds=window)
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"status": "ok"}

    app.add_middleware(
        SlidingWindowRateLimitMiddleware,
        limiter=limiter,
        key_func=lambda _: "static-key",
        limit=limiter.limit,
        window_seconds=limiter.window,
    )
    return app


def test_rate_limit_middleware_returns_429_when_limit_exceeded():
    app = build_rate_limited_app(limit=1, window=2)
    client = TestClient(app)

    first = client.get("/ping")
    assert first.status_code == 200
    assert first.headers["X-RateLimit-Limit"] == "1"
    assert first.headers["X-RateLimit-Remaining"] == "0"

    second = client.get("/ping")
    assert second.status_code == 429
    assert second.headers["Retry-After"] == "2"
    assert second.headers["X-RateLimit-Remaining"] == "0"
    assert second.json()["detail"] == "Too Many Requests"
