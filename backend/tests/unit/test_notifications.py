"""Unit tests for alert rule engine and notification service."""

from datetime import UTC, datetime

from app.modules.notifications.rules import DEFAULT_ALERT_RULES, AlertRule, AlertRuleEngine
from app.modules.notifications.service import NotificationService


class TestDefaultRules:
    def test_5_default_rules(self):
        assert len(DEFAULT_ALERT_RULES) == 5

    def test_all_have_channels(self):
        for r in DEFAULT_ALERT_RULES:
            assert len(r.channels) > 0
            assert "in_app" in r.channels

    def test_all_have_debounce(self):
        for r in DEFAULT_ALERT_RULES:
            assert r.debounce_minutes > 0

    def test_p1_rule_is_critical(self):
        p1_rule = next(r for r in DEFAULT_ALERT_RULES if r.name == "P1 No Update")
        assert p1_rule.severity == "critical"
        assert "email" in p1_rule.channels


class TestRuleEvaluation:
    def test_equality_match(self):
        engine = AlertRuleEngine(org_id="org-001")
        rule = AlertRule(
            id="r-1",
            name="Test",
            condition={"field": "priority", "operator": "==", "value": "P1"},
            severity="high",
            channels=["in_app"],
            recipients={"type": "role", "ids": ["manager"]},
            schedule_cron="* * * * *",
        )
        cases = [
            {"id": "c1", "sf_case_number": "001", "subject": "P1 case", "priority": "P1"},
            {"id": "c2", "sf_case_number": "002", "subject": "P3 case", "priority": "P3"},
        ]
        matches = engine.evaluate(rule, cases)
        assert len(matches) == 1
        assert matches[0].case_id == "c1"

    def test_greater_than_match(self):
        engine = AlertRuleEngine(org_id="org-001")
        rule = AlertRule(
            id="r-2",
            name="Old Cases",
            condition={"field": "case_age_days", "operator": ">", "value": 10},
            severity="medium",
            channels=["in_app"],
            recipients={"type": "team", "ids": []},
            schedule_cron="* * * * *",
        )
        cases = [
            {"id": "c1", "sf_case_number": "001", "subject": "Old", "case_age_days": 15},
            {"id": "c2", "sf_case_number": "002", "subject": "New", "case_age_days": 3},
        ]
        matches = engine.evaluate(rule, cases)
        assert len(matches) == 1

    def test_inactive_rule_skipped(self):
        engine = AlertRuleEngine(org_id="org-001")
        rule = AlertRule(
            id="r-3",
            name="Disabled",
            condition={"field": "priority", "operator": "==", "value": "P1"},
            severity="high",
            channels=["in_app"],
            recipients={"type": "team", "ids": []},
            schedule_cron="* * * * *",
            is_active=False,
        )
        matches = engine.evaluate(rule, [{"id": "c1", "priority": "P1", "sf_case_number": "1", "subject": "x"}])
        assert len(matches) == 0

    def test_debounce_prevents_repeat(self):
        recent = [{"rule_id": "r-4", "case_id": "c1", "sent_at": datetime.now(UTC)}]
        engine = AlertRuleEngine(org_id="org-001", recent_alerts=recent)
        rule = AlertRule(
            id="r-4",
            name="Test",
            condition={"field": "priority", "operator": "==", "value": "P1"},
            severity="high",
            channels=["in_app"],
            recipients={"type": "team", "ids": []},
            schedule_cron="* * * * *",
            debounce_minutes=60,
        )
        matches = engine.evaluate(rule, [{"id": "c1", "priority": "P1", "sf_case_number": "1", "subject": "x"}])
        assert len(matches) == 0  # Debounced

    def test_boolean_condition(self):
        engine = AlertRuleEngine(org_id="org-001")
        rule = AlertRule(
            id="r-5",
            name="Escalated",
            condition={"field": "is_escalated", "operator": "is_true", "value": None},
            severity="high",
            channels=["in_app"],
            recipients={"type": "team", "ids": []},
            schedule_cron="* * * * *",
        )
        cases = [
            {"id": "c1", "sf_case_number": "1", "subject": "x", "is_escalated": True},
            {"id": "c2", "sf_case_number": "2", "subject": "y", "is_escalated": False},
        ]
        matches = engine.evaluate(rule, cases)
        assert len(matches) == 1

    def test_evaluate_all_rules(self):
        engine = AlertRuleEngine(org_id="org-001")
        cases = [
            {
                "id": "c1",
                "sf_case_number": "1",
                "subject": "P1",
                "priority": "P1",
                "is_escalated": True,
                "sla_status": "Breached",
                "case_age_days": 20,
            },
        ]
        matches = engine.evaluate_all(DEFAULT_ALERT_RULES, cases)
        assert len(matches) >= 2  # Should match P1 + SLA + escalation rules


class TestNotificationService:
    def test_send_in_app(self):
        svc = NotificationService(org_id="org-001")
        notif = svc.send(user_id="u-001", channel="in_app", title="Test", body="Body", severity="info")
        assert notif.status == "sent"
        assert notif.sent_at is not None

    def test_unread_count(self):
        svc = NotificationService(org_id="org-001")
        svc.send("u-001", "in_app", "A", "B", "info")
        svc.send("u-001", "in_app", "C", "D", "high")
        svc.send("u-002", "in_app", "E", "F", "info")
        assert svc.get_unread_count("u-001") == 2
        assert svc.get_unread_count("u-002") == 1

    def test_mark_read(self):
        svc = NotificationService(org_id="org-001")
        notif = svc.send("u-001", "in_app", "Test", "Body", "info")
        assert svc.get_unread_count("u-001") == 1
        svc.mark_read(notif.id)
        assert svc.get_unread_count("u-001") == 0

    def test_mark_all_read(self):
        svc = NotificationService(org_id="org-001")
        svc.send("u-001", "in_app", "A", "B", "info")
        svc.send("u-001", "in_app", "C", "D", "high")
        count = svc.mark_all_read("u-001")
        assert count == 2
        assert svc.get_unread_count("u-001") == 0

    def test_get_for_user(self):
        svc = NotificationService(org_id="org-001")
        svc.send("u-001", "in_app", "A", "B", "info")
        svc.send("u-002", "in_app", "C", "D", "info")
        result = svc.get_for_user("u-001")
        assert len(result) == 1

    def test_email_stub_succeeds(self):
        svc = NotificationService(org_id="org-001")
        notif = svc.send("u-001", "email", "Subject", "Body", "info")
        assert notif.status == "sent"
