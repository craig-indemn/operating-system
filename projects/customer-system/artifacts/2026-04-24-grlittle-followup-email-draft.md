---
ask: "Generate the follow-up email for GR Little (Apr 22 first-discovery call) from the hydrated OS state + DISCOVERY Playbook's artifact_intent — the concrete deliverable for Kyle to compare against what he would have sent"
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
sources:
  - type: entity
    ref: "Touchpoint 69ebbec5472952352cdfda4f"
    description: "Manually-created Touchpoint for the Apr 22 meeting (GR Little + Kyle, 31 min)"
  - type: entity
    ref: "Deal GRLITTLE-2026 (69ebb7222b0a508618923c06)"
    description: "Stage: discovery, warmth: Warm, source: Inbound"
  - type: entity
    ref: "Playbook for DISCOVERY stage (69ebbe2f472952352cdfda2b)"
    description: "artifact_intent drove the shape of this email"
  - type: entity
    ref: "Extracted Tasks (2), Decisions (2), Commitments (4), Signals (5) linked to the Touchpoint"
    description: "The content that fed the draft"
---

# GR Little Follow-up Email — Draft

**The demo artifact.** Generated from the OS entity graph state after hydrating the GR Little Company / Deal / Meeting / Touchpoint / extracted intelligence, applying the DISCOVERY-stage Playbook's `artifact_intent` to the material.

Kyle's test is: compare this to what he would have sent. The diffs are the conversation.

---

## Metadata

| | |
|---|---|
| **To** | Walker Ross <walker.ross@grlittle.com> |
| **CC** | Heather F <heatherf@grlittle.com> |
| **From** | Kyle Geoghan <kyle@indemn.ai> |
| **Subject** | Great to meet — recap, NC examples, and the next one |

---

## Draft

Walker, Heather —

Really enjoyed the conversation on Tuesday. And Walker — congrats on the twins; hope their NICU stay is short.

Quick recap of what I heard, and the things I'm sending over.

From the call, the workflows that sounded most worth piloting were:

- **After-hours phone coverage.** You don't have it today, and that's where the missed-call pain seemed biggest. We can stand up an AI associate that answers out-of-hours calls, captures the 3-5 key data points, and hands the call off into Teams (or directly into Agency Zoom / HawkSoft) with a full summary.
- **Billing inquiries.** You described real volume flowing to your three front-desk positions for "how do I pay this bill on carrier X." Textbook first wedge for us — we can take those calls and chats and give your customers the answer instantly, 24/7, without anyone on your side losing a day to it.
- **Renewal questionnaires.** Today you're sending a Cognito form by email. Heather asked whether we could have an AI agent actually call the insured and walk them through the questions. Yes — that's one of our favorite outbound patterns. I'll bring a live example to the demo.

What you'll find in your inbox:

1. **Recording of the call.**
2. **Indemn deck** — one-pager on the Associates and how the front-door model works for independent agencies.
3. **NC agency examples** — what we're doing for the five other IIANC agencies we've signed through Pat Klein and 101 Western Labs. That's the closest comparison to you.

For the next meeting, I want to do something different. Instead of a generic demo, I'll scrape grlittle.com and **stand up a first-version version of your agency's agent** — so we're looking at how it handles *your* coastal book, *your* NCIUA program, *your* language, and your stack (HawkSoft + Agency Zoom + Glovebox). Not somebody else's.

Walker — my booking link is [CALENDAR_LINK]. Grab whatever works in the next week or two, and loop in anyone else on your side who should be in the room.

One more note on something you and Heather both raised: taking the actual payment for clients who need help, instead of redirecting them to the carrier's portal. That's a real gap — we've heard it from multiple agencies. We're navigating the PCI / compliance side of it and I'll bring you in whenever there's a good moment to pilot.

Thanks again, and say hi to the newest residents of Kitty Hawk when they're out of the NICU.

Kyle

---

## How this was built from the entity graph

The shape of the email is determined by the DISCOVERY Playbook's `artifact_intent`:

> A follow-up email to the primary contact that does four things.
> (1) Thanks them for the conversation and reinforces the specific pain points they raised, by name — not generic.
> (2) Proposes a concrete next step, usually a demo, with suggested timing and attendees.
> (3) Includes any materials they explicitly requested in the call (recording, one-pagers, relevant examples).
> (4) Optionally acknowledges the champion by referencing something specific from their background or perspective.
> The email should be short, direct, and signal that we listened. It is a continuation of the conversation, not a pitch.

And the content for each of those four is pulled from specific entities:

| Playbook requirement | Fed by | Entity fields used |
|---|---|---|
| (1) Reinforce specific pain points | **Signal** (insight): "Wedge candidates surfaced: (1) after-hours phone, (2) billing inquiries, (3) outbound renewal, (4) web lead conversion." | `signal.description`, `signal.attributed_to` |
| (2) Concrete next step | **Commitment** (customer): "Walker to book the full demo." + **Task**: "Scrape grlittle.com + build personalized first-version demo." | `commitment.description`, `task.title`, `task.description` |
| (3) Requested materials | **Commitment** (indemn): "Send recording, deck, NC agency examples." | `commitment.description` |
| (4) Acknowledge champion | **Signal** (champion): "Walker is 3rd-gen CORE Team Manager, referred via Pat Klein." + **Contact.notes** + **Company** (coastal/NCIUA niche, HawkSoft) | `signal.description`, `contact.notes`, `company.name/domain` |
| Continuation voice, not pitch | **Decision**: "Skip the quick peek, schedule full demo" + **Decision**: "Front-door-only positioning, no custom build." | `decision.description`, `decision.rationale` |
| Payment gap mention (extra) | **Signal** (expansion): Heather's interest in AI taking payment. | `signal.description`, `signal.attributed_to` |
| Personal opener (twins / Kitty Hawk) | **Meeting.transcript** directly (not extracted as an entity — personal detail) | `meeting.transcript` |

The last row is interesting: we did NOT extract Walker's personal context (twin girls in NICU, Kitty Hawk location) as a Signal or any other structured entity. It came directly from the transcript during drafting. That's a judgment call — should this kind of personal context be an entity? Probably a ContactProfile-shaped Signal with `type: insight, attributed_to: Walker Ross` capturing "currently on paternity leave, newborn twin girls." Note as a refinement for the Extractor behavior.

## What Kyle can react to

When Kyle sees this, the useful reactions are:

- **"The tone is off"** → refine the Playbook's `artifact_intent` (add voice/style guidance).
- **"You missed X"** → either a gap in extraction (Extractor missed a Signal/Commitment) or a gap in the Playbook requirements (artifact_intent doesn't ask for X).
- **"You shouldn't have mentioned payment at all"** → Playbook should specify "do not surface parked opportunities in early-stage follow-ups."
- **"This is basically what I would've sent"** → the mechanism works; scale it.
