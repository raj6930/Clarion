"""
OpenAI Engine Adapter
Connects to OpenAI API. Alternative external engine.
REQUIRES anonymisation — data is sent externally.
"""

import logging
import time

import httpx

from .base import BaseEngine, EngineError, EngineResponse

logger = logging.getLogger("clarion.ai.openai")

OPENAI_PRICING = {
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
}


class OpenAIEngine(BaseEngine):
    engine_name = "openai"
    is_local = False

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> EngineResponse:
        start = time.monotonic()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException:
            raise EngineError("OpenAI request timed out", self.engine_name, retryable=True)
        except httpx.HTTPStatusError as e:
            retryable = e.response.status_code in (429, 500, 502, 503)
            raise EngineError(f"OpenAI error: {e.response.status_code}", self.engine_name, retryable=retryable)

        latency = int((time.monotonic() - start) * 1000)
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage_data = data.get("usage", {})
        usage = {
            "prompt_tokens": usage_data.get("prompt_tokens", 0),
            "completion_tokens": usage_data.get("completion_tokens", 0),
            "total_tokens": usage_data.get("total_tokens", 0),
        }

        cost = self._track_cost(usage)
        logger.info(f"OpenAI/{self.model}: {usage['total_tokens']} tokens, {latency}ms, ${cost:.4f}")

        return EngineResponse(
            text=text,
            engine=self.engine_name,
            model=self.model,
            usage=usage,
            latency_ms=latency,
            cost_usd=cost,
            raw_response=data,
        )

    def _track_cost(self, usage: dict) -> float:
        pricing = OPENAI_PRICING.get(self.model, {"input": 2.5, "output": 10.0})
        input_cost = (usage.get("prompt_tokens", 0) / 1_000_000) * pricing["input"]
        output_cost = (usage.get("completion_tokens", 0) / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                return resp.status_code == 200
        except Exception:
            return False
