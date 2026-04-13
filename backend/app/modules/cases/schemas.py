"""
Clarion — Cases Module Schemas
SF-validated against Octave production org (intergraph-ppm.my.salesforce.com).
These Pydantic models serve as both API validation and inter-module contracts.
"""

from datetime import datetime

from pydantic import BaseModel


class CaseSummaryResponse(BaseModel):
    """Contract: GET /api/v1/cases/{id}/summary"""

    case_id: str
    sf_case_number: str
    subject: str
    status: str
    sub_status: str | None = None  # SF: Sub_Status__c
    priority: str  # Mapped: "2 - High" -> "P2"
    case_owner: str  # SF: Owner.Username
    case_owner_name: str  # SF: Owner.Name
    product: str | None = None  # SF: Support_Product_Name__c (NOT Product__c)
    product_family: str | None = None  # SF: Support_Product_Family__c
    support_area: str | None = None  # SF: PPMArea__c
    environment: str | None = None  # SF: Environment__c
    product_version: str | None = None  # SF: Reported_Version__c
    opened_date: datetime
    resolved_date: datetime | None = None  # SF: ResolvedDate__c
    closed_date: datetime | None = None
    last_activity_at: datetime | None = None  # SF: Last_Activity_Date__c
    case_age_days: int
    is_escalated: bool
    sla_status: str | None = None  # SF: SLA_Status__c
    total_event_count: int
    account_name: str | None = None
    sf_account_id: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None


class CaseListItem(BaseModel):
    """Contract: GET /api/v1/cases (list item) - used in both team and account views"""

    case_id: str
    sf_case_number: str
    subject: str
    status: str
    priority: str
    case_owner: str
    case_owner_name: str
    product: str | None = None
    opened_date: datetime
    case_age_days: int
    is_escalated: bool
    account_name: str | None = None


class CaseEventResponse(BaseModel):
    """Contract: individual event in timeline"""

    event_id: str
    event_type: str  # email, field_change, status_change, owner_change, feed_text, feed_content
    timestamp: datetime
    actor: str | None = None
    actor_type: str  # engineer, customer, internal, system
    direction: str | None = None  # inbound, outbound (emails only)
    subject: str | None = None
    body: str | None = None  # Plain text (HTML stripped for feeds)
    body_html: str | None = None  # Original HTML for UI rendering (feeds)
    has_attachments: bool = False
    thread_id: str | None = None  # Extracted from email subject "thread::XXX::"


class CaseSyncedEvent(BaseModel):
    """Contract: Event emitted to Redis pub/sub after case sync"""

    event_type: str  # "case.synced" or "account_case.synced"
    case_id: str
    team_id: str | None = None  # Present for team sync
    sf_account_id: str | None = None  # Present for account sync
    timestamp: datetime


class AccountSearchResult(BaseModel):
    """Contract: GET /api/v1/accounts/search - disambiguated account result.
    Validated: 8 Transgrid accounts differentiated by Type + Industry + Country."""

    sf_account_id: str  # 18-char Salesforce ID
    name: str  # May be duplicated across accounts
    account_type: str | None = None  # SF: Type ("Cloud Estate", "O/O", "Other")
    industry: str | None = None  # SF: Industry
    billing_country: str | None = None  # SF: BillingCountry
    billing_state: str | None = None  # SF: BillingState
    billing_city: str | None = None  # SF: BillingCity


class MonitoredAccountResponse(BaseModel):
    """Contract: GET /api/v1/accounts/monitored"""

    id: str
    sf_account_id: str
    account_name: str
    account_type: str | None = None
    account_industry: str | None = None
    account_country: str | None = None
    enable_predictions: bool
    enable_sentiment: bool
    open_case_count: int
    total_case_count: int


class AccountCaseSummary(BaseModel):
    """Contract: GET /api/v1/accounts/{id}/summary"""

    sf_account_id: str
    account_name: str
    total_open_cases: int
    priority_breakdown: dict
    status_breakdown: dict
    avg_case_age_days: float
    oldest_case_age_days: int
