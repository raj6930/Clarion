"""
Clarion — Application Factory
Bootstraps FastAPI, discovers modules, resolves dependencies, activates.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware import RateLimitMiddleware, SecurityHeadersMiddleware, RequestLoggingMiddleware, InputSanitisationMiddleware

from app.config import settings
from app.registry import registry

logger = logging.getLogger("clarion")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ─── Startup ───
    logging.basicConfig(level=getattr(logging, settings.log_level))
    logger.info("Clarion starting up...")

    # Discover and activate modules
    modules_path = Path(__file__).parent / "modules"
    registry.discover(modules_path)

    # TODO: Load feature flags from database
    # await registry.check_feature_flags(get_feature_flags)

    activation_order = registry.resolve_dependencies()
    logger.info(f"Module activation order: {activation_order}")

    registry.activate(app)
    logger.info(
        f"Clarion ready. {len(registry.enabled_modules)} modules active, "
        f"{len(registry.chatbot_tools)} chatbot tools registered."
    )

    yield

    # ─── Shutdown ───
    logger.info("Clarion shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Clarion API",
        description="Intelligent Support Analytics Platform",
        version="1.0.0",
        docs_url="/api/docs" if settings.environment == "development" else None,
        redoc_url="/api/redoc" if settings.environment == "development" else None,
        lifespan=lifespan,
    )

    # ─── CORS ───
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )n
    # ─── Security middleware ───n
    app.add_middleware(SecurityHeadersMiddleware)n
    app.add_middleware(RequestLoggingMiddleware)n
    app.add_middleware(InputSanitisationMiddleware)n
    app.add_middleware(RateLimitMiddleware, requests_per_minute=120
    )

    # ─── Core routes (always active, not module-registered) ───
    from app.api.v1.routes.health import router as health_router
    from app.api.v1.routes.auth import router as auth_router
    from app.api.v1.routes.admin import router as admin_router
    from app.api.v1.routes.appearance import router as appearance_router
    from app.api.v1.routes.appearance import preferences_router

    app.include_router(health_router, prefix="/api/v1", tags=["Health"])
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["Administration"])
    app.include_router(appearance_router, prefix="/api/v1", tags=["Appearance"])
    app.include_router(preferences_router, prefix="/api/v1", tags=["Preferences"])

    return app


# ASGI entry point
app = create_app()
