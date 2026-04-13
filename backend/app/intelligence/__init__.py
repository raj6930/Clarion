"""
Clarion Intelligence Layer
Central AI orchestration: engine adapters, routing, prompt management.
Shared across all modules via dependency injection.
"""
from .router import AIRouter

__all__ = ["AIRouter"]
