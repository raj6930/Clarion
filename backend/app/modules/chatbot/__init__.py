"""
Chatbot module — AI-powered assistant with context injection and tool calling.
Privacy-by-default: conversation does not persist across sessions.
"""

MODULE_MANIFEST = {
    "name": "chatbot",
    "version": "1.0.0",
    "description": "AI-powered chatbot with context injection, tool calling, and action confirmation.",
    "dependencies": ["cases", "analytics", "predictions"],
    "feature_flag": "module_chatbot",
    "routes_module": "app.modules.chatbot.routes",
    "routes_prefix": "/api/v1",
    "events_produced": ["chatbot.action.executed"],
    "events_consumed": [],
    "chatbot_tools": [],
}
