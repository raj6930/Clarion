"""
Notifications module — Alert rules, multi-channel dispatch, notification management.
"""

MODULE_MANIFEST = {
    "name": "notifications",
    "version": "1.0.0",
    "description": "Alert rule engine and multi-channel notification dispatch.",
    "dependencies": ["cases", "sync"],
    "feature_flag": "module_notifications",
    "routes_module": "app.modules.notifications.routes",
    "routes_prefix": "/api/v1",
    "events_produced": ["notification.sent", "notification.failed"],
    "events_consumed": ["sync.team.completed", "prediction.escalation.high", "review.finalized"],
    "chatbot_tools": ["list_alerts", "get_unread_count"],
}
