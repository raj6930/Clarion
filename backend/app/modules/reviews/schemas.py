"""Review module Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateReviewRequest(BaseModel):
    case_id: str
    ai_engine: str = "ollama"
    selection_source: str = "manual"
    trigger_reason: dict | None = None


class ReviewScoreResponse(BaseModel):
    question_id: str
    question_text: str
    category_name: str
    weight: float
    ai_score: int | None = None
    ai_comment: str | None = None
    ai_coaching: str | None = None
    manager_score: int | None = None
    manager_comment: str | None = None
    is_na: bool = False
    score_changed: bool = False


class ReviewResponse(BaseModel):
    review_id: str
    case_id: str
    reviewer_id: str
    ai_engine: str
    status: str
    overall_score: float | None = None
    coaching_summary: str | None = None
    scores: list[ReviewScoreResponse] = []
    created_at: datetime | None = None


class UpdateScoreRequest(BaseModel):
    question_id: str
    score: int | None = Field(None, ge=1, le=5)
    comment: str | None = None
    is_na: bool = False
    justification: str | None = None


class FinaliseRequest(BaseModel):
    manager_comment: str | None = None
    overall_score_override: float | None = Field(None, ge=0.0, le=5.0)
    override_justification: str | None = None


class RecommendationResponse(BaseModel):
    id: str
    case_id: str
    case_number: str | None = None
    case_subject: str | None = None
    reason: str
    status: str
    recommended_at: datetime | None = None


class RecommendationActionRequest(BaseModel):
    action: str  # accept | dismiss
    dismiss_reason: str | None = None
    ai_engine: str | None = "ollama"


class RubricCategoryResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    weight: float
    question_count: int
    is_active: bool


class RubricQuestionResponse(BaseModel):
    id: str
    category_id: str
    question_text: str
    score_1_definition: str
    score_3_definition: str
    score_5_definition: str
    allows_na: bool
    is_active: bool
