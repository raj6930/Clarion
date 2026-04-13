"""Unit tests for anonymisation pipeline."""
import pytest
from app.modules.anonymisation.detectors import detect_regex, detect_dictionary, DetectedEntity
from app.modules.anonymisation.tokens import TokenEngine, TokenMapping
from app.modules.anonymisation.service import AnonymisationService


class TestRegexDetection:
    def test_detects_email(self):
        entities = detect_regex("Contact john.smith@acme.com for help")
        assert any(e.entity_type == "email" and "john.smith@acme.com" in e.value for e in entities)

    def test_detects_multiple_emails(self):
        text = "CC: alice@test.com and bob@example.org"
        entities = detect_regex(text)
        emails = [e for e in entities if e.entity_type == "email"]
        assert len(emails) == 2

    def test_detects_phone(self):
        entities = detect_regex("Call +61 2 9876 5432 for support")
        assert any(e.entity_type == "phone" for e in entities)

    def test_detects_ip(self):
        entities = detect_regex("Server at 192.168.1.100 is down")
        ips = [e for e in entities if e.entity_type == "ip"]
        assert len(ips) == 1
        assert ips[0].value == "192.168.1.100"

    def test_detects_us_ssn(self):
        entities = detect_regex("SSN: 123-45-6789")
        assert any(e.entity_type == "tax_id" for e in entities)

    def test_detects_credit_card(self):
        entities = detect_regex("Card: 4111-1111-1111-1111")
        assert any(e.entity_type == "financial" for e in entities)

    def test_no_false_positives_on_plain_text(self):
        entities = detect_regex("The system is running normally with no issues")
        # Should not detect emails, phones, IPs, etc.
        high_confidence = [e for e in entities if e.confidence > 0.8]
        assert len(high_confidence) == 0


class TestDictionaryDetection:
    def test_exact_match(self):
        dictionary = [{"term": "Transgrid", "entity_type": "org", "match_mode": "exact"}]
        entities = detect_dictionary("Case raised by Transgrid Ltd about EcoSys", dictionary)
        assert len(entities) == 1
        assert entities[0].value == "Transgrid"

    def test_case_insensitive(self):
        dictionary = [{"term": "John Smith", "entity_type": "person", "match_mode": "exact"}]
        entities = detect_dictionary("Spoke with john smith today", dictionary)
        assert len(entities) == 1

    def test_multiple_matches(self):
        dictionary = [
            {"term": "Transgrid", "entity_type": "org", "match_mode": "exact"},
            {"term": "Tim Trulis", "entity_type": "person", "match_mode": "exact"},
        ]
        text = "Tim Trulis from Transgrid reported a bug"
        entities = detect_dictionary(text, dictionary)
        assert len(entities) == 2

    def test_regex_mode(self):
        dictionary = [{"term": r"TRG-\d+", "entity_type": "custom", "match_mode": "regex"}]
        entities = detect_dictionary("Ticket TRG-4567 is open", dictionary)
        assert len(entities) == 1

    def test_empty_dictionary(self):
        entities = detect_dictionary("Some text", [])
        assert len(entities) == 0


class TestTokenEngine:
    def test_consistent_mapping(self):
        engine = TokenEngine()
        e1 = DetectedEntity("person", "John Smith", 0, 10, "regex", 0.9)
        t1 = engine.get_or_create_token(e1)
        t2 = engine.get_or_create_token(e1)
        assert t1 == t2  # Same input → same token

    def test_type_preserving(self):
        engine = TokenEngine()
        person = DetectedEntity("person", "Jane Doe", 0, 8, "regex", 0.9)
        org = DetectedEntity("org", "Acme Corp", 10, 19, "regex", 0.9)
        t_person = engine.get_or_create_token(person)
        t_org = engine.get_or_create_token(org)
        assert t_person.startswith("PERSON_")
        assert t_org.startswith("ORG_")

    def test_sequential_numbering(self):
        engine = TokenEngine()
        e1 = DetectedEntity("person", "Alice", 0, 5, "regex", 0.9)
        e2 = DetectedEntity("person", "Bob", 6, 9, "regex", 0.9)
        t1 = engine.get_or_create_token(e1)
        t2 = engine.get_or_create_token(e2)
        assert t1 == "PERSON_001"
        assert t2 == "PERSON_002"

    def test_anonymise_text(self):
        engine = TokenEngine()
        text = "John Smith sent an email to jane@test.com"
        entities = [
            DetectedEntity("person", "John Smith", 0, 10, "ner", 0.8),
            DetectedEntity("email", "jane@test.com", 28, 41, "regex", 0.99),
        ]
        result = engine.anonymise(text, entities)
        assert "John Smith" not in result
        assert "jane@test.com" not in result
        assert "PERSON_001" in result
        assert "EMAIL_001" in result

    def test_deanonymise_round_trip(self):
        engine = TokenEngine()
        text = "Contact John Smith at john@acme.com"
        entities = [
            DetectedEntity("person", "John Smith", 8, 18, "ner", 0.8),
            DetectedEntity("email", "john@acme.com", 22, 35, "regex", 0.99),
        ]
        anonymised = engine.anonymise(text, entities)
        restored, orphaned = engine.deanonymise(anonymised)
        assert "John Smith" in restored
        assert "john@acme.com" in restored
        assert len(orphaned) == 0

    def test_mark_false_positive(self):
        engine = TokenEngine()
        entity = DetectedEntity("person", "Product Name", 0, 12, "ner", 0.6)
        token = engine.get_or_create_token(entity)
        assert engine.mark_false_positive(token)
        assert engine.mappings[0].is_false_positive

    def test_existing_mappings_loaded(self):
        existing = [TokenMapping("Alice", "PERSON_001", "person", "ner", 0.8)]
        engine = TokenEngine(existing_mappings=existing)
        entity = DetectedEntity("person", "Alice", 0, 5, "ner", 0.8)
        token = engine.get_or_create_token(entity)
        assert token == "PERSON_001"  # Reuses existing


class TestAnonymisationService:
    def test_full_pipeline(self):
        service = AnonymisationService(org_id="org-001")
        text = "Email john.doe@acme.com or call +1-555-123-4567 about server 10.0.0.1"
        result = service.anonymise(text)
        assert "john.doe@acme.com" not in result.anonymised_text
        assert result.entity_count > 0
        assert len(result.mappings) > 0

    def test_empty_text(self):
        service = AnonymisationService(org_id="org-001")
        result = service.anonymise("")
        assert result.anonymised_text == ""
        assert result.entity_count == 0

    def test_no_pii_text(self):
        service = AnonymisationService(org_id="org-001")
        text = "The system is running normally"
        result = service.anonymise(text)
        # May detect some false positives with low confidence, but high-confidence entities should be 0
        high_conf = [e for e in result.entities if e.confidence > 0.8]
        assert len(high_conf) == 0

    def test_with_dictionary(self):
        dictionary = [{"term": "Transgrid", "entity_type": "org", "match_mode": "exact"}]
        service = AnonymisationService(org_id="org-001", dictionary=dictionary)
        text = "Transgrid reported a performance issue"
        result = service.anonymise(text)
        assert "Transgrid" not in result.anonymised_text
        assert any(m.entity_type == "org" for m in result.mappings)

    def test_round_trip(self):
        service = AnonymisationService(org_id="org-001")
        text = "Contact support@acme.com for help"
        anon_result = service.anonymise(text)
        restored, orphaned = service.deanonymise(anon_result.anonymised_text)
        assert "support@acme.com" in restored
        assert len(orphaned) == 0
