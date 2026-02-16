# Slack API Operations Reference

Complete Python SDK patterns for every Slack operation. All examples assume `client = get_client()` is already initialized.

Slack SDK docs: https://tools.slack.dev/python-slack-sdk/web/
Slack API methods: https://docs.slack.dev/reference/methods/

---

## Messaging

### Send a message
```python
result = client.chat_postMessage(channel="#general", text="Hello team")
print(f"Sent: ts={result['ts']}")
```

### Send with rich formatting (Block Kit)
```python
client.chat_postMessage(
    channel="#general",
    text="Fallback text",  # shown in notifications
    blocks=[
        {"type": "header", "text": {"type": "plain_text", "text": "Weekly Update"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Pipeline:* 12 deals\n*Revenue:* $45K MRR"}},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "See full report in #analytics"}}
    ]
)
```

### Reply in a thread
```python
client.chat_postMessage(
    channel="C0123456789",
    text="Thread reply here",
    thread_ts="1234567890.123456"
)
```

### Edit a message
```python
client.chat_update(
    channel="C0123456789",
    ts="1234567890.123456",
    text="Updated message text"
)
```

### Delete a message
```python
client.chat_delete(channel="C0123456789", ts="1234567890.123456")
```

### Schedule a message
```python
import time
post_at = int(time.time()) + 3600  # 1 hour from now

result = client.chat_scheduleMessage(
    channel="#general",
    text="This was scheduled",
    post_at=post_at
)
print(f"Scheduled: id={result['scheduled_message_id']}")
```

### List scheduled messages
```python
result = client.chat_scheduledMessages_list(channel="C0123456789")
for msg in result["scheduled_messages"]:
    print(f"ID: {msg['id']} — post_at: {msg['post_at']} — text: {msg['text'][:50]}")
```

### Delete a scheduled message
```python
client.chat_deleteScheduledMessage(
    channel="C0123456789",
    scheduled_message_id="Q1234567890"
)
```

### Send an ephemeral message (only visible to one user)
```python
client.chat_postEphemeral(
    channel="C0123456789",
    user="U0123456789",
    text="Only you can see this"
)
```

---

## Direct Messages

### Open a DM with one person
```python
dm = client.conversations_open(users=["U0123456789"])
channel_id = dm["channel"]["id"]
client.chat_postMessage(channel=channel_id, text="Hey — quick question")
```

### Open a group DM (multi-party)
```python
dm = client.conversations_open(users=["U0123456789", "U9876543210"])
channel_id = dm["channel"]["id"]
client.chat_postMessage(channel=channel_id, text="Hey both — syncing on this")
```

### Find a user ID for DMs
```python
# By email
user = client.users_lookupByEmail(email="cam@indemn.ai")
user_id = user["user"]["id"]

# By searching user list
members = client.users_list(limit=200)
for u in members["members"]:
    if u["real_name"].lower() == "cam":
        user_id = u["id"]
        break
```

### End-to-end: DM someone by name
```python
# Find user
members = client.users_list(limit=200)
target = next(u for u in members["members"] if "cam" in u.get("real_name", "").lower())

# Open DM and send
dm = client.conversations_open(users=[target["id"]])
client.chat_postMessage(channel=dm["channel"]["id"], text="Hey Cam — got a minute?")
```

---

## Search

### Search messages
```python
results = client.search_messages(query="INSURICA renewal", count=20)
for m in results["messages"]["matches"]:
    ch = m["channel"]["name"]
    user = m.get("username", "?")
    ts = m["ts"]
    text = m["text"][:100]
    print(f"#{ch} @{user} ({ts}): {text}")
```

### Search files
```python
results = client.search_files(query="quarterly report", count=10)
for f in results["files"]["matches"]:
    print(f"{f['name']} ({f['filetype']}) — {f.get('url_private', '')}")
```

### Search operators
Combine in the `query` string:
- `from:<username>` — messages from a user
- `in:#channel` — restrict to channel
- `after:YYYY-MM-DD` / `before:YYYY-MM-DD` — date range
- `@<username>` — mentions of a user
- `has:link` — messages with links
- `has:reaction` — messages with reactions
- `has:pin` — pinned messages
- `is:thread` — thread messages only

Example: `"from:craig in:#customer-implementation after:2026-02-01 has:link"`

### Paginate search results
```python
all_matches = []
page = 1
while True:
    results = client.search_messages(query="INSURICA", count=100, page=page)
    matches = results["messages"]["matches"]
    if not matches:
        break
    all_matches.extend(matches)
    page += 1
print(f"Total: {len(all_matches)} messages")
```

---

## Channel History

### Read recent messages
```python
history = client.conversations_history(channel="C0123456789", limit=20)
for msg in history["messages"]:
    user = msg.get("user", "bot")
    text = msg.get("text", "")[:80]
    print(f"{user}: {text}")
```

### Read messages in a date range
```python
import datetime
oldest = datetime.datetime(2026, 2, 1).timestamp()
latest = datetime.datetime(2026, 2, 14).timestamp()

history = client.conversations_history(
    channel="C0123456789",
    oldest=str(oldest),
    latest=str(latest),
    limit=100
)
```

### Read a full thread
```python
replies = client.conversations_replies(
    channel="C0123456789",
    ts="1234567890.123456"  # thread parent ts
)
for r in replies["messages"]:
    print(f"{r.get('user', '?')}: {r['text'][:80]}")
```

### Paginate channel history (cursor-based)
```python
all_messages = []
cursor = None
while True:
    kwargs = {"channel": "C0123456789", "limit": 200}
    if cursor:
        kwargs["cursor"] = cursor
    result = client.conversations_history(**kwargs)
    all_messages.extend(result["messages"])
    cursor = result.get("response_metadata", {}).get("next_cursor")
    if not cursor:
        break
print(f"Total: {len(all_messages)} messages")
```

---

## Channels

### List all channels
```python
channels = []
cursor = None
while True:
    kwargs = {"types": "public_channel,private_channel", "limit": 200}
    if cursor:
        kwargs["cursor"] = cursor
    result = client.conversations_list(**kwargs)
    channels.extend(result["channels"])
    cursor = result.get("response_metadata", {}).get("next_cursor")
    if not cursor:
        break

for ch in channels:
    print(f"#{ch['name']} (id: {ch['id']}, members: {ch.get('num_members', '?')})")
```

### Get channel info
```python
info = client.conversations_info(channel="C0123456789")
ch = info["channel"]
print(f"#{ch['name']} — topic: {ch['topic']['value']}")
print(f"Purpose: {ch['purpose']['value']}")
print(f"Members: {ch['num_members']}")
```

### List channel members
```python
result = client.conversations_members(channel="C0123456789")
for uid in result["members"]:
    user = client.users_info(user=uid)
    print(f"  {user['user']['real_name']} ({uid})")
```

### Create a channel
```python
result = client.conversations_create(name="new-project", is_private=False)
print(f"Created: #{result['channel']['name']} ({result['channel']['id']})")
```

### Set channel topic
```python
client.conversations_setTopic(channel="C0123456789", topic="Q1 2026 Planning")
```

### Set channel purpose
```python
client.conversations_setPurpose(channel="C0123456789", purpose="Discuss Q1 planning")
```

### Invite users to a channel
```python
client.conversations_invite(channel="C0123456789", users="U0123456789,U9876543210")
```

### Remove a user from a channel
```python
client.conversations_kick(channel="C0123456789", user="U0123456789")
```

### Archive a channel
```python
client.conversations_archive(channel="C0123456789")
```

### Join a public channel
```python
client.conversations_join(channel="C0123456789")
```

### Mark a channel as read
```python
client.conversations_mark(channel="C0123456789", ts="1234567890.123456")
```

### Find a channel by name
```python
result = client.conversations_list(types="public_channel,private_channel", limit=200)
target = next((ch for ch in result["channels"] if ch["name"] == "customer-implementation"), None)
if target:
    print(f"Found: {target['id']}")
```

---

## Files

### Upload a file (2-step flow)
```python
import os

file_path = "/path/to/report.pdf"
file_size = os.path.getsize(file_path)

# Step 1: Get upload URL
upload = client.files_getUploadURLExternal(
    filename=os.path.basename(file_path),
    length=file_size
)

# Step 2: Upload the file content
import urllib.request
with open(file_path, "rb") as f:
    req = urllib.request.Request(upload["upload_url"], data=f.read(), method="POST")
    urllib.request.urlopen(req)

# Step 3: Complete and share to channel
client.files_completeUploadExternal(
    files=[{"id": upload["file_id"]}],
    channel_id="C0123456789"
)
```

### List files
```python
result = client.files_list(channel="C0123456789", count=20)
for f in result["files"]:
    print(f"{f['name']} ({f['filetype']}, {f['size']} bytes) — {f['permalink']}")
```

### Get file info
```python
info = client.files_info(file="F0123456789")
f = info["file"]
print(f"{f['name']} — {f['url_private']}")
```

### Delete a file
```python
client.files_delete(file="F0123456789")
```

---

## Reactions

### Add a reaction
```python
client.reactions_add(channel="C0123456789", timestamp="1234567890.123456", name="thumbsup")
```

### Remove a reaction
```python
client.reactions_remove(channel="C0123456789", timestamp="1234567890.123456", name="thumbsup")
```

### Get reactions on a message
```python
result = client.reactions_get(channel="C0123456789", timestamp="1234567890.123456")
msg = result["message"]
for r in msg.get("reactions", []):
    print(f":{r['name']}: ({r['count']}) — by: {', '.join(r['users'])}")
```

---

## Pins

### Pin a message
```python
client.pins_add(channel="C0123456789", timestamp="1234567890.123456")
```

### List pins in a channel
```python
result = client.pins_list(channel="C0123456789")
for item in result["items"]:
    msg = item.get("message", {})
    print(f"Pinned: {msg.get('text', '')[:60]} (ts: {msg.get('ts')})")
```

### Unpin a message
```python
client.pins_remove(channel="C0123456789", timestamp="1234567890.123456")
```

---

## Bookmarks

### Add a bookmark to a channel
```python
client.bookmarks_add(
    channel_id="C0123456789",
    title="Design Doc",
    type="link",
    link="https://example.com/doc"
)
```

### List bookmarks
```python
result = client.bookmarks_list(channel_id="C0123456789")
for b in result["bookmarks"]:
    print(f"{b['title']} — {b.get('link', 'n/a')}")
```

### Edit a bookmark
```python
client.bookmarks_edit(
    bookmark_id="Bk0123456789",
    channel_id="C0123456789",
    title="Updated Title"
)
```

### Remove a bookmark
```python
client.bookmarks_remove(bookmark_id="Bk0123456789", channel_id="C0123456789")
```

---

## Reminders

### Create a reminder
```python
result = client.reminders_add(text="Follow up with INSURICA", time="in 2 hours")
print(f"Reminder: {result['reminder']['id']}")
```

### Create a reminder for a specific time
```python
import time
remind_at = int(time.time()) + 86400  # tomorrow
client.reminders_add(text="Send proposal", time=remind_at)
```

### List reminders
```python
result = client.reminders_list()
for r in result["reminders"]:
    print(f"{r['text']} — complete: {r['complete_ts'] != 0}")
```

### Complete a reminder
```python
client.reminders_complete(reminder="Rm0123456789")
```

### Delete a reminder
```python
client.reminders_delete(reminder="Rm0123456789")
```

---

## Users

### List all workspace users
```python
members = client.users_list(limit=200)
for u in members["members"]:
    if not u["deleted"] and not u["is_bot"]:
        profile = u.get("profile", {})
        print(f"{u['real_name']} ({u['id']}) — {profile.get('title', '')} — {profile.get('email', '')}")
```

### Get user info
```python
user = client.users_info(user="U0123456789")
u = user["user"]
print(f"{u['real_name']} — {u['profile']['email']}")
print(f"Status: {u['profile'].get('status_emoji', '')} {u['profile'].get('status_text', '')}")
```

### Look up user by email
```python
user = client.users_lookupByEmail(email="cam@indemn.ai")
print(f"{user['user']['real_name']} — {user['user']['id']}")
```

### Set your status
```python
client.users_profile_set(profile={
    "status_text": "In a meeting",
    "status_emoji": ":calendar:",
    "status_expiration": 0  # 0 = don't expire, or set Unix timestamp
})
```

### Clear your status
```python
client.users_profile_set(profile={
    "status_text": "",
    "status_emoji": ""
})
```

### Get your profile
```python
result = client.users_profile_get()
profile = result["profile"]
print(f"Name: {profile['real_name']}")
print(f"Status: {profile.get('status_emoji', '')} {profile.get('status_text', '')}")
```

---

## User Groups

### List user groups
```python
result = client.usergroups_list()
for ug in result["usergroups"]:
    print(f"@{ug['handle']} — {ug['name']} (id: {ug['id']})")
```

### List members of a user group
```python
result = client.usergroups_users_list(usergroup="S0123456789")
print(f"Members: {result['users']}")
```

### Create a user group
```python
result = client.usergroups_create(name="Engineering", handle="engineering")
print(f"Created: @{result['usergroup']['handle']} ({result['usergroup']['id']})")
```

### Update user group members
```python
client.usergroups_users_update(usergroup="S0123456789", users="U111,U222,U333")
```

---

## Error Handling

All SDK methods raise `SlackApiError` on failure:

```python
from slack_sdk.errors import SlackApiError

try:
    client.chat_postMessage(channel="#nonexistent", text="test")
except SlackApiError as e:
    print(f"Error: {e.response['error']}")
    # Common errors: channel_not_found, not_in_channel, invalid_auth,
    # missing_scope, ratelimited, message_not_found
```

### Rate limiting
The SDK handles rate limiting automatically with retries. For burst operations, add a small delay:

```python
import time
for channel_id in channel_ids:
    client.chat_postMessage(channel=channel_id, text="Announcement")
    time.sleep(1)  # respect rate limits
```

---

## Common Patterns

### Get channel ID from name
```python
def get_channel_id(client, name):
    name = name.lstrip("#")
    result = client.conversations_list(types="public_channel,private_channel", limit=200)
    for ch in result["channels"]:
        if ch["name"] == name:
            return ch["id"]
    return None
```

### Get user ID from name
```python
def get_user_id(client, name):
    result = client.users_list(limit=200)
    name_lower = name.lower()
    for u in result["members"]:
        if name_lower in u.get("real_name", "").lower() or name_lower == u.get("name", "").lower():
            return u["id"]
    return None
```

### Get message permalink
```python
result = client.chat_getPermalink(channel="C0123456789", message_ts="1234567890.123456")
print(result["permalink"])
```
