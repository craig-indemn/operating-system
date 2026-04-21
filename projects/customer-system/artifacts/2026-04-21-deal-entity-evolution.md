---
ask: "Design the Deal + SuccessPhase entity model for Kyle's prospect tracking needs"
created: 2026-04-21
workstream: customer-system
session: 2026-04-21-a
sources:
  - type: local
    ref: "projects/customer-system/artifacts/context/kyle-exec/"
    name: "Kyle's EXEC folder (INDEX, PLAYBOOK-v2, DICT-SALES-v2, PROSPECT-SIX-LEADS-v0, etc.)"
  - type: google-drive
    ref: "1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph"
    name: "Cam's Proposals folder (Alliance, Branch, Johnson, GIC, Charley)"
  - type: live-system
    description: "CLI inspection of live OS entities (Deal, Meeting, Task already deployed)"
---

# Deal Entity Evolution + SuccessPhase

## Context

Kyle, Cam, and Craig aligned on April 20: the customer system focuses first on prospects. Kyle wants to see his close-now deals with current state, next steps, and owners. He has 6 leads ready to ingest (FoxQuilt, Alliance, Amynta, Rankin, Tillman, O'Connor).

Kyle's documents (saved in `artifacts/context/kyle-exec/`) define the full sales motion — stages, signals, cadence, per-deal success paths, data ingestion mechanisms, and the associate's job per deal. Cam's proposal folder shows how deals are structured in practice — customer-specific, outcome-anchored, phased.

This artifact captures what needs to change in the live OS to support Kyle's immediate ask.

## Current State (Live OS)

**Deal entity exists** — deployed April 18 with 0 records. Has:
- company (→ Company), name, primary_contact (→ Contact), owner (→ Actor)
- expected_arr, primary_outcome (enum), source (enum), source_conference (→ Conference)
- 5 scoring dimensions (company_fit, relationship, eagerness, use_case, milestone)
- warmth (enum), follow_up_date, competitive_notes, lost_reason, notes
- State machine: contact → discovery → demo → proposal → negotiation → verbal → signed → lost/parked

**What's missing for Kyle's immediate need:**

| Field | Why Kyle Needs It |
|-------|-------------------|
| `deal_id` | Human-readable key like FOXQUILT-2026 — scannable in Slack, email, conversation |
| `next_step` | The ONE thing that needs to happen next for this deal |
| `next_step_owner` | Who moves it forward — can differ from deal owner (prevents "nobody moves it") |
| `use_case` | What they want us to solve — the deal's substance, not just stage metadata |
| `proposal_candidate` | Y/N/Maybe flag — Kyle+Cam filter for which deals deserve proposal effort |

**What Kyle's docs describe but we DON'T need right now:**

| Field (from Kyle's DICT-SALES-v2) | Why Not Now |
|---|---|
| `commercialHypothesis` | Useful later for proposal generation. Not blocking the prospect view. |
| `dormantFlag` / `dormantReason` | The OS changes collection already tracks when things go stale. Build staleness detection as a watch/automation later. |
| `whyProposal` / `whatsNeeded` | Good fields for when proposal drafting becomes a workflow. Not blocking. |
| Sub-states (CONTACT.listed / CONTACT.outreached) | The OS state machine doesn't support sub-states natively. The `next_step` field captures the same intent. Can be added as separate fields or as state machine evolution later. |

## What to Change

### 1. Add Fields to Deal

```bash
indemn entity modify Deal --add-field deal_id --type str --unique true
indemn entity modify Deal --add-field next_step --type str
indemn entity modify Deal --add-field next_step_owner --type objectid --is-relationship --relationship-target Actor
indemn entity modify Deal --add-field use_case --type str
indemn entity modify Deal --add-field proposal_candidate --type str --enum-values '["Y", "N", "Maybe"]'
```

### 2. Create SuccessPhase Entity

A per-deal phased progression. Each deal has 2-5 phases describing the path from current state to signed contract.

```bash
indemn entity create --data '{
  "name": "SuccessPhase",
  "collection_name": "successphases",
  "fields": {
    "deal": {"type": "objectid", "required": true, "is_relationship": true, "relationship_target": "Deal"},
    "phase_number": {"type": "int", "required": true},
    "name": {"type": "str", "required": true},
    "entry_criteria": {"type": "str"},
    "expected_outcome": {"type": "str"},
    "go_no_go_signal": {"type": "str"},
    "owner": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "stage": {"type": "str", "is_state_field": true, "default": "not_started", "enum_values": ["not_started", "in_progress", "complete", "skipped"]},
    "notes": {"type": "str"}
  },
  "state_machine": {
    "not_started": ["in_progress", "skipped"],
    "in_progress": ["complete", "skipped"],
    "complete": [],
    "skipped": []
  }
}'
```

### 3. Populate Kyle's 6 Deals

From PROSPECT-SIX-LEADS-v0.md — create these deals with the data Kyle provided:

| deal_id | Company | Stage | Owner | Next Step | Proposal Candidate |
|---------|---------|-------|-------|-----------|-------------------|
| FOXQUILT-2026 | FoxQuilt | demo | Kyle | CEO demo with Karim Jamal Apr 22 | Y |
| ALLIANCE-2026 | Alliance Insurance | proposal | Marlon | Lock May meeting; pricing approval | Y |
| AMYNTA-GRD360-2026 | Amynta | discovery | Kyle | Post-demo debrief, ICP confirmation | Y |
| RANKIN-2026 | Rankin Insurance | signed | Kyle | Formalize expansion contract | Y |
| TILLMAN-2026 | Tillman Insurance | discovery | Kyle | Verify actual state — did go-live happen? | Y |
| OCONNOR-2026 | O'Connor Insurance | signed | Cam | Ground-truth from Cam — retention or expansion? | Y |

Note: Rankin and O'Connor are existing customers with deals for contract conversion (Kyle's "Motion B"). The Company exists; the Deal tracks the sales motion.

### 4. Populate Success Phases (second pass)

Example — FoxQuilt:
1. NDA + pilot scope with Karim sign-off (not_started)
2. Web chat 24/7 deployed on foxquilt.com (not_started)
3. Stripe failed-payment recovery automation (not_started)
4. Certificate issuance automation — surround-displace Strata (not_started)

Example — Alliance:
1. Proposal delivered — Retention Associate (not_started)
2. CSR prep tool deployed (not_started)
3. Coverage-gap identification automated (not_started)
4. Phone AI on Dialpad (not_started — blocked by Dialpad stabilization)

## How Deal and Company Relate

- **Company** = who they are, relationship stage (prospect/pilot/customer/expanding/churned)
- **Deal** = a specific business opportunity being worked through the sales funnel
- A Company can have multiple Deals (initial engagement + expansion)
- When a Deal reaches `signed`, the Company transitions (prospect → pilot, or pilot → customer)
- Kyle's "6 leads" are 6 Deals. FoxQuilt and Alliance are Companies in prospect stage with new-logo deals. Rankin and O'Connor are Companies in customer/pilot stage with expansion/contract-conversion deals.

## What Kyle Gets

After these changes, Kyle can:
- `indemn deal list --format table` — see all deals with stage, owner, next step
- `indemn deal list --proposal-candidate Y` — see only the elevated deals
- `indemn deal get FOXQUILT-2026` — full detail on one deal
- UI: Deal list view with stage colors, owner names resolved, next step visible
- UI: Deal detail with success phases listed, each with status
- `indemn successphase list --deal <deal_id>` — see the phased progression

## Entities We Keep vs Simplify

**Active and useful now:** Company, Contact, Deal (with additions), Conference, Stage, OutcomeType, AssociateType, Task, Meeting, SuccessPhase (new)

**Exist but empty — keep, don't delete:** Commitment, Signal, Decision (these activate when meeting ingestion starts), AssociateDeployment, Outcome, Playbook (these activate for customer delivery tracking)

**Can remove:** TestTask, VerifyTest (test entities from development)

## What This Doesn't Cover Yet (next iterations)

- Meeting ingestion (Google Drive adapter → Meeting entities → intelligence extraction)
- Staleness detection automation (watches on Deals where days since activity > threshold)
- Cadence enforcement (the associate's job per deal from Kyle's playbook)
- Proposal drafting (using Cam's proposal templates + deal data)
- Package entity (7 SKUs × 3 tiers — useful when proposal generation becomes a workflow)
- Implementation entity evolution (investorCohort, readinessCohort, contractStatus from Kyle's CS dictionary)
