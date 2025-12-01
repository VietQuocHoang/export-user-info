from fastapi import FastAPI

from api.routers import router
from middleware.rate_limiter import (SlidingWindowRateLimiter,
                                     SlidingWindowRateLimitMiddleware,
                                     default_key_func)

from .settings import get_settings

settings = get_settings()


def register_middlewares(app: FastAPI) -> None:
    limiter = SlidingWindowRateLimiter(
        limit=settings.limit, window_seconds=settings.window_time
    )
    app.add_middleware(
        SlidingWindowRateLimitMiddleware,
        limiter=limiter,
        key_func=default_key_func,
        limit=limiter.limit,
        window_seconds=limiter.window,
    )


def register_router(app: FastAPI) -> None:
    app.include_router(router)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok"}

    register_middlewares(app)
    register_router(app)

    return app


app = create_app()
