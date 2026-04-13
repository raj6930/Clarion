"""
Reviews module — AI-first case quality review framework.
AI generates complete draft, manager refines with tracked overrides.
"""

MODULE_MANIFEST = {
    "name": "reviews",
    "version": "1.0.0",
    "description": "AI-first case quality reviews with rubric scoring, coaching, and recommendations.",
    "dependencies": ["cases", "sync"],
    "feature_flag": "module_reviews",
    "routes_module": "app.modules.reviews.routes",
    "routes_prefix": "/api/v1",
    "events_produced": ["review.created", "review.finalized", "review.recommendation.created"],
    "events_consumed": ["sync.team.completed", "prediction.escalation.high"],
    "chatbot_tools": ["create_review", "list_reviews", "get_review_summary"],
}
