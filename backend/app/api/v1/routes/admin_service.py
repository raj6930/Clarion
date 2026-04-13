"""
Admin Service
Handles user management, system health, audit, and all configuration CRUD.
Phase 10: In-memory stubs. Phase 11+: PostgreSQL.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger("clarion.admin")


@dataclass
class SystemHealth:
    status: str = "healthy"
    uptime_hours: float = 0.0
    db_status: str = "connected"
    redis_status: str = "connected"
    ollama_status: str = "connected"
    active_modules: int = 10
    total_users: int = 1
    total_cases: int = 47
    sync_status: str = "idle"
    last_sync_at: str = ""
    disk_usage_pct: float = 42.0
    memory_usage_pct: float = 58.0


@dataclass
class ActivityMetrics:
    daily_active_users: int = 1
    weekly_active_users: int = 1
    ai_requests_today: int = 0
    ai_cost_mtd: float = 0.0
    reviews_completed_mtd: int = 0
    chatbot_queries_today: int = 0
    notifications_sent_today: int = 3
    sync_runs_today: int = 2


# Default terminology map
DEFAULT_TERMINOLOGY = {
    "cases": "Cases",
    "reviews": "Reviews",
    "analytics": "Analytics",
    "predictions": "Predictions",
    "notifications": "Alerts",
    "chatbot": "Assistant",
    "accounts": "Accounts",
    "engineer": "Support Engineer",
    "manager": "Support Manager",
    "csm": "Customer Success Manager",
    "escalation": "Escalation",
    "p1": "P1 — Critical",
    "p2": "P2 — High",
    "p3": "P3 — Medium",
    "p4": "P4 — Low",
}

# Default feature flags
DEFAULT_FEATURE_FLAGS = {
    "module_cases": True,
    "module_analytics": True,
    "module_reviews": True,
    "module_predictions": True,
    "module_notifications": True,
    "module_chatbot": True,
    "module_anonymisation": True,
    "module_sync": True,
    "module_accounts": True,
}

# Default excluded statuses for account views
DEFAULT_EXCLUDED_STATUSES = ["Closed", "Cancelled", "Merged"]
