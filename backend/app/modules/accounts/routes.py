"""Accounts module — API routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/search")
async def search_accounts(q: str = ""):
    """Search accounts by partial name. Returns disambiguated results."""
    # TODO: Phase 3 implementation
    return {"status": "not_implemented", "message": "Phase 3", "query": q}


@router.get("/monitored")
async def list_monitored():
    """List accounts monitored by current user."""
    return {"status": "not_implemented", "message": "Phase 3"}


@router.post("/monitored")
async def add_monitored():
    """Add account to user's monitored list."""
    return {"status": "not_implemented", "message": "Phase 3"}


@router.put("/monitored/{id}")
async def update_monitored(id: str):
    """Update monitored account settings (predictions, sentiment)."""
    return {"status": "not_implemented", "message": "Phase 3"}


@router.delete("/monitored/{id}")
async def remove_monitored(id: str):
    """Remove account from monitored list."""
    return {"status": "not_implemented", "message": "Phase 3"}


@router.get("/{sf_account_id}/cases")
async def account_cases(sf_account_id: str):
    """List cases for a monitored account (excluding closed/cancelled)."""
    return {"status": "not_implemented", "message": "Phase 3"}


@router.get("/{sf_account_id}/summary")
async def account_summary(sf_account_id: str):
    """Account case summary: volume, status breakdown, priority distribution."""
    return {"status": "not_implemented", "message": "Phase 3"}


@router.get("/{sf_account_id}/cases/{case_id}")
async def account_case_detail(sf_account_id: str, case_id: str):
    """Case detail: AI summary, next step, event history."""
    return {"status": "not_implemented", "message": "Phase 3"}
