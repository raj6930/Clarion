"""Contract tests for sync module schemas."""
import pytest
from app.modules.sync.schemas import SyncTriggerRequest, SyncStatusResponse, SyncLogEntry


class TestSyncTriggerContract:
    def test_default_values(self):
        req = SyncTriggerRequest()
        assert req.sync_type == "team"
        assert req.since is None

    def test_account_type(self):
        req = SyncTriggerRequest(sync_type="account")
        assert req.sync_type == "account"


class TestSyncStatusContract:
    def test_minimal_response(self):
        resp = SyncStatusResponse(sync_type="team", status="success")
        assert resp.sync_type == "team"
        assert resp.errors == []

    def test_full_response(self):
        resp = SyncStatusResponse(
            sync_type="account",
            status="partial",
            cases_synced=42,
            events_synced=180,
            errors=["timeout on case 123"],
        )
        assert resp.cases_synced == 42
        assert len(resp.errors) == 1
