"""
Analytics Service
Aggregates case data into operational metrics, trends, and patterns.
Phase 7: Mock data for UI development. Phase 8+: Live PostgreSQL queries.
"""

import logging
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

logger = logging.getLogger("clarion.analytics")


@dataclass
class DashboardMetrics:
    """Complete metrics payload for the dashboard widget system."""

    open_cases: int = 0
    open_cases_change: int = 0
    p1p2_active: int = 0
    p1p2_change: int = 0
    avg_resolution_days: float = 0.0
    resolution_change: float = 0.0
    sla_compliance_pct: float = 0.0
    sla_change: float = 0.0
    csat_score: float = 0.0
    csat_change: float = 0.0
    active_escalations: int = 0


@dataclass
class VolumeDataPoint:
    date: str
    opened: int = 0
    resolved: int = 0


@dataclass
class PriorityDistribution:
    p1: int = 0
    p2: int = 0
    p3: int = 0
    p4: int = 0


@dataclass
class EngineerWorkload:
    engineer_name: str
    engineer_initials: str
    case_count: int = 0
    capacity_pct: float = 0.0


@dataclass
class AttentionCase:
    case_id: str
    case_number: str
    subject: str
    owner: str
    age_days: int
    priority: str
    sla_status: str
    risk: str
    sentiment: str | None = None


@dataclass
class TrendDataPoint:
    period: str
    value: float


@dataclass
class SLAMetrics:
    overall_compliance: float
    within_sla: int
    breached: int
    at_risk: int
    by_priority: dict = field(default_factory=dict)
    trend: list[TrendDataPoint] = field(default_factory=list)


@dataclass
class WorkloadMetrics:
    engineers: list[EngineerWorkload] = field(default_factory=list)
    avg_load: float = 0.0
    max_load: int = 0
    total_capacity: int = 0


class AnalyticsService:
    """Aggregates case data into analytics for dashboards and reports."""

    def __init__(self, org_id: str, team_id: str | None = None):
        self.org_id = org_id
        self.team_id = team_id

    def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get headline KPIs for the dashboard stat cards."""
        # Phase 7: Mock data. Phase 8+: PostgreSQL aggregation queries.
        return DashboardMetrics(
            open_cases=47,
            open_cases_change=3,
            p1p2_active=8,
            p1p2_change=-2,
            avg_resolution_days=4.2,
            resolution_change=-0.3,
            sla_compliance_pct=94.0,
            sla_change=0.0,
            csat_score=4.1,
            csat_change=0.2,
            active_escalations=2,
        )

    def get_volume_trend(self, days: int = 30) -> list[VolumeDataPoint]:
        """Get daily case volume (opened vs resolved) for the chart widget."""
        data = []
        base = datetime.now(UTC) - timedelta(days=days)
        for i in range(days):
            d = base + timedelta(days=i)
            data.append(
                VolumeDataPoint(
                    date=d.strftime("%Y-%m-%d"),
                    opened=random.randint(2, 8),
                    resolved=random.randint(1, 7),
                )
            )
        return data

    def get_priority_distribution(self) -> PriorityDistribution:
        """Get current case count by priority."""
        return PriorityDistribution(p1=3, p2=8, p3=24, p4=12)

    def get_engineer_workload(self) -> list[EngineerWorkload]:
        """Get case count per engineer with capacity indicators."""
        return [
            EngineerWorkload("Vikram Singh", "VS", 6, 85.0),
            EngineerWorkload("Tim Trulis", "TT", 5, 70.0),
            EngineerWorkload("Wolf Gassmann", "WG", 4, 55.0),
            EngineerWorkload("Haresh J", "HJ", 3, 40.0),
            EngineerWorkload("Kavitha Hare", "KH", 2, 28.0),
            EngineerWorkload("Jon-Jon Leung", "JL", 4, 55.0),
        ]

    def get_attention_cases(self) -> list[AttentionCase]:
        """Get cases requiring immediate attention (SLA risk, escalated, negative sentiment)."""
        return [
            AttentionCase(
                "c-001",
                "00798234",
                "SSO login failure after Azure AD update",
                "Vikram Singh",
                18,
                "P1",
                "breached",
                "high",
                "frustrated",
            ),
            AttentionCase(
                "c-002",
                "00803992",
                "Performance issues with application",
                "Tim Trulis",
                12,
                "P2",
                "within",
                "high",
                "negative",
            ),
            AttentionCase(
                "c-003",
                "00689632",
                "Database performance degradation",
                "Wolf Gassmann",
                45,
                "P2",
                "within",
                "medium",
                "neutral",
            ),
            AttentionCase(
                "c-004",
                "00810445",
                "Report export timeout on large datasets",
                "Haresh J",
                3,
                "P3",
                "within",
                "low",
                "neutral",
            ),
            AttentionCase(
                "c-005",
                "00812001",
                "Data import validation errors",
                "Kavitha Hare",
                1,
                "P3",
                "within",
                "low",
                "positive",
            ),
            AttentionCase(
                "c-006",
                "00807891",
                "License activation failure after renewal",
                "Jon-Jon Leung",
                8,
                "P2",
                "within",
                "medium",
                "negative",
            ),
            AttentionCase(
                "c-007",
                "00813102",
                "Custom report formatting issue",
                "Haresh J",
                2,
                "P3",
                "within",
                "low",
                "neutral",
            ),
        ]

    def get_sla_metrics(self) -> SLAMetrics:
        """Get SLA compliance breakdown."""
        return SLAMetrics(
            overall_compliance=94.0,
            within_sla=44,
            breached=2,
            at_risk=1,
            by_priority={"P1": 67.0, "P2": 88.0, "P3": 100.0, "P4": 100.0},
            trend=[
                TrendDataPoint("W1", 91.0),
                TrendDataPoint("W2", 93.0),
                TrendDataPoint("W3", 92.0),
                TrendDataPoint("W4", 94.0),
            ],
        )

    def get_workload_metrics(self) -> WorkloadMetrics:
        """Get team workload analysis."""
        engineers = self.get_engineer_workload()
        loads = [e.case_count for e in engineers]
        return WorkloadMetrics(
            engineers=engineers,
            avg_load=round(sum(loads) / len(loads), 1) if loads else 0,
            max_load=max(loads) if loads else 0,
            total_capacity=len(engineers) * 7,
        )

    def get_trends(self, metric: str, periods: int = 8) -> list[TrendDataPoint]:
        """Get trend data for a specific metric over time."""
        trend_data = {
            "resolution_time": [5.2, 4.8, 4.6, 4.5, 4.3, 4.2, 4.1, 4.2],
            "csat": [3.8, 3.9, 4.0, 3.9, 4.0, 4.1, 4.0, 4.1],
            "volume": [140, 155, 148, 162, 151, 168, 159, 147],
        }
        values = trend_data.get(metric, [0] * periods)
        return [TrendDataPoint(f"W{i + 1}", v) for i, v in enumerate(values[:periods])]
