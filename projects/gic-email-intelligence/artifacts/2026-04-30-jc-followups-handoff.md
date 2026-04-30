---
ask: "Self-contained, fully-hydrating handoff for a fresh session to deliver JC's three follow-up requests (DEVOPS-163, 164, 165). Comprehensive — covers project history, architecture, data model, current production state, and lessons learned — so the new session arrives at peer-level understanding before touching code."
created: 2026-04-30
workstream: gic-email-intelligence
session: 2026-04-30-jc-followups-handoff
sources:
  - type: artifacts
    description: "Curated reading list across project history, architecture, data model, cutover, and the USLI feature plan (whose Sibling PR sections drive the actual work)"
  - type: codebase
    description: "Pointers into gic-email-intelligence-usli/ for the files each sibling touches"
  - type: linear
    description: "DEVOPS-163, 164, 165 already created under DEVOPS-151"
---

# JC Follow-Ups — Handoff

You're a fresh Claude Code session continuing work on **GIC Email Intelligence**. Your concrete job is to ship three small sibling PRs JC asked for: a task-subject format change, a faster-claim cron tightening, and an .eml-export attachment fix. Plus a backfill follow-on after the third lands.

**These are small features, but they touch a live customer-facing production pipeline.** You need full project context — pipeline architecture, data model, cutover state, lessons learned — before writing any code. Don't skip the reading list. The original session that designed this work spent ~3 hours absorbing context before brainstorming, and the same depth applies here.

**Do NOT start writing code until you've absorbed the full reading list below. Read everything. Build a complete mental model. THEN pick a sibling and execute.**

---

## What you're shipping (the goal)

| # | Linear | Title | Gates on |
|---|---|---|---|
| Sibling 1 | DEVOPS-163 | Task subject format → `[LOB] - Business description` | — (ship anytime) |
| Sibling 2 | DEVOPS-164 | Faster claim into "Indemn - Processing" folder | **DEVOPS-158 (7-day soak) closing — target ~2026-05-06.** Do NOT merge before that. |
| Sibling 3 | DEVOPS-165 | `.eml` export includes attachments inline | — (ship anytime) |
| Sibling 4 | DEVOPS-165 backfill | Backfill historical `.eml` uploads | Sibling 3 merged. **[NEEDS USER APPROVAL]** before running. |

JC asked for these directly. Maribel originally surfaced two of them. They're independent of the USLI quote automation feature build (currently paused on an unrelated blocker — see Layer 1 reading).

---

## Reading list (in order — read EVERYTHING)

### Layer 0 — This handoff (you're here)

### Layer 1 — Where the project is right now (~15 min)

1. **`projects/gic-email-intelligence/artifacts/2026-04-30-unisoft-quote-search-investigation.md`** — paused USLI search blocker. Read for context on what's currently in flight on the USLI side and why you should NOT touch that branch.
2. **`projects/gic-email-intelligence/artifacts/2026-04-29-cutover-execution-handoff.md`** (on `os-unisoft` worktree at `/Users/home/Repositories/operating-system/.claude/worktrees/unisoft/projects/gic-email-intelligence/artifacts/`) — post-cutover production state. Read in full. Especially the "Lessons learned / roadblocks hit" section (20 numbered items). Several apply directly to Sibling 2's cron-interval change (e.g., `aws-env-loader.sh PARAM_MAP` lesson, `docker exec -e VAR=val` for one-shots).
3. **`projects/gic-email-intelligence/INDEX.md`** — project resume map. Skim the "Status" section + the artifacts table. The decisions list at the bottom is dense but valuable — most of those 100+ decisions still hold.

### Layer 2 — The implementation plan that drives your work (~20 min)

4. **`projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-implementation-plan.md`** — read in full. Most of it is about the paused USLI feature; the relevant sections for you are the **Sibling PR sections starting around line 1798**. Each sibling has files-touched, failing tests, commit messages spelled out step by step. **You will follow these exactly** — don't reinvent the structure.
   - **Sibling 1** — search for "Sibling PR 1 — Task subject format"
   - **Sibling 2** — "Sibling PR 2 — Faster claim into Indemn - Processing"
   - **Sibling 3** — "Sibling PR 3 — `.eml` export includes attachments inline"
   - **Sibling 4** — "Sibling PR 4 — Backfill historical .eml uploads"
   
   Also note the "File overlap awareness" subsection — three files are touched by both siblings AND the paused USLI feature branch. Merge order matters.

5. **`projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-design.md`** — design doc for the paused USLI feature. Skim. You don't need the workflow details, but the "What This Replaces / What Stays" and the "Out of Scope" sections explicitly mention DEVOPS-163 + DEVOPS-165 as separate-PR work — that's your work.

### Layer 3 — How the system works (~30 min — required, not optional)

These are the architecture docs. Without these, you don't know enough to safely change the pipeline.

6. **`projects/gic-email-intelligence/artifacts/2026-03-30-pipeline-architecture-review.md`** — full pipeline walkthrough: sync → process (extract → classify → link) → automation. Every stage, every file, every limitation. **Critical for Sibling 2** — you're changing cron intervals and adding a claim-on-sync heuristic, you need to understand what each cron does today.
7. **`projects/gic-email-intelligence/artifacts/2026-03-24-data-model-redesign.md`** — submission lifecycle, classification model, situation assessment layer, entities (carriers, agents). Long but worth it — Sibling 2's claim-on-sync heuristic interacts with the classification stage.
8. **`projects/gic-email-intelligence/artifacts/2026-04-23-go-live-day-session-2.md`** (on `os-unisoft` worktree) — first full day of production. Classification Rule 7 (portal product lines), multi-LOB handling, deterministic activity + notification, ObjectId corruption recovery, duplicate routing, folder workflow. **Critical context for Sibling 1** (task subject is set in `create-quote-id.md` Step 6, which this session also touched) and **Sibling 2** (the existing folder-routing logic is in `email_mover.py`, which evolved during this day).
9. **`projects/gic-email-intelligence/artifacts/2026-04-24-upload-bypass-and-notification-fixes.md`** (on `os-unisoft` worktree) — Unisoft DTO conventions (full-fields-required pattern), MTOM/XOP chunked attachment uploads, the `SendActivityEmail` discovery on `IEmailService`. **Important for Sibling 3** — you're rebuilding `.eml` to include attachments inline, which will then get uploaded via the same chunked-upload path documented here.

### Layer 4 — The code (the source of truth)

After the docs, browse these files in `gic-email-intelligence-usli/` (or any worktree off `indemn/main` — they're identical to main other than the paused USLI feature work). You don't need to read every line; you need to understand the shape.

For all siblings:
- **`docker-compose.yml`** — service topology (api, sync-cron, processing-cron, automation-cron). Sibling 2 modifies cron commands.
- **`src/gic_email_intel/agent/harness.py`** — pipeline orchestrator + classification rules (including Rule 7). Sibling 2's claim-on-sync logic decides when to move emails before this orchestrator runs.

For Sibling 1 (task subject format):
- **`unisoft-proxy/client/cli.py`** — Unisoft CLI. Already has `_truncate_subject` helper at the top of the task section. Sibling 1 adds `_format_task_subject(lob, business_description)` next to it and threads `--business-description` through `task create`.
- **`src/gic_email_intel/automation/skills/create-quote-id.md`** — Step 6 (the task creation step) currently builds subject `[Auto] {INSURED_NAME} — {LOB} via {AGENCY}`. Updates to instruct: pass `--lob` + `--business-description`, let CLI auto-format.

For Sibling 2 (faster claim):
- **`src/gic_email_intel/cli/commands/sync.py`** — Sibling 2 adds `_is_likely_agent_submission(email)` heuristic + a folder move at sync time, BEFORE the processing cron classifies it.
- **`src/gic_email_intel/core/email_mover.py`** — folder move helper, auto-creates folders, SOAK_MODE-aware. Sibling 2 calls this at sync time for likely agent submissions.
- **`docker-compose.yml`** — sync-cron interval 300s → 60s; processing-cron interval 300s → 120s.

For Sibling 3 (.eml inline attachments):
- **`src/gic_email_intel/cli/commands/emails.py`** — `export_email` command (line ~532). Currently uses `MIMEMultipart("alternative")` with only text/html parts. Sibling 3 replaces with `MIMEMultipart()` (mixed) + factors out `_build_eml(email_doc, _download)` so Sibling 4's backfill script can reuse it.
- **`src/gic_email_intel/core/s3_client.py`** — `download_attachment(storage_path)` is the function `_build_eml` will inject as `_download`.

For Sibling 4 (backfill — after Sibling 3 merges):
- **`unisoft-proxy/client/cli.py`** — `attachment upload`, `attachment delete`, `attachment list` commands. Backfill uploads new .eml, verifies, deletes old.
- **`scripts/`** directory — Sibling 4 adds `backfill_eml_uploads.py`.

### Layer 5 — Unisoft API research (only if you hit Unisoft surface)

Sibling 4 (backfill) calls `attachment upload/list/delete`, which go through Unisoft. If you hit anything weird:

- **`projects/gic-email-intelligence/research/unisoft-api/operations-index.md`** — 89 captured SOAP operations + 19 REST endpoints (on `os-unisoft` branch worktree).
- **`projects/gic-email-intelligence/research/unisoft-api/wsdl-complete.md`** — full Unisoft API extraction. 40k lines, use grep to find specific entities.
- **`projects/gic-email-intelligence/research/unisoft-api/raw-payloads/soap/IINSFileService__*.txt`** — captured SOAP payloads for the file service (attachments). Authoritative wire format.

Siblings 1, 2, 3 do not hit Unisoft directly — skip Layer 5 for those.

---

## Mental model (internalize these — the system isn't going to teach you twice)

**Pipeline:**
```
Outlook (Microsoft Graph)
  → sync cron               (every 5min)   → MongoDB emails collection
  → processing cron         (every 5min)   → LLM classifier + extractor
                                           → submissions / quotes denormalized
  → automation cron         (every 15min)  → deepagent + Unisoft CLI
                                           → Unisoft Quote created
                                           → activity + notification email to agent
```

Sibling 2 tightens the first two intervals (sync 60s, processing 120s) AND adds an agent-submission claim at sync time so the email gets folder-moved into "Indemn - Processing" before the processing cron picks it up. This visibly speeds up "I sent it; the system saw it" feedback for JC + Maribel watching the inbox.

**Classification (Rule 7 is critical):**
- `gic_application` = has a Unisoft Quote ID already. Only Boats/Yachts, WC, Welders, Caterers come in this way (internal portal-issued).
- `agent_submission` = new business from an agent (everything else: HandyPerson, Rental Dwelling, contractor GL, restaurant GL, GL+CP, etc.).
- `usli_quote` / `usli_pending` / `usli_decline` = USLI carrier responses.
- Folder routing: Inbox → Indemn-Processing (on classification) → indemn processed (success) / Duplicates (dup detected) / Inbox (failure).

Sibling 2's claim-on-sync heuristic decides "this looks like an agent_submission" without an LLM call, then folder-moves at sync time. Sibling 2 must NOT misclassify (no false positives that move USLI emails to Processing) — see the test cases in the implementation plan.

**Multi-LOB:** one email = one quote, even if multiple LOBs in the submission. GL+CP → CP/PK (Package), restaurant GL → CG/HM, contractor GL → CG/AC. Rule lives in the create-quote-id skill (where Sibling 1 also touches the task subject).

**DTO discipline (Unisoft):** Always populate ALL schema fields, even with nil defaults. Partial DTOs cause silent server-side data loss. This was the cause of the notification-delivery bug in 2026-04-24 (Activity DTO missing fields → empty Notification). **Sibling 4 will need this same discipline** when calling `attachment upload` if it touches any DTO directly. The existing CLI handles it; just don't bypass.

**Attachment upload pattern:** Unisoft's Azure App Service has a ~1.5MB ceiling for buffered uploads. We bypass WCF entirely with custom `HttpWebRequest` + `SendChunked=true` + manually-built MTOM/XOP multipart. Already in the proxy. **Sibling 4's backfill should use the existing `unisoft attachment upload` CLI** — don't reinvent.

**LLM caveats (relevant to skill changes in Sibling 1):**
- Skills must be **inlined in the system prompt**, not loaded as flat files — `deepagents`' SkillsMiddleware doesn't currently work for our shape.
- `_load_skill` does `.format()` substitution on placeholders like `{graph_user_email}` in the skill markdown. Other curly braces in the file (e.g., `{INSURED_NAME}` placeholders the LLM fills in) are written as `{{INSURED_NAME}}`. Don't break this if you edit the skill.
- All LLM calls run on Gemini 2.5 Pro/Flash via Vertex AI.

**Mongo DB topology (post-cutover):**
- dev-services EC2 (`i-0fde0af9d216e9182`) → `gic_email_intelligence_devsoak` database. SOAK_MODE=true. Use this for testing.
- prod-services EC2 (`i-00ef8e2bfa651aaa8`) → `gic_email_intelligence` database. **Do not write here without approval.**
- Same Atlas cluster (`dev-indemn-pl-0`), different DBs.
- Customer Outlook inbox is shared between envs — **SOAK_MODE on dev is what keeps dev from clobbering prod.**

---

## Stakeholders

| Person | Role | What they care about |
|---|---|---|
| **JC** (jcdp@gicunderwriters.com) | Head of underwriting at GIC | Ergonomic queue. Approved USLI scope 2026-04-30. He asked for these three siblings. |
| **Maribel** | Underwriter using Outlook add-in | Detail-oriented. Surfaced the LOB-prefixed task title and the .eml-with-attachments asks. |
| **Dhruv** (Indemn) | DevOps engineer | SOC 2 / Datadog. PR reviewer. |
| **Dolly, Rudra** (Indemn) | Engineers | Frequent PR reviewers. |
| **Craig** | You're working with him | The CTO; will give you direction at every approval gate. He's pivoted from USLI to siblings to deliver these directly. |

---

## Hard rules (read before touching anything)

- **No merges to `indemn-ai/gic-email-intelligence:main`** without PR review (Dolly + Dhruv typically). Branch protection is on.
- **Sibling 2 does NOT merge before DEVOPS-158 closes.** Check status with `linearis-proxy.sh issues list --filter '{"id":{"eq":"DEVOPS-158"}}' --json | jq -r '.[].state'` — must be "Done" before pushing Sibling 2 to main. The cron interval change would invalidate ongoing prod soak observations.
- **Test in dev-services EC2** for new feature work — runs against `gic_email_intelligence_devsoak` Mongo + UAT Unisoft. SOAK_MODE prevents Outlook folder changes and real agent emails. Safe sandbox.
- **Production safety**: any prod-Param-Store, prod-EC2 mutation, prod folder creation, or prod cron unpause is `[NEEDS USER APPROVAL]` per the OS production-safety rule.
- **Don't touch `feat/usli-quote-automation`.** That branch is paused on the search blocker (see Layer 1 reading). Your siblings branch off `indemn/main`, NOT off the USLI feature branch.
- **Sibling 4 backfill is `[NEEDS USER APPROVAL]` end-to-end.** Even when you've built it, don't run live without Craig's go-ahead.
- **No `--no-verify` on commits.** No `--force-push` to main or prod branches.

---

## File overlap awareness

Three files are touched by both siblings AND the paused USLI feature branch. Be aware:

- `unisoft-proxy/client/cli.py` — modified by Sibling 1 AND USLI Phase C. Both add new code, low textual conflict, but rebase Sibling 1 last to be safe.
- `docker-compose.yml` — modified by Sibling 2 (cron intervals) AND USLI Phase G.0 (new `automation-usli-cron` container). **Direct conflict risk** — recommend Sibling 2 lands first, USLI G.0 rebases on it.
- `src/gic_email_intel/cli/commands/emails.py` — modified by Sibling 3 (export) AND USLI Phase C.4 (helper generalization). Different functions, low conflict.

**Recommended overall merge order:** Sibling 2 → Sibling 1 → Sibling 3 → USLI feature → Sibling 4.

---

## Git layout

**Repos:**
- `gic-email-intelligence-migration/` — mainline checkout. Use this for `git fetch indemn` operations.
- `gic-email-intelligence-usli/` — the active (paused) USLI feature worktree. **Don't touch.**
- New sibling worktrees you'll create off `indemn/main` (NOT off the USLI branch):

```bash
cd /Users/home/Repositories/gic-email-intelligence-migration
git fetch indemn

# Sibling 1
git worktree add ../gic-eml-sibling-1 -b fix/devops-163 indemn/main
# Sibling 3
git worktree add ../gic-eml-sibling-3 -b fix/devops-165 indemn/main

# After DEVOPS-158 closes:
git worktree add ../gic-eml-sibling-2 -b fix/devops-164 indemn/main

# After Sibling 3 merges:
git worktree add ../gic-eml-sibling-4 -b fix/devops-165-backfill indemn/main
```

**Remotes in the migration repo:**
- `indemn` → `indemn-ai/gic-email-intelligence` (the active prod repo — branch from here)
- `origin` → `craig-indemn/gic-email-intelligence` (legacy fork, frozen — do not use)

**OS repo (where this handoff lives):**
- Worktree: `/Users/home/Repositories/operating-system/.claude/worktrees/gic-feature-scoping/`
- Branch: `os-gic-feature-scoping`

---

## Conventions

- **Commit style:** `feat(scope): ...`, `fix(scope): ...`, `test: ...`. See `git log --oneline` in any worktree for examples.
- **PR style:** Summary, Test plan. Reference templates: PR #18 (SOAK_MODE) and PR #19 (Datadog).
- **Reviewers:** Dolly + Dhruv on most PRs. Add via `gh pr edit <num> --repo indemn-ai/gic-email-intelligence --add-reviewer dolly45,dhruvrajkotia`.
- **Linear:** parent epic DEVOPS-151. Sub-issues 162-165 already created. Link your PR to the right ticket.
- **TDD discipline:** the implementation plan's sibling sections are written as failing-test → implement → test passes → commit. Follow that structure exactly.
- **Test pattern:** mock-first; UAT smoke tests behind `@pytest.mark.uat` (excluded from default pytest runs); CliRunner for Typer commands. The conftest.py shim added for the USLI work (`from cli import app` works) is on `feat/usli-quote-automation` only — your sibling branches off `indemn/main` won't have it; don't depend on it.

---

## Skills you'll likely use

- **`superpowers:executing-plans`** — the implementation plan's sibling sections are written for this. Loads the plan, executes in batches with checkpoints. **Start here.**
- **`/beads`** — task tracker if you want it for sub-tasks within a sibling.
- **`/linear`** — for ticket updates as you complete sub-tasks. `linearis-proxy.sh issues read DEVOPS-163` etc.
- **`/postgres`**, **`/mongodb`** — only if you need to query data (Sibling 3 can use Mongo to find a real email with attachments to test against).
- **`/aws`** — for SSM into dev-services for any UAT-side testing.
- **`/github`** — `gh` CLI for PR creation.

---

## Your first response to Craig (when starting the new session)

After you've absorbed everything:

1. **Confirm context** with a one-paragraph summary back to Craig — what the project is, where it's at, which sibling you're starting with and why. Mention 2–3 specific things you internalized from the reading list (e.g., "I see Rule 7 distinguishes gic_application from agent_submission" or "I noted the file-overlap risk between Sibling 2's docker-compose change and the paused USLI Phase G.0"). This shows you actually read it.

2. **Pick the sibling** based on what's unblocked:
   - **Sibling 2 is blocked** until DEVOPS-158 closes (~2026-05-06) — don't start it yet.
   - **Sibling 1 (task subject) and Sibling 3 (.eml attachments)** are unblocked and can ship in parallel. They touch different files.
   - **Sibling 4 (backfill) is blocked** until Sibling 3 merges.
   - Recommended order: Sibling 1 first (smaller, less risky), then Sibling 3.

3. **Use `superpowers:executing-plans`** — load the implementation plan's relevant sibling section, execute task-by-task with the failing-test-first discipline.

4. Don't bundle siblings into one PR — each is a separate PR per the plan.

5. **For Sibling 4 (backfill):** when you get there, present the dry-run output to Craig BEFORE running live. `[NEEDS USER APPROVAL]` end-to-end.

---

## What's NOT your job

- USLI feature build — paused on the search blocker. See `2026-04-30-unisoft-quote-search-investigation.md`.
- Quote-search investigation — paused, awaiting fresh Fiddler SAZ from Craig.
- Anything beyond the four siblings listed above.

If something cross-cuts (e.g., Sibling 2's `docker-compose.yml` change conflicts with the paused USLI's planned `automation-usli-cron` container), flag it to Craig — don't try to merge the two streams.

Welcome. Read everything, then ship.
