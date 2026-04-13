"""
Clarion — Contract Testing Framework
Validates that module API responses match declared Pydantic schemas,
and that consuming modules can parse producer schemas.

Run: pytest tests/contracts/ -v
"""

import pytest


@pytest.fixture
def contract_context():
    """Shared context for contract tests."""
    return {
        "note": (
            "Contract tests validate inter-module API contracts. "
            "Each module's schemas.py defines the contract. "
            "Producer tests verify output matches the schema. "
            "Consumer tests verify the consuming module can parse it."
        )
    }
