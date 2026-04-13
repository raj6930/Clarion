"""Clarion — predictions Module."""
from app.registry import ModuleManifest

manifest = ModuleManifest(
    id="predictions",
    name="predictions",
    version="1.0.0",
    dependencies=[],
    required_permissions=["predictions:read"],
)

def register(app):
    pass
