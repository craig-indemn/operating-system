---
name: linear
description: Manage Linear issues, search the roadmap, track engineering work using the linearis CLI. Use for project management tasks.
---

# Linear

Issue management and roadmap tracking via `linearis` CLI.

## Prerequisites

- A Linear account with access to the Indemn workspace
- A Personal API Key from Linear (you create this yourself, no admin needed)

## Status Check

```bash
which linearis && echo "INSTALLED" || echo "NOT INSTALLED"
```

```bash
linearis issues list --limit 1 2>/dev/null && echo "AUTHENTICATED" || echo "NOT AUTHENTICATED"
```

## Setup

### Install
```bash
npm install -g linearis
```

### Authenticate
1. Go to Linear > Settings > Account > Security & Access
2. Create Personal API Key (select Read + Write scopes)
3. Set environment variable:
```bash
export LINEAR_API_KEY="lin_api_..."
```
Add to your `.env` file to persist.

**Important**: linearis expects the env var `LINEAR_API_TOKEN`, but our convention is `LINEAR_API_KEY`. Add this bridge to your `.env`:
```bash
export LINEAR_API_TOKEN="${LINEAR_API_KEY}"
```

Rate limit: 1,500 requests/hour.

## Usage

### List issues
```bash
linearis issues list
linearis issues list --limit 10
```

### Search issues
```bash
linearis issues search "evaluation system"
linearis issues search "renewal" --team Engineering --status "In Progress"
```

### View a specific issue
```bash
linearis issues read COP-312
```

### Create an issue
```bash
linearis issues create "Fix evaluation baseline" --team Engineering --priority 1
```

### Update an issue
```bash
linearis issues update COP-312 --status "Done"
linearis issues update COP-312 --priority 2 --assignee USER_ID
```

### Add a comment
```bash
linearis comments create COP-312 --body "Baseline results attached"
```

### List teams
```bash
linearis teams list
```

All commands output JSON by default — pipe to `jq` for filtering.
