"""Clarion — notifications Module."""
from app.registry import ModuleManifest

manifest = ModuleManifest(
    id="notifications",
    name="notifications",
    version="1.0.0",
    dependencies=[],
    required_permissions=["notifications:read"],
)

def register(app):
    pass
