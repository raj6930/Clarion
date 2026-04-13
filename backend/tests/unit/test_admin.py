"""Unit tests for admin service and configuration."""

from app.api.v1.routes.admin_service import (
    DEFAULT_EXCLUDED_STATUSES,
    DEFAULT_FEATURE_FLAGS,
    DEFAULT_TERMINOLOGY,
    ActivityMetrics,
    SystemHealth,
)


class TestSystemHealth:
    def test_defaults(self):
        h = SystemHealth()
        assert h.status == "healthy"
        assert h.active_modules == 10
        assert h.db_status == "connected"

    def test_all_fields_present(self):
        h = SystemHealth()
        fields = h.__dict__
        assert "uptime_hours" in fields
        assert "disk_usage_pct" in fields
        assert "memory_usage_pct" in fields


class TestActivityMetrics:
    def test_defaults(self):
        a = ActivityMetrics()
        assert a.daily_active_users >= 0
        assert a.ai_cost_mtd >= 0


class TestTerminology:
    def test_all_modules_have_terms(self):
        modules = [
            "cases",
            "reviews",
            "analytics",
            "predictions",
            "notifications",
            "chatbot",
            "accounts",
        ]
        for m in modules:
            assert m in DEFAULT_TERMINOLOGY, f"Module '{m}' missing from terminology"

    def test_all_priorities_have_terms(self):
        for p in ["p1", "p2", "p3", "p4"]:
            assert p in DEFAULT_TERMINOLOGY

    def test_roles_have_terms(self):
        for r in ["engineer", "manager", "csm"]:
            assert r in DEFAULT_TERMINOLOGY


class TestFeatureFlags:
    def test_all_modules_have_flags(self):
        expected = [
            "module_cases",
            "module_analytics",
            "module_reviews",
            "module_predictions",
            "module_notifications",
            "module_chatbot",
            "module_anonymisation",
            "module_sync",
            "module_accounts",
        ]
        for flag in expected:
            assert flag in DEFAULT_FEATURE_FLAGS, f"Flag '{flag}' missing"

    def test_all_enabled_by_default(self):
        for flag, enabled in DEFAULT_FEATURE_FLAGS.items():
            assert enabled, f"Flag '{flag}' should be enabled by default"


class TestExcludedStatuses:
    def test_defaults(self):
        assert "Closed" in DEFAULT_EXCLUDED_STATUSES
        assert "Cancelled" in DEFAULT_EXCLUDED_STATUSES
        assert len(DEFAULT_EXCLUDED_STATUSES) >= 2
