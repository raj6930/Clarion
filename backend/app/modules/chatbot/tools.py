"""
Chatbot Tool Registry
Discovers and manages tools registered by modules via their manifests.
Tools are functions the chatbot can invoke to answer queries or take actions.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field

logger = logging.getLogger("clarion.chatbot.tools")


@dataclass
class ChatbotTool:
    """A tool the chatbot can invoke."""

    name: str
    description: str
    module: str
    requires_confirmation: bool = False  # True for write actions
    handler: Callable | None = None
    parameters: dict = field(default_factory=dict)


class ToolRegistry:
    """Discovers and manages chatbot tools from module manifests."""

    def __init__(self):
        self._tools: dict[str, ChatbotTool] = {}

    def register(self, tool: ChatbotTool):
        self._tools[tool.name] = tool
        logger.info(f"Chatbot tool registered: {tool.name} (from {tool.module})")

    def get(self, name: str) -> ChatbotTool | None:
        return self._tools.get(name)

    @property
    def all_tools(self) -> list[ChatbotTool]:
        return list(self._tools.values())

    @property
    def tool_descriptions(self) -> str:
        """Format tool list for AI system prompt."""
        lines = []
        for t in self._tools.values():
            confirm = " [REQUIRES CONFIRMATION]" if t.requires_confirmation else ""
            lines.append(f"- {t.name}: {t.description}{confirm}")
        return "\n".join(lines)

    async def execute(self, name: str, params: dict) -> dict:
        """Execute a tool by name. Returns result dict."""
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"Unknown tool: {name}"}
        if tool.handler:
            try:
                result = await tool.handler(**params) if callable(tool.handler) else {"error": "Handler not callable"}
                return {"result": result, "tool": name}
            except Exception as e:
                logger.error(f"Tool {name} failed: {e}")
                return {"error": str(e), "tool": name}
        return {"error": f"Tool {name} has no handler", "tool": name}


def build_default_registry() -> ToolRegistry:
    """Build registry with built-in tools. Modules add their own at startup."""
    registry = ToolRegistry()

    registry.register(
        ChatbotTool(
            name="get_dashboard_metrics",
            description="Get current dashboard KPIs: open cases, P1/P2 active, SLA compliance, CSAT, resolution time.",
            module="analytics",
        )
    )
    registry.register(
        ChatbotTool(
            name="get_sla_status",
            description="Get SLA compliance breakdown by priority with trend.",
            module="analytics",
        )
    )
    registry.register(
        ChatbotTool(
            name="get_workload",
            description="Get engineer workload distribution with capacity percentages.",
            module="analytics",
        )
    )
    registry.register(
        ChatbotTool(
            name="get_at_risk_cases",
            description="List cases with high escalation risk and contributing factors.",
            module="predictions",
        )
    )
    registry.register(
        ChatbotTool(
            name="list_reviews",
            description="List recent case reviews with scores and status.",
            module="reviews",
        )
    )
    registry.register(
        ChatbotTool(
            name="create_review",
            description="Create a new quality review for a case. Triggers AI draft generation.",
            module="reviews",
            requires_confirmation=True,
        )
    )
    registry.register(
        ChatbotTool(
            name="list_alerts",
            description="List active alert rules and recent notifications.",
            module="notifications",
        )
    )
    registry.register(
        ChatbotTool(
            name="get_unread_count",
            description="Get count of unread notifications.",
            module="notifications",
        )
    )
    registry.register(
        ChatbotTool(
            name="search_cases",
            description="Search cases by keyword, priority, status, owner, or account.",
            module="cases",
        )
    )
    registry.register(
        ChatbotTool(
            name="get_case_summary",
            description="Get AI-generated summary of a specific case by case number.",
            module="cases",
        )
    )

    return registry
