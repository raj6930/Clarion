"""Chatbot module Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    message: str
    context: dict = {}  # {active_page, selected_case, filters}


class ChatMessageResponse(BaseModel):
    role: str
    content: str
    tool_call: str | None = None
    has_pending_action: bool = False
    timestamp: datetime | None = None


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessageResponse]
    session_id: str


class ConfirmActionResponse(BaseModel):
    role: str
    content: str
    tool_call: str | None = None
    tool_result: dict | None = None


class ToolResponse(BaseModel):
    name: str
    description: str
    module: str
    requires_confirmation: bool
