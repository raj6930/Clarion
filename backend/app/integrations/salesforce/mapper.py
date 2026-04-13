"""
Salesforce Field Mapper
Transforms raw SF records into Clarion's normalised schema.
Handles priority format mapping, email address parsing, HTML stripping,
thread ID extraction, and actor type resolution.
All mappings validated against Octave prod org (intergraph-ppm.my.salesforce.com).
"""
import re
import html
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger("clarion.sf.mapper")


# ─── Priority Mapping ───
# SF format: "1 - Critical", "2 - High", "3 - Medium", "4 - Low"
# Clarion format: P1, P2, P3, P4
PRIORITY_MAP = {
    "1 - Critical": "P1", "1": "P1", "Critical": "P1",
    "2 - High": "P2", "2": "P2", "High": "P2",
    "3 - Medium": "P3", "3": "P3", "Medium": "P3",
    "4 - Low": "P4", "4": "P4", "Low": "P4",
}


def map_priority(sf_priority: Optional[str]) -> str:
    """Map Salesforce priority format to Clarion P1-P4."""
    if not sf_priority:
        return "P4"
    return PRIORITY_MAP.get(sf_priority.strip(), "P4")


# ─── Email Address Parsing ───
# SF stores ToAddress, CcAddress, BccAddress as semicolon-separated strings
def parse_email_addresses(sf_addresses: Optional[str]) -> list[str]:
    """Parse semicolon-separated SF email addresses into a list."""
    if not sf_addresses:
        return []
    return [addr.strip() for addr in sf_addresses.split(";") if addr.strip()]


# ─── Thread ID Extraction ───
# SF embeds thread IDs in email Subject as "thread::XXXXX::"
THREAD_PATTERN = re.compile(r"thread::([^:]+)::")


def extract_thread_id(subject: Optional[str]) -> Optional[str]:
    """Extract thread ID from SF email subject."""
    if not subject:
        return None
    match = THREAD_PATTERN.search(subject)
    return match.group(1) if match else None


def clean_subject(subject: Optional[str]) -> Optional[str]:
    """Remove thread ID marker and common prefixes from email subject."""
    if not subject:
        return None
    cleaned = THREAD_PATTERN.sub("", subject).strip()
    # Remove RE: FW: prefixes for cleaner display
    cleaned = re.sub(r"^(RE|FW|Fwd):\s*", "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned or subject


# ─── HTML Stripping ───
TAG_RE = re.compile(r"<[^>]+>")
MULTI_SPACE = re.compile(r"\s+")
MULTI_NEWLINE = re.compile(r"\n{3,}")


def strip_html(html_content: Optional[str]) -> Optional[str]:
    """Strip HTML tags for AI consumption. Preserve paragraph breaks."""
    if not html_content:
        return None
    text = html_content.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = text.replace("</p>", "\n\n").replace("</div>", "\n")
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    text = MULTI_SPACE.sub(" ", text)
    text = MULTI_NEWLINE.sub("\n\n", text)
    return text.strip()


# ─── Actor Type Resolution ───
def resolve_actor_type(
    actor_email: Optional[str],
    team_emails: set[str],
    contact_emails: set[str],
) -> str:
    """
    Determine if an actor is customer, engineer, internal, or system.
    - If email matches a team member → engineer
    - If email matches a case contact → customer
    - If no email or system-generated → system
    - Otherwise → unknown
    """
    if not actor_email:
        return "system"

    email_lower = actor_email.lower().strip()

    if email_lower in team_emails:
        return "engineer"
    if email_lower in contact_emails:
        return "customer"

    # Heuristic: known system addresses
    system_patterns = ["noreply@", "no-reply@", "mailer-daemon@", "postmaster@", "salesforce.com"]
    if any(pat in email_lower for pat in system_patterns):
        return "system"

    return "unknown"


# ─── Case Header Field Mapping ───
# SF field name → Clarion column name
CASE_FIELD_MAP = {
    "Id": "sf_case_id",
    "CaseNumber": "sf_case_number",
    "Subject": "subject",
    "Description": "description",
    "Status": "status",
    "Priority": "_priority_raw",  # Needs mapping via map_priority()
    "Owner.Username": "case_owner",
    "Owner.Name": "case_owner_name",
    "Origin": "case_origin",
    "Type": "case_type",
    "Reason": "case_reason",
    "Contact.Name": "contact_name",
    "Contact.Email": "contact_email",
    "Contact.Phone": "contact_phone",
    "Account.Id": "_sf_account_id",
    "Support_Product_Name__c": "product",
    "Support_Product_Family__c": "product_family",
    "PPMArea__c": "support_area",
    "PPMSubArea__c": "support_sub_area",
    "Environment__c": "environment",
    "Reported_Version__c": "product_version",
    "Sub_Status__c": "sub_status",
    "CreatedDate": "opened_date",
    "ClosedDate": "closed_date",
    "LastModifiedDate": "last_modified_sf",
    "SLA_Status__c": "sla_status",
    "IsEscalated": "is_escalated",
    "Escalation_Date_Time__c": "escalated_at",
    "Reason_for_Escalation__c": "escalation_reason",
    "Reason_for_Escalation_Category__c": "escalation_category",
    "Management_Escalation__c": "management_escalation",
    "Internal_Escalation__c": "internal_escalation",
    "Resolution_Notes__c": "resolution_summary",
    "Root_Cause__c": "root_cause",
    "Workaround_Provided__c": "workaround_provided",
    "Workaround_Summary__c": "workaround_summary",
    "BugNumber__c": "bug_number",
    "TRCR_Number__c": "trcr_number",
    "TRCR_External_Status__c": "trcr_status",
    "TRCR_Type__c": "trcr_type",
    "ResolvedDate__c": "resolved_date",
    "Survey_CSAT_Rating__c": "csat_rating",
    "Survey_Response__c": "survey_response",
    "Article_Linked__c": "article_linked",
    "Platinum_Customer__c": "platinum_customer",
}


def map_case_record(sf_record: dict) -> dict:
    """Transform a raw SF Case record into Clarion's normalised case dict."""
    result = {}

    for sf_field, clarion_field in CASE_FIELD_MAP.items():
        value = _get_nested(sf_record, sf_field)
        if value is not None:
            result[clarion_field] = value

    # Apply priority mapping
    raw_priority = result.pop("_priority_raw", None)
    result["priority"] = map_priority(raw_priority)

    # Boolean defaults
    for bool_field in ["is_escalated", "article_linked", "platinum_customer", "workaround_provided"]:
        if bool_field in result:
            result[bool_field] = bool(result[bool_field])
        else:
            result[bool_field] = False

    return result


def _get_nested(record: dict, field_path: str):
    """Get a value from a nested dict using dot notation (e.g., 'Owner.Name')."""
    parts = field_path.split(".")
    current = record
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current
