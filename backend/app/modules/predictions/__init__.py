"""
Predictions module — Escalation risk prediction via LLM reasoning and ML models.
"""

MODULE_MANIFEST = {
    "name": "predictions",
    "version": "1.0.0",
    "description": "Escalation risk and SLA breach predictions.",
    "dependencies": ["cases", "sync"],
    "feature_flag": "module_predictions",
    "routes_module": "app.modules.predictions.routes",
    "routes_prefix": "/api/v1",
    "events_produced": ["prediction.escalation.high", "prediction.sla_breach.imminent"],
    "events_consumed": ["sync.team.completed"],
    "chatbot_tools": ["get_at_risk_cases", "predict_case_risk"],
}
