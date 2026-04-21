# Sales Data Dictionary

Domain configuration on Craig's operating system kernel · Kyle · April 20, 2026

---

## Purpose

Sales is the funnel sub-system. Moves qualified prospects from operational-pain recognition through staged close to signed contract — including pilot-to-enterprise conversion where a customer is already live without a written contract (Motion B).

**Two motions use the same entity + lifecycle, distinguished by whether an Implementation exists:**
- **New Logo** — prospect moving through CONTACT → WON, Implementation spawned on WON (or PILOT)
- **Customer Contract Conversion** — existing customer has an Implementation; Deal moves funnel to get written enterprise contract

No new `dealType` enum. State pairing (`Deal.stage` + Implementation existence) encodes both motions.

---

## Scope

**IN SCOPE:** active Deal management · Proposal + Contract artifacts as Drive docs linked to Deal · pricing + terms via Deal fields · contract close + handoff signal to CS

**OUT OF SCOPE:** Prospecting (pre-Deal qualification), Customer Success (post-contract delivery, health, expansion signal detection)

---

## Deal entity (extended from Craig's Prisma schema)

**Production stage enum (exact values):**

```
CONTACT · DISCOVERY · DEMO · PROPOSAL · NEGOTIATION · PILOT · WON · LOST
```

**Probability formula (Apr 2 design, formula-driven, not editable):**

```
CONTACT = 5% · DISCOVERY = 15% · DEMO = 20% · PROPOSAL = 30% · NEGOTIATION = 50% · PILOT = 70% · WON = 100% · LOST = 0%
```

**Sub-states (v2, from Prospect Playbook v0):**
- `CONTACT.listed` — Deal created, not yet reached
- `CONTACT.outreached` — first outbound sent, awaiting response
- `PROPOSAL.drafting` — internal alignment on scope + price
- `PROPOSAL.sent` — proposal delivered, awaiting decision

**Fields layered on Craig's Deal:**

- `dealId` (text, human-readable PK): convention `{COMPANY_TAG}-{YEAR}` or `{COMPANY_TAG}-{PRODUCT}-{YEAR}`. Examples: `AMYNTA-GRD360-2026` · `RANKIN-2026` · `FOXQUILT-2026` · `JM-EVENTGUARD-2026`
- `proposalCandidate` (`Y · N · Maybe`): Kyle + Cam elevated-subset filter
- `whyProposal` (text, required when Y): operational-pain-to-outcome narrative
- `whatsNeeded` (text): named blockers to next stage
- **`commercialHypothesis`** (enum, v2): `milestone_rev_share · paid_project · hybrid · unclear`
- `primaryOutcome` (Four Outcomes enum): `Revenue Growth · Operational Efficiency · Client Retention · Strategic Control`
- `proposedAssociates` (array of Associate refs)
- **`proposedPackage`** (Package ref, nullable): from Customer Cohort Baseline — Revenue Capture / Digital Front Desk / Renewal Machine / etc.
- `targetCloseDate` (date)
- `lastStageChange` (date, computed)
- `stageAging` (int days, computed)
- `owner` (Actor ref, named human per Deal)
- **`nextStepOwner`** (Actor ref, can differ from Deal owner — prevents "nobody moves it")
- `nextMove` (text)
- `nextMoveDue` (date)
- **`successPath`** (array of Phase records — per-Deal phased progression, see below)
- **`dormantFlag`** (bool, cross-cutting)
- **`dormantReason`** (enum when true): `silence · regression · stakeholder_turnover · scope_creep · competitive_loss · capacity · explicit_pass · investor_pass`

Expected ARR, closeConfidence, warmth, scoring dimensions already exist on Craig's Deal — reuse as-is.

**Proposal + Contract + Negotiation are NOT separate entities in v2.** Drive doc refs tagged by type on the Deal suffice. Promote if proposal-generation automation (Cam + Craig track) justifies it.

---

## Success Path (per-Deal phased progression, new in v2)

Universal stages are the same for every Deal. Each Deal carries a structured `successPath` array — the bespoke phased route this customer takes within the universal stages.

**Each Phase record:**
- `phaseNumber` (int)
- `name` (text)
- `entryCriteria` (text)
- `expectedOutcome` (text)
- `goNoGoSignal` (text)
- `status` (enum): `not_started · in_progress · complete · skipped · fallback_activated`

**Example — Amynta Success Path:**
1. Revenue Associate on `/contact/` (replaces static inquiry form)
2. Affinity rail to aftermarket Amynta customers
3. White-label partner rail
- Fallback: Paid efficiency project (IVR, inbox automation)

**Example — FoxQuilt Success Path:**
1. NDA + pilot scope with Karim sign-off
2. Web chat 24/7 deployed
3. Stripe failed-payment recovery automation
4. Certificate issuance automation (surround-displace Strata)

---

## Lifecycle (state machine on Deal)

**New Logo:** `CONTACT → DISCOVERY → DEMO → PROPOSAL → NEGOTIATION → PILOT → WON` (or LOST any time)

**Customer Contract Conversion (Implementation exists):** `DISCOVERY often skipped → DEMO → PROPOSAL → NEGOTIATION → PILOT → WON`

DORMANT is cross-cutting — can fire on any stage. Resumption returns to same stage with a reactivation Interaction logged.

Stage → stage transitions governed by entry/exit criteria documented in the Playbook (see `EXEC/PLAYBOOK-v2.md`).

---

## Actors

**Humans:**
- Sales owner per Deal — Kyle, Cam, Marlon, Ian, Rocky (one named human)
- Sales reviewer — Kyle + Cam (proposalCandidate flag, ICP discipline, contract approval)
- Implementation lead — takes over Owner at NEGOTIATION → PILOT (Jonathan, Ganesh, George, Peter, Rem, Ian depending on account)
- Contract signer Indemn side — Kyle or Cam

**AI associates (post-v2):**
- Proposal Drafting Associate — generates proposal v0 from Deal + Company + Associate catalog
- Stage Aging Watcher — flags Deals stagnant beyond stage-specific threshold
- Cadence Enforcer — tickles Owner when stage cadence slipped
- Intro Path Verifier — confirms introPath recorded; flags cold-outreach Deals for time-capping

**Roles:**
- Sales Owner, Sales Reviewer, Proposal Author (see Playbook for specifics)
- Operating split (new in v2): **pre-signing = Kyle + Cam; post-signing delivery = implementation lead**

---

## Relationships

- **Prospecting → Sales:** Deal created on `Prospect.qualificationStage = qualified`. Company + Contact relationships inherit.
- **Sales → CS:** Implementation spawned on `Deal.stage = WON` (new_logo) or already exists (customer_contract_conversion). Handoff = Message in Craig's kernel.
- **CS → Sales (expansion + renewal):** ExpansionSignal or Renewal cycle triggers Sales motion; new Deal created; same entity, same lifecycle.

---

## Outcomes served

**Primary:** Revenue Growth.
**Secondary:** Strategic Control (honest pipeline — Cam's "I don't care what you think your pipeline is, this is what it is").

