"""
Sync module API routes.
Manual trigger, status check, and sync history.
"""
from fastapi import APIRouter, Depends
from app.auth.dependencies import require_manager_or_admin, CurrentUser
from app.modules.sync.schemas import SyncTriggerRequest, SyncStatusResponse, SyncLogEntry

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/trigger", response_model=SyncStatusResponse)
async def trigger_sync(
    req: SyncTriggerRequest,
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """Manually trigger a team or account sync. Manager/Admin only."""
    # Phase 3: Dispatches Celery task. Returns immediately with running status.
    return SyncStatusResponse(
        sync_type=req.sync_type,
        status="running",
        cases_synced=0,
        events_synced=0,
    )


@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status(
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """Get current sync status."""
    return SyncStatusResponse(
        sync_type="team",
        status="idle",
        cases_synced=0,
        events_synced=0,
    )


@router.get("/history", response_model=list[SyncLogEntry])
async def get_sync_history(
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """Get sync history log."""
    return []
