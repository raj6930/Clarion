"""Analytics module Pydantic schemas."""

from pydantic import BaseModel


class DashboardMetricsResponse(BaseModel):
    open_cases: int
    open_cases_change: int
    p1p2_active: int
    p1p2_change: int
    avg_resolution_days: float
    resolution_change: float
    sla_compliance_pct: float
    sla_change: float
    csat_score: float
    csat_change: float
    active_escalations: int


class VolumeDataPointResponse(BaseModel):
    date: str
    opened: int
    resolved: int


class PriorityDistributionResponse(BaseModel):
    p1: int
    p2: int
    p3: int
    p4: int


class EngineerWorkloadResponse(BaseModel):
    engineer_name: str
    engineer_initials: str
    case_count: int
    capacity_pct: float


class AttentionCaseResponse(BaseModel):
    case_id: str
    case_number: str
    subject: str
    owner: str
    age_days: int
    priority: str
    sla_status: str
    risk: str
    sentiment: str | None = None


class SLAMetricsResponse(BaseModel):
    overall_compliance: float
    within_sla: int
    breached: int
    at_risk: int
    by_priority: dict


class TrendDataPointResponse(BaseModel):
    period: str
    value: float


class DashboardDataResponse(BaseModel):
    """Complete dashboard payload for the widget system."""

    metrics: DashboardMetricsResponse
    volume: list[VolumeDataPointResponse]
    priority: PriorityDistributionResponse
    engineers: list[EngineerWorkloadResponse]
    attention_cases: list[AttentionCaseResponse]
    sla: SLAMetricsResponse
