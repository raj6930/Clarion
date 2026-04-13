"""
Ollama Engine Adapter
Connects to local Ollama instance for Gemma4 inference.
No anonymisation required — data never leaves the system.
"""

import logging
import time

import httpx

from .base import BaseEngine, EngineError, EngineResponse

logger = logging.getLogger("clarion.ai.ollama")


class OllamaEngine(BaseEngine):
    engine_name = "ollama"
    is_local = True

    def __init__(self, base_url: str = "http://clarion-ollama:11434", model: str = "gemma2"):
        self.base_url = base_url.rstrip("/")
        self.model = model

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

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException:
            raise EngineError("Ollama request timed out", self.engine_name, retryable=True)
        except httpx.HTTPStatusError as e:
            raise EngineError(
                f"Ollama HTTP error: {e.response.status_code}",
                self.engine_name,
                retryable=e.response.status_code >= 500,
            )
        except httpx.ConnectError:
            raise EngineError(
                "Cannot connect to Ollama. Is the container running?",
                self.engine_name,
                retryable=True,
            )

        latency = int((time.monotonic() - start) * 1000)
        text = data.get("message", {}).get("content", "")
        usage = {
            "prompt_tokens": data.get("prompt_eval_count", 0),
            "completion_tokens": data.get("eval_count", 0),
            "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
        }

        logger.info(f"Ollama/{self.model}: {usage['total_tokens']} tokens, {latency}ms")
        return EngineResponse(
            text=text,
            engine=self.engine_name,
            model=self.model,
            usage=usage,
            latency_ms=latency,
            cost_usd=0.0,
            raw_response=data,
        )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
