"""Base class for Hive sync adapters.

Each adapter implements:
- fetch_records(): Pull records from the external system
- map_to_hive_record(): Transform external record to Hive document format
- get_sync_state(): Read last sync timestamp from MongoDB
- push_status(): (optional) Push status changes back to external system

Dedup: Uses system + external_id to prevent duplicates.
Incremental: Tracks last sync timestamp per adapter in MongoDB.
"""
import sys
from datetime import datetime, timezone

from db import get_collection


class SyncAdapter:
    """Base class for sync adapters."""

    # Subclasses must set these
    system_name: str = ""       # e.g., "linear", "calendar", "slack", "github"
    entity_type: str = ""       # e.g., "linear_issue", "calendar_event"

    # Status mapping: external status → Hive status
    STATUS_MAP: dict[str, str] = {}

    def __init__(self):
        self.coll = get_collection()
        self.stats = {"fetched": 0, "created": 0, "updated": 0, "errors": 0}

    def sync(self) -> dict:
        """Run the full sync cycle. Returns stats dict."""
        print(f"Syncing {self.system_name}...", file=sys.stderr)

        last_sync = self.get_sync_state()
        records = self.fetch_records(since=last_sync)
        self.stats["fetched"] = len(records)

        for ext_record in records:
            try:
                hive_doc = self.map_to_hive_record(ext_record)
                if not hive_doc:
                    continue
                self._upsert(hive_doc)
            except Exception as e:
                print(f"  Error syncing record: {e}", file=sys.stderr)
                self.stats["errors"] += 1

        self._update_sync_state()
        print(
            f"  {self.system_name}: {self.stats['created']} created, "
            f"{self.stats['updated']} updated, {self.stats['errors']} errors",
            file=sys.stderr,
        )
        return self.stats

    def fetch_records(self, since: datetime | None = None) -> list[dict]:
        """Fetch records from the external system. Override in subclass."""
        raise NotImplementedError

    def map_to_hive_record(self, external_record: dict) -> dict | None:
        """Transform external record to Hive document format. Override in subclass.

        Must return a dict with at minimum:
        - record_id: unique identifier (e.g., "AI-123" for Linear)
        - type: entity type (e.g., "linear_issue")
        - name/title: display value
        - status: mapped to Hive status
        - system: system name
        - external_id: original external ID
        - domains: list of domains
        """
        raise NotImplementedError

    def push_status(self, record_id: str, new_status: str) -> bool:
        """Push a status change back to the external system. Optional override.

        Returns True if successful.
        """
        return False

    def map_status(self, external_status: str) -> str:
        """Map external status to Hive status using STATUS_MAP."""
        return self.STATUS_MAP.get(external_status, "active")

    def get_sync_state(self) -> datetime | None:
        """Read last sync timestamp for this adapter from MongoDB."""
        state = self.coll.database["sync_state"].find_one(
            {"adapter": self.system_name}
        )
        if state:
            return state.get("last_sync")
        return None

    def _update_sync_state(self):
        """Update last sync timestamp for this adapter."""
        self.coll.database["sync_state"].update_one(
            {"adapter": self.system_name},
            {"$set": {
                "adapter": self.system_name,
                "last_sync": datetime.now(timezone.utc),
                "stats": self.stats,
            }},
            upsert=True,
        )

    def _upsert(self, hive_doc: dict):
        """Insert or update a record, deduplicating by record_id."""
        record_id = hive_doc["record_id"]
        now = datetime.now(timezone.utc)

        existing = self.coll.find_one({"record_id": record_id})
        if existing:
            # Update — preserve created_at
            hive_doc["updated_at"] = now
            hive_doc.pop("created_at", None)
            self.coll.update_one(
                {"record_id": record_id},
                {"$set": hive_doc},
            )
            self.stats["updated"] += 1
        else:
            # Insert
            hive_doc["created_at"] = now
            hive_doc["updated_at"] = now
            self.coll.insert_one(hive_doc)
            self.stats["created"] += 1

    def _resolve_person(self, email: str) -> str | None:
        """Resolve an email address to a Hive person entity record_id."""
        person = self.coll.find_one(
            {"type": "person", "email": email},
            {"record_id": 1},
        )
        if person:
            return person["record_id"]
        return None
