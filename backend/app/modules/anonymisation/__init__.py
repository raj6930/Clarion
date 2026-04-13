"""Clarion — anonymisation Module."""
from app.registry import ModuleManifest

manifest = ModuleManifest(
    id="anonymisation",
    name="anonymisation",
    version="1.0.0",
    dependencies=[],
    required_permissions=["anonymisation:read"],
)

def register(app):
    pass
