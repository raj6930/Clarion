"""
Clarion — Cases Module Schemas
SF-validated against Octave production org (intergraph-ppm.my.salesforce.com).
These Pydantic models serve as both API validation and inter-module contracts.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CaseSummaryResponse(BaseModel):
    """Contract: GET /api/v1/cases/{id}/summary"""
    case_id: str
    sf_case_number: str
    subject: str
    status: str
    sub_status: Optional[str] = None  # SF: Sub_Status__c
    priority: str  # Mapped: "2 - High" -> "P2"
    case_owner: str  # SF: Owner.Username
    case_owner_name: str  # SF: Owner.Name
    product: Optional[str] = None  # SF: Support_Product_Name__c (NOT Product__c)
    product_family: Optional[str] = None  # SF: Support_Product_Family__c
    support_area: Optional[str] = None  # SF: PPMArea__c
    environment: Optional[str] = None  # SF: Environment__c
    product_version: Optional[str] = None  # SF: Reported_Version__c
    opened_date: datetime
    resolved_date: Optional[datetime] = None  # SF: ResolvedDate__c
    closed_date: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None  # SF: Last_Activity_Date__c
    case_age_days: int
    is_escalated: bool
    sla_status: Optional[str] = None  # SF: SLA_Status__c
    total_event_count: int
    account_name: Optional[str] = None
    sf_account_id: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None


class CaseListItem(BaseModel):
    """Contract: GET /api/v1/cases (list item) - used in both team and account views"""
    case_id: str
    sf_case_number: str
    subject: str
    status: str
    priority: str
    case_owner: str
    case_owner_name: str
    product: Optional[str] = None
    opened_date: datetime
    case_age_days: int
    is_escalated: bool
    account_name: Optional[str] = None


class CaseEventResponse(BaseModel):
    """Contract: individual event in timeline"""
    event_id: str
    event_type: str  # email, field_change, status_change, owner_change, feed_text, feed_content
    timestamp: datetime
    actor: Optional[str] = None
    actor_type: str  # engineer, customer, internal, system
    direction: Optional[str] = None  # inbound, outbound (emails only)
    subject: Optional[str] = None
    body: Optional[str] = None  # Plain text (HTML stripped for feeds)
    body_html: Optional[str] = None  # Original HTML for UI rendering (feeds)
    has_attachments: bool = False
    thread_id: Optional[str] = None  # Extracted from email subject "thread::XXX::"


class CaseSyncedEvent(BaseModel):
    """Contract: Event emitted to Redis pub/sub after case sync"""
    event_type: str  # "case.synced" or "account_case.synced"
    case_id: str
    team_id: Optional[str] = None  # Present for team sync
    sf_account_id: Optional[str] = None  # Present for account sync
    timestamp: datetime


class AccountSearchResult(BaseModel):
    """Contract: GET /api/v1/accounts/search - disambiguated account result.
    Validated: 8 Transgrid accounts differentiated by Type + Industry + Country."""
    sf_account_id: str  # 18-char Salesforce ID
    name: str  # May be duplicated across accounts
    account_type: Optional[str] = None  # SF: Type ("Cloud Estate", "O/O", "Other")
    industry: Optional[str] = None  # SF: Industry
    billing_country: Optional[str] = None  # SF: BillingCountry
    billing_state: Optional[str] = None  # SF: BillingState
    billing_city: Optional[str] = None  # SF: BillingCity


class MonitoredAccountResponse(BaseModel):
    """Contract: GET /api/v1/accounts/monitored"""
    id: str
    sf_account_id: str
    account_name: str
    account_type: Optional[str] = None
    account_industry: Optional[str] = None
    account_country: Optional[str] = None
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
