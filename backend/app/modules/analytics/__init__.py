"""
Analytics module — Operational dashboards, SLA metrics, workload, trends, patterns.
"""

MODULE_MANIFEST = {
    "name": "analytics",
    "version": "1.0.0",
    "description": "Operational analytics, SLA compliance, workload distribution, and trend analysis.",
    "dependencies": ["cases", "sync"],
    "feature_flag": "module_analytics",
    "routes_module": "app.modules.analytics.routes",
    "routes_prefix": "/api/v1",
    "events_produced": ["analytics.report.generated"],
    "events_consumed": ["sync.team.completed", "sync.account.completed"],
    "chatbot_tools": ["get_dashboard_metrics", "get_sla_status", "get_workload"],
}
