"""001 — Core identity, configuration, and audit tables.

Revision ID: 001_core_tables
Create Date: 2026-04-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET

revision = "001_core_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── Enable extensions ───
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ─── organisations ───
    op.create_table(
        "organisations",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("domain", sa.String(255), nullable=False, unique=True),
        sa.Column("logo_data", sa.LargeBinary, nullable=True),
        sa.Column("logo_mime_type", sa.String(50), nullable=True),
        sa.Column("favicon_data", sa.LargeBinary, nullable=True),
        sa.Column("primary_colour", sa.String(7), nullable=False, server_default="#1B3A5C"),
        sa.Column("accent_colour", sa.String(7), nullable=False, server_default="#2E75B6"),
        sa.Column("dark_mode_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("tos_text", sa.Text, nullable=True),
        sa.Column("privacy_policy_text", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ─── roles ───
    op.create_table(
        "roles",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permissions", JSONB, nullable=False, server_default="[]"),
        sa.Column("data_scope_type", sa.String(50), nullable=False, server_default="team"),
        sa.Column("data_scope_filter", JSONB, nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ─── users ───
    op.create_table(
        "users",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("role_id", UUID, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending_approval"),
        sa.Column("mfa_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("mfa_secret", sa.String(255), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("onboarding_complete", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_unique_constraint("uq_users_email_org", "users", ["email", "org_id"])

    # ─── teams ───
    op.create_table(
        "teams",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("manager_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ─── team_members ───
    op.create_table(
        "team_members",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("team_id", UUID, sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engineer_name", sa.String(255), nullable=False),
        sa.Column("salesforce_username", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ─── sessions ───
    op.create_table(
        "sessions",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("refresh_token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("ip_address", INET, nullable=True),
        sa.Column("revoked", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ─── user_accounts (account-based access) ───
    op.create_table(
        "user_accounts",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sf_account_id", sa.String(18), nullable=False),
        sa.Column("account_name", sa.String(255), nullable=False),
        sa.Column("account_type", sa.String(100), nullable=True),
        sa.Column("account_industry", sa.String(255), nullable=True),
        sa.Column("account_country", sa.String(100), nullable=True),
        sa.Column("enable_predictions", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("enable_sentiment", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_unique_constraint("uq_user_accounts_user_account", "user_accounts", ["user_id", "sf_account_id"])
    op.create_index("ix_user_accounts_sf_account_id", "user_accounts", ["sf_account_id"])

    # ─── terminology ───
    op.create_table(
        "terminology",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("term_key", sa.String(100), nullable=False),
        sa.Column("term_value", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_unique_constraint("uq_terminology_org_key", "terminology", ["org_id", "term_key"])

    # ─── feature_flags ───
    op.create_table(
        "feature_flags",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("module_id", sa.String(100), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_unique_constraint("uq_feature_flags_org_module", "feature_flags", ["org_id", "module_id"])

    # ─── excluded_statuses_config ───
    op.create_table(
        "excluded_statuses_config",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status_value", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_unique_constraint("uq_excluded_statuses_org_status", "excluded_statuses_config", ["org_id", "status_value"])

    # ─── audit_log (append-only) ───
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("user_id", UUID, nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("ip_address", INET, nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("outcome", sa.String(10), nullable=False, server_default="success"),
        sa.Column("metadata", JSONB, nullable=True),
    )
    op.create_index("ix_audit_log_timestamp", "audit_log", ["timestamp"])
    op.create_index("ix_audit_log_user_id", "audit_log", ["user_id"])
    op.create_index("ix_audit_log_action", "audit_log", ["action"])

    # Revoke UPDATE/DELETE on audit_log for application role
    # (applied via separate grant script in production)

    # ─── theme_config (org-level appearance) ───
    op.create_table(
        "theme_config",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("default_layout_preset", sa.String(50), nullable=False, server_default="editorial"),
        sa.Column("primary_colour", sa.String(7), nullable=False, server_default="#2563EB"),
        sa.Column("accent_colour", sa.String(7), nullable=False, server_default="#3B82F6"),
        sa.Column("font_family", sa.String(100), nullable=False, server_default="Geist Sans"),
        sa.Column("card_radius_px", sa.Integer, nullable=False, server_default="14"),
        sa.Column("density", sa.String(20), nullable=False, server_default="comfortable"),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("company_name", sa.String(200), nullable=True),
        sa.Column("dark_mode_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    # ─── user_preferences (per-user overrides) ───
    op.create_table(
        "user_preferences",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("layout_preset", sa.String(50), nullable=True),
        sa.Column("dark_mode", sa.Boolean, nullable=True),
        sa.Column("density", sa.String(20), nullable=True),
        sa.Column("font_size_scale", sa.Numeric(3, 2), nullable=True),
        sa.Column("sidebar_collapsed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("user_preferences")
    op.drop_table("theme_config")
    op.drop_table("audit_log")
    op.drop_table("excluded_statuses_config")
    op.drop_table("feature_flags")
    op.drop_table("terminology")
    op.drop_table("user_accounts")
    op.drop_table("sessions")
    op.drop_table("team_members")
    op.drop_table("teams")
    op.drop_table("users")
    op.drop_table("roles")
    op.drop_table("organisations")
