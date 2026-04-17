---
ask: "Scope every remaining gap between the design and implementation — trace commands, runtime provisioning, platform upgrade, voice harness, monitoring, and operational surface items. All grounded in specific design claims."
created: 2026-04-17
workstream: product-vision
session: 2026-04-17-a
sources:
  - type: artifact
    ref: "2026-04-16-vision-map.md §§ 4, 10, 12, 14, 15, 20"
    description: "Observability, infrastructure, bulk ops, real-time, harness pattern"
  - type: artifact
    ref: "2026-04-13-remaining-gap-sessions.md § 3 Operations"
    description: "Debugging workflow, monitoring surfaces, platform upgrades"
  - type: artifact
    ref: "2026-04-13-infrastructure-and-deployment.md"
    description: "Production requirements, deployment strategy, monitoring"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-4-5-consolidated.md §§ 5.2, 5.3"
    description: "Runtime deployment, harness pattern, voice example"
  - type: artifact
    ref: "2026-04-10-realtime-architecture-design.md"
    description: "Voice harness, LiveKit Agents, handoff"
---

# Remaining Implementation Scope

Everything between where we are now and "the vision is fully implemented." Organized by implementation priority. Each item grounded in specific design claims.

**Already scoped separately:**
- Chat harness + assistant panel → `2026-04-17-chat-harness-scope.md`
- 9 original audit discrepancies → all resolved

---

## Item 1: Trace Commands — `indemn trace entity` + `indemn trace cascade`

### Design Claims (vision map § 14, remaining-gap-sessions § 3, pressure-test-findings)

- Three data stores linked by correlation_id (= OTEL trace_id):
  - **Changes collection**: field-level mutations (compliance, years retention)
  - **Message log**: completed work items (ops, months-years)
  - **OTEL traces**: execution path (debugging, days-weeks)
- `indemn trace entity {id}` queries all three, returns unified timeline
- `indemn trace cascade {correlation_id}` shows full execution tree from trigger to completion
- Example output: "Entity changed at 14:02:33. processing_status: null → extracted. Message MSG-042 generated. Target role: classifier. Claimed by: Email Classifier at 14:02:35. Completed at 14:02:38."
- For cascades without messages: hints about why (selective emission skipped)

### What to Build

**CLI commands** (`indemn_os/src/indemn_os/trace_commands.py`):

```
indemn trace entity <entity_type> <entity_id> [--limit 50]
```
- Query changes collection: `GET /api/changes?entity_type=X&entity_id=Y`
- Query message log: `GET /api/messages?entity_type=X&entity_id=Y`
- Merge by timestamp, display unified timeline

```
indemn trace cascade <correlation_id>
```
- Query changes collection: `GET /api/changes?correlation_id=X`
- Query message log: `GET /api/messages?correlation_id=X`
- Build tree from causation_id links
- Show depth, timing, actors involved

**API endpoints** (kernel/api/trace_routes.py):
- `GET /api/trace/entity/{entity_type}/{entity_id}` — aggregation across changes + messages
- `GET /api/trace/cascade/{correlation_id}` — tree-structured execution trace

### Effort: ~3 hours

### Verification
- Create TestTask, transition, let harness process → `indemn trace entity TestTask <id>` shows: creation, transition, message dispatch, harness processing, completion
- `indemn trace cascade <correlation_id>` shows the full tree

---

## Item 2: `indemn runtime create` with Service Token

### Design Claims (harness draft G1.2, harness-implementation-plan)

- "Service token issuance = stdout bootstrap on `indemn runtime create`"
- Operator runs command → kernel creates Runtime + Actor + Session → prints token once
- Operator copies token to Railway env var `INDEMN_SERVICE_TOKEN`
- Current state: `POST /api/_platform/service-token` exists but requires 2 separate steps (create Runtime via CRUD, then create token)

### What to Build

**CLI command** (`indemn_os/src/indemn_os/runtime_commands.py` — extend):

```
indemn runtime create --name "Async Dev" --kind async_worker --framework deepagents \
  --framework-version 0.1.0 --deployment-image indemn/runtime-async-deepagents:0.1.0 \
  --deployment-platform railway
```

Output:
```json
{
  "runtime_id": "69e...",
  "service_token": "indemn_...",
  "task_queue": "runtime-69e...",
  "note": "Store service_token securely. It will not be shown again."
}
```

**API endpoint**: `POST /api/_platform/runtime/create-with-token` — creates Runtime + service Actor + token in one transaction.

### Effort: ~1 hour

### Verification
- `indemn runtime create --name test --kind async_worker --framework deepagents` → prints runtime_id + service_token
- Token authenticates successfully when used in harness

---

## Item 3: OTEL → Grafana Verification

### Design Claims (vision map § 14, infrastructure-and-deployment)

- "Grafana Cloud free tier for MVP"
- "OTEL export is fire-and-forget — monitoring goes blind but zero app impact if Grafana down"
- "Every primitive touch is a span"

### What to Do

- Run E2E test (TestTask create → transition → harness processes)
- Check Grafana Cloud Explore → Traces
- Filter by `service.name = indemn-api` and `service.name = indemn-runtime-async`
- Verify spans appear: HTTP requests, Temporal activities, CLI subprocess calls
- If not: debug the `opentelemetry-instrument` setup

### Effort: ~30 minutes

### Verification
- Traces visible in Grafana with correct service names and span hierarchy

---

## Item 4: `indemn runtime transition`

### Design Claims (Phase 5 spec § 5.2)

- Runtime lifecycle: configured → deploying → active → draining → stopped
- "For MVP: deployment is a manual process (operator deploys the container, then updates the Runtime entity status)"

### What to Build

Add `transition` subcommand to `runtime_commands.py`:
```
indemn runtime transition <runtime_id> --to deploying
```

Calls `POST /api/runtimes/{id}/transition` (already exists via auto-generated routes).

### Effort: ~15 minutes

### Verification
- `indemn runtime transition <id> --to deploying` succeeds

---

## Item 5: `indemn bulk retry`

### Design Claims (vision map § 10)

- "Terminal states: completed / completed_with_errors / failed"
- CLI monitoring: `indemn bulk status`, `indemn bulk list`, `indemn bulk cancel`, `indemn bulk retry`

### What to Build

Add `retry` subcommand to `bulk_monitor.py`:
```
indemn bulk retry <workflow_id>
```

Calls Temporal to restart the BulkExecuteWorkflow with the same spec.

### Effort: ~30 minutes

### Verification
- Create a bulk operation that partially fails, retry it, verify it resumes

---

## Item 6: `indemn integration health`

### Design Claims (vision map § 7, remaining-gap-sessions § 3)

- Integration entity has `last_checked_at` and `last_error` fields
- Adapter has a `test` method
- "Integration health" is a monitoring surface in the base UI

### What to Build

Add `health` subcommand to `integration_commands.py`:
```
indemn integration health [--system-type email] [--status error]
```

Calls each integration's adapter test method, updates `last_checked_at`, reports results.

### Effort: ~1 hour

### Verification
- Create a test integration, run health check, verify last_checked_at updated

---

## Item 7: `indemn platform upgrade`

### Design Claims (remaining-gap-sessions § 3, infrastructure-and-deployment)

- `indemn platform upgrade --dry-run` previews configuration migrations
- `indemn platform upgrade` applies migrations
- "Kernel capability upgrades declare configuration schema versions. Entity definitions store which version they use. Upgrades include migration scripts."
- "Zero downtime through rolling deployment of the new kernel code"
- "A dry-run previews what would change. The upgrade applies migrations, auditable and rollbackable."

### What to Build

**CLI command** (`platform_commands.py`):
```
indemn platform upgrade --dry-run
indemn platform upgrade --apply
```

**API endpoint**: `POST /api/_platform/upgrade` with `dry_run` flag.

**Logic**:
1. Compare current kernel capability schema versions vs stored entity definition versions
2. For each entity definition with an older schema version:
   - Compute migration plan (fields to add/rename/remove)
   - In dry-run: report what would change
   - In apply: execute migration per `entity/migration.py`
3. Update entity definition schema versions

### Effort: ~3 hours

### Verification
- Add a new capability field to the kernel, run `--dry-run`, see the migration plan
- Run `--apply`, verify entity definitions updated

---

## Item 8: Voice Harness (Gates 5-6)

### Design Claims (vision map §§ 4, 12, realtime-architecture-design, Phase 5 spec § 5.3)

- Transport: **LiveKit Agents** (LiveKit Agents SDK for voice sessions)
- Image: `indemn/runtime-voice-deepagents:X.Y.Z`
- Same harness pattern as chat — deepagents + CLI + session lifecycle
- Different transport: LiveKit handles audio codec/streaming
- Voice clients for humans: Integration with `system_type=voice_client`, `owner=actor`
- Human takeover: human's voice_client Integration joins the LiveKit room
- Session lifecycle same as chat (Interaction + Attention + heartbeat + events stream)
- Handoff works identically (Interaction.handling_actor_id change)
- Daytona sandbox for voice (cold start ~90ms — acceptable per G1.3 for voice latency budget review)

### What to Build

```
harnesses/voice-deepagents/
  Dockerfile
  pyproject.toml          # deepagents, livekit-agents, temporalio
  main.py                 # LiveKit Agents entry point
  agent.py                # Same agent builder pattern
  session.py              # Session lifecycle (Interaction + Attention)
  events.py               # Events stream consumer
```

~300 lines of harness code (same pattern as chat, different transport).

### Effort: ~4-6 hours (LiveKit Agents integration needs verification against their SDK)

### Verification
- Voice harness starts, registers with Runtime, heartbeats
- Voice call connects via LiveKit → agent responds
- Mid-call event delivery works
- Handoff to human via voice_client Integration

---

## Item 9: Grafana Dashboards

### Design Claims (remaining-gap-sessions § 3, infrastructure-and-deployment)

- Not custom dashboards — leverage Grafana's OTEL auto-dashboards
- Key views:
  - Service latency (p50/p95/p99 per endpoint)
  - Error rate by service
  - Temporal workflow execution (success/fail/duration)
  - Trace search by correlation_id or service.name

### What to Build

- Configure Grafana data source for Tempo (traces) — should auto-discover from OTLP ingress
- Create 2-3 saved queries:
  - All traces for `service.name = indemn-api` (last 1h)
  - All traces for `service.name = indemn-runtime-async` (last 1h)
  - Trace search by correlation_id
- Optional: one dashboard panel with service latency if the data is flowing

### Effort: ~1-2 hours (configuration, not code)

### Verification
- Grafana shows traces with correct span hierarchy
- Can search by correlation_id and find the full cascade

---

## Item 10: Step 4 — Spec Catch-up (D.1 + D.2)

### What to Do

Update Phase 2-3 and Phase 4-5 consolidated specs to match what was built:

**D.1 — Phase 2-3 consolidated spec § 2.4:**
- Replace `process_with_associate` as kernel activity with: kernel dispatches to per-Runtime harness queue
- Remove `import anthropic` from spec code samples
- Document harness owns completion (`indemn queue complete/fail`)

**D.2 — Phase 4-5 consolidated spec:**
- § 4.7: Replace assistant as kernel endpoint with chat-harness instance
- § 5.3: Add async + chat harness specs alongside voice example
- Update service token creation flow

### Effort: ~2 hours

### Verification
- Specs match the actual implementation
- No references to `import anthropic` in spec code samples
- Harness pattern correctly described

---

## Item 11: Small CLI Operational Items

### 11a. `indemn interaction create/respond/transfer`

Interaction entity exists but needs explicit CLI commands for:
```
indemn interaction create --channel-type chat --associate <id>
indemn interaction respond <id> --content "message text"
indemn interaction transfer <id> --to-actor <actor_id>
indemn interaction transfer <id> --to-role <role_name>
```

These are used by the chat/voice harness and the handoff flow. Auto-CRUD exists but these need ergonomic wrappers.

### 11b. `indemn attention open/close`

Attention @exposed methods exist. CLI wrappers for:
```
indemn attention open --actor <id> --entity <type>/<id> --purpose real_time_session
indemn attention close <attention_id>
```

### Effort: ~1 hour total for both

---

## Summary — Full Remaining Implementation

| Priority | Item | Effort | Dependencies |
|---|---|---|---|
| **P1** | Trace commands (entity + cascade) | 3 hrs | None |
| **P1** | Runtime create with token | 1 hr | None |
| **P1** | OTEL → Grafana verification | 30 min | None |
| **P1** | Chat harness + assistant panel | 8-10 hrs | Interaction/Attention CLI, trace commands |
| **P1** | Interaction + Attention CLI wrappers | 1 hr | None |
| **P2** | Runtime transition CLI | 15 min | None |
| **P2** | Spec catch-up (D.1 + D.2) | 2 hrs | Chat harness built |
| **P2** | Bulk retry | 30 min | None |
| **P2** | Integration health | 1 hr | None |
| **P2** | Grafana dashboards | 1-2 hrs | OTEL verified |
| **P3** | Platform upgrade | 3 hrs | None |
| **P3** | Voice harness | 4-6 hrs | Chat harness proven |

**Total estimated: ~25-30 hours remaining to full vision implementation.**

After all items: every designed CLI command exists. Every API endpoint works. Every harness deployed. Observability pipeline connected. The OS runs real workloads with full debugging capability.

Then: Phase 6 (CRM dog-fooding with Craig's updated design).
