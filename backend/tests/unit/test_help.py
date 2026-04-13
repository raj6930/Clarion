"""Unit tests for help documentation service."""
import pytest
from app.modules.help.service import HelpService


class TestHelpService:
    def test_loads_3_sections(self):
        svc = HelpService()
        assert len(svc.get_all_sections()) == 3

    def test_section_ids(self):
        svc = HelpService()
        ids = [s.id for s in svc.get_all_sections()]
        assert "user-guide" in ids
        assert "technical" in ids
        assert "troubleshooting" in ids

    def test_get_section(self):
        svc = HelpService()
        section = svc.get_section("user-guide")
        assert section is not None
        assert "Dashboard" in section.content

    def test_get_nonexistent_section(self):
        svc = HelpService()
        assert svc.get_section("nonexistent") is None

    def test_search_finds_results(self):
        svc = HelpService()
        results = svc.search("dashboard")
        assert len(results) > 0
        assert any(r.section_id == "user-guide" for r in results)

    def test_search_relevance_ordering(self):
        svc = HelpService()
        results = svc.search("anonymisation pipeline")
        assert len(results) > 0
        assert results[0].relevance >= results[-1].relevance

    def test_search_no_results(self):
        svc = HelpService()
        results = svc.search("xyznonexistent123")
        assert len(results) == 0

    def test_rag_context(self):
        svc = HelpService()
        ctx = svc.get_rag_context("how to create a review")
        assert len(ctx) > 0
        assert len(ctx) <= 2500  # Respects max_chars roughly

    def test_word_counts(self):
        svc = HelpService()
        for section in svc.get_all_sections():
            assert section.word_count > 0
