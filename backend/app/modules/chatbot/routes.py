"""Chatbot module API routes."""

from app.auth.dependencies import CurrentUser, get_current_user
from app.config import settings
from app.modules.chatbot.schemas import (
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ConfirmActionResponse,
    ToolResponse,
)
from app.modules.chatbot.service import ChatbotService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

# Module-level service instance (Phase 10+: dependency injection)
_service_cache: dict[str, ChatbotService] = {}


def _get_service(user: CurrentUser) -> ChatbotService:
    if user.org_id not in _service_cache:
        from app.intelligence.router import AIRouter

        ai_router = AIRouter(
            org_id=user.org_id,
            ollama_url=settings.ollama_url,
            ollama_model=settings.default_local_model,
            claude_api_key=settings.claude_api_key,
            openai_api_key=settings.openai_api_key,
        )
        _service_cache[user.org_id] = ChatbotService(org_id=user.org_id, ai_router=ai_router)
    return _service_cache[user.org_id]


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    req: ChatMessageRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Send a message to the chatbot. Returns response with optional tool calls."""
    svc = _get_service(user)
    msg = await svc.process_message(
        user_id=user.user_id,
        message=req.message,
        context=req.context,
    )
    return ChatMessageResponse(
        role=msg.role,
        content=msg.content,
        tool_call=msg.tool_call,
        has_pending_action=msg.pending_action is not None,
        timestamp=msg.timestamp,
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_history(user: CurrentUser = Depends(get_current_user)):
    """Get current session chat history."""
    svc = _get_service(user)
    session = svc.get_or_create_session(user.user_id)
    return ChatHistoryResponse(
        session_id=session.session_id,
        messages=[
            ChatMessageResponse(
                role=m.role,
                content=m.content,
                tool_call=m.tool_call,
                has_pending_action=m.pending_action is not None,
                timestamp=m.timestamp,
            )
            for m in session.messages
        ],
    )


@router.post("/action/confirm", response_model=ConfirmActionResponse)
async def confirm_action(user: CurrentUser = Depends(get_current_user)):
    """Confirm a pending chatbot write action."""
    svc = _get_service(user)
    msg = await svc.confirm_action(user.user_id)
    return ConfirmActionResponse(
        role=msg.role,
        content=msg.content,
        tool_call=msg.tool_call,
        tool_result=msg.tool_result,
    )


@router.delete("/session")
async def clear_session(user: CurrentUser = Depends(get_current_user)):
    """Clear chatbot session (privacy-by-default)."""
    svc = _get_service(user)
    svc.clear_session(user.user_id)
    return {"data": {"cleared": True}}


@router.get("/tools", response_model=list[ToolResponse])
async def list_tools(user: CurrentUser = Depends(get_current_user)):
    """List available chatbot tools."""
    svc = _get_service(user)
    return [
        ToolResponse(
            name=t.name,
            description=t.description,
            module=t.module,
            requires_confirmation=t.requires_confirmation,
        )
        for t in svc.tool_registry.all_tools
    ]
