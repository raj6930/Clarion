"""Clarion — chatbot Module."""
from app.registry import ModuleManifest

manifest = ModuleManifest(
    id="chatbot",
    name="chatbot",
    version="1.0.0",
    dependencies=[],
    required_permissions=["chatbot:read"],
)

def register(app):
    pass
