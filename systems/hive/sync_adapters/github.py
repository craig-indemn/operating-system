"""GitHub sync adapter — pulls open PRs from indemn-ai org via gh CLI."""
import json
import subprocess
import sys
from datetime import datetime, timezone

from sync_adapters.base import SyncAdapter


class GitHubAdapter(SyncAdapter):
    system_name = "github"
    entity_type = "github_pr"

    STATUS_MAP = {
        "open": "active",
        "closed": "archived",
        "merged": "done",
    }

    ORG = "indemn-ai"

    def fetch_records(self, since: datetime | None = None) -> list[dict]:
        """Fetch open PRs from indemn-ai org via gh CLI."""
        try:
            result = subprocess.run(
                [
                    "gh", "search", "prs",
                    "--owner", self.ORG,
                    "--state", "open",
                    "--limit", "50",
                    "--json", "number,title,repository,state,author,labels,createdAt,updatedAt",
                ],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                print(f"  gh error: {result.stderr[:200]}", file=sys.stderr)
                return []
            return json.loads(result.stdout)
        except FileNotFoundError:
            print("  gh CLI not found", file=sys.stderr)
            return []
        except json.JSONDecodeError:
            print("  gh returned invalid JSON", file=sys.stderr)
            return []
        except subprocess.TimeoutExpired:
            print("  gh timed out", file=sys.stderr)
            return []

    def map_to_hive_record(self, ext: dict) -> dict | None:
        """Transform a GitHub PR to a Hive github_pr entity."""
        repo_info = ext.get("repository", {})
        repo_name = repo_info.get("name", "")
        number = ext.get("number", 0)
        title = ext.get("title", "")
        state = ext.get("state", "open").lower()
        author = ext.get("author", {}).get("login", "")

        if not repo_name or not number:
            return None

        record_id = f"PR-{repo_name}-{number}"
        hive_status = self.map_status(state)

        labels = [l.get("name", "") for l in ext.get("labels", []) if l.get("name")]

        record = {
            "record_id": record_id,
            "type": self.entity_type,
            "name": f"[{repo_name}#{number}] {title}",
            "repo": f"{self.ORG}/{repo_name}",
            "number": str(number),
            "author": author,
            "labels": labels,
            "domains": ["indemn"],
            "tags": [],
            "status": hive_status,
            "system": self.system_name,
            "external_id": f"{repo_name}/{number}",
        }

        # Try to resolve author to person entity
        if author:
            person_id = self._resolve_person_by_name(author)
            if person_id:
                record["refs_out"] = {"people": [person_id]}

        return record

    def _resolve_person_by_name(self, name: str) -> str | None:
        """Try to resolve a GitHub username to a Hive person entity."""
        from db import get_collection
        coll = get_collection()
        person = coll.find_one(
            {"type": "person", "name": {"$regex": f"^{name}$", "$options": "i"}},
            {"record_id": 1},
        )
        if person:
            return person["record_id"]
        return None


def get_adapter() -> GitHubAdapter:
    return GitHubAdapter()
