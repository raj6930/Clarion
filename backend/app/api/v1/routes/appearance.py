"""
Appearance and User Preferences API.
Layout presets, theme resolution, and user preference management.
"""
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user, require_admin, CurrentUser

router = APIRouter(prefix="/appearance", tags=["appearance"])

LAYOUT_PRESETS = [
    {"id": "editorial", "name": "Editorial", "description": "Hero metric with contextual summary, stacked side KPIs, trend chart, attention table."},
    {"id": "command", "name": "Command Center", "description": "Dense 4-card strip, dual charts, full table. Maximum info density."},
    {"id": "executive", "name": "Executive", "description": "Three ring gauges, single trend chart. Deliberately sparse."},
    {"id": "ops", "name": "Operations", "description": "Split view: case card queue with severity/sentiment, contextual metrics."},
    {"id": "magazine", "name": "Magazine", "description": "Asymmetric editorial grid with featured insight card, 2x2 tiles."},
    {"id": "flow", "name": "Flow", "description": "Full-width single column: metrics bar, chart, table stacked."},
]


@router.get("/layouts")
async def list_layouts(user: CurrentUser = Depends(get_current_user)):
    return {"data": LAYOUT_PRESETS}


@router.get("/theme")
async def get_resolved_theme(user: CurrentUser = Depends(get_current_user)):
    """Phase 3: Reads from theme_config + user_preferences, merges layers."""
    return {
        "data": {
            "primary_colour": "#2563EB",
            "accent_colour": "#3B82F6",
            "font_family": "Geist Sans",
            "card_radius_px": 14,
            "density": "comfortable",
            "dark_mode": False,
            "layout_preset": "editorial",
            "company_name": "Clarion",
        }
    }


@router.put("/theme")
async def update_org_theme(user: CurrentUser = Depends(require_admin)):
    """Update org-level theme config. Admin only."""
    return {"data": {"updated": True}}


preferences_router = APIRouter(prefix="/preferences", tags=["preferences"])


@preferences_router.get("")
async def get_preferences(user: CurrentUser = Depends(get_current_user)):
    return {
        "data": {
            "layout_preset": None,
            "dark_mode": None,
            "density": None,
            "font_size_scale": None,
            "sidebar_collapsed": False,
        }
    }


@preferences_router.put("")
async def update_preferences(user: CurrentUser = Depends(get_current_user)):
    return {"data": {"updated": True}}


@preferences_router.put("/layout")
async def update_layout(user: CurrentUser = Depends(get_current_user)):
    return {"data": {"updated": True}}


@preferences_router.put("/dark-mode")
async def toggle_dark_mode(user: CurrentUser = Depends(get_current_user)):
    return {"data": {"updated": True}}
