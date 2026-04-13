"""
AI Router — Central orchestrator for all AI operations.
Handles engine selection, data routing (local vs anonymised external),
cost tracking, and fallback logic.
"""
import logging
from typing import Optional

from app.intelligence.engine_adapters.base import BaseEngine, EngineResponse, EngineError
from app.intelligence.engine_adapters.ollama import OllamaEngine
from app.intelligence.engine_adapters.claude import ClaudeEngine
from app.intelligence.engine_adapters.openai import OpenAIEngine
from app.modules.anonymisation.service import AnonymisationService

logger = logging.getLogger("clarion.ai.router")


# Task → default engine mapping (from architecture doc)
TASK_DEFAULTS = {
    "quality_review": "claude",
    "review_draft": "claude",
    "review_reevaluation": "claude",
    "technical_assessment": "claude",
    "case_summary": "ollama",
    "sentiment_analysis": "ollama",
    "escalation_prediction": "ollama",
    "knowledge_matching": "ollama",
    "chatbot_query": "ollama",
    "pattern_detection": "ollama",
    "anon_context_review": "ollama",
}

# Tasks that require anonymisation when using external engines
EXTERNAL_REQUIRES_ANON = {
    "quality_review", "review_draft", "review_reevaluation",
    "technical_assessment", "case_summary",
}


class AIRouter:
    """
    Routes AI requests to the appropriate engine.
    Local engines get raw data. External engines get anonymised data only.
    """

    def __init__(
        self,
        org_id: str,
        ollama_url: str = "http://clarion-ollama:11434",
        ollama_model: str = "gemma2",
        claude_api_key: Optional[str] = None,
        claude_model: str = "claude-opus-4-6",
        openai_api_key: Optional[str] = None,
        openai_model: str = "gpt-4o",
    ):
        self.org_id = org_id
        self._engines: dict[str, BaseEngine] = {}

        # Always register local engine
        self._engines["ollama"] = OllamaEngine(base_url=ollama_url, model=ollama_model)

        # Register external engines if keys provided
        if claude_api_key:
            self._engines["claude"] = ClaudeEngine(api_key=claude_api_key, model=claude_model)
        if openai_api_key:
            self._engines["openai"] = OpenAIEngine(api_key=openai_api_key, model=openai_model)

    def get_engine(self, engine_name: str) -> Optional[BaseEngine]:
        return self._engines.get(engine_name)

    @property
    def available_engines(self) -> list[str]:
        return list(self._engines.keys())

    def resolve_engine(self, task: str, user_preference: Optional[str] = None) -> str:
        """
        Resolve which engine to use for a task.
        Priority: user preference → task default → ollama fallback.
        """
        if user_preference and user_preference in self._engines:
            return user_preference

        default = TASK_DEFAULTS.get(task, "ollama")
        if default in self._engines:
            return default

        # Fallback to ollama (always available)
        return "ollama"

    async def generate(
        self,
        task: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        user_preference: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        anon_service: Optional[AnonymisationService] = None,
    ) -> EngineResponse:
        """
        Route an AI request through the appropriate engine.
        Automatically anonymises data for external engines.
        """
        engine_name = self.resolve_engine(task, user_preference)
        engine = self._engines[engine_name]

        actual_prompt = prompt
        actual_system = system_prompt
        anon_result = None

        # If external engine and task requires anonymisation
        if not engine.is_local and task in EXTERNAL_REQUIRES_ANON:
            if anon_service is None:
                anon_service = AnonymisationService(org_id=self.org_id)

            logger.info(f"Anonymising data for external engine: {engine_name}")
            anon_result = anon_service.anonymise(prompt)
            actual_prompt = anon_result.anonymised_text

            if system_prompt:
                sys_anon = anon_service.anonymise(system_prompt)
                actual_system = sys_anon.anonymised_text

        # Execute
        logger.info(f"Routing task '{task}' to engine '{engine_name}'")
        response = await engine.generate(
            prompt=actual_prompt,
            system_prompt=actual_system,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # De-anonymise response if we anonymised the input
        if anon_result and anon_service:
            restored, orphaned = anon_service.deanonymise(response.text)
            if orphaned:
                logger.warning(f"Orphaned tokens in response: {orphaned}")
            response.text = restored

        return response

    async def health(self) -> dict[str, bool]:
        """Check health of all registered engines."""
        results = {}
        for name, engine in self._engines.items():
            try:
                results[name] = await engine.health_check()
            except Exception:
                results[name] = False
        return results
