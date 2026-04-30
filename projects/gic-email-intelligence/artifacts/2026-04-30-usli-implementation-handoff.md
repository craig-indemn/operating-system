---
ask: "Hydrate a fresh Claude session to continue executing the USLI Quote Automation implementation. Replicates the 2026-04-29 feature-scoping handoff with progress updates — same structure, current state."
created: 2026-04-30
workstream: gic-email-intelligence
session: 2026-04-30-b
sources:
  - type: artifacts
    description: "Curated reading list — design doc, implementation plan, original feature-scoping handoff, USLI fixture findings"
  - type: codebase
    description: "Pointers into gic-email-intelligence-migration (mainline) AND gic-email-intelligence-usli (in-progress feature worktree)"
  - type: research
    description: "Unisoft API extraction at projects/gic-email-intelligence/research/unisoft-api/ on the os-unisoft branch (40k-line WSDL, captured SOAP payloads, operations index)"
---

# USLI Implementation Handoff — GIC Email Intelligence

You're a fresh Claude session continuing the **USLI Quote Automation** implementation for GIC. Brainstorming + design + plan are done and committed; **Phase A is complete, Phase B is partial.** A specific blocker surfaced in B.2 and Craig has resolved it (see the "Option A decision" section). Your job is to keep executing the implementation plan task-by-task.

**Do NOT start writing new code until you've absorbed the design + plan + Option A context.** Read everything first. Build a complete mental model. Then pick up where the prior session left off.

---

## What this project is (one paragraph)

GIC Underwriters is an MGA (managing general agent) for commercial insurance. Their `quote@gicunderwriters.com` inbox receives ~50 submissions/day from agents — a mix of new business applications, quote requests, follow-ups, and portal acknowledgments. We've built an end-to-end pipeline that ingests these emails, classifies them, extracts submission data (PDF parsing of ACORD forms, contact info, agency lookup), and creates Quotes in **Unisoft** (their AMS) with attachments and notification emails — all autonomously, with deterministic fallbacks for the parts that LLMs can't be trusted to do reliably. **The system has been live in production since 2026-04-23 and migrated to Indemn's EC2 infrastructure on 2026-04-29.** Your work extends it to handle USLI quote responses (the 80%+ slice of inbox volume that's currently classified but not acted on).

## Where we are right now (2026-04-30)

**Cutover succeeded 2026-04-29 ~22:50 UTC.** Production runs on EC2 prod-services (`i-00ef8e2bfa651aaa8`) behind ALB `api.gic.indemn.ai`. Real customer email Q:146697 (Crown Park) verified end-to-end through the new pipeline. **DEVOPS-158 7-day soak window is active** until approximately 2026-05-06.

**USLI feature build is mid-flight.**

- ✅ Brainstormed + designed (artifact `2026-04-29-usli-quote-automation-design.md`)
- ✅ Customer-facing scope email sent to JC; **JC approved**
- ✅ Implementation plan written, two rounds of parallel-subagent review applied (artifact `2026-04-29-usli-quote-automation-implementation-plan.md`)
- ✅ 4 Linear tickets created (DEVOPS-162 through DEVOPS-165 — see "Linear tickets" below)
- ✅ Phase A (Workspace + Linear + conftest) — DONE
- ✅ Phase B.1 (USLI Quote Follow-Up ActionId + LetterName) — DONE
- ⏸ Phase B.2 (Unisoft Quote search) — surfaced a hard blocker; **Craig picked Option A** to resolve it (see below)
- ⏳ Phases B.3–B.6 + C–H — TODO

**Active feature branch:** `feat/usli-quote-automation` on `indemn-ai/gic-email-intelligence`. **Active feature worktree:** `/Users/home/Repositories/gic-email-intelligence-usli/`. 5 commits ahead of `indemn/main`.

## Reading list (in order)

Read these in order. Total reading: ~1.5 hours if thorough, ~45 min if you focus on the post-04-29 deltas.

### Layer 0 — This handoff (you're here)

### Layer 1 — USLI feature primary docs (~30 min)

1. **`projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-design.md`** — the agreed design. Two-path-collapsed-into-one workflow, scope boundaries, decisions summary, build-time verification list. Read this before the plan.

2. **`projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-implementation-plan.md`** — the bite-sized execution plan. Phases A through K + four sibling PRs. Two rounds of review applied (codebase accuracy, Unisoft API accuracy, logical coherence + production safety, test design). Hard rules embedded throughout. Phase H gates on DEVOPS-158 closing.

3. **`projects/gic-email-intelligence/artifacts/2026-04-29-feature-scoping-handoff.md`** — the original handoff that hydrated the prior session. Comprehensive project context (architecture, migration, stakeholders). **Lower priority** for you since this handoff replicates the structure with current state — but it's the canonical reference for anything not covered here.

### Layer 2 — What was built / decided / discovered (~15 min)

4. **`tests/fixtures/usli_config.json`** in the feature worktree — empirical findings from Phase B.1 + B.2. Contains the chosen ActionId (67), LetterName ("USLI Quote"), proxy debug-endpoint deployment notes, and the B.2 finding that surfaced the blocker.

5. **The 5 commits on `feat/usli-quote-automation`** — see "Progress so far" section below for what each one does.

6. **`/api/soap_raw/<op>` proxy debug endpoint** — deployed to UAT proxy (port 5000) only. New code in `unisoft-proxy/server/UniProxy.cs` (commit `3143886`). Lets us inspect raw SOAP responses bypassing JSON translation. Use it to debug any Unisoft response shape questions.

### Layer 3 — Unisoft API research (~20 min, read selectively)

The previous session pulled comprehensive Unisoft API documentation. **It lives on the `os-unisoft` branch of the OS repo**, not on this branch. Access via:
- Worktree path: `/Users/home/Repositories/operating-system/.claude/worktrees/unisoft/projects/gic-email-intelligence/research/unisoft-api/`
- Or via git: `git show os-unisoft:projects/gic-email-intelligence/research/unisoft-api/<filename>`

Files there:
- **`operations-index.md`** — 89 captured SOAP operations + 19 REST endpoints from real Unisoft UI traffic. Start here.
- **`wsdl-complete.md`** (40k lines) — full Unisoft API extraction. 910 SOAP operations, all DTOs, every field type/required/nullable. Use grep to find specific entities (e.g., `grep -A30 "QuoteSearchCriteriaDTO"`).
- **`raw-payloads/soap/IIMSService__*.txt`** — captured SOAP request/response pairs from real Unisoft UI sessions. Authoritative source for "what does this operation actually look like on the wire?" Especially relevant: SetSubmission, SetActivity, GetSubmissions, GetQuoteActions, GetActionNotifications.
- **`imsservice_wsdl.xml`** — raw WSDL.

### Layer 4 — How the system works (~30 min, skim if you've read 04-29 handoff)

7. **`projects/gic-email-intelligence/artifacts/2026-03-30-pipeline-architecture-review.md`** — pipeline stages: sync → process → automation. Cron-based, MongoDB-backed.
8. **`projects/gic-email-intelligence/artifacts/2026-03-24-data-model-redesign.md`** — emails, submissions, quotes, automations, agencies, contacts. Critical for any feature touching the data layer.
9. **`projects/gic-email-intelligence/artifacts/2026-04-23-go-live-day-session-2.md`** — classification rules (Rule 7), multi-LOB handling, deterministic activity + notification pattern, ObjectId corruption recovery, duplicate routing.
10. **`projects/gic-email-intelligence/artifacts/2026-04-24-upload-bypass-and-notification-fixes.md`** — Unisoft DTO conventions (full-fields-required pattern), MTOM/XOP chunked attachment uploads, **`SendActivityEmail` on `IEmailService`** (the fact that `SetActivity` does NOT send email; you need both calls). Critical for understanding the activity flow.

### Layer 5 — Cutover post-mortem (~5 min, current state context)

11. **`projects/gic-email-intelligence/artifacts/2026-04-29-cutover-execution-handoff.md`** (on `os-unisoft` branch) — what shipped, what didn't, the lessons captured. Covers the Datadog PR #19 status, AUTOMATION_START_DATE filter, the 7-day soak gate (DEVOPS-158).

### Layer 6 — Code (the source of truth)

After the docs, browse these files in `gic-email-intelligence-usli/` (the feature worktree):

- **`src/gic_email_intel/agent/harness.py`** — pipeline orchestrator + classification rules (including Rule 7).
- **`src/gic_email_intel/automation/agent.py`** — deepagent system prompt + skill loading. Note `_load_skill` does `.format()` substitution; D.1 will extend it for the new placeholders.
- **`src/gic_email_intel/automation/skills/create-quote-id.md`** — the existing `agent_submission` skill. Mirror its structure for `process-usli-quote.md` in D.2.
- **`src/gic_email_intel/cli/commands/emails.py`** — `gic emails complete` (deterministic activity + notification, duplicate detection, folder routing). C.4 generalizes `_create_activity_and_notify` here.
- **`src/gic_email_intel/core/email_mover.py`** — Outlook folder move helper. E.1 factors `ensure_folder_exists` out of inline logic.
- **`src/gic_email_intel/agent/tools.py`** — agent toolset, includes `_safe_object_id()` for LLM hex corruption recovery.
- **`unisoft-proxy/client/cli.py`** — Unisoft CLI (contacts, quote create, attachment upload/delete). C.1/C.2/C.3 add commands here.
- **`unisoft-proxy/server/UniProxy.cs`** — SOAP proxy on EC2. Now includes `/api/soap_raw/<op>` from commit `3143886`.
- **`docker-compose.yml`** — service topology. G.0 adds `automation-usli-cron` here.

---

## Option A decision — what it means for the implementation

Phase B.2 surfaced a Unisoft-side limitation: **all quote-search operations return correct match counts but empty data arrays**. `GetQuotesByName2`, `GetQuotesForLookupByCriteria`, and `GetQuotes` all behave the same way — the proxy's WS-Security user can `GetQuote(QuoteID)` (returns full DTO) but cannot enumerate quotes via search.

The previous session presented four options for handling this. **Craig picked (A): JC provides the Quote ID for each USLI quote.** This dramatically simplifies the design — we don't need to search Unisoft from an email. We just need a way for JC to attach the Quote ID to the workflow.

### What Option A means for design changes

- **Drop Phase C.1 (`unisoft quote search --name` wrapper).** Not needed — there's no name-search step in the agent's flow.
- **Drop B.2's `quote_usli_ref_field` discovery.** Moot.
- **Add a new mechanism for JC to communicate the Quote ID.** The "what" is decided; the "how" is open. Plausible UX paths:
  - **(a1) JC includes the Unisoft Quote ID in the email subject when forwarding/replying.** The system parses it (regex) and uses it directly.
  - **(a2) JC marks the email with a specific Outlook category/flag** that the system reads to know "this one's ready, here's the Quote ID."
  - **(a3) An out-of-band lookup table** (Mongo collection or fixture) maintained by JC that maps insured-name patterns to Quote IDs.
  - **(a4) JC pastes the Quote ID into a Unisoft activity note** on the existing portal Quote, which the system polls.
- **Phase B.5 (the JC-confirmation task) becomes the first thing the next session does** — talk to Craig about which UX shape JC prefers, then update the design doc + plan accordingly.

### What stays the same

- Phase B.1 (ActionId + LetterName) — already done; values in fixture
- Phase B.3 (PDF version detection) — still needed
- Phase B.4 (BrokerId / CarrierNo) — still needed
- Phase B.6 (Settings + Param Store wiring for ActionId + LetterName) — still needed
- Phase C.2 (`unisoft submission create --confirmation-no` flag) — still needed
- Phase C.3 (`unisoft submission update`) — still needed
- Phase C.4 (`_create_activity_and_notify` generalization) — still needed
- Phase C.5/C.6 (idempotency + failure-mode tests) — still needed
- Phases D, E, G, H — workflow shape unchanged; just the lookup step changes

### Updates needed to plan + design before resuming

Before you start C-phase work, update both docs:

1. **Design doc**: change Phase 2 of the workflow ("Find the Quote in Unisoft") from "search by insured name" to "JC provides the Quote ID via {chosen UX}". Mark `quote_usli_ref_field` and the search-fallback as **explicitly deferred**.
2. **Plan**: drop C.1 entirely, drop B.2's deferred consumer (the `--confirmation-number` flag tasks), add a new B.7 for "agree on UX with JC", and adjust the skill outline in D.2 step 2.
3. **Commit the doc + plan updates as `docs(usli): pivot to Option A — JC provides Quote ID`**

---

## Progress so far on `feat/usli-quote-automation`

5 commits, 4 deploys, 1 proxy modification. All on the feature branch — nothing merged to `indemn/main` yet.

```
7c326c0 fixture: B.2 finding — Unisoft search ops return empty arrays
3143886 proxy: add /api/soap_raw/<op> debug endpoint (UAT-only deploy)
9f7e81d fixture: B.1 — USLI Quote ActionId + LetterName
2e86b78 test: add 'uat' marker, sys.path shim for unisoft-proxy/client, fixtures dir
c668a67 test: fix stale 'stage-detector' reference (renamed to situation-assessor)
```

### What each commit did

1. **`c668a67`** — Pre-existing test bug fix. `tests/test_agent_tools.py::test_skill_tool_map_has_all_skills` was asserting `'stage-detector'` in `SKILL_TOOL_MAP`, but that skill was renamed to `situation-assessor` in the 2026-03-24 data-model redesign. One-line fix; baseline now 120/120 unit tests passing on the feature branch. **Could be cherry-picked to main as a separate small PR** if you want to clear it from the feature scope.

2. **`2e86b78`** — Phase A.3 setup. Three changes:
   - `pyproject.toml` registers `@pytest.mark.uat` and excludes it from default runs (`addopts = "-m 'not uat'"`)
   - `tests/conftest.py` appends a `sys.path` shim adding `unisoft-proxy/client/` so tests can `from cli import app` and `from unisoft_client import UnisoftClient`
   - `tests/fixtures/.gitkeep` creates the directory for empirical findings

3. **`9f7e81d`** — Phase B.1 fixture. Captures the empirical finding from probing UAT and prod for the right ActionId + notification template:
   - `usli_quote_action_id: 67` ("Send offer to agent")
   - `usli_quote_letter_name: "USLI Quote"` (active in both UAT and prod)
   - Subject: `Quote Proposal for [ApplicantName] - [QuoteId]`
   - Body: 2314 chars HTML referencing retailer + applicant copies — exactly JC's workflow
   - **Plan correction baked in**: ActionId 67 has 25 templates; need (action_id, letter_name) pair, not single ActionId. Settings/Param Store/_load_skill all need to thread both.
   - dev Param Store: `/indemn/dev/gic-email-intelligence/usli-quote-action-id` = `67`, `/indemn/dev/gic-email-intelligence/usli-quote-letter-name` = `USLI Quote` (set during B.1)

4. **`3143886`** — Proxy debug endpoint. Adds `POST /api/soap_raw/<op>` to `UniProxy.cs` that returns the raw SOAP response XML instead of JSON-translated body. Deployed UAT-only:
   - Compiled new `UniProxy.exe` (67,072 bytes, was 66,048)
   - **`UniProxy-Prod.exe` UNTOUCHED** — production proxy uptime preserved (was 6 days at deploy time)
   - Backup retained at `C:\unisoft\UniProxy.exe.20260430180503.bak` and `UniProxy.cs.20260430180503.bak`
   - Used to discover the B.2 finding; useful going forward for any Unisoft response shape questions

5. **`7c326c0`** — Phase B.2 fixture. Documents the Unisoft search-ops empty-array limitation that drove the Option A decision. WordLookupType valid values (`Contains`, `StartsWith`); SearchForValue does not search Name field; data permission is the most likely cause.

### AWS state changes

- **Linear tickets created** (under DEVOPS-151):
  - DEVOPS-162 — USLI quote automation
  - DEVOPS-163 — Task subject format `[LOB] - Business description` (sibling)
  - DEVOPS-164 — Faster claim into "Indemn - Processing" (sibling)
  - DEVOPS-165 — `.eml` export includes attachments inline (sibling)
- **AWS Param Store dev**:
  - `/indemn/dev/gic-email-intelligence/usli-quote-action-id` = `67`
  - `/indemn/dev/gic-email-intelligence/usli-quote-letter-name` = `USLI Quote`
- **No prod Param Store changes yet.** Prod equivalents will be set during Phase H, gated by DEVOPS-158 closing + JC sign-off.
- **No EC2 changes outside the UAT proxy.** Prod-services and dev-services containers untouched.
- **S3**: `s3://indemn-gic-attachments/proxy-deploy/UniProxy.cs` is the staging artifact for the proxy deploy. Retained for rollback if needed.

---

## Open work — what's next

### Immediate (start here)

1. **B.7 (NEW): Agree with Craig + JC on Option A UX shape.** See "Option A decision" above for plausible paths a1–a4. This unblocks the rest of the design.
2. **Update design + plan** to reflect the chosen UX. Drop C.1 + the dead B.2 consumer. Commit as `docs(usli): pivot to Option A`.

### Phase B remainder (after B.7)

3. **B.3** — Confirm PDF version detection patterns. Pull 5 recent USLI quote emails from Mongo (use prod DB `gic_email_intelligence`, read-only). Eyeball filename patterns for retailer / applicant / customer markers. Update fixture.
4. **B.4** — Confirm BrokerId + CarrierNo in prod. Likely same as UAT (1 / 2) but verify.
5. **B.5** — JC confirmation on ambiguous-match folder. **May become moot under Option A** — if JC provides the Quote ID, ambiguous match shouldn't happen.
6. **B.6** — Settings field + Param Store wiring for the (action_id, letter_name) pair. **Already partially done** — dev Param Store entries exist; just needs the Settings field added and aws-env-loader.sh PARAM_MAP updated.

### Phase B-exit gate

7. Verify all required fixture keys present, dev Param Store matches fixture, then proceed to Phase C.

### Phase C — CLI commands (TDD)

8. **C.0** — Fix `unisoft_client.get_submissions` PascalCase→camelCase bug (the C.3 prerequisite). Pre-existing bug; the WSDL + captured payload both use `QuoteId`.
9. ~~C.1~~ — **DROPPED under Option A.**
10. **C.2** — Add `--confirmation-no` flag to `unisoft submission create`.
11. **C.3** — Add `unisoft submission update` (wraps `SetSubmission Action=Update`, fetch-then-modify pattern).
12. **C.4** — Generalize `_create_activity_and_notify` to accept `(quote_id, action_id, submission_id, letter_name)`. Tests mock `httpx.post`. **Important schema correction**: `_create_activity_and_notify` and the related code paths need to thread the (action_id, letter_name) pair, not just action_id. The notification template lookup filters by both.
13. **C.5** — Idempotency classifier helper (3-layer + multi-LOB updates all empty-ref Submissions, per Craig's #8 decision).
14. **C.6** — Failure-mode + multi-LOB tests.

### Phase D — Skill + agent factory

15. **D.1** — Extend `_load_skill` to accept `{usli_quote_action_id}` AND `{usli_quote_letter_name}` placeholders. (Plan said one placeholder; needs two.)
16. **D.2** — Create `process-usli-quote.md` skill. Step 2 ("find Quote") uses Option A's chosen mechanism, NOT name search.
17. **D.3** — Add `create_automation_agent_usli()` factory.
18. **D.4** — Wire `gic automate run --type usli_quote` dispatch + `pause_usli_automation` Settings field.

### Phase E — Folder routing

19. **E.1** — Factor `ensure_folder_exists`, add `INDEM_USLI_PROCESSED` and `INDEM_USLI_NEEDS_REVIEW` constants. **`Indemn USLI Needs Review` may become moot under Option A** (if JC provides Quote ID, no ambiguous-match case).

### Phase G — UAT soak

20. **G.0** — Add `automation-usli-cron` container to `docker-compose.yml`.
21. **G.1** — Open PR (when feature branch is ready), wait for review + merge, dev-services container redeploys via `build.yml`.
22. **G.2** — Process N real `usli_quote` emails into UAT (SOAK_MODE active = no folder moves, no real agent emails). Verify against UAT Unisoft Submissions/Activities.
23. **G.3** — Numerical thresholds gate Phase H (10 successful runs, 0 customer copies, 0 empty templates, etc.).
24. **G.4** — Validate with JC — walk through 5 cases.
25. **G.5** — Draft customer comms.

### Phase H — Production rollout

**Gates on DEVOPS-158 closing (~2026-05-06).** Don't start until soak is Done.

26. H.0 — prod folders on quote@ inbox
27. H.1 — verify gates
28. H.2 — wire baseline Datadog alerts (depends on PR #19 / DEVOPS-156 landing)
29. H.3 — deploy to prod-services (paused initially)
30. H.4 — verify alerts firing on test events
31. H.5 — send T-0 customer comms + flip the switch
32. H.6 — 24h post-cutover watch

### Sibling PRs (independent of USLI)

33. **DEVOPS-163 (Sibling 1)** — Task subject format `[LOB] - Business description`. Worktree: `/Users/home/Repositories/gic-eml-sibling-1`. Ready to ship anytime.
34. **DEVOPS-164 (Sibling 2)** — Faster claim into "Indemn - Processing". **Gates on DEVOPS-158 closing** (cron interval change would invalidate the prod soak observations).
35. **DEVOPS-165 (Sibling 3)** — `.eml` export includes attachments inline. Worktree: `/Users/home/Repositories/gic-eml-sibling-3`. Ready to ship anytime.
36. **DEVOPS-165 backfill (Sibling 4)** — Backfill historical `.eml` uploads. Gates on Sibling 3 merging. **[NEEDS USER APPROVAL]** end-to-end.

---

## Mental model (internalize these — same as 04-29 handoff)

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
- `usli_quote` = USLI's quote response. **The slice we're now automating.** ~80% of inbox volume; classified + linked but not acted on today.
- Folder routing: Inbox → Indemn-Processing (on classification) → indemn processed (success) / Duplicates (dup detected) / Inbox (failure).

**Multi-LOB:** one email = one quote, even if multiple LOBs in the submission. GL+CP → CP/PK (Package), restaurant GL → CG/HM, contractor GL → CG/AC.

**DTO discipline (Unisoft):** Always populate ALL schema fields, even with nil defaults. Partial DTOs cause silent server-side data loss. This bit us with ActivityDTO AND the nested NotificationDTO. Same lesson likely applies to any new Unisoft API integration.

**Notification pattern:** `SendActivityEmail` on `IEmailService` is the actual email sender. `SetActivity` alone does NOT send email. The agent uses a 2-call workflow. Plain HTTPS transport security on this service (NOT WS-Security like the main API).

**Attachment upload pattern:** Unisoft's Azure App Service has a ~1.5MB ceiling for buffered uploads. We bypass WCF entirely with custom `HttpWebRequest` + `SendChunked=true` + manually-built MTOM/XOP multipart.

**LLM caveats:**
- LLMs corrupt hex strings (Mongo ObjectIds) by mis-reading characters. `_safe_object_id()` tries 16 variants to recover.
- Skills must be **inlined in the system prompt**, not loaded as flat files — `deepagents`' SkillsMiddleware doesn't currently work for our shape.
- All LLM calls run on Gemini 2.5 Pro/Flash via Vertex AI (Anthropic credit was depleted earlier in April).

**Mongo DB topology (post-cutover):**
- dev-services EC2 → `gic_email_intelligence_devsoak` database (sandbox; sync cron pulls real emails into it; SOAK_MODE prevents Outlook + agent-email side effects)
- prod-services EC2 → `gic_email_intelligence` database (live customer data)
- Same Atlas cluster (`dev-indemn-pl-0`), different databases. Customer Outlook inbox is shared between envs — **SOAK_MODE on dev is what keeps dev from clobbering prod.**

**USLI-feature-specific (NEW — internalize these):**
- ActionId 67 ("Send offer to agent") is the parent action. It has **25 notification templates** (the dropdown JC mentioned). LetterName="USLI Quote" picks the carrier-specific one.
- The notification template body says: "Attached you will find two versions of this quote: one from us to you (retailer copy)" — confirming the workflow JC dictated.
- USLI = CarrierNo 2; GIC Underwriters = BrokerId 1; AgentNo 777 = "GIC Office Quoted" internal identifier.
- Unisoft search ops return correct match counts but **empty data arrays** — auth/permission gating. `GetQuote(QuoteID)` works fine.
- Option A's "JC provides the Quote ID" sidesteps this entirely.

## Stakeholders

| Person | Role | What they care about |
|---|---|---|
| **JC** (jcdp@gicunderwriters.com) | Head of underwriting at GIC | Daily queue / backfill updates. Trusts the system. Will request retroactive runs of pipeline steps. **Approved the USLI feature scope on 2026-04-30.** |
| **Maribel** | Underwriter using Outlook add-in | Detail-oriented. Recently asked for: LOB-prefixed task titles, attachments-with-body uploads, USLI quote retailer-contact handling. |
| **Dhruv** (Indemn) | DevOps engineer | SOC 2 / Oneleet / WAF / Datadog. PR #19 (Datadog) still pending merge — H.2 alerts gate on it. |
| **Dolly, Rudra** (Indemn) | Engineers | Frequent PR reviewers. |
| **Craig** | You're working with him | The CTO; will give you direction at every approval gate. |

## Hard rules (post-cutover)

- **No merges to `indemn-ai/gic-email-intelligence:main`** without PR review (Dolly + Dhruv typically). Branch protection is on.
- **No deploys to prod-services EC2** until DEVOPS-158 closes (target ~2026-05-06).
- **Test in dev-services EC2** for new feature work — runs against `gic_email_intelligence_devsoak` Mongo + UAT Unisoft. SOAK_MODE prevents Outlook folder changes and real agent emails.
- **Sibling 2 (DEVOPS-164, faster claim)** explicitly waits until DEVOPS-158 closes — cron interval change would invalidate ongoing soak observations.
- **Production safety**: any prod-Param-Store, prod-EC2 mutation, prod folder creation, or prod cron unpause is `[NEEDS USER APPROVAL]` per the OS production-safety rule.
- **Prod proxy on `i-0dc2563c9bc92aa0e`** (`UniProxy-Prod.exe`, port 5001) was untouched by the proxy update on 2026-04-30 18:08. **DO NOT touch the prod proxy** — UAT-only changes during this feature.

## Git layout

**Repos:**
- `gic-email-intelligence-migration/` — mainline checkout, currently on `migration/indemn-infra` branch (33+ commits ahead of `indemn/main` historically; merged via PR #1 during cutover). Use this for `git fetch indemn` operations.
- `gic-email-intelligence-usli/` — **the active feature worktree.** On `feat/usli-quote-automation`, 5 commits ahead of `indemn/main`. Created in Phase A.1.

**Remotes in the migration repo:**
- `indemn` → `indemn-ai/gic-email-intelligence` (the active prod repo — branch from here)
- `origin` → `craig-indemn/gic-email-intelligence` (legacy fork, frozen — do not use)
- Branches: `main` (active), `prod` (protected, prod deploys only via PR), feature branches as needed.

**OS repo (where this handoff and design live):**
- Worktree: `/Users/home/Repositories/operating-system/.claude/worktrees/gic-feature-scoping/`
- Branch: `os-gic-feature-scoping`
- The original `2026-04-29-feature-scoping-handoff.md` and the design + plan are committed here.
- The Unisoft API research lives on a different branch: `os-unisoft`. Worktree at `/Users/home/Repositories/operating-system/.claude/worktrees/unisoft/`.

## Conventions

- **Commit style:** `feat(scope): ...`, `fix(scope): ...`, `test: ...`, `docs(scope): ...`, `proxy: ...`, `infra: ...`. See `git log --oneline` in the feature worktree for examples.
- **PR style:** Summary, Test plan, "Why this is a follow-on" section if relevant. PR #18 (SOAK_MODE) and PR #19 (Datadog) are good templates.
- **Reviewers:** Dolly + Dhruv on most PRs. Rudra sometimes. Add via `gh pr edit <num> --repo indemn-ai/gic-email-intelligence --add-reviewer dolly45,dhruvrajkotia`.
- **Linear:** parent epic DEVOPS-151. Sub-issues 162-165 created on 2026-04-30. Sub-tasks tracked as comments on each sub-issue.
- **Test pattern:** mock-first; UAT smoke tests behind `@pytest.mark.uat` (excluded from default pytest runs); CliRunner for Typer commands; `from cli import app` works via the conftest sys.path shim.
- **Production-safety:** `[NEEDS USER APPROVAL]` markers throughout the plan gate every prod-touching step.

## Skills you'll likely use

- **`superpowers:executing-plans`** — the plan was written for this. Loads the plan, executes in batches with checkpoints. **Start here.**
- **`/beads`** — task tracker. Existing tasks #6-#12 capture Phase A + B progress; create new ones for B.3 onward.
- **`/linear`** — for ticket updates as you complete sub-tasks. Use `linearis-proxy.sh issues read DEVOPS-162` etc.
- **`/postgres`**, **`/mongodb`** — for any Mongo data inspection (e.g., querying USLI emails for B.3).
- **`/aws`** — for SSM, Param Store, EC2 inspection. Already used heavily.
- **`/google-workspace`** — Gmail draft creation (G.5 customer comms).

## Your first response to Craig

After you've absorbed everything:

1. **Confirm context** with a one-paragraph summary back to Craig — what's been done, what's blocked on Option A's UX decision, what's next. Mention 2–3 specific things you internalized (e.g., "I see the (action_id, letter_name) pair correction in the B.1 fixture" or "I noted the proxy debug endpoint is UAT-only and prod-untouched"). This shows you actually read it.

2. **Surface the Option A UX decision question** — Craig + JC need to align on which path (a1–a4 above) to use. The next step is for you to ask Craig his preference, OR for Craig to send JC the question and tell you the answer.

3. **Once UX is decided, update the design + plan** with the change, commit, and proceed to Phase B.3 (the next non-blocked task).

4. **Use `superpowers:executing-plans`** to drive task-by-task execution per the plan's structure.

Don't write code beyond the design + plan updates until the UX is locked. Once it's locked, follow the plan task-by-task with the existing TDD discipline — failing test → implement → run-pass → commit. Frequent commits, atomic changes.

Welcome to the project.
