---
name: slack
description: Read channels, search messages, send messages, manage DMs, and perform all Slack operations using the Python Slack SDK. Use when the user needs to interact with Slack.
---

# Slack

Full Slack Web API access via the Python SDK (`slack_sdk`). Supports every Slack operation — messaging, search, DMs, channels, files, reactions, pins, reminders, user management.

## Status Check

```bash
source /Users/home/Repositories/operating-system/.env && PYTHONPATH=/Users/home/Repositories/operating-system/lib /usr/bin/python3 -c "
from slack_client import get_client
r = get_client().auth_test()
print(f'OK — {r[\"user\"]}@{r[\"team\"]}')
"
```

## Prerequisites

- **Python 3** with `slack_sdk` installed (`pip3 install slack_sdk`)
- **Slack token** — one of:
  - `SLACK_TOKEN` (xoxp-) — from an approved Slack app (preferred)
  - `SLACK_XOXC_TOKEN` + `SLACK_XOXD_COOKIE` — from Slack Desktop browser session (quick path)
- Token stored in `/Users/home/Repositories/operating-system/.env`

## Setup

### Install the SDK

```bash
pip3 install slack_sdk
```

### Get a Token

**Option A: Slack App (preferred — requires workspace admin approval)**

1. Go to https://api.slack.com/apps → **Create New App** → **From scratch**
2. Name: `Indemn OS`, Workspace: Indemn
3. Sidebar → **OAuth & Permissions** → scroll to **User Token Scopes**
4. Add all scopes listed in `references/slack-scopes.md`
5. Scroll up → **Install to Workspace** → Authorize
6. Copy the **User OAuth Token** (starts with `xoxp-`)
7. Add to `.env`:
```bash
export SLACK_TOKEN='xoxp-your-token-here'
```

**Option B: Browser Token (no admin needed — extract from Slack Desktop)**

1. Make sure Slack Desktop is running and you're signed in
2. Extract token and cookie from macOS Keychain or Slack's local storage
3. Add to `.env`:
```bash
export SLACK_XOXC_TOKEN='xoxc-...'
export SLACK_XOXD_COOKIE='xoxd-...'
```

Use single quotes — the cookie contains `/` and `+` characters.

Note: Browser tokens can expire. If auth starts failing, re-extract from Slack Desktop.

### Verify

```bash
source /Users/home/Repositories/operating-system/.env && PYTHONPATH=/Users/home/Repositories/operating-system/lib /usr/bin/python3 -c "
from slack_client import get_client
r = get_client().auth_test()
print(f'OK — {r[\"user\"]}@{r[\"team\"]} ({r[\"user_id\"]})')
"
```

## Execution Model

Every Slack operation follows this pattern:

```bash
source /Users/home/Repositories/operating-system/.env && PYTHONPATH=/Users/home/Repositories/operating-system/lib /usr/bin/python3 << 'PYEOF'
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
