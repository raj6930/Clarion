"""005 — Notification tables: alert_rules, notification_log.

Revision ID: 005_notification_tables
Create Date: 2026-04-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "005_notification_tables"
down_revision = "004_review_intelligence_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── alert_rules ───
    op.create_table(
        "alert_rules",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("condition_expression", JSONB, nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("channels", JSONB, nullable=False, server_default='["in_app"]'),
        sa.Column("recipients", JSONB, nullable=False),
        sa.Column("schedule_cron", sa.String(100), nullable=False, server_default="*/30 * * * *"),
        sa.Column("quiet_hours", JSONB, nullable=True),
        sa.Column("debounce_minutes", sa.Integer, nullable=False, server_default="60"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_alert_rules_org", "alert_rules", ["org_id"])
    op.create_index("ix_alert_rules_active", "alert_rules", ["is_active"])

    # ─── notification_log ───
    op.create_table(
        "notification_log",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alert_rule_id", UUID, sa.ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_detail", sa.Text, nullable=True),
        sa.Column("related_case_id", UUID, sa.ForeignKey("cases.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_notif_user_status", "notification_log", ["user_id", "status"])
    op.create_index("ix_notif_org_created", "notification_log", ["org_id", "created_at"])
    op.create_index("ix_notif_rule_case", "notification_log", ["alert_rule_id", "related_case_id"])


def downgrade() -> None:
    op.drop_table("notification_log")
    op.drop_table("alert_rules")
