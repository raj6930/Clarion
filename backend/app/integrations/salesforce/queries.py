"""
SOQL Query Builder
Pre-built queries validated against Octave prod org.
All field names confirmed via SF validation session.
"""
from typing import Optional


# ─── Case fields (validated) ───
CASE_FIELDS = """
    Id, CaseNumber, Subject, Description, Status, Priority,
    Owner.Username, Owner.Name, Origin, Type, Reason,
    Contact.Name, Contact.Email, Contact.Phone,
    Account.Id,
    Support_Product_Name__c, Support_Product_Family__c,
    PPMArea__c, PPMSubArea__c, Environment__c, Reported_Version__c, Sub_Status__c,
    CreatedDate, ClosedDate, LastModifiedDate,
    SLA_Status__c, IsEscalated,
    Escalation_Date_Time__c, Reason_for_Escalation__c, Reason_for_Escalation_Category__c,
    Management_Escalation__c, Internal_Escalation__c,
    Resolution_Notes__c, Root_Cause__c,
    Workaround_Provided__c, Workaround_Summary__c,
    BugNumber__c, TRCR_Number__c, TRCR_External_Status__c, TRCR_Type__c,
    ResolvedDate__c, Survey_CSAT_Rating__c, Survey_Response__c,
    Article_Linked__c, Platinum_Customer__c
""".strip()


def cases_by_owner(owner_usernames: list[str], since: Optional[str] = None) -> str:
    """Team sync: cases owned by team members."""
    owners = ", ".join(f"'{u}'" for u in owner_usernames)
    where = f"Owner.Username IN ({owners})"
    if since:
        where += f" AND LastModifiedDate > {since}"
    return f"SELECT {CASE_FIELDS} FROM Case WHERE {where} ORDER BY LastModifiedDate DESC"


def cases_by_account(account_ids: list[str], excluded_statuses: list[str], since: Optional[str] = None) -> str:
    """Account sync: open/active cases by account ID."""
    accounts = ", ".join(f"'{a}'" for a in account_ids)
    statuses = ", ".join(f"'{s}'" for s in excluded_statuses)
    where = f"AccountId IN ({accounts}) AND Status NOT IN ({statuses})"
    if since:
        where += f" AND LastModifiedDate > {since}"
    return f"SELECT {CASE_FIELDS} FROM Case WHERE {where} ORDER BY LastModifiedDate DESC"


def emails_for_case(case_id: str) -> str:
    """Pull EmailMessage records for a case."""
    return f"""
        SELECT Id, ParentId, Subject, TextBody, HtmlBody,
               FromAddress, FromName, ToAddress, CcAddress, BccAddress,
               Status, Incoming, MessageDate, HasAttachment
        FROM EmailMessage
        WHERE ParentId = '{case_id}'
        ORDER BY MessageDate ASC
    """


def comments_for_case(case_id: str) -> str:
    """Pull CaseComment records for a case."""
    return f"""
        SELECT Id, ParentId, CommentBody, IsPublished,
               CreatedById, CreatedBy.Name, CreatedDate
        FROM CaseComment
        WHERE ParentId = '{case_id}'
        ORDER BY CreatedDate ASC
    """


def feed_for_case(case_id: str) -> str:
    """Pull CaseFeed (not FeedItem — requires Id filter). Validated approach."""
    return f"""
        SELECT Id, Type, Body, Title,
               CreatedById, CreatedBy.Name, CreatedDate,
               Visibility, CommentCount, IsRichText
        FROM CaseFeed
        WHERE ParentId = '{case_id}'
          AND Type IN ('TextPost', 'ContentPost')
        ORDER BY CreatedDate ASC
    """


def feed_comments_for_item(feed_item_id: str) -> str:
    """Pull FeedComment for items with CommentCount > 0."""
    return f"""
        SELECT Id, FeedItemId, CommentBody,
               CreatedById, CreatedBy.Name, CreatedDate
        FROM FeedComment
        WHERE FeedItemId = '{feed_item_id}'
        ORDER BY CreatedDate ASC
    """


def history_for_case(case_id: str) -> str:
    """Pull CaseHistory for field changes."""
    return f"""
        SELECT Id, CaseId, Field, OldValue, NewValue,
               CreatedById, CreatedBy.Name, CreatedDate
        FROM CaseHistory
        WHERE CaseId = '{case_id}'
        ORDER BY CreatedDate ASC
    """


def search_accounts(name_partial: str) -> str:
    """Search accounts by partial name with disambiguation fields."""
    return f"""
        SELECT Id, Name, Type, Industry, BillingCountry
        FROM Account
        WHERE Name LIKE '%{name_partial}%'
        ORDER BY Name ASC
        LIMIT 50
    """
