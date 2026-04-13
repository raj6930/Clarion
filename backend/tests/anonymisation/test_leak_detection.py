"""
Anonymisation Leak Detection Tests — ZERO TOLERANCE
These tests assert that known PII never survives the anonymisation pipeline.
Any failure blocks the CI build. Every manually flagged miss gets added here.
"""

import pytest
from app.modules.anonymisation.service import AnonymisationService

# Known PII test dataset — synthetic data only, never real PII
KNOWN_PII = [
    # (text_containing_pii, pii_values_that_must_not_survive)
    (
        "Please contact John Smith at john.smith@transgrid.com.au or +61 2 9876 5432",
        ["john.smith@transgrid.com.au", "+61 2 9876 5432"],
    ),
    (
        "Customer Alice Johnson (alice.j@origin.com.au) reported from IP 203.45.67.89",
        ["alice.j@origin.com.au", "203.45.67.89"],
    ),
    (
        "SSN: 123-45-6789, credit card 4111-1111-1111-1111",
        ["123-45-6789", "4111-1111-1111-1111"],
    ),
    (
        "Server logs show connection from 10.0.0.55 by admin@internal.hexagon.com",
        ["10.0.0.55", "admin@internal.hexagon.com"],
    ),
    (
        "Engineer tim.trulis@hexagon.com escalated case for wolf.gassmann@hexagon.com",
        ["tim.trulis@hexagon.com", "wolf.gassmann@hexagon.com"],
    ),
]


class TestLeakDetection:
    """Zero-tolerance leak detection. Every test MUST pass."""

    @pytest.mark.parametrize("text,pii_values", KNOWN_PII)
    def test_no_pii_survives(self, text: str, pii_values: list[str]):
        """Assert that known PII values are not present in anonymised output."""
        service = AnonymisationService(org_id="org-test")
        result = service.anonymise(text)

        for pii in pii_values:
            assert pii not in result.anonymised_text, (
                f"PII LEAK DETECTED: '{pii}' survived anonymisation!\n"
                f"Original: {text}\n"
                f"Anonymised: {result.anonymised_text}"
            )

    def test_email_never_leaks(self):
        """Emails are the most common PII in support cases."""
        service = AnonymisationService(org_id="org-test")
        emails = [
            "user@example.com",
            "first.last@company.co.uk",
            "name+tag@domain.org",
            "a.b.c@sub.domain.com",
        ]
        for email in emails:
            result = service.anonymise(f"Contact {email} for help")
            assert email not in result.anonymised_text, f"Email leaked: {email}"

    def test_ip_never_leaks(self):
        """IP addresses in server logs must be anonymised."""
        service = AnonymisationService(org_id="org-test")
        ips = ["192.168.1.1", "10.0.0.1", "172.16.0.100", "203.0.113.50"]
        for ip in ips:
            result = service.anonymise(f"Connection from {ip} failed")
            assert ip not in result.anonymised_text, f"IP leaked: {ip}"

    def test_round_trip_preserves_all_data(self):
        """Anonymise → de-anonymise must produce the original text."""
        service = AnonymisationService(org_id="org-test")
        text = "Email support@acme.com from 10.0.0.1 about SSN 123-45-6789"
        anon = service.anonymise(text)
        restored, orphaned = service.deanonymise(anon.anonymised_text)

        # All high-confidence PII should round-trip
        assert "support@acme.com" in restored
        assert "10.0.0.1" in restored
        assert "123-45-6789" in restored
        assert len(orphaned) == 0
