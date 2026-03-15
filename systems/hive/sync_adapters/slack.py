"""Slack sync adapter — pulls recent mentions from Slack via Python SDK."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

from sync_adapters.base import SyncAdapter

# Script to run via slack-env.sh to fetch recent mentions
_FETCH_SCRIPT = '''
import json, sys, os
sys.path.insert(0, os.path.join(os.environ.get("OS_ROOT", "/Users/home/Repositories/operating-system"), "lib"))
from slack_client import get_client

client = get_client()
results = client.search_messages(query="to:me", count=20, sort="timestamp", sort_dir="desc")
messages = results.get("messages", {}).get("matches", [])

output = []
for m in messages:
    output.append({
        "ts": m.get("ts", ""),
        "text": m.get("text", "")[:300],
        "channel": m.get("channel", {}).get("name", "unknown"),
        "channel_id": m.get("channel", {}).get("id", ""),
        "user": m.get("username", ""),
        "permalink": m.get("permalink", ""),
    })
print(json.dumps(output))
'''


class SlackAdapter(SyncAdapter):
    system_name = "slack"
    entity_type = "slack_message"

    def fetch_records(self, since: datetime | None = None) -> list[dict]:
        """Fetch recent Slack mentions via slack-env.sh + Python SDK."""
        try:
            result = subprocess.run(
                ["slack-env.sh", "python3", "-c", _FETCH_SCRIPT],
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "PYTHONPATH": ""},
            )
            if result.returncode != 0:
                print(f"  slack error: {result.stderr[:200]}", file=sys.stderr)
                return []
            return json.loads(result.stdout)
        except FileNotFoundError:
            print("  slack-env.sh not found", file=sys.stderr)
            return []
        except json.JSONDecodeError:
            print("  slack returned invalid JSON", file=sys.stderr)
            return []
        except subprocess.TimeoutExpired:
            print("  slack timed out", file=sys.stderr)
            return []

    def map_to_hive_record(self, ext: dict) -> dict | None:
        """Transform a Slack message to a Hive slack_message entity."""
        ts = ext.get("ts", "")
        if not ts:
            return None

        text = ext.get("text", "No text")
        channel = ext.get("channel", "unknown")
        user = ext.get("user", "")

        # Build a short record ID from timestamp
        record_id = f"slack-{ts.replace('.', '-')}"

        # Truncate text for name
        name_text = text[:80] + ("..." if len(text) > 80 else "")
        name = f"#{channel}: {name_text}"

        record = {
            "record_id": record_id,
            "type": self.entity_type,
            "name": name,
            "channel": channel,
            "text": text,
            "from_user": user,
            "domains": ["indemn"],
            "tags": [],
            "status": "active",
            "system": self.system_name,
            "external_id": ts,
        }

        # Try to resolve sender to person entity
        refs_out = {}
        if user:
            person_id = self._resolve_person_by_name(user)
            if person_id:
                refs_out["people"] = [person_id]
        if refs_out:
            record["refs_out"] = refs_out

        return record

    def _resolve_person_by_name(self, name: str) -> str | None:
        """Try to resolve a Slack username to a Hive person entity."""
        from db import get_collection
        coll = get_collection()
        # Try exact match first, then case-insensitive
        for query in [
            {"type": "person", "name": name},
            {"type": "person", "name": {"$regex": f"^{name}$", "$options": "i"}},
        ]:
            person = coll.find_one(query, {"record_id": 1})
            if person:
                return person["record_id"]
        return None


def get_adapter() -> SlackAdapter:
    return SlackAdapter()
