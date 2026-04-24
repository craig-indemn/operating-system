---
ask: "Operational knowledge for running the customer system pipeline — everything a future session needs"
created: 2026-04-23
workstream: customer-system
session: 2026-04-23-roadmap
---

# Customer System Pipeline — Operations Guide

Everything a future session needs to run, monitor, and troubleshoot the email/meeting ingestion pipeline.

## Architecture

```
Gmail → [Gmail Adapter] → Email entity (received)
    → [Email Classifier associate] → classified / needs_review / irrelevant
        → [Touchpoint Synthesizer associate] → Touchpoint + Documents
            → [Intelligence Extractor associate] → Tasks, Decisions, Commitments, Signals
```

Three AI associates, three watches, one async runtime on Railway. All associates use `execute` tool with `indemn` CLI commands. Entity skills read on demand via `execute("indemn skill get <Entity>")`.

## How to Authenticate

The OS CLI needs auth. Two methods:

**Method 1: Environment variables (preferred for scripting)**
```bash
TOKEN=$(curl -s -X POST https://api.os.indemn.ai/auth/login \
  -H "Content-Type: application/json" \
  -d '{"org_slug": "_platform", "email": "craig@indemn.ai", "password": "indemn-os-dev-2026"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

INDEMN_API_URL=https://api.os.indemn.ai INDEMN_SERVICE_TOKEN=$TOKEN \
  uv run indemn <command>
```

**Method 2: Helper script**
```bash
# Create at /tmp/os-cli.sh
cd /Users/home/Repositories/indemn-os
TOKEN=$(curl -s -X POST https://api.os.indemn.ai/auth/login \
  -H "Content-Type: application/json" \
  -d '{"org_slug": "_platform", "email": "craig@indemn.ai", "password": "indemn-os-dev-2026"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
INDEMN_API_URL=https://api.os.indemn.ai INDEMN_SERVICE_TOKEN="$TOKEN" uv run indemn "$@" 2>&1 | grep -v "^warning: "
```

## How to Fetch Emails

```bash
# Single user, last week
indemn email fetch-new --data '{"user_emails": ["kyle@indemn.ai"], "since": "2026-04-21", "limit": 200}'

# Multiple users
indemn email fetch-new --data '{"user_emails": ["kyle@indemn.ai", "craig@indemn.ai", "cam@indemn.ai"], "since": "2026-04-21"}'

# Incremental (no --since, uses last email date automatically)
indemn email fetch-new --data '{"user_emails": ["kyle@indemn.ai"]}'
```

**Team email list:** kyle, craig, cam, dhruv, ganesh, george, peter, jonathan, ian, marlon, rocky (all @indemn.ai). Also dolly, rudra, kai, george.redenbaugh.

**Known issue:** CLI has 60-second timeout. For large fetches, use the API directly:
```bash
curl -s --max-time 300 -X POST "https://api.os.indemn.ai/api/emails/fetch-new" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_emails": ["kyle@indemn.ai"], "since": "2026-04-21", "limit": 200}'
```

**Cross-mailbox dedup:** Uses email Message-ID header, not Gmail internal ID. Same email seen from Kyle and Cam's inbox is stored once.

## How to Fetch Meetings

```bash
indemn meeting fetch-new
# Or with date filter:
indemn meeting fetch-new --data '{"since": "2026-03-24"}'
```

Uses Google Meet API via domain-wide delegation. Pulls from all @indemn.ai users. 30-day transcript retention limit.

## How to Monitor the Pipeline

**Queue status:**
```bash
indemn queue stats
```
Look for `email_classifier`, `touchpoint_synthesizer`, `intelligence_extractor` roles. `pending` = waiting, `processing` = active, `dead_letter` = permanently failed.

**Email status counts (paginate because email bodies are large):**
```bash
for STATUS in received classified needs_review irrelevant processed; do
  TOTAL=0; OFFSET=0
  while true; do
    N=$(indemn email list --status "$STATUS" --limit 20 --offset "$OFFSET" | python3 -c "import sys,json; print(len(json.loads(sys.stdin.read())))" 2>&1)
    if [ "$N" -eq 0 ] 2>/dev/null; then break; fi
    TOTAL=$((TOTAL + N)); OFFSET=$((OFFSET + 20))
    if [ "$OFFSET" -gt 1000 ]; then break; fi
  done
  echo "$STATUS: $TOTAL"
done
```

**Runtime logs:**
```bash
cd /Users/home/Repositories/indemn-os && railway logs --service indemn-runtime-async
```

**What to look for:**
- `Agent completed: N messages, tools=[...]` — success
- `CancelledError` — activity timed out (check concurrency, heartbeat)
- `Wrote N associate skills` — skill loading (should be 1 per agent)
- `Agent called tool [execute]` — agent using CLI correctly
- `Error 400` — validation error (agent sent wrong data)

## Temporal Workflow Management

```bash
# Get API key
TEMPORAL_SECRET=$(aws secretsmanager get-secret-value --secret-id indemn/dev/shared/temporal-cloud --query 'SecretString' --output text)
TEMPORAL_API_KEY=$(echo "$TEMPORAL_SECRET" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('api_key',''))")

# List running workflows
temporal workflow list \
  --address "indemn-dev.hxc6t.tmprl.cloud:7233" \
  --namespace "indemn-dev.hxc6t" \
  --api-key "$TEMPORAL_API_KEY" \
  --tls \
  --query "WorkflowType='ProcessMessageWorkflow' AND ExecutionStatus='Running'" \
  --limit 10

# Terminate all running workflows (use when deploying fixes)
temporal workflow terminate \
  --address "indemn-dev.hxc6t.tmprl.cloud:7233" \
  --namespace "indemn-dev.hxc6t" \
  --api-key "$TEMPORAL_API_KEY" \
  --tls \
  --query "WorkflowType='ProcessMessageWorkflow' AND ExecutionStatus='Running'" \
  --reason "reason here" \
  --yes
```

**IMPORTANT:** When changing workflow timeouts or harness code, you MUST:
1. Deploy the temporal worker (`railway up --service indemn-temporal-worker`)
2. Deploy the async runtime (`railway up --service indemn-runtime-async`)
3. Terminate all running workflows (they bake in old timeouts at dispatch time)
4. Queue processor re-dispatches with new settings

## Concurrency

**Current setting:** 30 concurrent sessions on async runtime.

**How to change:**
```bash
curl -s -X PUT "https://api.os.indemn.ai/api/runtimes/69e23d846a448759a34d3829" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"capacity": {"max_concurrent_sessions": 30}}'
```

Then redeploy runtime. **30 is the tested ceiling for one Railway container.** Above 30, `asyncio.to_thread` in langchain/deepagents stack starves and causes CancelledError. To go higher, need separate runtimes per associate or bigger containers.

## Key IDs

| Thing | ID |
|-------|-----|
| Async runtime | `69e23d846a448759a34d3829` |
| Email Classifier actor | `69ea1bca23eefe641ea13f44` |
| Touchpoint Synthesizer actor | `69ea1bd123eefe641ea13f48` |
| Intelligence Extractor actor | `69ea1bd223eefe641ea13f4c` |
| Platform Admin actor | `69e23d586a448759a34d3824` |
| _platform org | `69e23d586a448759a34d3823` |

## Railway Deployment

```bash
cd /Users/home/Repositories/indemn-os

# Deploy individual services
railway up --service indemn-api
railway up --service indemn-runtime-async
railway up --service indemn-temporal-worker
railway up --service indemn-queue-processor

# Check logs
railway logs --service indemn-runtime-async
railway logs --service indemn-queue-processor
```

**Services:**
| Service | URL | What |
|---------|-----|------|
| indemn-api | https://api.os.indemn.ai | API server + entity definitions |
| indemn-ui | https://os.indemn.ai | Auto-generated UI |
| indemn-runtime-async | (internal) | Runs AI associates |
| indemn-queue-processor | (internal) | Dispatches messages to Temporal |
| indemn-temporal-worker | (internal) | Runs kernel workflows |
| indemn-runtime-chat | wss://indemn-runtime-chat-production.up.railway.app | Chat assistant |

## Known Issues and Fixes Applied

### Skills must use progressive disclosure
Associate's own skill → written to per-activity directory → passed to `create_deep_agent(skills=[...])`. Entity skills → agent reads via `execute("indemn skill get <Entity>")`. NEVER load all skills into system prompt.

### Heartbeat during agent run
Background asyncio task heartbeats every 30s during `ainvoke()`. Without this, Temporal cancels long-running agent activities.

### Thread pool for concurrency
Default asyncio thread pool (5 per CPU) starves at high concurrency. Set to 500 workers in harness main.py.

### Cross-mailbox email dedup
Uses email `Message-ID` header as `external_ref`, not Gmail's internal message ID. Prevents duplicate creation when same email is fetched from multiple mailboxes.

### Non-retryable errors
`CLIError` and `ValidationError` added to Temporal retry policy's non-retryable list. Prevents infinite retry loops on bad data.

### CLI email list timeout
Email bodies (full HTML) make `email list` responses huge. Use `--limit 20` and paginate with `--offset`. Need to add `--fields` option to the CLI (tracked in INDEX.md open questions).

## Associate Skills

Skills live in two places:
1. **OS database** — `indemn skill get email-classifier` (what the agent reads)
2. **Local files** — `projects/customer-system/skills/email-classifier.md` (our source)

To update a skill:
```bash
indemn skill update email-classifier --content-from-file path/to/email-classifier.md
```

Each associate has ONE skill (its own behavioral instructions). It reads entity skills on demand via CLI. The DEFAULT_PROMPT in `harnesses/async-deepagents/agent.py` tells the agent to always use `execute` and always read entity skills before working with entities.

## Vertex AI / LLM Configuration

**Model:** `google_vertexai:gemini-2.5-flash` on project `prod-gemini-470505` (enterprise).

**Limits:** 30,000 RPM system cap, 2M-10M TPM depending on spend tier. Our 30 concurrent agents use ~0.3% of capacity. Not a bottleneck.

**To change model:**
```bash
curl -s -X PUT "https://api.os.indemn.ai/api/runtimes/69e23d846a448759a34d3829" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"llm_config": {"model": "google_vertexai:gemini-2.5-flash"}}'
```
