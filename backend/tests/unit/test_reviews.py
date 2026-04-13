"""Unit tests for case review service."""

import pytest
from app.modules.reviews.service import (
    DEFAULT_RUBRIC,
    ReviewService,
)


class TestDefaultRubric:
    def test_has_8_questions(self):
        assert len(DEFAULT_RUBRIC) == 8

    def test_4_categories(self):
        categories = set(q.category_id for q in DEFAULT_RUBRIC)
        assert len(categories) == 4

    def test_weights_sum_to_1(self):
        cat_weights = {}
        for q in DEFAULT_RUBRIC:
            cat_weights[q.category_id] = q.category_weight
        total = sum(cat_weights.values())
        assert abs(total - 1.0) < 0.01

    def test_all_have_scoring_definitions(self):
        for q in DEFAULT_RUBRIC:
            assert q.score_1_definition
            assert q.score_3_definition
            assert q.score_5_definition

    def test_na_questions_marked(self):
        na_questions = [q for q in DEFAULT_RUBRIC if q.allows_na]
        assert len(na_questions) == 2  # Root cause and Knowledge article


class TestReviewCreation:
    @pytest.mark.asyncio
    async def test_create_review(self):
        service = ReviewService(org_id="org-001")
        draft = await service.create_review(
            case_id="case-001",
            reviewer_id="user-001",
            ai_engine="ollama",
        )
        assert draft.review_id.startswith("rev-")
        assert draft.status == "draft"
        assert len(draft.scores) == 8

    @pytest.mark.asyncio
    async def test_scores_have_snapshots(self):
        service = ReviewService(org_id="org-001")
        draft = await service.create_review("case-001", "user-001")
        for score in draft.scores:
            assert score.question_text_snapshot
            assert score.category_name_snapshot
            assert score.weight_snapshot > 0


class TestScoreCalculation:
    @pytest.mark.asyncio
    async def test_overall_score(self):
        service = ReviewService(org_id="org-001")
        draft = await service.create_review("case-001", "user-001")

        # Set all AI scores to 4
        for s in draft.scores:
            s.ai_score = 4

        score = service._calculate_overall_score(draft)
        assert score == 4.0

    @pytest.mark.asyncio
    async def test_na_excluded_from_calculation(self):
        service = ReviewService(org_id="org-001")
        draft = await service.create_review("case-001", "user-001")

        for s in draft.scores:
            s.ai_score = 5
        # Mark one as N/A
        draft.scores[0].is_na = True

        score = service._calculate_overall_score(draft)
        assert score == 5.0  # N/A excluded, remaining are all 5

    @pytest.mark.asyncio
    async def test_manager_score_takes_precedence(self):
        service = ReviewService(org_id="org-001")
        draft = await service.create_review("case-001", "user-001")

        for s in draft.scores:
            s.ai_score = 3
        draft.scores[0].manager_score = 5

        score = service._calculate_overall_score(draft)
        # First question has manager=5, rest have ai=3
        assert score > 3.0


class TestManagerOverride:
    @pytest.mark.asyncio
    async def test_override_flags_change(self):
        service = ReviewService(org_id="org-001")
        draft = await service.create_review("case-001", "user-001")
        draft.scores[0].ai_score = 3

        result = service.apply_manager_score(
            draft,
            draft.scores[0].question_id,
            score=5,
            justification="Engineer handled escalation well",
        )
        assert result.score_changed
        assert result.change_justification == "Engineer handled escalation well"
        assert not result.ai_re_evaluated

    @pytest.mark.asyncio
    async def test_same_score_no_flag(self):
        service = ReviewService(org_id="org-001")
        draft = await service.create_review("case-001", "user-001")
        draft.scores[0].ai_score = 4

        result = service.apply_manager_score(
            draft,
            draft.scores[0].question_id,
            score=4,
        )
        assert not result.score_changed

    @pytest.mark.asyncio
    async def test_invalid_question_raises(self):
        service = ReviewService(org_id="org-001")
        draft = await service.create_review("case-001", "user-001")

        with pytest.raises(ValueError):
            service.apply_manager_score(draft, "nonexistent-q", score=3)


class TestFinalisation:
    @pytest.mark.asyncio
    async def test_finalise_locks_review(self):
        service = ReviewService(org_id="org-001")
        draft = await service.create_review("case-001", "user-001")

        result = service.finalise(draft, manager_comment="Good overall performance")
        assert result.status == "finalized"
        assert result.coaching_summary == "Good overall performance"


class TestCoachingSummary:
    @pytest.mark.asyncio
    async def test_identifies_strengths_and_gaps(self):
        service = ReviewService(org_id="org-001")
        draft = await service.create_review("case-001", "user-001")

        # High scores for first 2, low for last 2
        for i, s in enumerate(draft.scores):
            s.ai_score = 5 if i < 4 else 1

        summary = service._generate_coaching_summary(draft)
        assert "Strengths" in summary or "improvement" in summary
