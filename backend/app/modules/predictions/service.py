"""
Predictions Service
Escalation risk prediction via LLM reasoning (Phase 1) and ML model (Phase 2).
Phase 7: LLM reasoning via AI Router. Phase 8+: XGBoost trained model.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

logger = logging.getLogger("clarion.predictions")


@dataclass
class Prediction:
    case_id: str
    case_number: str
    prediction_type: str  # escalation_risk | sla_breach
    risk_score: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    risk_level: str  # high | medium | low
    contributing_factors: list[dict] = field(default_factory=list)
    reasoning: str | None = None
    source: str = "llm_reasoning"
    valid_until: datetime | None = None


class PredictionService:
    """Generates escalation risk predictions for cases."""

    def __init__(self, org_id: str, ai_router=None):
        self.org_id = org_id
        self.ai_router = ai_router

    async def predict_escalation(
        self,
        case_data: dict,
        events: list[dict],
    ) -> Prediction:
        """
        Generate escalation risk prediction for a case.
        Phase 7: LLM reasoning via Gemma4.
        Phase 8+: Combined LLM + XGBoost.
        """
        case_number = case_data.get("sf_case_number", "unknown")

        if self.ai_router:
            try:
                from app.intelligence.prompts.templates import escalation_prediction_prompt

                system_prompt, user_prompt = escalation_prediction_prompt(case_data, events)

                response = await self.ai_router.generate(
                    task="escalation_prediction",
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    max_tokens=500,
                )

                # Parse structured response
                try:
                    result = json.loads(response.text)
                    risk = result.get("risk", "low")
                    confidence = result.get("confidence", 0.5)
                    factors = result.get("factors", [])
                    recommendation = result.get("recommendation", "")

                    return Prediction(
                        case_id=case_data.get("id", ""),
                        case_number=case_number,
                        prediction_type="escalation_risk",
                        risk_score={"high": 0.85, "medium": 0.55, "low": 0.20}.get(risk, 0.5),
                        confidence=confidence,
                        risk_level=risk,
                        contributing_factors=[{"factor": f, "impact": "medium"} for f in factors],
                        reasoning=recommendation,
                        source="llm_reasoning",
                        valid_until=datetime.now(UTC) + timedelta(hours=24),
                    )
                except json.JSONDecodeError:
                    logger.warning(f"Non-JSON prediction response for {case_number}")

            except Exception as e:
                logger.error(f"Prediction failed for {case_number}: {e}")

        # Fallback: heuristic-based prediction
        return self._heuristic_prediction(case_data)

    def _heuristic_prediction(self, case_data: dict) -> Prediction:
        """Simple rule-based fallback when AI is unavailable."""
        score = 0.0
        factors = []

        priority = case_data.get("priority", "P4")
        if priority == "P1":
            score += 0.3
            factors.append({"factor": "P1 priority", "impact": "high"})
        elif priority == "P2":
            score += 0.15
            factors.append({"factor": "P2 priority", "impact": "medium"})

        age = case_data.get("case_age_days", 0)
        if age > 14:
            score += 0.2
            factors.append({"factor": f"Case age {age} days", "impact": "high"})
        elif age > 7:
            score += 0.1
            factors.append({"factor": f"Case age {age} days", "impact": "medium"})

        if case_data.get("sla_status") == "Breached":
            score += 0.25
            factors.append({"factor": "SLA breached", "impact": "high"})

        if case_data.get("is_escalated"):
            score += 0.2
            factors.append({"factor": "Already escalated", "impact": "high"})

        score = min(score, 1.0)
        risk_level = "high" if score > 0.6 else "medium" if score > 0.3 else "low"

        return Prediction(
            case_id=case_data.get("id", ""),
            case_number=case_data.get("sf_case_number", ""),
            prediction_type="escalation_risk",
            risk_score=round(score, 2),
            confidence=0.60,
            risk_level=risk_level,
            contributing_factors=factors,
            reasoning=f"Heuristic assessment based on {len(factors)} factors",
            source="heuristic",
            valid_until=datetime.now(UTC) + timedelta(hours=12),
        )

    def get_at_risk_cases(self) -> list[Prediction]:
        """Get all cases with high escalation risk. Phase 8+: from predictions table."""
        # Phase 7: mock data matching the dashboard
        return [
            Prediction(
                "c-001",
                "00798234",
                "escalation_risk",
                0.92,
                0.88,
                "high",
                [
                    {"factor": "P1 priority", "impact": "high"},
                    {"factor": "SLA breached", "impact": "high"},
                    {"factor": "Negative sentiment", "impact": "medium"},
                ],
                "P1 case with breached SLA and frustrated customer",
                "llm_reasoning",
            ),
            Prediction(
                "c-002",
                "00803992",
                "escalation_risk",
                0.78,
                0.82,
                "high",
                [
                    {"factor": "12-day age", "impact": "medium"},
                    {"factor": "Customer escalation request", "impact": "high"},
                ],
                "Long-running P2 with customer requesting escalation",
                "llm_reasoning",
            ),
            Prediction(
                "c-003",
                "00689632",
                "escalation_risk",
                0.55,
                0.71,
                "medium",
                [
                    {"factor": "45-day age", "impact": "high"},
                    {"factor": "Neutral sentiment", "impact": "low"},
                ],
                "Very old P2 case but stable sentiment",
                "llm_reasoning",
            ),
        ]
