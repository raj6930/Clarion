"""Clarion — Sync Module. Salesforce data synchronisation."""

from fastapi import FastAPI
from app.registry import ModuleManifest

manifest = ModuleManifest(
    id="sync",
    name="Salesforce Sync",
    version="1.0.0",
    description="Salesforce CLI data synchronisation with incremental sync and retry logic.",
    dependencies=[],
    required_permissions=["sync:read", "sync:trigger"],
    admin_configurable=True,
    chatbot_tools=["get_sync_status", "trigger_sync"],
)

def register(app: FastAPI) -> None:
    from .routes import router
    app.include_router(router, prefix="/api/v1/sync", tags=["Sync"])
