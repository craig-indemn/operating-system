"""Calendar sync adapter — pulls events from Google Calendar via gog CLI."""
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta

from sync_adapters.base import SyncAdapter


class CalendarAdapter(SyncAdapter):
    system_name = "calendar"
    entity_type = "calendar_event"

    STATUS_MAP = {}  # Computed dynamically based on time

    def fetch_records(self, since: datetime | None = None) -> list[dict]:
        """Fetch upcoming calendar events via gog CLI."""
        try:
            result = subprocess.run(
                ["gog", "calendar", "list", "--limit", "20", "--json"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                print(f"  gog error: {result.stderr[:200]}", file=sys.stderr)
                return []
            data = json.loads(result.stdout)
            return data.get("events", [])
        except FileNotFoundError:
            print("  gog CLI not found", file=sys.stderr)
            return []
        except json.JSONDecodeError:
            print("  gog returned invalid JSON", file=sys.stderr)
            return []
        except subprocess.TimeoutExpired:
            print("  gog timed out", file=sys.stderr)
            return []

    def map_to_hive_record(self, ext: dict) -> dict | None:
        """Transform a Google Calendar event to a Hive calendar_event entity."""
        event_id = ext.get("id", "")
        summary = ext.get("summary", "No title")
        if not event_id:
            return None

        # Parse start/end times
        start_raw = ext.get("start", {})
        end_raw = ext.get("end", {})
        start_str = start_raw.get("dateTime", start_raw.get("date", ""))
        end_str = end_raw.get("dateTime", end_raw.get("date", ""))

        # Determine status based on time
        now = datetime.now(timezone.utc)
        upcoming_window = now + timedelta(hours=48)
        status = "upcoming"
        try:
            # Parse ISO datetime
            if "T" in start_str:
                start_dt = datetime.fromisoformat(start_str)
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=timezone.utc)
                if start_dt < now:
                    status = "done"
                elif start_dt <= upcoming_window:
                    status = "active"
        except (ValueError, TypeError):
            pass

        # Resolve attendees to person entities
        refs_out = {}
        attendee_emails = []
        for att in ext.get("attendees", []):
            email = att.get("email", "")
            if email:
                attendee_emails.append(email)
                person_id = self._resolve_person(email)
                if person_id:
                    refs_out.setdefault("people", []).append(person_id)

        # Truncate event ID for record_id (they can be very long)
        # Use a hash-based short ID
        short_id = event_id[:40] if len(event_id) <= 40 else event_id[:20]
        record_id = f"cal-{short_id}"

        record = {
            "record_id": record_id,
            "type": self.entity_type,
            "name": summary,
            "start": start_str,
            "end": end_str,
            "location": ext.get("location", ""),
            "description": (ext.get("description") or "")[:500],
            "domains": ["indemn"],
            "tags": [],
            "status": status,
            "system": self.system_name,
            "external_id": event_id,
        }

        if refs_out:
            record["refs_out"] = refs_out

        return record


def get_adapter() -> CalendarAdapter:
    return CalendarAdapter()
