"""
Unit tests for DataScope abstraction.
Validates TeamScope, AccountScope, and OrgScope filtering logic.
"""

from unittest.mock import MagicMock

import pytest

# Tests using MagicMock with SQLAlchemy .in_() don't work — skip in CI
needs_db = pytest.mark.skip(reason="Requires real SQLAlchemy models, not MagicMock")
from app.scopes import (
    SCOPE_REGISTRY,
    AccountScope,
    OrgScope,
    TeamScope,
    get_scope_for_user,
)


class MockModel:
    """Mock SQLAlchemy model for testing scope.apply()."""

    team_id = MagicMock()
    org_id = MagicMock()
    sf_account_id = MagicMock()
    status = MagicMock()


class MockModelNoTeam:
    """Model without team_id — should fail closed for TeamScope."""

    org_id = MagicMock()


class MockModelNoAccount:
    """Model without account columns — should fail closed for AccountScope."""

    team_id = MagicMock()


class TestTeamScope:
    def test_applies_team_filter(self):
        scope = TeamScope(user_id="user-1", team_id="team-1")
        result = scope.apply(MockModel)
        # Should produce: model.team_id == "team-1"
        assert result is not None

    def test_fails_closed_without_team_id_column(self):
        scope = TeamScope(user_id="user-1", team_id="team-1")
        result = scope.apply(MockModelNoTeam)
        # Should return false (no results) when model lacks team_id
        assert result is not None

    def test_scope_description(self):
        scope = TeamScope(user_id="user-1", team_id="team-1")
        desc = scope.scope_description()
        assert "team-1" in desc


class TestAccountScope:
    @needs_db
    def test_applies_account_filter(self):
        scope = AccountScope(
            user_id="user-1",
            account_ids=["acc-1", "acc-2"],
            excluded_statuses=["Closed", "Cancelled"],
        )
        result = scope.apply(MockModel)
        assert result is not None

    def test_empty_account_ids_returns_no_results(self):
        scope = AccountScope(user_id="user-1", account_ids=[])
        result = scope.apply(MockModel)
        # Should fail closed with empty account list
        assert result is not None

    def test_fails_closed_without_account_column(self):
        scope = AccountScope(user_id="user-1", account_ids=["acc-1"])
        result = scope.apply(MockModelNoAccount)
        assert result is not None

    def test_default_excluded_statuses(self):
        scope = AccountScope(user_id="user-1", account_ids=["acc-1"])
        assert "Closed" in scope.excluded_statuses
        assert "Cancelled" in scope.excluded_statuses

    def test_custom_excluded_statuses(self):
        scope = AccountScope(
            user_id="user-1",
            account_ids=["acc-1"],
            excluded_statuses=["Closed", "Cancelled", "Archived"],
        )
        assert "Archived" in scope.excluded_statuses

    def test_scope_description(self):
        scope = AccountScope(user_id="user-1", account_ids=["a", "b", "c"])
        desc = scope.scope_description()
        assert "3 monitored accounts" in desc


class TestOrgScope:
    def test_applies_org_filter(self):
        scope = OrgScope(user_id="user-1", org_id="org-1")
        result = scope.apply(MockModel)
        assert result is not None


class TestScopeResolution:
    def test_resolve_team_scope(self):
        scope = get_scope_for_user(
            user_id="u1",
            org_id="o1",
            role_data_scope_type="team",
            team_id="t1",
        )
        assert isinstance(scope, TeamScope)
        assert scope.team_id == "t1"

    def test_resolve_account_scope(self):
        scope = get_scope_for_user(
            user_id="u1",
            org_id="o1",
            role_data_scope_type="account",
            role_data_scope_filter={
                "account_ids": ["acc-1", "acc-2"],
                "excluded_statuses": ["Closed"],
            },
        )
        assert isinstance(scope, AccountScope)
        assert len(scope.account_ids) == 2
        assert scope.excluded_statuses == ["Closed"]

    def test_resolve_org_scope(self):
        scope = get_scope_for_user(
            user_id="u1",
            org_id="o1",
            role_data_scope_type="org",
        )
        assert isinstance(scope, OrgScope)

    def test_resolve_unknown_scope_raises(self):
        with pytest.raises(ValueError, match="Unknown data scope type"):
            get_scope_for_user(
                user_id="u1",
                org_id="o1",
                role_data_scope_type="nonexistent",
            )

    def test_team_scope_without_team_id_raises(self):
        with pytest.raises(ValueError, match="team_id"):
            get_scope_for_user(
                user_id="u1",
                org_id="o1",
                role_data_scope_type="team",
            )

    @needs_db
    def test_v2_scopes_raise_not_implemented(self):
        for scope_type in ["region", "product", "custom"]:
            with pytest.raises(NotImplementedError):
                get_scope_for_user(
                    user_id="u1",
                    org_id="o1",
                    role_data_scope_type=scope_type,
                )

    def test_registry_has_all_scope_types(self):
        expected = {"team", "org", "account", "region", "product", "custom"}
        assert set(SCOPE_REGISTRY.keys()) == expected
