"""002 — Case data tables: cases, case_events, case_attachments, accounts.

Revision ID: 002_case_data_tables
Create Date: 2026-04-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "002_case_data_tables"
down_revision = "001_core_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── accounts ───
    op.create_table(
        "accounts",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sf_account_id", sa.String(18), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("account_type", sa.String(255), nullable=True),
        sa.Column("industry", sa.String(255), nullable=True),
        sa.Column("billing_country", sa.String(100), nullable=True),
        sa.Column("account_region", sa.String(100), nullable=True),
        sa.Column("total_cases", sa.Integer, nullable=False, server_default="0"),
        sa.Column("open_cases", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_platinum", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_accounts_sf_id_org", "accounts", ["sf_account_id", "org_id"], unique=True)
    op.create_index("ix_accounts_name", "accounts", ["name"])

    # ─── cases ───
    op.create_table(
        "cases",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("sf_case_id", sa.String(18), nullable=False),
        sa.Column("sf_case_number", sa.String(20), nullable=False),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("team_id", UUID, sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("account_id", UUID, sa.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True),

        # Case header
        sa.Column("subject", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(100), nullable=False),
        sa.Column("priority", sa.String(50), nullable=False),
        sa.Column("case_owner", sa.String(255), nullable=False),
        sa.Column("case_owner_name", sa.String(255), nullable=True),
        sa.Column("case_origin", sa.String(100), nullable=True),
        sa.Column("case_type", sa.String(100), nullable=True),
        sa.Column("case_reason", sa.String(255), nullable=True),

        # Contact
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(50), nullable=True),

        # Product and classification (SF-validated)
        sa.Column("product", sa.String(255), nullable=True),
        sa.Column("product_family", sa.String(255), nullable=True),
        sa.Column("support_area", sa.String(255), nullable=True),
        sa.Column("support_sub_area", sa.String(255), nullable=True),
        sa.Column("environment", sa.String(100), nullable=True),
        sa.Column("product_version", sa.String(100), nullable=True),
        sa.Column("sub_status", sa.String(100), nullable=True),

        # Dates
        sa.Column("opened_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_modified_sf", sa.DateTime(timezone=True), nullable=False),
        sa.Column("case_age_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_customer_contact_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_outbound_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),

        # SLA and survey (SF-validated)
        sa.Column("sla_status", sa.String(100), nullable=True),
        sa.Column("sla_breached", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("resolved_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("csat_rating", sa.String(50), nullable=True),
        sa.Column("survey_response", sa.String(100), nullable=True),
        sa.Column("article_linked", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("platinum_customer", sa.Boolean, nullable=False, server_default="false"),

        # Escalation and resolution (SF-validated)
        sa.Column("is_escalated", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("escalated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("escalation_reason", sa.Text, nullable=True),
        sa.Column("escalation_category", sa.String(255), nullable=True),
        sa.Column("management_escalation", sa.String(100), nullable=True),
        sa.Column("internal_escalation", sa.String(100), nullable=True),
        sa.Column("resolution_summary", sa.Text, nullable=True),
        sa.Column("root_cause", sa.Text, nullable=True),
        sa.Column("workaround_provided", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("workaround_summary", sa.Text, nullable=True),
        sa.Column("bug_number", sa.String(100), nullable=True),
        sa.Column("trcr_number", sa.String(100), nullable=True),
        sa.Column("trcr_status", sa.String(100), nullable=True),
        sa.Column("trcr_type", sa.String(100), nullable=True),

        # Relationships
        sa.Column("parent_case_id", UUID, sa.ForeignKey("cases.id", ondelete="SET NULL"), nullable=True),
        sa.Column("related_case_ids", JSONB, nullable=True),
        sa.Column("is_duplicate", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("sf_custom_fields", JSONB, nullable=True),

        # Denormalised counts
        sa.Column("total_event_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_email_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_comment_count", sa.Integer, nullable=False, server_default="0"),

        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_cases_sf_id_org", "cases", ["sf_case_id", "org_id"], unique=True)
    op.create_index("ix_cases_case_number", "cases", ["sf_case_number"])
    op.create_index("ix_cases_case_owner", "cases", ["case_owner"])
    op.create_index("ix_cases_status", "cases", ["status"])
    op.create_index("ix_cases_priority", "cases", ["priority"])
    op.create_index("ix_cases_account", "cases", ["account_id"])
    op.create_index("ix_cases_team", "cases", ["team_id"])
    op.create_index("ix_cases_last_modified", "cases", ["last_modified_sf"])
    op.create_index("ix_cases_opened", "cases", ["opened_date"])

    # ─── case_events ───
    op.create_table(
        "case_events",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_id", UUID, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_source", sa.String(50), nullable=False),
        sa.Column("sf_record_id", sa.String(18), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sequence_number", sa.Integer, nullable=False),

        # Actor
        sa.Column("actor", sa.String(255), nullable=True),
        sa.Column("actor_email", sa.String(255), nullable=True),
        sa.Column("actor_type", sa.String(50), nullable=False, server_default="unknown"),

        # Communication
        sa.Column("direction", sa.String(20), nullable=True),
        sa.Column("subject", sa.Text, nullable=True),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("body_html", sa.Text, nullable=True),
        sa.Column("is_public", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("language_detected", sa.String(10), nullable=True),
        sa.Column("word_count", sa.Integer, nullable=True),

        # Email-specific
        sa.Column("from_address", sa.String(255), nullable=True),
        sa.Column("from_name", sa.String(255), nullable=True),
        sa.Column("to_addresses", JSONB, nullable=True),
        sa.Column("cc_addresses", JSONB, nullable=True),
        sa.Column("bcc_addresses", JSONB, nullable=True),
        sa.Column("thread_id", sa.String(255), nullable=True),
        sa.Column("is_first_response", sa.Boolean, nullable=False, server_default="false"),

        # Threading
        sa.Column("parent_event_id", UUID, sa.ForeignKey("case_events.id", ondelete="SET NULL"), nullable=True),

        # Feed-specific
        sa.Column("feed_type", sa.String(50), nullable=True),
        sa.Column("feed_visibility", sa.String(50), nullable=True),

        # Task-specific
        sa.Column("task_type", sa.String(100), nullable=True),
        sa.Column("task_status", sa.String(100), nullable=True),
        sa.Column("task_due_date", sa.Date, nullable=True),
        sa.Column("task_completed_date", sa.Date, nullable=True),
        sa.Column("call_duration_seconds", sa.Integer, nullable=True),

        # Field change
        sa.Column("field_name", sa.String(100), nullable=True),
        sa.Column("field_label", sa.String(255), nullable=True),
        sa.Column("old_value", sa.Text, nullable=True),
        sa.Column("new_value", sa.Text, nullable=True),

        # Attachments
        sa.Column("has_attachments", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("attachment_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("metadata", JSONB, nullable=True),

        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_events_case_ts", "case_events", ["case_id", "timestamp"])
    op.create_index("ix_events_case_seq", "case_events", ["case_id", "sequence_number"])
    op.create_index("ix_events_type", "case_events", ["event_type"])
    op.create_index("ix_events_sf_id", "case_events", ["sf_record_id"])

    # ─── case_attachments ───
    op.create_table(
        "case_attachments",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_id", UUID, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("case_event_id", UUID, sa.ForeignKey("case_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sf_attachment_id", sa.String(18), nullable=True),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=True),
        sa.Column("content_type", sa.String(100), nullable=True),
        sa.Column("sf_download_url", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_attachments_case", "case_attachments", ["case_id"])

    # ─── sync_log ───
    op.create_table(
        "sync_log",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sync_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("records_synced", sa.Integer, nullable=True),
        sa.Column("records_failed", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("triggered_by", sa.String(100), nullable=True),
    )
    op.create_index("ix_sync_log_org_type", "sync_log", ["org_id", "sync_type"])


def downgrade() -> None:
    op.drop_table("sync_log")
    op.drop_table("case_attachments")
    op.drop_table("case_events")
    op.drop_table("cases")
    op.drop_table("accounts")
