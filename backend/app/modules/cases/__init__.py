"""
Clarion — Cases Module
Core case data viewing, chronology, and search.

This is the first feature module and serves as the reference
implementation for the module registry pattern.
"""

from fastapi import FastAPI

from app.registry import ModuleManifest

manifest = ModuleManifest(
    id="cases",
    name="Case Management",
    version="1.0.0",
    description="Core case data viewing, search, and chronology.",
    dependencies=["sync"],
    required_permissions=["cases:read", "cases:write"],
    admin_configurable=True,
    chatbot_tools=[
        "query_cases",
        "get_case_detail",
        "flag_case",
        "search_cases",
    ],
)


def register(app: FastAPI) -> None:
    """Register this module's routes with the application."""
    from .routes import router

    app.include_router(router, prefix="/api/v1/cases", tags=["Cases"])
