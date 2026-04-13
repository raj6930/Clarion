"""
FastAPI dependencies for authentication and authorisation.
Provides get_current_user, require_role, and require_any_role.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.security import decode_token

security = HTTPBearer(auto_error=False)


class CurrentUser:
    """Authenticated user context available in route handlers."""

    def __init__(self, user_id: str, email: str, role: str, org_id: str, display_name: str = ""):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.org_id = org_id
        self.display_name = display_name

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_manager(self) -> bool:
        return self.role in ("admin", "manager")

    @property
    def is_csm(self) -> bool:
        return self.role == "csm"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> CurrentUser:
    """Extract and validate JWT from Authorization header."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Phase 3: Replace with database lookup for full user hydration
    return CurrentUser(
        user_id=payload.get("sub", ""),
        email=payload.get("email", ""),
        role=payload.get("role", ""),
        org_id=payload.get("org_id", ""),
        display_name=payload.get("name", ""),
    )


def require_role(*allowed_roles: str):
    """Dependency factory that restricts access to specific roles."""

    async def _check(user: CurrentUser = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {', '.join(allowed_roles)}",
            )
        return user

    return _check


# Convenience shortcuts
require_admin = require_role("admin")
require_manager_or_admin = require_role("admin", "manager")
require_authenticated = get_current_user
