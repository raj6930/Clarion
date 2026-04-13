"""004 — Review and intelligence tables.

Revision ID: 004_review_intelligence_tables
Create Date: 2026-04-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "004_review_intelligence_tables"
down_revision = "003_anonymisation_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── rubric_categories ───
    op.create_table(
        "rubric_categories",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("weight", sa.Numeric(3, 2), nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False),
        sa.Column("is_conditional", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("condition_expression", JSONB, nullable=True),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("has_been_used", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_rubric_cat_org", "rubric_categories", ["org_id"])

    # ─── rubric_questions ───
    op.create_table(
        "rubric_questions",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("category_id", UUID, sa.ForeignKey("rubric_categories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_text", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("score_1_definition", sa.Text, nullable=False),
        sa.Column("score_3_definition", sa.Text, nullable=False),
        sa.Column("score_5_definition", sa.Text, nullable=False),
        sa.Column("na_validity_guidance", sa.Text, nullable=True),
        sa.Column("example_evidence", sa.Text, nullable=True),
        sa.Column("coaching_guidance", sa.Text, nullable=True),
        sa.Column("allows_na", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("sort_order", sa.Integer, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("has_been_used", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_rubric_q_cat", "rubric_questions", ["category_id"])

    # ─── reviews ───
    op.create_table(
        "reviews",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_id", UUID, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("team_id", UUID, sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewer_id", UUID, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("ai_engine_used", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("selection_source", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("trigger_reason", JSONB, nullable=True),
        sa.Column("overall_score_calculated", sa.Numeric(3, 1), nullable=True),
        sa.Column("overall_score_override", sa.Numeric(3, 1), nullable=True),
        sa.Column("override_justification", sa.Text, nullable=True),
        sa.Column("coaching_summary", sa.Text, nullable=True),
        sa.Column("manager_overall_comment", sa.Text, nullable=True),
        sa.Column("anonymisation_session_id", UUID, sa.ForeignKey("anon_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pdf_generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("emailed_to_engineer_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("engineer_email", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_reviews_case", "reviews", ["case_id"])
    op.create_index("ix_reviews_reviewer", "reviews", ["reviewer_id"])
    op.create_index("ix_reviews_status", "reviews", ["status"])
    op.create_index("ix_reviews_org_team", "reviews", ["org_id", "team_id"])

    # ─── review_scores ───
    op.create_table(
        "review_scores",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("review_id", UUID, sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", UUID, sa.ForeignKey("rubric_questions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("question_text_snapshot", sa.Text, nullable=False),
        sa.Column("category_name_snapshot", sa.String(255), nullable=False),
        sa.Column("weight_snapshot", sa.Numeric(3, 2), nullable=False),
        sa.Column("ai_score", sa.SmallInteger, nullable=True),
        sa.Column("ai_comment", sa.Text, nullable=True),
        sa.Column("ai_evidence_event_ids", JSONB, nullable=True),
        sa.Column("ai_coaching_suggestion", sa.Text, nullable=True),
        sa.Column("manager_score", sa.SmallInteger, nullable=True),
        sa.Column("manager_comment", sa.Text, nullable=True),
        sa.Column("is_na", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("score_changed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("change_justification", sa.Text, nullable=True),
        sa.Column("ai_re_evaluated", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_review_scores_review", "review_scores", ["review_id"])

    # ─── review_comments ───
    op.create_table(
        "review_comments",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("review_id", UUID, sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", UUID, sa.ForeignKey("rubric_categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("comment_text", sa.Text, nullable=False),
        sa.Column("author_type", sa.String(20), nullable=False),
        sa.Column("author_id", UUID, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    # ─── review_selection_rules ───
    op.create_table(
        "review_selection_rules",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("rule_type", sa.String(50), nullable=False),
        sa.Column("condition_expression", JSONB, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("priority", sa.Integer, nullable=False, server_default="100"),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    # ─── review_recommendations ───
    op.create_table(
        "review_recommendations",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_id", UUID, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", UUID, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("team_id", UUID, sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("review_selection_rule_id", UUID, sa.ForeignKey("review_selection_rules.id", ondelete="SET NULL"), nullable=True),
        sa.Column("recommended_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("actioned_by", UUID, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actioned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dismiss_reason", sa.Text, nullable=True),
        sa.Column("review_id", UUID, sa.ForeignKey("reviews.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_recommendations_status", "review_recommendations", ["status"])
    op.create_index("ix_recommendations_org", "review_recommendations", ["org_id", "team_id"])

    # ─── technical_review_requests ───
    op.create_table(
        "technical_review_requests",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("review_id", UUID, sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requested_by", UUID, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("reviewer_name", sa.String(255), nullable=False),
        sa.Column("reviewer_email", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("pdf_snapshot", sa.LargeBinary, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="sent"),
    )

    # ─── predictions ───
    op.create_table(
        "predictions",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_id", UUID, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prediction_type", sa.String(50), nullable=False),
        sa.Column("prediction_source", sa.String(50), nullable=False),
        sa.Column("risk_score", sa.Numeric(3, 2), nullable=False),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=False),
        sa.Column("contributing_factors", JSONB, nullable=False),
        sa.Column("reasoning", sa.Text, nullable=True),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_predictions_case", "predictions", ["case_id"])
    op.create_index("ix_predictions_type", "predictions", ["prediction_type"])

    # ─── sentiment_scores ───
    op.create_table(
        "sentiment_scores",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_event_id", UUID, sa.ForeignKey("case_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("case_id", UUID, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sentiment", sa.String(20), nullable=False),
        sa.Column("score", sa.Numeric(3, 2), nullable=False),
        sa.Column("evidence", sa.Text, nullable=True),
        sa.Column("ai_engine", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_sentiment_case", "sentiment_scores", ["case_id"])


def downgrade() -> None:
    op.drop_table("sentiment_scores")
    op.drop_table("predictions")
    op.drop_table("technical_review_requests")
    op.drop_table("review_recommendations")
    op.drop_table("review_selection_rules")
    op.drop_table("review_comments")
    op.drop_table("review_scores")
    op.drop_table("reviews")
    op.drop_table("rubric_questions")
    op.drop_table("rubric_categories")
