"""
Intelligence API routes.
Exposes AI generation, engine health, and configuration.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import CurrentUser, get_current_user
from app.config import settings
from app.intelligence.engine_adapters.base import EngineError
from app.intelligence.router import AIRouter
from app.intelligence.schemas import (
    AIGenerateRequest,
    AIGenerateResponse,
    AIHealthResponse,
    EngineStatusResponse,
)

router = APIRouter(prefix="/ai", tags=["intelligence"])


def _get_router(user: CurrentUser) -> AIRouter:
    """Create an AI router for the current user's org."""
    return AIRouter(
        org_id=user.org_id,
        ollama_url=settings.ollama_url,
        ollama_model=settings.default_local_model,
        claude_api_key=settings.claude_api_key,
        openai_api_key=settings.openai_api_key,
    )


@router.post("/generate", response_model=AIGenerateResponse)
async def generate(
    req: AIGenerateRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Route an AI generation request to the appropriate engine."""
    ai = _get_router(user)

    try:
        response = await ai.generate(
            task=req.task,
            prompt=req.prompt,
            system_prompt=req.system_prompt,
            user_preference=req.engine,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )
    except EngineError as e:
        raise HTTPException(
            status_code=503 if e.retryable else 400,
            detail=str(e),
        )

    return AIGenerateResponse(
        text=response.text,
        engine=response.engine,
        model=response.model,
        tokens_used=response.total_tokens,
        latency_ms=response.latency_ms,
        cost_usd=response.cost_usd,
    )


@router.get("/health", response_model=AIHealthResponse)
async def ai_health(user: CurrentUser = Depends(get_current_user)):
    """Check health of all AI engines."""
    ai = _get_router(user)
    health = await ai.health()

    engines = []
    for name, available in health.items():
        engine = ai.get_engine(name)
        engines.append(
            EngineStatusResponse(
                engine=name,
                available=available,
                is_local=engine.is_local if engine else False,
                model=getattr(engine, "model", "unknown"),
            )
        )

    return AIHealthResponse(engines=engines)


@router.get("/engines")
async def list_engines(user: CurrentUser = Depends(get_current_user)):
    """List available AI engines."""
    ai = _get_router(user)
    return {"data": ai.available_engines}
