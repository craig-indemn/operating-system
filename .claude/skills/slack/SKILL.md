---
name: slack
description: Read Slack channels, search messages, post updates using agent-slack CLI. Use when the user needs to interact with Slack.
---

# Slack

Access Indemn's Slack workspace from the terminal using agent-slack.

## Prerequisites

- **Slack Desktop app** installed (for automatic token import — quickest path), OR
- An existing Slack bot/user token (`xoxb-` or `xoxc-`) provided by a workspace admin

No external service accounts or third-party approvals needed — you can self-service if you have the Slack Desktop app.

## Status Check

```bash
npx agent-slack --version 2>/dev/null && echo "INSTALLED" || echo "NOT INSTALLED"
```

```bash
npx agent-slack auth test 2>/dev/null && echo "AUTHENTICATED" || echo "AUTH FAILED"
```

## Setup

### Install
agent-slack runs via npx — no global install needed. Requires Node.js 18+.

### Authenticate

**Option A: Import from Slack Desktop (quickest, recommended)**
1. Make sure Slack Desktop is running and you're signed in
2. Run:
```bash
npx agent-slack auth import-desktop
```
Done. This grabs the token and cookie automatically.

**Option B: Import from Chrome (if no Desktop app)**
```bash
npx agent-slack auth import-chrome
```
Requires a logged-in Slack tab in Google Chrome.

**Option C: Manual token (bot or browser)**
```bash
npx agent-slack auth add --token "xoxb-..." --workspace-url "https://indemn.slack.com"
```

### Verify
```bash
npx agent-slack auth test
```
Should return `"ok": true` with your user and workspace.

## Usage

### Read recent messages from a channel
```bash
npx agent-slack message list #general --limit 20
```

### Read a thread
```bash
npx agent-slack message list #general --thread-ts 1234567890.123456
```

### Search messages
```bash
npx agent-slack search messages "INSURICA renewal"
```

### Send a message
```bash
npx agent-slack message send #dev "Deployment complete"
```

### Send to a thread
```bash
npx agent-slack message send #dev "Follow-up here" --thread-ts 1234567890.123456
```

### List workspace users
```bash
npx agent-slack user list
```

### Get a specific user
```bash
npx agent-slack user get @craig
```

All commands output token-efficient JSON. Pipe to `jq` for filtering.
