"""Cases module — API routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_cases():
    """List cases for user's team. Supports filtering, sorting, pagination."""
    # TODO: Phase 3 implementation
    return {"status": "not_implemented", "message": "Phase 3"}


@router.get("/{case_id}")
async def get_case(case_id: str):
    """Get full case detail including chronology."""
    return {"status": "not_implemented", "message": "Phase 3", "case_id": case_id}


@router.get("/{case_id}/timeline")
async def get_case_timeline(case_id: str):
    """Get case event timeline (paginated)."""
    return {"status": "not_implemented", "message": "Phase 3", "case_id": case_id}
