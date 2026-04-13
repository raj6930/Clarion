"""
Chatbot Service
Orchestrates: context injection → tool selection → AI generation → response.
Conversation is per-session (does not persist across sessions — privacy-by-default).
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.modules.chatbot.tools import build_default_registry

logger = logging.getLogger("clarion.chatbot")


@dataclass
class ChatMessage:
    role: str  # user | assistant | system
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    tool_call: str | None = None
    tool_result: dict | None = None
    pending_action: dict | None = None  # For write actions awaiting confirmation


@dataclass
class ChatSession:
    session_id: str
    user_id: str
    messages: list[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def history_for_prompt(self) -> list[dict]:
        """Format conversation history for AI context window."""
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages[-20:]  # Keep last 20 messages for context
            if m.role in ("user", "assistant")
        ]


class ChatbotService:
    """Manages chatbot sessions and query processing."""

    def __init__(self, org_id: str, ai_router=None):
        self.org_id = org_id
        self.ai_router = ai_router
        self.tool_registry = build_default_registry()
        self._sessions: dict[str, ChatSession] = {}

    def get_or_create_session(self, user_id: str) -> ChatSession:
        """Get existing session or create a new one."""
        if user_id not in self._sessions:
            self._sessions[user_id] = ChatSession(
                session_id=f"chat-{user_id}",
                user_id=user_id,
            )
        return self._sessions[user_id]

    def clear_session(self, user_id: str) -> bool:
        """Clear a user's chat session."""
        if user_id in self._sessions:
            del self._sessions[user_id]
            return True
        return False

    async def process_message(
        self,
        user_id: str,
        message: str,
        context: dict,
    ) -> ChatMessage:
        """
        Process a user message:
        1. Inject context (page, selected case, filters)
        2. Build system prompt with available tools
        3. Route to AI engine
        4. Parse response for tool calls
        5. Execute tools if needed
        6. Return response
        """
        session = self.get_or_create_session(user_id)

        # Add user message
        user_msg = ChatMessage(role="user", content=message)
        session.messages.append(user_msg)

        # Build system prompt with context and tools
        system_prompt = self._build_system_prompt(context)

        if not self.ai_router:
            response = ChatMessage(
                role="assistant",
                content="I'm Clarion AI Assistant. The AI engine is not currently available. "
                "Please check that the Ollama container is running.",
            )
            session.messages.append(response)
            return response

        try:
            # Build conversation for AI
            from app.intelligence.prompts.templates import chatbot_query_prompt

            _, user_prompt = chatbot_query_prompt(message, context)

            ai_response = await self.ai_router.generate(
                task="chatbot_query",
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
            )

            response_text = ai_response.text

            # Check for tool call patterns in response
            tool_call = self._extract_tool_call(response_text)
            pending_action = None

            if tool_call:
                tool = self.tool_registry.get(tool_call["name"])
                if tool and tool.requires_confirmation:
                    pending_action = tool_call
                    response_text = (
                        f"I'd like to **{tool_call['name']}**"
                        f"{' with ' + json.dumps(tool_call.get('params', {})) if tool_call.get('params') else ''}. "
                        f"This is a write action that requires your confirmation. Shall I proceed?"
                    )
                elif tool:
                    result = await self.tool_registry.execute(tool_call["name"], tool_call.get("params", {}))
                    response_text += f"\n\n_Tool result: {json.dumps(result)}_"

            response = ChatMessage(
                role="assistant",
                content=response_text,
                tool_call=tool_call["name"] if tool_call else None,
                pending_action=pending_action,
            )

        except Exception as e:
            logger.error(f"Chatbot query failed: {e}")
            response = ChatMessage(
                role="assistant",
                content=f"I encountered an issue processing your request. Please try again. (Error: {str(e)[:100]})",
            )

        session.messages.append(response)
        return response

    async def confirm_action(self, user_id: str) -> ChatMessage:
        """Confirm and execute a pending write action."""
        session = self.get_or_create_session(user_id)

        # Find the last message with a pending action
        pending = None
        for msg in reversed(session.messages):
            if msg.pending_action:
                pending = msg.pending_action
                msg.pending_action = None  # Clear
                break

        if not pending:
            response = ChatMessage(role="assistant", content="No pending action to confirm.")
            session.messages.append(response)
            return response

        result = await self.tool_registry.execute(pending["name"], pending.get("params", {}))
        response = ChatMessage(
            role="assistant",
            content=f"Action **{pending['name']}** executed successfully.\n\n_Result: {json.dumps(result)}_",
            tool_call=pending["name"],
            tool_result=result,
        )
        session.messages.append(response)
        return response

    def _build_system_prompt(self, context: dict) -> str:
        """Build system prompt with context and available tools."""
        tools_desc = self.tool_registry.tool_descriptions
        ctx_parts = []
        if context.get("active_page"):
            ctx_parts.append(f"The user is currently viewing: {context['active_page']}")
        if context.get("selected_case"):
            ctx_parts.append(f"Selected case: {context['selected_case']}")
        if context.get("filters"):
            ctx_parts.append(f"Active filters: {json.dumps(context['filters'])}")

        ctx_text = "\n".join(ctx_parts) if ctx_parts else "No specific page context."

        return (
            "You are Clarion AI Assistant, a support analytics chatbot for support managers. "
            "You help them understand team performance, find cases, interpret analytics, and take actions.\n\n"
            f"Current context:\n{ctx_text}\n\n"
            f"Available tools:\n{tools_desc}\n\n"
            "Guidelines:\n"
            "- Be concise and actionable\n"
            "- Reference specific data when possible\n"
            "- For write actions (marked REQUIRES CONFIRMATION), ask the user to confirm before executing\n"
            '- If you want to call a tool, respond with: TOOL_CALL: tool_name({"param": "value"})\n'
            "- If the user's question is outside your scope, suggest where they can find the answer"
        )

    def _extract_tool_call(self, response: str) -> dict | None:
        """Extract tool call from AI response text."""
        if "TOOL_CALL:" not in response:
            return None
        try:
            tool_part = response.split("TOOL_CALL:")[1].strip()
            # Parse: tool_name({"param": "value"})
            paren_idx = tool_part.find("(")
            if paren_idx == -1:
                return {"name": tool_part.strip(), "params": {}}
            name = tool_part[:paren_idx].strip()
            params_str = tool_part[paren_idx + 1 : tool_part.rfind(")")]
            params = json.loads(params_str) if params_str.strip() else {}
            return {"name": name, "params": params}
        except (json.JSONDecodeError, IndexError, ValueError):
            return None
