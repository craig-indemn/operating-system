---
ask: "Self-contained handoff for a fresh session to deliver JC's three follow-up requests (DEVOPS-163 task subject format, DEVOPS-164 faster claim, DEVOPS-165 .eml inline attachments). Independent of the USLI feature build, which is paused on a separate blocker."
created: 2026-04-30
workstream: gic-email-intelligence
session: 2026-04-30-jc-followups-handoff
sources:
  - type: artifacts
    description: "Implementation plan 2026-04-29-usli-quote-automation-implementation-plan.md — Sibling PR sections starting line ~1798"
  - type: linear
    description: "DEVOPS-163, DEVOPS-164, DEVOPS-165 (already created under DEVOPS-151)"
  - type: codebase
    description: "Pointers into gic-email-intelligence-usli/ for the files each sibling touches"
---

# JC Follow-Ups — Handoff

You're a fresh Claude Code session. Your job is to ship the three sibling PRs JC asked for. These are independent of the USLI quote automation feature (which is paused on an unrelated blocker — see `2026-04-30-unisoft-quote-search-investigation.md`).

**Read this whole doc, then read the implementation plan section linked below for each sibling. Don't write code until you've read the plan section for whichever sibling you're starting with.**

## What you're delivering

| # | Linear | Title | Gates on |
|---|---|---|---|
| Sibling 1 | DEVOPS-163 | Task subject format → `[LOB] - Business description` | — (ship anytime) |
| Sibling 2 | DEVOPS-164 | Faster claim into "Indemn - Processing" folder | **DEVOPS-158 (7-day soak) closing — target ~2026-05-06.** Don't merge before that. |
| Sibling 3 | DEVOPS-165 | `.eml` export includes attachments inline | — (ship anytime) |
| Sibling 4 | DEVOPS-165 backfill | Backfill historical `.eml` uploads | Sibling 3 merged. **[NEEDS USER APPROVAL]** before running |

## Where the detailed task plans live

The implementation plan was written for these and includes failing tests, file lists, and step-by-step instructions for each:

`projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-implementation-plan.md`

- **Sibling 1** — section starts at "Sibling PR 1 — Task subject format" (search the doc for that header)
- **Sibling 2** — "Sibling PR 2 — Faster claim into Indemn - Processing"
- **Sibling 3** — "Sibling PR 3 — `.eml` export includes attachments inline"
- **Sibling 4** — "Sibling PR 4 — Backfill historical .eml uploads"

Each section has files-touched + failing tests + commit messages spelled out. Follow them.

## Project state — what's live, what's safe to touch

**Production:** EC2 prod-services (`i-00ef8e2bfa651aaa8`) behind ALB `api.gic.indemn.ai`. Live since 2026-04-29 ~22:50 UTC. **DEVOPS-158 7-day soak window is active until ~2026-05-06.** Sibling 2 specifically waits for this to close — the cron interval change would invalidate ongoing soak observations. Siblings 1 + 3 don't touch cron behavior, so they can ship at any time.

**Mongo topology (post-cutover):**
- dev-services EC2 (`i-0fde0af9d216e9182`) → `gic_email_intelligence_devsoak` DB. SOAK_MODE=true. Use this for testing.
- prod-services EC2 (`i-00ef8e2bfa651aaa8`) → `gic_email_intelligence` DB. **Do not write here without approval.**
- Same Atlas cluster (`dev-indemn-pl-0`), different DBs.

**Active feature branches:**
- `feat/usli-quote-automation` on `indemn-ai/gic-email-intelligence` — paused, not your concern.
- Sibling worktrees should be created off `indemn/main`, NOT off the USLI feature branch (per the implementation plan's "Sibling worktree setup" section).

**Sibling worktree setup commands** (from the implementation plan):

```bash
cd /Users/home/Repositories/gic-email-intelligence-migration
git fetch indemn

git worktree add ../gic-eml-sibling-1 -b fix/devops-163 indemn/main
git worktree add ../gic-eml-sibling-3 -b fix/devops-165 indemn/main

# After DEVOPS-158 closes:
git worktree add ../gic-eml-sibling-2 -b fix/devops-164 indemn/main

# After Sibling 3 merges:
git worktree add ../gic-eml-sibling-4 -b fix/devops-165-backfill indemn/main
```

## Files each sibling touches (sanity check)

Per the implementation plan and code state in `gic-email-intelligence-usli` (which mirrors `indemn/main` structure):

- **Sibling 1 (DEVOPS-163):** `unisoft-proxy/client/cli.py` (add `_format_task_subject` next to existing `_truncate_subject`, accept `--business-description` on `task create`); `src/gic_email_intel/automation/skills/create-quote-id.md` (Step 6 update); new `tests/test_task_subject_format.py`.
- **Sibling 2 (DEVOPS-164):** `docker-compose.yml` (cron intervals: sync 60s was 300s; processing 120s was 300s); `src/gic_email_intel/cli/commands/sync.py` (new `_is_likely_agent_submission` heuristic + claim-on-sync folder move); new `tests/test_sync_claim_on_arrival.py`.
- **Sibling 3 (DEVOPS-165):** `src/gic_email_intel/cli/commands/emails.py` (extract `_build_eml`, switch from `MIMEMultipart("alternative")` to `MIMEMultipart()` with attachment parts); new `tests/test_emails_export.py`.
- **Sibling 4:** new `scripts/backfill_eml_uploads.py` (upload-verify-delete with checkpointing).

## File overlap awareness (from the plan)

- `unisoft-proxy/client/cli.py` — modified by Sibling 1 AND USLI Phase C. Both add new code; low textual conflict.
- `docker-compose.yml` — modified by Sibling 2 AND USLI Phase G.0 (new automation-usli-cron container). **Direct conflict risk.** Recommended order: **Sibling 2 lands first, USLI G.0 rebases on it.**
- `src/gic_email_intel/cli/commands/emails.py` — modified by Sibling 3 AND USLI Phase C.4. Different functions; low conflict.

Recommended overall merge order: **Sibling 2 → Sibling 1 → Sibling 3 → USLI feature → Sibling 4**.

## Conventions

- **Commit style:** `feat(scope): ...`, `fix(scope): ...`, `test: ...`. See `git log --oneline` in any worktree for examples.
- **PR style:** Summary, Test plan. See PR #18 (SOAK_MODE) and PR #19 (Datadog) for templates.
- **Reviewers:** `dolly45` + `dhruvrajkotia` on most PRs. `gh pr edit <num> --repo indemn-ai/gic-email-intelligence --add-reviewer dolly45,dhruvrajkotia`.
- **TDD discipline:** failing test → implement → test passes → commit. The plan's task sections lay this out step-by-step.
- **Production safety:** Sibling 4 (backfill) is `[NEEDS USER APPROVAL]` end-to-end. Don't run live without Craig's go-ahead.

## Hard rules

- **Sibling 2 does NOT merge before DEVOPS-158 closes.** Check status with `linearis-proxy.sh issues list --filter '{"id":{"eq":"DEVOPS-158"}}' --json | jq -r '.[].state'` — must be "Done" before pushing Sibling 2 to main.
- **Don't touch `feat/usli-quote-automation`.** That branch is paused, not your work.
- **Test in dev-services EC2** — runs against `_devsoak` Mongo + UAT Unisoft. SOAK_MODE prevents Outlook folder changes and real agent emails. Safe sandbox.
- Per the OS production-safety rule: any prod EC2 mutation, prod cron change, or write to `indemn/prod/*` Param Store needs explicit approval first.

## Stakeholders (in case JC pings)

- **JC** (jcdp@gicunderwriters.com) — head of underwriting. He asked for these. Approved USLI feature scope on 2026-04-30.
- **Maribel** — underwriter, originally surfaced these specific items.
- **Dhruv** (Indemn) — DevOps, PR #19 reviewer.
- **Dolly, Rudra** (Indemn) — engineers, frequent PR reviewers.

## Skills you'll likely use

- **`superpowers:executing-plans`** — the implementation plan was written for this. Loads + executes in batches with checkpoints. Start here.
- **`/beads`** — task tracker if you want it.
- **`/linear`** — for Linear ticket updates (`linearis-proxy.sh issues read DEVOPS-163` etc.).
- **`/github`** — `gh` CLI for PR creation.

## First response when starting the new session

1. **Confirm context** — one paragraph back to Craig: which sibling you're starting with and why (if Sibling 2 is gated, start with Sibling 1 or 3). Mention 2 specific things from this handoff to prove you read it.
2. **Pick the sibling**, create the worktree, read its section in the implementation plan in full.
3. **Use `superpowers:executing-plans`** to drive task-by-task execution per the plan's structure.

Don't bundle siblings into one PR — each is a separate PR per the plan.

## What's not your job

- USLI feature build (paused — see `2026-04-30-unisoft-quote-search-investigation.md`).
- Quote-search investigation (paused, awaiting fresh Fiddler SAZ from Craig).
- Anything beyond the four siblings listed above.

Welcome. Pick a sibling and ship it.
