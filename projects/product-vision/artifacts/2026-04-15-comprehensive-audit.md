---
ask: "Comprehensive audit — is the full vision built? What's implemented, what's missing, what regressed?"
created: 2026-04-15
updated: 2026-04-16
workstream: product-vision
session: 2026-04-15-b
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design source of truth — 937 lines, 11 sections"
  - type: artifact
    ref: "INDEX.md"
    description: "160+ locked decisions"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1-consolidated.md"
    description: "Authoritative Phase 0+1 spec — 3,225 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-2-3-consolidated.md"
    description: "Authoritative Phase 2+3 spec — 2,009 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-4-5-consolidated.md"
    description: "Authoritative Phase 4+5 spec — 2,076 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-6-7-consolidated.md"
    description: "Authoritative Phase 6+7 spec — 707 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-gaps.md"
    description: "90 gaps identified, all resolved in consolidated specs"
  - type: artifact
    ref: "2026-04-14-impl-spec-verification-report.md"
    description: "4-pass verification, 29 findings, all resolved"
  - type: artifact
    ref: "2026-04-15-shakeout-session-findings.md"
    description: "19 findings from first boot — 15 fixed, 4 documented"
  - type: codebase
    ref: "https://github.com/indemn-ai/indemn-os"
    description: "Every Python and TypeScript file read, git history examined"
  - type: artifact
    description: "All 65+ design artifacts from sessions 1-6, all 5 context documents"
---

# Comprehensive Audit: Is the Full Vision Built?

**Auditor:** Claude Opus 4.6 (1M context)
**Date:** 2026-04-15
**Method:** Read every spec file, every design artifact, every locked decision, every Python file, every TypeScript file, and the git history to trace which changes came from the build vs. the shakeout fixes.

---

## 1. The Design Pipeline

8 design sessions produced 65+ artifacts and 160+ locked decisions, consolidated into a white paper (937 lines, 11 sections) and four implementation specs (8,017 lines total). 90 gaps were identified across 7 verification passes and resolved in consolidated specs. The specs were verified against the design 4 times with 29 findings, all resolved before building.

The build produced 17,330 lines of code across 181 files (110 kernel Python, 30 test files, 41 UI files) with 176 passing tests. A shakeout session booted the system for the first time, found 19 issues, fixed 15 inline.

**The spec-to-design alignment is clean.** The verification report confirmed it. The question is whether the code matches.

---

## 2. What IS Built

Checked against every section of the white paper and every INDEX.md decision.

### Six Primitives — ALL IMPLEMENTED

| Primitive | Status | Evidence |
|-----------|--------|----------|
| **Entity** | COMPLETE | EntityDefinition in MongoDB, dynamic class creation via factory.py, state machines, computed fields, flexible data, schema migration, auto-generated CLI/API/skills |
| **Message** | COMPLETE | Queue + log split, selective emission, correlation IDs, cascade depth, visibility timeout, dead-letter, claiming via findOneAndUpdate |
| **Actor** | COMPLETE | Human/associate/tier3_developer types, role assignment, execution modes (deterministic/reasoning/hybrid), skills, scheduling, owner_actor_id, strict_deterministic flag |
| **Role** | COMPLETE | Permissions (read/write per entity type, wildcard), watches (entity type + event + conditions + scope), can_grant, mfa_required, inline roles for associates |
| **Organization** | COMPLETE | Multi-tenancy scope, OrgScopedCollection, environments-as-orgs (clone/diff/deploy), settings, slug |
| **Integration** | COMPLETE | Owner type (org/actor), provider + version, credential resolution priority chain, adapter dispatch, webhook endpoint, content_visibility, OAuth token refresh |

### Seven Kernel Entities — ALL IMPLEMENTED

| Entity | Fields | State Machine | Indexes | Special Behavior |
|--------|--------|---------------|---------|-----------------|
| **Organization** | name, slug, status, settings, template_source, default_mfa_required | onboarding→active→suspended | slug | Self-referencing org_id for bootstrap |
| **Actor** | name, email, type, status, role_ids, skills, mode, runtime_id, owner_actor_id, llm_config, trigger_schedule, strict_deterministic, auth_methods, mfa_exempt | provisioned→active→suspended→deprovisioned | email, type+status, role_ids | Associate-specific fields coexist with human fields |
| **Role** | name, permissions, watches, can_grant, mfa_required, is_inline, bound_actor_id | None | org_id+name | WatchDefinition embedded model |
| **Integration** | name, owner_type, owner_id, system_type, provider, provider_version, config, secret_ref, access, status, last_checked_at, last_error, content_visibility | configured→connected→active→error→paused | system_type+status, owner | Credential resolution chain |
| **Attention** | actor_id, target_entity, related_entities, purpose (5 types), runtime_id, workflow_id, session_id, opened_at, last_heartbeat, expires_at, metadata, status | active→expired/closed | actor+purpose, target, runtime, expires | Heartbeat bypass in save_tracked, @exposed heartbeat method |
| **Runtime** | name, kind (4 types), framework, framework_version, transport, llm_config, sandbox_config, deployment_image, deployment_platform, deployment_ref, capacity, status, instances | configured→deploying→active→draining→stopped→error | kind+status | Three-layer config merge pattern |
| **Session** | actor_id, type (4 types), auth_method_used, ip_address, user_agent, status, expires_at, access_token_jti, refresh_token_ref, mfa_verified, mfa_verified_at, claims_stale, platform_admin_context | active→expired/revoked | actor+status, jti, expires | Revocation cache with Change Stream |

### Kernel Mechanisms — ALL IMPLEMENTED

| Mechanism | Status | Notes |
|-----------|--------|-------|
| **save_tracked() transaction** | IMPLEMENTED (with regression — see Finding 1) | Entity write + changes record + watch evaluation + message creation. Version restore on exception. |
| **Selective emission** | COMPLETE | Creation > transition > method > no emission. Priority order correct. |
| **Watch evaluation** | COMPLETE | Cache with 60s TTL + immediate invalidation on Role save. Event matching supports specific methods (`method:classify`) and specific transitions (`transitioned:active`). |
| **Scope resolution** | COMPLETE | field_path traversal with _id suffix shorthand. active_context via Attention lookup. Relationship targets stored on dynamic classes by factory.py. |
| **Rule engine** | COMPLETE | Priority ordering, veto overrides positive, lookup resolution, evaluation context for debugging. |
| **Condition evaluator** | COMPLETE | 15 operators (equals, not_equals, contains, starts_with, ends_with, gt, gte, lt, lte, in, not_in, matches, exists, older_than, within). Logical composition (all, any, not). Nested field access via dot notation. |
| **Changes collection** | COMPLETE | Append-only, hash chain (SHA-256), field-level diffs, correlation_id linking. |
| **Capability system** | COMPLETE | Registry pattern, auto_classify + stale_check implemented, --auto pattern returns needs_reasoning. |
| **Optimistic dispatch + sweep backstop** | COMPLETE | API fires-and-forgets Temporal workflow after save. Queue processor sweeps for undispatched messages every 5 seconds. |

### Authentication — COMPLETE

| Feature | Status |
|---------|--------|
| Password (Argon2id) | IMPLEMENTED |
| Service tokens (hash + verify) | IMPLEMENTED |
| SSO (via Integration adapter) | IMPLEMENTED |
| TOTP MFA with backup codes | IMPLEMENTED |
| Magic links (password reset, email verify) | IMPLEMENTED |
| JWT (HS256, 15min expiry, jti) | IMPLEMENTED |
| Revocation cache (bootstrap + Change Stream) | IMPLEMENTED |
| MFA policy (role-level + actor exempt + org default) | IMPLEMENTED |
| Platform admin cross-org sessions (4h default, 24h max, work-type tagged) | IMPLEMENTED |
| Claims refresh on role change (X-Refreshed-Token header) | IMPLEMENTED |
| Pre-auth rate limiting (sliding window, 5/10min → 30min lockout) | IMPLEMENTED |
| Auth audit events (18 event types) | IMPLEMENTED |
| Tier 3 self-service signup | IMPLEMENTED |
| Password reset via magic link | IMPLEMENTED |
| MFA backup codes (hashed, single-use) | IMPLEMENTED |
| First-org bootstrap (one-time, save_tracked for admin/role) | IMPLEMENTED |

### Base UI — COMPLETE (with one gap)

| Feature | Status |
|---------|--------|
| Auto-generated entity list views | IMPLEMENTED |
| Auto-generated entity detail views with forms | IMPLEMENTED |
| Queue view with correlation-based coalescing | IMPLEMENTED |
| Role overview | IMPLEMENTED |
| Auth events view | IMPLEMENTED |
| Navigation auto-generated from entity metadata | IMPLEMENTED |
| State indicator + transition buttons | IMPLEMENTED |
| Capability action buttons | IMPLEMENTED |
| Field type → renderer mapping | IMPLEMENTED |
| WebSocket real-time via Change Streams | IMPLEMENTED |
| Login with MFA redirect | IMPLEMENTED |
| Status banner for degraded dependencies | IMPLEMENTED |
| Assistant top-bar input + conversation panel | IMPLEMENTED |
| **Assistant tool execution** | **NOT IMPLEMENTED (Finding 2)** |

### Associate Execution — COMPLETE

| Feature | Status |
|---------|--------|
| ProcessMessageWorkflow (claim→process→complete) | IMPLEMENTED |
| HumanReviewWorkflow (Temporal signals) | IMPLEMENTED |
| BulkExecuteWorkflow (batched with progress) | IMPLEMENTED |
| Deterministic skill interpreter | IMPLEMENTED |
| LLM reasoning with execute_command tool | IMPLEMENTED |
| Hybrid (deterministic first, LLM fallback) | IMPLEMENTED |
| Skill loading with tamper detection | IMPLEMENTED |
| Context propagation (correlation_id + depth via headers) | IMPLEMENTED |
| OTEL TracingInterceptor | IMPLEMENTED |
| Per-activity retry policies | IMPLEMENTED |
| Scheduled associate execution (cron → queue) | IMPLEMENTED |
| Direct invocation (queue entry + immediate workflow) | IMPLEMENTED |

### Integration Framework — COMPLETE

| Feature | Status |
|---------|--------|
| Adapter base class + error hierarchy | IMPLEMENTED |
| Adapter registry (provider:version) | IMPLEMENTED |
| Credential resolution (actor→owner→org) | IMPLEMENTED |
| Credential caching (5min TTL) | IMPLEMENTED |
| OAuth token refresh | IMPLEMENTED |
| Webhook endpoint with adapter dispatch | IMPLEMENTED |
| Outlook adapter (fetch + send + refresh) | IMPLEMENTED |
| Stripe adapter (charge + webhook) | IMPLEMENTED |
| Credential rotation | IMPLEMENTED |
| Adapter version upgrade | IMPLEMENTED |
| Integration test endpoint | IMPLEMENTED |

### Bulk Operations — COMPLETE

| Feature | Status |
|---------|--------|
| BulkExecuteWorkflow | IMPLEMENTED |
| 5 CLI verbs (create, transition, method, update, delete) | IMPLEMENTED |
| Selective emission discipline (bulk-update is silent) | IMPLEMENTED |
| Failure handling (skip-and-continue + abort mode) | IMPLEMENTED |
| Dry-run preview | IMPLEMENTED |
| Bulk monitoring (status, list, cancel) | IMPLEMENTED |
| Per-batch MongoDB transactions | IMPLEMENTED |

### Org Lifecycle — COMPLETE

| Feature | Status |
|---------|--------|
| Clone (config only, no entity instances) | IMPLEMENTED |
| Diff (show config differences between orgs) | IMPLEMENTED |
| Export (YAML directory: entities/, roles/, rules/{entity}/, skills/*.md, lookups/, actors/, integrations/, capabilities/) | IMPLEMENTED |
| Import (from YAML directory) | IMPLEMENTED |
| Deploy (source→target with dry-run) | IMPLEMENTED |
| Report compare (parallel run validation) | IMPLEMENTED |

### Infrastructure — COMPLETE

| Feature | Status |
|---------|--------|
| Dockerfile (multi-entry-point) | IMPLEMENTED |
| docker-compose.yml (API + QP + Temporal dev) | IMPLEMENTED |
| CI pipeline (.github/workflows/ci.yml) | IMPLEMENTED |
| Queue processor (7 sweep functions) | IMPLEMENTED |
| Health endpoint (MongoDB + Temporal) | IMPLEMENTED |
| Structured JSON logging | IMPLEMENTED |
| OTEL tracing | IMPLEMENTED |
| Graceful shutdown (SIGTERM/SIGINT) | IMPLEMENTED |
| CLAUDE.md with conventions | IMPLEMENTED |

---

## 3. What's MISSING

> **2026-04-16 update:** A new structural finding (Finding 0) surfaced in conversation with Craig. This finding is more severe than anything else in this list — it's not a missing feature, it's an architectural-layer mismatch. It also exposes a methodological gap in how this audit and the prior verification report were conducted. See "Audit Methodology Gap" section below.

### Finding 0: Agent Execution Lives in the Wrong Architectural Layer (STRUCTURAL)

**What the design artifact (`2026-04-10-realtime-architecture-design.md`) says:**

The design defines harnesses as the universal execution pattern for ALL agent execution — async, real-time chat, real-time voice. Three deployable images:
- `indemn/runtime-async-deepagents` — async work + Temporal worker subscription
- `indemn/runtime-chat-deepagents` — chat + WebSocket server
- `indemn/runtime-voice-deepagents` — voice + LiveKit Agents

Each is ~60 lines of glue code that runs OUTSIDE the kernel. The harness loads an Associate's config, uses the CLI for ALL OS interactions, and bridges between its framework (deepagents/LangChain/custom) and its transport (Temporal/WebSocket/LiveKit). Per the design: "The harness uses the CLI, not a separate Python SDK. This is the key design decision. The CLI is already the universal interface. The harness is 'just another client' of the CLI."

The kernel's role for agent execution is dispatch only — tell the harness "process this message" via Temporal task queue (for async) or accept a connection (for real-time). The kernel does not contain any agent code.

**What the code does:**

Agent execution lives INSIDE the kernel:
- `kernel/temporal/activities.py::process_with_associate` — the full agent loop (load skills, set up Anthropic client, tool-use with `execute_command`, iterate until completion) runs inside the Temporal activity, which runs inside the Temporal worker process, which is part of the kernel image.
- `kernel/api/assistant.py::assistant_message` — a stripped-down agent loop (no tools at all, just text streaming) runs inside the API server process.

There are no harness images. The Phase 5 spec shows a complete voice harness as example code but it was not implemented as a deployable artifact.

**How this happened:**

The Phase 2 implementation spec put `process_with_associate` inside `kernel/temporal/activities.py` as an activity function, including the full LLM loop. This was a deviation from the design artifact, which explicitly says agent execution belongs in harness images outside the kernel. The deviation was not flagged in the spec consolidation, the 90-gap review, or the 4-pass verification. The build implemented the spec faithfully. The shakeout tested runtime correctness, not architectural location.

**Severity:** STRUCTURAL — not a feature gap, not a bug. The agent code runs and works. But it's in the wrong layer.

**Impact:**

1. **Two execution paths instead of one.** The Temporal activity has the full agent loop with tool-use. The assistant endpoint has a degraded version with no tools. This is the root cause of Finding 2 (assistant has no tools): the assistant was written as a separate, simpler thing instead of as a harness instance.

2. **The kernel knows about Anthropic.** Per the design, the kernel should be LLM-agnostic and framework-agnostic. The harness picks the framework. With agent code in the kernel, swapping providers or frameworks requires kernel changes — defeating one of the design's stated benefits.

3. **No real-time channels work yet.** Without external harness images, voice/chat agents can't run. The kernel provides everything harnesses would need (events stream, attention heartbeat, interaction transfer, CLI auth) — but no harnesses use it.

4. **The unified actor model is partially broken.** The design says associates run uniformly across async and real-time via the same harness pattern. Today async runs in-kernel (Temporal activity) and real-time doesn't run at all. They were supposed to share code via the harness pattern.

**Fix:** Build the three harness images per the design. Move `process_with_associate`'s loop OUT of the kernel and INTO `harnesses/async-deepagents/`. Move the assistant's text streaming logic INTO `harnesses/chat-deepagents/`. The kernel keeps only dispatch (Temporal task queue for async, WebSocket connection acceptance for chat). Decision on deployable target deferred to a new session.

**Methodology lesson:** This finding was NOT caught by:
- The 4-pass spec verification (verified specs against the white paper, but the white paper's Runtime/harness section is necessarily a summary; the source artifact has the architectural detail)
- The 90-gap analysis (looked for missing mechanisms, not misplaced ones)
- The shakeout (tested runtime correctness)
- This audit (verified field-by-field, file-by-file — every file matches a spec section)

The finding was caught when Craig asked "why isn't the assistant using the harness pattern?" — a question that came from holding the design intent in his head, not from reading any single document.

---

### Finding 1: Transaction Scope Regression (CRITICAL)

**What the design says:** Entity write, changes record, and message emission are one atomic MongoDB transaction. "If any part fails, none of it commits."

**What the code does:** The shakeout fix (commit 23fcf06) accidentally moved `write_change_record()` and `evaluate_watches_and_emit()` outside the transaction scope. The original build (commit 63751e2) had them inside. The regression happened when adding a try/except for version restore — the indentation shifted.

**Why it matters:** An entity can be written without its audit record or messages. The #1 architectural invariant is broken.

**Fix:** Re-indent two function calls back inside `async with session.start_transaction():`. Keep the try/except wrapper. ~2 lines of indentation change.

### Finding 2: Assistant Has No Tools (CRITICAL)

**What the design says:** "The assistant can execute any operation the user has permission for." The white paper describes it as "at forefront" — the primary human-to-system interface.

**What the code does:** `kernel/api/assistant.py` streams text from Claude with no `tools` parameter. The system prompt says "You can execute any CLI command" but the LLM has no mechanism to do so. The associate execution system (`_execute_reasoning` in activities.py) has the exact tool-use pattern needed — `execute_command` tool that translates CLI commands to API calls — but the assistant endpoint doesn't use it.

**Why it matters:** The assistant is decorative. Users can ask questions but can't say "create a submission for Acme Corp" and have it happen.

**Fix:** Add tool definitions to the assistant's `client.messages.stream()` call. The tools should map to API endpoints the user's roles permit. The pattern already exists in activities.py — adapt it for the assistant context.

### Finding 3: Seed Templates Are Empty

**What the design says:** "The OS ships with a standard library of entity definitions, default skills, and reference roles as seed files. When a new organization is created, it can clone from a template."

**What the code does:** `seed/entities/`, `seed/roles/`, `seed/skills/` directories exist but contain zero files. The loading mechanism (seed.py) works correctly.

**Why it matters:** The "clone from template" pattern has no templates. Phase 6 (dog-fooding) would create content via CLI, so it's not blocking kernel functionality — but a fresh deployment has no starting point.

**Fix:** Create seed YAML for at least one template org. Could be a minimal "starter" template or the CRM entity definitions from Phase 6.

### Finding 4: Rule Group Status Not Enforced

**What the design says:** "Rule groups with lifecycle — draft, active, archived. Draft group → rules not evaluated. Active group → rules evaluate. Archive → rules stop."

**What the code does:** `evaluate_rules()` in engine.py queries `Rule.find({"status": "active"})` but does NOT check whether the rule's group (if any) is also active. A rule in an active state belonging to a draft group evaluates.

**Why it matters:** The organizational layer for testing rules before production is bypassed. Rules in draft groups can accidentally affect production.

**Fix:** Add a group status check in `evaluate_rules()`. Either join through group_id or add a pre-filter that excludes rules whose group_id references a non-active group.

### Finding 5: Hash Chain Verification Broken

**What the design says:** "Verification is a CLI command." The tamper-evident audit trail should be verifiable.

**What the code does:** `indemn audit verify` reports broken chains. The hash computation was improved during shakeout (strftime + ms truncation for MongoDB round-trip consistency), but verification at read time still produces different hashes than at write time. The chain links are correct (each `previous_hash` matches the prior `current_hash`), but recomputation doesn't match.

**Why it matters:** The compliance claim of tamper evidence can't be demonstrated. The chain exists but can't prove integrity.

**Fix:** Debug the serialization difference between write-time and read-time hash computation. Likely a remaining ObjectId or datetime serialization inconsistency in the `_serialize_changes` helper or in how ChangeRecord fields round-trip through MongoDB.

### Finding 6: No Harness Implementation

**What the design says:** "Each harness is a thin piece of glue code — roughly 60 lines — that loads the associate's configuration at session start and uses the CLI for all OS interactions."

**What the code does:** The kernel provides everything harnesses need (events stream API + CLI command, attention heartbeat endpoint, interaction transfer endpoint, CLI authentication via service token). But no actual harness code exists. The Phase 4-5 spec shows a complete voice harness example, but it's spec, not code.

**Why it matters:** Real-time channels (voice, chat) can't run. This is Phase 5 scope and was not part of the build sessions — the kernel endpoints are ready, the harness code needs to be written as a separate deployable image.

**Fix:** Implement the chat harness first (simpler than voice). ~60 lines per the spec. Uses CLI subprocess for all OS operations, `indemn events stream` for scoped event delivery, attention heartbeat loop.

---

## 3a. Audit Methodology Gap (added 2026-04-16)

Finding 0 exposes a methodological problem in how this audit and all prior verification passes were conducted. Documenting it here so the next pass doesn't repeat the same blind spots.

### What every audit pass checked

| Audit | Question it asked | What it caught | What it missed |
|-------|------------------|----------------|----------------|
| Spec consolidation (90 gaps) | Are all mechanisms from the white paper specified? | Missing function definitions, missing CLI commands, missing flow specs | Architectural-layer placement |
| Verification report (4 passes, 29 findings) | Do the consolidated specs match the white paper? Do they have technical errors? Are they buildable? Are they internally consistent? | Code bugs (`$or` collision, `dict()` deprecation), missing helper functions, naming collisions | Whether the spec itself drifted from the source design |
| Shakeout (19 findings) | Does the system boot and process work? | Runtime errors (ObjectId serialization, init_beanie ordering, Beanie inheritance, watch cache, CORS, hash chain) | Whether the right code was in the right place |
| This audit (initial pass) | Does the implementation match the consolidated specs? Are deviations field-level or behavioral? | Transaction scope regression, assistant has no tools, rule group enforcement, hash chain verification | Whether the consolidated specs themselves match the source design artifacts |

Every pass took the prior layer as authoritative. The consolidated specs took the white paper as authoritative. The verification report took the consolidated specs as authoritative. The build took the verified specs as authoritative. The shakeout took the running build as authoritative. This audit took the build + shakeout as authoritative.

**No pass cross-referenced consolidated specs back to the source design artifacts at the architectural-layer level.** That's the gap that let Finding 0 through.

### What a "Pass 2" of this audit would look like

A second pass should:

1. **For each subsystem, identify the source design artifact.** Not the white paper section (which summarizes), and not the consolidated spec (which builds), but the design session artifact where the architectural decisions were made and the trade-offs documented.

2. **Read the source artifact in full.** Not summaries. Not INDEX.md bullets. The full design.

3. **Ask architectural questions, not field questions:**
   - Where does this code live (which process, which image, which boundary)?
   - What's the intended dependency direction?
   - Did the design specify external vs in-kernel?
   - Did the design specify which framework/library, or was that left open?
   - Did the design specify a process/deployment topology?

4. **Compare the answer to where the code actually lives.**

This is a different kind of audit than the field-level one. It's slower per item but catches structural deviations.

### Subsystems that warrant Pass 2 review

In addition to the harness/agent execution pattern (Finding 0), these subsystems have rich source design artifacts that may have similar layer-level deviations:

| Subsystem | Source design artifact(s) | What to check for |
|-----------|--------------------------|-------------------|
| **Harness / agent execution** | `2026-04-10-realtime-architecture-design.md` | DONE — Finding 0. Agent loop in kernel, should be in harness images. |
| **Integration adapter dispatch** | `2026-04-10-integration-as-primitive.md` | Are adapters in the kernel image (correct) or should they be plugin-loadable? Where does adapter code live for new providers? |
| **Channel transport** | `2026-04-10-realtime-architecture-design.md` Part 5 | WebSocket/LiveKit/Twilio bundled with Runtime per design — but with no harnesses, where does this live now? |
| **Sandbox execution** | `2026-03-30-design-layer-3-associate-system.md` (referenced sandboxes via Daytona) | Is sandbox execution implemented? Per design, sandboxes wrap agent execution. With agent execution in-kernel, where would sandboxes go? |
| **Skill execution** | `2026-04-09-entity-capabilities-and-skill-model.md` | Is skill execution where the design specified? The skill interpreter currently lives inside the Temporal activity — if the activity moves to a harness, skill execution moves with it. |
| **Authentication** | `2026-04-11-authentication-design.md` | Cross-checked extensively. Likely OK but verify platform-admin and Tier 3 signup flows match the source. |
| **Bulk operations** | `2026-04-10-bulk-operations-pattern.md` | Already in code as BulkExecuteWorkflow. Verify the Temporal-based design matches and that bulk-update is genuinely silent. |
| **Base UI** | `2026-04-11-base-ui-operational-surface.md` | Verify the assistant pattern (currently broken — Finding 0 explains why). Verify "tables over charts" and "auto-generation only, no per-org dashboards." |
| **Org lifecycle** | `2026-04-09-data-architecture-everything-is-data.md` | Verify clone/diff/deploy semantics match — what's included, what's excluded, version tracking. |
| **Watch coalescing** | `2026-04-10-realtime-architecture-design.md` Part 2 → simplified out per `2026-04-13-simplification-pass.md` | Verify simplification was actually applied (UI-only coalescing, no kernel mechanism). |

### Recommendation

Before continuing with Findings 2-6, conduct Pass 2 of this audit. Read each source artifact above. Identify any other Finding 0-class deviations. Document them. Then we have the complete picture of what needs fixing.

---

## 4. What's NOT Missing (Confirmed Present)

Items that might appear missing on casual inspection but are fully implemented:

- **Org clone/diff/deploy/export/import** — full implementation in org_lifecycle.py + admin_routes.py + org_commands.py
- **Skill approval workflow** — submit-for-review + approve endpoints in skill_routes.py
- **Audit verify CLI command** — implemented (produces wrong results, but the mechanism exists)
- **Report compare for parallel run** — implemented in admin_routes.py + report_commands.py
- **Credential rotation** — implemented in rotation.py + integration_routes.py
- **Pipeline metrics** — state_distribution + queue_depth in aggregations.py + admin_routes.py
- **All Temporal activities registered** — worker.py has all 8 activities
- **Bootstrap uses save_tracked** — admin actor + admin role use save_tracked with `__bootstrap__` actor (only org itself uses insert due to self-reference)
- **Watch cache TTL refresh** — now schedules async reload via create_task (was no-op during shakeout, since fixed)
- **State machine bypass protection** — PUT endpoint rejects state field changes (added in shakeout round 3)
- **Dual base class** — KernelBaseEntity + DomainBaseEntity. Introduced during shakeout to fix Beanie/Motor crashes with dynamic classes. Correct engineering decision. Spec should be updated to reflect this.

---

## 5. The Dual Base Class (Design Evolution, Not Gap)

The original build had one `BaseEntity(Document)` per spec. The shakeout discovered that Beanie's dynamic model features crash on domain entities (`dir()` hits Motor Database → `bool()` raises NotImplementedError, and `is_root=True` caused single-collection inheritance issues).

The fix split into `KernelBaseEntity(Document)` for the 7 kernel entities and `DomainBaseEntity(BaseModel)` for dynamic domain entities, with a shared `_EntityMixin` preserving the same interface. A `_DomainQuery` class replicates Beanie's chainable query API for domain entities.

This is a **correct architectural evolution** — the design assumed Beanie would handle dynamic classes cleanly, and it doesn't. The split preserves the spec's interface contract while solving real runtime problems. The spec should be updated to document this as the intended architecture.

---

## 6. Summary (revised 2026-04-16 after Finding 0 surfaced)

| Category | Count | Items |
|----------|-------|-------|
| **STRUCTURAL deviations** | 1 | Finding 0 — agent execution in wrong layer (entire harness pattern not built; existing agent code is in kernel instead of in external harness images) |
| **CRITICAL fixes needed** | 2 | Finding 1 — transaction scope regression (FIXED 2026-04-16); Finding 2 — assistant tools (will be solved as side effect of Finding 0 resolution) |
| **IMPORTANT fixes needed** | 2 | Rule group enforcement, hash chain verification |
| **Content needed (not code)** | 1 | Seed templates |
| **Design evolution to document** | 1 | Dual base class architecture |
| **Pending** | many? | Pass 2 audit needed before total can be claimed (see "Audit Methodology Gap" section) |

### Revised Priority Order

1. **Pass 2 audit** — Before any more fixes, find any other Finding 0-class structural deviations by re-reading source design artifacts at the architectural-layer level. Documented in section 3a.
2. **Finding 0 (harness pattern)** — Build harness images, move agent execution out of the kernel. This solves Finding 2 (assistant tools) as a side effect. Decision on deployable target deferred to a new session per Craig.
3. ~~Transaction scope~~ — DONE 2026-04-16. Re-indented 2 blocks. 3 atomicity tests added. 179 tests passing.
4. ~~Assistant tools~~ — Subsumed by Finding 0. The assistant becomes a chat-harness instance that runs the user's default associate.
5. **Rule group enforcement** — Add group status check to evaluate_rules(). Small but prevents production-affecting bugs.
6. **Hash chain verification** — Debug serialization mismatch. Compliance requirement.
7. **Seed templates** — Create starter content. Not blocking but needed for "clone from template" pattern.

### Confidence statement

The "~95% implemented" claim from the original audit needs revision. After Finding 0:
- Field-level: ~95% (every spec field is implemented somewhere)
- Architectural-layer: unknown until Pass 2 completes
- Two execution paths (Temporal activity + assistant endpoint) collapse into the harness pattern when Finding 0 is resolved. The amount of code to delete vs. relocate vs. add is significant — likely several hundred lines moving from kernel to harness images, plus net new harness code.
