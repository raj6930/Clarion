"""Clarion — analytics Module."""
from app.registry import ModuleManifest

manifest = ModuleManifest(
    id="analytics",
    name="analytics",
    version="1.0.0",
    dependencies=[],
    required_permissions=["analytics:read"],
)

def register(app):
    pass
