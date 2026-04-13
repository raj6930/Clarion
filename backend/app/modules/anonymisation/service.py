"""
Anonymisation Service
Orchestrates the 4-stage detection pipeline, token replacement,
and human-in-the-loop review flow.
"""
import logging
from dataclasses import dataclass
from typing import Optional

from app.modules.anonymisation.detectors import (
    DetectedEntity, DetectionResult,
    detect_regex, detect_dictionary, detect_ner, detect_llm,
)
from app.modules.anonymisation.tokens import TokenEngine, TokenMapping

logger = logging.getLogger("clarion.anon")


@dataclass
class AnonymisationResult:
    """Full result of anonymising a text."""
    original_text: str
    anonymised_text: str
    entities: list[DetectedEntity]
    mappings: list[TokenMapping]
    entity_count: int
    session_id: Optional[str] = None


class AnonymisationService:
    """
    Runs the full anonymisation pipeline on text input.
    Designed for defence-in-depth: each stage catches what previous stages missed.
    """

    def __init__(
        self,
        org_id: str,
        dictionary: list[dict] | None = None,
        existing_mappings: list[TokenMapping] | None = None,
        scope: str = "session",
    ):
        self.org_id = org_id
        self.dictionary = dictionary or []
        self.token_engine = TokenEngine(scope=scope, existing_mappings=existing_mappings)

    def anonymise(self, text: str) -> AnonymisationResult:
        """
        Run the full 4-stage pipeline on input text.
        Returns anonymised text with all mappings.
        """
        if not text or not text.strip():
            return AnonymisationResult(
                original_text=text,
                anonymised_text=text,
                entities=[],
                mappings=[],
                entity_count=0,
            )

        result = DetectionResult(text=text)

        # Stage 1: Regex
        for entity in detect_regex(text):
            result.add(entity)
        logger.debug(f"Stage 1 (regex): {result.count} entities")

        # Stage 2: Dictionary
        for entity in detect_dictionary(text, self.dictionary):
            result.add(entity)
        logger.debug(f"Stage 2 (dictionary): {result.count} entities")

        # Stage 3: NER
        for entity in detect_ner(text):
            result.add(entity)
        logger.debug(f"Stage 3 (NER): {result.count} entities")

        # Stage 4: LLM (stub in Phase 4, live in Phase 5)
        for entity in detect_llm(text, result.entities):
            result.add(entity)
        logger.debug(f"Stage 4 (LLM): {result.count} entities")

        # Apply token replacements
        anonymised = self.token_engine.anonymise(text, result.entities)

        logger.info(f"Anonymisation complete: {result.count} entities detected, text length {len(text)} → {len(anonymised)}")

        return AnonymisationResult(
            original_text=text,
            anonymised_text=anonymised,
            entities=result.entities,
            mappings=self.token_engine.mappings,
            entity_count=result.count,
        )

    def deanonymise(self, text: str) -> tuple[str, list[str]]:
        """Reverse anonymisation. Returns (original_text, orphaned_tokens)."""
        return self.token_engine.deanonymise(text)

    def mark_false_positive(self, pseudonym: str) -> bool:
        """Mark an entity as not actually PII."""
        return self.token_engine.mark_false_positive(pseudonym)

    def add_to_dictionary(self, term: str, entity_type: str) -> dict:
        """Add a manually flagged term to the dictionary for future detection."""
        entry = {"term": term, "entity_type": entity_type, "match_mode": "exact"}
        self.dictionary.append(entry)
        return entry
