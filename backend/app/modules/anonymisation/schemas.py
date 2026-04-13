"""Anonymisation module Pydantic schemas."""

from pydantic import BaseModel


class AnonymiseRequest(BaseModel):
    text: str
    scope: str = "session"  # session | org
    target_engine: str = "claude"


class DetectedEntityResponse(BaseModel):
    entity_type: str
    value: str
    start: int
    end: int
    detection_stage: str
    confidence: float


class MappingResponse(BaseModel):
    pseudonym: str
    entity_type: str
    detection_stage: str
    confidence: float
    is_false_positive: bool = False


class AnonymiseResponse(BaseModel):
    session_id: str | None = None
    anonymised_text: str
    entity_count: int
    entities: list[DetectedEntityResponse]
    mappings: list[MappingResponse]


class DeanonymiseRequest(BaseModel):
    text: str
    session_id: str


class DeanonymiseResponse(BaseModel):
    restored_text: str
    orphaned_tokens: list[str]


class FlagFalsePositiveRequest(BaseModel):
    pseudonym: str


class AddDictionaryRequest(BaseModel):
    term: str
    entity_type: str = "custom"
    match_mode: str = "exact"
