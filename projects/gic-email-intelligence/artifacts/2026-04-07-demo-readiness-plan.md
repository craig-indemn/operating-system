---
ask: "Plan to get GIC email intelligence demo-ready — reliable end-to-end pipeline, AMS linkage, UI clarity"
created: 2026-04-07
workstream: gic-email-intelligence
session: 2026-04-07a
sources:
  - type: mongodb
    description: "Pipeline status analysis — email types, automation results, failure reasons, linkage gaps"
  - type: codebase
    description: "Processing pipeline code (harness.py, extractor.py, ams_link.py, automation agent)"
---

# Demo Readiness Plan — GIC Email Intelligence

**Date:** 2026-04-07
**Objective:** Get the GIC email intelligence system demo-ready for customer presentation. The system must reliably process emails end-to-end from Outlook inbox to Unisoft AMS, with clear UI visibility into every step.

## Demo Story

"We connected your Outlook inbox to your Unisoft AMS. New applications are automatically processed and entered into Unisoft. Here's the pipeline running live, here's what it's doing, here are the results, and here's our plan to bring this to production."

## Success Criteria

1. **Automation running reliably in dev** — connected to `quote@gicunderwriters.com` inbox and Unisoft UAT, processing new emails automatically
2. **Every automation failure is a legitimate business gap** — not a software bug. Agency not in Unisoft = expected. Software error = not acceptable.
3. **All linkable data is linked** — portal submissions, carrier responses inheriting parent Quote IDs, not just agent_submission automation
4. **UI clearly shows processing status** — what's been processed, what failed and why, what's linked to AMS
5. **Demo narrative prepared** — showcase of work done, questions for JC, production roadmap
6. **No ad-hoc processing** — all data processing runs through the same pipeline/cron that handles new emails. Historical reprocessing uses the same code path.

## Current State (2026-04-07)

### Email Volume
| Type | Count | Description |
|------|-------|-------------|
| `usli_quote` | 2,623 | USLI carrier quote responses |
| `usli_pending` / `usli_decline` | 596 | USLI status updates |
| `agent_submission` | 183 | New applications from retail agents — **primary automation target** |
| `agent_reply` / `agent_followup` | 200 | Agent correspondence |
| `gic_portal_submission` | 47 | Applications via Unisoft online portal |
| `gic_application` | 28 | Applications via Granada portal |
| Other (reports, internal, hiscox, etc.) | ~164 | Various |
| **Total** | **3,841** | |

### Automation Results (agent_submission)
| Status | Count | Rate |
|--------|-------|------|
| Completed | 108 | 59% |
| Failed | 71 | 39% |
| In progress | 2 | 1% |
| Not started | 2 | 1% |

### AMS Linkage
| Source | Count | Method |
|--------|-------|--------|
| Automation (deepagent created Quote ID) | 28 | `automation_result.unisoft_quote_id` |
| Portal (reference number in subject) | 15 | `classification.reference_numbers` validated via `GetQuote` |
| **Total linked** | **43** | |
| **Unlinked with potential** | **~2,700+** | Carrier responses, more portal subs, Granada |

### Pipeline Infrastructure
- **Sync cron**: Every 5 min, pulls from Outlook via MS Graph API
- **Processing cron**: Every 5 min, runs extract → classify → link
- **Automation cron**: Every 15 min, runs deepagent on `agent_submission` emails
- **Form extractor**: Fixed (WAF allowlist + MongoDB URI). Primary extraction method for all PDFs.
- **Rate limit handling**: Retry with exponential backoff on all LLM calls (4 retries, 5-40s)

## Plan

### Workstream 1: Validate Automation Reliability

**Goal:** Confirm every automation failure is a legitimate business gap, not a software bug.

**Principle:** No ad-hoc verification. Build the verification into the pipeline so it runs on every new email too.

#### 1a. Agency verification via API
Systematically verify each of the 71 failed agencies against Unisoft using the API (`SearchAgents`, `GetAgentsByName`). This should be a pipeline capability, not a one-time script — the automation agent already searches for agencies, but the failure investigation needs to confirm the search was thorough.

**Approach:**
- Query Unisoft API for each failed agency name with multiple search strategies (exact, partial, DBA name, producer code)
- Document results: truly missing vs found under different name vs search bug
- If search logic is insufficient, fix it in the automation skill (`create-quote-id.md`)
- Add the verified results to a "agency verification" artifact

**Outcome:** A definitive list split into:
- Agencies confirmed not in Unisoft (question for JC: add them or flag for manual?)
- Agencies that exist but agent couldn't find (fix the matching logic)

#### 1b. Reprocess failed emails through the standard pipeline
Any emails that failed due to software bugs (not business gaps) should be reset to `pending` and reprocessed through the normal processing + automation cron. No special reprocessing scripts — the cron picks them up naturally.

### Workstream 2: Maximize AMS Linkage

**Goal:** Link every email that CAN be linked to a Unisoft Quote ID, without wasting LLM compute.

**Principle:** The linkage logic runs in the pipeline, not as backfill scripts. The `resolve_quote_id()` function and the cron are the mechanisms.

#### 2a. Portal submissions (47 emails, 18 more linkable)
The `resolve_quote_id()` function already handles portal submissions — checks `classification.reference_numbers`, validates via `GetQuote`. 15 are linked, 18 more have reference numbers.

**Action:** Debug why the 18 didn't link during backfill. Likely: the reference number failed `GetQuote` validation (Quote ID doesn't exist in Unisoft UAT, or it's a different number format). Fix the resolution logic if needed, then rerun backfill through the standard CLI.

#### 2b. Carrier response inheritance (2,623+ USLI emails)
USLI/Hiscox emails are carrier responses TO submissions that may already have Quote IDs. The carrier response doesn't need its own Quote ID — it should inherit the parent submission's linkage.

**Key insight from Craig:** Don't burn LLM compute extracting data from carrier emails if the data is already in Unisoft. Focus compute on emails that NEED processing (new applications).

**Action:** The submission already groups emails. If a submission has a Quote ID (from any source), ALL emails in that submission inherit the AMS linkage. This is already how the UI works (ApplicantPanel shows AMS data for the submission, not per-email). No new code needed — the AMS data endpoint already works at the submission level.

**What IS needed:** Ensure the processing pipeline doesn't waste extraction tokens on carrier response emails where we already have the data. Add a pipeline optimization: for `usli_quote`, `usli_pending`, `usli_decline`, `hiscox_quote` types, skip LLM extraction if the parent submission already has a Quote ID — the authoritative data is in Unisoft.

#### 2c. Granada portal applications (28 emails)
These come from `quotes@granadainsurance.com`. They're a different entry path — Granada is a sister company. Currently not linked because there's no automation path.

**Action:** Deferred to future iteration. Requires Unisoft name search (`GetQuotesByName2`) which involves fuzzy matching. Not needed for the demo — focus on the reliable paths first.

### Workstream 3: UI Clarity

**Goal:** The UI should clearly show the processing status and AMS linkage for every applicant.

#### 3a. Processing status visibility
Add a way to see in the queue which applicants have been fully processed vs partially processed vs failed. This could be:
- A "Processing" column or indicator
- Color coding on the existing AMS column
- A filter for "needs attention" (failed processing)

#### 3b. Failure reasons in queue
The AutomationBanner shows failure reasons in the detail view, but the queue doesn't surface them. For the demo, you should be able to see at a glance which applicants failed and why.

#### 3c. Email type visibility
Different email types should be clearly distinguishable. The queue currently shows LOB but not email type. For the demo, being able to filter by "new applications" vs "carrier responses" vs "agent correspondence" would help tell the story.

### Workstream 4: Demo Preparation

**Goal:** Narrative, questions for JC, production roadmap.

- **Demo script:** Walk through the pipeline live — show a recent email, show it being processed, show the Unisoft record
- **Questions for JC:**
  - Missing agencies: should we create them automatically or flag for manual entry?
  - Portal Quote ID confirmation: are reference numbers in `gic_portal_submission` subjects always Unisoft Quote IDs?
  - Production readiness: what's needed to move from UAT to production Unisoft?
  - Agency creation policy: who manages the Unisoft agent registry?
- **Production roadmap:** What the path looks like from dev/UAT to production (infrastructure, credentials, testing, rollout)

## Priority Order

1. **Agency verification** (Workstream 1a) — highest leverage, validates or invalidates the automation
2. **Pipeline optimization** (Workstream 2b) — skip unnecessary LLM processing for carrier emails
3. **Portal linkage** (Workstream 2a) — quick win, links 18+ more submissions
4. **UI clarity** (Workstream 3) — make the data story visible
5. **Demo prep** (Workstream 4) — narrative and materials

## Design Principle: No Ad-Hoc Processing

All processing must flow through the standard pipeline:
- **New emails:** Sync cron → Processing cron (extract → classify → link) → Automation cron
- **Reprocessing:** Reset email `processing_status` to `pending` → Processing cron picks it up naturally
- **Backfill:** Uses the same `resolve_quote_id()` function, invoked via CLI but running the same code
- **No one-time scripts** that bypass the pipeline. If we need new behavior, it goes into the pipeline code and runs for all emails going forward.
