"""
Base engine adapter interface.
All AI engines implement this contract.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class EngineError(Exception):
    """Raised when an AI engine request fails."""

    def __init__(self, message: str, engine: str, retryable: bool = False):
        super().__init__(message)
        self.engine = engine
        self.retryable = retryable


@dataclass
class EngineResponse:
    """Standardised response from any AI engine."""

    text: str
    engine: str
    model: str
    usage: dict = field(default_factory=dict)  # {prompt_tokens, completion_tokens, total_tokens}
    latency_ms: int = 0
    cost_usd: float = 0.0
    raw_response: dict | None = None

    @property
    def total_tokens(self) -> int:
        return self.usage.get("total_tokens", 0)


class BaseEngine(ABC):
    """Abstract base class for AI engine adapters."""

    engine_name: str = "base"
    is_local: bool = False  # Local engines don't need anonymisation

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> EngineResponse:
        """Generate a completion from the engine."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the engine is available."""
        ...

    def _track_cost(self, usage: dict) -> float:
        """Calculate cost in USD. Override per engine with actual pricing."""
        return 0.0
