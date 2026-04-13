"""Unit tests for AI Router and engine adapters."""

from app.intelligence.engine_adapters.base import EngineError, EngineResponse
from app.intelligence.prompts.templates import (
    anon_context_review_prompt,
    case_summary_prompt,
    chatbot_query_prompt,
    escalation_prediction_prompt,
    sentiment_prompt,
)
from app.intelligence.router import EXTERNAL_REQUIRES_ANON, AIRouter


class TestEngineResolution:
    def test_default_task_mapping(self):
        router = AIRouter(org_id="org-001")
        assert router.resolve_engine("sentiment_analysis") == "ollama"
        # Claude not available (no API key), falls back to ollama
        assert router.resolve_engine("quality_review") == "ollama"

    def test_user_preference_overrides(self):
        router = AIRouter(org_id="org-001")
        assert router.resolve_engine("case_summary", user_preference="ollama") == "ollama"

    def test_unavailable_engine_falls_back(self):
        router = AIRouter(org_id="org-001")
        # OpenAI not registered (no key), should fall back
        resolved = router.resolve_engine("case_summary", user_preference="openai")
        assert resolved == "ollama"  # Falls back to ollama

    def test_with_claude_key(self):
        router = AIRouter(org_id="org-001", claude_api_key="sk-test-key")
        assert "claude" in router.available_engines
        assert router.resolve_engine("quality_review") == "claude"

    def test_with_all_engines(self):
        router = AIRouter(
            org_id="org-001",
            claude_api_key="sk-test",
            openai_api_key="sk-test",
        )
        assert len(router.available_engines) == 3
        assert set(router.available_engines) == {"ollama", "claude", "openai"}

    def test_ollama_always_available(self):
        router = AIRouter(org_id="org-001")
        assert "ollama" in router.available_engines

    def test_local_tasks_use_ollama(self):
        router = AIRouter(org_id="org-001", claude_api_key="sk-test")
        local_tasks = [
            "sentiment_analysis",
            "escalation_prediction",
            "chatbot_query",
            "pattern_detection",
        ]
        for task in local_tasks:
            assert router.resolve_engine(task) == "ollama", f"Task {task} should default to ollama"


class TestAnonymisationRouting:
    def test_external_tasks_require_anon(self):
        assert "quality_review" in EXTERNAL_REQUIRES_ANON
        assert "review_draft" in EXTERNAL_REQUIRES_ANON
        assert "technical_assessment" in EXTERNAL_REQUIRES_ANON

    def test_local_tasks_dont_require_anon(self):
        assert "sentiment_analysis" not in EXTERNAL_REQUIRES_ANON
        assert "chatbot_query" not in EXTERNAL_REQUIRES_ANON
        assert "escalation_prediction" not in EXTERNAL_REQUIRES_ANON


class TestPromptTemplates:
    def test_case_summary_prompt(self):
        case = {
            "sf_case_number": "00803992",
            "subject": "Test",
            "priority": "P2",
            "status": "Working",
            "product": "EcoSys",
            "case_age_days": 12,
            "case_owner_name": "Tim",
        }
        events = [{"timestamp": "2026-01-01", "event_type": "email", "body": "Hello"}]
        system, user = case_summary_prompt(case, events)
        assert "Clarion" in system
        assert "00803992" in user
        assert "EcoSys" in user

    def test_sentiment_prompt(self):
        system, user = sentiment_prompt("I am very frustrated with the slow response time")
        assert "sentiment" in system.lower()
        assert "frustrated" in user

    def test_escalation_prompt(self):
        case = {
            "sf_case_number": "123",
            "priority": "P1",
            "case_age_days": 20,
            "status": "Escalated",
            "sla_status": "Breached",
        }
        events = [{"event_type": "email", "body": "Still waiting"}]
        system, user = escalation_prediction_prompt(case, events)
        assert "escalation" in system.lower()
        assert "P1" in user

    def test_chatbot_prompt_with_context(self):
        context = {"active_page": "/cases", "selected_case": "00803992"}
        system, user = chatbot_query_prompt("Show me P1 cases", context)
        assert "Clarion" in system
        assert "/cases" in user
        assert "P1 cases" in user

    def test_chatbot_prompt_without_context(self):
        system, user = chatbot_query_prompt("Hello", {})
        assert "No specific context" in user

    def test_anon_context_review_prompt(self):
        detected = [{"entity_type": "email", "value": "test@acme.com"}]
        system, user = anon_context_review_prompt("Contact test@acme.com or John", detected)
        assert "PII" in system
        assert "test@acme.com" in user


class TestEngineResponse:
    def test_response_fields(self):
        resp = EngineResponse(
            text="Hello",
            engine="ollama",
            model="gemma2",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            latency_ms=200,
            cost_usd=0.0,
        )
        assert resp.total_tokens == 15
        assert resp.cost_usd == 0.0

    def test_cost_calculation_zero_for_local(self):
        resp = EngineResponse(text="", engine="ollama", model="gemma2")
        assert resp.cost_usd == 0.0


class TestEngineError:
    def test_retryable_flag(self):
        err = EngineError("timeout", "ollama", retryable=True)
        assert err.retryable
        assert err.engine == "ollama"

    def test_non_retryable(self):
        err = EngineError("bad request", "claude", retryable=False)
        assert not err.retryable
