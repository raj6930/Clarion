"""Contract tests for intelligence module schemas."""
import pytest
from app.intelligence.schemas import (
    AIGenerateRequest, AIGenerateResponse, AIHealthResponse, EngineStatusResponse,
)


class TestAIGenerateContract:
    def test_minimal_request(self):
        req = AIGenerateRequest(task="case_summary", prompt="Summarise case 123")
        assert req.task == "case_summary"
        assert req.engine is None
        assert req.temperature == 0.3

    def test_full_request(self):
        req = AIGenerateRequest(
            task="quality_review", prompt="Review this case",
            system_prompt="You are a reviewer", engine="claude",
            temperature=0.5, max_tokens=4000,
        )
        assert req.engine == "claude"

    def test_response_structure(self):
        resp = AIGenerateResponse(
            text="Summary here", engine="ollama", model="gemma2",
            tokens_used=150, latency_ms=2000, cost_usd=0.0,
        )
        assert resp.tokens_used == 150

    def test_health_response(self):
        health = AIHealthResponse(engines=[
            EngineStatusResponse(engine="ollama", available=True, is_local=True, model="gemma2"),
            EngineStatusResponse(engine="claude", available=False, is_local=False, model="claude-opus-4-6"),
        ])
        assert len(health.engines) == 2
        assert health.engines[0].is_local
