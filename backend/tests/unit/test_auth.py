"""
Unit tests for authentication module.
Tests JWT creation/validation, password hashing, and role checking.
"""

from app.auth.dependencies import CurrentUser
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        pw = "TestPassword123!"
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert not verify_password("wrong", hashed)

    def test_different_hashes_each_time(self):
        pw = "SamePassword"
        h1 = hash_password(pw)
        h2 = hash_password(pw)
        assert h1 != h2  # bcrypt salts differ
        assert verify_password(pw, h1)
        assert verify_password(pw, h2)


class TestJWT:
    def test_create_and_decode_access_token(self):
        data = {
            "sub": "usr-001",
            "email": "test@example.com",
            "role": "manager",
            "org_id": "org-001",
        }
        token = create_access_token(data)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "usr-001"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "manager"

    def test_create_refresh_token_has_type(self):
        data = {"sub": "usr-001", "email": "test@example.com"}
        token = create_refresh_token(data)
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"

    def test_invalid_token_returns_none(self):
        assert decode_token("garbage.token.here") is None

    def test_tampered_token_returns_none(self):
        token = create_access_token({"sub": "usr-001"})
        # Tamper with last character
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        assert decode_token(tampered) is None


class TestCurrentUser:
    def test_role_properties(self):
        admin = CurrentUser("1", "a@b.com", "admin", "org-1")
        assert admin.is_admin
        assert admin.is_manager  # admin is also a manager-level user

        manager = CurrentUser("2", "m@b.com", "manager", "org-1")
        assert not manager.is_admin
        assert manager.is_manager

        csm = CurrentUser("3", "c@b.com", "csm", "org-1")
        assert not csm.is_admin
        assert not csm.is_manager
        assert csm.is_csm

        eng = CurrentUser("4", "e@b.com", "engineer", "org-1")
        assert not eng.is_admin
        assert not eng.is_manager
        assert not eng.is_csm
