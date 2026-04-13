"""Analytics module API routes. Feeds the dashboard widget system."""

from app.auth.dependencies import CurrentUser, get_current_user
from app.modules.analytics.schemas import (
    AttentionCaseResponse,
    DashboardDataResponse,
    DashboardMetricsResponse,
    EngineerWorkloadResponse,
    PriorityDistributionResponse,
    SLAMetricsResponse,
    VolumeDataPointResponse,
)
from app.modules.analytics.service import AnalyticsService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardDataResponse)
async def get_dashboard_data(user: CurrentUser = Depends(get_current_user)):
    """Complete dashboard payload — feeds all widgets in every layout preset."""
    svc = AnalyticsService(org_id=user.org_id)
    metrics = svc.get_dashboard_metrics()
    volume = svc.get_volume_trend(30)
    priority = svc.get_priority_distribution()
    engineers = svc.get_engineer_workload()
    attention = svc.get_attention_cases()
    sla = svc.get_sla_metrics()

    return DashboardDataResponse(
        metrics=DashboardMetricsResponse(**metrics.__dict__),
        volume=[VolumeDataPointResponse(**v.__dict__) for v in volume],
        priority=PriorityDistributionResponse(**priority.__dict__),
        engineers=[EngineerWorkloadResponse(**e.__dict__) for e in engineers],
        attention_cases=[AttentionCaseResponse(**c.__dict__) for c in attention],
        sla=SLAMetricsResponse(
            overall_compliance=sla.overall_compliance,
            within_sla=sla.within_sla,
            breached=sla.breached,
            at_risk=sla.at_risk,
            by_priority=sla.by_priority,
        ),
    )


@router.get("/sla", response_model=SLAMetricsResponse)
async def get_sla_metrics(user: CurrentUser = Depends(get_current_user)):
    svc = AnalyticsService(org_id=user.org_id)
    sla = svc.get_sla_metrics()
    return SLAMetricsResponse(
        overall_compliance=sla.overall_compliance,
        within_sla=sla.within_sla,
        breached=sla.breached,
        at_risk=sla.at_risk,
        by_priority=sla.by_priority,
    )


@router.get("/workload")
async def get_workload(user: CurrentUser = Depends(get_current_user)):
    svc = AnalyticsService(org_id=user.org_id)
    wl = svc.get_workload_metrics()
    return {
        "data": {
            "avg_load": wl.avg_load,
            "max_load": wl.max_load,
            "total_capacity": wl.total_capacity,
            "engineers": [e.__dict__ for e in wl.engineers],
        }
    }


@router.get("/trends")
async def get_trends(metric: str = "resolution_time", user: CurrentUser = Depends(get_current_user)):
    svc = AnalyticsService(org_id=user.org_id)
    trend = svc.get_trends(metric)
    return {"data": [{"period": t.period, "value": t.value} for t in trend]}


@router.get("/patterns")
async def get_patterns(user: CurrentUser = Depends(get_current_user)):
    """AI-detected patterns. Phase 8+: live AI analysis."""
    return {
        "data": [
            {
                "pattern": "EcoSys performance issues",
                "case_count": 5,
                "trend": "increasing",
                "first_seen": "2026-03-01",
            },
            {
                "pattern": "SSO/Azure AD integration",
                "case_count": 3,
                "trend": "stable",
                "first_seen": "2026-02-15",
            },
        ]
    }


@router.post("/report")
async def generate_report(user: CurrentUser = Depends(get_current_user)):
    return {"data": {"report_id": "rpt-001", "status": "generating"}}
