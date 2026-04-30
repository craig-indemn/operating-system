---
ask: "TD-1 says the Slack adapter is a NEW build, multi-session work. Capture the full design + scaffold so the next session (or fork) can execute against it without re-deriving decisions."
created: 2026-04-30
workstream: customer-system
session: 14
sources:
  - type: roadmap
    ref: "projects/customer-system/roadmap.md § TD-1 — Slack adapter (NEW, to be built)"
  - type: indemn-os-source
    description: "kernel/integration/adapters/google_workspace.py + outlook.py as adapter precedents"
  - type: design-decision
    description: "Session 13 alignment: direct Slack API, all channels via admin, no DMs initially, per-message granularity, polling-then-Events-API"
---

# Slack Adapter — Design + Scaffold (TD-1 Sub-piece)

> **Status:** Design only. Implementation deferred to a focused build session (likely 4-8 hours, fork-worthy). All architectural decisions resolved in Session 13's TD-1 alignment + Session 14 review.
>
> **Pairing candidate:** Drive adapter (Bug #43 in os-learnings.md) — same shape (paginate external API, create entities per item, watermark). Build them in sequence.

## What this delivers

The adapter ingests every Slack message in workspace-relevant channels into the OS as `SlackMessage` entities, plus any attached files as `Document` entities. Once running on the Slack-Fetcher actor's `*/5 * * * *` cron, every Slack message becomes available to the cascade (TD-2's `SlackClassifier` + `TouchpointSynthesizer`). Per-message granularity preserves all threading metadata via `SlackMessage.thread_ts`; threading is metadata, not a primary entity.

## Architectural decisions (resolved Session 13)

| Decision | Resolution | Rationale |
|---|---|---|
| **Library vs. direct API** | Direct Slack Web API (REST). NOT `agent-slack`. | Clean separation; fewer dependencies; matches outlook/google_workspace adapter style. |
| **Workspace scope** | All channels Craig has admin access to. No DMs initially. | Team uses channels for customer-relevant chatter. DMs add per-user OAuth complexity and personal-channel noise. Add later if needed. |
| **Granularity** | One `SlackMessage` per individual message. `thread_ts` captures threading. | Touchpoints are 1:1 with source-events (per TD-1 design). Threading ≠ primary entity. |
| **Trigger model** | Polling every 5 min for now. Events API webhook migration post-TD-2. | Polling is simpler to start; Events API requires public webhook URL + signature verification. |
| **File attachments** | Each file → linked `Document` entity. `Document.source = "slack_file_attachment"` (added Apr 30). | Document entity is source-agnostic; we already have email_attachment + manual_upload precedent. |
| **Backfill** | One-time 90-day historical pull. | Captures recent customer-relevant chatter. Channel API supports `oldest` cursor. |
| **Auth** | OAuth-based via OS `Integration` entity, `system_type: messaging`, `provider: slack`, `owner_type: org`. Credentials in AWS Secrets Manager, referenced via `secret_ref`. | Standard OS integration pattern. |

## SlackMessage entity definition

To be created via `indemn entity create` with these fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `slack_ts` | str | yes | Slack's per-message timestamp (`"1234567890.123456"`). Effectively the message's external_ref. Unique per channel; index `(channel_id, slack_ts)`. |
| `channel_id` | str | yes | Slack channel ID (`C01234`). Index. |
| `channel_name` | str | no | Denormalized for ergonomics; refresh on channel-rename. |
| `thread_ts` | str | no | If non-null, this message is a thread reply. The parent's `slack_ts`. Index. |
| `user_id` | str | yes | Slack user ID of sender. Index. |
| `sender_email` | str | no | Resolved via `users.info` API at fetch time when possible. Optional because Slack sometimes returns just the ID. |
| `sender_contact` | objectid | no | `relationship_target: Contact`. Filled by SlackClassifier (TD-2). Null at fetch time. |
| `sender_employee` | objectid | no | `relationship_target: Employee`. Filled by SlackClassifier. Null at fetch time. |
| `text` | str | yes | The message text. Slack-mrkdwn — preserve as-is. |
| `posted_at` | datetime | yes | Derived from slack_ts (parsed to ISO). For sortability. |
| `files` | list | no | List of `Document` ObjectId references for attached files. |
| `mentions` | list | no | Channel/user mentions extracted from text. Optional optimization. |
| `company` | objectid | no | `relationship_target: Company`. Filled by SlackClassifier. |
| `touchpoint` | objectid | no | `relationship_target: Touchpoint`. Filled by TouchpointSynthesizer. |
| `status` | str | no, default `received` | State: `received → classified → processed → irrelevant → needs_review`. State field. |

State machine:
- `received → classified` (SlackClassifier success)
- `received → irrelevant` (SlackClassifier sees off-topic / bot noise)
- `received → needs_review` (SlackClassifier total failure — terminal cascade halt)
- `classified → processed` (TouchpointSynthesizer creates Touchpoint)

Indexes:
- Compound `(channel_id, slack_ts)` unique — natural key, dedup
- `thread_ts` — for reply lookup
- `user_id` — for sender queries
- `status` — for queue-style "give me unclassified messages"

## Adapter module: `kernel/integration/adapters/slack.py`

Skeleton structure (mirrors google_workspace.py):

```python
"""Slack adapter — direct Web API + Events API (later).

Fetches SlackMessage entities from workspace channels via the Web API.
Currently polling-mode; Events API webhook is post-TD-2.
"""

import asyncio
from typing import Any
from datetime import datetime, timezone

from kernel.integration.adapter_base import IntegrationAdapter, AdapterError, AdapterValidationError
from kernel.integration.errors import _PerUserErrorTracker  # if shared


class SlackAdapter(IntegrationAdapter):
    """Slack workspace adapter. fetch_new pulls SlackMessages incrementally per channel."""

    def __init__(self, config: dict, credentials: dict):
        super().__init__(config, credentials)
        self._token = credentials.get("bot_token")  # xoxb-... from AWS Secrets
        if not self._token:
            raise AdapterValidationError("Slack adapter requires bot_token in credentials")
        # Optional: workspace_id config
        self._workspace_id = config.get("workspace_id")

    async def fetch(
        self,
        since: datetime | None = None,
        until: datetime | None = None,
        channels: list[str] | None = None,
        **unknown_params,
    ) -> dict:
        """Pull SlackMessages from listed channels (or all accessible) within time window."""
        if unknown_params:
            raise AdapterValidationError(
                f"Unsupported params: {list(unknown_params.keys())}. "
                f"Supported: since, until, channels."
            )

        # 1. List channels (conversations.list) if `channels` not specified
        if channels is None:
            channels = await self._list_channels()

        # 2. Per channel: paginate conversations.history with `oldest` and `latest` cursors
        #    Per Slack API: `oldest` is unix epoch ts; latest is upper bound.
        #    Use cursor for pagination; tracker for per-channel error budget.
        tracker = _PerUserErrorTracker(total=len(channels), op="fetch_slack_history")
        fetched = 0
        created = 0
        skipped = 0
        for channel in channels:
            try:
                messages = await self._fetch_channel_history(channel, since, until)
                for msg in messages:
                    fetched += 1
                    if await self._dedup_check(channel, msg["ts"]):
                        skipped += 1
                        continue
                    sm_id = await self._create_slack_message(channel, msg)
                    created += 1
                    # File attachments
                    for f in msg.get("files", []):
                        await self._create_document_from_file(f, sm_id)
                tracker.record_success()
            except Exception as e:
                tracker.record_failure(channel, e)

        tracker.maybe_raise()
        return {
            "fetched": fetched,
            "created": created,
            "skipped_duplicates": skipped,
            "errors": [],  # tracker handles systemic errors via raise
        }

    async def _list_channels(self) -> list[str]:
        """Workspace conversations.list — public_channel + private_channel; exclude DMs."""
        # paginate via cursor; respect rate limits
        ...

    async def _fetch_channel_history(self, channel_id: str, since, until) -> list[dict]:
        """conversations.history(channel=channel_id, oldest=since.ts, latest=until.ts)"""
        ...

    async def _dedup_check(self, channel_id: str, ts: str) -> bool:
        """Look up SlackMessage by (channel_id, slack_ts). Return True if exists."""
        ...

    async def _create_slack_message(self, channel: str, msg: dict) -> ObjectId:
        """Create SlackMessage entity. Return _id for file linking."""
        ...

    async def _create_document_from_file(self, file_obj: dict, slack_message_id: ObjectId) -> ObjectId:
        """Download file (within size limit), create Document with source='slack_file_attachment'."""
        ...
```

## Slack API endpoints used

| Endpoint | Purpose |
|---|---|
| `conversations.list` | Enumerate channels (types: `public_channel,private_channel`; exclude `im,mpim`). Paginate via `cursor`. |
| `conversations.history` | Per-channel message history. Params: `oldest`, `latest`, `cursor`, `limit` (default 100). Returns up to ~1000 with continuations. |
| `users.info` | Resolve `user_id → email` when needed. Cache aggressively. |
| `files.info` / `files.download` | File attachment metadata + content. Slack files require auth header to download. |

## Rate limit handling

Slack tier 3 endpoints (history) cap at ~50 requests/min per workspace. With ~50 channels × paginated history = many requests. Build in:
- Exponential backoff on 429
- Per-channel concurrency limit (1-2 parallel)
- Sleep between channels if needed

## OS Integration entity

Create via `indemn integration create`:
```bash
indemn integration create \
  --name "Slack Workspace" \
  --system-type messaging \
  --provider slack \
  --owner-type org
indemn integration set-credentials <id> --secret-ref indemn/dev/integrations/slack-oauth
```

AWS Secrets Manager secret at `indemn/dev/integrations/slack-oauth` should contain:
```json
{
  "bot_token": "xoxb-...",
  "app_token": "xapp-...",
  "signing_secret": "..."
}
```

## Slack-Fetcher actor

Once the adapter is live + capability activated on SlackMessage:
- Role `slack_fetcher` (read+write SlackMessage, read Integration, write Document)
- Skill `slack-fetcher` (mirror of email-fetcher and meeting-fetcher — minimal CLI shell)
- Actor `Slack Fetcher`, `mode=hybrid`, `trigger_schedule="*/5 * * * *"`, `runtime_id=<async-deepagents-dev>`
- Inherits `gemini-3-flash-preview/global` from runtime default

## Backfill

One-time historical pull post-adapter-live:
```bash
INDEMN_CLI_TIMEOUT=3600 indemn slackmessage fetch-new --data '{
  "since": "2026-01-31T00:00:00",
  "until": "2026-04-30T00:00:00"
}'
```
Or per-channel if all-channel timeout is an issue (mirrors Meeting backfill pattern).

## TD-2 dependencies (informational)

When TD-2 builds the SlackClassifier (SC):
- SC watches `SlackMessage created`
- Classifies channel-context-aware (e.g., `#sales-customer-x` channel implies external customer X by default)
- Resolves participants: `user_id → users.info → email → Contact/Employee entity-resolve`
- Resolves Company from channel name + content
- Transitions `SlackMessage.status: received → classified` (or `irrelevant` / `needs_review`)

TouchpointSynthesizer then watches `SlackMessage transitioned to classified`, creates Touchpoint per message.

## Out of scope for the Slack-Fetcher build (post-TD-2)

- DM ingestion (1:1, group DMs)
- Real-time Events API push
- Slack threads as primary entity (we keep `thread_ts` metadata only)
- Workspace admin tooling (channel browse, message search via UI) — TD-3 territory
- Multi-workspace support — single workspace for Indemn-internal initially

## Tests

For the build session:
- Unit: per-method, mocked Slack API responses
- Integration: hit a test workspace; verify SlackMessage + Document creation; dedup; thread_ts handling; rate limit retry
- E2E: adapter fetch_new produces N SlackMessages from M channels in known time window

## Open questions for the build session

1. **Channel filter:** all-public vs. opt-in list? Default to all-public for now. Configurable via Integration entity if needed.
2. **File size cap:** `files.info` returns size; we should refuse files > 100MB by default (configurable).
3. **Bot messages:** include or exclude messages from `subtype: bot_message`? Default include — bot messages can carry data we care about (Granola bot, integrations posting summaries).
4. **Edited messages:** Slack returns `edited` metadata. Update SlackMessage on edit, or treat as immutable + create new? **Recommendation: immutable. Edits are rare and the audit trail matters.**
5. **Deleted messages:** Slack returns `subtype: tombstone`. Skip on first ingest; soft-delete on re-ingest if we see one for an existing SlackMessage.

---

*This document is the source of truth for the Slack adapter build. Update as decisions are revised.*
