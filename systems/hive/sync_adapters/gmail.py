"""Gmail sync adapter — pulls emails from Gmail via gog CLI."""
import json
import subprocess
import sys
from datetime import datetime, timezone

from sync_adapters.base import SyncAdapter


class GmailAdapter(SyncAdapter):
    system_name = "gmail"
    entity_type = "email_thread"

    STATUS_MAP = {
        "UNREAD": "active",
        "INBOX": "active",     # In inbox but read
        "IMPORTANT": "active",
        "STARRED": "active",
        "SENT": "done",
        "TRASH": "archived",
        "SPAM": "archived",
    }

    def fetch_records(self, since: datetime | None = None) -> list[dict]:
        """Fetch recent emails via gog CLI."""
        try:
            # Fetch recent unread + important emails
            result = subprocess.run(
                ["gog", "gmail", "list", "--limit", "30", "--json"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                print(f"  gog gmail error: {result.stderr[:200]}", file=sys.stderr)
                return []
            data = json.loads(result.stdout)
            # gog may return emails under different keys
            emails = data if isinstance(data, list) else data.get("messages", data.get("emails", []))
            return emails
        except FileNotFoundError:
            print("  gog CLI not found", file=sys.stderr)
            return []
        except json.JSONDecodeError:
            print("  gog returned invalid JSON", file=sys.stderr)
            return []
        except subprocess.TimeoutExpired:
            print("  gog gmail timed out", file=sys.stderr)
            return []

    def map_to_hive_record(self, ext: dict) -> dict | None:
        """Transform a Gmail message to a Hive email_thread entity."""
        msg_id = ext.get("id", ext.get("threadId", ""))
        subject = ext.get("subject", ext.get("snippet", "No subject"))
        if not msg_id:
            return None

        # Extract sender
        from_email = ext.get("from", ext.get("sender", ""))
        # Handle "Name <email>" format
        if "<" in from_email:
            from_email = from_email.split("<")[-1].rstrip(">")

        # Determine status from labels
        labels = ext.get("labelIds", ext.get("labels", []))
        if isinstance(labels, list):
            label_set = set(labels)
        else:
            label_set = set()

        if "UNREAD" in label_set:
            status = "active"
        elif "STARRED" in label_set or "IMPORTANT" in label_set:
            status = "active"
        elif "TRASH" in label_set or "SPAM" in label_set:
            status = "archived"
        else:
            status = "done"

        # Resolve sender to person entity
        refs_out = {}
        if from_email:
            person_id = self._resolve_person(from_email)
            if person_id:
                refs_out["people"] = [person_id]

        # Determine domain — default to indemn for work emails
        domains = ["indemn"]

        # Build short record ID
        short_id = msg_id[:30] if len(msg_id) > 30 else msg_id
        record_id = f"email-{short_id}"

        # Get date
        date = ext.get("date", ext.get("internalDate", ""))
        if isinstance(date, (int, float)):
            # internalDate is epoch ms
            date = datetime.fromtimestamp(date / 1000, tz=timezone.utc).isoformat()

        snippet = ext.get("snippet", "")[:200]

        record = {
            "record_id": record_id,
            "type": self.entity_type,
            "name": subject,
            "from_email": from_email,
            "date": date,
            "snippet": snippet,
            "labels": list(label_set) if label_set else [],
            "domains": domains,
            "tags": [],
            "status": status,
            "system": self.system_name,
            "external_id": msg_id,
            "ref": f"https://mail.google.com/mail/u/0/#inbox/{msg_id}",
        }

        if refs_out:
            record["refs_out"] = refs_out

        return record


def get_adapter() -> GmailAdapter:
    return GmailAdapter()
