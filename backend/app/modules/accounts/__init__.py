"""Clarion — Accounts Module. Account-based access for managers, CSMs, and account teams."""

from app.registry import ModuleManifest
from fastapi import FastAPI

manifest = ModuleManifest(
    id="accounts",
    name="Account Monitoring",
    version="1.0.0",
    description="Account search, selection, monitoring, and account-scoped case views.",
    dependencies=["cases"],
    required_permissions=["accounts:read", "accounts:write"],
    admin_configurable=True,
    chatbot_tools=[
        "search_accounts",
        "list_monitored_accounts",
        "get_account_cases",
        "get_account_summary",
    ],
)


def register(app: FastAPI) -> None:
    from .routes import router

    app.include_router(router, prefix="/api/v1/accounts", tags=["Accounts"])
