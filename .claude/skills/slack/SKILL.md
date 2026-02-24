---
name: slack
description: Read channels, search messages, send messages, manage DMs, and perform all Slack operations using the Python Slack SDK. Use when the user needs to interact with Slack.
---

# Slack

Full Slack Web API access via the Python SDK (`slack_sdk`). Supports every Slack operation — messaging, search, DMs, channels, files, reactions, pins, reminders, user management.

## Status Check

```bash
REPO_ROOT=$(git rev-parse --show-toplevel) && source "$REPO_ROOT/.env" && PYTHONPATH="$REPO_ROOT/lib" /usr/bin/python3 -c "
from slack_client import get_client
r = get_client().auth_test()
print(f'OK — {r[\"user\"]}@{r[\"team\"]}')
"
```

## Prerequisites

- **Node.js** (for `npx agent-slack` — used for automated token extraction)
- **Python 3** with `slack_sdk` installed (`pip3 install slack_sdk`)
- **Slack Desktop** running and signed in to the Indemn workspace
- Token stored in the repo root `.env` file

## Setup

**YOU (Claude Code) run all of this. The user just needs Slack Desktop running.**

### 1. Install the SDK

```bash
pip3 install slack_sdk
```

### 2. Extract Token from Slack Desktop (automated)

This uses `agent-slack` (runs via npx, no install needed) to pull the browser token directly from Slack Desktop's local data:

```bash
npx agent-slack auth import-desktop
```

This extracts the `xoxc` token and `xoxd` cookie from Slack Desktop and stores them in macOS Keychain.

### 3. Write Token to .env

Read the tokens from agent-slack and write them into the project `.env`:

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
CREDS=$(npx agent-slack auth whoami 2>/dev/null)
XOXC=$(echo "$CREDS" | python3 -c "import sys,json; ws=json.load(sys.stdin)['workspaces'][0]; print(ws['token'])")
XOXD=$(echo "$CREDS" | python3 -c "import sys,json; ws=json.load(sys.stdin)['workspaces'][0]; print(ws['cookie_d'])")

# Append to .env if not already present
if ! grep -q "SLACK_XOXC_TOKEN" "$REPO_ROOT/.env" 2>/dev/null; then
  echo "" >> "$REPO_ROOT/.env"
  echo "# Slack (extracted from Slack Desktop via agent-slack)" >> "$REPO_ROOT/.env"
  echo "export SLACK_XOXC_TOKEN='$XOXC'" >> "$REPO_ROOT/.env"
  echo "export SLACK_XOXD_COOKIE='$XOXD'" >> "$REPO_ROOT/.env"
  echo "Slack tokens written to .env"
else
  echo "Slack tokens already in .env"
fi
```

### 4. Verify

```bash
REPO_ROOT=$(git rev-parse --show-toplevel) && source "$REPO_ROOT/.env" && PYTHONPATH="$REPO_ROOT/lib" /usr/bin/python3 -c "
from slack_client import get_client
r = get_client().auth_test()
print(f'OK — {r[\"user\"]}@{r[\"team\"]} ({r[\"user_id\"]})')
"
```

### Token Refresh

Browser tokens can expire. If auth starts failing, re-run steps 2-4 to re-extract from Slack Desktop.

### Alternative: Slack App Token (long-lived, requires admin)

If browser tokens expire too often, create a Slack app for a permanent `xoxp-` token:

1. https://api.slack.com/apps → **Create New App** → **From scratch**
2. Name: `Indemn OS`, Workspace: Indemn
3. **OAuth & Permissions** → **User Token Scopes** → add scopes from `references/slack-scopes.md`
4. **Install to Workspace** → copy the **User OAuth Token** (`xoxp-`)
5. Add to `.env`: `export SLACK_TOKEN='xoxp-...'`

## Execution Model

Every Slack operation follows this pattern:

```bash
REPO_ROOT=$(git rev-parse --show-toplevel) && source "$REPO_ROOT/.env" && PYTHONPATH="$REPO_ROOT/lib" /usr/bin/python3 << 'PYEOF'
from slack_client import get_client

client = get_client()
# ... SDK calls here
PYEOF
```

- `source .env` loads credentials
- `PYTHONPATH=.../lib` makes the `slack_client` helper importable
- `/usr/bin/python3` uses system Python (has slack_sdk)
- Single-quoted heredoc (`'PYEOF'`) prevents shell interpretation
- `get_client()` handles both token types (xoxp- or xoxc-) automatically

## Quick Reference

### Search Messages

```python
results = client.search_messages(query="from:craig after:2026-02-10", count=20)
for m in results["messages"]["matches"]:
    ch = m["channel"]["name"]
    print(f"#{ch}: {m['text'][:80]}")
```

Search operators: `from:<user>`, `in:#channel`, `after:YYYY-MM-DD`, `before:YYYY-MM-DD`, `@<user>`, `has:link`, `has:reaction`, `has:pin`. Combine freely.

### How to Search Slack — Start From the User

When the user asks "what's going on in Slack" or any open-ended Slack question, **do NOT guess at channel names**. Run `auth_test()` to get the username, then:

1. **Their recent messages** — `from:<username> after:YYYY-MM-DD` (last 3-5 days)
2. **Workspace activity** — `after:YYYY-MM-DD` (broad, recent)
3. **Mentions of them** — `@<username> after:YYYY-MM-DD`
4. **Drill into channels/threads** based on what surfaces

Run steps 1-3 in a single script for efficiency.

### Send a Message

```python
client.chat_postMessage(channel="#general", text="Hello")
```

### Reply in a Thread

```python
client.chat_postMessage(channel="#dev", text="Following up", thread_ts="1234567890.123456")
```

### Send a DM

```python
dm = client.conversations_open(users=["U0123456789"])
client.chat_postMessage(channel=dm["channel"]["id"], text="Hey — quick question")
```

### Read Channel History

```python
history = client.conversations_history(channel="C0123456789", limit=20)
for msg in history["messages"]:
    print(f"{msg.get('user', '?')}: {msg['text'][:80]}")
```

### Read a Thread

```python
replies = client.conversations_replies(channel="C0123456789", ts="1234567890.123456")
for r in replies["messages"]:
    print(f"{r.get('user', '?')}: {r['text'][:80]}")
```

### List Channels

```python
result = client.conversations_list(types="public_channel,private_channel", limit=100)
for ch in result["channels"]:
    print(f"#{ch['name']} ({ch['num_members']} members) — {ch.get('purpose', {}).get('value', '')[:60]}")
```

### Find a User

```python
# By email
user = client.users_lookupByEmail(email="cam@indemn.ai")
print(f"{user['user']['real_name']} — {user['user']['id']}")

# By listing
members = client.users_list(limit=200)
for u in members["members"]:
    if not u["deleted"]:
        print(f"{u['real_name']} ({u['id']}) — {u.get('profile', {}).get('title', '')}")
```

### React to a Message

```python
client.reactions_add(channel="C0123456789", timestamp="1234567890.123456", name="thumbsup")
```

## Full API Reference

For comprehensive patterns covering all operations (edit/delete messages, schedule messages, file uploads, channel management, pins, bookmarks, reminders, user status, user groups), see:

- `references/slack-api-operations.md` — all SDK patterns by category
- `references/slack-scopes.md` — OAuth scopes needed for each operation
- Slack SDK docs: https://tools.slack.dev/python-slack-sdk/web/
- Slack API methods: https://docs.slack.dev/reference/methods/
