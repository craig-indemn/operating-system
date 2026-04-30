---
ask: "Hydrate a fresh feature-scoping session with comprehensive project context — built mid-cutover so the session has everything needed to brainstorm new automation features without rediscovering what exists."
created: 2026-04-29
workstream: gic-email-intelligence
session: 2026-04-29-a
sources:
  - type: artifacts
    description: "Curated reading list across current state, architecture, data model, migration, and stakeholder context"
  - type: codebase
    description: "Pointers into gic-email-intelligence-migration repo for ground-truth reading after the design docs"
---

# Feature-Scoping Handoff — GIC Email Intelligence

You're a fresh Claude session joining the **GIC Email Intelligence** project to scope a **new automation feature**. Craig will describe the feature after you finish hydrating context.

**Do NOT start brainstorming or writing code until Craig presents the problem.** Read everything first. Build a complete mental model. Then wait.

---

## What this project is (one paragraph)

GIC Underwriters is an MGA (managing general agent) for commercial insurance. Their `quote@gicunderwriters.com` inbox receives ~50 submissions/day from agents — a mix of new business applications, quote requests, follow-ups, and portal acknowledgments. We've built an end-to-end pipeline that ingests these emails, classifies them, extracts submission data (PDF parsing of ACORD forms, contact info, agency lookup), and creates Quotes in **Unisoft** (their AMS) with attachments and notification emails — all autonomously, with deterministic fallbacks for the parts that LLMs can't be trusted to do reliably. The system has been live in production since 2026-04-23 and is processing real submissions for JC and Maribel today.

## Where we are right now (2026-04-29)

**Cutover day.** Production is migrating from Railway → AWS EC2 (`prod-services`, `i-00ef8e2bfa651aaa8`) at 5 PM ET today. The cutover infrastructure is built (ALB `prod-gic-email-intelligence`, ACM cert for `api.gic.indemn.ai`, Route 53 alias all live; backend container will start when the prod branch is pushed during the cutover window). A separate Claude session (`gic-cutover-execution`) is handling the actual cutover.

**Your job is parallel feature work** — design a new automation feature that will:
- Build on top of the existing pipeline
- Be testable in **dev-services EC2** (the future prod infrastructure) or Railway dev (legacy, sunsetting)
- Land **after** cutover + 24h soak passes (earliest = Thursday 2026-04-30 morning)

---

## Reading list (in order)

Read these in order. Take notes — you'll need to remember a lot of moving parts. Total reading: ~1.5 hours if thorough, ~45 min if you skim Layer 4.

### Layer 1 — Current state (~15 min)

1. **`projects/gic-email-intelligence/INDEX.md`** — the resume map. Status, key code files, immediate priorities, recent work, gotchas.
2. **`projects/gic-email-intelligence/artifacts/2026-04-28-phase-i-cutover-readiness.md`** — today's cutover-day runbook + state snapshot.
3. **`projects/gic-email-intelligence/artifacts/2026-04-28-phase-g-soak-handoff.md`** — Phase G validation outcome (5 successful UAT Quote creations) + issues fixed during F + G.

### Layer 2 — How the system works (~30 min)

4. **`projects/gic-email-intelligence/artifacts/2026-03-30-pipeline-architecture-review.md`** — pipeline stages: sync → process → automation. Cron-based, MongoDB-backed.
5. **`projects/gic-email-intelligence/artifacts/2026-03-24-data-model-redesign.md`** — emails, submissions, quotes, automations, agencies, contacts. Critical for any feature touching the data layer. Long but worth it.
6. **`projects/gic-email-intelligence/artifacts/2026-04-23-go-live-day-session-2.md`** — classification rules (Rule 7), multi-LOB handling, deterministic activity + notification pattern, ObjectId corruption recovery, duplicate routing.
7. **`projects/gic-email-intelligence/artifacts/2026-04-24-upload-bypass-and-notification-fixes.md`** — Unisoft DTO conventions (full-fields-required pattern), MTOM/XOP chunked attachment uploads, `SendActivityEmail` on `IEmailService`.

### Layer 3 — Migration context (~15 min, skim)

8. **`projects/gic-email-intelligence/artifacts/2026-04-27-migration-implementation-plan.md`** — skim. Phases A through J. We're at Phase I (cutover today). J is 7-day soak. Tear-down of Railway after.
9. **`projects/gic-email-intelligence/artifacts/2026-04-27-migration-to-indemn-infrastructure-design.md`** — skim. Why we're moving (Railway → AWS), risk table, architecture diagrams.
10. **`projects/gic-email-intelligence/artifacts/2026-04-27-phase-e-execution-handoff.md`** — AWS infra (Secrets Manager, Param Store, IAM, OIDC) for context on how dev-services and prod-services are configured.

### Layer 4 — Specific subsystems (read if relevant to Craig's feature)

11. **Outlook add-in:** `projects/gic-email-intelligence/artifacts/2026-03-19-outlook-addin-design.md` — sidebar UI for Maribel; calls `/api/lookup-email` on the FastAPI backend.
12. **Unisoft REST proxy:** `projects/gic-email-intelligence/artifacts/2026-04-01-unisoft-rest-proxy-design.md` — SOAP-to-REST proxy on Windows EC2 (`i-0dc2563c9bc92aa0e`), maps Unisoft's WCF API to JSON for the Python pipeline.
13. **Intake Manager integration:** `projects/gic-email-intelligence/artifacts/2026-03-23-intake-manager-integration-analysis.md` — the original web-based intake system we evaluated.
14. **Demo briefing:** `projects/gic-email-intelligence/artifacts/2026-04-13-gic-demo-briefing.md` — short narrative summary of the system pre-go-live.

### Layer 5 — Code (the source of truth)

After the docs, browse these files in `gic-email-intelligence-migration/` (added via `--add-dir`):

- **`src/gic_email_intel/agent/harness.py`** — pipeline orchestrator + classification rules (including Rule 7).
- **`src/gic_email_intel/automation/agent.py`** — deepagent system prompt + tools registration (the automation brain).
- **`src/gic_email_intel/automation/skills/create-quote-id.md`** — automation skill (multi-LOB rules, contact lookup, applicant email).
- **`src/gic_email_intel/agent/skills/submission_linker.md`** — linker (single submission for multi-LOB).
- **`src/gic_email_intel/cli/commands/emails.py`** — `gic emails complete` (deterministic activity + notification, duplicate detection, folder routing).
- **`src/gic_email_intel/core/email_mover.py`** — Outlook folder move helper.
- **`src/gic_email_intel/agent/tools.py`** — agent toolset, includes `_safe_object_id()` for LLM hex corruption recovery.
- **`unisoft-proxy/client/cli.py`** — Unisoft CLI (contacts, quote create, attachment upload/delete).
- **`unisoft-proxy/server/UniProxy.cs`** — SOAP proxy on EC2, includes the chunked MTOM upload path.
- **`docker-compose.yml`** — service topology (api, sync-cron, processing-cron, automation-cron). Note: shared-datadog network + DD env wiring just landed in PR #19.

---

## Mental model (internalize these)

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

**Classification (Rule 7 is critical):**
- `gic_application` = has a Unisoft Quote ID already. Only Boats/Yachts, WC, Welders, Caterers come in this way (internal portal-issued).
- `agent_submission` = new business from an agent (everything else: HandyPerson, Rental Dwelling, contractor GL, restaurant GL, GL+CP, etc.).
- Folder routing: Inbox → Indemn-Processing (on classification) → indemn processed (success) / Duplicates (dup detected) / Inbox (failure).

**Multi-LOB:** one email = one quote, even if multiple LOBs in the submission. GL+CP → CP/PK (Package), restaurant GL → CG/HM, contractor GL → CG/AC.

**DTO discipline (Unisoft):** Always populate ALL schema fields, even with nil defaults. Partial DTOs cause silent server-side data loss. This bit us with ActivityDTO AND the nested NotificationDTO. Same lesson likely applies to any new Unisoft API integration.

**Notification pattern:** `SendActivityEmail` on `IEmailService` is the actual email sender. `SetActivity` alone does NOT send email. The agent uses a 2-call workflow. Plain HTTPS transport security on this service (NOT WS-Security like the main API).

**Attachment upload pattern:** Unisoft's Azure App Service has a ~1.5MB ceiling for buffered uploads. We bypass WCF entirely with custom `HttpWebRequest` + `SendChunked=true` + manually-built MTOM/XOP multipart. See `2026-04-24-upload-bypass-and-notification-fixes.md`.

**LLM caveats:**
- LLMs corrupt hex strings (Mongo ObjectIds) by mis-reading characters. `_safe_object_id()` tries 16 variants to recover.
- Skills must be **inlined in the system prompt**, not loaded as flat files — `deepagents`' SkillsMiddleware doesn't currently work for our shape.
- All LLM calls run on Gemini 2.5 Pro/Flash via Vertex AI (Anthropic credit was depleted earlier in April).

---

## Stakeholders

| Person | Role | What they care about |
|---|---|---|
| **JC** (jcdp@gicunderwriters.com) | Head of underwriting at GIC | Daily queue / backfill updates. Trusts the system. Will request retroactive runs of pipeline steps. |
| **Maribel** | Underwriter using Outlook add-in | Detail-oriented. Recently asked for: LOB-prefixed task titles, attachments-with-body uploads, USLI quote retailer-contact handling. |
| **Dhruv** (Indemn) | DevOps engineer | SOC 2 / Oneleet / WAF / Datadog. Asked for Datadog wiring → PR #19 just opened. |
| **Dolly, Rudra** (Indemn) | Engineers | Frequent PR reviewers — both approved PR #18. |
| **Craig** | You're working with him | The CTO; will give you the feature problem after this handoff. |

---

## Hard rules (cutover-related)

- **No merges to `indemn-ai/gic-email-intelligence:main`** between 4:30 PM ET and 9:30 PM ET today. Cutover window — keep moving parts to a minimum.
- **No deploys to prod-services EC2** until cutover passes + 24h soak completes (Thursday 2026-04-30 morning earliest).
- **Test in dev-services EC2** for new feature work — it matches the future prod infrastructure exactly (Atlas PrivateLink, shared-dd-agent, same docker-compose). Railway dev still works but is sunsetting.
- **Branch from `indemn/main`** (post-PR #18 = commit `dd579f9`, plus PR #19 once merged).
- **Coordinate with the cutover session** if your feature touches sync / processing / automation / agent harness — risk of merge conflicts.

## Git remotes in the migration repo

- `indemn` → `indemn-ai/gic-email-intelligence` (the active prod fork — branch from here)
- `origin` → `craig-indemn/gic-email-intelligence` (legacy fork, frozen — do not use)
- Branches: `main` (active), `prod` (protected, prod deploys only via PR), feature branches as needed.

## Conventions

- **Commit style:** `feat(scope): ...`, `fix(scope): ...`. See `git log --oneline` in the migration repo for examples.
- **PR style:** see PR #18 (SOAK_MODE) and PR #19 (Datadog) for templates — Summary, Test plan, sometimes a "Why this is a follow-on" section.
- **Reviewers:** Dolly + Dhruv on most PRs. Rudra sometimes. Add via `gh pr edit <num> --repo indemn-ai/gic-email-intelligence --add-reviewer dolly45,dhruvrajkotia`.
- **Linear:** parent epic DEVOPS-151. New feature work likely gets its own child ticket; ask Craig before creating.

## Skills you'll likely use

- **`superpowers:brainstorming`** — start here when Craig describes the feature. It's the right discipline for design work.
- **`superpowers:writing-plans`** — once design is locked, write a phase plan.
- **`/beads`** — task tracker for the work breakdown.
- **`/linear`** — for Linear ticket linking and updates.
- **`/postgres`** / **`/mongodb`** — if your feature needs to query existing data to inform the design (e.g., "how often does X happen in the email corpus").

---

## Your first response to Craig

After you've absorbed everything:

1. **Confirm context** with a one-paragraph summary back to Craig — what the project is, where we are, what your understanding is. Mention 2–3 specific things you internalized (e.g., "I see Rule 7 distinguishes gic_application from agent_submission" or "I noted the Unisoft DTO full-fields-required pattern from the 04-24 fixes"). This shows you actually read it.
2. **Then wait** for Craig to describe the feature problem. He explicitly said he'd "talk about the problem" after the handoff.
3. **When he does, invoke `superpowers:brainstorming`** before doing anything else.

Don't write code. Don't open PRs. Don't merge. Don't commit to anything with JC/Maribel without Craig's review. Brainstorm and design first; everything else after that.

Welcome to the project.
