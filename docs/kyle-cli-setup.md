# Kyle — Indemn OS CLI Setup

## Install the CLI

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/craig-indemn/indemn-os/main/install-cli.sh)
```

This installs the `indemn` command.

## Log In

```bash
export INDEMN_API_URL=https://api.os.indemn.ai
indemn auth login --org _platform --email kyle@indemn.ai --password indemn-kyle-2026
```

You should see: `Logged in as kyle@indemn.ai @ _platform`

**Add this to your shell profile** so the API URL is always set:
```bash
echo 'export INDEMN_API_URL=https://api.os.indemn.ai' >> ~/.zshrc
```

## What You Can Do

### Deals (read + write)
```bash
# List all deals
indemn deal list

# See a specific deal
indemn deal get <deal_id>

# Update a deal's next step
indemn deal update <deal_id> --data '{"next_step": "Schedule demo for May 5"}'

# Transition a deal stage
indemn deal transition <deal_id> --to proposal
```

### Companies (read + write)
```bash
# List companies
indemn company list

# Update a company
indemn company update <company_id> --data '{"notes": "Met at InsurTechNY"}'
```

### Tasks (read + write)
```bash
# List tasks
indemn task list

# Create a task
indemn task create --data '{"title": "Follow up with Alliance on pricing", "assignee": "Marlon", "priority": "high", "due_date": "2026-04-25"}'

# Complete a task
indemn task transition <task_id> --to completed
```

### Meetings (read only)
```bash
# List recent meetings
indemn meeting list

# See a specific meeting with transcript
indemn meeting get <meeting_id>
```

### Employees (read + write)
```bash
indemn employee list
```

## Using with Claude Code

Add this to your project's `CLAUDE.md` or tell Claude:

```
I have access to the Indemn OS CLI. The API is at https://api.os.indemn.ai.
To authenticate: indemn auth login --org _platform --email kyle@indemn.ai --password indemn-kyle-2026

Available commands: indemn deal list/get/update/transition, indemn company list/get/update,
indemn task list/get/create/update/transition, indemn meeting list/get, indemn employee list/get.

Use this to check deal status, update next steps, create tasks, and review meetings.
```

## The UI

The web UI is at **https://os.indemn.ai** — same login credentials.
