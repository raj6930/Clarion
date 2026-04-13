"""Contract tests for admin module schemas."""

import pytest
from pydantic import ValidationError


class TestBrandingContract:
    def test_default_branding(self):
        # Import inline to avoid circular dependency issues in test collection
        from app.api.v1.routes.admin import BrandingConfig

        b = BrandingConfig()
        assert b.primary_colour == "#2563EB"
        assert b.density == "comfortable"
        assert b.default_layout_preset == "editorial"

    def test_custom_branding(self):
        from app.api.v1.routes.admin import BrandingConfig

        b = BrandingConfig(
            company_name="Octave Support",
            primary_colour="#1E40AF",
            dark_mode_default=True,
        )
        assert b.company_name == "Octave Support"
        assert b.dark_mode_default


class TestRoleUpdateContract:
    def test_valid_roles(self):
        from app.api.v1.routes.admin import RoleUpdateRequest

        for role in ["admin", "manager", "csm", "engineer"]:
            r = RoleUpdateRequest(role=role)
            assert r.role == role

    def test_invalid_role_rejected(self):
        from app.api.v1.routes.admin import RoleUpdateRequest

        with pytest.raises(ValidationError):
            RoleUpdateRequest(role="superadmin")


class TestPurgeContract:
    def test_minimum_days(self):
        from app.api.v1.routes.admin import PurgeRequest

        with pytest.raises(ValidationError):
            PurgeRequest(entity="cases", older_than_days=7)  # Min 30

    def test_valid_purge(self):
        from app.api.v1.routes.admin import PurgeRequest

        p = PurgeRequest(entity="cases", older_than_days=90, confirm=True)
        assert p.confirm
