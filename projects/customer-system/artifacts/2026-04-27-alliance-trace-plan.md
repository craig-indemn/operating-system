---
ask: "Plan the Alliance v2 proposal trace before executing — sources, what gets written to the OS, sequence, questions for Craig. Reference document for the session and for future trace work on other customers."
created: 2026-04-27
workstream: customer-system
session: 2026-04-27-alliance-trace
sources:
  - type: conversation
    description: "Craig + Claude alignment Apr 27 after vision/roadmap crystallization, before executing the Alliance v2 trace"
  - type: local
    ref: "projects/customer-system/vision.md"
    description: "The vision this trace exercises"
  - type: local
    ref: "projects/customer-system/roadmap.md"
    description: "Phase A2 — Alliance proposal trace is the second shake-out"
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-24-trace-plan-and-design-notes.md"
    description: "The GR Little trace plan template that this builds on"
---

# Alliance v2 Trace — Plan

This document captures the plan for tracing Alliance Insurance end-to-end through the OS to produce a v2 (revised) Proposal artifact for Cam. The trace is **Phase A2** in the customer-system roadmap — the second shake-out trace after GR Little (A1, done 2026-04-24, Kyle validated). This plan was written before executing so the approach is reviewable; the trace itself is documented in the companion `2026-04-27-alliance-trace.md` artifact (forthcoming).

## What "trace" means

A trace is **not a bulk data load.** It is a step-by-step walk through how the customer system would actually work if running per the vision. At each step:

- **Trigger** — what entity changed, what watch fired
- **Associate** — which AI actor would run
- **Inputs** — what entities exist + what raw source content is available
- **Outputs** — what new entities the associate creates
- **Gaps** — when an associate or capability is needed but doesn't exist yet

Claude-in-this-conversation plays each associate's role. The trace produces a real entity graph in the OS, but the path the data takes mirrors the autonomous flow we're designing toward. Where an autonomous capability is missing (Slack ingestion, Option B source pointers, the Apr 8 meeting transcript not being in the OS), the gap is documented and the trace continues with the manual reconstruction.

This is how we validate the vision against a real customer, not how we shortcut to a hydrated graph.

## Sources I have in hand

| Source | Form | Date | Where |
|---|---|---|---|
| **Alliance v1 proposal** | Google Doc + PDF | Feb 11 | Drive `1KDeMtV3f1wbexq0KkZNZp7AGZCjYS7t0awz3CPCUj9I` (Doc) + `17rqhqLbQfT5moIgtG2FIKGYHPKff8C77` (PDF). Full text pulled. |
| **Capability Document** | Markdown (Slack file) + PDF (Slack DM) | Feb 18-19 | Slack file `F0AGS9LL064` in `#customer-implementation`. Craig's analysis of 2,156 phone recordings → 20 engagement types. 683 lines / 42KB. Saved to `/tmp/alliance-capability-doc.md`. |
| **Feb 1 discovery call summary** | Slack message (kyle intelligence bot) | Feb 1 | `#customer-success-working` ts `1770090453.076719`. Christopher + Brian + Kyle. Lists 5 Indemn commitments + 1 Brian commitment + 1 Christopher commitment. |
| **Apr 7-8 Retention Associate / "compound outcome" thread** | Slack thread | Apr 7-8 | `#customer-implementation` parent ts `1775611051.296399`. Kyle frames Retention Associate, Cam coins compound outcome, Craig + Jonathan + Dhruv + Peter weigh in. Includes Peter's data validation with real account/policy numbers. |
| **Apr 8/9 actual meeting with Christopher** | NOT in OS, NOT in Slack | Apr 8/9 | Likely on Apollo/Granola only. The renewal-wedge pivot meeting itself. Pre-thread is rich enough to reconstruct what was likely discussed. |
| **Apr 21 mpdm Cam/Kyle/Craig** | Slack message | Apr 21 | `C0A3B18LY07` ts `1776732900.102669`. Cam packaging EXEC docs for daily sync. |
| **Apr 21 BT Core integration emails (2)** | Email entities in OS | Apr 21 | `69ea550d0a2b41b769607126` + `69ea5844a25d34b927d7405f`. **Misclassified** to wrong Companies (Bug #16 manifestation). Subject: "Re: Indemn/Alliance - Exciting project with BT Core data". |
| **Existing OS state** | MongoDB | various | Canonical Alliance Company `69e41a82b5699e1b9d7e98eb`. Deal `ALLIANCE-2026` at `proposal` stage with renewal-wedge `next_step`. Zero Contacts/Meetings/Documents/Touchpoints/Operations/Opportunities/Proposals/Phases linked to Alliance currently. |
| **Apr 25 session handoff + design rationale Alliance Test** | Project artifacts | Apr 22-25 | Pre-articulated picture of Alliance state. Used as ground truth where source material is missing (e.g., for the Apr 8 meeting reconstruction). |

## Sources I do NOT have but would matter

- The Apr 8/9 actual meeting transcript with Christopher (likely Apollo/Granola)
- The full Kyle ↔ Christopher email thread (Christopher's stewardship request note from Apr 7 referenced in the Slack thread)
- The Feb 1 meeting transcript itself (only have the auto-summary)
- Alliance's "72+ organized policy/procedure files" referenced in v1 proposal (no inventory found)

These gaps are first-class trace findings.

## What gets written to the OS — by entity type

The full hydration is comprehensive (~50+ entities). Each is created by an associate (played by Claude) at the appropriate step in the trace, NOT pre-loaded.

### Group A — Refine canonical Company (`69e41a82b5699e1b9d7e98eb`)

Currently: just `name: "Alliance Insurance"`, `type: Broker`, `stage: pilot`. Will add structured fields as discovered through the trace:
- Location (Winston-Salem NC) — discovered in Capability Document
- Domain, website — needs verification
- Real account/policy counts (9,516 / 16,744) — discovered in Apr 7 thread (Peter's data validation)

### Group B — Contacts (~6-8)

Created by **Email Classifier** on first email encounter, or by **Touchpoint Synthesizer** when extracting meeting participants:

- **Christopher Cook** (CEO, decision-maker, primary signer) — surfaces in Feb 1 meeting + Feb 11 proposal recipient + Apr 7 thread mentions
- **Brian Leftwich** (operating lead, point of execution) — surfaces in Feb 1 meeting commitment ("Brian to check Alliance computers")
- **Jessica** (only bilingual commercial agent — operator-level) — surfaces in Capability Document edge cases
- 3-5 others from Feb 1 meeting (need to surface from richer sources)

### Group C — Documents (3+)

Created by **Touchpoint Synthesizer** when attachments arrive in emails, or by **Document Importer** for standalone Drive files:

- v1 Proposal (Drive Doc + PDF) — `source: drive`, content: full text
- Capability Document (Slack file Feb 19 + PDF Feb 26) — `source: slack`
- Possibly: Alliance's 72+ policy/procedure files

### Group D — Touchpoints (7 confirmed, manually synthesized since Synth associate suspended)

Created by **Touchpoint Synthesizer** when raw data (Email, Meeting, Slack thread) arrives:

1. **Feb 1 — Discovery call** (meeting, external) — w/ Christopher + Brian + Kyle. Source: Meeting entity (would exist if Google Meet ingestion ran in Feb; doesn't today).
2. **Feb 11 — v1 proposal sent** (email, external) — Kyle → Christopher with proposal attached.
3. **Feb 18-19 — Capability analysis** (slack, internal) — Craig analyzing 2,156 recordings then posting Capability Document to #customer-implementation. Produces the Capability Document as artifact.
4. **Feb 26 — Capability doc shared with Ryan** (slack, internal) — Craig DM to Ryan.
5. **Apr 7-8 — Pre-Wednesday-meeting prep thread** (slack, internal) — Multi-team brainstorm producing the Retention Associate / compound outcome framework.
6. **Apr 8/9 — Actual meeting with Christopher** (meeting, external) — The renewal-wedge pivot. Reconstructed from pre-thread + design rationale + Apr 25 handoff since the meeting itself isn't in the OS.
7. **Apr 21 — mpdm Cam packaging for v2** (slack, internal) — Cam staging the proposal-generation thread.

### Group E — Operations (6, derived from Capability Document by Intelligence Extractor)

Created when **Intelligence Extractor** processes the Capability Document Touchpoint:

- Renewal outreach (133 calls/period; Phase 1 of v2 wedge)
- Inbound call handling (1,543 substantive calls/period; 77% callback_needed)
- Quote generation (215 calls; 15+ carrier portals)
- Billing question handling (145 calls)
- Payment processing (135 calls)
- Stewardship/renewal prep (manual Producer write-ups; the specific ask Christopher surfaced Apr 7)

### Group F — CustomerSystem (~10)

Created by Intelligence Extractor when systems are mentioned in Touchpoints:

- BT Core (primary data source; Salesforce-based; integration in dev)
- Applied Epic (AMS — from design rationale)
- Dialpad (phone — no adapter — blocks phone AI)
- Conga Sign, Salesforce, Composio (planned)
- Carrier portals (~20): Progressive, Auto Owners, Cincinnati, National General, Penn National, Westfield, SafeCo, Foremost, USLI, NC Grange, Hartford, Utica National, Northwest Farmers, etc.

### Group G — BusinessRelationship (3-4)

Created when relationships are mentioned in Touchpoints:

- **Pat Klene / 101 Weston Labs** (referrer/network — origin) — appears in Feb 1 commitment ("Present to 101 Weston Labs members") + the v1 proposal mentions "101 Weston Pilot"
- **IIANC** (member, NC independent agents association — implied from NC focus)
- **Everett Cash Mutual** (carrier — from design rationale)
- Carrier ecosystem (the 20+ above)

### Group H — Opportunities (~6-8, mapped to AssociateTypes)

Created by Intelligence Extractor when pain-points-with-product-fit are identified:

1. Stewardship/renewal prep automation → **Retention Associate** (compound = Inbox + Knowledge + custom skills) — the v2 Phase 1 wedge
2. Renewal outreach (low-touch outbound) → Renewal Associate
3. After-hours + overflow missed call capture → Front Desk / Lead Capture Associate
4. Billing question handling → Billing Associate
5. Payment processing → Billing Associate
6. Document generation (COIs, info updates) → Document Associate
7. Internal knowledge search (72+ files) → Knowledge Associate
8. Bilingual capability (Spanish/Vietnamese) → cross-cutting

### Group I — Intelligence entities (extracted from Touchpoints)

By **Intelligence Extractor**, per Touchpoint:

- **Tasks** — ~10-12, lifecycle states from open → completed
- **Decisions** — ~5: renewal-wedge pivot, compound outcome coined, Retention Associate as compound, BT Core via OAuth Connected App, Composio for Producer inbox longer-term
- **Commitments** — ~10 across all touchpoints; both indemn-side and customer-side; each with due_date where known
- **Signals** — ~10-12: health, blocker, expansion, champion, insight, budget; each tied to its source Touchpoint and the Company

### Group J — Proposal v1 + v2

Created by **Artifact Generator** at PROPOSAL stage; v2 supersedes v1:

- **Proposal v1** — version=1, status=`superseded`, source_document=v1 Doc, date_prepared=2026-02-11, date_sent=2026-02-11
- **Proposal v2** — version=2, status=`drafting`, supersedes=v1, date_prepared=today

### Group K — Phases on Proposal v2 (3, narrower than v1, renewal-wedge first)

- **Phase 1: Retention Associate** (compound) — renewal stewardship prep + pre-review email + outreach cadence. Addresses Opportunities 1+2. ~$2,500/mo, month-to-month.
- **Phase 2: Lead Capture Associate** (after-hours + overflow; bilingual) — Addresses Opportunity 3. TBD pricing.
- **Phase 3: Service expansion** (billing + COIs + knowledge) — Addresses Opportunities 4-7. $5K-10K/mo, 12-month commitment.

### Group L — Reclassify the 2 misclassified Apr 21 emails

Currently linked to wrong Companies (Bug #16 evidence). Touchpoint Synthesizer would re-process them once they're correctly classified. New Touchpoint for the Apr 21 BT Core thread.

### Group M — Playbook record for PROPOSAL stage

Created when Deal.stage transitions to PROPOSAL (the Playbook hydration mechanism). Drives the Artifact Generator at PROPOSAL stage. Fields:
- stage, description, entry_signals, required_entities, expected_next_moves, artifact_intent

This Playbook is the template for any future PROPOSAL-stage artifact for any customer.

## Artifacts produced (project files)

1. **This plan** (`2026-04-27-alliance-trace-plan.md`) — saved before executing for review and reuse on future traces.
2. **The trace itself** (`2026-04-27-alliance-trace.md`, forthcoming) — every step from T=0 to T=now with trigger / associate / inputs / outputs / gaps.
3. **The v2 Alliance proposal** (`2026-04-27-alliance-proposal-v2.md`, forthcoming) — the deliverable for Cam. Mirrors v1 structure but with renewal-wedge as Phase 1, real call data from Capability Document, real account/policy numbers from Peter's validation, references the Retention Associate / compound outcome framing.
4. **Updates to spine files** — `os-learnings.md` (gaps), `roadmap.md` (Slack ingestion moved forward), `INDEX.md` (decisions, open questions, artifacts table).

## Sequence of execution

1. **Resolve `indemn` CLI auth.** The system alias points to bot-service's binary (wrong); need to find the correct one and authenticate. Possibly login as Craig.
2. **Set up the trace document** (`2026-04-27-alliance-trace.md`) as a living document we write to as we go.
3. **Walk the trace from earliest event forward**, executing each step as the associate would:
   - For each step: trigger → associate → inputs → outputs (write entities to OS) → gaps documented
   - Reclassify the 2 misclassified emails when we reach Apr 21
   - Reach the PROPOSAL stage and play the Artifact Generator role
4. **Generate the v2 proposal artifact** as the Artifact Generator's output.
5. **Update spine files** per discipline (`os-learnings.md`, `roadmap.md`, `INDEX.md`).

## OS gaps the trace will surface (anticipated)

- **Slack ingestion not built.** Several Touchpoints (capability-doc thread, Apr 7-8 prep thread, Apr 21 mpdm) would normally come from Slack ingestion. Currently impossible. → Slack adapter must move forward in roadmap (was Phase F deferred; needs to be much earlier).
- **Apr 8 meeting transcript missing.** Real meetings happen and don't always end up in the OS. Even with Apollo/Granola, ingestion lag exists.
- **Email Classifier creates wrong Companies.** Bug #16 evidence: 2 Apr 21 emails about Alliance went to wrong Company entities. Entity-resolution capability is the root fix.
- **No Document import for Slack file attachments.** The Capability Document came from a Slack file attachment; the autonomous path for Slack file → Document entity isn't built.
- **No backfill mechanism.** Even if associates were running today, they wouldn't process historical Touchpoints (Bug #10).
- **Touchpoint source pointers (Option B) not implemented.** Will surface when the trace tries to navigate from a synthesized Touchpoint back to source content.

These gaps get logged to `os-learnings.md` as the trace surfaces them.

## Open questions

- **Scope of Phase 2/3 in v2 proposal.** Tight (Phase 1 only, hint at the rest) or comprehensive (all 3 phases like v1, with Phase 1 the visceral wedge)? *Current lean: 3 phases, Phase 1 dominant.*
- **Where does the Apr 8 meeting Touchpoint get its content** if the meeting transcript isn't in the OS? *Current lean: reconstruct from pre-thread + design rationale + Apr 25 handoff, citing those as sources.*
- **How does the Artifact Generator access the v1 proposal text** to inform v2 generation? In real life: the Document entity has `content` field for text-based files; the Generator queries the Document and reads it. For the trace: Claude already has the v1 text in context.
- **Do we create CustomerSystem entities for all 20+ carriers** or just the ones operationally most material (BT Core, Applied Epic, Dialpad, top carriers)? *Current lean: all of them — they're all real and the model says entities are cheap.*

## Why this artifact exists going forward

The structure of this plan applies to any customer trace. Future Alliance updates (v3, post-meeting), Arches trace, FoxQuilt trace, or any new prospect onboarding all follow this shape:

1. Inventory what sources exist
2. Map each source to which entity creation step it would feed
3. Walk the trace step-by-step playing each associate
4. Document gaps as they surface
5. Render the artifact appropriate to the current stage

This document is the template. Reference it when starting any future trace.
