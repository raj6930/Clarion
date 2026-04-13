"""Unit tests for chatbot service and tool registry."""

import pytest
from app.modules.chatbot.service import ChatbotService, ChatMessage, ChatSession
from app.modules.chatbot.tools import ChatbotTool, ToolRegistry, build_default_registry


class TestToolRegistry:
    def test_default_registry_has_tools(self):
        registry = build_default_registry()
        assert len(registry.all_tools) == 10

    def test_register_and_get(self):
        registry = ToolRegistry()
        tool = ChatbotTool(name="test_tool", description="A test tool", module="test")
        registry.register(tool)
        assert registry.get("test_tool") is not None
        assert registry.get("nonexistent") is None

    def test_tool_descriptions_format(self):
        registry = build_default_registry()
        desc = registry.tool_descriptions
        assert "get_dashboard_metrics" in desc
        assert "create_review" in desc
        assert "REQUIRES CONFIRMATION" in desc

    def test_write_tools_require_confirmation(self):
        registry = build_default_registry()
        create_review = registry.get("create_review")
        assert create_review.requires_confirmation

    def test_read_tools_no_confirmation(self):
        registry = build_default_registry()
        get_metrics = registry.get("get_dashboard_metrics")
        assert not get_metrics.requires_confirmation

    def test_all_tools_have_module(self):
        registry = build_default_registry()
        for tool in registry.all_tools:
            assert tool.module, f"Tool {tool.name} has no module"


class TestChatSession:
    def test_new_session_empty(self):
        session = ChatSession(session_id="test", user_id="u-001")
        assert len(session.messages) == 0

    def test_history_for_prompt_limits(self):
        session = ChatSession(session_id="test", user_id="u-001")
        for i in range(30):
            session.messages.append(ChatMessage(role="user", content=f"Message {i}"))
            session.messages.append(ChatMessage(role="assistant", content=f"Response {i}"))
        history = session.history_for_prompt
        assert len(history) == 20  # Last 20 messages

    def test_history_excludes_system(self):
        session = ChatSession(session_id="test", user_id="u-001")
        session.messages.append(ChatMessage(role="system", content="System prompt"))
        session.messages.append(ChatMessage(role="user", content="Hello"))
        session.messages.append(ChatMessage(role="assistant", content="Hi"))
        history = session.history_for_prompt
        assert len(history) == 2  # Excludes system


class TestChatbotService:
    def test_create_session(self):
        svc = ChatbotService(org_id="org-001")
        session = svc.get_or_create_session("u-001")
        assert session.user_id == "u-001"

    def test_session_reuse(self):
        svc = ChatbotService(org_id="org-001")
        s1 = svc.get_or_create_session("u-001")
        s2 = svc.get_or_create_session("u-001")
        assert s1 is s2

    def test_clear_session(self):
        svc = ChatbotService(org_id="org-001")
        svc.get_or_create_session("u-001")
        assert svc.clear_session("u-001")
        assert not svc.clear_session("u-001")  # Already cleared

    @pytest.mark.asyncio
    async def test_no_ai_router_fallback(self):
        svc = ChatbotService(org_id="org-001", ai_router=None)
        msg = await svc.process_message("u-001", "Hello", {})
        assert msg.role == "assistant"
        assert "not currently available" in msg.content

    def test_extract_tool_call(self):
        svc = ChatbotService(org_id="org-001")
        result = svc._extract_tool_call("Let me check. TOOL_CALL: get_dashboard_metrics({})")
        assert result is not None
        assert result["name"] == "get_dashboard_metrics"

    def test_extract_tool_call_with_params(self):
        svc = ChatbotService(org_id="org-001")
        result = svc._extract_tool_call('TOOL_CALL: search_cases({"priority": "P1"})')
        assert result["name"] == "search_cases"
        assert result["params"]["priority"] == "P1"

    def test_extract_no_tool_call(self):
        svc = ChatbotService(org_id="org-001")
        result = svc._extract_tool_call("Here are the metrics for your team.")
        assert result is None

    def test_system_prompt_includes_context(self):
        svc = ChatbotService(org_id="org-001")
        prompt = svc._build_system_prompt({"active_page": "/cases", "selected_case": "00803992"})
        assert "/cases" in prompt
        assert "00803992" in prompt
        assert "get_dashboard_metrics" in prompt

    @pytest.mark.asyncio
    async def test_confirm_no_pending(self):
        svc = ChatbotService(org_id="org-001")
        svc.get_or_create_session("u-001")
        msg = await svc.confirm_action("u-001")
        assert "No pending action" in msg.content
