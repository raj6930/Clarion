"""Notifications module Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    channel: str
    title: str
    body: str
    severity: str
    status: str
    related_case_id: str | None = None
    related_case_number: str | None = None
    sent_at: datetime | None = None
    read_at: datetime | None = None
    created_at: datetime | None = None


class AlertRuleResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    severity: str
    channels: list[str]
    schedule_cron: str
    debounce_minutes: int
    is_active: bool
    is_default: bool


class AlertRuleCreateRequest(BaseModel):
    name: str
    description: str | None = None
    condition_expression: dict
    severity: str = "medium"
    channels: list[str] = ["in_app"]
    recipients: dict = {"type": "role", "ids": ["manager"]}
    schedule_cron: str = "0 */1 * * *"
    quiet_hours: dict | None = None
    debounce_minutes: int = 60


class AlertRuleUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    severity: str | None = None
    channels: list[str] | None = None
    is_active: bool | None = None
    debounce_minutes: int | None = None


class UnreadCountResponse(BaseModel):
    count: int
