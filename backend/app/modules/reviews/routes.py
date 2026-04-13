"""Review module API routes."""

from app.auth.dependencies import (
    CurrentUser,
    require_manager_or_admin,
)
from app.modules.reviews.schemas import (
    CreateReviewRequest,
    FinaliseRequest,
    RecommendationActionRequest,
    RecommendationResponse,
    ReviewResponse,
    ReviewScoreResponse,
    RubricCategoryResponse,
    RubricQuestionResponse,
    UpdateScoreRequest,
)
from app.modules.reviews.service import DEFAULT_RUBRIC, ReviewService
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    req: CreateReviewRequest,
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """Create a new review and generate AI draft."""
    service = ReviewService(org_id=user.org_id)
    draft = await service.create_review(
        case_id=req.case_id,
        reviewer_id=user.user_id,
        ai_engine=req.ai_engine,
        selection_source=req.selection_source,
    )
    return _draft_to_response(draft)


@router.get("", response_model=list[ReviewResponse])
async def list_reviews(
    status: str = None,
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """List reviews for the user's team."""
    return []


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str,
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """Get a single review with all scores."""
    raise HTTPException(404, "Review not found (Phase 7: database lookup)")


@router.put("/{review_id}/scores")
async def update_score(
    review_id: str,
    req: UpdateScoreRequest,
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """Update a manager score for a question. Triggers re-evaluation flag."""
    return {"data": {"updated": True, "score_changed": True}}


@router.post("/{review_id}/finalise", response_model=ReviewResponse)
async def finalise_review(
    review_id: str,
    req: FinaliseRequest,
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """Finalise and lock a review."""
    raise HTTPException(404, "Review not found (Phase 7: database lookup)")


@router.post("/{review_id}/re-evaluate")
async def re_evaluate_overrides(
    review_id: str,
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """Trigger AI re-evaluation for overridden questions."""
    return {"data": {"re_evaluated": True}}


@router.post("/{review_id}/export-pdf")
async def export_pdf(
    review_id: str,
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """Export review as PDF."""
    return {"data": {"pdf_url": f"/api/v1/reviews/{review_id}/pdf"}}


@router.post("/{review_id}/email")
async def email_to_engineer(
    review_id: str,
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """Email the review to the case owner."""
    return {"data": {"sent": True}}


# ─── Recommendations ───


@router.get("/recommendations/pending", response_model=list[RecommendationResponse])
async def list_pending_recommendations(
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """List AI-flagged cases pending review."""
    return []


@router.post("/recommendations/{rec_id}/action")
async def action_recommendation(
    rec_id: str,
    req: RecommendationActionRequest,
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """Accept or dismiss a review recommendation."""
    return {"data": {"actioned": True, "action": req.action}}


# ─── Rubric Admin ───


@router.get("/rubric/categories", response_model=list[RubricCategoryResponse])
async def list_rubric_categories(
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """List all rubric categories."""
    seen = {}
    for q in DEFAULT_RUBRIC:
        if q.category_id not in seen:
            seen[q.category_id] = {
                "id": q.category_id,
                "name": q.category_name,
                "weight": q.category_weight,
                "count": 0,
                "is_active": True,
                "description": None,
            }
        seen[q.category_id]["count"] += 1
    return [
        RubricCategoryResponse(
            id=v["id"],
            name=v["name"],
            weight=v["weight"],
            question_count=v["count"],
            is_active=v["is_active"],
            description=v["description"],
        )
        for v in seen.values()
    ]


@router.get("/rubric/questions", response_model=list[RubricQuestionResponse])
async def list_rubric_questions(
    user: CurrentUser = Depends(require_manager_or_admin),
):
    """List all rubric questions."""
    return [
        RubricQuestionResponse(
            id=q.id,
            category_id=q.category_id,
            question_text=q.question_text,
            score_1_definition=q.score_1_definition,
            score_3_definition=q.score_3_definition,
            score_5_definition=q.score_5_definition,
            allows_na=q.allows_na,
            is_active=True,
        )
        for q in DEFAULT_RUBRIC
    ]


def _draft_to_response(draft) -> ReviewResponse:
    return ReviewResponse(
        review_id=draft.review_id,
        case_id=draft.case_id,
        reviewer_id=draft.reviewer_id,
        ai_engine=draft.ai_engine,
        status=draft.status,
        overall_score=draft.overall_score,
        coaching_summary=draft.coaching_summary,
        scores=[
            ReviewScoreResponse(
                question_id=s.question_id,
                question_text=s.question_text_snapshot,
                category_name=s.category_name_snapshot,
                weight=float(s.weight_snapshot),
                ai_score=s.ai_score,
                ai_comment=s.ai_comment,
                ai_coaching=s.ai_coaching_suggestion,
                manager_score=s.manager_score,
                manager_comment=s.manager_comment,
                is_na=s.is_na,
                score_changed=s.score_changed,
            )
            for s in draft.scores
        ],
        created_at=draft.created_at,
    )
