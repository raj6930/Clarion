"""Reviews module — API routes."""
from fastapi import APIRouter
router = APIRouter()

@router.post("")
async def create_review():
    return {"status": "not_implemented", "message": "Phase 6"}

@router.get("")
async def list_reviews():
    return {"status": "not_implemented", "message": "Phase 6"}

@router.get("/recommendations")
async def list_recommendations():
    return {"status": "not_implemented", "message": "Phase 6"}
