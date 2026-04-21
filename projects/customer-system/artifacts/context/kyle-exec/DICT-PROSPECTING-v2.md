# Prospecting Data Dictionary

Domain configuration on Craig's operating system kernel · Kyle · April 20, 2026

---

## Purpose

Prospecting is the front-of-funnel sub-system. Identifies, enriches, and qualifies Companies until they become Deals in Sales. The load-bearing decision: **which prospects earn sales-team time?**

Cam's ICP discipline is "extreme." Prospecting encodes that so team time tracks with opportunity.

---

## Scope

**IN SCOPE:** capture every new Company · `introPath` (warm intro / conference / inbound / investor) · triage (qualify → Sales creates Deal · disqualify · park · nurture) · touches pre-qualification · update mechanisms that keep data hydrated without manual sheet maintenance

**OUT OF SCOPE:** Sales (active Deal movement) · Customer Success (post-contract delivery)

---

## Prospect view of Company (extended from Craig's Prisma Company)

A Company is a Prospect when it has no Deal past CONTACT. Once `Deal.stage` advances to DISCOVERY+, Sales owns primary; Prospecting fields persist.

**Fields layered on Craig's Company:**

- `qualificationStage` (enum): `unknown · awareness · engaged · qualified · disqualified · dormant`
- `icpTier` (enum, manually set by Kyle or Cam): `A · B · C · D`
- `sourceChannel` (enum): `ITNY · ALER26 · conference_other · inbound_web · inbound_email · warm_intro · investor_referred · partnership · outbound` (rare)
- `introPath` (text, **required**): specific path — "Luge portfolio diligence (David Nault)" · "Ian at ITNY booth" · "Cam referral via Aubie Knight" · "Warm from Scott Hartley"
- `firstTouchDate` (date)
- `lastTouchDate` (date, computed)
- `lastTouchChannel` (enum, computed)
- `nextMove` (text)
- **`nextStepOwner`** (Actor ref — v2 addition, can differ from Company owner, prevents "nobody moves it")
- `nextMoveDue` (date)
- `daysDormant` (int, computed)
- `droppedReason` (enum nullable): `icp_mismatch · no_engagement · wrong_stage · capacity · explicit_pass · investor_pass`
- `promotedToSalesDate` (date, nullable)
- **`inferredPackageFit`** (Package ref, nullable — v2): best-guess Package based on `sourceChannel` + Type (e.g., IIANC → Digital Front Desk $2K Voice-First)
- **`prospectId`** (text, human-readable PK): convention `{COMPANY_TAG}-{YEAR}` (see Sales v2; Prospect IDs can be reused on Deal spawn)

`icpScore` (0-100) explicitly NOT in v2. Kyle + Cam are the ICP filter manually. Revisit scoring after 50-100 decisions.

**Contact (extended):**
- `role` (enum): `champion · decision_maker · influencer · gatekeeper · researcher · unknown`
- `relationshipStrength` (enum): `cold · warm · developing · strong · gone_dark`
- `indemnOwner` (Actor ref): who holds the relationship

**Outreach and Qualification NOT separate entities.** Outreach = Activity with `type = outreach`. Qualification = state transition + notes; changes collection captures audit.

---

## Warm-intro-required (first-class, from 5 Core Platform wins)

All 5 Core Platform customers came through warm intros. v2 encodes:

- `introPath` required at Company creation
- `sourceChannel = outbound` is exceptional — time-capped per Cam's discipline
- Warm intro provenance stored (who intro'd, context)
- Cold-sourced Companies flagged for review before DISCOVERY

Rocky test case: proactive energy good, targets must be vetted before time spent.

---

## The Rocky problem — update mechanisms (from Prospect Playbook v0)

Cam's problem: Rocky won't use Apollo (too complex); interactions don't hit source of truth. **Fix: multiple input paths, all auto-hydrated.**

| Input | How it enters | Owner |
|---|---|---|
| Gmail | Cron polls per known contact email → auto-creates Interaction records | Craig (automation) |
| Granola | Transcript lands → Associate parses → updates `lastTouchDate` + `lastTouchSource` + matches Company by attendee domain | Craig (automation) |
| Google Meet native | Team opt-in to Google transcripts → shared folder → same pipeline as Granola | Craig + team |
| Apollo | Existing ~70% catch | Already built |
| Manual note | Post in `#prospects-ledger` or DM `@prospect-associate`: "Talked to X, they want Y, next step Z" | Associate parses NL |
| Conference notes | Paper/Notion/memory → conversation dump → Associate extracts rows + conference tag | Kyle did this for ITNY |
| Direct edit | Cowork/CLI/UI | Already in Craig's system |

Every update has provenance (who updated, from what source, when). Daily ledger = this materialized.

---

## Lifecycle (state machine on `Company.qualificationStage`)

```
unknown → awareness → engaged → qualified (→ Deal spawned in Sales)
                                  ↘ disqualified
                                  ↘ dormant ↔ awareness
```

**Transitions:**
- `unknown → awareness`: first Interaction logged
- `awareness → engaged`: response received OR second Interaction without dropoff
- `engaged → qualified`: Kyle / Cam / sales owner sets `qualificationStage = qualified`; Deal created in Sales at `CONTACT.listed` or `CONTACT.outreached`
- `engaged → dormant`: `daysDormant > threshold` (14d inbound · 30d warm · 60d cold)
- `any → disqualified`: ICP mismatch, explicit pass, capacity cut
- `dormant → awareness`: new Interaction resets

Transition to `qualified` spawns Deal. Deal inherits Company + Contact refs, `primaryOutcome` (from qualification notes), initial `icpTier`, `inferredPackageFit` → `proposedPackage`.

---

## The Associate's Job (per prospect)

For every Prospect in awareness/engaged, the prospecting Associate maintains:

1. **Current-state summary** — 5-10 line brief, refreshed on every new Interaction
2. **Days-since-last-touch** — auto-computed
3. **Next-move recommendation** — based on sourceChannel + qualificationStage + signals
4. **Pre-drafted outreach** — email draft ready for human approval (no auto-send)
5. **Dormancy flag** — crossing threshold per sourceChannel
6. **Qualification handoff packet** — when Kyle/Cam set qualified, associate prepares brief for Sales owner

---

## Actors

**Humans:**
- Ian — ITNY + ALER26 + 101 Weston-adjacent
- Marlon — outbound + some inbound triage
- Rocky — relationship-heavy, high-touch
- Kyle — strategic top-of-house, investor-sourced, warm intros
- Cam — enterprise (Nationwide-tier), Aubie-network, strategic partners

**AI associates (post-v2):**
- Research Associate — company context, tech stack, decision-maker background
- Intro Path Verifier — confirms warm intro recorded; flags cold-sourced for time-capping
- Dormancy Watcher — flags threshold crossings
- Qualification Assistant — pre-drafts qualification brief when Kyle/Cam approve

---

## Outcomes served

**Primary:** Revenue Growth (pipeline that converts).
**Secondary:** Strategic Control (visible top-of-funnel, honest about leaks).
**Tertiary:** Operational Efficiency (cut time on low-ICP accounts).

---

## Open questions (need Craig's input)

1. Does the existing Company entity already have `qualificationStage` or equivalent? Align naming if so.
2. How are ITNY/ALER26 batches represented — `sourceChannel` values or related Conference entity? (Conference-ID per batch might be worth it for cohort retrospectives.)
3. Dormancy thresholds (14d inbound / 30d warm / 60d cold) — store as org config, not hard-coded.
4. `inferredPackageFit` — formula from (sourceChannel, Type) tuple? Start manual, automate after patterns build.
