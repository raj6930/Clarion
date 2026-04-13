"""Sync module Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class SyncTriggerRequest(BaseModel):
    sync_type: str = "team"  # team | account
    since: str | None = None  # ISO datetime for incremental


class SyncStatusResponse(BaseModel):
    sync_type: str
    status: str  # success | partial | failed | running
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None
    cases_synced: int | None = None
    events_synced: int | None = None
    errors: list[str] = []


class SyncLogEntry(BaseModel):
    id: str
    sync_type: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None
    records_synced: int | None = None
    triggered_by: str | None = None
