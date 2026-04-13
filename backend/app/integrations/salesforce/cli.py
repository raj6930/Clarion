"""
Salesforce CLI Wrapper
Executes SOQL queries via the Salesforce CLI (sf).
Handles authentication, query execution, pagination, and error handling.
Phase 3: Core implementation. Proven approach from CaseLens.
"""
import json
import logging
import subprocess
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("clarion.sf")


@dataclass
class SFQueryResult:
    """Result of a SOQL query."""
    records: list[dict]
    total_size: int
    done: bool


class SFCliError(Exception):
    """Raised when SF CLI returns an error."""
    pass


class SalesforceClient:
    """Wrapper around the Salesforce CLI for SOQL queries."""

    def __init__(self, instance_url: str, target_org: Optional[str] = None):
        self.instance_url = instance_url
        self.target_org = target_org
        self._verify_cli()

    def _verify_cli(self) -> None:
        """Verify sf CLI is installed and accessible."""
        try:
            result = subprocess.run(
                ["sf", "version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                raise SFCliError("SF CLI not available")
            logger.info(f"SF CLI verified: {result.stdout.strip()}")
        except FileNotFoundError:
            raise SFCliError("SF CLI (sf) not found. Install: npm install -g @salesforce/cli")

    def query(self, soql: str, bulk: bool = False) -> SFQueryResult:
        """Execute a SOQL query and return results."""
        cmd = ["sf", "data", "query", "--query", soql, "--json"]

        if self.target_org:
            cmd.extend(["--target-org", self.target_org])

        if bulk:
            cmd.append("--bulk")

        logger.debug(f"SF query: {soql[:200]}...")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120
            )
        except subprocess.TimeoutExpired:
            raise SFCliError(f"SF query timed out after 120s: {soql[:100]}")

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            try:
                error_json = json.loads(result.stdout)
                error_msg = error_json.get("message", error_msg)
            except (json.JSONDecodeError, KeyError):
                pass
            raise SFCliError(f"SF query failed: {error_msg}")

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise SFCliError(f"Invalid JSON response from SF CLI")

        result_data = data.get("result", data)
        records = result_data.get("records", [])
        total_size = result_data.get("totalSize", len(records))
        done = result_data.get("done", True)

        logger.info(f"SF query returned {len(records)} of {total_size} records")
        return SFQueryResult(records=records, total_size=total_size, done=done)

    def query_all(self, soql: str) -> list[dict]:
        """Execute query and handle pagination to get all records."""
        all_records = []
        result = self.query(soql)
        all_records.extend(result.records)

        # SF CLI handles pagination internally for non-bulk queries
        # For bulk queries, all results come in one shot
        logger.info(f"SF query_all: {len(all_records)} total records retrieved")
        return all_records
