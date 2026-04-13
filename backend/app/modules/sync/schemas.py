"""Sync module Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SyncTriggerRequest(BaseModel):
    sync_type: str = "team"  # team | account
    since: Optional[str] = None  # ISO datetime for incremental


class SyncStatusResponse(BaseModel):
    sync_type: str
    status: str  # success | partial | failed | running
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    cases_synced: Optional[int] = None
    events_synced: Optional[int] = None
    errors: list[str] = []


class SyncLogEntry(BaseModel):
    id: str
    sync_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    records_synced: Optional[int] = None
    triggered_by: Optional[str] = None
