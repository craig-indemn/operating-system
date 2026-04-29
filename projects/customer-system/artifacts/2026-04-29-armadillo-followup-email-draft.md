---
ask: "Follow-up email artifact for Armadillo from the 2026-04-28 discovery call. Generated per the DISCOVERY-stage Playbook artifact_intent (1) thank + reinforce specific pain by name, (2) propose concrete next step, (3) include materials David asked for, (4) acknowledge champion. Short, direct, listening signal — continuation of the conversation, not a pitch. Part of the 2026-04-29 Armadillo trace artifact for Kyle."
created: 2026-04-29
workstream: customer-system
session: 2026-04-29-armadillo-trace
sources:
  - type: google-drive
    ref: "1HmaB38MJIbQSF6VvwHwqdPAzcLOADfQrKW53lMdpfkI"
    name: "Indemn & Armadillo - 2026/04/28 13:59 EDT - Notes by Gemini"
    description: "Apr 28 discovery call transcript pulled from Kyle's Drive via DWD. The four artifact_intent points anchor on specific quotes and decisions from this transcript."
  - type: cli
    description: "Trace through the OS — Email entity 69f21cf925b15be7ce064426 (Apr 2 intro), Meeting entity 69f20e7725b15be7ce063dd3 (Apr 28 discovery), Touchpoints 69f2233325b15be7ce064461 + 69f2238525b15be7ce06446a, Deal 69f223cc25b15be7ce064470 (discovery), 3 Operations + 3 Opportunities + 1 Decision + 2 Commitments + 4 Signals + 2 CustomerSystem + 1 Task extracted via the IE pass."
  - type: local
    ref: "projects/customer-system/skills/email-classifier.md"
    description: "EC v9 — replaced Hard Rule #1 from 'never auto-create Company' to 'resolve before create'. Enabled the autonomous flow on Armadillo's first-contact email."
---

# Armadillo — Follow-up Email Draft (Discovery, 2026-04-28)

*Draft from the Artifact Generator pass. Renders the DISCOVERY-stage Playbook's `artifact_intent` against the Apr 28 call. Anchors every claim in extracted entities (line-to-entity mapping below).*

---

**To:** David Wellner <david@armadillo.one>
**Cc:** Matan Slagter <matan@armadillo.one>
**Subject:** Re: Indemn / Armadillo — pilot scope + talking points for Matan

Hi David,

Great call yesterday. The renewal pilot you proposed — 200 non-auto renewals over July through September with an A/B against your current human-only effort — is exactly the right shape. Connectivity is the unlock: getting in front of the half of your ~1,000 monthly renewers who don't pick up first time, with something they can actually transact on at 9pm on a Sunday. That's where we add measurable dollars.

Two things coming this week:

1. **Pilot scope and a touch-and-feel mock** — what the customer experience looks like for the 200, what data points we'd need from your renewal book to preset their options, and the 30/60/90-day implementation profile. Aim for end of this week.
2. **The Matan talking points** — a one-pager on why insurance-specific AI clears generalized vendors and in-house builds for what you're trying to do. Built for the conversation you'll have with him, not for me to send.

On the side: we both heard customer service / claims-status as a candidate channel and the after-hours "time extender" idea (a phone or chat number that completes a renewal sale without a human in the loop). Both stay in the picture; the renewal pilot is the right wedge first.

If it's useful — when you're ready to walk Matan through this together, I'll set time. Marlon and I will be on, and we can bring Cam (proposal owner on our side) if that helps the close. No rush — your timing.

Best,
Kyle

---

## Line-to-entity mapping (trace evidence)

| Email line | Source entity | OS ID |
|---|---|---|
| "renewal pilot you proposed — 200 non-auto renewals over July through September with an A/B against your current human-only effort" | **Decision** (renewal workflow prioritized for pilot) | `69f224b025b15be7ce064489` |
| "half of your ~1,000 monthly renewers who don't pick up first time" | **Operation: Renewals** + transcript quote (Apr 28 16:23 timestamp) | `69f224a725b15be7ce06447d` |
| "Pilot scope and a touch-and-feel mock... 30/60/90-day implementation profile" | **Commitment: Kyle plan pilot** | `69f224b225b15be7ce06448b` |
| "the Matan talking points — a one-pager on why insurance-specific AI clears generalized vendors" | **Commitment: David review pilot with Matan** + **Signal: David explicitly asked for talking points** | `69f224b325b15be7ce06448d`, `69f224b525b15be7ce064491` |
| "customer service / claims-status as a candidate channel" | **Opportunity: Service Associate (claims-status routing)** | `69f224ad25b15be7ce064487` |
| "after-hours 'time extender' idea... completes a renewal sale without a human" | **Opportunity: Time Extender** | `69f224ac25b15be7ce064485` |
| "Marlon and I will be on, and we can bring Cam" | **Touchpoint participants** + Deal owner pattern | Touchpoint `69f2238525b15be7ce06446a` |
| "your timing" / "no rush" | **Signal: Matan is gatekeeper** (read between lines — Kyle defers to David's pacing because David needs to convert Matan first) | `69f224b625b15be7ce064493` |

Every claim in this email traces back to an extracted entity from the Apr 28 Touchpoint (`69f2238525b15be7ce06446a`) or its source Meeting (`69f20e7725b15be7ce063dd3`). No fabrication; the email is a rendering of what the OS already knows.

---

## How this artifact was generated (the mechanism)

Per the breakthrough — *the entity model IS the playbook; the Proposal is the spine; every stage produces an artifact via the same mechanism*:

```
(Deal at discovery + recent Touchpoints + extracted intel + DISCOVERY Playbook + raw call transcript)
  → Artifact Generator
  → DISCOVERY-stage follow-up email
```

For Armadillo:
- **Deal**: `69f223cc25b15be7ce064470` (Armadillo — AI for Renewals + Customer Service, stage=discovery, warmth=Warm)
- **Touchpoints**: Apr 2 email (Matan intro) `69f2233325b15be7ce064461` + Apr 28 meeting `69f2238525b15be7ce06446a`
- **Extracted intel**: 3 Opportunities, 1 Decision, 2 Commitments, 4 Signals, 3 Operations, 2 CustomerSystems, 1 Task — all linked to the Apr 28 Touchpoint
- **Playbook (DISCOVERY)**: `69ebbe2f472952352cdfda2b` — `artifact_intent`: "thank + reinforce by name, propose concrete next step, include requested materials, optionally acknowledge champion"
- **Raw transcript**: Drive file `1HmaB38MJIbQSF6VvwHwqdPAzcLOADfQrKW53lMdpfkI` — provides voice, texture, the "Sunday night" personalization

Same mechanism produced GR Little's discovery follow-up (Apr 24) and Alliance's PROPOSAL-stage v2 proposal doc (Apr 27). Only the Playbook record changes per stage.
