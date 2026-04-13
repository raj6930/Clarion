"""Contract tests for chatbot module schemas."""

from app.modules.chatbot.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ToolResponse,
)


class TestChatContract:
    def test_message_request(self):
        req = ChatMessageRequest(
            message="Show me P1 cases",
            context={"active_page": "/dashboard", "selected_case": None},
        )
        assert req.message == "Show me P1 cases"

    def test_message_request_no_context(self):
        req = ChatMessageRequest(message="Hello")
        assert req.context == {}

    def test_message_response(self):
        resp = ChatMessageResponse(
            role="assistant",
            content="Here are your P1 cases.",
            has_pending_action=False,
        )
        assert not resp.has_pending_action

    def test_message_response_with_action(self):
        resp = ChatMessageResponse(
            role="assistant",
            content="Shall I create a review?",
            tool_call="create_review",
            has_pending_action=True,
        )
        assert resp.has_pending_action
        assert resp.tool_call == "create_review"

    def test_tool_response(self):
        t = ToolResponse(
            name="get_dashboard_metrics",
            description="Get KPIs",
            module="analytics",
            requires_confirmation=False,
        )
        assert not t.requires_confirmation
