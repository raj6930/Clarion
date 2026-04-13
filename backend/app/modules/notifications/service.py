"""
Notification Service
Dispatches notifications to configured channels: in_app, email, teams, slack.
Phase 8: In-app + email stubs. Phase 9+: Teams/Slack webhooks.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

logger = logging.getLogger("clarion.notifications")


@dataclass
class Notification:
    id: str
    user_id: str
    channel: str  # in_app | email | teams | slack
    title: str
    body: str
    severity: str  # critical | high | medium | low | info
    status: str = "pending"  # pending | sent | failed | read
    related_case_id: str | None = None
    related_case_number: str | None = None
    alert_rule_id: str | None = None
    sent_at: datetime | None = None
    read_at: datetime | None = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(UTC)


class NotificationService:
    """Dispatches and manages notifications."""

    def __init__(self, org_id: str):
        self.org_id = org_id
        # Phase 8: in-memory store. Phase 9+: PostgreSQL.
        self._store: list[Notification] = []
        self._counter = 0

    def send(
        self,
        user_id: str,
        channel: str,
        title: str,
        body: str,
        severity: str = "info",
        related_case_id: str | None = None,
        related_case_number: str | None = None,
        alert_rule_id: str | None = None,
    ) -> Notification:
        """Create and dispatch a notification."""
        self._counter += 1
        notif = Notification(
            id=f"notif-{self._counter:04d}",
            user_id=user_id,
            channel=channel,
            title=title,
            body=body,
            severity=severity,
            related_case_id=related_case_id,
            related_case_number=related_case_number,
            alert_rule_id=alert_rule_id,
        )

        # Dispatch to channel
        success = self._dispatch(notif)
        notif.status = "sent" if success else "failed"
        if success:
            notif.sent_at = datetime.now(UTC)

        self._store.append(notif)
        logger.info(f"Notification {notif.id} [{channel}] → {user_id}: {notif.status}")
        return notif

    def send_batch(self, matches: list, user_ids: list[str]) -> list[Notification]:
        """Send notifications for alert matches to specified users."""
        notifications = []
        for match in matches:
            for user_id in user_ids:
                for channel in match.rule.channels:
                    notif = self.send(
                        user_id=user_id,
                        channel=channel,
                        title=f"[{match.severity.upper()}] {match.rule.name}",
                        body=f"Case {match.case_number}: {match.case_subject}\n{match.match_reason}",
                        severity=match.severity,
                        related_case_id=match.case_id,
                        related_case_number=match.case_number,
                        alert_rule_id=match.rule.id,
                    )
                    notifications.append(notif)
        return notifications

    def get_for_user(self, user_id: str, status: str | None = None) -> list[Notification]:
        """Get notifications for a user, optionally filtered by status."""
        result = [n for n in self._store if n.user_id == user_id]
        if status:
            result = [n for n in result if n.status == status]
        return sorted(result, key=lambda n: n.created_at, reverse=True)

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread in-app notifications."""
        return sum(
            1
            for n in self._store
            if n.user_id == user_id and n.channel == "in_app" and n.read_at is None and n.status == "sent"
        )

    def mark_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        for n in self._store:
            if n.id == notification_id:
                n.read_at = datetime.now(UTC)
                n.status = "read"
                return True
        return False

    def mark_all_read(self, user_id: str) -> int:
        """Mark all in-app notifications as read for a user."""
        count = 0
        for n in self._store:
            if n.user_id == user_id and n.channel == "in_app" and n.read_at is None:
                n.read_at = datetime.now(UTC)
                n.status = "read"
                count += 1
        return count

    def _dispatch(self, notif: Notification) -> bool:
        """Dispatch to the appropriate channel."""
        if notif.channel == "in_app":
            return self._dispatch_in_app(notif)
        elif notif.channel == "email":
            return self._dispatch_email(notif)
        elif notif.channel == "teams":
            return self._dispatch_teams(notif)
        elif notif.channel == "slack":
            return self._dispatch_slack(notif)
        return False

    def _dispatch_in_app(self, notif: Notification) -> bool:
        """In-app: store for polling/WebSocket push."""
        # Phase 8: stored in memory. Phase 9+: PostgreSQL + WebSocket.
        return True

    def _dispatch_email(self, notif: Notification) -> bool:
        """Email dispatch. Phase 8: stub. Phase 9+: aiosmtplib."""
        logger.info(f"Email stub: would send '{notif.title}' to user {notif.user_id}")
        return True

    def _dispatch_teams(self, notif: Notification) -> bool:
        """Teams webhook. Phase 9+: httpx POST to webhook URL."""
        logger.info(f"Teams stub: would post '{notif.title}'")
        return True

    def _dispatch_slack(self, notif: Notification) -> bool:
        """Slack webhook. Phase 9+: httpx POST to webhook URL."""
        logger.info(f"Slack stub: would post '{notif.title}'")
        return True
