"""
Clarion — DataScope Abstraction
Pluggable data filtering at the repository layer.

V1 ships with TeamScope only. Adding new scopes in V2 requires only
a new class implementation — no query rewrites.

Usage in repository:
    from app.scopes import get_scope_for_user

    class CaseRepository:
        async def list_cases(self, user: User, filters: dict) -> list[Case]:
            scope = get_scope_for_user(user)
            query = select(Case).where(scope.apply(Case))
            # ... add filters, pagination, etc.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import and_, or_, true
from sqlalchemy.sql import ColumnElement

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("clarion.scopes")


class DataScope(ABC):
    """
    Abstract base for data scope implementations.
    
    Each scope defines how to filter database queries based on the
    user's role and scope configuration. The apply() method returns
    a SQLAlchemy WHERE clause that restricts data access.
    """

    def __init__(self, user_id: str, scope_filter: Optional[dict] = None):
        self.user_id = user_id
        self.scope_filter = scope_filter or {}

    @abstractmethod
    def apply(self, model: Any) -> ColumnElement:
        """
        Return a SQLAlchemy WHERE clause that filters the given model
        to only rows this user should see.
        
        Args:
            model: SQLAlchemy model class (e.g., Case, Review)
            
        Returns:
            SQLAlchemy boolean expression for WHERE clause
        """
        ...

    @abstractmethod
    def scope_description(self) -> str:
        """Human-readable description of what this scope allows."""
        ...


class TeamScope(DataScope):
    """
    V1 default scope. User sees only data belonging to their team.
    
    Requires the model to have a `team_id` column.
    The team_id is resolved from the user's team membership.
    """

    def __init__(self, user_id: str, team_id: str, scope_filter: Optional[dict] = None):
        super().__init__(user_id, scope_filter)
        self.team_id = team_id

    def apply(self, model: Any) -> ColumnElement:
        if not hasattr(model, "team_id"):
            logger.warning(
                f"Model {model.__name__} has no team_id column. "
                f"TeamScope cannot filter — returning no results for safety."
            )
            # Fail closed: if the model doesn't support team scoping, show nothing
            return false_clause()

        return model.team_id == self.team_id

    def scope_description(self) -> str:
        return f"Team-scoped: sees data for team {self.team_id}"


class OrgScope(DataScope):
    """
    Admin/executive scope. User sees all data in their organisation.
    
    Requires the model to have an `org_id` column.
    """

    def __init__(self, user_id: str, org_id: str, scope_filter: Optional[dict] = None):
        super().__init__(user_id, scope_filter)
        self.org_id = org_id

    def apply(self, model: Any) -> ColumnElement:
        if not hasattr(model, "org_id"):
            return true()
        return model.org_id == self.org_id

    def scope_description(self) -> str:
        return f"Org-scoped: sees all data in organisation {self.org_id}"


# ═══════════════════════════════════════════════════════
# V2 Scope Stubs — Ready for implementation
# ═══════════════════════════════════════════════════════

class AccountScope(DataScope):
    """
    V1: User sees data for their monitored accounts.
    Only includes cases NOT in excluded statuses.
    
    Used by:
    - Managers in account view mode
    - CSM / Accounts roles (their only scope)
    """

    def __init__(
        self,
        user_id: str,
        account_ids: list[str],
        excluded_statuses: list[str] | None = None,
        scope_filter: Optional[dict] = None,
    ):
        super().__init__(user_id, scope_filter)
        self.account_ids = account_ids
        self.excluded_statuses = excluded_statuses or ["Closed", "Cancelled"]

    def apply(self, model: Any) -> ColumnElement:
        if not self.account_ids:
            logger.warning(
                f"AccountScope for user {self.user_id} has no account_ids. "
                f"Returning no results for safety."
            )
            return false_clause()

        # Model must have sf_account_id (cases table via account FK)
        # or account_id depending on the model
        account_col = None
        if hasattr(model, "sf_account_id"):
            account_col = model.sf_account_id
        elif hasattr(model, "account_id"):
            account_col = model.account_id
        else:
            logger.warning(
                f"Model {model.__name__} has no sf_account_id or account_id column. "
                f"AccountScope cannot filter — returning no results for safety."
            )
            return false_clause()

        conditions = [account_col.in_(self.account_ids)]

        # Exclude closed/cancelled statuses if the model has a status column
        if hasattr(model, "status") and self.excluded_statuses:
            conditions.append(~model.status.in_(self.excluded_statuses))

        return and_(*conditions)

    def scope_description(self) -> str:
        return (
            f"Account-scoped: sees data for {len(self.account_ids)} monitored accounts, "
            f"excluding statuses: {self.excluded_statuses}"
        )


class RegionScope(DataScope):
    """V2: User sees data for their region(s)."""

    def apply(self, model: Any) -> ColumnElement:
        raise NotImplementedError("RegionScope is planned for V2")

    def scope_description(self) -> str:
        return "Region-scoped: sees data for assigned regions"


class ProductScope(DataScope):
    """V2: User sees data for their product(s)."""

    def apply(self, model: Any) -> ColumnElement:
        raise NotImplementedError("ProductScope is planned for V2")

    def scope_description(self) -> str:
        return "Product-scoped: sees data for assigned products"


class CustomScope(DataScope):
    """V2: Admin-defined filter expression."""

    def apply(self, model: Any) -> ColumnElement:
        raise NotImplementedError("CustomScope is planned for V2")

    def scope_description(self) -> str:
        return "Custom-scoped: admin-defined filter"


# ═══════════════════════════════════════════════════════
# Scope Registry and Resolution
# ═══════════════════════════════════════════════════════

SCOPE_REGISTRY: dict[str, type[DataScope]] = {
    "team": TeamScope,
    "org": OrgScope,
    "account": AccountScope,
    "region": RegionScope,
    "product": ProductScope,
    "custom": CustomScope,
}


def get_scope_for_user(
    user_id: str,
    org_id: str,
    role_data_scope_type: str,
    role_data_scope_filter: Optional[dict] = None,
    team_id: Optional[str] = None,
) -> DataScope:
    """
    Resolve the correct DataScope implementation for a user based on their role.
    
    This is the single entry point for all repository-layer data filtering.
    Called by dependency injection in route handlers.
    
    Args:
        user_id: The authenticated user's ID
        org_id: The user's organisation ID
        role_data_scope_type: From the user's role record (team, org, account, etc.)
        role_data_scope_filter: From the user's role record (scope-specific config)
        team_id: The user's team ID (required for TeamScope)
        
    Returns:
        A DataScope instance ready to apply to queries
        
    Raises:
        ValueError: If the scope type is unknown
        NotImplementedError: If the scope type is planned for V2
    """
    scope_class = SCOPE_REGISTRY.get(role_data_scope_type)
    if not scope_class:
        raise ValueError(
            f"Unknown data scope type: {role_data_scope_type}. "
            f"Available: {list(SCOPE_REGISTRY.keys())}"
        )

    # Each scope type requires different constructor args
    if role_data_scope_type == "team":
        if not team_id:
            raise ValueError("TeamScope requires a team_id")
        return TeamScope(user_id=user_id, team_id=team_id, scope_filter=role_data_scope_filter)

    elif role_data_scope_type == "org":
        return OrgScope(user_id=user_id, org_id=org_id, scope_filter=role_data_scope_filter)

    elif role_data_scope_type == "account":
        account_ids = (role_data_scope_filter or {}).get("account_ids", [])
        excluded_statuses = (role_data_scope_filter or {}).get("excluded_statuses", ["Closed", "Cancelled"])
        return AccountScope(
            user_id=user_id,
            account_ids=account_ids,
            excluded_statuses=excluded_statuses,
            scope_filter=role_data_scope_filter,
        )

    else:
        # V2 scopes — will raise NotImplementedError
        return scope_class(user_id=user_id, scope_filter=role_data_scope_filter)


def false_clause() -> ColumnElement:
    """SQLAlchemy expression that always evaluates to False."""
    from sqlalchemy import literal
    return literal(False)
