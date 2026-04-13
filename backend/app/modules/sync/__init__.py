"""
Sync module — Salesforce data synchronisation.
Handles team sync (by case owner) and account sync (by AccountId).
"""

MODULE_MANIFEST = {
    "name": "sync",
    "version": "1.0.0",
    "description": "Salesforce data synchronisation for cases, events, and accounts.",
    "dependencies": [],
    "feature_flag": "module_sync",
    "routes_module": "app.modules.sync.routes",
    "routes_prefix": "/api/v1",
    "events_produced": ["sync.team.completed", "sync.account.completed", "sync.failed"],
    "events_consumed": [],
    "chatbot_tools": [],
}
