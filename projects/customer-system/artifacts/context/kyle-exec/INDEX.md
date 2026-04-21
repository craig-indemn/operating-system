# Indemn OS — Revenue Pass-off

For Craig + Cam · Apr 20, 2026 · `~/claude-code/EXEC/`

---

## Active revenue this quarter

**New logo close candidates** (the 6 deals that can sign):

| Deal | Stage | $ | Owner | Next move | By |
|---|---|---|---|---|---|
| FOXQUILT-2026 | DEMO | TBD | Kyle → FDE | CEO demo w/ Karim Jamal | Apr 22 10am |
| AMYNTA-GRD360-2026 | DEMO | TBD | Kyle | Discovery-disguised-as-demo, get volume/traffic/conversion numbers | wk of Apr 27 |
| ALLIANCE-2026 | PROPOSAL | $42K | Marlon | Lock May meeting; pricing ($2.5K vs $1K/mo) | May wk 1 |
| NATIONWIDE | PROPOSAL | $1M+ | Cam | Four-channel confirmation | TBD |
| BRANCH-2026 (exp) | PILOT | $138K | Jonathan + Kyle | DPA countersign, enterprise scoping | ongoing |
| DISTINGUISHED (exp) | PROPOSAL | TBD | Ganesh → Kyle | Mani 20-MGA portal scope | TBD |
| HOMESTEADERS-2026 | CONTACT | TBD | Cam | Cam enriching w/ Parker context | TBD |
| TRUSTAGE | CONTACT | TBD | TBD | Identify Indemn owner from GIS | TBD |

**Expansion on delivered customers** (grounded revenue):

| Customer | Expansion | $ | Owner |
|---|---|---|---|
| JM (JM-EVENTGUARD-2026) | National scale + rev share on jewelry insurance | $745K upside | Ganesh + Kyle |
| INSURICA (INSURICA-RENEWAL-2026) | Multi-channel renewal expansion | $89K+ | Jonathan |
| GIC | Email triage ($17K) + AMS integration + 3-state | $17K near-term | Jonathan |

**Customers needing written enterprise contract** (delivering on pilot/usage — Motion B):

Tillman · O'Connor · Rankin · Bonzah · eSpecialty · BIB · Branch (trial → enterprise)

These convert via PILOT stage on a Deal while the Implementation stays LIVE. Not a new motion — same playbook.

---

## The system (one page)

### Deal stages + probability

```
CONTACT (5%)  →  DISCOVERY (15%)  →  DEMO (20%)  →  PROPOSAL (30%)  →  NEGOTIATION (50%)  →  PILOT (70%)  →  WON (100%)
                                                                                                           ↘  LOST (0%)
```

Sub-states: `CONTACT.listed / CONTACT.outreached` · `PROPOSAL.drafting / PROPOSAL.sent`
Cross-cutting flag: `DORMANT` with reason (silence · regression · stakeholder_turnover · scope_creep · competitive_loss · capacity · explicit_pass).

### Signals per stage (🟢 / 🟡 / 🔴)

Full detail in `PLAYBOOK-v2.md`. TL;DR: redlines coming back fast = 🟢. Silence past cadence = 🔴. Scope creeping without commitment = 🔴.

### Cadence per stage

- `CONTACT.outreached` — touch every 5-7d, max 3 touches
- `DISCOVERY` — weekly
- `PROPOSAL.drafting` — 2-3d to ship
- `PROPOSAL.sent` — 3-5d check-in
- `NEGOTIATION` — weekly, escalate >7d no movement
- `PILOT` — weekly exec sponsor checkpoint

### How the sales motion actually works (5 Core Platform patterns)

1. **Warm intro required.** No cold outreach in Core Platform.
2. **Qualifying signal = operational pain**, quantified. Not "interest in AI."
3. **Proposals outcome-specific**, not product-specific.
4. **Close is staged** — small package first, expansion later.
5. **Implementation credibility closes.** The technical lead on-site is the close lever, not pitch polish.

### ICP discipline (Cam's line: "extreme")

In: insurance MGA/carrier/agency/program/embedded · named workflow bottleneck · DM accessible · budget signal · champion identified.
Out: single-operator, free-forever expectation, anti-AI, vendors-as-prospects, custom we can't amortize.

### Proposal Candidate flag (Kyle + Cam set)

- **Y** — elevate, invest proposal effort (current: FoxQuilt, Amynta, Nationwide, Branch expansion, Alliance, Distinguished expansion, Homesteaders, TruStage)
- **Maybe** — needs more qualification, time-capped
- **N** — stay in pool, no proposal effort

---

## Entities (what to store)

### Deal
Production stage enum (above) + these fields on top of the existing Prisma Deal:

`dealId` (human-readable PK: `{COMPANY}-{YEAR}` or `{COMPANY}-{PRODUCT}-{YEAR}`) · `proposalCandidate` (Y/N/Maybe) · `whyProposal` (text) · `whatsNeeded` (text) · `commercialHypothesis` (milestone_rev_share / paid_project / hybrid / unclear) · `proposedPackage` (Package ref) · `successPath` (array of phases) · `nextStepOwner` (can differ from Deal owner) · `dormantFlag` + `dormantReason`

Full spec: `DICT-SALES-v2.md`

### Company
Prospect-view fields: `qualificationStage` (unknown / awareness / engaged / qualified / disqualified / dormant) · `icpTier` (A/B/C/D, manual) · `sourceChannel` · `introPath` (required) · `inferredPackageFit`

Full spec: `DICT-PROSPECTING-v2.md`

### Implementation
Stage enum: `KICKOFF · LIVE · EXPAND · RENEW · ADVOCATE` · Health: `ON_TRACK · AT_RISK · BLOCKED` + optional 0-100 score · **Two cohort axes:** `investorCohort` (Core Platform / Graduating / AI Investments / New Win / Partner) + `readinessCohort` (A Pilot Locked / B Baseline Running / C At Risk / D Open) · `currentPackage` · `growthPackagePath`

Full spec: `DICT-CUSTOMER-SUCCESS-v2.md`

### Package
7 SKUs × 3 tiers. Tier 1 customer-facing: Revenue Capture ($3-10K+/mo) · Digital Front Desk ($2-3.5K/mo, $2K Voice-First is IIANC SKU) · Renewal Machine ($2.5-4K/mo). Tier 2 expansion: Submission Command Center · Command Center. Tier 3 pipeline: Outbound Revenue · AI Insurance Products.

Full spec: `DICT-CUSTOMER-SUCCESS-v2.md`

---

## How data gets into the system (the Rocky problem solved)

No more "please update the sheet." Multiple inputs, all auto-hydrated:

| Input | Mechanism | Owner |
|---|---|---|
| Gmail | Cron polls per contact email → Interaction records | Craig automates |
| Granola | Meeting ends → Associate parses transcript → matches by attendee domain | Craig automates |
| Google Meet native | Team opt-in → shared folder → same pipeline as Granola | Craig + team |
| Apollo | Existing ~70% catch | Already built |
| Manual note | `#prospects-ledger` or DM `@prospect-associate`: "Talked to X, they want Y, next step Z" | Associate parses NL |
| Conference notes | Conversation dump → Associate extracts rows + tag | Kyle did ITNY; replicate |
| Direct edit | Cowork / CLI / UI | Already in Craig's OS |

Every update carries provenance (who, from what source, when). This is the daily ledger.

---

## What the Associate does per deal

For every Deal in `CONTACT.outreached` through PILOT:

1. Current-state summary (5-10 lines, refreshed on every Interaction)
2. Days-since-last-touch (auto)
3. Next-move recommendation (based on stage + cadence + signals)
4. Pre-drafted artifact (email / call script / proposal draft — for human approval)
5. Escalation flag (cadence slipped, signals turned red, dormant waking up)
6. Handoff packet (stage transitions — NEGOTIATION → PILOT, PILOT → WON)

**Associate does not auto-send externally. Humans approve every outbound.**

---

## Who does what

- **Craig** — owns the system. Ingests this dictionary into the beta OS. Builds the data ingestion (Gmail + Granola + Meet). Evolves it. Shares the canonical data dictionary back.
- **Cam** — owns adoption + ICP discipline + sales team contribution standards. Loops team in post-review. Commercial approval on proposals.
- **Kyle** — contributes callable data (Gmail, Calendar, Drive, Granola, Slack, 200+ memory files). Flags proposal candidates. Unblocks. Stays off operational Owner column.
- **Implementation leads (George · Jonathan · Ganesh · Peter · Rem · Ian)** — take over Owner at NEGOTIATION → PILOT handoff. Own delivery. Surface expansion signals.
- **Associate (AI, per deal)** — maintains the 6 deliverables above. Doesn't auto-send.

---

## Deliverables in this folder

- `PLAYBOOK-v2.md` — full operational motion (stages, signals, cadence, Associate's Job)
- `DICT-PROSPECTING-v2.md` — Prospect/Company schema
- `DICT-SALES-v2.md` — Deal schema
- `DICT-CUSTOMER-SUCCESS-v2.md` — Implementation + Package schema + cohorts
- `PROSPECT-PLAYBOOK-v0.md` — earlier operational take (superseded by PLAYBOOK-v2)
- `PROSPECT-SIX-LEADS-v0.md` — six leads hydrated to schema (FoxQuilt, Amynta, Alliance, Rankin, Tillman, O'Connor)
- `scripts/hydrate-deal.py` — hydrator (DB-dependent, waiting on restore)

**Live data sheets** (Craig can ingest via Sheets API):
- Customer Success Path Tracker: `1bHUrxuHmB4avZaWMMLkIO9dtBLocXXHH6igp1ej9sKU`
- Customer Cohort Baseline (A/B/C/D + packages): `13dU92WebBcrwlnniB1Zuy-16Y1PpuQFrPE56DWfMdLA`
- Revenue Baseline (72 prospects · 27 customers — broader inventory): `1M_luVsSUk3whOHVrBl-6r57MFI_XqV4iIC8JSbMaWbU`
- Portfolio Tracker (existing, 4 weeks stale — refresh target): `1etsZyXfES6cx-acTHja_29EKh1xK2eFkjyw4JSujYa4`
- ARR source of truth: `17Oznn4tNeRWuCmUPOCGL4eNOgpafDYmf3Ai6qSCz6rE`

**Production references Craig already has:**
- Prisma schema: `~/claude-code/indemn-pipeline/prisma/schema.prisma`
- customer-health skill (scoring formula): `~/claude-code/.claude/skills/customer-health/SKILL.md`
- PACKAGES.md: `~/claude-code/indemn-context/product/PACKAGES.md`

---

## What's needed from Craig

1. Ingest the four .md files into the beta OS as domain config.
2. Share the canonical data dictionary (entities + fields + enums) from the beta OS back — we've been inferring.
3. Build the Gmail + Granola ingestion path (your ask from the Apr 20 meeting).
4. Daily Kyle+Craig sync starts Apr 21.

---

## Cam's win condition (verbatim, Apr 20)

> "If we got this figured out in the right way… it will completely control the process. On an automated basis or by a tickle, it will reach out to Kyle and say, hey, Kyle — you haven't talked to so-and-so about this in a week. Today's the day. The leakage we're getting on prospects in terms of new ARR would be — I don't even know how to quantify it immediately. We could attribute probably as our top salesperson almost immediately."

That is what this builds toward.
