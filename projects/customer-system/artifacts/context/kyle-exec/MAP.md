# Indemn Master Map

**As of:** 2026-04-18  |  **Schema:** v3  |  **Source of truth:** `EXEC/MAP.json`

This is the reference rendering. The canonical substrate is the JSON. The *primary artifact* of the system is `/advance` — the queue of proposed next moves with ready drafts. This map is input fuel.

---

## At a Glance

```
PILLAR A · CAPITAL          ████████████████  6 workstreams  ·  1 blocked
PILLAR B · REVENUE          ██████████████    6 workstreams  ·  1 UNRESOLVED OWNER
PILLAR C · PRODUCT / OS     ██████████████    7 workstreams  ·  live
PILLAR D · PARTNERSHIP      ████████████      4 workstreams  ·  gates all others
PILLAR E · TEAM             ██████████████    7 workstreams  ·  live
                                              ────
                                              30 workstreams total
```

**Cross-cutting blockers:**
- 🔴 Brown Winnick cap table review blocks A.4, A.5, E.4
- 🟡 Iowa Apr 14 outcomes capture gates D.1, D.3, D.4
- 🔴 Net-new logo owner (B.2) is the biggest strategic open question

---

## PILLAR A — CAPITAL

*Raise the money we need on the terms we want.*

**Top targets:**
- Term sheet signed by May 15, 2026
- $10M first tranche close before July
- $15M extension by year-end ($25M total)
- Daniel Alpern $5M @ $30M pre closes
- Clean cap table before any strategic close

| ID | Workstream | Owner | State | Next Action |
|----|-----------|-------|-------|-------------|
| A.1 | Investor outreach & pipeline | Kyle | live | Send White Star + Martha; activate 5-bucket cadence |
| A.2 | Pitch deck engineering | shared | live | Cam reviews headlines, then fork render.py |
| A.3 | Financial model & data room | Kyle | **blocked** | Unblock Brian (27d) or build internally |
| A.4 | Strategic capital (Daniel + customer-investors) | shared | live | Watch for Daniel reply; Brown Winnick clears first |
| A.5 | Term sheet negotiation | Kyle | live | Activates on term sheet arrival |
| A.6 | Conference follow-through (ITNY, ALER26) | Kyle | live | Send Morrow + Jones Advisors ALER26 drafts |

---

## PILLAR B — REVENUE

*Grow ARR from $1.1M to $4M by year-end, $10M in 24 months.*

**Top targets:**
- $4M ARR by year-end 2026
- $10M ARR by Q1 2028 (100-customer model)
- Branch enterprise expansion $138K
- Voice live (Rankin/Tillman/O'Connor) May 31
- EventGuard national scale (JM) June 30
- Resolve net-new logo owner in 60-90d

| ID | Workstream | Owner | State | Next Action |
|----|-----------|-------|-------|-------------|
| B.1 | Expansion — deep-stack customers | Cam | live | Julia Hester Distinguished 1:1 (9d overdue) |
| B.2 | **Net-new logo motion (THE HOLE)** | **UNRESOLVED** | new | Kyle+Cam decision: who owns? |
| B.3 | Channel distribution | Cam | live | Drew & Lisa IIANC plan (overdue) |
| B.4 | Customer-specific deals | shared | live | FoxQuilt cal invite Apr 22; Alliance proposal Apr 21 |
| B.5 | Voice cohort | delegated-Ian | live | Receive Ian status report |
| B.6 | EventGuard scale (JM) | delegated-George | live | Kyle shares modularization before India |

---

## PILLAR C — PRODUCT / OS

*Build the Indemn Operating System. Indemn runs Indemn, then productizes.*

**Top targets:**
- Published product catalog mapped to Four Outcomes (2w post-Iowa)
- First OS slice prototype (30d post-Iowa = May 14)
- 10 AI insurance products in 2 years
- Front Door pricing approved ($500/$1K/$1.5K)
- SOC 2 complete

| ID | Workstream | Owner | State | Next Action |
|----|-----------|-------|-------|-------------|
| C.1 | Indemn OS platform (Craig) | shared | live | Kyle reviews OS white paper; Craig demo review |
| C.2 | Associates Catalog + Front Door | shared | live | Cam pricing approval; define Billing Associate next |
| C.3 | Voice agents (product side) | delegated-team | live | Team-driven |
| C.4 | EventGuard evolution | delegated-team | live | Share next-version approach before India |
| C.5 | Proposal / ROI / deck engine | Kyle | live | Decide ROI calc hosting |
| C.6 | SOC 2 compliance | delegated-Ganesh | live | Ganesh status |
| C.7 | Agentic site + capabilities | Kyle | live | Iterate post-Cam feedback |

---

## PILLAR D — PARTNERSHIP

*Kyle ↔ Cam alignment. **Gates all other pillars.***

**Top targets:**
- Weekly Iowa-style cadence operational
- Cam equity restructure (ask what he wants first)
- Kyle's owed deliverables to Cam shipped (2-4w post-Iowa)
- Context-first protocol live
- Priority stability

| ID | Workstream | Owner | State | Next Action |
|----|-----------|-------|-------|-------------|
| D.1 | Iowa alignment cadence | shared | live | Capture Apr 14 outcomes; schedule Round 2 |
| D.2 | Kyle-owed deliverables to Cam | Kyle | live | Ship one catalog entry/day; share sales process doc |
| D.3 | Equity / compensation framework | Cam | new | Kyle asks Cam what he wants |
| D.4 | Operating model + role definition | shared | live | Name the roles in a doc |

**The 6 things Kyle owes Cam (from Feb-Mar asks):**
1. GTM system (cadence, minimums, templates, decision trees) — documented Mar 12, not shared
2. Product catalog mapped to Four Outcomes — 7/24 defined
3. Context-first protocol on handoffs — behavior change, immediate
4. Priority stability — behavior change, immediate
5. Equity-vs-cash framework (Cam proposes, Kyle responds) — open
6. Sales process doc — documented Mar 12, not formally shared

---

## PILLAR E — TEAM

*Hiring, roles, development.*

**Top targets:**
- Craig CTO track: daily cadence
- Kai decision by Apr 24
- Director of CS hire (highest priority)
- Ganesh SVP path: 2 milestones closed
- Advisory Board formalized
- Marlon retention resolved

| ID | Workstream | Owner | State | Next Action |
|----|-----------|-------|-------|-------------|
| E.1 | Craig CTO track | Kyle | live | First daily sync; OS white paper review |
| E.2 | Kai Taylor decision (Apr 24) | Kyle | live | Kyle-Cam conversation about Kai |
| E.3 | Ganesh SVP path | Kyle | live | Receive plan deliverable |
| E.4 | Advisory Board formalization | shared | new | Decide structure with Cam |
| E.5 | Director of CS hire | Cam | new | JD + search |
| E.6 | Sales rep decisions (Marlon/Ian) | Cam | live | Cam → Ian role transition convo |
| E.7 | Engineering team | Kyle | live | Weekly sync |

---

## Stale Goals Flagged (Kyle decides)

The Pipeline API has 15 goals; 9 are stale 14d+. Recommendations (Kyle confirms each):

| Goal ID | Recommendation | Reason |
|---------|---------------|--------|
| SA-ANGEL | **ARCHIVE** | Retired Mar 9 per Kyle directive |
| SA-MATERIALS | UPDATE | Stale 47d; v25 + Patchwork not reflected |
| REV-WINS | VERIFY | Branch signed Mar 13; may be undercounted |
| PROD-VOICE | VERIFY | Rankin live; Tillman/O'Connor status needed |
| PROD-SOC2 | VERIFY | Ganesh status needed |
| SA-CALLS | UPDATE | 11/40 was Apr 10 snapshot |
| SA-INTROS | RECONCILE | API overcounts (46 vs real ~10-20) |
| REV-PIPELINE | UPDATE | 4 focus accounts moving |
| REV-EXPANSION | UPDATE | Branch enterprise negotiation active |

---

## Owner Split (strawman for Cam conversation)

| Pillar | Kyle-led | Cam-led | Shared | Delegated |
|--------|----------|---------|--------|-----------|
| A Capital | A.1 Outreach · A.3 Fin model · A.5 Term sheet | — | A.2 Deck · A.4 Strategic | — |
| B Revenue | — | B.1 Expansion · B.3 Channel | B.4 Customer deals · **B.2 HOLE (unresolved)** | B.5 Voice→Ian · B.6 EG→George |
| C Product | C.5 Engine · C.7 Site | — | C.1 OS (Craig) · C.2 Catalog | C.3 Voice · C.4 EG · C.6 SOC2 |
| D Partnership | D.2 Kyle-owed | D.3 Equity | D.1 Iowa · D.4 Operating model | — |
| E Team | E.1 Craig · E.2 Kai · E.3 Ganesh · E.7 Eng | E.5 CS hire · E.6 Sales reps | E.4 Advisory | — |

---

*This map exists so the advancement engine has something to chew on. If a workstream below doesn't produce next-moves, the system flags it. If a pillar's top targets aren't being advanced, the system escalates. The map is not an artifact to be read; it's substrate for the engine.*
