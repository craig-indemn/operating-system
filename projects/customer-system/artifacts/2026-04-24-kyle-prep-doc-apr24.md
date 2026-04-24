---
ask: "Preserve Kyle's Apr 24 OS Collaboration Prep doc as durable context — treat as aspirational signal about desired outcomes, not as implementation spec"
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
sources:
  - type: google-doc
    ref: "1yAt-IopSeiJMRW8SVYlJpQOVar7zYwsCEbufXqHsFkA"
    name: "OS Collaboration Prep — Kyle+Craig Sync Apr 24"
---

# Kyle's Apr 24 Prep Doc — Preserved (read as signal, not spec)

Kyle's three-part prep doc written overnight before the Apr 24 sync. He wrote it using Claude Code. Saved here as context.

**Important:** This is aspirational signal about what Kyle wants to *see* from the system, not a requirements spec. Per Craig's framing (`2026-04-24-alignment-framing.md`), we do not treat the field names, enums, or phase deadlines as contract. We treat the underlying *intents* (extraction quality, provenance, outcomes visible to Kyle) as signal.

---

## Kyle's framing (verbatim)

> Purpose: three pre-built artifacts so tomorrow's sync goes from "discover the spec live" to "compare and iterate." Kyle produced these against yesterday's two real calls (Foxquilt CEO exec + GR Little discovery) to give Craig a concrete target for the OS extraction.
>
> Contents:
>   PART 1 — Pre-extraction of the two Apr 22 transcripts into structured data (the "here's what I think should come out of a call" baseline).
>   PART 2 — V1 Extraction Spec: the canonical fields every customer/prospect call should yield.
>   PART 3 — Project Plan: three-phase OS build schedule with deliverables.
>
> The test tomorrow: run both Apr 22 transcripts through the OS, compare its output to Part 1 below, and iterate the spec. Where Kyle's version and the OS output differ, that's the conversation.
>
> End framing: "Craig reads this before tomorrow's sync; Kyle adds anything missing; sync starts with 'where do we disagree' instead of 'where do we start.'"

## Part 1 — Kyle's JSON extractions (summary)

### FoxQuilt + Karim Jamal CEO exec call

- Meeting: customer_call / exec_discovery, Apr 22 60 min
- Attendees: Kyle, Nick Goodfellow (champion, VP Insurance Ops), Karim Jamal (exec_sponsor, CEO, ex-CFO/ex-Aviva), George Remmer, Craig
- Company: FoxQuilt (MGA_MGU), 400 inbound inquiries/mo, 3 brokers, $1500 avg premium, 20K customer book. Network anchor to GIC/Granada.
- Deal state: playbook_stage 3→4, pipeline_status CONTACT→DEMO, icp_tier CUSTOM_STRATEGIC, gtm_segment DIGITAL_PRODUCT, focus_account, warmth hot, primary_outcome efficiency
- Decisions: 60-90 day no-cost trial locked; Two-phase pilot (30d web/voice, 30-90d Stripe); 3 Associates in scope; pricing options; internal escalation path
- Commitments: Kyle follow-up after Nick+Karim sync (Apr 24); Kyle+Cam ship proposal (Apr 30); FDE decision Jonathan vs Craig (Apr 24); Nick→Paige approval; Nick mentions Indemn to David Nalt Thursday
- ROI stated: $35K annual efficiency, 30% deflection 90d, 85% automation with API
- Technical: AMS=Epic, email=Gmail, DW=BigQuery (no public API), Stripe PCI hard-no, Strata voice incumbent (surround-displace)
- Surfaced opportunity (PARKED): Stripe widget as reusable MGA Payment Associate product
- Provenance chain: Mar 25 warm_intro (Luge Capital) → Mar 30 ITNY → Apr 17 Nick (2→3) → Apr 22 Karim (3→4)
- Close path: "conference + investor-intro (28 days)"

### G.R. Little + Walker Ross discovery call

- Meeting: customer_call / first_discovery, Apr 22 30 min
- Attendees: Kyle, Walker Ross (champion_candidate, 3rd-gen CORE Team Manager, CPCU/CIC/AAI/ARM/CISR), Heather F
- Company: G.R. Little Agency (BROKER), Elizabeth City NC, 120 years, 3rd gen family-owned (Monty=Principal, Julie=VP, Walker+Wyatt=3rd gen), 35 employees, 65% personal / 35% commercial, NCIUA wind pool niche
- Tech stack: HawkSoft AMS, AgencyZoom, Cognito, Gaia, LightSpeed, GloveBox (10-15% active)
- Deal state: null→2 DISCOVERY, icp_tier STANDARD_AGENCY, gtm_segment BROKER_RESOURCES, warmth warm, primary_outcome efficiency, expected_arr_band $18K, close_confidence 20
- Pain points: low digital adoption, manual renewal questionnaires, billing inquiries, no after-hours, weak web lead conversion
- Commitments: Kyle sends notes+recording+deck+NC examples (Apr 23); Walker books demo; Walker confirms demo attendees
- Wedge candidates: after-hours phone / renewal questionnaires / billing inquiries / HawkSoft data entry
- Product fit frame: "Front-door agency Associate only (web chat + voice + email automations). No custom build. Entry-tier pricing."
- Surfaced opportunity (PARKED): agency CC payment on carrier portal — needs ≥3 agencies surfacing before productizing
- Provenance chain: Mar 31 calendly_inbound → Apr 22 Walker+Heather (0→2)
- Close path: "calendly_inbound (single-agency, lower-velocity)"

## Part 2 — V1 Extraction Spec

Kyle's proposed canonical fields (summarized):

**Meeting-level:** meeting_id, meeting_type (customer_call/internal/prospect_discovery/partner_call), sub_type (first_discovery/follow_up/exec_discovery/demo/proposal_review/pilot_checkpoint/contract_negotiation), occurred_at, duration_min, attendees[]

**Attendee shape:** name, side (indemn/buyer/partner/other), role, relationship_tag (champion/exec_sponsor/champion_candidate/influencer/attendee/blocker), family_member (bool), background

**Company-level:** name, type (MGA_MGU/BROKER/CARRIER/OTHER), location, scale (free shape), channels, tech_stack (free shape), network_anchor (anchor_customer, relationship, strategic_value)

**Deal-state:** playbook_stage_before/after (int 0-8), stage_name_after, pipeline_status_before/after (CONTACT/DISCOVERY/DEMO/PROPOSAL/NEGOTIATION/CLOSED), icp_tier (CUSTOM_STRATEGIC/STANDARD_AGENCY/STANDARD_MGA/ARCHIVE), gtm_segment (DIGITAL_PRODUCT/BROKER_RESOURCES/AGENT_NETWORK), focus_account (bool), warmth (hot/warm/cool/cold), primary_outcome (revenue/efficiency/retention/strategic_control), secondary_outcomes[], expected_arr_band, close_confidence (0-100)

**Event-derived:**
- decisions[] — plain string sentences
- commitments[] — {owner, owner_side, action, due, type enum}
- next_steps[] — same as commitments but forward-looking
- pain_points[] — plain strings (discovery calls)
- wedge_candidates[] — plain strings (scoping calls)
- roi_stated — free shape
- technical_constraints — {ams, dw, email, hard_moats[], existing_incumbents[]}
- surfaced_opportunities[] — {ref, description, priority, prerequisite}
- provenance_chain[] — {date, type, from[], org, counterpart, stage_transition}
- close_path_template — one-line string
- success_plan — {current_stage, next_gate, pilot_kpis[], expansion_path, upsell_ceiling}
- signals — {positive[], watch[], negative[]}

**Quality checks Kyle wants the OS to run:**

1. Every commitment has owner + due + type
2. Every decision is verifiable against the transcript (quote if ambiguous)
3. Stage transitions match Prospect Playbook schema (0-8)
4. If company is in existing customer's network, network_anchor populated — do not silently drop
5. Surfaced opportunities go to Opportunity Registry, never silently absorbed into proposal
6. Provenance chain is cumulative — each meeting adds, never overwrites

## Part 3 — Kyle's three-phase plan

### Phase 1 — One customer end-to-end (this week)
Goal: Alliance proposal generated by OS from real Gmail + Google Meet + Drive data.

Deliverables (all Kyle-written, all by Fri Apr 25):
- Gmail ingestion for Alliance contacts (live)
- Meeting ingestion for Alliance (backfill + ongoing)
- Drive doc ingestion for Alliance proposals
- Touchpoint timeline rendered for Alliance
- Company → Opportunities → Proposal draft generated by OS
- Extract Apr 22 Foxquilt + GR Little transcripts; compare to Part 1
- V1 extraction spec locked after comparison (Thu Apr 24 sync)

### Phase 2 — Executive dashboard (next week, Apr 28 – May 2)
Goal: Cam opens one view and sees close-now customers, owner, stage, days-since-last-touch, next step, blockers.

### Phase 3 — Per-stage extraction (week of May 5)
Goal: OS handles customer at any of 9 Playbook stages.
- First "persistent AI Prospect Associate" skill wired to dashboard — drafts next-step email per deal on a cron

### Done-ness tests Kyle proposes

- Phase 1: Craig generates Alliance proposal using only OS data. Kyle reads it side-by-side with Feb 3 real proposal. OS version doesn't have to be better; has to be recognizable.
- Phase 2: Cam opens dashboard without help and names three things he'd change. Those three things are spec for v1.1.
- Phase 3: Given random real deal, OS produces (a) current stage, (b) next move with owner+due, (c) draft artifact for that move. Success = Kyle approves draft with ≤2 edits.

## Our response (per alignment-framing.md)

**We do not treat this as a spec.** We treat it as signal about outcomes Kyle wants to see:

- Rich structured data from every call → we already extract Tasks/Decisions/Commitments/Signals via Intelligence Extractor. Kyle's JSON shape is a VIEW across entities, not a new entity.
- Follow-up emails auto-drafted → THIS is the concrete ask from Apr 23. Today's goal.
- Dashboard for close-now customers → Phase 2 work, uses existing auto-generated entity views.
- Per-stage extraction + persistent agents → long-term, emerges from real data in the entities.

**Fields in Kyle's spec we don't currently model and may or may not add:**

| Kyle's field | Our current model | Decision |
|---|---|---|
| icp_tier (CUSTOM_STRATEGIC / STANDARD_AGENCY / STANDARD_MGA / ARCHIVE) | Not modeled | Defer. If it proves load-bearing in Playbook, add as Company or Deal field. |
| gtm_segment (DIGITAL_PRODUCT / BROKER_RESOURCES / AGENT_NETWORK) | Not modeled | Defer. |
| focus_account (bool) | Not modeled | Defer. May be a Deal filter or a Company flag. |
| close_confidence (int 0-100) | We have computed `probability` from stage | Defer. Stage-derived probability is sufficient. |
| close_path_template | Not modeled | Defer. Pattern we'll see in data over time. |
| meeting sub_type (enum) | Not modeled | Defer — extraction could classify. |
| playbook_stage (int 0-8) | Deal.stage enum | Duplicate of our existing field. Kyle can number them if useful for UI. |
| pipeline_status (enum) | Deal.stage enum | Duplicate of our existing field. |
| network_anchor.strategic_value | BusinessRelationship entity exists but no strategic_value field | Absorb into BusinessRelationship.type or new field when needed. |
| roi_stated | Not modeled | Will emerge from extraction — attach to Opportunity or Phase. |
| wedge_candidates[] | Closest is Opportunity | Pre-Opportunity artifact; candidates become Opportunities when narrowed. |
| surfaced_opportunities with "PARKED" priority | Opportunity state machine: identified → validated → proposed → addressed → resolved | Our "identified" state covers PARKED. Could add "parked" as sub-state later. |
| provenance_chain[] | Derivable from Touchpoints on Company | Derived view, not stored redundantly. |
| success_plan object | Mix of Deal + Phase + Opportunity fields | Derivable. |

**The quality checks Kyle lists (6 items)** — these are extractor quality rules. Worth adding to the Intelligence Extractor skill once we have the Playbook defined.
