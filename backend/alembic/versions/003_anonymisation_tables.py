"""003 — Anonymisation tables: sessions, mappings, dictionary, rules.

Revision ID: 003_anonymisation_tables
Create Date: 2026-04-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "003_anonymisation_tables"
down_revision = "002_case_data_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── anon_sessions ───
    op.create_table(
        "anon_sessions",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scope", sa.String(20), nullable=False, server_default="session"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending_review"),
        sa.Column("target_engine", sa.String(50), nullable=False),
        sa.Column("source_text_hash", sa.String(64), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("entity_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("flagged_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_anon_sessions_user", "anon_sessions", ["user_id"])
    op.create_index("ix_anon_sessions_org", "anon_sessions", ["org_id"])

    # ─── anon_mappings ───
    op.create_table(
        "anon_mappings",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("session_id", UUID, sa.ForeignKey("anon_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("original_value", sa.Text, nullable=False),  # ENCRYPTED at app layer
        sa.Column("pseudonym", sa.String(100), nullable=False),
        sa.Column("detection_stage", sa.String(20), nullable=False),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=False),
        sa.Column("is_false_positive", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_anon_mappings_session", "anon_mappings", ["session_id"])
    op.create_index("ix_anon_mappings_org_pseudo", "anon_mappings", ["org_id", "pseudonym"])

    # ─── anon_dictionary ───
    op.create_table(
        "anon_dictionary",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("term", sa.String(500), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("match_mode", sa.String(20), nullable=False, server_default="exact"),
        sa.Column("added_by", UUID, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.String(30), nullable=False, server_default="manual"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_anon_dict_org_term", "anon_dictionary", ["org_id", "term"])

    # ─── anon_rules ───
    op.create_table(
        "anon_rules",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_pattern", sa.String(255), nullable=False),
        sa.Column("action", sa.String(20), nullable=False, server_default="anonymise"),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_anon_rules_org", "anon_rules", ["org_id"])


def downgrade() -> None:
    op.drop_table("anon_rules")
    op.drop_table("anon_dictionary")
    op.drop_table("anon_mappings")
    op.drop_table("anon_sessions")
