"""Clarion test configuration."""

import os
import pytest

# Ensure test environment
os.environ.setdefault("CLARION_DB_PASSWORD", "test")
os.environ.setdefault("CLARION_JWT_SECRET", "test-secret")
os.environ.setdefault("CLARION_ENVIRONMENT", "test")


@pytest.fixture
def sample_org():
    return {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Octave",
        "domain": "hexagon.com",
    }


@pytest.fixture
def sample_user(sample_org):
    return {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "email": "manager@hexagon.com",
        "display_name": "Test Manager",
        "org_id": sample_org["id"],
        "role": "manager",
        "data_scope_type": "team",
    }
