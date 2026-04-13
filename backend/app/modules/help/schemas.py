"""Help module schemas."""
from pydantic import BaseModel
from typing import Optional


class HelpSectionResponse(BaseModel):
    id: str
    title: str
    content: str
    word_count: int


class HelpSearchResult(BaseModel):
    section_id: str
    section_title: str
    snippet: str
    relevance: float


class HelpSearchRequest(BaseModel):
    query: str
    max_results: int = 5
