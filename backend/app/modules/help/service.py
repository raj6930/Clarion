"""
Help Documentation Service
Serves documentation content, supports search for chatbot RAG.
Content is stored as markdown files in docs/ directory.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger("clarion.help")


@dataclass
class HelpSection:
    id: str
    title: str
    content: str
    word_count: int = 0


@dataclass
class SearchResult:
    section_id: str
    section_title: str
    snippet: str
    relevance: float


class HelpService:
    """Serves and searches help documentation."""

    def __init__(self):
        self._sections: dict[str, HelpSection] = {}
        self._load_docs()

    def _load_docs(self):
        """Load markdown docs from docs/ directory or embedded content."""
        docs = {
            "user-guide": ("User Guide", self._get_user_guide()),
            "technical": ("Technical Guide", self._get_technical_guide()),
            "troubleshooting": ("Troubleshooting", self._get_troubleshooting()),
        }
        for section_id, (title, content) in docs.items():
            self._sections[section_id] = HelpSection(
                id=section_id,
                title=title,
                content=content,
                word_count=len(content.split()),
            )
        logger.info(f"Help docs loaded: {len(self._sections)} sections")

    def get_section(self, section_id: str) -> HelpSection | None:
        return self._sections.get(section_id)

    def get_all_sections(self) -> list[HelpSection]:
        return list(self._sections.values())

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Simple keyword search across all sections. Phase 12+: vector embeddings."""
        query_lower = query.lower()
        terms = query_lower.split()
        results = []

        for section in self._sections.values():
            content_lower = section.content.lower()
            # Score: count of matching terms
            score = sum(1 for t in terms if t in content_lower) / max(len(terms), 1)

            if score > 0:
                # Extract snippet around first match
                snippet = self._extract_snippet(section.content, terms[0])
                results.append(
                    SearchResult(
                        section_id=section.id,
                        section_title=section.title,
                        snippet=snippet,
                        relevance=score,
                    )
                )

        results.sort(key=lambda r: r.relevance, reverse=True)
        return results[:max_results]

    def get_rag_context(self, query: str, max_chars: int = 2000) -> str:
        """Get relevant documentation context for chatbot RAG."""
        results = self.search(query, max_results=3)
        chunks = []
        total = 0
        for r in results:
            section = self._sections.get(r.section_id)
            if section:
                remaining = max_chars - total
                if remaining <= 0:
                    break
                chunk = section.content[:remaining]
                chunks.append(f"[{section.title}]\n{chunk}")
                total += len(chunk)
        return "\n\n---\n\n".join(chunks)

    def _extract_snippet(self, content: str, term: str, window: int = 150) -> str:
        idx = content.lower().find(term.lower())
        if idx == -1:
            return content[:window] + "..."
        start = max(0, idx - window // 2)
        end = min(len(content), idx + window // 2)
        snippet = content[start:end].strip()
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        return snippet

    def _get_user_guide(self) -> str:
        return """# Clarion User Guide

## Getting Started
Navigate to your Clarion instance and sign in with your credentials. First-time users must be approved by an administrator.

## Dashboard
The dashboard shows headline KPIs, case volume trends, SLA compliance, engineer workload, and cases requiring attention. Switch between six layout presets from Settings.

## Team View vs Account View
Toggle between Team View (cases owned by your team) and Account View (cases for monitored accounts) using the header buttons.

## Cases
Filter by priority, status, owner, product, or date range. Click any case for the full detail view with timeline and AI insights.

## Reviews
AI-first workflow: AI generates a draft, you refine it. Score questions 1-5 using rubric definitions. Provide justification when overriding AI scores.

## Analytics
SLA compliance by priority, resolution trends, workload distribution, and AI-detected patterns.

## Predictions
Escalation risk predictions using AI analysis. High-risk cases appear in the Attention Queue.

## Notifications
Configure alert rules, channels, quiet hours, and debounce from Settings.

## Chatbot
Context-aware AI assistant. Knows your current page and selected case. Can search cases, show metrics, and create reviews."""

    def _get_technical_guide(self) -> str:
        return """# Clarion Technical Guide

## Architecture
Modular monolith: FastAPI + React 18 + PostgreSQL 16 + Redis 7 + Celery 5 + Ollama.

## Module Registry
Self-registering modules with manifests. Feature flags enable/disable without code changes.

## Data Flow
Salesforce → Sync Service → PostgreSQL → API → React. AI: Router → Local (Ollama) or External (Anonymise → Claude/OpenAI → De-anonymise).

## Database
6 migrations, 30+ tables. Run: alembic upgrade head.

## Docker
7 containers. Start: docker compose up -d.

## AI Engines
Ollama/Gemma4 (local, no anonymisation), Claude Opus (external, anonymised), OpenAI (external, anonymised).

## Anonymisation
4-stage pipeline: regex → dictionary → NER → LLM. Zero-tolerance leak tests in CI."""

    def _get_troubleshooting(self) -> str:
        return """# Troubleshooting

## Cannot log in
Check credentials, admin approval status, browser cache. Verify API at /api/v1/health.

## Dashboard shows no data
Check sync status, trigger manual sync, verify team configuration.

## AI not working
Check Ollama container status. Pull model if missing: docker exec clarion-ollama ollama pull gemma2.

## Anonymisation false positives
Mark as false positive, add to passthrough dictionary.

## Notifications not arriving
Check alert rule status, quiet hours, SMTP/webhook config.

## Slow performance
Check system health. Ollama uses ~8GB RAM. Adjust sync frequency for large volumes."""
