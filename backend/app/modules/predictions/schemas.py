"""Predictions module Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class ContributingFactor(BaseModel):
    factor: str
    impact: str  # high | medium | low


class PredictionResponse(BaseModel):
    case_id: str
    case_number: str
    prediction_type: str
    risk_score: float
    confidence: float
    risk_level: str
    contributing_factors: list[ContributingFactor]
    reasoning: str | None = None
    source: str
    valid_until: datetime | None = None


class PredictionRefreshRequest(BaseModel):
    case_ids: list[str]
