"""Clarion — Reviews Module. AI-first case quality review framework."""
from app.registry import ModuleManifest

manifest = ModuleManifest(
    id="reviews",
    name="Case Reviews",
    version="1.0.0",
    description="AI-first case quality review framework with structured rubric.",
    dependencies=["cases"],
    required_permissions=["reviews:read", "reviews:write"],
    admin_configurable=True,
    chatbot_tools=["request_review", "get_review_detail", "list_reviews"],
)

def register(app):
    from .routes import router
    app.include_router(router, prefix="/api/v1/reviews", tags=["Reviews"])
