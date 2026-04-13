"""
Case Review Service
Orchestrates the AI-first review workflow:
1. Create review → 2. Load rubric → 3. AI generates draft → 4. Manager refines
→ 5. Override handling (re-evaluate) → 6. Finalise → 7. Distribute
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

logger = logging.getLogger("clarion.reviews")


@dataclass
class RubricQuestion:
    id: str
    category_id: str
    category_name: str
    category_weight: float
    question_text: str
    score_1_definition: str
    score_3_definition: str
    score_5_definition: str
    allows_na: bool = False
    coaching_guidance: str | None = None
    sort_order: int = 0


@dataclass
class ReviewScore:
    question_id: str
    question_text_snapshot: str
    category_name_snapshot: str
    weight_snapshot: float
    ai_score: int | None = None
    ai_comment: str | None = None
    ai_evidence_event_ids: list[str] = field(default_factory=list)
    ai_coaching_suggestion: str | None = None
    manager_score: int | None = None
    manager_comment: str | None = None
    is_na: bool = False
    score_changed: bool = False
    change_justification: str | None = None
    ai_re_evaluated: bool = False


@dataclass
class ReviewDraft:
    review_id: str
    case_id: str
    reviewer_id: str
    ai_engine: str
    status: str = "draft"
    scores: list[ReviewScore] = field(default_factory=list)
    coaching_summary: str | None = None
    overall_score: float | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class ReviewService:
    """Orchestrates the complete AI-first review lifecycle."""

    def __init__(self, org_id: str, ai_router=None):
        self.org_id = org_id
        self.ai_router = ai_router

    async def create_review(
        self,
        case_id: str,
        reviewer_id: str,
        ai_engine: str = "ollama",
        selection_source: str = "manual",
        trigger_reason: dict | None = None,
    ) -> ReviewDraft:
        """
        Step 1-2: Create review record and load active rubric.
        Phase 6: In-memory. Phase 7+: PostgreSQL.
        """
        review_id = f"rev-{case_id[:8]}"

        # Load rubric (Phase 6: defaults, Phase 7+: from database)
        rubric = self._load_default_rubric()

        draft = ReviewDraft(
            review_id=review_id,
            case_id=case_id,
            reviewer_id=reviewer_id,
            ai_engine=ai_engine,
        )

        # Create score slots from rubric with snapshots
        for q in rubric:
            draft.scores.append(
                ReviewScore(
                    question_id=q.id,
                    question_text_snapshot=q.question_text,
                    category_name_snapshot=q.category_name,
                    weight_snapshot=q.category_weight,
                )
            )

        logger.info(f"Review {review_id} created for case {case_id}: {len(rubric)} questions")
        return draft

    async def generate_ai_draft(
        self,
        draft: ReviewDraft,
        case_data: dict,
        events: list[dict],
    ) -> ReviewDraft:
        """
        Steps 3-6: Generate AI draft scores, comments, and coaching.
        Routes through AI Router (anonymises for external engines).
        """
        if not self.ai_router:
            logger.warning("No AI router available — returning empty draft")
            return draft

        rubric_for_prompt = [
            {
                "id": s.question_id,
                "text": s.question_text_snapshot,
                "weight": float(s.weight_snapshot),
            }
            for s in draft.scores
        ]

        from app.intelligence.prompts.templates import review_draft_prompt

        system_prompt, user_prompt = review_draft_prompt(case_data, events, rubric_for_prompt)

        try:
            response = await self.ai_router.generate(
                task="review_draft",
                prompt=user_prompt,
                system_prompt=system_prompt,
                user_preference=draft.ai_engine,
            )

            # Parse AI response into scores
            import json

            try:
                ai_scores = json.loads(response.text)
                if isinstance(ai_scores, list):
                    self._apply_ai_scores(draft, ai_scores)
            except json.JSONDecodeError:
                logger.warning(f"AI returned non-JSON response for review {draft.review_id}")

            # Calculate overall score
            draft.overall_score = self._calculate_overall_score(draft)
            draft.coaching_summary = self._generate_coaching_summary(draft)

        except Exception as e:
            logger.error(f"AI draft generation failed for {draft.review_id}: {e}")

        return draft

    def apply_manager_score(
        self,
        draft: ReviewDraft,
        question_id: str,
        score: int | None,
        comment: str | None = None,
        is_na: bool = False,
        justification: str | None = None,
    ) -> ReviewScore:
        """
        Step 7-8: Manager overrides an AI score.
        Captures justification and flags for re-evaluation.
        """
        for s in draft.scores:
            if s.question_id == question_id:
                s.manager_score = score
                s.manager_comment = comment
                s.is_na = is_na

                if s.ai_score is not None and score is not None and score != s.ai_score:
                    s.score_changed = True
                    s.change_justification = justification or "Manager disagreed with AI assessment"
                    # Flag for AI re-evaluation
                    s.ai_re_evaluated = False  # Will be set True after re-eval

                # Recalculate overall
                draft.overall_score = self._calculate_overall_score(draft)
                return s

        raise ValueError(f"Question {question_id} not found in review")

    async def re_evaluate_overrides(self, draft: ReviewDraft, case_data: dict) -> ReviewDraft:
        """
        Step 8 continued: AI re-evaluates comments for questions where manager changed the score.
        """
        if not self.ai_router:
            return draft

        changed = [s for s in draft.scores if s.score_changed and not s.ai_re_evaluated]
        if not changed:
            return draft

        for score in changed:
            try:
                prompt = (
                    f"The manager reviewed your assessment of '{score.question_text_snapshot}' "
                    f"and changed the score from {score.ai_score} to {score.manager_score}. "
                    f"Justification: {score.change_justification}\n\n"
                    f"Update your comment and coaching suggestion to align with the manager's assessment."
                )
                response = await self.ai_router.generate(
                    task="review_reevaluation",
                    prompt=prompt,
                    user_preference=draft.ai_engine,
                    max_tokens=500,
                )
                score.ai_comment = response.text
                score.ai_re_evaluated = True
            except Exception as e:
                logger.warning(f"Re-evaluation failed for question {score.question_id}: {e}")

        return draft

    def finalise(self, draft: ReviewDraft, manager_comment: str | None = None) -> ReviewDraft:
        """Step 9: Finalise and lock the review."""
        draft.status = "finalized"
        if manager_comment:
            draft.coaching_summary = manager_comment
        logger.info(f"Review {draft.review_id} finalised. Score: {draft.overall_score}")
        return draft

    def _apply_ai_scores(self, draft: ReviewDraft, ai_scores: list[dict]):
        """Map AI response to draft score slots."""
        score_map = {s.get("question_id"): s for s in ai_scores}
        for slot in draft.scores:
            ai = score_map.get(slot.question_id)
            if ai:
                slot.ai_score = ai.get("score")
                slot.ai_comment = ai.get("comment", "")
                slot.ai_coaching_suggestion = ai.get("coaching", "")
                slot.ai_evidence_event_ids = ai.get("evidence_ids", [])

    def _calculate_overall_score(self, draft: ReviewDraft) -> float:
        """Calculate weighted overall score. Uses manager score if available, else AI score."""
        total_weight = 0.0
        weighted_sum = 0.0

        for s in draft.scores:
            if s.is_na:
                continue
            score = s.manager_score if s.manager_score is not None else s.ai_score
            if score is None:
                continue
            weighted_sum += score * float(s.weight_snapshot)
            total_weight += float(s.weight_snapshot)

        if total_weight == 0:
            return 0.0
        return round(weighted_sum / total_weight, 1)

    def _generate_coaching_summary(self, draft: ReviewDraft) -> str:
        """Generate coaching narrative from scores."""
        strengths = []
        gaps = []
        for s in draft.scores:
            score = s.manager_score or s.ai_score
            if score is None or s.is_na:
                continue
            if score >= 4:
                strengths.append(s.category_name_snapshot)
            elif score <= 2:
                gaps.append(s.category_name_snapshot)

        parts = []
        if strengths:
            parts.append(f"Strengths: {', '.join(set(strengths))}")
        if gaps:
            parts.append(f"Areas for improvement: {', '.join(set(gaps))}")
        return ". ".join(parts) if parts else "Review complete."

    def _load_default_rubric(self) -> list[RubricQuestion]:
        """Load default rubric questions. Phase 7+: from database."""
        return DEFAULT_RUBRIC


# ─── Default Rubric (ships with V1) ───
DEFAULT_RUBRIC = [
    RubricQuestion(
        id="q-01",
        category_id="cat-01",
        category_name="Process Adherence",
        category_weight=0.25,
        sort_order=1,
        question_text="Case categorised and prioritised correctly per SLA definitions",
        score_1_definition="Priority or category completely wrong with no correction",
        score_3_definition="Minor categorisation issues, corrected within 24h",
        score_5_definition="Perfect categorisation from initial triage",
        coaching_guidance="Review SLA matrix with engineer. Provide examples of correct categorisation.",
    ),
    RubricQuestion(
        id="q-02",
        category_id="cat-01",
        category_name="Process Adherence",
        category_weight=0.25,
        sort_order=2,
        question_text="Initial response sent within SLA target",
        score_1_definition="First response significantly beyond SLA",
        score_3_definition="First response within SLA but close to limit",
        score_5_definition="First response well within SLA with quality content",
        coaching_guidance="Review time management and triage workflow.",
    ),
    RubricQuestion(
        id="q-03",
        category_id="cat-02",
        category_name="Technical Quality",
        category_weight=0.30,
        sort_order=3,
        question_text="Troubleshooting approach was systematic and logical",
        score_1_definition="No clear troubleshooting methodology, random attempts",
        score_3_definition="Basic troubleshooting with some gaps in methodology",
        score_5_definition="Excellent systematic approach with clear diagnostic steps",
        coaching_guidance="Walk through ideal troubleshooting flow for this product area.",
    ),
    RubricQuestion(
        id="q-04",
        category_id="cat-02",
        category_name="Technical Quality",
        category_weight=0.30,
        sort_order=4,
        question_text="Root cause identified or appropriate escalation made",
        score_1_definition="No root cause found, no escalation despite complexity",
        score_3_definition="Partial root cause, or timely escalation with context",
        score_5_definition="Clear root cause identified with prevention recommendation",
        allows_na=True,
        coaching_guidance="Discuss escalation criteria and when to seek help.",
    ),
    RubricQuestion(
        id="q-05",
        category_id="cat-03",
        category_name="Customer Communication",
        category_weight=0.25,
        sort_order=5,
        question_text="Updates provided at appropriate frequency",
        score_1_definition="Customer left without updates for extended periods",
        score_3_definition="Regular updates but gaps during complex phases",
        score_5_definition="Proactive, timely updates throughout the case lifecycle",
        coaching_guidance="Review communication cadence expectations per priority.",
    ),
    RubricQuestion(
        id="q-06",
        category_id="cat-03",
        category_name="Customer Communication",
        category_weight=0.25,
        sort_order=6,
        question_text="Communication was clear, professional, and empathetic",
        score_1_definition="Unclear, overly technical, or dismissive communication",
        score_3_definition="Professional but could improve clarity or empathy",
        score_5_definition="Excellent clarity, tone, and customer-centric language",
        coaching_guidance="Share examples of good customer communication.",
    ),
    RubricQuestion(
        id="q-07",
        category_id="cat-04",
        category_name="Documentation & Knowledge",
        category_weight=0.20,
        sort_order=7,
        question_text="Case notes are comprehensive and useful for future reference",
        score_1_definition="Minimal or no internal documentation",
        score_3_definition="Basic notes present but missing key details",
        score_5_definition="Thorough documentation that would help any engineer pick up the case",
        coaching_guidance="Show what good case documentation looks like.",
    ),
    RubricQuestion(
        id="q-08",
        category_id="cat-04",
        category_name="Documentation & Knowledge",
        category_weight=0.20,
        sort_order=8,
        question_text="Knowledge article linked or created where applicable",
        score_1_definition="Relevant knowledge exists but not linked; no new article for novel issue",
        score_3_definition="Existing article linked; novel issue acknowledged but no article created",
        score_5_definition="Relevant article linked and updated, or new article created for novel solution",
        allows_na=True,
        coaching_guidance="Review KCS methodology and article contribution expectations.",
    ),
]
