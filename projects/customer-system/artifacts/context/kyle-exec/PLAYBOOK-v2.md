# Playbook — Indemn Sales Motion

For Craig's customer operating system · Kyle · April 20, 2026

---

## The Real Indemn Sales Motion (what actually closes)

Five Core Platform customers (JM, INSURICA, UG, GIC, Distinguished) got signed. Patterns:

1. **Introduction is always warm.** JM via industry relationships. INSURICA via Kylie Hubbard + Julia Hester. UG via Ben Bailey. GIC + Distinguished via business development. No cold outreach in the Core Platform.

2. **Qualifying signal is operational pain, not interest in AI.** Quantified where possible. JM unbound event premium. INSURICA renewal workload. UG 3-week response times + 50% quote loss + $100K+ outsourced labor. GIC multi-channel governance at scale. Distinguished 20-BU consistency.

3. **Proposals are outcome-specific, not product-specific.** EventGuard rev share (JM). Multi-channel renewal automation (INSURICA). GL comparative rater + ACIC API (UG). Unified governance (GIC). Cyber Agent template for 20 BUs (Distinguished).

4. **Close is staged.** INSURICA: Receptionist Agent first, renewal agents later. Distinguished: Cyber Agents first, 20-BU rollout later. UG: implementation fees alongside ARR.

5. **Close driven by implementation credibility, not pitch polish.** George 9-month deep dive at UG. Jonathan two-track on-site at INSURICA. Ganesh hands-on KB at Distinguished. Craig email automation build at GIC.

**What's absent:** heated negotiation, discount gimmicks, compressed timelines, "land-and-expand" language. If a Deal looks like it needs any of those, re-check ICP.

---

## Entity shape (Deal) + operational layer

Schema layer uses production Prisma enum + Apr 2 probability:

```
CONTACT (5%) · DISCOVERY (15%) · DEMO (20%) · PROPOSAL (30%) · NEGOTIATION (50%) · PILOT (70%) · WON (100%) · LOST (0%)
```

**Sub-states within stages (from Prospect Playbook v0):**

- `CONTACT.listed` — Deal added, not yet reached
- `CONTACT.outreached` — first outbound sent, awaiting response
- `PROPOSAL.drafting` — Cam+Kyle internal alignment on scope + price
- `PROPOSAL.sent` — proposal delivered, awaiting decision

`DORMANT` is cross-cutting status flag, not a stage. A Deal can be in PROPOSAL + dormant = 14d silence after send. Reason codes: `silence · regression · stakeholder_turnover · scope_creep · competitive_loss · capacity · explicit_pass · investor_pass`.

**Kyle's contribution layer on Deal:**

- `proposalCandidate` (Y · N · Maybe): elevated-subset flag
- `whyProposal` (text, required when Y): operational-pain-to-outcome narrative
- `whatsNeeded` (text): named blockers to next stage
- `commercialHypothesis` (enum): `milestone_rev_share · paid_project · hybrid · unclear` (from Success Path Tracker)

**Motion B** (customers needing written enterprise contract while already delivering): Deal.stage = PILOT while Implementation exists at KICKOFF or LIVE. No new dealType.

---

## Per-stage operational detail

Adapted from Prospect Playbook v0 with stage names aligned to production.

### CONTACT.listed
- **Entry:** Deal created (Prospect qualification or direct add)
- **Exit:** first outbound sent → `CONTACT.outreached` · OR ICP-fail → LOST (icp_mismatch)
- **Owner:** ingester (Marlon · Ian · Kyle · Cam · George)
- **Cadence:** within 7d of creation
- **Next moves:** confirm ICP + outreach · schedule warm intro · drop as non-ICP
- **Data required:** sourceChannel, introPath, initial icpTier

### CONTACT.outreached
- **Entry:** first outbound sent
- **Exit:** response → DISCOVERY · OR 21d silence after 3 touches → DORMANT
- **Owner:** outreacher
- **Cadence:** touch every 5-7d, max 3 touches before pausing
- **Next moves:** follow-up touch · different channel · warm intro · pause
- **Signals:** 🟢 email open, meeting accept, LinkedIn connect · 🟡 open no reply · 🔴 hard no, unsubscribe, bounce

### DISCOVERY
- **Entry:** response received, discovery call scheduled or held
- **Exit:** use case clear + ICP confirmed → DEMO · OR disqualify → LOST
- **Owner:** AE (Kyle · Cam · Rocky · Marlon depending on account)
- **Cadence:** weekly touch until use case clear
- **Next moves:** second discovery call · internal scoping workshop · request data/access for ROI model · disqualify
- **Signals:** 🟢 champion named + pain confirmed + willingness-to-pay · 🟡 interested no next step · 🔴 can't describe workflow, demos-without-conversation, anti-AI

### DEMO
- **Entry:** champion clear, decision maker accessible, outcome mapping drafted
- **Exit:** outcome-specific scope drafted, pricing frame aligned → PROPOSAL
- **Owner:** AE + Technical FDE (Jonathan · Craig · Ganesh)
- **Cadence:** weekly with prospect; daily internal during scope draft
- **Next moves:** FDE validates technical feasibility · internal pricing scope · ROI model sent · competitor differentiation
- **Signals:** 🟢 prospect sends data/API specs, champion proactively schedules · 🟡 enthusiasm no backend access · 🔴 scope keeps expanding without committing

### PROPOSAL.drafting
- **Entry:** internal alignment on scope + price + timeline
- **Exit:** proposal delivered → `PROPOSAL.sent`
- **Owner:** AE drafts, Cam approves commercial structure
- **Cadence:** 2-3 days to ship; don't let sit
- **Next moves:** draft → Cam review → send · add compound-outcome pricing · add FDE deliverable timeline
- **Signals:** 🟢 pricing + scope fields clear · 🟡 one stakeholder missing · 🔴 scope creeping, timeline slipping past 7d

### PROPOSAL.sent
- **Entry:** proposal sent
- **Exit:** verbal yes → NEGOTIATION · substantive pushback → DEMO or PROPOSAL.drafting · 14d silence → DORMANT
- **Owner:** AE + exec sponsor
- **Cadence:** 3-5 day check-in if no response
- **Next moves:** check-in nudge · exec-level push (Kyle to Kyle, Cam to COO) · walk proposal line-by-line · revise
- **Signals:** 🟢 redline questions, legal loop-in, "when can we start" · 🟡 "reviewing internally" · 🔴 14d silence, new concerns, stakeholder turnover

### NEGOTIATION
- **Entry:** proposal accepted in principle, contract drafting
- **Exit:** contract signed → PILOT (or WON if no trial) · fall through → LOST
- **Owner:** Kyle or Cam + Brown Winnick
- **Cadence:** weekly; escalate if >7d no movement
- **Next moves:** MSA redline response · CLO conversation · pricing concession · exec-to-exec escalation
- **Signals:** 🟢 redlines returning fast, scope stable · 🟡 legal Q's >7d · 🔴 repeated MSA punt, new stakeholder at 11th hour

### PILOT (70%)
- **Entry:** resources engaged, trial or pilot contract or verbal active
- **Exit:** enterprise contract signed → WON · trial fails → LOST
- **Owner:** implementation lead (George · Jonathan · Ganesh)
- **Cadence:** weekly checkpoint with exec sponsor
- **Next moves:** weekly checkpoint · expansion proposal once KPIs hit · trial extension · scope adjustment
- **Signals:** 🟢 prospect asks "what's next after trial" · 🟡 trial running no expansion conversation · 🔴 KPIs missed, prospect cooling
- **Motion B case:** Implementation already LIVE; `Deal.stage = PILOT` encodes "delivering, needs written enterprise contract"

### WON
- **Entry:** written enterprise contract executed
- **Exit:** kickoff → Customer Success playbook (handoff)
- **Owner:** handoff from AE to implementation lead within 48h
- **Signals:** 🟢 kickoff on calendar · 🟡 handoff delayed · 🔴 signed then silent

### LOST
- **Entry:** explicit pass · ICP surfaced late · competitive loss · capacity cut
- Reason code required
- Some LOSTs are re-qualification candidates; some are hard-drop

---

## The Rocky problem — how data actually gets into the system

Cam's problem: Rocky won't put interactions in Apollo because Apollo is too complex. Interactions don't hit source of truth. **Fix: multiple input paths, all auto-hydrated to the same data layer.**

| Input source | How it enters | Owner |
|---|---|---|
| **Gmail** | Cron polls per known contact email → auto-creates Interaction records | Craig (automation) |
| **Granola** | Meeting ends → transcript lands → Associate parses → updates `last_interaction_summary` + matches Company by attendee domain | Craig (automation) |
| **Google Meet native** | Team opt-in to Google transcripts → shared folder → same pipeline as Granola | Craig + team opt-in |
| **Apollo** | Existing ~70% catch | Already built |
| **Manual note** | Team member posts in #prospects-ledger or DM `@prospect-associate`: "Talked to X, they want Y, next step Z" | Associate parses NL, updates state; human stays in flow |
| **Conference notes** | Paper/Notion/memory → conversation dump → Associate extracts rows + conference tag | Kyle did this for ITNY; replicate per event |
| **Direct edit** | Cowork/CLI/UI | Already in Craig's system |

**Ledger requirement:** every update has a provenance record (who updated, from what source, when). Cam's "daily published ledger" = this materialized.

---

## The Associate's Job (per prospect)

For every Deal in `CONTACT.outreached` through PILOT, the prospect Associate produces and maintains:

1. **Current-state summary** — 5-10 line brief, refreshed on every new Interaction
2. **Days-since-last-touch** — auto-computed
3. **Next-move recommendation** — based on stage + cadence + signals
4. **Pre-drafted artifact** — email / call script / proposal draft, ready for human approval
5. **Escalation flag** — stage cadence slipped, signals turned red, ancient lead wakes up
6. **Handoff packet** — when stage transitions (NEGOTIATION → PILOT, PILOT → WON), a handoff doc for the new owner

Humans review and approve. **Associate doesn't auto-send externally.**

---

## Per-Deal Success Path

Universal stages are the same for every Deal. Each Deal has its own bespoke Success Path inside those stages — the phased progression specific to this customer's situation.

**Example — Amynta (AMYNTA-GRD360-2026):**
- Phase 1: Revenue Associate on `/contact/` (replaces static inquiry form)
- Phase 2: Affinity rail to aftermarket Amynta customers
- Phase 3: White-label partner rail
- Fallback: Paid efficiency project (IVR, inbox automation)

**Example — FoxQuilt (FOXQUILT-2026):**
- Phase 1: NDA + pilot scope with Karim sign-off
- Phase 2: Web chat 24/7 deployed on foxquilt.com
- Phase 3: Stripe failed-payment recovery automation
- Phase 4: Certificate issuance automation (surround-displace Strata)

Success Path lives on the Deal as a structured field (phases array) and feeds into the commercial proposal. Each phase has entry criteria + expected outcome + go/no-go signal.

---

## ICP discipline (Cam's current stance: extreme)

**ICP signals — enter or stay:**
- Insurance MGA, carrier, retail agency, program, embedded, direct
- Named repeatable workflow bottleneck (broker portal, FNOL, quoting, renewals, service, payments)
- Decision maker accessible within 2-3 people of our entry point
- Budget signal: explicit ("we'd pay $X") or proxy (staff volume × time spent ≥ $50K value)
- Champion-candidate identified (wants this, not just CEO doing fit)

**Non-ICP signals — early drop:**
- Single-operator agency with no bandwidth
- Expects free forever
- Anti-AI stance
- "Send info" with no return engagement after 2 touches
- Pure vendor / partner / media / investor disguised as prospect
- Custom build we can't amortize

**System job:** when ICP, surface + elevate. When not, cap time spent.

---

## Proposal Candidate flag (Kyle + Cam strategic layer)

- **Y** — elevate. Operational pain quantified, champion warm, outcome mapped.
  - Current Y list (Apr 20): FoxQuilt, Amynta, Nationwide, Branch expansion, Alliance, Distinguished expansion, Homesteaders (Cam enriching), TruStage (owner TBD).
- **Maybe** — needs more qualification. Cam's ICP discipline applies.
- **N** — not a proposal candidate right now. Stays in pool at appropriate stage, no proposal effort.

Changes logged in Craig's changes collection.

---

## Operating Split (from Amynta handoff, codified in v2)

- **Pre-signing** = Kyle + Cam frame the commercial hypothesis and manage relationship
- **Post-signing delivery** = implementation lead owns (Ganesh: JM + Distinguished + Family First + Loro + Amynta; Jonathan: INSURICA + Branch + GIC + Bonzah; George: UG; Peter: data/integrations; Rem: UG technical; Ian: 101 Weston cohort)
- **Handoff at WON** is explicit: AE → implementation lead within 48h (handoff packet from Associate)

---

## Deal ID convention (from Success Path Tracker)

Structured, human-readable: `{COMPANY_TAG}-{YEAR}` or `{COMPANY_TAG}-{PRODUCT}-{YEAR}` for multi-product companies.

Examples: `AMYNTA-GRD360-2026` · `RANKIN-2026` · `TILLMAN-2026` · `OCONNOR-2026` · `ALLIANCE-2026` · `FOXQUILT-2026` · `JM-EVENTGUARD-2026` · `INSURICA-RENEWAL-2026`

Prevents auto-generated ID collisions and makes Deal references scannable in Slack + Gmail.

---

## Cam's win condition (verbatim, Apr 20 2 PM)

> "If we got this figured out in the right way… it will completely control the process. On an automated basis or by a tickle, it will reach out to Kyle and say, hey, Kyle — you haven't talked to so-and-so about this in a week. Today's the day. The leakage we're getting on prospects in terms of new ARR would be — I don't even know how to quantify it immediately. We could attribute probably as our top salesperson almost immediately."

That is what this playbook is for.
