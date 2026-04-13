"""Unit tests for analytics service."""

from app.modules.analytics.service import AnalyticsService


class TestDashboardMetrics:
    def test_returns_all_fields(self):
        svc = AnalyticsService(org_id="org-001")
        m = svc.get_dashboard_metrics()
        assert m.open_cases > 0
        assert m.sla_compliance_pct > 0
        assert m.csat_score > 0
        assert m.avg_resolution_days > 0

    def test_volume_trend_length(self):
        svc = AnalyticsService(org_id="org-001")
        data = svc.get_volume_trend(30)
        assert len(data) == 30
        for d in data:
            assert d.opened >= 0
            assert d.resolved >= 0

    def test_priority_distribution_sums(self):
        svc = AnalyticsService(org_id="org-001")
        p = svc.get_priority_distribution()
        total = p.p1 + p.p2 + p.p3 + p.p4
        assert total == 47  # Matches open_cases

    def test_engineer_workload(self):
        svc = AnalyticsService(org_id="org-001")
        engineers = svc.get_engineer_workload()
        assert len(engineers) >= 5
        for e in engineers:
            assert e.case_count >= 0
            assert 0 <= e.capacity_pct <= 100

    def test_attention_cases_sorted_by_priority(self):
        svc = AnalyticsService(org_id="org-001")
        cases = svc.get_attention_cases()
        assert len(cases) > 0
        # First case should be highest priority
        assert cases[0].priority == "P1"

    def test_sla_metrics(self):
        svc = AnalyticsService(org_id="org-001")
        sla = svc.get_sla_metrics()
        assert sla.overall_compliance > 0
        assert sla.within_sla + sla.breached + sla.at_risk == 47

    def test_workload_metrics(self):
        svc = AnalyticsService(org_id="org-001")
        wl = svc.get_workload_metrics()
        assert wl.avg_load > 0
        assert wl.total_capacity > 0

    def test_trends(self):
        svc = AnalyticsService(org_id="org-001")
        trend = svc.get_trends("resolution_time")
        assert len(trend) == 8
        for t in trend:
            assert t.value > 0


class TestPredictions:
    def test_heuristic_p1_high_risk(self):
        from app.modules.predictions.service import PredictionService

        svc = PredictionService(org_id="org-001")
        pred = svc._heuristic_prediction(
            {
                "id": "c-001",
                "sf_case_number": "001",
                "priority": "P1",
                "case_age_days": 20,
                "sla_status": "Breached",
                "is_escalated": True,
            }
        )
        assert pred.risk_level == "high"
        assert pred.risk_score > 0.6
        assert len(pred.contributing_factors) >= 3

    def test_heuristic_p4_low_risk(self):
        from app.modules.predictions.service import PredictionService

        svc = PredictionService(org_id="org-001")
        pred = svc._heuristic_prediction(
            {
                "id": "c-002",
                "sf_case_number": "002",
                "priority": "P4",
                "case_age_days": 2,
            }
        )
        assert pred.risk_level == "low"
        assert pred.risk_score < 0.3

    def test_at_risk_cases(self):
        from app.modules.predictions.service import PredictionService

        svc = PredictionService(org_id="org-001")
        cases = svc.get_at_risk_cases()
        assert len(cases) >= 2
        # All should be high or medium
        for c in cases:
            assert c.risk_level in ("high", "medium")

    def test_heuristic_score_capped_at_1(self):
        from app.modules.predictions.service import PredictionService

        svc = PredictionService(org_id="org-001")
        pred = svc._heuristic_prediction(
            {
                "id": "c-003",
                "sf_case_number": "003",
                "priority": "P1",
                "case_age_days": 30,
                "sla_status": "Breached",
                "is_escalated": True,
            }
        )
        assert pred.risk_score <= 1.0
