"""006 — Configuration tables: sync_config, ai_config.

Revision ID: 006_config_tables
Create Date: 2026-04-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "006_config_tables"
down_revision = "005_notification_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── sync_config ───
    op.create_table(
        "sync_config",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("sf_instance_url", sa.String(500), nullable=True),
        sa.Column("sf_auth_method", sa.String(50), nullable=False, server_default="cli"),
        sa.Column("schedule_cron", sa.String(100), nullable=False, server_default="0 */2 * * *"),
        sa.Column("account_sync_cron", sa.String(100), nullable=False, server_default="0 */4 * * *"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sync_status", sa.String(20), nullable=True),
        sa.Column("last_sync_duration_ms", sa.Integer, nullable=True),
        sa.Column("last_sync_records", sa.Integer, nullable=True),
        sa.Column("retry_max", sa.Integer, nullable=False, server_default="5"),
        sa.Column("retry_backoff_base", sa.Integer, nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    # ─── ai_config ───
    op.create_table(
        "ai_config",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine_id", sa.String(50), nullable=False),
        sa.Column("is_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("api_key", sa.Text, nullable=True),  # ENCRYPTED at app layer
        sa.Column("api_endpoint", sa.String(500), nullable=True),
        sa.Column("model_name", sa.String(100), nullable=True),
        sa.Column("monthly_budget_usd", sa.Numeric(10, 2), nullable=True),
        sa.Column("monthly_usage_usd", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("rate_limit_rpm", sa.Integer, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_ai_config_org_engine", "ai_config", ["org_id", "engine_id"], unique=True)


def downgrade() -> None:
    op.drop_table("ai_config")
    op.drop_table("sync_config")
