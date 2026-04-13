"""
Token Replacement Engine
Consistent pseudonymisation and de-anonymisation.
Type-preserving tokens: PERSON_001, ORG_003, EMAIL_007, etc.
Bidirectional mapping enables reliable round-trip.
"""
import logging
from dataclasses import dataclass, field

from app.modules.anonymisation.detectors import DetectedEntity

logger = logging.getLogger("clarion.anon.tokens")


@dataclass
class TokenMapping:
    """Single mapping between original value and pseudonym."""
    original_value: str
    pseudonym: str
    entity_type: str
    detection_stage: str
    confidence: float
    is_false_positive: bool = False


class TokenEngine:
    """
    Manages pseudonymisation and de-anonymisation.
    Maintains consistent mappings: same input → same token within scope.
    """

    def __init__(self, scope: str = "session", existing_mappings: list[TokenMapping] | None = None):
        self.scope = scope
        self._forward: dict[str, str] = {}   # original → pseudonym
        self._reverse: dict[str, str] = {}   # pseudonym → original
        self._counters: dict[str, int] = {}  # entity_type → next counter
        self._mappings: list[TokenMapping] = []

        # Load existing mappings (for org-scoped persistence)
        if existing_mappings:
            for m in existing_mappings:
                self._forward[m.original_value] = m.pseudonym
                self._reverse[m.pseudonym] = m.original_value
                self._mappings.append(m)
                # Update counter
                prefix = m.entity_type.upper() + "_"
                if m.pseudonym.startswith(prefix):
                    try:
                        num = int(m.pseudonym[len(prefix):])
                        self._counters[m.entity_type] = max(
                            self._counters.get(m.entity_type, 0), num + 1
                        )
                    except ValueError:
                        pass

    def _next_token(self, entity_type: str) -> str:
        """Generate the next sequential pseudonym for an entity type."""
        counter = self._counters.get(entity_type, 1)
        self._counters[entity_type] = counter + 1
        return f"{entity_type.upper()}_{counter:03d}"

    def get_or_create_token(self, entity: DetectedEntity) -> str:
        """Get existing token or create a new one for an entity."""
        # Consistent mapping: same value always gets same token
        existing = self._forward.get(entity.value)
        if existing:
            return existing

        pseudonym = self._next_token(entity.entity_type)
        self._forward[entity.value] = pseudonym
        self._reverse[pseudonym] = entity.value
        self._mappings.append(TokenMapping(
            original_value=entity.value,
            pseudonym=pseudonym,
            entity_type=entity.entity_type,
            detection_stage=entity.detection_stage,
            confidence=entity.confidence,
        ))
        return pseudonym

    def anonymise(self, text: str, entities: list[DetectedEntity]) -> str:
        """
        Replace all detected entities in text with pseudonyms.
        Processes entities in reverse order (by position) to preserve offsets.
        """
        # Sort by start position descending so replacements don't shift offsets
        sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)
        result = text

        for entity in sorted_entities:
            pseudonym = self.get_or_create_token(entity)
            result = result[:entity.start] + pseudonym + result[entity.end:]

        return result

    def deanonymise(self, text: str) -> tuple[str, list[str]]:
        """
        Replace all pseudonym tokens in text with original values.
        Returns (restored_text, orphaned_tokens).
        """
        result = text
        orphaned = []

        # Find all tokens in text matching our pattern
        import re
        token_pattern = re.compile(r"\b[A-Z]+_\d{3}\b")

        for match in token_pattern.finditer(text):
            token = match.group()
            original = self._reverse.get(token)
            if original:
                result = result.replace(token, original)
            else:
                orphaned.append(token)

        if orphaned:
            logger.warning(f"Orphaned tokens in de-anonymisation: {orphaned}")

        return result, orphaned

    @property
    def mappings(self) -> list[TokenMapping]:
        return self._mappings

    @property
    def entity_count(self) -> int:
        return len(self._mappings)

    def mark_false_positive(self, pseudonym: str) -> bool:
        """Mark a mapping as false positive (user says it's not PII)."""
        for m in self._mappings:
            if m.pseudonym == pseudonym:
                m.is_false_positive = True
                return True
        return False
