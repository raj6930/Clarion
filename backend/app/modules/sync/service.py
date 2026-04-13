"""
Sync Service
Orchestrates team sync and account sync operations.
Transforms SF records, upserts to PostgreSQL, emits events.
Phase 3: Core sync logic. Phase 4: Adds anonymisation pre-processing.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.integrations.salesforce import SalesforceClient, SFCliError
from app.integrations.salesforce.mapper import (
    map_case_record, map_priority, parse_email_addresses,
    extract_thread_id, strip_html, resolve_actor_type, clean_subject,
)
from app.integrations.salesforce.queries import (
    cases_by_owner, cases_by_account, emails_for_case,
    comments_for_case, feed_for_case, feed_comments_for_item,
    history_for_case,
)

logger = logging.getLogger("clarion.sync")


class SyncResult:
    """Holds the result of a sync operation."""
    def __init__(self):
        self.cases_synced = 0
        self.events_synced = 0
        self.errors: list[str] = []
        self.started_at = datetime.now(timezone.utc)
        self.completed_at: Optional[datetime] = None

    @property
    def status(self) -> str:
        if self.errors:
            return "partial" if self.cases_synced > 0 else "failed"
        return "success"

    @property
    def duration_ms(self) -> int:
        if not self.completed_at:
            return 0
        return int((self.completed_at - self.started_at).total_seconds() * 1000)

    def complete(self):
        self.completed_at = datetime.now(timezone.utc)


class SyncService:
    """Orchestrates Salesforce data synchronisation."""

    def __init__(self, sf_client: SalesforceClient, org_id: str):
        self.sf = sf_client
        self.org_id = org_id

    def team_sync(
        self,
        owner_usernames: list[str],
        since: Optional[str] = None,
    ) -> SyncResult:
        """
        Full team sync: pull cases by owner, then pull events for each case.
        """
        result = SyncResult()
        logger.info(f"Team sync starting: {len(owner_usernames)} engineers, since={since}")

        try:
            # 1. Pull case headers
            soql = cases_by_owner(owner_usernames, since)
            sf_cases = self.sf.query_all(soql)
            logger.info(f"Retrieved {len(sf_cases)} case headers")

            # 2. Transform and upsert each case
            for sf_case in sf_cases:
                try:
                    case_data = map_case_record(sf_case)
                    case_data["org_id"] = self.org_id

                    # Phase 3: In-memory processing. Phase 3b: PostgreSQL upsert.
                    # self._upsert_case(case_data)

                    # 3. Pull events for this case
                    sf_case_id = sf_case.get("Id")
                    if sf_case_id:
                        events = self._sync_case_events(sf_case_id)
                        result.events_synced += events

                    result.cases_synced += 1

                except Exception as e:
                    logger.error(f"Error syncing case {sf_case.get('CaseNumber', '?')}: {e}")
                    result.errors.append(str(e))

        except SFCliError as e:
            logger.error(f"SF CLI error during team sync: {e}")
            result.errors.append(str(e))

        result.complete()
        logger.info(
            f"Team sync complete: {result.cases_synced} cases, "
            f"{result.events_synced} events, {len(result.errors)} errors, "
            f"{result.duration_ms}ms"
        )
        return result

    def account_sync(
        self,
        account_ids: list[str],
        excluded_statuses: list[str],
        since: Optional[str] = None,
    ) -> SyncResult:
        """
        Lightweight account sync: open/active cases only.
        """
        result = SyncResult()
        logger.info(f"Account sync starting: {len(account_ids)} accounts")

        try:
            soql = cases_by_account(account_ids, excluded_statuses, since)
            sf_cases = self.sf.query_all(soql)
            logger.info(f"Retrieved {len(sf_cases)} account cases")

            for sf_case in sf_cases:
                try:
                    case_data = map_case_record(sf_case)
                    case_data["org_id"] = self.org_id
                    result.cases_synced += 1
                except Exception as e:
                    result.errors.append(str(e))

        except SFCliError as e:
            result.errors.append(str(e))

        result.complete()
        logger.info(f"Account sync complete: {result.cases_synced} cases, {result.duration_ms}ms")
        return result

    def _sync_case_events(self, sf_case_id: str) -> int:
        """Pull all event types for a single case and return count."""
        count = 0

        # Emails
        try:
            emails = self.sf.query_all(emails_for_case(sf_case_id))
            for em in emails:
                self._transform_email(em)
                count += 1
        except SFCliError as e:
            logger.warning(f"Email sync failed for {sf_case_id}: {e}")

        # Comments
        try:
            comments = self.sf.query_all(comments_for_case(sf_case_id))
            count += len(comments)
        except SFCliError as e:
            logger.warning(f"Comment sync failed for {sf_case_id}: {e}")

        # CaseFeed (TextPost, ContentPost only)
        try:
            feeds = self.sf.query_all(feed_for_case(sf_case_id))
            for feed in feeds:
                self._transform_feed(feed)
                count += 1

                # Pull FeedComments if any
                comment_count = feed.get("CommentCount", 0) or 0
                if comment_count > 0:
                    try:
                        fc = self.sf.query_all(feed_comments_for_item(feed["Id"]))
                        count += len(fc)
                    except SFCliError:
                        pass
        except SFCliError as e:
            logger.warning(f"Feed sync failed for {sf_case_id}: {e}")

        # CaseHistory (field changes)
        try:
            history = self.sf.query_all(history_for_case(sf_case_id))
            count += len(history)
        except SFCliError as e:
            logger.warning(f"History sync failed for {sf_case_id}: {e}")

        return count

    def _transform_email(self, sf_email: dict) -> dict:
        """Transform SF EmailMessage to Clarion case_event format."""
        return {
            "event_type": "email",
            "event_source": "salesforce_email",
            "sf_record_id": sf_email.get("Id"),
            "timestamp": sf_email.get("MessageDate"),
            "direction": "inbound" if sf_email.get("Incoming") else "outbound",
            "subject": clean_subject(sf_email.get("Subject")),
            "body": sf_email.get("TextBody"),
            "body_html": sf_email.get("HtmlBody"),
            "from_address": sf_email.get("FromAddress"),
            "from_name": sf_email.get("FromName"),
            "to_addresses": parse_email_addresses(sf_email.get("ToAddress")),
            "cc_addresses": parse_email_addresses(sf_email.get("CcAddress")),
            "bcc_addresses": parse_email_addresses(sf_email.get("BccAddress")),
            "thread_id": extract_thread_id(sf_email.get("Subject")),
            "has_attachments": bool(sf_email.get("HasAttachment")),
        }

    def _transform_feed(self, sf_feed: dict) -> dict:
        """Transform SF CaseFeed to Clarion case_event format."""
        body_html = sf_feed.get("Body")
        return {
            "event_type": "feed",
            "event_source": "salesforce_feed",
            "sf_record_id": sf_feed.get("Id"),
            "timestamp": sf_feed.get("CreatedDate"),
            "feed_type": sf_feed.get("Type"),
            "body": strip_html(body_html),
            "body_html": body_html,
            "actor": sf_feed.get("CreatedBy", {}).get("Name") if isinstance(sf_feed.get("CreatedBy"), dict) else None,
            "feed_visibility": sf_feed.get("Visibility"),
            "is_public": sf_feed.get("Visibility") == "AllUsers",
        }
