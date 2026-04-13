"""
Alert Rule Engine
Evaluates alert rules against case data, handles deduplication,
quiet hours, debouncing, and notification dispatch.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

logger = logging.getLogger("clarion.notifications.rules")


@dataclass
class AlertRule:
    id: str
    name: str
    condition: dict  # {field, operator, value, logical_op}
    severity: str  # critical | high | medium | low | info
    channels: list[str]  # ["in_app", "email", "teams", "slack"]
    recipients: dict  # {type: "team"|"user"|"role", ids: [...]}
    schedule_cron: str
    quiet_hours: dict | None = None  # {start, end, timezone}
    debounce_minutes: int = 60
    is_active: bool = True


@dataclass
class AlertMatch:
    """A case that matched an alert rule."""

    rule: AlertRule
    case_id: str
    case_number: str
    case_subject: str
    match_reason: str
    severity: str


class AlertRuleEngine:
    """Evaluates alert rules against case data."""

    def __init__(self, org_id: str, recent_alerts: list[dict] | None = None):
        self.org_id = org_id
        self._recent_alerts = recent_alerts or []

    def evaluate(self, rule: AlertRule, cases: list[dict]) -> list[AlertMatch]:
        """Evaluate a single rule against a list of cases. Returns matches."""
        if not rule.is_active:
            return []

        if self._in_quiet_hours(rule):
            logger.debug(f"Rule '{rule.name}' skipped (quiet hours)")
            return []

        matches = []
        for case in cases:
            if self._case_matches(rule.condition, case):
                if not self._is_debounced(rule, case.get("id", "")):
                    matches.append(
                        AlertMatch(
                            rule=rule,
                            case_id=case.get("id", ""),
                            case_number=case.get("sf_case_number", ""),
                            case_subject=case.get("subject", ""),
                            match_reason=self._build_reason(rule, case),
                            severity=rule.severity,
                        )
                    )

        logger.info(f"Rule '{rule.name}': {len(matches)} matches from {len(cases)} cases")
        return matches

    def evaluate_all(self, rules: list[AlertRule], cases: list[dict]) -> list[AlertMatch]:
        """Evaluate all rules against all cases."""
        all_matches = []
        for rule in rules:
            all_matches.extend(self.evaluate(rule, cases))
        return all_matches

    def _case_matches(self, condition: dict, case: dict) -> bool:
        """Check if a case matches a condition expression."""
        field_name = condition.get("field", "")
        operator = condition.get("operator", "")
        value = condition.get("value")
        case_value = case.get(field_name)

        if case_value is None:
            return False

        try:
            if operator == "==":
                return case_value == value
            elif operator == "!=":
                return case_value != value
            elif operator == ">":
                return float(case_value) > float(value)
            elif operator == ">=":
                return float(case_value) >= float(value)
            elif operator == "<":
                return float(case_value) < float(value)
            elif operator == "in":
                return case_value in value
            elif operator == "contains":
                return str(value).lower() in str(case_value).lower()
            elif operator == "is_true":
                return bool(case_value)
            elif operator == "is_null":
                return case_value is None
            elif operator == "hours_since_gt":
                # Check if a timestamp field is older than X hours
                if isinstance(case_value, str):
                    ts = datetime.fromisoformat(case_value.replace("Z", "+00:00"))
                    hours = (datetime.now(UTC) - ts).total_seconds() / 3600
                    return hours > float(value)
        except (ValueError, TypeError) as e:
            logger.warning(f"Condition eval error: {e}")
            return False

        return False

    def _in_quiet_hours(self, rule: AlertRule) -> bool:
        """Check if current time falls within quiet hours."""
        if not rule.quiet_hours:
            return False

        start = rule.quiet_hours.get("start", "")
        end = rule.quiet_hours.get("end", "")
        if not start or not end:
            return False

        now = datetime.now(UTC)
        try:
            start_h, start_m = map(int, start.split(":"))
            end_h, end_m = map(int, end.split(":"))
            current_minutes = now.hour * 60 + now.minute
            start_minutes = start_h * 60 + start_m
            end_minutes = end_h * 60 + end_m

            if start_minutes <= end_minutes:
                return start_minutes <= current_minutes <= end_minutes
            else:  # Crosses midnight
                return current_minutes >= start_minutes or current_minutes <= end_minutes
        except (ValueError, AttributeError):
            return False

    def _is_debounced(self, rule: AlertRule, case_id: str) -> bool:
        """Check if we recently sent an alert for this rule + case combo."""
        cutoff = datetime.now(UTC) - timedelta(minutes=rule.debounce_minutes)
        for alert in self._recent_alerts:
            if (
                alert.get("rule_id") == rule.id
                and alert.get("case_id") == case_id
                and alert.get("sent_at", datetime.min) > cutoff
            ):
                return True
        return False

    def _build_reason(self, rule: AlertRule, case: dict) -> str:
        """Build a human-readable reason for why this alert fired."""
        cond = rule.condition
        field = cond.get("field", "")
        value = case.get(field, "")
        return f"{rule.name}: {field} = {value}"


# ─── Default Alert Rules (ship with V1) ───
DEFAULT_ALERT_RULES = [
    AlertRule(
        id="rule-01",
        name="P1 No Update",
        condition={"field": "priority", "operator": "==", "value": "P1"},
        severity="critical",
        channels=["in_app", "email"],
        recipients={"type": "role", "ids": ["manager"]},
        schedule_cron="0 */4 * * *",
        debounce_minutes=240,
    ),
    AlertRule(
        id="rule-02",
        name="SLA Breach Warning",
        condition={"field": "sla_status", "operator": "==", "value": "Breached"},
        severity="high",
        channels=["in_app", "email"],
        recipients={"type": "role", "ids": ["manager"]},
        schedule_cron="0 */1 * * *",
        debounce_minutes=120,
    ),
    AlertRule(
        id="rule-03",
        name="Customer Response Gap",
        condition={"field": "case_age_days", "operator": ">", "value": 7},
        severity="medium",
        channels=["in_app"],
        recipients={"type": "team", "ids": []},
        schedule_cron="0 9 * * 1-5",
        quiet_hours={"start": "22:00", "end": "06:00", "timezone": "Australia/Sydney"},
        debounce_minutes=1440,
    ),
    AlertRule(
        id="rule-04",
        name="New Escalation",
        condition={"field": "is_escalated", "operator": "is_true", "value": None},
        severity="high",
        channels=["in_app", "email"],
        recipients={"type": "role", "ids": ["manager"]},
        schedule_cron="*/15 * * * *",
        debounce_minutes=60,
    ),
    AlertRule(
        id="rule-05",
        name="High Escalation Risk Prediction",
        condition={"field": "escalation_risk", "operator": ">", "value": 0.75},
        severity="medium",
        channels=["in_app"],
        recipients={"type": "role", "ids": ["manager"]},
        schedule_cron="0 */2 * * *",
        debounce_minutes=360,
    ),
]
