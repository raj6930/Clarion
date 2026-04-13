"""
Contract tests for the Cases module.
Validates SF-validated schemas and inter-module consumption.
"""

from datetime import UTC, datetime

import pytest
from app.modules.cases.schemas import (
    AccountSearchResult,
    CaseEventResponse,
    CaseSummaryResponse,
    CaseSyncedEvent,
)
from pydantic import ValidationError


class TestCaseSummaryContract:
    """Producer contract: CaseSummaryResponse with SF-validated fields."""

    def test_valid_case_summary_with_sf_fields(self):
        summary = CaseSummaryResponse(
            case_id="550e8400-e29b-41d4-a716-446655440000",
            sf_case_number="00803992",
            subject="Performance Issues with Application",
            status="Cancelled",
            sub_status="Duplicate",
            priority="P2",  # Mapped from "2 - High"
            case_owner="timothy.trulis@hexagon.com",
            case_owner_name="Tim Trulis",
            product="EcoSys",  # SF: Support_Product_Name__c
            product_family="Enterprise Project Performance",
            support_area="Cloud Performance",  # SF: PPMArea__c
            environment="Production",
            product_version="9.2",  # SF: Reported_Version__c
            opened_date=datetime(2026, 3, 31, 5, 19, 32, tzinfo=UTC),
            resolved_date=datetime(2026, 3, 31, 6, 27, 29, tzinfo=UTC),
            closed_date=datetime(2026, 4, 2, 15, 37, 41, tzinfo=UTC),
            last_activity_at=datetime(2026, 4, 2, 15, 37, 31, tzinfo=UTC),
            case_age_days=2,
            is_escalated=False,
            sla_status="Within SLA",
            total_event_count=97,
            account_name="Transgrid Ltd",
            sf_account_id="0013t00002qwhPMAAY",
            contact_name="Rahul Uriti",
            contact_email="rahul.uriti@hexagon.com",
        )
        assert summary.product == "EcoSys"
        assert summary.priority == "P2"
        assert summary.sub_status == "Duplicate"
        assert summary.support_area == "Cloud Performance"

    def test_missing_required_field_fails(self):
        with pytest.raises(ValidationError):
            CaseSummaryResponse(case_id="test")

    def test_optional_sf_fields_default_none(self):
        summary = CaseSummaryResponse(
            case_id="test",
            sf_case_number="001",
            subject="Test",
            status="Open",
            priority="P3",
            case_owner="eng1",
            case_owner_name="Engineer One",
            opened_date=datetime.now(tz=UTC),
            case_age_days=1,
            is_escalated=False,
            total_event_count=0,
        )
        assert summary.product is None
        assert summary.product_family is None
        assert summary.sub_status is None
        assert summary.sla_status is None


class TestCaseEventContract:
    """Producer contract: CaseEventResponse with feed HTML handling."""

    def test_feed_event_with_html(self):
        event = CaseEventResponse(
            event_id="test-001",
            event_type="feed_text",
            timestamp=datetime.now(tz=UTC),
            actor="Vikram Singh",
            actor_type="engineer",
            body="The customer is experiencing slowness within the application.",
            body_html="<p>The customer is experiencing slowness within the application.</p>",
        )
        assert event.body_html is not None
        assert "<p>" not in event.body

    def test_email_event_with_thread_id(self):
        event = CaseEventResponse(
            event_id="test-002",
            event_type="email",
            timestamp=datetime.now(tz=UTC),
            actor="rahul.uriti@hexagon.com",
            actor_type="customer",
            direction="inbound",
            subject="Re: Case 00803992 - Performance Issues",
            body="Could you please prioritize this?",
            thread_id="JnRKSCtqczqOY_FS4I6tF3Q",
        )
        assert event.thread_id == "JnRKSCtqczqOY_FS4I6tF3Q"
        assert event.direction == "inbound"


class TestCaseSyncedEventContract:
    """Event bus contracts for team sync and account sync."""

    def test_team_sync_event(self):
        event = CaseSyncedEvent(
            event_type="case.synced",
            case_id="test-001",
            team_id="team-001",
            timestamp=datetime.now(tz=UTC),
        )
        assert event.team_id == "team-001"
        assert event.sf_account_id is None

    def test_account_sync_event(self):
        event = CaseSyncedEvent(
            event_type="account_case.synced",
            case_id="test-002",
            sf_account_id="0013t00002qwhPMAAY",
            timestamp=datetime.now(tz=UTC),
        )
        assert event.sf_account_id == "0013t00002qwhPMAAY"
        assert event.team_id is None

    def test_reviews_can_consume_sync_event(self):
        """Consumer: reviews module parses sync events for selection rules."""
        event = CaseSyncedEvent(
            event_type="case.synced",
            case_id="test-001",
            team_id="team-001",
            timestamp=datetime.now(tz=UTC),
        )
        assert hasattr(event, "case_id")
        assert hasattr(event, "team_id")


class TestAccountSearchContract:
    """Producer contract: AccountSearchResult for disambiguation."""

    def test_disambiguated_transgrid_accounts(self):
        """Validated: 8 Transgrid accounts in Octave org."""
        results = [
            AccountSearchResult(
                sf_account_id="0013Z00001bHm19QAC",
                name="Transgrid Ltd",
                account_type="O/O (Owner/Operator)",
                industry="Public Sector/Gov - Admin",
                billing_country="Australia",
                billing_state="New South Wales",
                billing_city="Sydney",
            ),
            AccountSearchResult(
                sf_account_id="0013t00002qwhPMAAY",
                name="Transgrid Ltd",
                account_type="Cloud Estate",
                industry="Other",
                billing_country="United States",
                billing_state="Alabama",
                billing_city="Madison",
            ),
        ]
        assert results[0].sf_account_id != results[1].sf_account_id
        assert results[0].account_type != results[1].account_type
        assert results[0].billing_country != results[1].billing_country
