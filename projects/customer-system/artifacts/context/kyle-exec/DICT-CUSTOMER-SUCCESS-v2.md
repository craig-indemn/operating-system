# Customer Success Data Dictionary

Domain configuration on Craig's operating system kernel · Kyle · April 20, 2026

---

## Purpose

Customer Success is the delivery sub-system. Three jobs in order of revenue impact:

1. **Deliver quality** against the outcome Sales promised
2. **Support the written-enterprise-contract close** for customers on pilot/usage/month-to-month (Motion B — `Deal.stage = PILOT` while Implementation is LIVE; handled in Sales with CS providing delivery credibility)
3. **Surface expansion** when delivery quality crosses threshold — CS detects, Sales executes

---

## Scope

**IN SCOPE:** every customer with a live Implementation (any `contractStatus`) · health tracking (score + ternary) · milestone progression · expansion candidate detection + evidence · readiness cohort + package tracking · per-customer Success Path phases

**OUT OF SCOPE:** Sales (Deal movement, proposals, pricing, signature) · Prospecting (pre-customer funnel)

---

## Implementation entity (extended from Craig's Prisma schema)

**Production stage enum (post-migration target):**

```
KICKOFF · LIVE · EXPAND · RENEW · ADVOCATE
```

Legacy values still in Prisma (SCOPING, CONFIGURATION, TESTING, LAUNCH, ONBOARDING, ACTIVE) migrate to KICKOFF or LIVE with Milestone sub-tasks capturing the sub-state.

**Health enum (production ternary):** `ON_TRACK · AT_RISK · BLOCKED`
**`healthScore`** (int 0-100, optional persisted) — from customer-health skill formula

**Fields on Implementation (v2 additions in bold):**

- `stage` (`KICKOFF · LIVE · EXPAND · RENEW · ADVOCATE`)
- `contractStatus` (`none · trial_month_to_month · pilot_with_end · verbal_no_paper · enterprise_contracted · amended · terminated`)
- `health` (`ON_TRACK · AT_RISK · BLOCKED`)
- `healthScore` (int 0-100, optional)
- **`investorCohort`** (enum — investor-tested language): `Core Platform · Graduating · AI Investments · New Win · Partner`
- **`readinessCohort`** (enum — operational, from Customer Cohort Baseline): `A (Pilot Locked, Growth Plan Defined) · B (Baseline Running) · C (Exploring / At Risk) · D (Open Opportunities)`
- **`currentPackage`** (Package ref, nullable): Revenue Capture · Digital Front Desk · Renewal Machine · Submission Command Center · Command Center · Outbound Revenue · AI Insurance Products
- **`growthPackagePath`** (array of Package refs): the packages this customer graduates through
- **`successPath`** (array of Phase records — mirrors `Deal.successPath`, inherited on handoff, continues through delivery)
- `primaryOutcome` (`Revenue Growth · Operational Efficiency · Client Retention · Strategic Control`)
- `champion` (Contact ref), `champions` (array), `executiveSponsor` (Contact ref nullable)
- `implementationLead` (Actor ref): George · Jonathan · Ganesh · Peter · Rem · Ian
- **`preSigningLead`** (Actor ref — new in v2 from Operating Split): Kyle + Cam pre-signing; empty post-signing
- `deployedAssociates` (array of Associate refs)
- `ARR` (currency), `potentialARR` (currency)
- `lastTouchDate` (date, computed)
- `lastTouchSource` (text: Gmail thread ID, Granola ID, Slack permalink)
- `daysSinceContact` (int, computed)
- `expansionCandidate` (bool)
- `expansionShape` (text, nullable — description)
- `expansionEvidence` (text, nullable — specific signal that triggered)

HealthEvent, Milestone, ExpansionSignal NOT separate entities. Served by: changes collection (health audit) + `healthScore` field + `Task.isMilestone` extension + expansion fields on Implementation.

**Task (extended, not new):**
- `isMilestone` (bool)
- `successCriteria` (text nullable)

---

## Two cohort axes (v2 locks both; they answer different questions)

### `investorCohort` — portfolio narrative + revenue materiality
- **Core Platform** (5, contracted, ~$273K ARR, ~88% of revenue): JM · INSURICA · Union General · GIC · Distinguished
- **Graduating** (pre-enterprise-contract, delivering): Johnson · Tillman · O'Connor · Rankin · Bonzah
- **AI Investments** (co-invested, not revenue-primary): Family First · mShift · eSpecialty · ConvergentRPS
- **New Win** (recently signed, early delivery): Branch ($2K/mo trial → $138K target)
- **Partner** (MOU-based): Loro · BT Core · Borrowed Tyme

### `readinessCohort` — operational, from Customer Cohort Baseline (Kyle+Cam Apr 20)
- **A — Pilot Locked, Growth Plan Defined** (ramping to baseline in 60-90d): Alliance · Branch · Charley · BIB · Johnson
- **B — Baseline Running** (template customers, $309K current ARR, $365K+ 2026): JM · INSURICA · UG · GIC · Distinguished · Rankin · Tillman · Bonzah · eSpecialty
- **C — Exploring / At Risk** (decide save/convert/close): O'Connor · Family First · mShift
- **D — Open Opportunities** (pipeline stalled without clear package pitch): Silent Sports · Middendorf · HML · Nationwide

**Transitions:**
- `investorCohort`: New Win → Core Platform on enterprise contract (annualized ≥ $25K). Graduating → Core Platform on enterprise contract + confirmed first renewal.
- `readinessCohort`: B → A when growth plan defined. B → C on at-risk signal. C → B on recovery. D → A when package clarity lands.

---

## Package entity (new in v2 from Customer Cohort Baseline)

**Canonical source:** `~/claude-code/indemn-context/product/PACKAGES.md` (Mar 20, 7 packages × 3 tiers).

**Tier 1 (customer-facing, baseline SKU per segment):**
- Revenue Capture ($3-10K+/mo) — JM proof point
- Digital Front Desk ($2-3.5K/mo) — INSURICA + GIC proof. $2K Voice-First is the IIANC cohort SKU (Rankin + Tillman)
- Renewal Machine ($2.5-4K/mo) — INSURICA proof

**Tier 2 (expansion, not entry):**
- Submission Command Center (UG proof)
- Command Center (bundled over $5K/mo)

**Tier 3 (pipeline / carrier JV):**
- Outbound Revenue
- AI Insurance Products (EventGuard model — JM carrier JV)

**Apr 2 rule (Kyle + Cam):** Lead with **bundled outcomes, not individual associates**. Selling one associate à la carte = minority case.

**Package entity fields:**
- `name` (text)
- `tier` (`1 · 2 · 3`)
- `priceRange` (text)
- `proof` (array of Implementation refs — which current customers prove this package)
- `includedAssociates` (array of Associate refs)

`Deal.proposedPackage` links here. `Implementation.currentPackage` links here.

---

## Operating Split (new in v2 from Amynta handoff)

- **Pre-signing** = Kyle + Cam frame commercial hypothesis and manage relationship
- **Post-signing delivery** = implementation lead owns
- **Handoff at WON** is explicit: AE → implementation lead within 48h

Ganesh self-declared Apr 20: "I can take charge once a customer is brought in." This encodes that.

---

## Lifecycle (state machine on Implementation)

```
KICKOFF → LIVE → EXPAND (optional, can return to LIVE)
                  ↘ RENEW (periodic from LIVE or EXPAND)
                  ↘ ADVOCATE (customer providing references)
```

Health transitions independent of stage. At_risk can fire at any stage; recovery restores to on_track. `readinessCohort` updates independently based on package + growth plan state.

---

## Health scoring (formula from customer-health skill, not re-specified)

customer-health skill at `~/claude-code/.claude/skills/customer-health/SKILL.md`:
- **Base weights:** last contact 30% · open commitments 25% · implementation status 20% · engagement trend 15% · expansion signals 10%
- **Cohort multipliers:** Core Platform 2x weight on commitments + engagement · Graduating 2x weight on implementation · AI Investments flag only if 30+ days silent
- **Output:** 0-100 score → `healthScore` field, mapped to ternary (`ON_TRACK ≥ 70`, `AT_RISK 40-69`, `BLOCKED < 40`)

v2 reuses. Persists `healthScore`. Ternary enum stays the primary surface for UI + filtering.

---

## Actors

**Humans:**
- Implementation leads — George (comms) · Jonathan (INSURICA + Branch + GIC + Bonzah) · Ganesh (JM + Distinguished + Family First + Loro + Amynta) · Peter (data + integrations) · Rem (UG) · Ian (101 Weston: Tillman + O'Connor + Rankin)
- Exec sponsor Indemn side — Kyle (JM + Branch enterprise) or Cam (strategic partners + Nationwide)
- Pre-signing lead — Kyle + Cam (new Operating Split codification)
- Health reviewer — Cam + Ganesh (portfolio level)

**AI associates (post-v2):**
- Retention Associate — Jonathan's existing INSURICA work generalized
- Expansion Signal Detector
- Health Scorer
- Commitment Watcher
- Package Fit Scorer — matches Implementation state to right `currentPackage`; surfaces mismatch (underpackaged = expansion signal; overpackaged = at-risk signal)

---

## Relationships

- **Sales → CS:** Implementation spawned on `Deal.stage = WON` (new_logo) or exists already (customer_contract_conversion).
- **CS → Sales (expansion):** `expansionCandidate = true` triggers Sales motion; new Deal.
- **CS → Sales (renewal):** renewal cycle fires; Sales creates renewal Deal; Implementation stays LIVE during renewal.
- Handoff events are Messages in Craig's kernel (`implementation_started · expansion_signal_detected · renewal_due · readiness_cohort_changed · package_upgraded`).

---

## Open questions (need Craig's input)

1. Run the one-time migration to retire legacy SCOPING/CONFIGURATION/TESTING/LAUNCH/ONBOARDING/ACTIVE stages? Portfolio Tracker uses them across 18 rows.
2. Should Package be a Prisma enum or a first-class entity? Leaning entity since pricing + included associates matter.
3. `readinessCohort` transitions triggered automatically or manually? Kyle + Cam manual initially; automation when decision data accrues.
4. Ganesh Customer Success data pull — fast-follow once extraction proves on Prospect side.
