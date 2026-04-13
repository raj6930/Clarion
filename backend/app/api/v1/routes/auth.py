"""
Authentication endpoints: register, login, refresh, me, change-password, logout.
Phase 2: In-memory user store for development. Phase 3: PostgreSQL via SQLAlchemy.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.security import (
    hash_password, verify_password, create_access_token, create_refresh_token, decode_token,
)
from app.auth.dependencies import get_current_user, CurrentUser
from app.auth.schemas import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse,
    RefreshRequest, ChangePasswordRequest,
)
from app.config import settings

router = APIRouter()

# ─── Phase 2: In-memory user store (replaced by DB in Phase 3) ───
_users: dict[str, dict] = {
    "demo@hexagon.com": {
        "id": "usr-001",
        "email": "demo@hexagon.com",
        "display_name": "Raj Singh",
        "password_hash": hash_password("Clarion2026!"),
        "role": "manager",
        "org_id": "org-001",
        "org_name": "Octave",
        "team_name": "APAC Support",
        "is_active": True,
    }
}


def _user_to_response(u: dict) -> UserResponse:
    return UserResponse(
        id=u["id"], email=u["email"], display_name=u["display_name"],
        role=u["role"], org_id=u["org_id"], org_name=u["org_name"],
        team_name=u.get("team_name"),
    )


def _create_tokens(u: dict) -> TokenResponse:
    token_data = {
        "sub": u["id"], "email": u["email"], "role": u["role"],
        "org_id": u["org_id"], "name": u["display_name"],
    }
    access = create_access_token(token_data)
    refresh = create_refresh_token(token_data)
    return TokenResponse(
        access_token=access, refresh_token=refresh,
        expires_in=settings.jwt_expire_minutes * 60,
        user=_user_to_response(u),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest):
    """Register a new user account."""
    if req.email in _users:
        raise HTTPException(status_code=409, detail="Email already registered")

    user_id = f"usr-{len(_users) + 1:03d}"
    user = {
        "id": user_id,
        "email": req.email,
        "display_name": req.display_name,
        "password_hash": hash_password(req.password),
        "role": "manager",  # Phase 3: pending approval flow
        "org_id": "org-001",
        "org_name": "Octave",
        "team_name": None,
        "is_active": True,
    }
    _users[req.email] = user
    return _create_tokens(user)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Authenticate with email and password."""
    user = _users.get(req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    return _create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshRequest):
    """Exchange a refresh token for new access + refresh tokens."""
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    email = payload.get("email")
    user = _users.get(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return _create_tokens(user)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """Get current authenticated user profile."""
    user = _users.get(current_user.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_to_response(user)


@router.put("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Change password for current user."""
    user = _users.get(current_user.email)
    if not user or not verify_password(req.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user["password_hash"] = hash_password(req.new_password)
    return {"data": {"updated": True}}


@router.post("/logout")
async def logout(current_user: CurrentUser = Depends(get_current_user)):
    """Logout (invalidate token). Phase 3: Add to token blacklist in Redis."""
    return {"data": {"logged_out": True}}
