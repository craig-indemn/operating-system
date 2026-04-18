---
ask: "Systematic wiring audit: for every designed behavior in the Indemn OS vision, trace the code path from trigger to completion. Find every function that exists but isn't called, every designed flow that's disconnected."
created: 2026-04-17
workstream: product-vision
session: 2026-04-17-b
sources:
  - type: codebase
    ref: "/Users/home/Repositories/indemn-os"
    description: "Full codebase audit via 10 parallel agents across all subsystems"
  - type: artifact
    ref: "2026-04-16-vision-map.md"
    description: "Authoritative design reference — 23 sections"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1-consolidated.md"
    description: "Phase 0-1 kernel framework spec"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-2-3-consolidated.md"
    description: "Phase 2-3 associate execution + integrations spec"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-4-5-consolidated.md"
    description: "Phase 4-5 base UI + real-time spec"
---

# Wiring Audit — The Indemn OS

**Date:** 2026-04-17
**Method:** 10 parallel code exploration agents, each tracing designed behaviors through trigger → handler → side effect → completion in the live codebase.
**Scope:** Every designed behavior in the vision map (23 sections), all consolidated specs (Phases 0-5), and all session decisions.

---

## Executive Summary

**Total designed behaviors audited:** 139
**WIRED (working end-to-end):** 99 (71%)
**PARTIAL (infrastructure exists, chain broken):** 27 (19%)
**UNWIRED (dead code or missing):** 13 (10%)

The kernel core is solid — save_tracked atomicity, watch evaluation, queue processing, dispatch, and entity auto-generation all work. The gaps cluster in three areas:
1. **Authentication flows** — most auth functions exist but aren't called at the right trigger points
2. **Observability components** — UI components built but never routed; OTEL spans incomplete
3. **Integration bugs** — 4 distinct bugs in the integration management layer

---

## Table of Contents

1. [UNWIRED — Dead Code & Missing Connections](#1-unwired)
2. [PARTIAL — Chain Broken, Infrastructure Present](#2-partial)
3. [BUGS — Code Exists but Broken](#3-bugs)
4. [WIRED — Confirmed Working](#4-wired)
5. [Implementation Priority Matrix](#5-priority-matrix)
6. [File Reference Index](#6-file-reference)

---

## 1. UNWIRED — Dead Code & Missing Connections {#1-unwired}

These are functions/features that exist in the code but are never called at the right place, or designed flows where the code is completely absent. **These are the highest priority fixes.**

### U-01: Human Actor Onboarding Flow

**Design:** `indemn actor create --type human` → magic_link → password setup → activation (one flow)
**Reality:** Requires 5 separate manual API calls. No magic link generated. Actor stays "provisioned" forever.

- CLI command exists: `indemn_os/src/indemn_os/actor_commands.py:14-84`
- POSTs to `/api/actors` with bare minimum data
- No magic link generation during actor creation
- No password setup flow
- No activation transition

**What to build:** After creating the Actor, if type is `human`: generate magic_link token, print to stdout (same pattern as bootstrap), set initial status to `provisioned`, document the password setup endpoint that validates the magic link and sets the password.

---

### U-02: Magic Link Token — Generated But Never Delivered

**Design:** Magic link tokens sent via email Integration adapter or printed to stdout
**Reality:** `generate_magic_link_token()` called in 3 places, token discarded every time

- Function: `kernel/auth/jwt.py:88-98`
- Call site 1: `kernel/api/auth_routes.py:449` — password reset initiation — token generated then discarded
- Call site 2: `kernel/api/auth_routes.py:697` — Tier3 signup verification — token generated then discarded
- Call site 3: Never called during actor creation (see U-01)

**What to fix:** Return the token in the API response (for MVP, stdout/response is sufficient). Wire to email Integration adapter when one exists.

---

### U-03: Refresh Tokens — Field Exists, Never Populated

**Design:** Opaque refresh tokens, rotated with 30-second overlap window
**Reality:** `Session.refresh_token_ref` field exists but is never set. No refresh endpoint.

- Field: `kernel_entities/session.py:29` — `refresh_token_ref: Optional[str] = None`
- Never populated in `kernel/auth/session_manager.py:16-49`
- No `POST /auth/refresh` endpoint exists
- No token rotation logic

**What to build:** Generate opaque refresh token during `create_session()`, hash and store in Secrets Manager via `refresh_token_ref`, create `POST /auth/refresh` endpoint with 30s overlap rotation.

---

### U-04: MFA Policy Check — Wrong Logic Entirely

**Design:** Resolution: actor `mfa_exempt` → role `mfa_required` → org `default_mfa_required`
**Reality:** Checks if TOTP method *exists on the actor*, ignoring all policy fields

- Wrong function: `kernel/api/auth_routes.py:633-635`
  ```python
  def _actor_has_mfa(actor) -> bool:
      return any(m.get("type") == "totp" for m in actor.authentication_methods)
  ```
- Should check: `actor.mfa_exempt` (bypass) → any role `mfa_required` → org `default_mfa_required`
- All three fields exist on the correct entities but are never read

**What to fix:** Rewrite `_actor_has_mfa()` to implement the designed resolution order. Fields already exist on Actor (mfa_exempt), Role (mfa_required), Organization (default_mfa_required).

---

### U-05: Claims Refresh Trigger — `mark_claims_stale()` Never Called

**Design:** Role change → set `claims_stale=true` on all active sessions → auto-refresh on next request
**Reality:** Auto-refresh mechanism works (`kernel/auth/middleware.py:99-127`), but the trigger never fires

- Function exists: `kernel/auth/middleware.py:130-140` — `mark_claims_stale(actor_id)`
- Never called from `actor_add_role()` at `kernel/api/admin_routes.py:182-210`
- Never called from any role modification path

**What to fix:** Add `await mark_claims_stale(target.id)` after role changes in `actor_add_role()` and any role revocation path.

---

### U-06: Entity Migration — Orphaned Kernel Code

**Design:** `indemn entity migrate` with rename/add/remove/convert, batching, dry-run, aliases, rollback
**Reality:** Full implementation exists but is unreachable from CLI or API

- Implementation: `kernel/entity/migration.py` — `plan_migration()` (lines 27-41), `execute_migration()` (lines 44-124)
- CLI stub: `indemn_os/src/indemn_os/entity_commands.py:92-111` — incomplete, ends with comment
- No API endpoint exists for migration
- Functions never called anywhere

**What to build:** Complete the CLI command, create `POST /api/entitydefinitions/{name}/migrate` endpoint, wire to existing kernel implementation.

---

### U-07: causation_id — Field Exists, Never Set

**Design:** `causation_id = parent message` — enables cascade tree reconstruction
**Reality:** Field defined on Message and MessageLog schemas, never populated

- Field: `kernel/message/schema.py:27,70`
- Never set in `kernel/message/emit.py` during message creation
- `indemn trace cascade` can find messages by correlation_id but can't build parent-child tree

**What to fix:** When message processing triggers a cascade (watch fires → new message), set `causation_id = str(parent_message_id)` on the new message.

---

### U-08: Skill Content Hash — Computed But Never Verified

**Design:** Content hash verified on every skill fetch (tamper detection)
**Reality:** `verify_content_hash()` exists but is never called anywhere

- Hash creation: `kernel/skill/integrity.py:10` — `compute_content_hash()` called on creation
- Verification: `kernel/skill/integrity.py:15` — `verify_content_hash()` — **ZERO call sites in entire codebase**
- Skills returned to agents without integrity check

**What to fix:** Call `verify_content_hash()` in skill retrieval path (`kernel/api/skill_routes.py` when returning skill content). Reject tampered skills.

---

### U-09: LLM Fallback for `needs_reasoning: true`

**Design:** When `--auto` rules return `needs_reasoning`, trigger associate skill for LLM reasoning
**Reality:** API returns `needs_reasoning: true` to caller. No workflow spawned, no message enqueued.

- Rule evaluation works: `kernel/api/registration.py:207-227`
- When `result.get("needs_reasoning")` is True: just `return result` (line 227)
- No Temporal workflow dispatched
- No message created for associate processing

**What to build:** When `needs_reasoning: true`, create a message targeting the appropriate associate role with the entity context and capability request. Let the normal watch → dispatch → harness pipeline handle it.

---

### U-10: Rule Validation Not Called by API

**Design:** Rule creation validates: fields exist, state fields excluded from set-fields, overlap detection
**Reality:** `validate_rule()` function exists but API endpoint doesn't call it

- Validation: `kernel/rule/validation.py:10` — comprehensive validation
- API create: `kernel/api/rule_routes.py:50-82` — does NOT call `validate_rule()`
- Invalid rules can be created through the API

**What to fix:** Add `await validate_rule(rule_data, entity_definition)` call before insert in `create_rule` endpoint.

---

### U-11: Auth CLI Commands — Completely Absent

**Design:** `indemn auth login`, `indemn auth logout`, `indemn auth token`
**Reality:** No auth CLI commands exist despite API endpoints being present

- No auth_commands.py file
- API endpoints exist: `POST /auth/login`, `POST /auth/signup`, etc.
- CLI users must use raw HTTP or the UI

**What to build:** `auth_commands.py` with login (email+password → store token), logout (revoke session), token (show current token info/expiry).

---

### U-12: Entity Skill Not Regenerated on Modify

**Design:** Entity skills auto-update when EntityDefinition changes
**Reality:** `generate_entity_skill()` called on create but NOT on modify

- Called at: `kernel/api/admin_routes.py:40-59` (create endpoint)
- NOT called at: `kernel/api/admin_routes.py:111-147` (modify endpoint)
- Modified entity definitions have stale skills

**What to fix:** Add `generate_entity_skill()` call after save in the modify endpoint.

---

### U-13: Entity Definition Modify Doesn't Re-Register Class

**Design:** Entity definition changes take effect at runtime
**Reality:** `PUT /api/entitydefinitions/{name}/modify` updates DB but doesn't call `register_domain_entity()`

- Modify endpoint: `kernel/api/admin_routes.py:111-147` — saves definition, no re-registration
- New fields/state changes don't take effect until server restart

**What to fix:** Call `register_domain_entity()` after saving the modified definition.

---

## 2. PARTIAL — Chain Broken, Infrastructure Present {#2-partial}

These have most pieces in place but a specific link in the chain is missing or unverified.

### P-01: Login Flow — JWT Works, No Refresh Tokens

- `POST /auth/login` works → returns JWT access token
- Session created, password verified, rate limiting applied
- **Missing:** Refresh token generation and rotation (see U-03)

### P-02: First-Org Bootstrap — Uses JWT, Not Magic Link

- Bootstrap endpoint returns JWT directly (pragmatic for dev)
- Design says magic_link via stdout
- **Acceptable for MVP** — JWT is more useful during development

### P-03: Conversation Persistence — Plumbed, Not Verified E2E

- MongoDBSaver checkpointer initialized in chat harness
- Passed to agent builder with `thread_id=interaction_id`
- Checkpointer can be None if MONGODB_URI not set
- Async harness does NOT have checkpointer
- **Status:** Infrastructure wired, E2E verification needed

### P-04: Events Stream — Mid-Conversation Awareness TODO

- `indemn events stream` CLI command exists
- API endpoint with MongoDB Change Stream exists
- Chat harness starts events stream subprocess, reads lines, sends to WebSocket
- **Explicit TODO in code:** `session.py:212` — "TODO: feed event to running agent for mid-conversation awareness"
- Events reach the WebSocket client but NOT the running agent

### P-05: Interaction Respond — Not Verified E2E

- CLI: `indemn_os/src/indemn_os/interaction_commands.py:31-43`
- API: `kernel/api/interaction.py:117-165`
- Creates Message targeting handling actor
- **Not verified** against live system; no UI or harness consumption evidence

### P-06: Message Queue Dispatch to Harness

- Temporal worker in async harness listens on `runtime-{runtime_id}` queue
- Kernel `ProcessMessageWorkflow` routes to runtime-specific queue
- **Chain verified in prior session** for async harness
- Chat harness uses WebSocket path, not Temporal queue (correct by design)

### P-07: Tables — No Sort/Filter UI

- TanStack Table renders entity data correctly
- Only `getCoreRowModel()` configured
- **Missing:** `getSortedRowModel()`, `getFilteredRowModel()` for interactive sort/filter
- Drill-through and action buttons work

### P-08: Create Entity Form — Missing

- Entity detail view has update form (EntityForm component)
- **No create/new entity form** in routes or views
- Must use CLI or direct API to create entities

### P-09: UI Context Injection — IDs Only

- Assistant receives: `view_type`, `current_path`, `entity_type`, `entity_id`
- **Missing:** Full entity data payload not sent with messages
- Assistant must fetch entity data itself based on IDs

### P-10: Observability UI Components — Dead Code

Three components built but never routed or imported:
- `ui/src/views/CascadeViewer.tsx` — cascade trace viewer, no route
- `ui/src/components/IntegrationHealth.tsx` — integration status, never imported
- `ui/src/components/PipelineMetrics.tsx` — state distribution + queue depth, never imported

### P-11: Bootstrap Entity Navigation Ordering

- Entities auto-loaded from `/api/_meta/entities`
- No explicit pinning/ordering for kernel entities vs domain entities
- Relies on API return order

### P-12: Cross-Session Conversation Persistence

- Assistant conversation thread persists within session
- **Lost on page reload** — no localStorage or backend persistence

### P-13: OTEL Span Coverage — ~40%

Instrumented:
- Entity save (`entity.save_tracked`)
- Watch evaluation (`watch.evaluate`)
- Message creation (`message.create`)

**Not instrumented:**
- Rule evaluation
- Temporal workflow activities
- LLM calls (harness-side, deferred)
- CLI commands
- HTTP requests at middleware level
- MongoDB transactions

### P-14: OrgScopedCollection — Not Mandatory

OrgScopedCollection exists but raw Motor calls bypass it in:
1. Auth rate limiting (INTENTIONAL — pre-auth)
2. Entity migration (manual org_id filter)
3. **Org lifecycle** (`kernel/api/org_lifecycle.py:41,114-124`) — direct inserts
4. **Queue routes** (`kernel/api/queue_routes.py:54`) — `Message.find()` with no org_id filter
5. **Bulk silent update** (`kernel/temporal/activities.py:212+`) — intentional bypass
6. **Lookup update** (`kernel/api/lookup_routes.py:44`) — direct Motor call

### P-15: Append-Only Changes — Application-Level Only

- Code only calls `insert()` on changes collection
- MongoDB user-level `insert-only` permission is an assumption, not verified in codebase

### P-16: Daytona Sandbox Deferred

- LocalShellBackend in harness uses `shell=True` (acknowledged in code)
- Mitigated by: approved skills assumption + container isolation
- Daytona `NotImplementedError` at `harness_common/backend.py:69`
- **Risk amplified by:** skill hash verification being unwired (U-08)

### P-17: OTEL Export — Conditional on Config

- `init_tracing()` creates OTLPSpanExporter only if `otel_exporter_endpoint` is set
- Default is NO-OP
- No verification that exporter is actually working

---

## 3. BUGS — Code Exists but Broken {#3-bugs}

### B-01: Bulk Create — Missing Import

**File:** `kernel/temporal/activities.py:223`
**Bug:** `current_org_id.get()` referenced without import
**Impact:** `indemn bulk create` will crash with NameError
**Fix:** Add `from kernel.context import current_org_id` at top of file

### B-02: Integration Create — owner_id Sentinel

**File:** `indemn_os/src/indemn_os/integration_commands.py:46`
**Bug:** CLI sends `"owner_id": "current_org"` as sentinel value; ObjectId coercion in registration.py fails
**Impact:** Cannot create org-level integrations via CLI
**Fix:** Resolve `"current_org"` to actual org_id before entity creation

### B-03: Integration Health Check — Route Mismatch

**File:** `kernel/api/integration_routes.py:119`
**Bug:** CLI calls `POST /api/_platform/integration/health-check` but route is mounted under `/api/integrations` prefix, making actual path `POST /api/integrations/api/_platform/integration/health-check`
**Impact:** `indemn integration health` returns 404
**Fix:** Move to admin_router (no prefix) or fix the path

### B-04: Integration Health Check — Wrong Argument Type

**File:** `kernel/api/integration_routes.py:145`
**Bug:** Calls `await get_adapter(integ)` but `get_adapter()` expects `system_type: str` as first parameter
**Impact:** Health check fails with TypeError
**Fix:** Change to `get_adapter(integ.system_type, ...)`

### B-05: Integration Health Check — Missing test() Method

**File:** `kernel/api/integration_routes.py:147`
**Bug:** Calls `await adapter.test()` but no adapter defines a `test()` method
**Impact:** Health check fails with AttributeError
**Fix:** Add `test()` to Adapter base class or use `fetch(limit=1)` pattern (which the separate test endpoint already uses)

### B-06: Events Stream — Ignored Format Flag

**File:** `harnesses/chat-deepagents/session.py:198`
**Bug:** Passes `--format json-lines` flag but CLI command doesn't accept this parameter
**Impact:** Flag silently ignored by typer; events still output as NDJSON (benign)
**Fix:** Remove the flag or add it to the CLI command

---

## 4. WIRED — Confirmed Working {#4-wired}

### Entity Framework Core
| Behavior | File | Status |
|----------|------|--------|
| Entity definitions → dynamic classes at startup | `kernel/entity/factory.py`, `kernel/db.py:40-168` | WIRED |
| Auto-generated API routes (CRUD + transition + capabilities) | `kernel/api/registration.py` | WIRED |
| Auto-generated CLI commands per entity type | `indemn_os/src/indemn_os/main.py` | WIRED |
| Dual base class (KernelBaseEntity + DomainBaseEntity) | `kernel/entity/base.py` | WIRED |
| Flexible data validation | `kernel/entity/save.py:60-63` | WIRED |
| Entity registry + org-scoped queries | `kernel/db.py`, `kernel/entity/base.py:70-79` | WIRED |
| Computed field evaluation | `kernel/entity/save.py:57` | WIRED |

### save_tracked() + Watches + Queue
| Behavior | File | Status |
|----------|------|--------|
| save_tracked() ONE transaction (entity + changes + watches + messages) | `kernel/entity/save.py:109-156` | WIRED |
| Selective emission (create + transition + @exposed only) | `kernel/entity/save.py:195-209` | WIRED |
| Optimistic concurrency (version check) | `kernel/entity/save.py:124-132` | WIRED |
| Watch evaluation with 60s TTL cache | `kernel/watch/cache.py` | WIRED |
| Watch cache invalidation on Role save | `kernel/entity/save.py:165-169` | WIRED |
| Scope resolution (field_path + active_context) | `kernel/watch/scope.py` | WIRED |
| JSON condition evaluator (shared by watches + rules) | `kernel/watch/evaluator.py:18-95` | WIRED |
| Message claiming (findOneAndUpdate, atomic) | `kernel/message/mongodb_bus.py:21-44` | WIRED |
| Visibility timeout recovery | `kernel/queue_processor.py:36-50` | WIRED |
| Max attempts → dead_letter | `kernel/message/mongodb_bus.py:103-126` | WIRED |
| Optimistic dispatch (fire-and-forget post-transaction) | `kernel/message/dispatch.py:14-66` | WIRED |
| Sweep backstop (every 5s for missed messages) | `kernel/queue_processor.py:74-146` | WIRED |
| Cascade depth tracking (max 10, circuit breaker) | `kernel/entity/save.py:81-93` | WIRED |
| Bootstrap entity cascade guard (depth 1) | `kernel/entity/save.py:100-107` | WIRED |
| correlation_id = OTEL trace_id (propagated everywhere) | `kernel/context.py`, `kernel/auth/middleware.py:77` | WIRED |

### Temporal Workflows
| Behavior | File | Status |
|----------|------|--------|
| ProcessMessageWorkflow → claim → route to runtime queue | `kernel/temporal/workflows.py:30-102` | WIRED |
| HumanReviewWorkflow → claim → wait for signal/timeout | `kernel/temporal/workflows.py:124-162` | WIRED |
| BulkExecuteWorkflow → batch → transaction | `kernel/temporal/workflows.py:191-253` | WIRED |

### Bulk Operations
| Behavior | File | Status |
|----------|------|--------|
| bulk-create, bulk-transition, bulk-method, bulk-update, bulk-delete | `indemn_os/src/indemn_os/bulk_commands.py` | WIRED |
| bulk status/list/cancel/retry | `indemn_os/src/indemn_os/bulk_monitor.py` | WIRED |
| Per-batch MongoDB transaction | `kernel/temporal/activities.py:187-188` | WIRED |
| Failure mode: skip-and-continue / abort | `kernel/temporal/activities.py:236-242` | WIRED |
| Silent updates (bulk-update bypasses save_tracked) | `kernel/temporal/activities.py:212-221` | WIRED |

### Rule Engine + Lookups
| Behavior | File | Status |
|----------|------|--------|
| JSON conditions → set_fields / force_reasoning actions | `kernel/rule/engine.py:73-103` | WIRED |
| Veto rules (force_reasoning overrides positive matches) | `kernel/rule/engine.py:85-103` | WIRED |
| Rule groups with lifecycle (Draft/Active/Archived) | `kernel/rule/schema.py` | WIRED |
| Group status checked in evaluator (D-07 fix) | `kernel/rule/engine.py:48-59` | WIRED |
| Lookups (separate, CSV-importable, referenced by rules) | `kernel/rule/lookup.py` | WIRED |

### Authentication (working paths)
| Behavior | File | Status |
|----------|------|--------|
| Password login → JWT access token | `kernel/api/auth_routes.py:101-171` | WIRED |
| Session revocation cache + Change Stream invalidation | `kernel/auth/jwt.py:20-170` | WIRED |
| Pre-auth rate limiting (5/10min → 30min lockout) | `kernel/auth/rate_limit.py` | WIRED |
| Platform admin cross-org sessions (time-limited, audited) | `kernel/api/auth_routes.py:365-428` | WIRED |
| Auth middleware (JWT decode, context propagation) | `kernel/auth/middleware.py` | WIRED |

### Org Lifecycle
| Behavior | File | Status |
|----------|------|--------|
| indemn org clone | `kernel/api/org_lifecycle.py:254-260` | WIRED |
| indemn org diff | `kernel/api/org_lifecycle.py:263-285` | WIRED |
| indemn org deploy (--dry-run / --apply) | `kernel/api/org_lifecycle.py:288-320` | WIRED |
| indemn org export (YAML) | `kernel/api/org_lifecycle.py:20-127` | WIRED |
| indemn org import (YAML) | `kernel/api/org_lifecycle.py:130-251` | WIRED |
| indemn platform upgrade (--dry-run / --apply) | `kernel/api/admin_routes.py:590-652` | WIRED |

### Integration Framework
| Behavior | File | Status |
|----------|------|--------|
| Integration entity model (all fields) | `kernel_entities/integration.py` | WIRED |
| Credentials via AWS Secrets Manager (5min TTL cache) | `kernel/integration/credentials.py` | WIRED |
| Adapter base class (fetch/send/charge/validate/parse/auth) | `kernel/integration/adapter.py` | WIRED |
| Adapter registry (provider:version keyed) | `kernel/integration/registry.py` | WIRED |
| Credential resolution chain (actor → owner → org → fail) | `kernel/integration/resolver.py` | WIRED |
| Adapter dispatch with auto token refresh | `kernel/integration/dispatch.py` | WIRED |
| Retry logic (auth, rate limit, timeout) | `kernel/integration/dispatch.py` | WIRED |
| Webhook endpoint: POST /webhook/{provider}/{id} | `kernel/api/webhook.py` | WIRED |
| Stripe adapter (charge + webhook) | `kernel/integration/adapters/stripe_adapter.py` | WIRED |
| Outlook adapter (fetch + send + OAuth refresh) | `kernel/integration/adapters/outlook.py` | WIRED |

### Harness Pattern
| Behavior | File | Status |
|----------|------|--------|
| Service token auth → register-instance | `harnesses/_base/harness_common/runtime.py:15-19` | WIRED |
| CLI subprocess for ALL OS operations | `harnesses/_base/harness_common/cli.py:18-43` | WIRED |
| Skill loading via CLI | `harnesses/async-deepagents/main.py:78-81` | WIRED |
| Three-layer LLM config merge | `harnesses/chat-deepagents/session.py:29-35` | WIRED |
| WebSocket → Interaction → Attention → agent → response | `harnesses/chat-deepagents/main.py:88-121` | WIRED |
| Interaction transfer endpoint | `kernel/api/interaction.py:20-90` | WIRED |
| Attention.purpose=observing (first-class) | `kernel_entities/attention.py:24-30` | WIRED |

### Base UI
| Behavior | File | Status |
|----------|------|--------|
| Auto-generated from entity definitions | `ui/src/views/EntityListView.tsx`, `EntityDetailView.tsx` | WIRED |
| Entity list/detail/queue/role views + routes | `ui/src/App.tsx:34-41` | WIRED |
| State machine: current state + transition buttons | `ui/src/components/StateIndicator.tsx` | WIRED |
| Assistant input: slim, top-bar, / and Cmd-K focus | `ui/src/assistant/AssistantInput.tsx` | WIRED |
| Assistant panel: ~450px right-side slide-in | `ui/src/assistant/AssistantPanel.tsx` | WIRED |
| Assistant IS chat-harness WebSocket instance | `ui/src/assistant/AssistantProvider.tsx` | WIRED |
| Login flow (form → API → JWT → localStorage) | `ui/src/auth/LoginPage.tsx`, `ui/src/api/client.ts` | WIRED |
| MFA challenge + backup codes | `ui/src/auth/MfaChallenge.tsx` | WIRED |
| MongoDB Change Streams via WebSocket | `ui/src/api/websocket.ts` | WIRED |
| WebSocket keepalive 30s ping | `ui/src/api/websocket.ts:42-47` | WIRED |
| Live subscriptions on list/detail/queue views | `ui/src/hooks/useRealtime.ts` | WIRED |
| Role-scoped navigation + permissions | `ui/src/layout/Navigation.tsx`, `ui/src/hooks/usePermissions.ts` | WIRED |

### Observability + Trace
| Behavior | File | Status |
|----------|------|--------|
| indemn trace entity (unified timeline) | `kernel/api/trace_routes.py:19` | WIRED |
| indemn trace cascade (execution tree) | `kernel/api/trace_routes.py:98` | WIRED |
| indemn audit verify (hash chain) | `kernel/api/admin_routes.py:337+` | WIRED |
| Hash chain on changes (SHA-256) | `kernel/changes/hash_chain.py` | WIRED |
| Context propagation (X-Correlation-ID, X-Cascade-Depth) | `kernel/auth/middleware.py:77,80` | WIRED |
| contextvars for org_id + actor_id | `kernel/context.py`, `kernel/auth/middleware.py:73-74` | WIRED |
| PlatformCollection with audit logging | `kernel/scoping/platform.py` | WIRED |

### Skill System
| Behavior | File | Status |
|----------|------|--------|
| Skills as markdown in MongoDB (content-hashed) | `kernel/skill/schema.py` | WIRED |
| Entity skills auto-generated on EntityDefinition create | `kernel/api/admin_routes.py:40-59` | WIRED |
| Associate skills CRUD | `kernel/api/skill_routes.py` | WIRED |
| Skill CLI (list/get/create/update) | `kernel/cli/skill_commands.py` | WIRED |
| Skill version tracking + approval workflow | `kernel/api/skill_routes.py` | WIRED |

---

## 5. Implementation Priority Matrix {#5-priority-matrix}

### P0 — Blocks Phase 6 (CRM Dog-Fooding)

| ID | Issue | Effort | What to Do |
|----|-------|--------|------------|
| U-01 | Human actor onboarding flow | 3-4h | Generate magic_link on `actor create --type human`, print token, add password setup endpoint |
| U-04 | MFA policy check wrong logic | 1h | Rewrite `_actor_has_mfa()` to check policy fields (actor.mfa_exempt → role.mfa_required → org.default_mfa_required) |
| U-05 | Claims refresh never triggered | 30m | Add `mark_claims_stale(actor_id)` call in `actor_add_role()` and role revocation |
| B-01 | Bulk create missing import | 5m | Add `from kernel.context import current_org_id` to activities.py |
| B-02 | Integration owner_id sentinel | 30m | Resolve `"current_org"` to actual org_id in integration create |
| U-11 | Auth CLI absent | 2h | Create `auth_commands.py` with login/logout/token |

### P1 — Completes Core Wiring

| ID | Issue | Effort | What to Do |
|----|-------|--------|------------|
| U-03 | Refresh tokens missing | 4-6h | Generate opaque refresh tokens, store hashed in Secrets Manager, create refresh endpoint |
| U-06 | Entity migration orphaned | 2h | Complete CLI, create API endpoint, wire to existing kernel code |
| U-07 | causation_id never set | 1h | Set `causation_id = parent_message_id` during cascade message creation |
| U-08 | Skill hash never verified | 30m | Add `verify_content_hash()` call in skill retrieval path |
| U-10 | Rule validation not called by API | 30m | Add `validate_rule()` call in `create_rule` endpoint |
| U-12 | Entity skill not regenerated on modify | 30m | Add `generate_entity_skill()` in modify endpoint |
| U-13 | Entity def modify doesn't re-register | 30m | Add `register_domain_entity()` in modify endpoint |
| B-03 | Integration health route mismatch | 15m | Fix route mounting path |
| B-04 | Integration health wrong arg type | 5m | Fix `get_adapter()` call |
| B-05 | Integration health missing test() | 30m | Add test() method or use fetch(limit=1) |

### P2 — UI Completeness

| ID | Issue | Effort | What to Do |
|----|-------|--------|------------|
| P-07 | Table sort/filter | 1h | Add getSortedRowModel + getFilteredRowModel to TanStack Table |
| P-08 | Create entity form | 2h | Add create route + form that POSTs to auto-generated endpoint |
| P-09 | Full entity context injection | 1h | Include current entity data in assistant message payload |
| P-10 | Observability components not routed | 2h | Add routes for CascadeViewer, integrate IntegrationHealth + PipelineMetrics into views |
| P-12 | Cross-session conversation | 1h | localStorage persistence for assistant thread |

### P3 — Hardening

| ID | Issue | Effort | What to Do |
|----|-------|--------|------------|
| U-02 | Magic link delivery | 2h | Return tokens in API responses, wire to email adapter later |
| U-09 | LLM fallback for needs_reasoning | 3h | Create message → dispatch → harness pipeline for reasoning fallback |
| P-04 | Events stream → agent awareness | 2h | Feed events into running agent's context (remove TODO) |
| P-13 | OTEL span coverage | 3h | Add spans to rule evaluation, Temporal activities, HTTP middleware |
| P-14 | OrgScopedCollection enforcement | 2h | Refactor org_lifecycle.py, queue_routes.py to use scoped wrappers |

### Dead Code to Remove

| File | What | Why |
|------|------|-----|
| `kernel/integration/rotation.py` | Credential rotation module | Never imported; rotation handled by adapter refresh_token directly |

---

## 6. File Reference Index {#6-file-reference}

### Kernel Core
- `kernel/entity/save.py` — save_tracked(), selective emission, cascade guard
- `kernel/entity/factory.py` — create_entity_class() dynamic Pydantic model creation
- `kernel/entity/base.py` — KernelBaseEntity, DomainBaseEntity, find_scoped()
- `kernel/entity/migration.py` — ORPHANED: plan_migration(), execute_migration()
- `kernel/entity/definition.py` — EntityDefinition schema
- `kernel/entity/exposed.py` — @exposed decorator
- `kernel/db.py` — init_database(), register_domain_entity(), ENTITY_REGISTRY
- `kernel/context.py` — ContextVars (org_id, actor_id, correlation_id, depth)

### Watches + Messages + Queue
- `kernel/watch/cache.py` — Watch cache with TTL and invalidation
- `kernel/watch/evaluator.py` — JSON condition evaluator
- `kernel/watch/scope.py` — Scope resolution (field_path, active_context)
- `kernel/message/emit.py` — evaluate_watches_and_emit()
- `kernel/message/schema.py` — Message, MessageLog (causation_id field unused)
- `kernel/message/mongodb_bus.py` — MongoDBMessageBus (claim, complete, fail)
- `kernel/message/dispatch.py` — optimistic_dispatch()
- `kernel/queue_processor.py` — Sweep backstop

### Rules + Lookups + Capabilities
- `kernel/rule/engine.py` — evaluate_rules() with group status and veto
- `kernel/rule/schema.py` — Rule, RuleGroup
- `kernel/rule/validation.py` — validate_rule() (NEVER CALLED by API)
- `kernel/rule/lookup.py` — Lookup, resolve_lookup_references()
- `kernel/capability/auto_classify.py` — auto_classify capability
- `kernel/capability/registry.py` — Capability registry

### Auth
- `kernel/auth/jwt.py` — JWT creation, revocation cache, magic_link (DEAD CODE)
- `kernel/auth/session_manager.py` — create_session() (no refresh token)
- `kernel/auth/middleware.py` — Auth middleware, mark_claims_stale() (NEVER CALLED)
- `kernel/auth/rate_limit.py` — Pre-auth rate limiting
- `kernel/api/auth_routes.py` — Login, MFA, signup, platform admin, _actor_has_mfa (WRONG)

### Skills
- `kernel/skill/schema.py` — Skill document
- `kernel/skill/generator.py` — generate_entity_skill()
- `kernel/skill/integrity.py` — content hash (verify NEVER CALLED)
- `kernel/api/skill_routes.py` — Skill CRUD routes

### Integration
- `kernel/integration/adapter.py` — Base adapter (no test() method)
- `kernel/integration/registry.py` — Adapter registry
- `kernel/integration/credentials.py` — AWS Secrets Manager fetch/store
- `kernel/integration/resolver.py` — Credential resolution chain
- `kernel/integration/dispatch.py` — get_adapter() + execute_with_retry()
- `kernel/integration/rotation.py` — DEAD CODE
- `kernel/integration/adapters/stripe_adapter.py` — Stripe (charge + webhook)
- `kernel/integration/adapters/outlook.py` — Outlook (email + OAuth)
- `kernel/api/webhook.py` — Webhook handler
- `kernel/api/integration_routes.py` — Integration management (BUGS: B-03, B-04, B-05)

### Temporal
- `kernel/temporal/workflows.py` — ProcessMessage, HumanReview, BulkExecute
- `kernel/temporal/activities.py` — Activities (B-01: missing import)

### Org Lifecycle
- `kernel/api/org_lifecycle.py` — Export, import, clone, diff, deploy

### API Routes
- `kernel/api/registration.py` — Auto-generated CRUD + transition + capability + bulk routes
- `kernel/api/admin_routes.py` — EntityDefinition, platform, audit, actor management
- `kernel/api/trace_routes.py` — Trace entity + cascade
- `kernel/api/events.py` — Events stream endpoint
- `kernel/api/interaction.py` — Transfer, respond, observe
- `kernel/api/queue_routes.py` — Queue stats, complete, fail
- `kernel/api/bulk.py` — Bulk monitoring
- `kernel/api/bootstrap.py` — First-org bootstrap
- `kernel/api/app.py` — FastAPI application factory

### CLI Commands
- `indemn_os/src/indemn_os/main.py` — CLI app with dynamic entity commands
- `indemn_os/src/indemn_os/actor_commands.py` — Actor create (incomplete flow)
- `indemn_os/src/indemn_os/entity_commands.py` — Entity definition management (migrate stub)
- `indemn_os/src/indemn_os/bulk_commands.py` — All 5 bulk verbs
- `indemn_os/src/indemn_os/bulk_monitor.py` — Bulk monitoring
- `indemn_os/src/indemn_os/integration_commands.py` — Integration management (B-02)
- `indemn_os/src/indemn_os/runtime_commands.py` — Runtime management
- `indemn_os/src/indemn_os/interaction_commands.py` — Interaction management
- `indemn_os/src/indemn_os/org_commands.py` — Org lifecycle
- `indemn_os/src/indemn_os/platform_commands.py` — Platform management
- `indemn_os/src/indemn_os/trace_commands.py` — Trace commands
- `indemn_os/src/indemn_os/events_commands.py` — Events stream
- `indemn_os/src/indemn_os/audit_commands.py` — Audit verify
- (MISSING: auth_commands.py)

### Harnesses
- `harnesses/_base/harness_common/cli.py` — CLI subprocess wrapper
- `harnesses/_base/harness_common/runtime.py` — Runtime registration
- `harnesses/_base/harness_common/interaction.py` — Interaction helpers
- `harnesses/async-deepagents/main.py` — Async harness entry point
- `harnesses/chat-deepagents/main.py` — Chat harness WebSocket server
- `harnesses/chat-deepagents/session.py` — Chat session lifecycle (P-04 TODO)
- `harnesses/chat-deepagents/agent.py` — Agent builder

### UI
- `ui/src/App.tsx` — Routes
- `ui/src/api/client.ts` — HTTP client with JWT injection
- `ui/src/api/websocket.ts` — WebSocket subscription manager
- `ui/src/assistant/AssistantProvider.tsx` — Chat harness connection
- `ui/src/views/EntityListView.tsx` — Entity list (P-07: no sort/filter)
- `ui/src/views/EntityDetailView.tsx` — Entity detail + form
- `ui/src/views/QueueView.tsx` — Queue view
- `ui/src/views/CascadeViewer.tsx` — DEAD CODE (not routed)
- `ui/src/components/IntegrationHealth.tsx` — DEAD CODE (not imported)
- `ui/src/components/PipelineMetrics.tsx` — DEAD CODE (not imported)
- `ui/src/components/EntityTable.tsx` — TanStack Table (missing sort/filter models)
- `ui/src/components/StateIndicator.tsx` — State + transitions

### Observability
- `kernel/observability/tracing.py` — OTEL setup (conditional)
- `kernel/changes/collection.py` — Change records with hash chain
- `kernel/changes/hash_chain.py` — SHA-256 hash computation

### Kernel Entities
- `kernel_entities/organization.py` — default_mfa_required field
- `kernel_entities/actor.py` — mfa_exempt, owner_actor_id, authentication_methods
- `kernel_entities/role.py` — mfa_required field
- `kernel_entities/session.py` — refresh_token_ref (NEVER POPULATED)
- `kernel_entities/integration.py` — Full model with content_visibility
- `kernel_entities/attention.py` — 5 purposes including observing
- `kernel_entities/runtime.py` — Kind + framework + lifecycle

---

**This document is the source of truth for implementation. Every item has a status, priority, effort estimate, file location, and fix description. Work through P0 first, then P1, then P2, then P3.**
