"""Help module API routes."""

from app.auth.dependencies import CurrentUser, get_current_user
from app.modules.help.schemas import HelpSearchRequest, HelpSearchResult, HelpSectionResponse
from app.modules.help.service import HelpService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/help", tags=["help"])
_service = HelpService()


@router.get("/sections", response_model=list[HelpSectionResponse])
async def list_sections(user: CurrentUser = Depends(get_current_user)):
    """List all help documentation sections."""
    return [HelpSectionResponse(**s.__dict__) for s in _service.get_all_sections()]


@router.get("/sections/{section_id}", response_model=HelpSectionResponse)
async def get_section(section_id: str, user: CurrentUser = Depends(get_current_user)):
    section = _service.get_section(section_id)
    if not section:
        from fastapi import HTTPException

        raise HTTPException(404, f"Section '{section_id}' not found")
    return HelpSectionResponse(**section.__dict__)


@router.post("/search", response_model=list[HelpSearchResult])
async def search_docs(req: HelpSearchRequest, user: CurrentUser = Depends(get_current_user)):
    """Search help documentation (also used by chatbot RAG)."""
    results = _service.search(req.query, req.max_results)
    return [HelpSearchResult(**r.__dict__) for r in results]
