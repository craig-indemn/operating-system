# Complete-Alignment Audit — Session Handoff

**Written:** 2026-04-16 (session 1 of multi-session audit)
**Purpose:** Preserve full state so next session picks up without loss of information or accuracy.

---

## READ-ME-FIRST (next-session Claude)

If you're reading this because the user pasted a resume prompt or pointed you here: **follow this sequence before answering any question**.

1. Read THIS file in full (you're doing that now).
2. Open and read the audit manifest: `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/manifest.yml` — confirms 104 files, 58 checked.
3. Read the Pass 2 audit report: `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-16-pass-2-audit.md` — this is the completed work you're building on.
4. Read the 3 most architecturally-important existing notes (below) to understand the depth of Finding 0 analysis already done:
   - `.audit/notes/projects_product-vision_artifacts_2026-04-10-realtime-architecture-design_md.md`
   - `.audit/notes/Users_home_Repositories_indemn-os_kernel_temporal_activities_py.md`
   - `.audit/notes/projects_product-vision_artifacts_2026-04-14-impl-spec-phase-2-3-consolidated_md.md`
5. Read the full notes index (§ "Complete index of existing notes") below to see what's already captured.
6. Confirm to the user in one sentence what's been done, what remains, and what you're doing first.
7. Wait for user confirmation before starting new reading.

**Do not re-read any of the 58 files already processed. The notes on disk are the source of truth.**

**Do not rewrite the Pass 2 audit. Build on it.**

**Do not invent content. If you're unsure, read the specific notes file first.**

---

## What the user is trying to accomplish

**End objective (user's own words):**
> "Identify every single discrepancy so that we can ensure what is implemented matches the vision. That is the end objective: to have the vision being implemented exactly."

**Path to get there:**
1. Read ALL design artifacts (the vision) + ALL specifications (the blueprint) 
2. Synthesize into a comprehensive vision map, respecting that **later artifacts may override earlier uncertain decisions**
3. Read/audit the implementation against the vision map
4. Produce a discrepancy report listing every misalignment

---

## Current state (end of session 1)

### What's on disk (persists across sessions)

| Path | Purpose |
|---|---|
| `.audit/manifest.yml` | Single source of truth for audit scope — 104 files, 58 checked, 46 remaining |
| `.audit/notes/` | 59 structured note files (one per file read, plus this handoff indirectly) |
| `.audit/cross-reference-matrix.md` | Matrix from Pass 2 (41 files only — needs regeneration after Pass 3 completes) |
| `projects/product-vision/artifacts/2026-04-16-pass-2-audit.md` | Pass 2 audit report (Finding 0 confirmed, 8 subsystems verified clean) |
| `.claude/settings.local.json` | Has the `synthesis-gate.sh` hook configured to block writes to audit reports until manifest is 100% checked |

### Audit infrastructure — the systematic-audit skill

Scripts at `.claude/skills/systematic-audit/`:
- `init.sh <name> <file-list>` — creates manifest (**DO NOT RUN — manifest already exists**)
- `read-next.sh` — picks next unchecked file from manifest
- `validate-notes.sh <file-path>` — validates notes have required sections, marks file checked
- `cross-reference.sh` — aggregates all notes into layer/location matrix (run AFTER all files checked)
- `synthesis-gate.sh` — PreToolUse hook that blocks Write to audit-report files until manifest is 100% checked (already active)

Notes template (required by validator):
```
# Notes: <filename>

**File:** <full path>
**Read:** <timestamp>
**Category:** <category>

## Key Claims
## Architectural Decisions
## Layer/Location Specified
## Dependencies Declared
## Code Locations Specified
## Cross-References
## Open Questions or Ambiguities
```

---

## Pass progression

| Pass | Files | Status | Deliverable |
|---|---|---|---|
| Pass 1 (historical, pre-session) | — | Done | 2026-04-15-comprehensive-audit.md. Surfaced Finding 0 (agent execution in wrong layer). Exposed methodology gap (no pass cross-referenced specs to source design at layer level). |
| Pass 2 (session 1, early) | 41 (12 design + 4 specs + 23 code + 2 infra) | **Done** | 2026-04-16-pass-2-audit.md. Confirmed Finding 0 at 3 levels (spec/code/infra). Identified Finding 0b (assistant-as-kernel-endpoint instead of chat-harness). Verified 8 other subsystems clean. |
| Pass 3 (session 1, middle) | Extended to +63 design artifacts (63 new files added) | **17 of 63 done; 46 remaining** | When complete → comprehensive vision map (Task #7) |
| Pass 4 (not started) | All code in `/Users/home/Repositories/indemn-os/` | Not started | Discrepancy report: for every vision claim, is it correctly implemented? |

---

## Remaining 46 files to read (Pass 3 continuation)

Listed in priority order. Categories in brackets.

### Tier S — Architecturally critical (18)

These contain the most architectural-layer decisions. Read first:

- [design-source] 2026-04-08-primitives-resolved.md — where the 6 primitives got locked
- [design-source] 2026-04-08-kernel-vs-domain.md — the kernel/domain layer boundary decision
- [design-source] 2026-04-09-temporal-integration-architecture.md — Temporal placement (directly relevant to Finding 0)
- [design-source] 2026-04-09-unified-queue-temporal-execution.md — queue/execution (directly relevant to Finding 0)
- [design-source] 2026-04-09-data-architecture-solutions.md — security, OrgScopedCollection, PlatformCollection
- [design-source] 2026-04-09-architecture-ironing-round-3.md — final architecture ironing before session 5
- [design-retrace] 2026-04-10-crm-retrace.md — pressure test (surfaced actor-context scoping)
- [design-retrace] 2026-04-10-eventguard-retrace.md — pressure test (surfaced mid-conversation event delivery — Finding 0 origin)
- [design-retrace] 2026-04-10-gic-retrace-full-kernel.md — pressure test (surfaced bulk ops, coalescing)
- [design-source] 2026-04-13-documentation-sweep.md — cross-cutting updates after all design sessions
- [design-source] 2026-04-13-infrastructure-and-deployment.md — explicit infrastructure design
- [spec-verification] 2026-04-14-impl-spec-verification-report.md — the 4-pass verification audit
- [spec-gap-tracking] 2026-04-14-impl-spec-gaps.md — 90 gaps identified
- [runtime-findings] 2026-04-15-shakeout-session-findings.md — runtime issues from first boot
- [earlier-audit] 2026-04-15-spec-vs-implementation-audit.md — earlier audit
- [stakeholder-context] context/craigs-vision.md — Craig's foundational thesis (referenced throughout)
- [design-source] 2026-04-08-pressure-test-findings.md — consolidated pressure test outcomes
- [design-source] 2026-04-09-consolidated-architecture.md — architecture consolidation

### Tier A — High value (9)

- [design-pressure-test] 2026-04-07-challenge-realtime-systems.md
- [design-pressure-test] 2026-04-07-challenge-distributed-systems.md
- [design-pressure-test] 2026-04-07-challenge-mvp-buildability.md
- [design-pressure-test] 2026-04-07-challenge-insurance-practitioner.md
- [design-source] 2026-04-08-actor-spectrum-and-primitives.md
- [design-source] 2026-04-08-actor-references-and-targeting.md
- [design-source] 2026-04-08-entry-points-and-triggers.md
- [design-source] 2026-04-09-architecture-ironing-round-2.md
- [design-source] 2026-04-09-architecture-ironing.md

### Tier B — Reviews + context (6)

- [design-review] 2026-04-09-capabilities-model-review-findings.md
- [design-review] 2026-04-09-data-architecture-review-findings.md
- [design-source] 2026-04-13-remaining-gap-sessions.md
- [stakeholder-context] context/architecture.md
- [stakeholder-context] context/business.md
- [stakeholder-context] context/product.md

### Tier C — Superseded / context (13)

- [spec-superseded] 2026-04-14-impl-spec-phase-0-1-addendum.md (superseded by consolidated)
- [spec-superseded] 2026-04-14-impl-spec-phase-0-1.md (superseded)
- [spec-superseded] 2026-04-14-impl-spec-phase-2-3.md (superseded)
- [spec-superseded] 2026-04-14-impl-spec-phase-4-5.md (superseded)
- [spec-superseded] 2026-04-14-impl-spec-phase-6-7.md (superseded)
- [session-checkpoint] 2026-04-08-session-3-checkpoint.md
- [session-checkpoint] 2026-04-09-session-4-checkpoint.md
- [session-checkpoint] 2026-04-10-session-5-checkpoint.md
- [session-checkpoint] 2026-04-13-session-6-checkpoint.md
- [stakeholder-context] context/strategy.md
- [stakeholder-context] vision/2026-03-25-the-vision-v1.md
- [stakeholder-context] vision/2026-03-25-the-vision.md
- [design-pressure-test] 2026-04-07-challenge-developer-experience.md (will come up next in read-next order — already sampled but notes not written yet. Check if marked checked in manifest before writing. — UPDATE: yes, already checked per manifest, note exists)

---

## Vision map — synthesized from the 58 files read so far

**Caveat:** This is a working draft. Next session must extend/refine it after reading the remaining 46 files. The user emphasized: "later artifacts may override earlier uncertain decisions."

### 1. The six primitives

| Primitive | Role | Source artifacts |
|---|---|---|
| Entity | Data with structure + optional lifecycle | white-paper, core-primitives, data-architecture-everything-is-data, entity-capabilities-and-skill-model |
| Message | "Nervous system" — connective tissue | core-primitives, realtime-architecture, bulk-operations |
| Actor | Participant (human or associate) | white-paper, associate-architecture |
| Role | Permissions + watches | white-paper, base-ui-and-auth, authentication-design |
| Organization | Multi-tenancy scope | white-paper, data-architecture-everything-is-data ("environments = orgs") |
| Integration | External connectivity (primitive #6) | integration-as-primitive |

### 2. The seven kernel entities

Organization, Actor, Role, Integration, **Attention**, **Runtime**, **Session** — all managed via CLI/API like any entity, but kernel depends on them.
- Attention added in realtime-architecture-design (unifies UI soft-lock + active routing context)
- Runtime added in realtime-architecture-design (deployable host for associate execution)
- Session added in authentication-design (7th; supports hybrid JWT + opaque refresh)

### 3. Trust boundary + deployment topology (CRITICAL for Finding 0)

**Design says (white-paper + realtime-architecture-design):**
- **Inside trust boundary**: API Server + Queue Processor + Temporal Worker (share ONE kernel image, direct MongoDB access)
- **Outside trust boundary**: Base UI + Harnesses + CLI + Tier 3 apps (API-auth only)
- **Three harness images required** (from realtime-architecture-design Part 4):
  - `indemn/runtime-voice-deepagents:1.2.0` — voice + deepagents + LiveKit Agents
  - `indemn/runtime-chat-deepagents:1.2.0` — chat + deepagents + WebSocket server
  - `indemn/runtime-async-deepagents:1.2.0` — async + deepagents + Temporal worker
- "The harness uses the CLI, not a separate Python SDK. This is the key design decision."
- Kernel is LLM-agnostic + framework-agnostic

**Specs did (Phase 2-3 §2.4 + Phase 4-5 §4.7):**
- Put `process_with_associate` inside `kernel/temporal/activities.py` as Temporal activity
- Imports `anthropic` directly in kernel
- Put assistant as `kernel/api/assistant.py` endpoint — NO tools
- Only voice harness shown in Phase 5 (as example, not deployable); chat + async harnesses MISSING from spec entirely

**Code does:** matches the spec (faithful implementation of the deviation)

**Infrastructure does:**
- Dockerfile builds ONLY the kernel image (no harness Dockerfiles exist)
- docker-compose.yml starts only API + Queue Processor + Temporal dev (kernel services)
- No `harnesses/` directory in `/Users/home/Repositories/indemn-os/`

**→ Finding 0 confirmed at 3 levels.**

### 4. Kernel mechanisms (all in `kernel/`)

- **`save_tracked()`** — the atomic transaction: entity write + changes record + watch evaluation + message creation. #1 architectural invariant. (Pass 1 found regression; fixed 2026-04-16 per comprehensive audit.)
- **Selective emission** — only state transitions + @exposed methods + create/delete emit messages
- **Watch evaluation** with cache + scoped watches (field_path + active_context resolution at emit time)
- **Rule engine** + Lookups (condition language shared with watches)
- **Capability library** + `--auto` pattern (auto_classify + stale_check)
- **Correlation ID** + causation_id + cascade depth (max 10)
- **Visibility timeout** + idempotent processing + max_attempts
- **Optimistic dispatch + sweep backstop** (optimistic from API after save_tracked, sweep in queue processor every ~5s)
- **Organizations as environments** — clone/diff/deploy with config only (no instances, no secrets, no messages)
- **Context propagation** via X-Correlation-ID + X-Cascade-Depth headers

### 5. Entity framework (from data-architecture-everything-is-data + entity-framework)

- Entity definitions as DATA in MongoDB (`entity_definitions` collection), not Python classes on disk
- Dynamic class creation via `create_model` + Beanie Document inheritance
- `factory.py` creates classes from EntityDefinition at startup
- Auto-generation of CLI + API + skills per entity
- Flexible data schema (form_schema-driven validation)
- Schema migration first-class (rename, type-change, batching, aliases, rollback)
- Dual base class post-shakeout: KernelBaseEntity (for 7 kernel entities) + DomainBaseEntity (for dynamic domain entities with `_DomainQuery`)

### 6. Integration primitive + adapters

- Integration is primitive #6; Adapter is implementation (kernel code in `kernel/integration/adapters/`)
- Adapter registry keyed by `{provider}:{version}`
- Credential resolution chain: actor → owner (for owner-bound associates) → org (role-based access)
- Credentials NEVER in MongoDB — AWS Secrets Manager via `secret_ref`
- Provider_version enables per-org adapter upgrades
- Outbound + inbound (webhook dispatch via `/webhook/{provider}/{integration_id}`)
- Outlook + Stripe as MVP reference adapters
- Voice clients for humans = Integration with `system_type=voice_client`

### 7. Authentication (from authentication-design)

- **Session is the 7th kernel entity**
- 5 auth method types: password (Argon2id in MongoDB), totp (seed in Secrets Manager), sso (via Integration primitive with identity_provider system_type), token (opaque long-lived, hashed), magic_link (one-time)
- Hybrid JWT + refresh token model: access token 15 min (HS256, jti), refresh token opaque random in Secrets Manager
- JWT signing: **platform-wide key** (not per-org) — simpler, security via org_id in claims
- MFA policy: role-level `mfa_required` + actor `mfa_exempt` override + org `default_mfa_required`
- Platform admin cross-org: `_platform` system org + PlatformCollection + work-type tagging + time-limited (4h default, 24h max) + customer-configurable notification
- Claims refresh on role change (not revocation): `claims_stale=true`, next request auto-refreshes
- Default assistant inherits user's session JWT (injected into its harness at session start) — **per design, this is a chat-harness instance**; current code has it as kernel endpoint → **Finding 0b**
- Pre-auth rate limiting: 5 failures in 10 min → 30 min lockout
- Revocation cache: in-memory per API instance, invalidated via Change Stream on Session
- First-org bootstrap: magic_link token via stdout

### 8. Base UI (from base-ui-operational-surface)

- **UI is projection of system definition, not an application**
- Auto-generated from entity definitions only; **no per-org custom UI**, no per-entity custom code
- Tables > charts > prose. Tables are interactive (sort, filter, drill, take actions)
- Auto-gen rendering contract: entity list views / entity detail views / queue view / role overview / bootstrap entity observability / pipeline metric widgets / integration health / runtime observability / cascade viewer / assistant panel
- Kernel aggregation capabilities: `state-distribution`, `throughput`, `dwell-time`, `queue-depth`, `cascade-lineage`
- **Assistant at top-bar of every view (slim, always-visible, `/` or Cmd-K focus)** — slide-in panel on engagement
- **Assistant is a running chat-harness instance** — not a kernel endpoint (per design — but current code violates this)
- Real-time via MongoDB Change Streams filtered by org_id + subscription filters
- WebSocket keepalive (30-45s ping) — hosting proxy drops idle at 60s
- `Widget`, `DashboardConfig`, `AlertConfig` deferred to post-MVP
- Active alerting deferred

### 9. Bulk operations (from bulk-operations-pattern)

- Pattern, not primitive. Composes existing mechanisms.
- Generic `bulk_execute` Temporal workflow in kernel code
- `bulk_operation_id = temporal_workflow_id` (deliberate coupling)
- 5 CLI verbs: `bulk-create`, `bulk-transition`, `bulk-method`, `bulk-update` (silent), `bulk-delete`
- Per-batch MongoDB transaction (~1000 ops max per txn)
- Default failure = skip-and-continue; `--failure-mode=abort` opt-in
- Permanent errors (StateMachine, Validation, PermissionDenied, EntityNotFound) skip; transient (VersionConflict, Network, lock timeout) retry
- Multi-entity per row via skill code (Option α); `bulk_apply` DSL deferred
- No cross-batch rollback for MVP; saga compensation deferred
- Terminal states: `completed` / `completed_with_errors` / `failed`

### 10. Simplifications accepted

From 2026-04-13-simplification-pass.md:
- **Watch coalescing REMOVED from kernel** → UI rendering concern (group by correlation_id). NO `coalesce` field on watches, NO `batch_id` on messages, NO grouping logic in kernel emission path.
- **Rule evaluation trace removed as separate concept** → metadata on existing changes collection records
- Kept in MVP (pushed back on deferrals): schema migration, all 5 Attention purposes, content visibility scoping, rule groups with lifecycle
- Deferred post-MVP: WebAuthn/passkeys, per-operation MFA re-verification (`requires_fresh_mfa`)
- "Bootstrap entity" renamed to "kernel entity"

### 11. Phase structure (final, from white paper § 11)

8 phases:
- Phase 0: Development Foundation (repo, CLAUDE.md, env, CI, deploy config)
- Phase 1: Kernel Framework (entity + message + watch + rule + capability + auth middleware + Session + 7 kernel entities)
- Phase 2: Associate Execution (Temporal — **this is where Finding 0 entered**)
- Phase 3: Integration Framework (adapters)
- Phase 4: Base UI (**this is where Finding 0b entered — assistant as kernel endpoint**)
- Phase 5: Real-Time (Attention activation, Runtime deployment, **harness pattern** — only voice example in spec, not built)
- Phase 6: Dog-Fooding (Indemn CRM use case — NOT yet implemented)
- Phase 7: First External Customer (GIC)

Note earlier artifacts had 6 phases (2026-04-02-implementation-plan); evolved to final 8.

### 12. "Everything is data" — data architecture

- OS Codebase (Git) = PLATFORM (deployed once per release)
- MongoDB = APPLICATION (per-org config + business data + kernel cross-org data)
- S3 = unstructured files (scoped by org_id)
- Temporal Cloud = execution state (no app data)
- OTEL backend = ephemeral traces (days-weeks retention)
- Clone/diff/deploy semantics — config only, no instances/messages/secrets
- YAML export format (entities/, roles/, rules/{entity}/, skills/*.md, lookups/, actors/, integrations/, capabilities/)

---

## Finding status (so far)

### Finding 0 — CONFIRMED (agent execution in wrong architectural layer)

**Magnitude:** STRUCTURAL. Not a feature gap — architectural-layer mismatch propagated spec → code → infrastructure.

**Cascade of symptoms (all traced to this root):**
1. Assistant has no tools (Finding 2 from Pass 1 = Finding 0b)
2. Kernel knows about Anthropic (violation of LLM-agnostic principle)
3. No real-time channels work (no harnesses)
4. Unified actor model partially broken (async in-kernel, real-time doesn't run)
5. Sandbox execution absent (per Layer 3 design, Daytona wraps agent execution)
6. Task-queue model flattened (everything on `indemn-kernel` queue)

**Fix direction:**
- Build `harnesses/async-deepagents/` first (replaces `process_with_associate`)
- Build `harnesses/chat-deepagents/` (replaces `kernel/api/assistant.py`; resolves Finding 0b)
- Build `harnesses/voice-deepagents/` (per Phase 5 spec example)
- Update Dockerfile(s) + docker-compose.yml + deployment per harness image

**Files with concrete evidence:**
- `/Users/home/Repositories/indemn-os/kernel/temporal/activities.py` (Finding 0 code site)
- `/Users/home/Repositories/indemn-os/kernel/api/assistant.py` (Finding 0b code site)
- `/Users/home/Repositories/indemn-os/Dockerfile` (only builds kernel image)
- `/Users/home/Repositories/indemn-os/docker-compose.yml` (only kernel services)

### Subsystems verified clean (no Finding 0-class deviations found)

Per Pass 2 audit, confirmed:
1. Integration adapter dispatch — correctly kernel-side per design
2. Channel transport (kernel-side parts) — WebSocket, events stream, interaction transfer correctly placed
3. Skill execution plumbing (schema + generator + integrity) — correctly placed
4. Authentication — all kernel-side per design
5. Bulk operations — `bulk_execute` correctly kernel-side
6. Base UI auto-generation (except the assistant) — correct pattern
7. Org lifecycle — clone/diff/deploy correctly kernel-side
8. Watch coalescing — correctly simplified out of kernel

---

## Next session — step-by-step resumption

### Step 1: Orient (5 minutes)

```bash
cd /Users/home/Repositories/operating-system/.claude/worktrees/roadmap
cat .audit/SESSION-HANDOFF.md  # this document
cat .audit/manifest.yml | head -30
ls .audit/notes/ | wc -l  # should be 58 or 59
```

### Step 2: Continue Pass 3 reading (priority order)

Use `bash .claude/skills/systematic-audit/read-next.sh` to get next file. The script picks in manifest order — but you can read OUT OF ORDER if you want to prioritize Tier S files. To read out of order:
1. Read the file directly with Read tool
2. Write notes to `.audit/notes/<slug>.md` per the template
3. Run `bash .claude/skills/systematic-audit/validate-notes.sh <path>` to mark it checked

**Recommendation for next session:**
- Tier S first (18 files) — closes most remaining Finding 0-class discovery risk
- Then Tier A, B, C as context allows
- Notes should be concise — extract architectural claims + supersedence relationships, skip field-level detail

**For each file, ask:**
1. What architectural-layer claims does this make (kernel/harness/external/browser)?
2. Does it constrain the trust boundary or deployment topology?
3. Does it specify what framework/library lives where?
4. Does it supersede an earlier artifact's decision?
5. Does it introduce a mechanism or resolve an open question?

### Step 3: Regenerate cross-reference matrix

After all 46 files checked:
```bash
bash .claude/skills/systematic-audit/cross-reference.sh
```

This regenerates `.audit/cross-reference-matrix.md` with ALL 104 files' layer/location declarations — the primary tool for finding layer mismatches.

### Step 4: Build final vision map

Extend the vision map draft in this document (Section "Vision map — synthesized from the 58 files") with anything new from the 46 remaining files. Organize by subsystem. For each subsystem, note:
- What the design says (source artifact references)
- Any supersedence (earlier decision overridden by later)
- The final authoritative claim

Save to `projects/product-vision/artifacts/2026-04-17-vision-map.md` (or date the next session).

**Key question to answer per subsystem:** What is the authoritative design statement for where this subsystem lives, what it depends on, and how it's deployed?

### Step 5: Comprehensive implementation audit (Pass 4)

For every claim in the final vision map, check implementation.

**Scope:** `/Users/home/Repositories/indemn-os/`

**Code files already read in Pass 2** (23 files, notes at `.audit/notes/`):
- kernel/temporal/{activities, workflows, worker}.py
- kernel/api/{assistant, websocket, events, interaction, auth_routes, registration, bulk, org_lifecycle}.py
- kernel/integration/{adapter, registry, dispatch, resolver}.py
- kernel/skill/{generator, schema}.py
- kernel/auth/{session_manager, jwt}.py
- kernel/watch/{cache, evaluator}.py
- ui/src/assistant/{AssistantProvider.tsx, useAssistant.ts}
- Dockerfile + docker-compose.yml

**Additional code files likely needed for full Pass 4:**
- kernel/entity/{base, definition, factory, state_machine, computed, flexible, migration, exposed, save}.py (entity framework — core)
- kernel/message/{schema, bus, mongodb_bus, emit, event_metadata, dispatch, idempotency}.py (message system)
- kernel/changes/{collection, hash_chain}.py (audit trail)
- kernel/capability/{registry, auto_classify, aggregations, stale_check}.py
- kernel/rule/{schema, engine, lookup, validation}.py
- kernel/scoping/{org_scoped, platform}.py (OrgScopedCollection, PlatformCollection)
- kernel/observability/{tracing, correlation, logging}.py
- kernel/queue_processor.py
- kernel/seed.py
- kernel/api/{app, meta, health, errors, bootstrap, webhook, skill_routes, human_review, direct_invoke, admin_routes, queue_routes, rule_routes, integration_routes, lookup_routes}.py
- kernel/cli/ (all 18 command modules)
- kernel_entities/{organization, actor, role, integration, attention, runtime, session}.py
- kernel/auth/{middleware, password, rate_limit, audit, token}.py
- kernel/integration/{credentials, rotation}.py + adapters/{outlook, stripe_adapter}.py
- kernel/watch/{scope, validation}.py
- ui/src/ (full tree — views, components, auth, layout, hooks, api)
- tests/ (to verify behavior expectations)

**Recommended audit workflow:** For each subsystem in the vision map:
1. List the specific files that implement it
2. Read each file (or spot-check if Pass 2 already covered it)
3. For each design claim in the vision map, verify the code matches
4. Record any discrepancy (vision says X, code does Y, reason/impact)

### Step 6: Produce discrepancy report

Deliverable: `projects/product-vision/artifacts/2026-04-17-alignment-audit.md` (or dated for next session).

Structure:
1. Executive summary (count of discrepancies found, severity classification)
2. **Finding 0** (already known — restate with new evidence from remaining files if any)
3. **Finding 0b** (assistant-as-chat-harness gap)
4. Per-subsystem discrepancy findings (for each of the 12 subsystems in the vision map):
   - Vision says
   - Spec says
   - Code does
   - Discrepancy? If yes: severity (structural / critical / important / cosmetic), impact, fix direction
5. Methodology notes

---

## Special context for next session

### The synthesis-gate hook is active

`.claude/settings.local.json` has the hook configured. It blocks Write/Edit on files matching `(audit|report|finding|summary|deviation|review-report|analysis).md$` UNLESS manifest is 100% checked. To write the final audit report, all 104 files must be checked first.

### The "later artifacts override earlier" principle

User emphasized: "later artifacts may override earlier uncertain decisions." When building vision map, resolve conflicts by timestamp — later wins. But check for explicit supersedence statements (e.g., Phase 2-3 consolidated spec header says it supersedes base spec + addendum).

### The user is not looking for a rubber stamp

User pushed back when I suggested skipping "summaries." Their view: every artifact matters, don't prune. The audit should be thorough.

### Trust boundary claims are the most Finding-0-relevant

When reading remaining files, pay special attention to any statement about:
- Where code runs (kernel process / harness process / browser / external)
- Who has direct DB access (trust boundary)
- What framework/library lives where (LLM-agnostic kernel principle)
- Task queue topology (should be per-Runtime, not single `indemn-kernel`)

### The retraces are critical

2026-04-10-crm/eventguard/gic-retrace are pressure tests. Per Pass 2 notes, these surfaced:
- CRM retrace → actor-context scoping need
- EventGuard retrace → mid-conversation event delivery gap (Finding 0 origin)
- GIC retrace → bulk operations + coalescing concerns

Reading these carefully may reveal additional architectural claims not yet captured.

### Craig's vision doc is foundational

`context/craigs-vision.md` is referenced in every subsequent artifact as the thesis source. Should be read in Tier S.

---

## Files read so far (58 files) — reference list

All have structured notes at `.audit/notes/<slug>.md`. The filename slug is the file path with `/` and `.` replaced by `_`.

**Design artifacts (22):**
- 2026-03-24-associate-domain-mapping.md
- 2026-03-24-source-index.md
- 2026-03-25-associate-architecture.md
- 2026-03-25-domain-model-research.md
- 2026-03-25-domain-model-v2.md
- 2026-03-25-platform-tiers-and-operations.md
- 2026-03-25-session-notes.md
- 2026-03-25-the-operating-system-for-insurance.md
- 2026-03-25-why-insurance-why-now.md
- 2026-03-30-design-layer-1-entity-framework.md
- 2026-03-30-design-layer-3-associate-system.md
- 2026-03-30-entity-system-and-generator.md
- 2026-03-30-vision-session-2-checkpoint.md
- 2026-04-02-core-primitives-architecture.md
- 2026-04-02-design-layer-4-integrations.md
- 2026-04-02-design-layer-5-experience.md
- 2026-04-02-implementation-plan.md
- 2026-04-03-message-actor-architecture-research.md
- 2026-04-07-challenge-developer-experience.md (note: raw JSON transcript; notes capture agent findings)
- 2026-04-09-data-architecture-everything-is-data.md
- 2026-04-09-entity-capabilities-and-skill-model.md
- 2026-04-10-base-ui-and-auth-design.md
- 2026-04-10-bulk-operations-pattern.md
- 2026-04-10-integration-as-primitive.md
- 2026-04-10-post-trace-synthesis.md
- 2026-04-10-realtime-architecture-design.md
- 2026-04-11-authentication-design.md
- 2026-04-11-base-ui-operational-surface.md
- 2026-04-13-simplification-pass.md
- 2026-04-13-white-paper.md

**Consolidated specs (4):**
- 2026-04-14-impl-spec-phase-0-1-consolidated.md
- 2026-04-14-impl-spec-phase-2-3-consolidated.md
- 2026-04-14-impl-spec-phase-4-5-consolidated.md
- 2026-04-14-impl-spec-phase-6-7-consolidated.md

**Code files (23):**
- /Users/home/Repositories/indemn-os/kernel/temporal/activities.py
- /Users/home/Repositories/indemn-os/kernel/api/assistant.py
- /Users/home/Repositories/indemn-os/kernel/temporal/workflows.py
- /Users/home/Repositories/indemn-os/kernel/temporal/worker.py
- /Users/home/Repositories/indemn-os/kernel/integration/adapter.py
- /Users/home/Repositories/indemn-os/kernel/integration/registry.py
- /Users/home/Repositories/indemn-os/kernel/integration/dispatch.py
- /Users/home/Repositories/indemn-os/kernel/integration/resolver.py
- /Users/home/Repositories/indemn-os/kernel/api/websocket.py
- /Users/home/Repositories/indemn-os/kernel/api/events.py
- /Users/home/Repositories/indemn-os/kernel/api/interaction.py
- /Users/home/Repositories/indemn-os/kernel/skill/generator.py
- /Users/home/Repositories/indemn-os/kernel/skill/schema.py
- /Users/home/Repositories/indemn-os/kernel/auth/session_manager.py
- /Users/home/Repositories/indemn-os/kernel/auth/jwt.py
- /Users/home/Repositories/indemn-os/kernel/api/auth_routes.py
- /Users/home/Repositories/indemn-os/kernel/api/registration.py
- /Users/home/Repositories/indemn-os/kernel/api/bulk.py
- /Users/home/Repositories/indemn-os/ui/src/assistant/AssistantProvider.tsx
- /Users/home/Repositories/indemn-os/ui/src/assistant/useAssistant.ts
- /Users/home/Repositories/indemn-os/kernel/api/org_lifecycle.py
- /Users/home/Repositories/indemn-os/kernel/watch/cache.py
- /Users/home/Repositories/indemn-os/kernel/watch/evaluator.py

**Infrastructure (2):**
- /Users/home/Repositories/indemn-os/Dockerfile
- /Users/home/Repositories/indemn-os/docker-compose.yml

---

## Complete index of existing notes

All 59 notes files at `.audit/notes/`. Paths are absolute and can be read directly with the Read tool. The filename slug is the source file path with `/` and `.` replaced by `_`.

**How to use this index:** when you need to understand what an earlier session decided about a specific subsystem, read the corresponding note. Notes are structured (Key Claims / Architectural Decisions / Layer/Location Specified / Dependencies / Code Locations / Cross-References / Open Questions) — they surface the architectural content without re-reading the original file.

### Design artifacts (30 notes — corresponds to 30 design-source + 2 in subfolders already read)

- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-24-associate-domain-mapping_md.md` — 48 associates → domain objects + capabilities frequency
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-24-source-index_md.md` — source catalog (provenance)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-25-associate-architecture_md.md` — associates as deep agents (early)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-25-domain-model-research_md.md` — 70 entities / 9 sub-domains
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-25-domain-model-v2_md.md` — DDD classification
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-25-platform-tiers-and-operations_md.md` — 3 tiers (Out-of-box / Configured / Developer)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-25-session-notes_md.md` — session 1 vibes
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-25-the-operating-system-for-insurance_md.md` — core OS framing
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-25-why-insurance-why-now_md.md` — business rationale
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-30-design-layer-1-entity-framework_md.md` — Layer 1, modular monolith, FastAPI/Typer/Beanie (partially superseded)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-30-design-layer-3-associate-system_md.md` — Layer 3, deepagents + sandbox (Daytona)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-30-entity-system-and-generator_md.md` — auto-generation pattern as OS kernel
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-03-30-vision-session-2-checkpoint_md.md` — session 2 summary
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-02-core-primitives-architecture_md.md` — 4 primitives + foundation hardening (optimistic concurrency, transaction atomicity, selective emission, correlation_id, visibility timeout — all retained)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-02-design-layer-4-integrations_md.md` — adapter pattern, entity operations own external connectivity
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-02-design-layer-5-experience_md.md` — UI as visual layer on entity API
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-02-implementation-plan_md.md` — 6-phase plan (later 8)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-03-message-actor-architecture-research_md.md` — actor model / outbox / MongoDB queues research
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-07-challenge-developer-experience_md.md` — DX pressure test (raw agent JSON transcript; notes capture findings)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-09-data-architecture-everything-is-data_md.md` — "everything is data"
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-09-entity-capabilities-and-skill-model_md.md` — kernel capabilities + --auto pattern
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-10-base-ui-and-auth-design_md.md` — early UI + auth sketch (largely superseded)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-10-bulk-operations-pattern_md.md` — bulk operations = kernel pattern (not primitive)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-10-integration-as-primitive_md.md` — Integration as primitive #6
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-10-post-trace-synthesis_md.md` — post-retrace synthesis (10 items routing document)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-10-realtime-architecture-design_md.md` — **THE Finding 0 source artifact**. Harness pattern, Runtime entity, Attention entity, scoped watches
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-11-authentication-design_md.md` — full auth (Session = 7th kernel entity)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-11-base-ui-operational-surface_md.md` — final Base UI (assistant-as-harness claim)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-13-simplification-pass_md.md` — watch coalescing removed from kernel
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-13-white-paper_md.md` — design source of truth

### Consolidated specs (4 notes)

- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-14-impl-spec-phase-0-1-consolidated_md.md` — Phase 0 (foundation) + Phase 1 (kernel framework)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-14-impl-spec-phase-2-3-consolidated_md.md` — **Phase 2 (associate exec) + Phase 3 (integrations). Contains Finding 0 source in spec.**
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-14-impl-spec-phase-4-5-consolidated_md.md` — **Phase 4 (Base UI) + Phase 5 (Real-Time). Contains Finding 0b source in spec (kernel/api/assistant.py); voice harness example only.**
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-14-impl-spec-phase-6-7-consolidated_md.md` — Phase 6 (dog-fooding) + Phase 7 (first external customer)

### Code — kernel Temporal + API (8 notes)

- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_temporal_activities_py.md` — **Finding 0 code site** (process_with_associate + _execute_reasoning + _execute_deterministic + _execute_hybrid + `import anthropic`)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_temporal_workflows_py.md` — ProcessMessageWorkflow + HumanReviewWorkflow + BulkExecuteWorkflow
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_temporal_worker_py.md` — registers all 3 workflows + 8 activities on `indemn-kernel` task queue
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_api_assistant_py.md` — **Finding 0b code site** (kernel endpoint, no tools)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_api_websocket_py.md` — UI real-time via MongoDB Change Streams
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_api_events_py.md` — events stream endpoint (server side of `indemn events stream`)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_api_interaction_py.md` — handoff + observe endpoints
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_api_registration_py.md` — auto-registration of entity routes

### Code — kernel Integration (4 notes)

- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_integration_adapter_py.md` — Adapter base class
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_integration_registry_py.md` — ADAPTER_REGISTRY
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_integration_dispatch_py.md` — get_adapter + execute_with_retry
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_integration_resolver_py.md` — credential resolution chain

### Code — kernel Auth (4 notes)

- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_auth_session_manager_py.md` — session lifecycle
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_auth_jwt_py.md` — JWT + partial tokens + revocation cache
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_api_auth_routes_py.md` — login/SSO/MFA/platform-admin/signup/refresh-claims/auth-events
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_api_bulk_py.md` — bulk monitoring endpoints (list/status/cancel)

### Code — kernel Skill + Watch + Org (5 notes)

- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_skill_generator_py.md` — entity skill markdown generator
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_skill_schema_py.md` — Skill document model
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_watch_cache_py.md` — watch cache (NO coalescing — correctly simplified out)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_watch_evaluator_py.md` — condition evaluator (15 operators + logical composition)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_api_org_lifecycle_py.md` — clone/diff/deploy/export/import

### Code — UI (2 notes)

- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_ui_src_assistant_AssistantProvider_tsx.md` — UI assistant provider (HTTP + streaming, no WebSocket)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_ui_src_assistant_useAssistant_ts.md` — React context hook

### Infrastructure (2 notes)

- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_Dockerfile.md` — builds ONLY kernel image (Finding 0 at infra level)
- `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_docker-compose_yml.md` — only kernel services, no harnesses

### Code — kernel registration (1 note already listed above)

All 59 notes indexed. Each contains the standardized 7-section structure: File/Read/Category header, Key Claims, Architectural Decisions, Layer/Location Specified, Dependencies Declared, Code Locations Specified, Cross-References, Open Questions or Ambiguities.

---

## Final note to next-session Claude

You are resuming a multi-session audit whose end goal is **zero information loss + every discrepancy between vision and implementation identified.**

Your predecessor session ran out of context while reading design artifacts. All notes are on disk — they survive. The manifest has truth of what's done + what's remaining.

**Do not restart from scratch.** The Pass 2 audit (`2026-04-16-pass-2-audit.md`) is complete and confirmed Finding 0. The vision map draft in this document captures synthesized understanding from 58 files. Extend it; don't rewrite.

**Do not skip files.** The user pushed back on that explicitly. All 46 remaining files get read.

**Don't trust your own summary memory.** Read the file, write notes to disk, validate. The manifest + notes are the source of truth, not anything you "remember" from this handoff.

The hardest part is the comprehensive implementation audit (Pass 4). That's the deliverable. The user's endgame: "identify every single discrepancy so that we can ensure what is implemented matches the vision." The audit report is what they're paying context for.
