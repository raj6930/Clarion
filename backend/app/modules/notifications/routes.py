"""Notifications module API routes."""

from app.auth.dependencies import (
    CurrentUser,
    get_current_user,
    require_admin,
    require_manager_or_admin,
)
from app.modules.notifications.rules import DEFAULT_ALERT_RULES
from app.modules.notifications.schemas import (
    AlertRuleCreateRequest,
    AlertRuleResponse,
    AlertRuleUpdateRequest,
    NotificationResponse,
    UnreadCountResponse,
)
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    status: str = None,
    user: CurrentUser = Depends(get_current_user),
):
    """List notifications for current user."""
    # Phase 8: mock data. Phase 9+: from notification_log.
    return [
        NotificationResponse(
            id="notif-0001",
            channel="in_app",
            title="[HIGH] SLA Breach Warning",
            body="Case 00798234: SSO login failure — SLA breached at 18 days",
            severity="high",
            status="sent",
            related_case_id="c-001",
            related_case_number="00798234",
        ),
        NotificationResponse(
            id="notif-0002",
            channel="in_app",
            title="[CRITICAL] P1 No Update",
            body="Case 00798234 has not been updated in 4+ hours",
            severity="critical",
            status="sent",
            related_case_id="c-001",
            related_case_number="00798234",
        ),
        NotificationResponse(
            id="notif-0003",
            channel="in_app",
            title="[MEDIUM] High Escalation Risk",
            body="Case 00803992 has 78% escalation risk — customer requesting escalation",
            severity="medium",
            status="sent",
            related_case_id="c-002",
            related_case_number="00803992",
        ),
    ]


@router.get("/unread", response_model=UnreadCountResponse)
async def get_unread_count(user: CurrentUser = Depends(get_current_user)):
    """Get unread notification count for the bell badge."""
    return UnreadCountResponse(count=3)


@router.put("/{notification_id}/read")
async def mark_read(notification_id: str, user: CurrentUser = Depends(get_current_user)):
    return {"data": {"read": True}}


@router.put("/read-all")
async def mark_all_read(user: CurrentUser = Depends(get_current_user)):
    return {"data": {"marked": 3}}


# ─── Alert Rules (Manager/Admin) ───


@router.get("/rules", response_model=list[AlertRuleResponse])
async def list_alert_rules(user: CurrentUser = Depends(require_manager_or_admin)):
    """List all alert rules."""
    return [
        AlertRuleResponse(
            id=r.id,
            name=r.name,
            description=None,
            severity=r.severity,
            channels=r.channels,
            schedule_cron=r.schedule_cron,
            debounce_minutes=r.debounce_minutes,
            is_active=r.is_active,
            is_default=True,
        )
        for r in DEFAULT_ALERT_RULES
    ]


@router.post("/rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(
    req: AlertRuleCreateRequest,
    user: CurrentUser = Depends(require_admin),
):
    """Create a custom alert rule. Admin only."""
    return AlertRuleResponse(
        id="rule-new",
        name=req.name,
        description=req.description,
        severity=req.severity,
        channels=req.channels,
        schedule_cron=req.schedule_cron,
        debounce_minutes=req.debounce_minutes,
        is_active=True,
        is_default=False,
    )


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: str,
    req: AlertRuleUpdateRequest,
    user: CurrentUser = Depends(require_admin),
):
    """Update an alert rule. Admin only."""
    return AlertRuleResponse(
        id=rule_id,
        name=req.name or "Updated Rule",
        description=req.description,
        severity=req.severity or "medium",
        channels=req.channels or ["in_app"],
        schedule_cron="0 */1 * * *",
        debounce_minutes=req.debounce_minutes or 60,
        is_active=req.is_active if req.is_active is not None else True,
        is_default=False,
    )


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(rule_id: str, user: CurrentUser = Depends(require_admin)):
    """Delete a custom alert rule. Cannot delete default rules."""
    return {"data": {"deleted": True}}
