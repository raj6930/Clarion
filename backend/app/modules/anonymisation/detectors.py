"""
PII Detection Pipeline — 4 stages
Stage 1: Regex patterns (structured PII)
Stage 2: Dictionary lookup (known entities)
Stage 3: NER via spaCy (named entities)
Stage 4: LLM context review via Gemma4 (stub — Phase 5)
"""
import re
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("clarion.anon.detect")


@dataclass
class DetectedEntity:
    """A single PII entity detected in text."""
    entity_type: str          # person | org | email | phone | ip | location | tax_id | custom
    value: str                # The original text
    start: int                # Character offset start
    end: int                  # Character offset end
    detection_stage: str      # regex | dictionary | ner | llm | manual
    confidence: float         # 0.0 - 1.0


@dataclass
class DetectionResult:
    """Result of running all detection stages on a text."""
    entities: list[DetectedEntity] = field(default_factory=list)
    text: str = ""

    def add(self, entity: DetectedEntity):
        # Deduplicate: skip if same span already detected
        for existing in self.entities:
            if existing.start == entity.start and existing.end == entity.end:
                # Keep higher confidence
                if entity.confidence > existing.confidence:
                    existing.confidence = entity.confidence
                    existing.detection_stage = entity.detection_stage
                return
        self.entities.append(entity)

    @property
    def count(self) -> int:
        return len(self.entities)


# ═══════════════════════════════════════════════════════
# STAGE 1: Regex Patterns
# ═══════════════════════════════════════════════════════

REGEX_PATTERNS: list[tuple[str, str, float]] = [
    # (pattern, entity_type, confidence)
    # Email addresses
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email", 0.99),

    # Phone numbers (international formats)
    (r"\b\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b", "phone", 0.85),

    # IP addresses (IPv4)
    (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "ip", 0.95),

    # Credit card numbers (basic)
    (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", "financial", 0.90),

    # Australian TFN (9 digits with optional spaces)
    (r"\b\d{3}\s?\d{3}\s?\d{3}\b", "tax_id", 0.60),

    # US SSN
    (r"\b\d{3}-\d{2}-\d{4}\b", "tax_id", 0.95),

    # UK National Insurance
    (r"\b[A-Z]{2}\d{6}[A-Z]\b", "tax_id", 0.90),

    # URLs with paths (may contain identifiable info)
    (r"https?://[^\s]+/(?:user|profile|account|customer)/[^\s]+", "url", 0.80),

    # Australian postcodes (4 digits, common ranges)
    (r"\b(?:2\d{3}|3\d{3}|4\d{3}|5\d{3}|6\d{3}|7\d{3}|0[89]\d{2})\b", "location", 0.40),
]

_compiled_patterns = [(re.compile(p, re.IGNORECASE), t, c) for p, t, c in REGEX_PATTERNS]


def detect_regex(text: str) -> list[DetectedEntity]:
    """Stage 1: Fast regex-based detection for structured PII."""
    entities = []
    for pattern, entity_type, confidence in _compiled_patterns:
        for match in pattern.finditer(text):
            entities.append(DetectedEntity(
                entity_type=entity_type,
                value=match.group(),
                start=match.start(),
                end=match.end(),
                detection_stage="regex",
                confidence=confidence,
            ))
    return entities


# ═══════════════════════════════════════════════════════
# STAGE 2: Dictionary Lookup
# ═══════════════════════════════════════════════════════

def detect_dictionary(text: str, dictionary: list[dict]) -> list[DetectedEntity]:
    """
    Stage 2: Match against known entity dictionary.
    dictionary: list of {term, entity_type, match_mode}
    """
    entities = []
    text_lower = text.lower()

    for entry in dictionary:
        term = entry["term"]
        entity_type = entry.get("entity_type", "custom")
        match_mode = entry.get("match_mode", "exact")

        if match_mode == "exact":
            idx = text_lower.find(term.lower())
            while idx != -1:
                entities.append(DetectedEntity(
                    entity_type=entity_type,
                    value=text[idx:idx + len(term)],
                    start=idx,
                    end=idx + len(term),
                    detection_stage="dictionary",
                    confidence=0.95,
                ))
                idx = text_lower.find(term.lower(), idx + 1)

        elif match_mode == "regex":
            try:
                for match in re.finditer(term, text, re.IGNORECASE):
                    entities.append(DetectedEntity(
                        entity_type=entity_type,
                        value=match.group(),
                        start=match.start(),
                        end=match.end(),
                        detection_stage="dictionary",
                        confidence=0.90,
                    ))
            except re.error:
                logger.warning(f"Invalid regex in dictionary: {term}")

    return entities


# ═══════════════════════════════════════════════════════
# STAGE 3: NER (spaCy)
# ═══════════════════════════════════════════════════════

_nlp = None

SPACY_ENTITY_MAP = {
    "PERSON": "person",
    "ORG": "org",
    "GPE": "location",
    "LOC": "location",
    "FAC": "location",
}


def _get_nlp():
    """Lazy-load spaCy model."""
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded: en_core_web_sm")
        except (ImportError, OSError) as e:
            logger.warning(f"spaCy not available: {e}. NER stage will be skipped.")
            _nlp = False  # Sentinel: tried and failed
    return _nlp if _nlp is not False else None


def detect_ner(text: str) -> list[DetectedEntity]:
    """Stage 3: Named Entity Recognition via spaCy."""
    nlp = _get_nlp()
    if nlp is None:
        return []

    doc = nlp(text)
    entities = []

    for ent in doc.ents:
        entity_type = SPACY_ENTITY_MAP.get(ent.label_)
        if entity_type:
            entities.append(DetectedEntity(
                entity_type=entity_type,
                value=ent.text,
                start=ent.start_char,
                end=ent.end_char,
                detection_stage="ner",
                confidence=0.75,
            ))

    return entities


# ═══════════════════════════════════════════════════════
# STAGE 4: LLM Context Review (Gemma4 — stub for Phase 5)
# ═══════════════════════════════════════════════════════

def detect_llm(text: str, existing_entities: list[DetectedEntity]) -> list[DetectedEntity]:
    """
    Stage 4: Local LLM context-aware sweep.
    Phase 5: Sends text + existing detections to Gemma4 for final review.
    Phase 4: Returns empty (stub).
    """
    # Phase 5 implementation will:
    # 1. Send text to local Ollama/Gemma4
    # 2. Prompt: "Given these already-detected entities, identify any additional PII..."
    # 3. Parse response for additional entities
    # 4. No data leaves the system — Gemma4 runs locally
    return []
