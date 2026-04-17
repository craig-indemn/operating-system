---
ask: "Complete session handoff — everything the next session needs to understand the OS, its current state, what's deployed, what's wired, what's not, and what to do next."
created: 2026-04-17
workstream: product-vision
session: 2026-04-17-a
sources:
  - type: codebase
    ref: "/Users/home/Repositories/indemn-os"
    description: "All kernel + harness + CLI + UI code"
  - type: infrastructure
    ref: "Railway project a02ca954-1d1d-405c-a162-1123ca221133"
    description: "7 deployed services"
  - type: artifact
    ref: "All 2026-04-17 artifacts"
    description: "Operational audit, chat harness scope, remaining scope, session summary"
---

# Session Handoff — 2026-04-17

## Reading Protocol

**Read these files IN THIS ORDER before doing any work.**

### Mandatory (load first — ~80K tokens)

1. **This file** — you're reading it now. Current state, deployments, credentials, known gaps.
2. **`projects/product-vision/CLAUDE.md`** — project entry point, artifact index, design integrity rules, session bootstrap protocol.
3. **`artifacts/2026-04-16-vision-map.md`** — THE authoritative design synthesis. 23 sections covering all primitives, mechanisms, trust boundary, harness pattern, auth, UI, observability. **This replaces reading 40+ individual design artifacts.**
4. **`projects/product-vision/INDEX.md`** § Decisions — every decision from 2026-04-16 and 2026-04-17 sessions. ~30 entries covering gates, architectural choices, design principles.

### Context (read the notes for what was audited)

5. **`.audit/notes/`** — 104 structured notes from the 4-pass audit. Each covers one design artifact or code file with: Key Claims, Architectural Decisions, Layer/Location, Dependencies, Code Locations, Cross-References, Open Questions. **Read these to understand what was checked and what each file contains** — they're the inheritance mechanism from the full reading.
6. **`.audit/cross-reference-matrix.md`** — aggregated layer/location declarations from all 104 notes.

### On-demand per task

7. **Consolidated specs** (read only the phase you're working on):
   - `artifacts/2026-04-14-impl-spec-phase-0-1-consolidated.md` — kernel framework
   - `artifacts/2026-04-14-impl-spec-phase-2-3-consolidated.md` — associate execution + integrations (UPDATED 2026-04-17 for harness pattern)
   - `artifacts/2026-04-14-impl-spec-phase-4-5-consolidated.md` — base UI + real-time (UPDATED 2026-04-17 for chat harness)
8. **Session artifacts** (read for specific context):
   - `artifacts/2026-04-17-operational-surface-audit.md` — gap report, 15 subsystems verified
   - `artifacts/2026-04-17-chat-harness-scope.md` — 47 design claims for chat harness
   - `artifacts/2026-04-17-remaining-implementation-scope.md` — every remaining gap
   - `artifacts/2026-04-17-session-summary.md` — what was built and deployed
   - `artifacts/2026-04-16-alignment-audit.md` — the 9 discrepancies (all resolved)

---

## Current State of the OS

### GitHub Repository

**`https://github.com/craig-indemn/indemn-os`** (private, owned by craig-indemn)

### Deployed Services (Railway)

Railway project: `a02ca954-1d1d-405c-a162-1123ca221133`
Railway static IP: `162.220.234.15` (in Atlas allow list)

| Service | Status | Public URL | Dockerfile |
|---|---|---|---|
| indemn-api | SUCCESS | https://indemn-api-production.up.railway.app | `Dockerfile` |
| indemn-queue-processor | SUCCESS | (internal) | `Dockerfile` (SERVICE_TYPE=queue_processor) |
| indemn-temporal-worker | SUCCESS | (internal) | `Dockerfile` (SERVICE_TYPE=temporal_worker) |
| indemn-runtime-async | SUCCESS | (Temporal queue) | `harnesses/async-deepagents/Dockerfile` |
| indemn-runtime-chat | SUCCESS | https://indemn-runtime-chat-production.up.railway.app | `harnesses/chat-deepagents/Dockerfile` |
| indemn-ui | SUCCESS | https://indemn-ui-production.up.railway.app | `ui/Dockerfile` |

### External Services

| Service | Endpoint | Auth |
|---|---|---|
| MongoDB Atlas | `dev-indemn.mifra5.mongodb.net` (public, NOT `-pl-0`) | URI in AWS Secrets Manager |
| Temporal Cloud | `indemn-dev.hxc6t.tmprl.cloud:7233` | API key in AWS Secrets Manager |
| Grafana Cloud | `otlp-gateway-prod-us-east-3.grafana.net/otlp` | Basic auth in AWS Secrets Manager |
| GCP Vertex AI | Project `prod-gemini-470505`, Gemini 2.0 Flash | Service account in AWS Secrets Manager |

### AWS Secrets Manager

| Secret | Purpose |
|---|---|
| `indemn/dev/shared/mongodb-uri` | MongoDB Atlas connection (use public endpoint, NOT `-pl-0` private link) |
| `indemn/dev/shared/temporal-cloud` | Temporal namespace + address + API key |
| `indemn/dev/shared/jwt-signing-key` | JWT signing key for dev |
| `indemn/dev/shared/grafana-otlp` | Grafana Cloud OTLP endpoint + auth |
| `indemn/dev/shared/google-cloud-sa` | GCP service account (NOTE: private_key has escaped `\\n` — must replace with real `\n` at runtime) |
| `indemn/dev/shared/google-api-key` | Google AI API key (has HTTP referrer restrictions — use Vertex AI instead) |
| `indemn/dev/shared/anthropic-api-key` | Anthropic API key |
| `indemn/dev/shared/runtime-async-service-token` | Async harness service token |
| `indemn/dev/shared/runtime-chat-service-token` | Chat harness service token |

### Platform Bootstrap Data

| Entity | ID | Notes |
|---|---|---|
| Platform org (`_platform`) | `69e23d586a448759a34d3823` | Bootstrap org |
| Admin actor (craig@indemn.ai) | `69e23d586a448759a34d3824` | Password: `indemn-os-dev-2026` |
| Kyle actor (kyle@indemn.ai) | `69e28fedf508e1ceb69654c7` | Password: `kyle-indemn-2026` |
| Async Runtime | `69e23d846a448759a34d3829` | async_worker, deepagents, status=active |
| Chat Runtime | `69e2777c02fab4de6eea7d9e` | realtime_chat, deepagents, status=active |
| harness_service Role | `69e244027202d4c8f7bbb9c4` | read/write all |
| platform_admin Role | `69e23d586a448759a34d3825` | (created at bootstrap) |
| TestTask EntityDefinition | in DB | Test entity used for E2E verification |
| Interaction EntityDefinition | in DB | Conversation container |
| VerifyTest EntityDefinition | in DB | Created during E2E verification |

### Entity Skills in MongoDB

7 kernel entity skills uploaded: Organization, Actor, Role, Integration, Attention, Runtime, Session. Auto-generated entity skills: TestTask, Interaction, VerifyTest. All created 2026-04-17.

---

## What Works E2E (Verified Against Live System)

| Behavior | Evidence |
|---|---|
| Entity creation → skill auto-generates | VerifyTest entity → skill with fields, lifecycle, commands |
| Entity transition → watch fires → message → harness processes → entity updated | TestTask: `result = "Processed test task"` |
| Entity GET with `?depth=2&include_related=true` | Returns `_related` key |
| Chat harness: WebSocket → Interaction + Attention → agent → response | "Hello! I process test tasks." |
| Trace entity: unified timeline | Changes + messages + message log merged |
| Trace cascade: execution tree | correlation_id → full chain |
| Queue stats | Pending/processing/dead-letter per role |
| Service token auth (opaque `indemn_*` tokens) | Harnesses authenticate successfully |
| User JWT auth | Login returns access_token, used by UI |
| OTEL → Grafana | Traces visible in Grafana Cloud |
| Selective emission | Only creation + transitions + @exposed methods emit |
| Watch cache invalidation on Role save | Immediate reload |
| Hash chain integrity | D-08 fixed (datetime normalization + sort order) |
| State machine enforcement | _state_field_name on all 6 kernel entities |
| Rule group status | D-07 fixed (group status checked in evaluate_rules) |
| Platform upgrade dry-run | Shows entity definitions needing migration |
| Integration health check | Tests adapter connectivity |

---

## CRITICAL: Known Unwired Behaviors

**These are designed in the vision/specs but the code path is NOT connected end-to-end. This is the #1 priority for the next session.**

| # | Designed Behavior | Where it should be wired | Current state |
|---|---|---|---|
| 1 | **Actor creation for humans → magic_link invitation → password setup → activation** | `actor create --type human` should generate magic_link, set password (or prompt), assign role, activate — all in one flow | Requires 5 separate API calls with manual password hashing |
| 2 | **Conversation persistence** | Chat harness checkpointer should save/load conversation history keyed by Interaction ID | Code added, build just succeeded — NOT yet verified E2E |
| 3 | **Interaction respond** | Human handler submits response during handoff → message created for handling actor | API endpoint added — NOT yet verified E2E |
| 4 | **UI login flow** | UI connects to API at correct URL, user logs in, sees entity views | API URL fixed via VITE_API_URL — NOT yet verified (CORS may need testing) |

### Methodology for Finding More

The pattern that keeps appearing: **designed behavior exists as a function in the code, but nothing calls it in the right place.** Examples found this session:
- `generate_entity_skill()` existed but was never called during entity creation
- `_build_context()` with depth existed but was never exposed via API GET
- `create_magic_link_token()` exists but is never called during actor creation
- `indemn events stream` CLI exists but harness events integration is basic

**The next session MUST do a systematic wiring audit**: for every designed behavior in the consolidated specs, trace the code path from trigger to completion. Not "does the function exist" but "is it called when it should be."

---

## Design Integrity Rules (from Craig — non-negotiable)

1. **Vision IS the MVP.** Never simplify, collapse, or defer designed features without explicit approval.
2. **Implement EXACTLY what the design specifies.** Every flag, parameter, and behavior. If the design says `--depth 2 --include-related`, the code has it.
3. **Verify against the live system.** Don't just commit — confirm it works E2E.
4. **When Craig asserts something was designed**, search until you find it in the artifacts. His cross-session memory is authoritative.
5. **Never simplify during implementation.** If a design claim seems unnecessary, ASK before cutting it.
6. **Save everything in project artifacts.** Findings, decisions, gaps — all documented for future sessions.

---

## What the Next Session Should Do

### Priority 1: Systematic Wiring Audit

For every designed behavior in the consolidated specs (Phases 0-5), trace the code path:
1. What triggers this behavior?
2. What function handles it?
3. Is that function actually called from the trigger point?
4. Does the full path work against the live system?

Focus areas most likely to have unwired paths:
- Authentication flows (login, magic_link, MFA, session refresh, revocation)
- Org lifecycle (clone, diff, deploy — do they actually work?)
- Schema migration (does `indemn entity migrate` actually run?)
- Bulk operations (does `indemn bulk create` trigger BulkExecuteWorkflow?)
- Capability `--auto` pattern (do rules evaluate, does LLM fallback work?)
- Events stream (does the harness actually receive and process mid-conversation events?)
- Handoff (does Interaction.handling_actor_id change actually switch harness mode?)

### Priority 2: Fix All Unwired Paths

Wire them exactly as the design specifies. Verify each one E2E against the live system.

### Priority 3: CRM Building

Craig has an updated CRM spec (supersedes `2026-04-10-crm-retrace.md`). Use `/domain-modeling` skill for the 8-step process. Build against the live OS.

---

## CLI Quick Reference

```bash
# Connect
export INDEMN_API_URL=https://indemn-api-production.up.railway.app
export INDEMN_SERVICE_TOKEN=<token>  # or login

# Entity management
indemn entity create --data '{...}'
indemn entity list
indemn {entity_type} list / get / create / update / transition

# Actors + associates
indemn actor create --type human --name "X" --email x@y.com --role admin
indemn actor create --type associate --name "X" --mode hybrid --runtime-id <id> --role <role> --skills '["skill-name"]'
indemn runtime create --name "X" --kind async_worker --framework deepagents

# Debugging
indemn trace entity <EntityType> <id>
indemn trace cascade <correlation_id>
indemn queue stats
indemn integration health
indemn platform health

# Railway
railway logs --service <name>
railway service status --service <name>
railway up --service <name> --detach -m "message"

# Temporal
temporal workflow list --address indemn-dev.hxc6t.tmprl.cloud:7233 --namespace indemn-dev.hxc6t --api-key "$(aws secretsmanager get-secret-value --secret-id indemn/dev/shared/temporal-cloud --query SecretString --output text | python3 -c 'import sys,json;print(json.load(sys.stdin)[\"api_key\"])')"
```

---

## Files Changed This Session (indemn-os commits)

Major commits (chronological):
1. `01a8b5d` — 5 bug fixes (D-04, D-07, D-08, M-2, M-3)
2. `1e2de60` — CLI extraction + harness scaffolding + kernel dispatch rewiring
3. `7d2c304` — Service token endpoint + opaque token auth
4. `9c3a391` — G2.3 kernel deletion (LLM-agnostic kernel)
5. `da5fd1c` — Trace commands + runtime create + interaction/attention CLI
6. `d33789d` — Chat harness (WebSocket + deepagents + session lifecycle)
7. `e81cb8d` — UI assistant panel rewired to chat harness
8. `9c6fbec` — 6 E2E verification fixes (skill auto-gen, depth/related, respond, UI, OTEL, Attention)
9. `cd95798` — P2 operational surface (runtime transition, bulk retry, integration health, platform upgrade)
10. `167fe4e` — Comprehensive CLAUDE.md for indemn-os repo

All pushed to `https://github.com/craig-indemn/indemn-os` (private).

## OS Repo Commits

All on branch `os-roadmap`:
- Spec updates (D.1 Phase 2-3, D.2 Phase 4-5)
- Doc updates (D-01, M-1, D.3, D.4, D.5)
- 4 new artifacts (operational audit, chat harness scope, remaining scope, session summary)
- Project CLAUDE.md + domain-modeling skill
- INDEX.md with all 2026-04-17 decisions
