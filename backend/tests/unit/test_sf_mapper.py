"""Unit tests for Salesforce field mapper."""

from app.integrations.salesforce.mapper import (
    clean_subject,
    extract_thread_id,
    map_case_record,
    map_priority,
    parse_email_addresses,
    resolve_actor_type,
    strip_html,
)


class TestPriorityMapping:
    def test_full_format(self):
        assert map_priority("2 - High") == "P2"
        assert map_priority("1 - Critical") == "P1"
        assert map_priority("3 - Medium") == "P3"
        assert map_priority("4 - Low") == "P4"

    def test_number_only(self):
        assert map_priority("1") == "P1"
        assert map_priority("3") == "P3"

    def test_word_only(self):
        assert map_priority("Critical") == "P1"
        assert map_priority("High") == "P2"

    def test_none_defaults_to_p4(self):
        assert map_priority(None) == "P4"

    def test_unknown_defaults_to_p4(self):
        assert map_priority("Urgent") == "P4"

    def test_strips_whitespace(self):
        assert map_priority("  2 - High  ") == "P2"


class TestEmailParsing:
    def test_single_address(self):
        assert parse_email_addresses("user@example.com") == ["user@example.com"]

    def test_multiple_semicolon_separated(self):
        result = parse_email_addresses("a@b.com; c@d.com; e@f.com")
        assert result == ["a@b.com", "c@d.com", "e@f.com"]

    def test_none_returns_empty(self):
        assert parse_email_addresses(None) == []

    def test_empty_string_returns_empty(self):
        assert parse_email_addresses("") == []

    def test_strips_whitespace(self):
        result = parse_email_addresses("  a@b.com ;  c@d.com  ")
        assert result == ["a@b.com", "c@d.com"]

    def test_filters_empty_entries(self):
        result = parse_email_addresses("a@b.com;;c@d.com;")
        assert result == ["a@b.com", "c@d.com"]


class TestThreadIdExtraction:
    def test_standard_format(self):
        assert extract_thread_id("RE: Case update thread::ABC123::") == "ABC123"

    def test_no_thread_id(self):
        assert extract_thread_id("Regular subject line") is None

    def test_none_subject(self):
        assert extract_thread_id(None) is None

    def test_clean_subject_removes_thread(self):
        result = clean_subject("RE: Case update thread::ABC123::")
        assert "thread::" not in result
        assert "ABC123" not in result

    def test_clean_subject_removes_prefixes(self):
        assert clean_subject("RE: FW: Some subject") == "Some subject"


class TestHtmlStripping:
    def test_basic_tags(self):
        assert strip_html("<p>Hello <b>world</b></p>") == "Hello world"

    def test_br_to_newline(self):
        result = strip_html("Line 1<br>Line 2<br/>Line 3")
        assert "Line 1\nLine 2\nLine 3" == result

    def test_preserves_text(self):
        assert strip_html("No HTML here") == "No HTML here"

    def test_none_returns_none(self):
        assert strip_html(None) is None

    def test_html_entities(self):
        result = strip_html("&amp; &lt; &gt;")
        assert result == "& < >"


class TestActorTypeResolution:
    def test_engineer_match(self):
        assert resolve_actor_type("eng@hex.com", {"eng@hex.com"}, set()) == "engineer"

    def test_customer_match(self):
        assert resolve_actor_type("cust@client.com", set(), {"cust@client.com"}) == "customer"

    def test_system_address(self):
        assert resolve_actor_type("noreply@salesforce.com", set(), set()) == "system"

    def test_no_email_is_system(self):
        assert resolve_actor_type(None, set(), set()) == "system"

    def test_unknown_fallback(self):
        assert resolve_actor_type("random@unknown.com", set(), set()) == "unknown"

    def test_case_insensitive(self):
        assert resolve_actor_type("ENG@hex.com", {"eng@hex.com"}, set()) == "engineer"


class TestCaseRecordMapping:
    def test_maps_basic_fields(self):
        sf_record = {
            "Id": "500xx000001abc",
            "CaseNumber": "00803992",
            "Subject": "Test case",
            "Status": "Working",
            "Priority": "2 - High",
            "Owner": {"Username": "tim@hex.com", "Name": "Tim Trulis"},
            "CreatedDate": "2026-01-15T10:00:00Z",
            "LastModifiedDate": "2026-04-10T14:30:00Z",
        }
        result = map_case_record(sf_record)
        assert result["sf_case_id"] == "500xx000001abc"
        assert result["sf_case_number"] == "00803992"
        assert result["priority"] == "P2"
        assert result["case_owner"] == "tim@hex.com"
        assert result["case_owner_name"] == "Tim Trulis"

    def test_handles_missing_nested_fields(self):
        sf_record = {
            "Id": "500xx000001abc",
            "CaseNumber": "123",
            "Subject": "Test",
            "Status": "New",
            "Priority": None,
            "CreatedDate": "2026-01-01T00:00:00Z",
            "LastModifiedDate": "2026-01-01T00:00:00Z",
        }
        result = map_case_record(sf_record)
        assert result["priority"] == "P4"  # None defaults to P4
