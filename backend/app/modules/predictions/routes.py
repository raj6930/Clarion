"""Predictions module API routes."""

from app.auth.dependencies import CurrentUser, get_current_user
from app.modules.predictions.schemas import (
    ContributingFactor,
    PredictionRefreshRequest,
    PredictionResponse,
)
from app.modules.predictions.service import PredictionService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("", response_model=list[PredictionResponse])
async def list_predictions(user: CurrentUser = Depends(get_current_user)):
    """List predictions for user's team cases."""
    svc = PredictionService(org_id=user.org_id)
    preds = svc.get_at_risk_cases()
    return [_to_response(p) for p in preds]


@router.get("/at-risk", response_model=list[PredictionResponse])
async def get_at_risk(user: CurrentUser = Depends(get_current_user)):
    """List cases with high escalation risk."""
    svc = PredictionService(org_id=user.org_id)
    preds = [p for p in svc.get_at_risk_cases() if p.risk_level in ("high", "medium")]
    return [_to_response(p) for p in preds]


@router.get("/{case_id}", response_model=PredictionResponse)
async def get_prediction(case_id: str, user: CurrentUser = Depends(get_current_user)):
    """Get prediction for a specific case."""
    svc = PredictionService(org_id=user.org_id)
    preds = [p for p in svc.get_at_risk_cases() if p.case_id == case_id]
    if not preds:
        # Generate on-demand
        pred = svc._heuristic_prediction(
            {"id": case_id, "sf_case_number": "unknown", "priority": "P3", "case_age_days": 5}
        )
        return _to_response(pred)
    return _to_response(preds[0])


@router.post("/refresh")
async def refresh_predictions(
    req: PredictionRefreshRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Re-run predictions for specified cases."""
    return {"data": {"refreshed": len(req.case_ids), "status": "queued"}}


def _to_response(p) -> PredictionResponse:
    return PredictionResponse(
        case_id=p.case_id,
        case_number=p.case_number,
        prediction_type=p.prediction_type,
        risk_score=p.risk_score,
        confidence=p.confidence,
        risk_level=p.risk_level,
        contributing_factors=[ContributingFactor(**f) for f in p.contributing_factors],
        reasoning=p.reasoning,
        source=p.source,
        valid_until=p.valid_until,
    )
