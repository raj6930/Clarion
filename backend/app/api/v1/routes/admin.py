"""
Admin endpoints — comprehensive CRUD for all configuration sections.
All require admin role. Phase 10: Full implementation with stubs for DB operations.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.v1.routes.admin_service import (
    DEFAULT_EXCLUDED_STATUSES,
    DEFAULT_FEATURE_FLAGS,
    DEFAULT_TERMINOLOGY,
    ActivityMetrics,
    SystemHealth,
)
from app.auth.dependencies import CurrentUser, require_admin

router = APIRouter()


# ═══════════════════════════════════════════════════════
# USER MANAGEMENT
# ═══════════════════════════════════════════════════════


class UserListItem(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    is_active: bool
    created_at: str | None = None


class RoleUpdateRequest(BaseModel):
    role: str = Field(..., pattern="^(admin|manager|csm|engineer)$")


@router.get("/users", response_model=list[UserListItem])
async def list_users(user: CurrentUser = Depends(require_admin)):
    return [
        UserListItem(
            id="usr-001",
            email="demo@hexagon.com",
            display_name="Raj Singh",
            role="manager",
            is_active=True,
            created_at="2026-04-01T00:00:00Z",
        )
    ]


@router.put("/users/{user_id}/approve")
async def approve_user(user_id: str, user: CurrentUser = Depends(require_admin)):
    return {"data": {"approved": True, "user_id": user_id}}


@router.put("/users/{user_id}/role")
async def change_user_role(user_id: str, req: RoleUpdateRequest, user: CurrentUser = Depends(require_admin)):
    return {"data": {"updated": True, "user_id": user_id, "new_role": req.role}}


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(user_id: str, user: CurrentUser = Depends(require_admin)):
    if user_id == user.user_id:
        raise HTTPException(400, "Cannot deactivate yourself")
    return {"data": {"deactivated": True, "user_id": user_id}}


# ═══════════════════════════════════════════════════════
# SYSTEM HEALTH & MONITORING
# ═══════════════════════════════════════════════════════


@router.get("/health")
async def system_health(user: CurrentUser = Depends(require_admin)):
    h = SystemHealth()
    return {"data": h.__dict__}


@router.get("/activity")
async def activity_dashboard(user: CurrentUser = Depends(require_admin)):
    a = ActivityMetrics()
    return {"data": a.__dict__}


@router.get("/audit")
async def query_audit_log(
    action: str | None = None,
    user_id: str | None = None,
    limit: int = 50,
    user: CurrentUser = Depends(require_admin),
):
    return {"data": [], "total": 0, "limit": limit}


# ═══════════════════════════════════════════════════════
# BRANDING & APPEARANCE
# ═══════════════════════════════════════════════════════


class BrandingConfig(BaseModel):
    company_name: str = "Clarion"
    primary_colour: str = "#2563EB"
    accent_colour: str = "#3B82F6"
    font_family: str = "Geist Sans"
    card_radius_px: int = 14
    density: str = "comfortable"
    dark_mode_default: bool = False
    default_layout_preset: str = "editorial"
    logo_url: str | None = None


@router.get("/config/branding")
async def get_branding(user: CurrentUser = Depends(require_admin)):
    return {"data": BrandingConfig().model_dump()}


@router.put("/config/branding")
async def update_branding(req: BrandingConfig, user: CurrentUser = Depends(require_admin)):
    return {"data": req.model_dump()}


@router.get("/config/appearance")
async def get_appearance(user: CurrentUser = Depends(require_admin)):
    return {"data": BrandingConfig().model_dump()}


@router.put("/config/appearance")
async def update_appearance(req: BrandingConfig, user: CurrentUser = Depends(require_admin)):
    return {"data": req.model_dump()}


# ═══════════════════════════════════════════════════════
# TERMINOLOGY
# ═══════════════════════════════════════════════════════


@router.get("/config/terminology")
async def get_terminology(user: CurrentUser = Depends(require_admin)):
    return {"data": DEFAULT_TERMINOLOGY}


class TerminologyUpdate(BaseModel):
    terminology: dict[str, str]


@router.put("/config/terminology")
async def update_terminology(req: TerminologyUpdate, user: CurrentUser = Depends(require_admin)):
    return {"data": req.terminology}


# ═══════════════════════════════════════════════════════
# SALESFORCE SYNC CONFIG
# ═══════════════════════════════════════════════════════


class SyncConfig(BaseModel):
    sf_instance_url: str | None = None
    sf_auth_method: str = "cli"
    schedule_cron: str = "0 */2 * * *"
    account_sync_cron: str = "0 */4 * * *"
    retry_max: int = 5
    retry_backoff_base: int = 1


@router.get("/config/sync")
async def get_sync_config(user: CurrentUser = Depends(require_admin)):
    return {"data": SyncConfig().model_dump()}


@router.put("/config/sync")
async def update_sync_config(req: SyncConfig, user: CurrentUser = Depends(require_admin)):
    return {"data": req.model_dump()}


@router.get("/config/account-sync")
async def get_account_sync_config(user: CurrentUser = Depends(require_admin)):
    return {"data": {"schedule_cron": "0 */4 * * *"}}


@router.put("/config/account-sync")
async def update_account_sync_config(req: SyncConfig, user: CurrentUser = Depends(require_admin)):
    return {"data": {"schedule_cron": req.account_sync_cron}}


# ═══════════════════════════════════════════════════════
# AI ENGINE CONFIG
# ═══════════════════════════════════════════════════════


class AIEngineConfig(BaseModel):
    engine_id: str
    is_enabled: bool = True
    model_name: str | None = None
    monthly_budget_usd: float | None = None
    rate_limit_rpm: int | None = None


@router.get("/config/ai")
async def get_ai_config(user: CurrentUser = Depends(require_admin)):
    return {
        "data": [
            {
                "engine_id": "ollama",
                "is_enabled": True,
                "model_name": "gemma2",
                "monthly_budget_usd": None,
                "monthly_usage_usd": 0,
                "rate_limit_rpm": None,
            },
            {
                "engine_id": "claude",
                "is_enabled": False,
                "model_name": "claude-opus-4-6",
                "monthly_budget_usd": 50.0,
                "monthly_usage_usd": 0,
                "rate_limit_rpm": 60,
            },
            {
                "engine_id": "openai",
                "is_enabled": False,
                "model_name": "gpt-4o",
                "monthly_budget_usd": 30.0,
                "monthly_usage_usd": 0,
                "rate_limit_rpm": 60,
            },
        ]
    }


@router.put("/config/ai")
async def update_ai_config(req: AIEngineConfig, user: CurrentUser = Depends(require_admin)):
    return {"data": req.model_dump()}


# ═══════════════════════════════════════════════════════
# NOTIFICATION CONFIG
# ═══════════════════════════════════════════════════════


class NotificationConfig(BaseModel):
    email_enabled: bool = True
    teams_webhook_url: str | None = None
    slack_webhook_url: str | None = None
    quiet_hours_default: dict | None = None
    digest_schedule: str = "0 9 * * 1-5"


@router.get("/config/notifications")
async def get_notification_config(user: CurrentUser = Depends(require_admin)):
    return {"data": NotificationConfig().model_dump()}


@router.put("/config/notifications")
async def update_notification_config(req: NotificationConfig, user: CurrentUser = Depends(require_admin)):
    return {"data": req.model_dump()}


# ═══════════════════════════════════════════════════════
# FEATURE FLAGS
# ═══════════════════════════════════════════════════════


@router.get("/config/features")
async def get_feature_flags(user: CurrentUser = Depends(require_admin)):
    return {"data": DEFAULT_FEATURE_FLAGS}


class FeatureFlagUpdate(BaseModel):
    flags: dict[str, bool]


@router.put("/config/features")
async def update_feature_flags(req: FeatureFlagUpdate, user: CurrentUser = Depends(require_admin)):
    return {"data": req.flags}


# ═══════════════════════════════════════════════════════
# EXCLUDED STATUSES
# ═══════════════════════════════════════════════════════


@router.get("/config/excluded-statuses")
async def get_excluded_statuses(user: CurrentUser = Depends(require_admin)):
    return {"data": DEFAULT_EXCLUDED_STATUSES}


class ExcludedStatusesUpdate(BaseModel):
    statuses: list[str]


@router.put("/config/excluded-statuses")
async def update_excluded_statuses(req: ExcludedStatusesUpdate, user: CurrentUser = Depends(require_admin)):
    return {"data": req.statuses}


# ═══════════════════════════════════════════════════════
# DATA MANAGEMENT
# ═══════════════════════════════════════════════════════


@router.post("/backup/trigger")
async def trigger_backup(user: CurrentUser = Depends(require_admin)):
    return {"data": {"backup_id": "bkp-001", "status": "queued"}}


@router.post("/backup/restore")
async def restore_backup(user: CurrentUser = Depends(require_admin)):
    return {"data": {"status": "not_implemented"}}


class PurgeRequest(BaseModel):
    entity: str  # cases | events | reviews | predictions | notifications
    older_than_days: int = Field(ge=30)
    confirm: bool = False


@router.post("/data/purge")
async def purge_data(req: PurgeRequest, user: CurrentUser = Depends(require_admin)):
    if not req.confirm:
        raise HTTPException(400, "Set confirm=true to proceed with data purge")
    return {"data": {"entity": req.entity, "purged": 0, "status": "completed"}}
