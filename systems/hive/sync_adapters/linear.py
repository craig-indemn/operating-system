"""Linear sync adapter — pulls issues from Linear via linearis CLI."""
import json
import subprocess
import sys
from datetime import datetime, timezone

from sync_adapters.base import SyncAdapter

LINEARIS_CMD = "linearis-proxy.sh"


class LinearAdapter(SyncAdapter):
    system_name = "linear"
    entity_type = "linear_issue"

    STATUS_MAP = {
        "Triage": "active",
        "Backlog": "active",
        "Todo": "active",
        "In Progress": "active",
        "In Review": "active",
        "Done": "done",
        "Canceled": "archived",
        "Cancelled": "archived",
        "Duplicate": "archived",
    }

    def fetch_records(self, since: datetime | None = None) -> list[dict]:
        """Fetch issues from Linear via linearis CLI."""
        try:
            result = subprocess.run(
                [LINEARIS_CMD, "issues", "list", "--limit", "50"],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode != 0:
                print(f"  linearis error: {result.stderr[:200]}", file=sys.stderr)
                return []
            return json.loads(result.stdout)
        except FileNotFoundError:
            print("  linearis-proxy.sh not found", file=sys.stderr)
            return []
        except json.JSONDecodeError:
            print("  linearis returned invalid JSON", file=sys.stderr)
            return []
        except subprocess.TimeoutExpired:
            print("  linearis timed out", file=sys.stderr)
            return []

    def map_to_hive_record(self, ext: dict) -> dict | None:
        """Transform a Linear issue to a Hive linear_issue entity."""
        identifier = ext.get("identifier", "")
        if not identifier:
            return None

        title = ext.get("title", "")
        state_name = ext.get("state", {}).get("name", "")
        team_name = ext.get("team", {}).get("name", "")
        team_key = ext.get("team", {}).get("key", "")
        assignee_name = ext.get("assignee", {}).get("name", "")
        priority = ext.get("priority", 0)
        labels = [l.get("name", "") for l in ext.get("labels", []) if l.get("name")]

        # Map status
        hive_status = self.map_status(state_name)

        # Map priority (Linear: 0=none, 1=urgent, 2=high, 3=medium, 4=low)
        priority_map = {0: "medium", 1: "critical", 2: "high", 3: "medium", 4: "low"}
        hive_priority = priority_map.get(priority, "medium")

        # Build refs
        refs_out = {}
        # Try to resolve assignee to a person entity
        if assignee_name:
            person_id = self._resolve_person_by_name(assignee_name)
            if person_id:
                refs_out["people"] = [person_id]

        record = {
            "record_id": identifier,
            "type": self.entity_type,
            "name": f"[{identifier}] {title}",
            "key": identifier,
            "description": (ext.get("description") or "")[:500],
            "team": f"{team_name} ({team_key})" if team_key else team_name,
            "priority": hive_priority,
            "labels": labels,
            "domains": ["indemn"],
            "tags": [],
            "status": hive_status,
            "system": self.system_name,
            "external_id": ext.get("id", ""),
        }

        if refs_out:
            record["refs_out"] = refs_out

        return record

    def _resolve_person_by_name(self, name: str) -> str | None:
        """Try to resolve a name to a Hive person entity."""
        # Simple name-to-slug resolution
        from db import get_collection
        coll = get_collection()
        person = coll.find_one(
            {"type": "person", "name": {"$regex": f"^{name}$", "$options": "i"}},
            {"record_id": 1},
        )
        if person:
            return person["record_id"]
        return None


def get_adapter() -> LinearAdapter:
    return LinearAdapter()
