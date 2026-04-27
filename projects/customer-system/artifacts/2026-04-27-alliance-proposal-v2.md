---
ask: "Generate Alliance v2 Proposal — the deliverable for Cam, produced by the Artifact Generator (played by Claude in this trace) from the hydrated Alliance entity graph + PROPOSAL Playbook + raw source content (v1 proposal, Capability Document, Apr 7-8 prep thread, Apr 8 pivot meeting)."
created: 2026-04-27
workstream: customer-system
session: 2026-04-27-alliance-trace
sources:
  - type: os
    ref: "Proposal v2 entity 69efbd174d65e2ca69b0dd70 (Alliance, drafting → internal_review)"
    description: "The Proposal entity this Document renders"
  - type: os
    ref: "Phase 1 (Retention Associate compound) 69efbd344d65e2ca69b0dd72; Phase 2 (Lead Capture) 69efbd354d65e2ca69b0dd74; Phase 3 (Service expansion) 69efbd354d65e2ca69b0dd76"
    description: "The Phases inside Proposal v2"
  - type: os
    ref: "Touchpoints across the Alliance timeline: Feb 1 discovery, Feb 11 v1 send, Feb 19 Capability Doc, Apr 7-8 prep thread, Apr 8 renewal-wedge pivot, Apr 21 BT Core thread"
    description: "Timeline source — every customer-facing and internal interaction that shaped the proposal"
  - type: os
    ref: "Operations + Opportunities + CustomerSystem + Decisions + Signals + Commitments linked to Alliance Company 69e41a82b5699e1b9d7e98eb"
    description: "Structured intelligence the Artifact Generator reads to populate the document"
  - type: drive
    ref: "1KDeMtV3f1wbexq0KkZNZp7AGZCjYS7t0awz3CPCUj9I"
    name: "v1 Alliance proposal (Feb 11 2026) — basis for v2 structure + tone"
  - type: slack
    ref: "F0AGS9LL064 in #customer-implementation; PDF in DM with Ryan"
    name: "Capability Document — 2,156 call recordings analyzed, 20 engagement types, drives the customer-specific data in v2"
  - type: slack
    ref: "thread #customer-implementation parent ts 1775611051.296399"
    description: "Apr 7-8 prep thread — Retention Associate framing, compound outcome packaging, BT Core integration approach, Peter's data validation"
  - type: drive
    ref: "1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph (Cam's proposal folder)"
    description: "Examples for proposal style — Branch, Johnson, GIC, Charley, Physicians Mutual proposals all follow the same outcome-anchored, phased, Crawl-Walk-Run pattern"
playbook: "PROPOSAL stage Playbook 69efbcf34d65e2ca69b0dd6e"
---

# Strategic Partnership Proposal v2: Renewal Stewardship as Your Wedge

**A Proposal Prepared for:**
Christopher Cook, CEO
Alliance Insurance Services
Winston-Salem, NC

**April 27, 2026**

*Supersedes the February 11, 2026 Strategic Partnership Proposal: Your Digital Workforce Roadmap.*

---

## Why This Version

In our April 8 conversation, you described a sharper ask than the original Crawl-Walk-Run roadmap could land cleanly. With nine new hires absorbing your team's onboarding bandwidth, you wanted something tighter to start. You wanted to take the highest-leverage piece — Producer-led renewals — and use it as the wedge to prove value before broader rollout.

This v2 reorders around that wedge. Same ultimate destination as v1; different starting point.

**v1 framed lead capture as Phase 1 (the missed-calls bleeding).** **v2 frames Producer renewal stewardship as Phase 1** because:

1. It's the operational pain you proactively reached out about — the ask you sent alongside the v1 proposal still sitting open.
2. It demands less change-absorption from your team than rolling out a customer-facing voice associate; the work happens on the Producer side and inside your existing renewal cadence.
3. It establishes the BT Core data foundation we need anyway for Phases 2-3 — building it for renewals lights it up for everything that follows.
4. With Main Street America and NGM Insurance exiting the NC market, you have a high-urgency cohort of policies to target first. Real proof on real renewals in the first 60 days.

The lead-capture work (v1 Phase 1) becomes Phase 2 of v2. The service expansion (billing, COIs, knowledge) stays as Phase 3. The Crawl-Walk-Run is intact — just resequenced.

---

## What We're Solving — Grounded in Your Data

Our analysis of 2,156 of your call recordings (1,543 substantive, classified into 20 engagement types) gave us a structured picture of what your team is actually doing every day. Combined with your team's data validation, we have specific, verified numbers to work from — not industry-typical estimates.

**Your operational reality, by the numbers:**
- **9,516 accounts** across personal + commercial lines
- **16,744 policies** in force
- **3,946 policies** renewing in the next 90 days
- **56.3%** of accounts mono-line; **43.7%** multi-line
- **20+** carriers actively used (Progressive, Auto Owners, Cincinnati, National General, Penn National, Westfield, SafeCo, USLI, NC Grange, Hartford, Utica National, and more)
- **77%** of substantive inbound calls end without resolution (callback_needed) — the single biggest value leak across every engagement type
- **Roughly 100 calls/week** unanswered — approximately **$260K+/year** in revenue at risk on missed connections alone

**Where the renewal/rate-review work fits:**
- 8.5% of inbound call volume (133 calls in our sample) is rate-review or renewal-related
- Heavy carrier-exit work (Main Street America, NGM Insurance) compounds the volume
- Per-Producer view today is limited to your top 100 accounts (~1,100 of ~8,900 mapped); the remaining ~7,800 accounts have no per-Producer renewal cadence visible
- Stewardship prep is manual: each Producer assembles their own snapshot for each renewal call

**Christopher, this is what you described in your April 7 note: consistent renewal-prep snapshots without manual Producer write-ups, plus an auto-generated client-facing pre-review email off the same snapshot. We can stand that up.**

---

## Phase 1: The Wedge — Retention Associate (Compound)

**Months 1-2 — $2,500/month, month-to-month**

The Retention Associate isn't a single bot. It's a *compound outcome* — multiple AI Associates working as one, coordinated across a unified intelligence layer. Specifically:
- **Inbox Associate** skill — parses Producer email patterns, extracts interaction frequency + open requests + endorsement/claims signals
- **Knowledge Associate** skill — assembles per-account snapshots from BT Core + carrier portal data + policy/claim history
- **Custom orchestration** — composes the prep doc + drafts the pre-review email + runs the persistence cadence across the Producer's book

**What it does on Day 1:**
- For each account renewing in the next 30/60/90 days, assembles a **renewal stewardship snapshot**: coverage, # policies, policies-by-carrier, recent endorsements, claims activity, last-touch dates, open items.
- Drafts a **client-facing pre-review email** off the same snapshot — ready for the Producer to review, edit, and send.
- Runs an agreed **persistence cadence** — if the client doesn't respond by day N, the system surfaces the case to the Producer (or, in later iterations, follows up directly).

**Outcome targets at 60 days:**
- Producer prep time per renewal cut from ~30 minutes to ~5 minutes (manual write-up replaced by review-and-send)
- Pre-review email response rate measured and reported
- Carrier-exit cohort (Main Street America, NGM) covered first as the high-urgency proof set
- Per-Producer renewal cadence established for all accounts (not just top 100)

### What we need from Alliance to make Phase 1 work

**BT Core integration (Connected App OAuth — the cleanest path):**
Your team creates a Connected App on the Alliance Salesforce/BT Core org and shares OAuth credentials with us. We pull policies, renewals, claims, and client records from our backend — no Salesforce account or license needed on our side. Real-time, secure, industry-standard.

If your team prefers not to grant direct access, we have alternatives (scheduled exports, or a middleware push via Workato / Zapier). We'll work with your team on the option that fits your IT comfort level.

**A 30-minute Producer walkthrough** to map the existing renewal-prep workflow per Producer + identify the snapshot fields most useful in the wild (vs. what we infer from the data).

That's it. No rollout to your customers. No new systems to learn. Phase 1 sits behind your Producers; they remain the customer-facing voice on every renewal call.

### What we deliver in Phase 1

| Week | Indemn | Alliance |
|---|---|---|
| Week 1 | BT Core connection setup; per-Producer cadence configuration; carrier-exit cohort prioritized | 30-min Producer walkthrough; Connected App created |
| Week 2 | First renewal snapshots generated for the 30-day cohort; first pre-review email drafts surfaced for Producer review | Producers review the first batch; corrections feed the next iteration |
| Week 4 | 60-day cohort live; persistence cadence active; first Producer-time-saved + email-response-rate metrics | 15-min ROI review with Brian and the AI Roundtable |
| Week 8 | 90-day cohort live; Producer training on edit/send patterns; carrier-exit-cohort outcomes reported | Decide expansion to Phase 2 + integration depth for Phase 3 |

---

## Phase 2: Lead Capture (Bilingual)

**Months 3-4 — $2,500/month, month-to-month**

Once the Retention Associate is producing real ROI, Phase 2 addresses the visceral pain from v1: the ~100 missed calls/week.

A bilingual (Spanish + Vietnamese) **Lead Capture Associate** answers business-hour overflow + after-hours calls, captures the 3-5 critical data points (caller, callback number, intent, urgency), and hands the call into your team via Teams / Agency Zoom / your AMS — with a full structured summary and AI-flagged urgency.

This addresses the 77% callback-needed rate from the inbound side: every inbound contact reaches a structured record, not voicemail.

**Outcome target:** reduce 100+ missed calls/week to fewer than 10 unrouted contacts.

---

## Phase 3: Service Expansion

**Months 5+ — $5,000–$10,000/month, 12-month commitment**

Once Phase 1 and Phase 2 are proven, we expand into the **High Automation Tier** identified in our analysis: 24% of your call volume — Follow-up / Status Check, Make a Payment, Document Request (COIs, info updates), and Policy Info Update — all of which have structured workflows + clear resolution criteria + the highest ROI per engineering hour.

Plus **Internal Knowledge Search** across your 72+ organized policy / procedure / training files, which gives every Producer (and the Lead Capture Associate from Phase 2) access to the answers Jessica is currently the only person able to provide.

**Outcome target:** absorb the 24% high-automation tier end-to-end (50-80% automation per engagement type) and free roughly 20+ hours/week of Producer + service-team capacity.

---

## Implementation Roles & Commitment

| Milestone | Alliance Commitment | Indemn Responsibility |
|---|---|---|
| Week 1: Phase 1 Setup | Producer walkthrough; Connected App creation | BT Core connection; per-Producer cadence config |
| Week 2: First Cohort Live | Review first batch of snapshots + pre-review emails | Snapshot generation; email drafting; Producer review surface |
| Week 4: ROI Review | 15-min check-in with Brian and the AI Roundtable | Metrics report (Producer time saved, email response rate) |
| Week 8: Phase 1 → Phase 2 decision | Define Phase 2 scope (full bilingual or English-first) | Phase 2 deployment plan |
| Months 3-4: Phase 2 | Provide carrier escalation contacts | Lead Capture Associate deployment; HITL setup |
| Month 5: Phase 3 decision | Define Tier 1/2/3 service criteria | BT Core deep-integration; Knowledge Search ingestion |

---

## Operational Guardrails (Same as v1)

- **Human-in-the-Loop:** every customer-facing AI output (Phase 2 Lead Capture conversations; Phase 3 service interactions) routes to a human review queue when confidence is below threshold. No "hallucinations" to clients without your team's sign-off.
- **No-Code Control:** your team can update FAQs, eligibility rules, snapshot fields, and email templates in real-time without IT tickets.
- **Insurance-Native:** our Associates are pre-trained on binding authority, surplus lines logic, NC-specific regulations (state-mandated rates, JUA policy terms, Condo Act coverage), and your specific carrier list.
- **Phase 1 month-to-month:** we earn our place every month. No long-term commitment until Phase 3, and only if Phases 1 + 2 prove out.

---

## Investment Summary

| Phase | Core Outcome | Terms | Monthly Investment |
|---|---|---|---|
| 1 — Retention Associate (compound) | Producer time saved + per-account renewal cadence + carrier-exit cohort coverage | Month-to-month | **$2,500** |
| 2 — Lead Capture (bilingual) | Missed-call capture (100+/week → <10) | Month-to-month | **$2,500** |
| 3 — Service Expansion (24% volume tier) | High-automation absorption + 20+ hrs/wk Producer/service capacity recovered | 12-month | **$5,000 – $10,000** |

---

## Next Steps

1. **Approve Phase 1** — sign and we begin Week 1 setup immediately on your return from ISU.
2. **Schedule the 30-min Producer walkthrough** — we map the renewal-prep workflow per Producer.
3. **Authorize the BT Core Connected App** — your IT team and our team coordinate the OAuth setup.

We'd like to ship Phase 1 outputs to your team within 14 days of authorization.

---

## INDEMN SERVICES AGREEMENT

*[Standard SaaS Agreement embedded — terms unchanged from v1: ownership & data, AI oversight (HITL), fees & payment Net-30, 98.9% uptime SLA, mutual indemnity, liability cap at 12 months fees, 60-day termination, NY governing law. Christopher and Brian have the v1 agreement on file; v2 carries the same terms. Available on request.]*

---

## Acceptance & Authorization

By signing below, the Customer agrees to the terms of this Proposal and the Services Agreement.

**For Alliance Insurance Services:**

Signature: ______________________________________________________________________

Printed Name: ___________________________________________________________________

Title:___________________________________________________________________________

Date:___________________________________________________________________________

**For Indemn:**

Signature: ______________________________________________________________________

Printed Name: ___________________________________________________________________

Title:___________________________________________________________________________

Date:___________________________________________________________________________

---
---

# How this proposal was built from the entity graph

*This section is internal — not part of the customer-facing document. It's the line-to-entity mapping that proves every claim in v2 traces back to a real entity in the OS, mirroring the GR Little artifact pattern.*

| Proposal section | Sourced from (entity / Touchpoint) |
|---|---|
| "Christopher described a sharper ask … Producer-led renewals as the wedge" | **Touchpoint Apr 8 (`69efbc914d65e2ca69b0dd5c`)** + **Decision (renewal-wedge pivot, `69efbc914d65e2ca69b0dd5f`)** |
| "Nine new hires absorbing your team's onboarding bandwidth" | **Signal: insight (`69efbc924d65e2ca69b0dd63`)** — bandwidth-constrained customers prefer narrow-wedge proposals |
| "Operational pain you proactively reached out about — the ask you sent alongside the v1 proposal still sitting open" | **Touchpoint Apr 7-8 prep (`69efbc6c4d65e2ca69b0dd4c`)** + **Signal: champion (`69efbc6e4d65e2ca69b0dd55`)** |
| "Main Street America and NGM Insurance exiting the NC market" | **Signal: churn_risk (`69efbbb44d65e2ca69b0dd3a`)** sourced from Capability Document |
| "Lead-capture work (v1 Phase 1) becomes Phase 2 of v2" | **Proposal v1 (`69efba9650cea0a476d6fa9a`)** + the reordering Decision |
| "Our analysis of 2,156 of your call recordings (1,543 substantive)" | **Document: Capability Document (`69efbb1150cea0a476d6fa9f`)** |
| "9,516 accounts / 16,744 policies / 3,946 in next 90 days / 56.3% mono-line / 43.7% multi-line" | **Signal: insight (`69efbc6e4d65e2ca69b0dd57`)** — Peter's data validation Apr 8 |
| "20+ carriers actively used (named list)" | **CustomerSystem: carrier portal cluster (`69efbb604d65e2ca69b0dd1c`)** |
| "77% of substantive inbound calls end without resolution" | **Signal: insight (`69efbbb14d65e2ca69b0dd30`)** — Capability Document headline finding |
| "100 calls/week unanswered = $260K+/year at risk" | **Signal: blocker (`69efb96750cea0a476d6fa80`)** — surfaced at Feb 1 discovery + reinforced in v1 proposal text |
| "8.5% of call volume is rate-review / renewal-related (133 calls)" | **Signal: insight (`69efbbb34d65e2ca69b0dd38`)** — wedge volume context |
| "Per-Producer view today is limited to your top 100 accounts (~1,100 of ~8,900)" | **Signal: blocker (`69efbc6f4d65e2ca69b0dd59`)** — BT Core gate from Apr 8 |
| "Stewardship prep is manual: each Producer assembles their own snapshot" | **Operation: Stewardship/renewal-prep for Producers (`69efbb434d65e2ca69b0dd12`)** |
| "Christopher, this is what you described in your April 7 note" | **Touchpoint Apr 7-8 (`69efbc6c4d65e2ca69b0dd4c`)** + **Decision: Retention Associate framing (`69efbc6c4d65e2ca69b0dd4f`)** |
| **Phase 1 — Retention Associate compound = Inbox + Knowledge + custom skills** | **Phase 1 (`69efbd344d65e2ca69b0dd72`)** with associates field = [Renewal AT, Inbox AT, Knowledge AT] + **Decision: compound outcome (`69efbc6d4d65e2ca69b0dd51`)** |
| "BT Core integration via Connected App OAuth (or scheduled exports / middleware push as alternates)" | **Decision: BT Core OAuth (`69efbc6d4d65e2ca69b0dd53`)** + **CustomerSystem: BT Core (`69efbc6b4d65e2ca69b0dd4a`)** |
| "30-min Producer walkthrough" | **Operation: Stewardship/renewal-prep (`69efbb434d65e2ca69b0dd12`)** — matches the Apr 7-8 prep thread's Tasks for Producer-side mapping |
| **Phase 2 — Lead Capture Associate (bilingual; Spanish + Vietnamese)** | **Phase 2 (`69efbd354d65e2ca69b0dd74`)** + **Opportunity: missed-call capture (`69efbbad4d65e2ca69b0dd26`)** + v1 Phase 1 (preserves the Spanish/Vietnamese language commitment from v1) |
| **Phase 3 — Service Expansion (24% volume tier)** | **Phase 3 (`69efbd354d65e2ca69b0dd76`)** + **Signal: insight (`69efbbb14d65e2ca69b0dd32`)** — Phase-1 high-automation tier from Capability Doc |
| "20+ hrs/wk Producer + service-team capacity recovered" | v1 proposal text — same outcome metric carried forward (Phase 2 of v1 was framed at 20+ hrs/wk recovered) |
| "Internal Knowledge Search across your 72+ organized files" | v1 proposal text — same KB scope referenced |
| "NC mandates / JUA / Condo Act / state-mandated rates" | **Document: Capability Document (`69efbb1150cea0a476d6fa9f`)** — Required Knowledge sections per engagement type |
| Implementation Roles & Commitment table (Brian + AI Roundtable) | **Contact: Brian Leftwich (`69efb8f450cea0a476d6fa6b`)** + v1 proposal text (Brian was named as point for the 60-day Checkpoint Call) |
| "Carrier escalation contacts" | **Commitment Brian (`69efb96650cea0a476d6fa7c`)** — open commitment from Feb 1 (computer/IT readiness check); related to escalation routing |
| Operational Guardrails (HITL, No-Code Control, Insurance-Native, Phase 1 month-to-month) | **Document: v1 proposal (`69efba5f50cea0a476d6fa8e`)** — same guardrails carried forward |
| Investment Summary table | **Phase 1/2/3 entities** — investment + investment_period + commitment_months pulled directly from each Phase entity |
| SaaS Agreement reference | v1 proposal (`69efba5f50cea0a476d6fa8e`) — embedded SaaS Agreement carried over |

**Trace fidelity:** every quantitative claim, named operation, named carrier, named Producer commitment, and Phase pricing/term in this proposal traces to a specific entity in the Alliance constellation. The Artifact Generator (Claude in this trace) read those entities + the PROPOSAL Playbook's `artifact_intent` and produced this document as the rendering. Same mechanism every stage: only the Playbook record changed.
