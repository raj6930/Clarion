"""Sync module — API routes."""
from fastapi import APIRouter
router = APIRouter()

@router.get("/status")
async def sync_status():
    return {"status": "not_implemented", "message": "Phase 3"}

@router.post("/trigger")
async def trigger_sync():
    return {"status": "not_implemented", "message": "Phase 3"}
