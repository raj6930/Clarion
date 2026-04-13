"""Contract tests for notifications module schemas."""

from app.modules.notifications.schemas import (
    AlertRuleCreateRequest,
    AlertRuleResponse,
    NotificationResponse,
    UnreadCountResponse,
)


class TestNotificationContract:
    def test_notification_response(self):
        n = NotificationResponse(
            id="n-001",
            channel="in_app",
            title="Test",
            body="Body",
            severity="high",
            status="sent",
        )
        assert n.severity == "high"

    def test_unread_count(self):
        u = UnreadCountResponse(count=5)
        assert u.count == 5


class TestAlertRuleContract:
    def test_create_request(self):
        req = AlertRuleCreateRequest(
            name="Custom Rule",
            condition_expression={"field": "priority", "operator": "==", "value": "P1"},
        )
        assert req.severity == "medium"
        assert req.channels == ["in_app"]

    def test_rule_response(self):
        r = AlertRuleResponse(
            id="r-001",
            name="P1 Alert",
            severity="critical",
            channels=["in_app", "email"],
            schedule_cron="0 */4 * * *",
            debounce_minutes=240,
            is_active=True,
            is_default=True,
        )
        assert r.is_default
