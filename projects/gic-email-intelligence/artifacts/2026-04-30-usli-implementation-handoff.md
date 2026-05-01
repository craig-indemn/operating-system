---
ask: "Hydrate a fresh Claude session to continue executing the USLI Quote Automation implementation. Replicates the original 2026-04-29 feature-scoping handoff structure, refreshed with 2026-05-01 progress. Designed for zero knowledge loss between sessions: read this once, internalize the deltas, pick up exactly where the prior session left off. Updated 2026-05-01 evening to reflect the deterministic-lookup architectural pivot + 9 commits shipped today."
created: 2026-04-30
updated: 2026-05-01
workstream: gic-email-intelligence
session: 2026-05-01-handoff
sources:
  - type: artifacts
    description: "Curated reading list — design doc + implementation plan (both updated 2026-05-01), two new architecture artifacts captured today, USLI fixture findings"
  - type: codebase
    description: "Pointers into gic-email-intelligence-migration (mainline) AND gic-email-intelligence-usli (in-progress feature worktree, 14 commits ahead of indemn/main)"
  - type: research
    description: "Unisoft API extraction at projects/gic-email-intelligence/research/unisoft-api/ on the os-unisoft branch (40k-line WSDL, captured SOAP payloads, operations index) PLUS the 2026-05-01 fresh SAZ capture in S3"
---

# USLI Implementation Handoff — GIC Email Intelligence (updated 2026-05-01)

You're a fresh Claude session continuing the **USLI Quote Automation** implementation for GIC. Brainstorming + design + plan are done. **Phase A is complete, Phase B is complete, Phase C is mostly done (4/7 tasks shipped today), Phase D is open.** The 2026-05-01 session resolved a major architectural question that the prior handoff got wrong, and produced two new artifacts that are now load-bearing for the rest of the build.

**Do NOT start writing new code until you've absorbed the design + plan + the 2026-05-01 architectural pivot.** Read everything first. Build a complete mental model. Then pick up at C.5 — the next non-blocked task.

> **Lesson for this session, learned painfully in the last one:** the prior handoff (2026-04-30 morning) asserted that Craig had picked "Option A: JC provides the Quote ID" to resolve the search-impossibility blocker. **That was a misread of the prior session.** Craig had actually picked options B + C (research the Unisoft API for a working search path). I spent ~30 minutes designing around Option A before he corrected me. **Verify any "Craig decided X" claim in the handoff with him before building on it.** Especially anything tagged as a pivot or design change.

---

## What this project is (one paragraph)

GIC Underwriters is an MGA (managing general agent) for commercial insurance. Their `quote@gicunderwriters.com` inbox receives ~50 submissions/day from agents — a mix of new business applications, quote requests, follow-ups, and portal acknowledgments. We've built an end-to-end pipeline that ingests these emails, classifies them, extracts submission data (PDF parsing of ACORD forms, contact info, agency lookup), and creates Quotes in **Unisoft** (their AMS) with attachments and notification emails — all autonomously, with deterministic fallbacks for the parts that LLMs can't be trusted to do reliably. **The system has been live in production since 2026-04-23 and migrated to Indemn's EC2 infrastructure on 2026-04-29.** Your work extends it to handle USLI quote responses (the 80%+ slice of inbox volume that's currently classified but not acted on).

## Where we are right now (2026-05-01 evening)

**Cutover succeeded 2026-04-29 ~22:50 UTC.** Production runs on EC2 prod-services (`i-00ef8e2bfa651aaa8`) behind ALB `api.gic.indemn.ai`. Real customer email Q:146697 (Crown Park) verified end-to-end through the new pipeline. **DEVOPS-158 7-day soak window is active** until approximately **2026-05-06**. Phase H of the USLI feature gates on DEVOPS-158 closing.

**USLI feature build is mid-flight, accelerated.**

- ✅ Brainstormed + designed (artifact `2026-04-29-usli-quote-automation-design.md`, with 2026-05-01 update callouts)
- ✅ Customer-facing scope email sent to JC; **JC approved**
- ✅ Implementation plan written, reviewed, and updated 2026-05-01 with comprehensive deltas (artifact `2026-04-29-usli-quote-automation-implementation-plan.md` — has a top-of-doc Updates Log)
- ✅ 4 Linear tickets created (DEVOPS-162 through DEVOPS-165)
- ✅ **Phase A** (Workspace + Linear + conftest) — DONE
- ✅ **Phase B** (build-time verification) — DONE 2026-05-01:
  - B.1 — ActionId 67 + LetterName "USLI Quote" in fixture
  - B.2 — canonical Unisoft search wire format captured + documented (artifact `2026-05-01-unisoft-quote-search-canonical-shape.md`)
  - B.3 — PDF whitelist policy verified against prod corpus
  - B.4 — BrokerId/CarrierNo prod parity confirmed
  - B.5 — **deterministic-lookup architecture locked** (artifact `2026-05-01-usli-deterministic-lookup-architecture.md`)
  - B.6 — Settings + Param Store wiring shipped
- ✅ **Phase C partial** (4 of 7 tasks shipped today):
  - C.0 — `unisoft_client.get_submissions` PascalCase fix
  - C.1 — `unisoft quote search` via `GetQuotesForLookupByCriteria` with canonical Criteria
  - C.2 — `--confirmation-no` flag on `unisoft submission create`
  - C.3 — `unisoft submission update` (fetch-then-modify)
  - C.4 — `_create_activity_and_notify` letter_name template filter (real bug fix)
- ⏳ **C.5, C.7 (NEW), C.6** — open
- ⏳ **Phase D, E, G, H, K** — open

**Active feature branch:** `feat/usli-quote-automation` on `indemn-ai/gic-email-intelligence`. **Active feature worktree:** `/Users/home/Repositories/gic-email-intelligence-usli/`. **14 commits ahead of `indemn/main`** as of 2026-05-01. **32 new tests, all passing locally (some pre-existing tests fail on local Mac due to lack of Atlas access — not regressions).**

## Reading list (in order)

Read these in order. **Total reading: ~45 min if thorough.** New artifacts have been added at Layer 1.5; older items are mostly skim.

### Layer 0 — This handoff (you're here)

### Layer 1 — Authoritative current spec (~25 min, this is the most important)

The plan + design are working documents. They were updated 2026-05-01 with comprehensive UPDATE callouts at every section that changed. **Read these before anything else.**

1. **`projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-implementation-plan.md`** — the bite-sized execution plan. Has a top-of-doc Updates Log summarizing the 2026-05-01 deltas. Per-task UPDATE callouts at every revised section. **Phase B is now mostly SHIPPED with commit pointers; Phase C.0-C.4 marked SHIPPED; C.5/C.7 spec'd; D/E/G/H/K revised.** New C.7 task (deterministic-lookup helper) added inline after C.6.
2. **`projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-design.md`** — the design doc. Top-of-doc UPDATE callouts surface the architectural pivot, the (action_id, letter_name) pair, the whitelist PDF policy. The original "branched on lookup" diagram is preserved as historical record but the deterministic-lookup architecture supersedes it.

### Layer 1.5 — NEW 2026-05-01 architecture artifacts (~15 min, REQUIRED)

These are the load-bearing references for the rest of the build. **Read both.**

3. **`projects/gic-email-intelligence/artifacts/2026-05-01-unisoft-quote-search-canonical-shape.md`** — captures the canonical SOAP wire format for `GetQuotesForLookupByCriteria`. Reverse-engineered from a fresh Fiddler SAZ on 2026-05-01. **Critical learning: model the request after the captured UI wire format, NOT after the saved-search XML returned by `GetAllSearchPreferences`.** Lists every dead-end the prior session walked (Login op, REST gateway probes, IsNewSystem variations, pagination matrix, alternate hosts). Future-self-defense.

4. **`projects/gic-email-intelligence/artifacts/2026-05-01-usli-deterministic-lookup-architecture.md`** — locks the lookup algorithm for finding the right Unisoft Quote when a USLI quote-response email arrives. **Three-tier deterministic lookup with loop-closure stamping**: Tier 1 Mongo by USLI ref → Tier 2 Unisoft search with agent+LOB+recency+status filter → Tier 3 Path-2 create. Every Submission we touch gets `ConfirmationNo=usli_ref` stamped, so future re-quotes hit Tier 1. **Drops the `Indemn USLI Needs Review` folder** — Tier 2 ambiguity uses tiebreak (highest QuoteId), not human triage. This artifact is what D.2's skill consumes.

### Layer 2 — Other architectural references

5. **`projects/gic-email-intelligence/artifacts/2026-04-29-feature-scoping-handoff.md`** — the original session-zero handoff. Comprehensive project context. Lower priority for you since this handoff replicates the structure with current state.
6. **`tests/fixtures/usli_config.json`** in the feature worktree — empirical findings. Has corrected B.2 finding, canonical Criteria template, B.3 whitelist patterns, B.4 prod parity confirmation, B.6 keys. **The B-exit gate's revised assertion list (in the plan, B-exit section) checks this.**

### Layer 3 — Unisoft API research (~10 min, read selectively)

The research lives on the **`os-unisoft` branch** of the OS repo:
- Worktree path: `/Users/home/Repositories/operating-system/.claude/worktrees/unisoft/projects/gic-email-intelligence/research/unisoft-api/`
- Files: `operations-index.md`, `wsdl-complete.md` (40k lines, grep), `raw-payloads/soap/IIMSService__*.txt` (real captured wire payloads).

**The 2026-05-01 SAZ capture is in S3, not git:** `s3://indemn-gic-attachments/research/quote-search-2026-05-01-export5.saz` — 962KB, 333 sessions. Session 115 is the canonical `GetQuotesForLookupByCriteria(Name=Craig)` that returns Q:17129 with full QuoteForLookupDTO. Pull and extract if you need to inspect any specific Unisoft op the UI uses.

### Layer 4 — How the system works (~30 min, skim if you've read prior handoffs)

7. **`projects/gic-email-intelligence/artifacts/2026-03-30-pipeline-architecture-review.md`** — pipeline stages: sync → process → automation. Cron-based, MongoDB-backed.
8. **`projects/gic-email-intelligence/artifacts/2026-03-24-data-model-redesign.md`** — emails, submissions, quotes, automations, agencies, contacts. Critical for any feature touching the data layer.
9. **`projects/gic-email-intelligence/artifacts/2026-04-23-go-live-day-session-2.md`** — classification rules (Rule 7), multi-LOB handling, deterministic activity + notification pattern, ObjectId corruption recovery, duplicate routing. **(On `os-unisoft` branch.)**
10. **`projects/gic-email-intelligence/artifacts/2026-04-24-upload-bypass-and-notification-fixes.md`** — Unisoft DTO conventions (full-fields-required pattern), MTOM/XOP chunked attachment uploads, **`SendActivityEmail` on `IEmailService`**. **(On `os-unisoft` branch.)**

### Layer 5 — Cutover post-mortem (~5 min)

11. **`projects/gic-email-intelligence/artifacts/2026-04-29-cutover-execution-handoff.md`** **(on `os-unisoft` branch)** — what shipped, what didn't, lessons. Covers Datadog PR #19, AUTOMATION_START_DATE filter, the 7-day soak gate (DEVOPS-158).

### Layer 6 — Code (the source of truth)

After the docs, browse these files in `gic-email-intelligence-usli/` (the feature worktree):

- **`src/gic_email_intel/agent/harness.py`** — pipeline orchestrator + classification rules (including Rule 7).
- **`src/gic_email_intel/automation/agent.py`** — deepagent system prompt + skill loading. Note `_load_skill` does `.format()` substitution; D.1 will extend it for the new placeholders (BOTH `usli_quote_action_id` AND `usli_quote_letter_name`).
- **`src/gic_email_intel/automation/skills/create-quote-id.md`** — the existing `agent_submission` skill. Mirror its structure for `process-usli-quote.md` in D.2 (but D.2 calls a single CLI shim for lookup rather than embedding the algorithm in prose).
- **`src/gic_email_intel/cli/commands/emails.py`** — `gic emails complete` (deterministic activity + notification, duplicate detection, folder routing). C.4 generalized `_create_activity_and_notify` here with `(action_id, letter_name, submission_id)` — shipped 2026-05-01 commit `0515868`.
- **`src/gic_email_intel/core/email_mover.py`** — Outlook folder move helper. E.1 factors `ensure_folder_exists` out; under the new architecture only `INDEM_USLI_PROCESSED` is needed (Needs Review folder dropped).
- **`src/gic_email_intel/agent/tools.py`** — agent toolset, includes `_safe_object_id()` for LLM hex corruption recovery.
- **`src/gic_email_intel/cli/commands/submissions.py`** — submission CLI; gets new commands for C.5 (`classify-usli-state`) and C.7 (`find-quote-for-usli`).
- **`unisoft-proxy/client/cli.py`** — Unisoft CLI. Now has `quote search`, `submission create --confirmation-no`, `submission update` (all shipped today).
- **`unisoft-proxy/client/unisoft_client.py`** — client methods. Has `search_quotes()` (C.1), `update_submission()` (C.3), `get_submissions()` with camelCase fix (C.0).
- **`unisoft-proxy/server/UniProxy.cs`** — SOAP proxy on EC2. Includes `/api/soap_raw/<op>` debug endpoint (UAT only, port 5000).
- **`docker-compose.yml`** — service topology. G.0 will add `automation-usli-cron`.
- **`tests/fixtures/usli_config.json`** — all empirical findings + canonical Criteria template + B.6 PDF patterns.
- **`tests/test_emails_complete.py`** — the C.4 letter_name test (the smoking-gun: 25 templates with the right one at index 7).
- **`tests/test_unisoft_quote_search.py`** — canonical Criteria regression guards.
- **`tests/test_unisoft_submission.py`** — C.2/C.3 tests.
- **`tests/test_unisoft_client.py`** — C.0 test.
- **`tests/test_settings_usli.py`** — B.6 Settings tests.

---

## Progress so far on `feat/usli-quote-automation`

**14 commits ahead of `indemn/main`. 32 new tests, all green locally.** Listed newest first:

```
28ce5e6 feat(config): USLI Settings + Param Store wiring (B.6)
0515868 fix(emails): _create_activity_and_notify filters templates by letter_name (C.4)
74cd768 fixture: B.3 — USLI PDF version detection patterns (whitelist policy)
fa8d55a fixture: B.4 — confirmed BrokerId=1 (GIC) + CarrierNumber=2 (USLI) match prod
8608121 feat(unisoft): submission update (fetch-then-modify, PersistSubmission=Update) (C.3)
aec13fa feat(unisoft): submission create accepts --confirmation-no (C.2)
ea0fe75 fix(unisoft_client): get_submissions sends QuoteId (camelCase) per WSDL (C.0)
b2f0f27 feat(unisoft): quote search via GetQuotesForLookupByCriteria with canonical Criteria (C.1)
7c326c0 fixture: B.2 finding — Unisoft search ops return empty arrays (NOW SUPERSEDED — see canonical-shape artifact)
3143886 proxy: add /api/soap_raw/<op> debug endpoint (UAT-only deploy)
9f7e81d fixture: B.1 — USLI Quote ActionId + LetterName
2e86b78 test: add 'uat' marker, sys.path shim for unisoft-proxy/client, fixtures dir
c668a67 test: fix stale 'stage-detector' reference (renamed to situation-assessor)
```

Plus on the OS repo branch `os-gic-feature-scoping`:
```
2113fd7 docs(usli): lock deterministic-lookup architecture + spec deltas across plan + design
b0813c9 docs(usli): canonical Unisoft quote-search wire format from SAZ session 115
```

### What today (2026-05-01) accomplished

**1. The "search returns empty arrays" mystery — solved.** Captured a fresh Fiddler SAZ of the Unisoft desktop UI doing a name-based quote search. Session 115 in that SAZ shows the canonical SOAP request shape: `GetQuotesForLookupByCriteria` with a Criteria DTO that uses `WordLookupType` (not `SelWordFilterOption`), no `SelectedSearchByOption`, no nested `*DateRange` objects, plus `BusinessType`/`LOB`/`SubLOB`/`Underwriter` as nillable fields. The prior session was modeling Criteria after the saved-search XML returned by `GetAllSearchPreferences` — that's the UI's internal-state format, not the SOAP wire. Same field names, completely different shapes. Documented in `2026-05-01-unisoft-quote-search-canonical-shape.md` so future-self never repeats this dead-end.

**2. Deterministic-lookup architecture — locked.** Empirical inspection of 7 real USLI-linked Quotes in prod showed the USLI ref is NOT stored anywhere on Unisoft side today. Every `Quote.ConfirmationNumber` / `Submission.ConfirmationNo` (CarrierNo=2) is null. JC's broker workflow doesn't stamp it; USLI Retail Web doesn't write it back. **Building the deterministic key on OUR side**: Tier 1 Mongo by ref → Tier 2 Unisoft search w/ agent+LOB+recency+status filter → Tier 3 create. **Every Submission we create or touch gets `ConfirmationNo` stamped (loop closure)**, so within ~2 weeks of running, ≥95% of incoming USLI quote emails hit Tier 1 directly. The "Indemn USLI Needs Review" folder is dropped — Tier 2 ambiguity uses tiebreak (highest QuoteId). Architecture artifact: `2026-05-01-usli-deterministic-lookup-architecture.md`.

**3. C.4 latent bug fixed.** `_create_activity_and_notify` was picking `templates[0]` blindly — works for ActionId 6 (one template), silently fires the wrong template for ActionId 67 (25 templates). Now filters by `LetterName == letter_name`. The smoking-gun test seeds 25 templates with "USLI Quote" at index 7 to prove order-independence.

**4. Plan + Design updated comprehensively** with UPDATE callouts at every revised section. Original plan body preserved as historical record per the never-delete-history rule. New C.7 task spec'd inline. New K.8 task added (backfill historical USLI Submissions with ConfirmationNo). K.5 marked superseded.

### AWS state changes today

- **EC2 proxy box (`i-0dc2563c9bc92aa0e`) upgraded** from `t3.small` → `t3.large`. EIP `54.83.28.79` and private IP `172.31.23.146` preserved. Total prod proxy outage during the swap: ~4-5 minutes. Both proxy services came up clean on first poll. (The t3.small was choking when Craig tried to run Fiddler + Unisoft UI simultaneously.)
- **Fiddler installed** on the proxy box. Per-Administrator install at `C:\Users\Administrator\AppData\Local\Programs\Fiddler\Fiddler.exe`. Desktop shortcut `Fiddler.lnk` created. Used for the SAZ capture.
- **Unisoft desktop ClickOnce apps reinstalled** on the proxy box. Two `.application` manifests on the Desktop: `Unisoft-UAT.application` (points at `ins-gic-client-uat-app.azurewebsites.net`) and `Unisoft-PROD.application` (points at `ins-gic-client-prod-app.azurewebsites.net`). Both deployment URLs reachable. ClickOnce cache cleared during install to fix prior stuck-update state.
- **dev Param Store** already had `usli-quote-action-id=67` and `usli-quote-letter-name="USLI Quote"` from the original B.1 work. The PARAM_MAP entries in `aws-env-loader.sh` were missing — silently dropping these values during container env load. **B.6 closed that gap.** Loader now writes both vars on container env reload.
- **No prod Param Store changes.** Prod entries gate on Phase H (DEVOPS-158 closing).
- **No prod proxy changes.** Prod proxy (`UniProxy-Prod.exe`, port 5001) was untouched throughout the session. Only UAT proxy (port 5000) has the soap_raw debug endpoint.
- **S3:** `s3://indemn-gic-attachments/research/quote-search-2026-05-01-export5.saz` (962KB, 333 sessions). Source of truth for the canonical wire format.

---

## Open work — what's next (in punch-list order)

The plan's review subagent (run today) produced this execution order. Each task's spec is in the implementation plan. The new artifacts (Layer 1.5 above) are the authoritative reference for design decisions.

### Immediate (start here)

1. **C.5 — `should_upload_pdf` whitelist + `classify-usli-state` CLI.** Create `src/gic_email_intel/automation/usli_helpers.py` with two pure helpers: `should_upload_pdf(filename, retailer_patterns, applicant_patterns)` (whitelist policy from B.3) and `classify_submission_state(submissions, usli_ref)` (3-layer idempotency from the original plan — implementation unchanged, docstring updated). Add `gic submissions classify-usli-state --quote-id N --usli-ref REF` CLI shim using `httpx.post` directly. Tests in `tests/test_usli_helpers.py` (new file).

2. **C.7 — Deterministic-lookup helper (NEW).** Create `find_quote_for_usli_ref(usli_ref, insured_name, agent_no, lob, *, skip_backfill=False, mongo_only=False)` in `usli_helpers.py`. Implements the 3-tier algorithm from the architecture artifact. CLI shim: `gic submissions find-quote-for-usli`. **Add Mongo index** `db.submissions.createIndex({"reference_numbers": 1, "unisoft_quote_id": 1})` (idempotent). The LOB-prefix → Unisoft-LOB map (MGL→CG, MPL→CP, MSE→Special Events, NPP→CG, XSL→CU, ...) is a new fixture key `usli_ref_prefix_to_lob`. Comprehensive tests for all branches of the 3-tier algorithm.

3. **C.6 — Failure-mode tests.** Several tests still placeholder'd in the plan. Some need Mongo testcontainer; defer the heavier ones if too costly. Update the customer-copy-blacklist test to whitelist-policy version per the B.3 update.

### Phase D — Skill + agent factory

4. **D.1** — Extend `_load_skill` to substitute BOTH `{usli_quote_action_id}` AND `{usli_quote_letter_name}` placeholders. Test verifies both land in rendered prose.

5. **D.2** — Create `src/gic_email_intel/automation/skills/process-usli-quote.md`. **Major rewrite vs original plan**: skill calls a single CLI shim (`gic submissions find-quote-for-usli`) for lookup and branches on the JSON `state`. No name-search or filtering in skill prose — all in C.7. Step 6 (PDF upload) reads `pdf_retailer_patterns` + `pdf_applicant_patterns` from fixture, applies whitelist. Step 7 (`gic emails complete`) passes both `--action-id 67` and `--letter-name "USLI Quote"`. No `Indemn USLI Needs Review` folder logic.

6. **D.3** — Add `create_automation_agent_usli()` factory in `automation/agent.py`. Test asserts both "67" and "USLI Quote" land in the rendered system prompt.

7. **D.4** — Wire `gic automate run --type usli_quote` dispatch + `pause_usli_automation` Settings field (already exists per B.6). Same pattern as today's `agent_submission` dispatch.

### Phase E — Folder routing

8. **E.1** — Factor `ensure_folder_exists` helper, add `INDEM_USLI_PROCESSED` constant. **Drop `INDEM_USLI_NEEDS_REVIEW`** per the deterministic-lookup architecture.

### Phase G — UAT soak

9. **G.0** — Add `automation-usli-cron` container to `docker-compose.yml`.
10. **G.1** — Open PR for review + merge to main; dev-services container redeploys via `build.yml`.
11. **G.2** — Process N real `usli_quote` emails into UAT (SOAK_MODE active = no folder moves, no real agent emails).
12. **G.3** — Revised numerical thresholds: ambiguous-tiebreak rate < 1% steady-state, **stamping success rate = 100% (non-negotiable)**, Tier 1 hit rate trends to ≥95% within 2 weeks, customer-copy uploads = 0, template-empty = 0.
13. **G.4** — Validate with JC — walk through 5 cases.
14. **G.5** — Draft customer comms.

### Phase H — Production rollout

**Gates on DEVOPS-158 closing (~2026-05-06).** Don't start until soak is Done.

15. H.0 — prod folders on quote@ inbox (only `Indemn USLI Processed` now)
16. H.1 — verify gates
17. H.2 — wire baseline Datadog alerts (depends on PR #19 / DEVOPS-156 landing)
18. H.3 — deploy to prod-services (paused initially)
19. H.4 — verify alerts firing on test events
20. H.5 — send T-0 customer comms + flip the switch
21. H.6 — 24h post-cutover watch

### Phase K — Post-launch

- K.5 superseded (not deferred; built into v1 via C.7).
- **K.8 NEW** — backfill `Submission.ConfirmationNo` for the ~7 historical USLI-linked Quotes. One-shot script. **[NEEDS USER APPROVAL]** before running against prod.
- K.1, K.2, K.3, K.4, K.6, K.7 unchanged.

### Sibling PRs (independent of USLI)

- **DEVOPS-163 (Sibling 1)** — Task subject format `[LOB] - Business description`. Worktree `/Users/home/Repositories/gic-eml-sibling-1`. Ready to ship anytime.
- **DEVOPS-164 (Sibling 2)** — Faster claim into "Indemn - Processing". **Gates on DEVOPS-158 closing.**
- **DEVOPS-165 (Sibling 3)** — `.eml` export includes attachments inline. Worktree `/Users/home/Repositories/gic-eml-sibling-3`. Ready to ship anytime.
- **DEVOPS-165 backfill (Sibling 4)** — Backfill historical `.eml` uploads. Gates on Sibling 3 merging. **[NEEDS USER APPROVAL]** end-to-end.

---

## Mental model (internalize these — same as before plus the new architecture)

**Pipeline:**
```
Outlook (Microsoft Graph)
  → sync cron               (every 5min)   → MongoDB emails collection
  → processing cron         (every 5min)   → LLM classifier + extractor
                                           → submissions / quotes denormalized
  → automation cron         (every 15min)  → deepagent + Unisoft CLI
                                           → Unisoft Quote created/found
                                           → Submission created/updated (ConfirmationNo stamped)
                                           → activity + notification email to agent
```

**Classification (Rule 7 is critical):**
- `gic_application` = has a Unisoft Quote ID already. Only Boats/Yachts, WC, Welders, Caterers come in this way.
- `agent_submission` = new business from an agent (everything else: HandyPerson, Rental Dwelling, contractor GL, restaurant GL, GL+CP, etc.).
- `usli_quote` = USLI's quote response. **The slice we're now automating.** ~80% of inbox volume.
- Folder routing: Inbox → Indemn-Processing (on classification) → indemn processed (success) / Duplicates (dup detected) / Inbox (failure).

**Multi-LOB:** one email = one quote, even if multiple LOBs in the submission. GL+CP → CP/PK (Package), restaurant GL → CG/HM, contractor GL → CG/AC.

**DTO discipline (Unisoft):** Always populate ALL schema fields, even with nil defaults. Partial DTOs cause silent server-side data loss. This bit us with ActivityDTO AND the nested NotificationDTO, AND with Criteria DTO for search (where the saved-search XML field set was wrong).

**Notification pattern:** `SendActivityEmail` on `IEmailService` is the actual email sender. `SetActivity` alone does NOT send email. The agent uses a 2-call workflow.

**Attachment upload pattern:** Unisoft's Azure App Service has a ~1.5MB ceiling for buffered uploads. We bypass WCF entirely with custom `HttpWebRequest` + `SendChunked=true` + manually-built MTOM/XOP multipart.

**LLM caveats:**
- LLMs corrupt hex strings (Mongo ObjectIds) — `_safe_object_id()` recovers from corruption.
- Skills inlined in system prompt, not loaded as flat files.
- All LLM calls run on Gemini 2.5 Pro/Flash via Vertex AI.

**USLI-feature-specific (NEW):**
- ActionId 67 ("Send offer to agent") is the parent action; LetterName="USLI Quote" picks the carrier-specific template among 25.
- USLI = CarrierNumber 2; GIC Underwriters = BrokerId 1; AgentNo 777 = "GIC Office Quoted" internal identifier.
- USLI ref is NOT stored on Unisoft side today — we build the deterministic key on our side via Mongo + loop-closure stamping.
- Search via `GetQuotesForLookupByCriteria` works with the canonical Criteria shape (NOT the saved-search XML format).
- PDF uploads use whitelist policy (retailer/applicant only); attachment field in Mongo is `name`, not `filename`.

**Mongo DB topology (post-cutover):**
- dev-services EC2 → `gic_email_intelligence_devsoak` database (sandbox)
- prod-services EC2 → `gic_email_intelligence` database (live)
- Same Atlas cluster (`dev-indemn-pl-0`), different databases. Customer Outlook inbox shared between envs — **SOAK_MODE on dev is what keeps dev from clobbering prod.**

## Stakeholders

| Person | Role | What they care about |
|---|---|---|
| **JC** (jcdp@gicunderwriters.com) | Head of underwriting at GIC | Daily queue / backfill updates. Approved USLI feature scope 2026-04-30. |
| **Maribel** | Underwriter using Outlook add-in | Detail-oriented. Recently asked for: LOB-prefixed task titles, attachments-with-body uploads, USLI quote retailer-contact handling. |
| **Dhruv** (Indemn) | DevOps engineer | SOC 2 / Oneleet / WAF / Datadog. PR #19 (Datadog) still pending merge — H.2 alerts gate on it. |
| **Dolly, Rudra** (Indemn) | Engineers | Frequent PR reviewers. |
| **Craig** | You're working with him | The CTO; will give you direction at every approval gate. |

## Hard rules (post-cutover)

- **No merges to `indemn-ai/gic-email-intelligence:main`** without PR review (Dolly + Dhruv typically). Branch protection is on.
- **No deploys to prod-services EC2** until DEVOPS-158 closes (target ~2026-05-06).
- **Test in dev-services EC2** for new feature work — runs against `gic_email_intelligence_devsoak` Mongo + UAT Unisoft. SOAK_MODE prevents Outlook folder changes and real agent emails.
- **Sibling 2 (DEVOPS-164)** explicitly waits until DEVOPS-158 closes — cron interval change would invalidate ongoing soak observations.
- **Production safety**: any prod-Param-Store, prod-EC2 mutation, prod folder creation, or prod cron unpause is `[NEEDS USER APPROVAL]` per the OS production-safety rule.
- **Prod proxy on `i-0dc2563c9bc92aa0e`** (`UniProxy-Prod.exe`, port 5001) was untouched throughout the 2026-05-01 session. **DO NOT touch the prod proxy.** Only the UAT proxy on the same box (port 5000, `UniProxy.exe`) has the `/api/soap_raw/<op>` debug endpoint deployed.
- **Verify any "Craig decided X" claim** (especially design/architecture pivots) with him before building on it. The previous handoff misreported a Craig decision; cost ~30 minutes of wrong-direction work this session.

## Git layout

**Repos:**
- `gic-email-intelligence-migration/` — mainline checkout. Use this for `git fetch indemn` operations.
- `gic-email-intelligence-usli/` — **the active feature worktree.** On `feat/usli-quote-automation`, **14 commits ahead of `indemn/main`.**

**Remotes in the migration repo:**
- `indemn` → `indemn-ai/gic-email-intelligence` (the active prod repo — branch from here)
- `origin` → `craig-indemn/gic-email-intelligence` (legacy fork, frozen — do not use)
- Branches: `main` (active), `prod` (protected, prod deploys only via PR), feature branches as needed.

**OS repo (where this handoff and design + plan + new artifacts live):**
- Worktree: `/Users/home/Repositories/operating-system/.claude/worktrees/gic-feature-scoping/`
- Branch: `os-gic-feature-scoping`
- 2026-05-01 commits: `b0813c9` (canonical wire format artifact), `2113fd7` (lookup architecture artifact + plan/design updates)
- The Unisoft API research (40k-line WSDL, captured payloads, etc.) lives on `os-unisoft` branch. Worktree `/Users/home/Repositories/operating-system/.claude/worktrees/unisoft/`.

## Conventions

- **Commit style:** `feat(scope): ...`, `fix(scope): ...`, `test: ...`, `docs(scope): ...`, `proxy: ...`, `infra: ...`, `fixture: ...`. See `git log --oneline` in the feature worktree for examples.
- **PR style:** Summary, Test plan, "Why this is a follow-on" section if relevant.
- **Reviewers:** Dolly + Dhruv on most PRs. Add via `gh pr edit <num> --repo indemn-ai/gic-email-intelligence --add-reviewer dolly45,dhruvrajkotia`.
- **Linear:** parent epic DEVOPS-151. Sub-issues 162-165 created.
- **Test pattern:** mock-first; UAT smoke tests behind `@pytest.mark.uat` (excluded from default pytest runs); CliRunner for Typer commands; `from cli import app` works via the conftest sys.path shim.
- **Production-safety:** `[NEEDS USER APPROVAL]` markers throughout the plan gate every prod-touching step.

## Skills you'll likely use

- **`superpowers:executing-plans`** — the plan was written for this. **Start here.** Loads the plan, executes in batches with checkpoints.
- **`/beads`** — task tracker.
- **`/linear`** — for Linear ticket updates as you complete sub-tasks.
- **`/postgres`**, **`/mongodb`** — for any Mongo data inspection (e.g., querying USLI emails for the C.7 lookup helper's tests).
- **`/aws`** — for SSM, Param Store, EC2 inspection.
- **`/google-workspace`** — Gmail draft creation (G.5 customer comms).

## Your first response to Craig

After you've absorbed everything:

1. **Confirm context** with a one-paragraph summary back to Craig — what's been done (specifically the 14 commits + 2 architecture artifacts shipped today), what's next (C.5 → C.7 → D.x → E → G → H). Mention 2–3 specific things you internalized to demonstrate you actually read the artifacts. Examples: "I see C.4's letter_name filter is the smoking-gun fix for ActionId 67's 25 templates" or "I noted the C.7 helper needs to handle the LOB-prefix → Unisoft-LOB mapping (MGL→CG, MPL→CP, ...) which isn't yet in the fixture" or "I see the deterministic-lookup architecture drops the Indemn USLI Needs Review folder entirely".

2. **Confirm the next task is C.5** (`should_upload_pdf` whitelist + `classify-usli-state` CLI). It's the next non-blocked task on the punch list and it's self-contained (~30 min, mock-driven tests). Don't pivot to anything else without explicit instruction.

3. **Use `superpowers:executing-plans`** to drive task-by-task execution. Each task in the plan has bite-sized steps with TDD discipline (failing test → implement → run-pass → commit). Frequent commits, atomic changes.

4. **The 32 new tests pass locally** (other test failures are pre-existing Atlas-connection issues on local Mac, not regressions). Verify you can run the test suite cleanly before starting C.5.

Don't try to ship multiple phases in one session. Get C.5 → C.7 → C.6 cleanly, then check in. D.2 is the next big chunk (skill rewrite). Pace it.

Welcome to the project.
