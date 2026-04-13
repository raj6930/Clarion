"""Health check endpoint — always active, not module-registered."""

from fastapi import APIRouter

from app.registry import registry

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "clarion-api",
        "version": "1.0.0",
        "modules": registry.get_health_status(),
    }
