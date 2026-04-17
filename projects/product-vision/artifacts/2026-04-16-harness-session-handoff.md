---
ask: "Capture the full state of the harness implementation work so the next session picks up without information loss. Covers: gate status, decisions with rationale, drafts awaiting review, pending input items, and read-me-first sequence for resumption."
created: 2026-04-16
workstream: product-vision
session: 2026-04-16-b (end of)
sources:
  - type: audit-trail
    ref: "Session conversation 2026-04-16-b"
    description: "Multi-turn Gate 0 → Gate 2 review with Craig"
  - type: artifacts
    ref: "Five new artifacts produced in this session (listed below)"
---

# Harness Implementation — Session Handoff

**Written at end of session 2026-04-16-b** to preserve full context across a session clear.

---

## READ-ME-FIRST (next-session Claude)

If you're resuming harness implementation work, follow this sequence **before touching any code or answering any question**:

1. Read THIS file in full (you're doing that now).
2. Read `2026-04-16-vision-map.md` — authoritative synthesized design (23 sections, covers the whole OS).
3. Read `2026-04-16-alignment-audit.md` — the 9 open discrepancies between vision and current implementation.
4. Read `2026-04-16-harness-implementation-plan.md` — the governing plan + gate structure (7 gates requiring Craig's approval).
5. Read `2026-04-16-async-harness-draft.md` — the current drafted implementation for the FIRST harness (async-deepagents). This is what Craig is reviewing.
6. Read `2026-04-16-cli-update-flow.md` — how the `indemn-os` package + `indemn` binary work; foundational for understanding the harness's CLI subprocess pattern.
7. Check INDEX.md Decisions section for any entries dated after 2026-04-16 — they might contain further approvals or refinements.
8. Ask Craig what he wants to tackle — the gate state is captured below, and "what's next" depends on what he's approved since this handoff.

**Do not**:
- Re-read the `.audit/notes/` files (the audit is complete; those notes informed the vision map and alignment audit). Pass 2/3 is done.
- Restart the Gate 0-2 conversation. All those decisions are captured below with rationale.
- Invent new code paths without Craig's input. He explicitly required per-gate approval.

---

## Where We Are — Gate Status

| Gate | Status | Notes |
|---|---|---|
| **G0** (pre-work decisions) | ✓ APPROVED | All 5 sub-decisions locked. See INDEX.md 2026-04-16 entries. |
| **G1** (async harness pre-build) | ✓ APPROVED with G1.3 refinements | LocalShellBackend for MVP, Daytona for prod, switched via env var, both clearly marked in code |
| **G2** (async harness implementation review) | ⬜ DRAFTED, AWAITING REVIEW | Draft at `2026-04-16-async-harness-draft.md`. Three sub-gates: G2.1 (glue code), G2.2 (kernel dispatch rewiring), G2.3 (kernel code deletion — IRREVERSIBLE) |
| **G3** (chat harness pre-build) | ⬜ NOT STARTED | |
| **G4** (chat harness implementation) | ⬜ NOT STARTED | |
| **G5** (voice harness pre-build) | ⬜ NOT STARTED | |
| **G6** (voice harness implementation) | ⬜ NOT STARTED | |
| **G7** (post-implementation verification) | ⬜ NOT STARTED | |

**What's needed from Craig next:**
- Review `2026-04-16-async-harness-draft.md`
- Confirm Q3 (Pydantic model `AgentExecutionInput` — recommended) and Q5 final details (CLI extraction — already confirmed conceptually)
- Approve G2.1 (harness code) and G2.2 (kernel dispatch changes)
- Then implementation can begin in `/Users/home/Repositories/indemn-os/` — G2.3 approval comes AFTER verification

---

## Locked Decisions (in order, with rationale)

### Gate 0 — Pre-work

- **G0.1 Deployable target = Railway** (per-harness service). Matches existing Indemn infra.
- **G0.2 Shared base image** `indemn/harness-base:X.Y.Z`. Reduces duplication across 3 harnesses.
- **G0.3 Repo structure**: `harnesses/{async,chat,voice}-deepagents/` at `indemn-os` repo root. Per realtime-architecture-design.
- **G0.4 Image tagging**: `indemn/runtime-{kind}-{framework}:{version}` where version = semver + `main-{shortsha}` + `latest`.
- **G0.5 Single CI pipeline on push to main** builds all 4 images (kernel + 3 harnesses). Deploys to Railway.

### Gate 1 — Async harness pre-build

- **G1.1 Task queue naming** = `runtime-{runtime_id}` (ObjectId, stable identifier). Per realtime-architecture-design line 461.
- **G1.2 Service token issuance**: `indemn runtime create` prints token once to stdout → operator copies to Railway `INDEMN_SERVICE_TOKEN` env var → harness reads at startup + calls `indemn runtime register-instance`. Bootstrap pattern from first-org signup (authentication-design).
- **G1.3 Sandbox backend — MVP vs prod (refined twice through conversation):**
  - **MVP / testing** = `LocalShellBackend` (no sandbox). Container is the blast radius. Accept risk because we control prompts + inputs during dev.
  - **Pre-prod / production** = `DaytonaSandbox` (per-session isolation). Already have Daytona account. 90ms cold start acceptable for async.
  - **Switch** via `INDEMN_SANDBOX_TYPE` env var. Both implementations clearly marked in `harness_common/backend.py` (Daytona stubbed with `NotImplementedError`).
  - **Refinement note**: initial framing "subprocess.run(args_list), no shell=True is the invariant" was INCORRECT — LocalShellBackend uses `shell=True`. The actual safety model is container isolation + ephemeral container + no DB creds + service-token scope, not the subprocess args-list. Documented in INDEX.md 2026-04-16 entries.
- **G1.4 Middleware** = all 5 deepagents middleware modules enabled (todo, filesystem, subagents, summarization, HITL). Per the conversation + deepagents docs review: these come automatically via `create_deep_agent()` + the configured backend, not via a custom middleware list.
- **G1.5 Migration sequence** = Option B (straight cutover). Still in development, no real workloads. Phased migration reserved for post-Phase 7 real-customer migrations.

### Naming + package

- **Package name on PyPI**: `indemn-os`
- **Binary name**: `indemn` (matches 100+ design-artifact references)
- **Not extending existing `indemn-cli` NPM package** (different runtime, different purpose: current-system ops)

### deepagents API (verified from LangChain docs 2026-04-16)

- `create_deep_agent(model, system_prompt, tools, backend)` is the signature
- Built-in tools: `write_todos`, `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `task` (subagents), and `execute` (only when backend supports it)
- `execute` tool availability by backend:
  - `StateBackend`, `FilesystemBackend`, `StoreBackend` → NO execute
  - `LocalShellBackend` → YES, via `subprocess.run(shell=True)` (MVP choice)
  - Sandbox backends (Modal, Daytona, Runloop, AgentCore, LangSmith) → YES, inside sandbox
- Consequence: **no custom `execute` wrapper needed in agent.py**. Pass the right backend, deepagents handles the rest.
- Sources:
  - https://docs.langchain.com/oss/python/deepagents/overview
  - https://docs.langchain.com/oss/python/deepagents/backends
  - https://docs.langchain.com/oss/python/deepagents/sandboxes

### Q&A

- **Q1 Multi-associate dispatch (Option D)**: Queue Processor picks the associate at dispatch time. Round-robin for MVP. Dispatch decision in `kernel/queue_processor.py::dispatch_associate_workflows`. Handles both `target_actor_id` set (scope resolved) and null (role-only targeting).
- **Q2 Failure semantics**: MVP accepts single Runtime per config. No fallback routing. Temporal retries on same `runtime-{id}` queue.
- **Q3 Activity arg signature** (RECOMMENDED, AWAITING CRAIG LOCK): Pydantic model `AgentExecutionInput` in `indemn_os.types`. Extensible (new fields with defaults = non-breaking). Used by both kernel workflow (caller) + harness activity (callee).
- **Q4 OTEL propagation**: deferred to implementation phase. Need proper W3C traceparent extraction from Temporal context.
- **Q5 CLI extraction** (CONFIRMED): extract `kernel/cli/` to `indemn-os` package. Full rationale in `2026-04-16-cli-update-flow.md`.

---

## Artifacts Produced This Session

All in `projects/product-vision/artifacts/`:

| Artifact | Purpose | Status |
|---|---|---|
| `2026-04-16-pass-2-audit.md` | Pass 2 architectural-layer audit (41 files) — Finding 0 confirmed | Final |
| `2026-04-16-vision-map.md` | Authoritative design synthesis from 104 files | Final |
| `2026-04-16-alignment-audit.md` | 9 open discrepancies between vision + implementation | Final |
| `2026-04-16-harness-implementation-plan.md` | Harness hosting decision (Option 1) + 7 input gates | Governing plan |
| `2026-04-16-async-harness-draft.md` | **Gate 2 draft of async harness** (code, Dockerfiles, kernel diffs, deletion list) | **Awaiting Craig's review** |
| `2026-04-16-cli-update-flow.md` | How `indemn-os` package + `indemn` binary evolve | Foundational reference |
| `2026-04-16-harness-session-handoff.md` | THIS FILE — session continuity | Final |

Plus `.audit/` infrastructure from audit work:
- `.audit/manifest.yml` (104 files checked)
- `.audit/notes/*.md` (104 structured notes)
- `.audit/cross-reference-matrix.md`
- `.audit/SESSION-HANDOFF.md` (audit-specific; this file supersedes for harness work)

And extensive INDEX.md updates — all 2026-04-16 dated Decision entries are from this session.

---

## The Next Immediate Actions

1. **Craig reviews `2026-04-16-async-harness-draft.md`** — specifically §§ 6 (harness code), 7 (kernel rewiring), 8 (deletion list), and the open Q&A in § 10.
2. **Locks any remaining Q&A** — Q3 (Pydantic model), Q5 final extraction shape.
3. **Approves G2.1** (harness code: base image, harness_common, async-deepagents Dockerfile + main.py + agent.py + backend factory) — unlocks building these in the `indemn-os` repo.
4. **Approves G2.2** (kernel dispatch rewiring: ProcessMessageWorkflow per-Runtime routing + worker.py activity registration + queue_processor.py dispatch selection + load_actor activity) — unlocks kernel-side changes.
5. **Implementation proceeds** per § 11 build sequence in the async-harness-draft (extract `indemn_os/`, add load_actor, rewire dispatch, create `harnesses/_base/` + `harnesses/async-deepagents/`, Railway deploy).
6. **Verification per § 9** — all 6 groups must pass.
7. **G2.3 sign-off** (irreversible kernel code deletion) — only after verification passes.
8. **Move to Gate 3** (chat harness pre-build) → Gate 4 (implementation, resolves Finding 0b).
9. **Then Gate 5 + 6** (voice harness).
10. **Gate 7** (post-implementation verification across all harnesses).

After Gate 7: Phase 6 (Indemn CRM dog-fooding) + Phase 7 (GIC first external customer) unblocked. Plus Track B mechanism bugs (D-04, D-07, D-08) and Track C documentation (D-01 dual base class) run in parallel per alignment audit § 7.

---

## Rules for the Next Session (DO / DON'T)

### DO

- Read the artifacts above in full before proposing any change. They capture decisions Craig has explicitly approved.
- Honor the gate structure. Every structural change needs its gate.
- Use deepagents' actual API (verified from docs this session). Don't invent custom tool wrappers unless a specific associate needs one.
- Record new decisions in INDEX.md with date + rationale. Append, don't replace.
- When you're about to touch `/Users/home/Repositories/indemn-os/`, verify you have G2.1 + G2.2 approved. G2.3 is separate + post-verification.
- Keep artifacts as the system of record. Chat scatters; artifacts encapsulate.

### DON'T

- Don't re-litigate Gate 0 or Gate 1. Those decisions are locked with rationale.
- Don't assume the LocalShellBackend safety model is "args-list no shell=True" — it uses shell=True. The actual safety is container-level + controlled inputs. (Mistake I made earlier in this session.)
- Don't wrap deepagents' `execute` in a custom tool. It comes automatically via the backend.
- Don't delete kernel code (G2.3) until harness is verified working end-to-end per § 9 of the async-harness-draft.
- Don't invent URLs, customer names, or business data in prompts/configs/code.
- Don't forget `indemn` is the binary, `indemn-os` is the package, and neither should be confused with NPM's `indemn-cli` (different tool).

---

## The End-Goal Reminder

Craig's end objective (quoted):
> "Identify every single discrepancy so that we can ensure what is implemented matches the vision. That is the end objective: to have the vision being implemented exactly."

The alignment audit identified 9 open discrepancies. Track A (harness work — Gates 2-7) closes Finding 0 + 0b (the 2 structural ones). Tracks B (mechanism bugs D-04, D-07, D-08) and C (D-01 dual base class doc) run in parallel per alignment audit § 7.

After Track A: Phase 6 + Phase 7 unblocked. The OS can run real insurance workloads (Indemn CRM dog-fooding + GIC first customer).
