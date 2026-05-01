---
ask: "Hydrate a fresh Claude session for the USLI quote automation production rollout. Tell the session to read the project comprehensively, point to the design + implementation plan + checklist, give it the current status, and frame the first action."
created: 2026-05-01
workstream: gic-email-intelligence
session: 2026-05-01-h-prep
sources:
  - type: artifacts
    description: "Curated reading list across status, design, architecture, implementation plan, and the paste-ready prod deployment checklist"
  - type: codebase
    description: "Pointers into gic-email-intelligence-usli/ feature worktree where the code lives, gic-email-intelligence-migration/ for the indemn remote"
---

# USLI Quote Automation — Production Rollout Handoff

You're a fresh Claude session continuing the **USLI Quote Automation** rollout for GIC. The feature is **code complete, UAT validated, pre-staged for prod**. Your job is the rollout itself — Phase H of the implementation plan.

**Do NOT execute anything until you've absorbed the project context. Read everything first. Build a complete mental model. Then surface the gate checks before any prod-touching action.** All H-phase steps are `[NEEDS USER APPROVAL]` per the OS production-safety rule.

---

## What this project is (one paragraph)

GIC Underwriters is an MGA (managing general agent) for commercial insurance. Their `quote@gicunderwriters.com` inbox receives ~50 submissions/day from agents — a mix of new business applications, quote requests, follow-ups, and portal acknowledgments. We've built an end-to-end pipeline that ingests these emails, classifies them, extracts submission data (PDF parsing of ACORD forms, contact info, agency lookup), and creates Quotes in **Unisoft** (their AMS) with attachments and notification emails — all autonomously, with deterministic fallbacks for the parts that LLMs can't be trusted to do reliably. **The system has been live in production since 2026-04-23 for `agent_submission` emails. Your work activates the same pipeline pattern for `usli_quote` emails (the 80%+ slice of inbox volume that's currently classified but not acted on).**

## Where we are right now (2026-05-01 evening, awaiting rollout)

The feature is fully implemented, UAT-validated end-to-end on dev-services + UAT Unisoft, and pre-staged for production. Three external blockers gate the rollout:

1. **PR #23 review + merge** by Dolly + Dhruv — open at https://github.com/indemn-ai/gic-email-intelligence/pull/23
2. **DEVOPS-158 closing** — 7-day prod soak that started 2026-04-29 22:50 UTC, target ~2026-05-06
3. **Dhruv configures 2 Datadog monitors** per `2026-05-01-usli-datadog-alerts-spec.md` (no Datadog API key in 1Password vaults; UI config required)

Once those three close, the rollout is largely a paste-ready checklist (see Layer 1 below). The single-flip moment is one Param Store write.

## Reading list (in order)

Read these in order. **Total reading: ~30 min if thorough.** Pre-staged work means most of what existed at the start of UAT prep is already done — the docs reflect the state at the moment rollout begins.

### Layer 0 — This handoff (you're here)

### Layer 1 — Authoritative current rollout reference (~10 min, this is the most important)

1. **`projects/gic-email-intelligence/INDEX.md`** — the project resume map. Status section leads with the 2026-05-01 USLI summary; Artifacts table includes the four 2026-05-01 entries; Decisions section captures the architectural calls.

2. **`projects/gic-email-intelligence/artifacts/2026-05-01-usli-prod-deployment-checklist.md`** — **the paste-ready execution doc**. Captures every identifier (PR #23, latest SHA `655a950`, EC2 instance IDs, Mongo DB names, Param Store paths, Gmail draft ID, customer mailbox folder), the pre-staged work table (✅ what's already done — DO NOT REDO), hard gates verification block, the H.3–H.6 cutover sequence, rollback procedures, and post-launch backfill scripts (K.8 + cutover-window stranded). **You'll spend most of your active work in this doc.**

### Layer 2 — Architecture (~10 min, REQUIRED before executing)

3. **`projects/gic-email-intelligence/artifacts/2026-05-01-usli-deterministic-lookup-architecture.md`** — locks the 3-tier deterministic lookup model. Tier 1 Mongo by USLI ref → Tier 2 Unisoft `GetQuotesForLookupByCriteria` w/ agent+LOB+recency filter + highest-QuoteId tiebreak → Tier 3 caller-creates. Loop-closure stamping (`Submission.ConfirmationNo = usli_ref` on every Submission we touch) drives Tier 1 hit rate to ≥95% within ~2 weeks. Drops the original "Indemn USLI Needs Review" folder — tiebreak resolves ambiguity, no human triage.

4. **`projects/gic-email-intelligence/artifacts/2026-05-01-unisoft-quote-search-canonical-shape.md`** — captures the canonical SOAP wire format for `GetQuotesForLookupByCriteria`. **Critical learning: model the request after the captured UI wire format, NOT after the saved-search XML returned by `GetAllSearchPreferences`.** Same field names, completely different shapes. Lists every dead-end the prior session walked. If a Unisoft op behaves unexpectedly, this doc explains how to diagnose.

5. **`projects/gic-email-intelligence/artifacts/2026-05-01-usli-datadog-alerts-spec.md`** — the two Datadog monitors that Dhruv must configure before H.5: USLI failure rate > 10% over 1h, failed_recovery_review > 0. Includes Slack channel routing + synthetic-test verification pattern.

### Layer 3 — Design + plan (~10 min, skim if Layer 1+2 are absorbed)

6. **`projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-design.md`** — original feature design with 2026-05-01 UPDATE callouts pointing to Layer 2 supersessions. Useful for the *why* behind the architecture if a step's context isn't obvious from the checklist.

7. **`projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-implementation-plan.md`** — the plan that drove the build. Has Updates Log + per-task UPDATE callouts. Phases A–E + G.0 are SHIPPED; H.0–H.6 + K.8 are what your session executes. The checklist (Layer 1) condenses the H + K work; the plan has the broader context.

### Layer 4 — How the system works (~30 min, optional/skim)

8. **`projects/gic-email-intelligence/artifacts/2026-04-29-cutover-execution-handoff.md`** **(on `os-unisoft` branch)** — the post-mortem from when the existing `agent_submission` automation cutover happened. Useful for understanding the deploy patterns (build.yml, build-prod.yml, prod-services EC2, AUTOMATION_START_DATE filter, the unintended-Quote cleanup story). Your USLI rollout follows the same shape.

9. **`projects/gic-email-intelligence/artifacts/2026-04-23-go-live-day-session-2.md`** **(on `os-unisoft` branch)** — classification rules (Rule 7), multi-LOB handling, deterministic activity + notification pattern, ObjectId corruption recovery, duplicate routing.

10. **`projects/gic-email-intelligence/artifacts/2026-04-24-upload-bypass-and-notification-fixes.md`** **(on `os-unisoft` branch)** — Unisoft DTO discipline (full-fields-required), MTOM/XOP chunked attachment uploads, **`SendActivityEmail` on `IEmailService` is the actual email sender** (not `SetActivity`). The C.4 letter_name fix shipped in this session builds on this.

### Layer 5 — Code (the source of truth)

After the docs, browse these files in `gic-email-intelligence-usli/` (the feature worktree):

- **`src/gic_email_intel/automation/skills/process-usli-quote.md`** — the USLI deepagent skill (~300 lines). Three iterations during UAT debugging: explicit `--status failed --error` CLI, Step 3a address parsing from the retailer block, agents-collection sync as a one-time op.
- **`src/gic_email_intel/automation/agent.py`** — `_load_skill` threads 5 placeholders, `create_automation_agent_usli()` lazy-builds prompt, `run_one(factory=...)` accepts dispatch.
- **`src/gic_email_intel/automation/usli_helpers.py`** — `should_upload_pdf` (whitelist), `classify_submission_state` (3-layer), `find_quote_for_usli_ref` (3-tier lookup), `ensure_lookup_index` (lazy Mongo index).
- **`src/gic_email_intel/cli/commands/automate.py`** — `_get_agent_factory` (D.4 dispatch), `_automate_tick` honors `pause_usli_automation`.
- **`src/gic_email_intel/cli/commands/submissions.py`** — `gic submissions classify-usli-state` + `gic submissions find-quote-for-usli` CLIs.
- **`src/gic_email_intel/cli/commands/emails.py`** — `_create_activity_and_notify` filters `GetActionNotifications` by `LetterName` (C.4 fix). SOAK_MODE gates the email-send.
- **`src/gic_email_intel/core/email_mover.py`** — `ensure_folder_exists` factor, `INDEM_USLI_PROCESSED` constant. NO `INDEM_USLI_NEEDS_REVIEW` — architecture dropped it.
- **`tests/fixtures/usli_config.json`** — empirical findings (action_id 67, letter_name "USLI Quote", whitelist patterns, BrokerId 1 / CarrierNo 2).
- **`docker-compose.yml`** — has the new `automation-usli-cron` service (G.0).

Test count baseline: **218 passing, 5 documented skips, 7 pre-existing Atlas-down failures excluded** in CI.

---

## Mental model (internalize these — most are unchanged from session start, plus the new architecture)

**Pipeline:**
```
Outlook (Microsoft Graph)
  → sync cron               (every 5min)   → MongoDB emails collection
  → processing cron         (every 5min)   → LLM classifier + extractor
                                           → submissions / quotes denormalized
  → automation-cron         (every 15min)  → agent_submission flow
                                           → Unisoft Quote / Submission / Activity
  → automation-usli-cron    (every 15min)  → usli_quote flow (NEW)
                                           → Quote (find/create) + Submission stamp
                                           → Activity bound to USLI Submission
                                           → Notification email to retail agent
```

Both crons read from the same Mongo `emails` collection, claim atomically via `gic emails next`, dispatch to different agent factories per `--type`. Both honor `pause_automation` globally; `automation-usli-cron` additionally honors `pause_usli_automation`.

**Three-tier deterministic lookup (the key architectural call):**
- **Tier 1 (Mongo):** `submissions.find({reference_numbers: ref, unisoft_quote_id: {$ne: None}})`. ≥95% steady-state hit rate after ~2 weeks.
- **Tier 2 (Unisoft search):** canonical Criteria DTO + agent + LOB + recency filter + highest-QuoteId tiebreak.
- **Tier 3 (caller-creates):** D.2 skill creates a new Quote with `--confirmation-no <ref>` already stamped (closes Unisoft side of the loop).
- **Loop closure:** every Submission we touch ends with `ConfirmationNo` populated. Loss = degrades back to name-search-with-tiebreak.

**Critical safety properties:**
- **SOAK_MODE** (dev only): blocks Outlook folder moves AND `SendActivityEmail`. Activity records still create in UAT Unisoft (intended). **In prod, SOAK_MODE=false** — folder moves and emails go for real.
- **PAUSE_USLI_AUTOMATION**: per-type kill switch. Set to `true` at H.3 deploy; flipped to `false` at H.5 cutover. Settings reload per cron tick (~15min) so flips take effect within one tick without container restart.
- **`pause-usli-automation`** (Param Store) is the rollback switch. Flip to `true` and the cron stops within 15 min. `docker stop gic-email-automation-usli` is instant.

**Tag separation in Docker:**
- `:main` (built by `build.yml` on push-to-main) → deployed to **dev-services** (`i-0fde0af9d216e9182`)
- `:prod` (built by `build-prod.yml` on push-to-prod) → deployed to **prod-services** (`i-00ef8e2bfa651aaa8`)
- The two are independent — pushing a feature branch to dev (via workflow_dispatch) overwrites `:main` but doesn't touch `:prod`.

**LLM caveats:**
- LLMs corrupt hex strings (Mongo ObjectIds) — `_safe_object_id()` recovers from corruption.
- Skills inlined in system prompt, not loaded as flat files.
- All LLM calls run on Gemini 2.5 Pro/Flash via Vertex AI.

---

## Pre-staged (✅ done at session start — DO NOT REDO)

This is the same table as the deployment checklist's "Pre-staged" section. Surfaced here so you internalize what's already settled before touching anything:

| Item | State |
|---|---|
| Prod Param Store: `usli-quote-action-id=67`, `usli-quote-letter-name="USLI Quote"`, **`pause-usli-automation=true`** | ✅ |
| Prod customer mailbox folder `Indemn USLI Processed` | ✅ created on quote@gicunderwriters.com Inbox |
| Prod `unisoft_agents` collection | ✅ 2,898 agents (synced 4/22) |
| Prod proxy `GetQuotesForLookupByCriteria` smoke test | ✅ Crown Park returns 5 results, USLI carrier name matches prod pattern |
| Gmail draft (G.5 customer comms) | ✅ `r5499973616452698529` saved on craig@indemn.ai |
| `aws-env-loader.sh` PARAM_MAP entries (lines 242-245) | ✅ all 4 USLI keys mapped |
| Datadog alert spec doc | ✅ committed in OS repo (Dhruv configures via UI) |
| UAT validation | ✅ 2/3 USLI emails processed end-to-end (Q:17379 TAMARA, Q:17380 AIRA), 1 legitimate fail |
| Loop-closure stamping verified in UAT | ✅ both successful Submissions have `ConfirmationNo == usli_ref` |
| SOAK_MODE end-to-end gate verified | ✅ live audit: SetActivity fires in UAT, send-activity-email blocked |

## Stakeholders

| Person | Role | What they care about |
|---|---|---|
| **JC** (jcdp@gicunderwriters.com) | Head of underwriting at GIC | Daily queue / backfill updates. Approved USLI feature scope 2026-04-30. T-0 customer comms drafted in his Gmail Drafts (`r5499973616452698529`) — fill date placeholder, then send at H.5. |
| **Dhruv** (Indemn) | DevOps engineer | SOC 2 / Oneleet / WAF / Datadog. **Configures the 2 Datadog monitors** per the spec doc before H.5 cutover. PR #23 reviewer. |
| **Dolly** (Indemn) | Engineer | PR #23 reviewer. |
| **Craig** | The CTO; runs this rollout with you | Will give direction at every approval gate. |

## Hard rules (rollout-related)

- **No prod-touching action without explicit user approval** per OS production-safety rule. Each H step is `[NEEDS USER APPROVAL]`. The checklist marks them inline.
- **Before any prod write, surface the gate-check block** (DEVOPS-158, PR #23, Datadog, prod-services healthy). If any gate is red, STOP and report — do not proceed.
- **The pause flag is the rollback switch.** At any sign of trouble post-go-live, flip `pause-usli-automation` to `true` and report to Craig. Settings reload per tick → stops within 15 min. `docker stop` is instant.
- **Don't backfill historical USLI emails.** Each backfilled email fires `SendActivityEmail` to a real retail agent. The Unisoft audit-trail Quote isn't valuable enough to justify confusing agents with weeks-old quote follow-ups. Specific historical quotes can be one-shot on JC's request.
- **Don't bypass `--status failed`** on `gic emails complete`. The skill iterations during UAT confirmed: omitting `--status failed` silently marks failures as completed (the `--status` default). Failure must always set status explicitly.

## Git layout

**Repos:**
- `gic-email-intelligence-migration/` — mainline checkout. Use this for `git fetch indemn` and the prod-deploy `git push indemn main:prod`.
- `gic-email-intelligence-usli/` — feature worktree. On `feat/usli-quote-automation` at SHA `655a950`. **28 commits ahead of `indemn/main`.** PR #23 captures all of them.

**Remotes in the migration repo:**
- `indemn` → `indemn-ai/gic-email-intelligence` (the active prod repo — branch from here)
- `origin` → `craig-indemn/gic-email-intelligence` (legacy fork, frozen — do not use)
- Branches: `main` (active), `prod` (protected, prod deploys via push or PR), feature branches as needed.

**OS repo (where this handoff and design + plan + checklist live):**
- Worktree: `/Users/home/Repositories/operating-system/.claude/worktrees/gic-feature-scoping/`
- Branch: `os-gic-feature-scoping`
- Latest commit: `e2153a0` (this handoff lives here once committed)

## Conventions

- **Commit style:** `feat(scope): ...`, `fix(scope): ...`, `test: ...`, `docs(scope): ...`. See `git log --oneline` in the feature worktree for examples.
- **PR style:** Summary, Test plan, Why-this-is-a-follow-on. PR #23 is the live example.
- **Reviewers:** Dolly + Dhruv on most PRs.
- **`[NEEDS USER APPROVAL]` markers** throughout the deployment checklist gate every prod-touching step.
- **SSM patterns:** for any non-trivial Python on prod-services, base64-encode locally → decode on EC2 → `docker cp` → `docker exec python /tmp/script.py`. JSON-in-Bash-in-SSM-in-Bash-in-docker is too many quote layers (Lesson #13 from cutover handoff).

## Skills you'll likely use

- **`/aws`** — SSM commands to prod-services, Param Store reads/writes
- **`/github`** — PR #23 status checks, workflow runs, push main → prod
- **`/google-workspace`** (gog) — send the JC draft at H.5
- **`/linear`** — DEVOPS-158 status check, DEVOPS-162 close-out
- **`/mongodb`** / **`/postgres`** — for any post-cutover Mongo state inspection
- **`/slack`** — confirm Datadog alerts fired in #deployment

## Your first response to Craig

After you've absorbed everything:

1. **Confirm context** with a one-paragraph summary back to Craig — what's been done (specifically the 28 commits + UAT validation + 6 pre-stage items), what's blocked (PR #23 review, DEVOPS-158, Dhruv's Datadog config). Mention 2–3 specific things you internalized to demonstrate you actually read the artifacts. Examples: "I see the deterministic-lookup architecture drops the Indemn USLI Needs Review folder entirely — tiebreak resolves ambiguity at C.7" or "I noted the loop-closure design call: C.7 does only Mongo backfill; Unisoft stamping happens in D.2's update branch via `unisoft submission update`" or "I see the prod proxy was already smoke-tested for `GetQuotesForLookupByCriteria` and the carrier name matches prod pattern".

2. **Run the hard gates verification block** from the checklist's "Hard gates" section. Report which are green and which are still pending:
   - Gate 1: DEVOPS-158 status
   - Gate 2: PR #23 review/merge state
   - Gate 3: Datadog monitors configured (manual UI check; ask Craig)
   - Gate 4: prod-services container health

3. **Wait for Craig's instruction** before any H.3+ action. Do not push main → prod, do not flip pause flag, do not send the JC email until each step is explicitly approved.

4. **When approved, execute step-by-step from the checklist.** Each step has paste-ready commands. Stop and report after each step's verification.

Don't try to ship the entire H phase in one go. The checklist is structured for stop-and-verify between H.3, H.4, H.5, and H.6.

Welcome to the rollout.
