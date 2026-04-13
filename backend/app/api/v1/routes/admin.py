"""
Admin endpoints. All require admin role.
Phase 2: Stubs with auth enforcement. Phase 10: Full implementation.
"""
from fastapi import APIRouter, Depends
from app.auth.dependencies import require_admin, CurrentUser

router = APIRouter()


@router.get("/users")
async def list_users(user: CurrentUser = Depends(require_admin)):
    return {"data": []}


@router.get("/health")
async def system_health(user: CurrentUser = Depends(require_admin)):
    return {"data": {"status": "healthy", "modules": 9, "db": "connected"}}


@router.get("/audit")
async def audit_log(user: CurrentUser = Depends(require_admin)):
    return {"data": []}


@router.get("/config/appearance")
async def get_appearance(user: CurrentUser = Depends(require_admin)):
    return {"data": {"default_layout": "editorial", "primary_colour": "#2563EB"}}


@router.put("/config/appearance")
async def update_appearance(user: CurrentUser = Depends(require_admin)):
    return {"data": {"updated": True}}
