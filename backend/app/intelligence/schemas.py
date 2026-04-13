"""Intelligence module Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional


class AIGenerateRequest(BaseModel):
    task: str  # quality_review | case_summary | sentiment_analysis | etc.
    prompt: str
    system_prompt: Optional[str] = None
    engine: Optional[str] = None  # User preference override
    temperature: float = 0.3
    max_tokens: int = 2000


class AIGenerateResponse(BaseModel):
    text: str
    engine: str
    model: str
    tokens_used: int
    latency_ms: int
    cost_usd: float


class EngineStatusResponse(BaseModel):
    engine: str
    available: bool
    is_local: bool
    model: str


class AIHealthResponse(BaseModel):
    engines: list[EngineStatusResponse]
