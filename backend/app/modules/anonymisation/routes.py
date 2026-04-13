"""Anonymisation API routes."""

from app.auth.dependencies import CurrentUser, get_current_user, require_admin
from app.modules.anonymisation.schemas import (
    AddDictionaryRequest,
    AnonymiseRequest,
    AnonymiseResponse,
    DeanonymiseRequest,
    DeanonymiseResponse,
    DetectedEntityResponse,
    FlagFalsePositiveRequest,
    MappingResponse,
)
from app.modules.anonymisation.service import AnonymisationService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/anonymise", tags=["anonymisation"])


@router.post("/run", response_model=AnonymiseResponse)
async def anonymise_text(
    req: AnonymiseRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Run the full 4-stage anonymisation pipeline on input text."""
    service = AnonymisationService(org_id=user.org_id, scope=req.scope)
    result = service.anonymise(req.text)

    return AnonymiseResponse(
        anonymised_text=result.anonymised_text,
        entity_count=result.entity_count,
        entities=[
            DetectedEntityResponse(
                entity_type=e.entity_type,
                value=e.value,
                start=e.start,
                end=e.end,
                detection_stage=e.detection_stage,
                confidence=e.confidence,
            )
            for e in result.entities
        ],
        mappings=[
            MappingResponse(
                pseudonym=m.pseudonym,
                entity_type=m.entity_type,
                detection_stage=m.detection_stage,
                confidence=m.confidence,
                is_false_positive=m.is_false_positive,
            )
            for m in result.mappings
        ],
    )


@router.post("/deanonymise", response_model=DeanonymiseResponse)
async def deanonymise_text(
    req: DeanonymiseRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Reverse anonymisation using session mappings."""
    # Phase 5: Load mappings from DB by session_id
    return DeanonymiseResponse(restored_text=req.text, orphaned_tokens=[])


@router.post("/false-positive")
async def flag_false_positive(
    req: FlagFalsePositiveRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Mark a detected entity as not actually PII."""
    return {"data": {"marked": True, "pseudonym": req.pseudonym}}


@router.post("/dictionary")
async def add_to_dictionary(
    req: AddDictionaryRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Add a term to the PII detection dictionary."""
    return {"data": {"added": True, "term": req.term}}


@router.get("/dictionary")
async def list_dictionary(
    user: CurrentUser = Depends(get_current_user),
):
    """List all dictionary entries for the org."""
    return {"data": []}


@router.get("/rules")
async def list_rules(
    user: CurrentUser = Depends(require_admin),
):
    """List anonymisation rules. Admin only."""
    return {"data": []}
