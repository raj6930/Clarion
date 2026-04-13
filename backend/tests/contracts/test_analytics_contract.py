"""Contract tests for analytics and predictions schemas."""

from app.modules.analytics.schemas import (
    AttentionCaseResponse,
    DashboardMetricsResponse,
    VolumeDataPointResponse,
)
from app.modules.predictions.schemas import ContributingFactor, PredictionResponse


class TestDashboardContract:
    def test_metrics_response(self):
        m = DashboardMetricsResponse(
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
        assert m.open_cases == 47

    def test_attention_case(self):
        c = AttentionCaseResponse(
            case_id="c-001",
            case_number="00798234",
            subject="SSO failure",
            owner="V. Singh",
            age_days=18,
            priority="P1",
            sla_status="breached",
            risk="high",
            sentiment="frustrated",
        )
        assert c.sentiment == "frustrated"

    def test_volume_data(self):
        v = VolumeDataPointResponse(date="2026-04-01", opened=5, resolved=3)
        assert v.opened > v.resolved


class TestPredictionContract:
    def test_prediction_response(self):
        p = PredictionResponse(
            case_id="c-001",
            case_number="001",
            prediction_type="escalation_risk",
            risk_score=0.85,
            confidence=0.90,
            risk_level="high",
            contributing_factors=[ContributingFactor(factor="SLA breached", impact="high")],
            reasoning="High risk",
            source="llm_reasoning",
        )
        assert p.risk_score > 0.8
        assert len(p.contributing_factors) == 1
