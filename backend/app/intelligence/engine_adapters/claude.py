"""
Claude Engine Adapter
Connects to Anthropic API for Claude Opus 4.6.
REQUIRES anonymisation — data is sent externally.
"""
import logging
import time
from typing import Optional

import httpx

from .base import BaseEngine, EngineResponse, EngineError

logger = logging.getLogger("clarion.ai.claude")

# Pricing per 1M tokens (as of 2026)
CLAUDE_PRICING = {
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
}


class ClaudeEngine(BaseEngine):
    engine_name = "claude"
    is_local = False  # External — anonymisation required

    def __init__(self, api_key: str, model: str = "claude-opus-4-6"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> EngineResponse:
        start = time.monotonic()

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(f"{self.base_url}/messages", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException:
            raise EngineError("Claude API timed out", self.engine_name, retryable=True)
        except httpx.HTTPStatusError as e:
            body = e.response.json() if e.response.headers.get("content-type", "").startswith("application/json") else {}
            msg = body.get("error", {}).get("message", str(e))
            retryable = e.response.status_code in (429, 500, 502, 503, 529)
            raise EngineError(f"Claude API error: {msg}", self.engine_name, retryable=retryable)

        latency = int((time.monotonic() - start) * 1000)
        text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")

        usage_data = data.get("usage", {})
        usage = {
            "prompt_tokens": usage_data.get("input_tokens", 0),
            "completion_tokens": usage_data.get("output_tokens", 0),
            "total_tokens": usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
        }

        cost = self._track_cost(usage)
        logger.info(f"Claude/{self.model}: {usage['total_tokens']} tokens, {latency}ms, ${cost:.4f}")

        return EngineResponse(
            text=text, engine=self.engine_name, model=self.model,
            usage=usage, latency_ms=latency, cost_usd=cost, raw_response=data,
        )

    def _track_cost(self, usage: dict) -> float:
        pricing = CLAUDE_PRICING.get(self.model, {"input": 15.0, "output": 75.0})
        input_cost = (usage.get("prompt_tokens", 0) / 1_000_000) * pricing["input"]
        output_cost = (usage.get("completion_tokens", 0) / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.base_url}/messages",
                    headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
                )
                # 405 Method Not Allowed means the API is reachable
                return resp.status_code in (200, 405)
        except Exception:
            return False
