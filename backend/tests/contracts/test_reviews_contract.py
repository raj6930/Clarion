"""Contract tests for review module schemas."""

from app.modules.reviews.schemas import (
    CreateReviewRequest,
    RecommendationActionRequest,
    UpdateScoreRequest,
)


class TestCreateReviewContract:
    def test_minimal(self):
        req = CreateReviewRequest(case_id="case-001")
        assert req.ai_engine == "ollama"
        assert req.selection_source == "manual"

    def test_with_trigger(self):
        req = CreateReviewRequest(
            case_id="case-001",
            ai_engine="claude",
            selection_source="intelligent",
            trigger_reason={"type": "escalation_risk", "score": 0.85},
        )
        assert req.trigger_reason["score"] == 0.85


class TestUpdateScoreContract:
    def test_valid_score(self):
        req = UpdateScoreRequest(question_id="q-01", score=4)
        assert req.score == 4

    def test_na_toggle(self):
        req = UpdateScoreRequest(question_id="q-01", is_na=True)
        assert req.is_na


class TestRecommendationContract:
    def test_accept(self):
        req = RecommendationActionRequest(action="accept", ai_engine="claude")
        assert req.action == "accept"

    def test_dismiss(self):
        req = RecommendationActionRequest(action="dismiss", dismiss_reason="Already reviewed informally")
        assert req.dismiss_reason is not None
