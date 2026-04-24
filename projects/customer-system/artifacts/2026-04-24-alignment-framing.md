---
ask: "Capture today's alignment between Craig and Claude on how to interpret Kyle's prep doc and what today's goal is before the Kyle sync"
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
sources:
  - type: google-doc
    ref: "1yAt-IopSeiJMRW8SVYlJpQOVar7zYwsCEbufXqHsFkA"
    name: "OS Collaboration Prep — Kyle+Craig Sync Apr 24 (Kyle's prep doc with 3-part JSON spec + project plan)"
  - type: google-doc
    ref: "1bHhSG_Eguwh5KXmdFndhAcfvBE4QEaQ0sAbET671h70"
    name: "Craig | Kyle - Sync - 2026/04/23 15:30 EDT - Notes by Gemini (verbal alignment, simpler than prep doc)"
  - type: conversation
    description: "Craig briefing Claude on how to interpret Kyle's material — Kyle is CEO not systems engineer, prep doc is aspirational signal not implementation spec"
---

# Alignment Framing — Apr 24 Kyle Sync

The lens through which we interpret Kyle's prep doc, frame our response, and decide what today's goal is. Written before the Apr 24 sync. Intended as durable context for future sessions.

## Core framing: Kyle's detailed spec is signal, not spec

Kyle is the CEO. He uses Claude Code to generate very detailed documents with field-level specs, enums, JSON shapes, and phased project plans. **He is not a systems engineer and does not have the systems-thinking context to write the OS's entity model for us.** When he hands us something that looks like a specification, it's actually a wishlist of outcomes expressed in the closest language Claude Code could give him.

This matters because when the CEO hands an engineer a "spec" with ICP_TIER enums and `close_confidence` int fields and three-phase project plans, the default move is to pattern-match it as a requirement and debate the details. That is **counterproductive**:

- Kyle doesn't know what he doesn't know. He can't evaluate the trade-offs between "new entity," "new field," "derived view," and "out of scope."
- Debating field names before he's seen a real system output is backwards — we're negotiating a spec against imaginary outputs.
- The time spent aligning on a detailed spec is time not spent making the system useful to him.

**The right move is to extract the intent (what outcomes does he actually want?) and ignore the implementation detail.** Then build what we were already building, show him concrete output, and iterate from there.

## What Kyle actually wants (from Apr 23 verbal sync)

The Apr 23 one-on-one transcript is the cleaner signal:

- **"By looking at yesterday's meeting transcript, we could mock up a follow-up email to see how closely it aligns with what I would have sent — demonstrating immediate utility and scalability for the rest of the team."**
- Alliance first (late-stage → proposal). Then something earlier-stage (like Apr 22 meetings) → define next steps + extract.
- Dashboard views + defined stages → persistent AI agents that analyze data and trigger next steps.
- "Focus on small, useful, and playbook-related activities."
- **Playbook emerges from historical data.** Understand what we've done with customers before, use that as the starting outline, refine over time.

## What Kyle over-specified (Apr 24 prep doc)

The prep doc adds:

- Part 1: Two hand-extracted JSON blobs (FoxQuilt CEO call + GR Little discovery) as an "output shape" target
- Part 2: ~20 fields across Meeting / Company / Deal / extraction categories with specific enums (ICP_TIER, GTM_SEGMENT, sub_type, close_path_template, close_confidence, etc.)
- Part 3: Three-phase / three-week project plan with Friday deliverables (Alliance proposal, Drive adapter, dashboard, per-stage extraction)

Taken literally, this would pull us off our path. Taken as signal, it's useful: it tells us what Kyle wants to *see* the system produce.

## What we're NOT doing in response to Kyle's prep doc

- **Not updating the entity model** to match Kyle's JSON schema. Our entity model (26 entities, locked Apr 22-23) is correct.
- **Not adding ICP_TIER, GTM_SEGMENT, close_confidence, close_path_template** as Deal fields just because Kyle's extraction has them.
- **Not debating data model specifics** with Kyle in the meeting. He doesn't actually want to debate them.
- **Not committing to Kyle's Friday project plan** as written. Drive adapter, Alliance proposal by Fri, per-stage extraction by May 9 — these are aspirational, not a contract.

## What we ARE doing

- **Continuing the path:** recurring email fetch → meeting backfill → meetings flow through extraction pipeline → entities populate → playbook emerges → proposal generation.
- **Showing Kyle the outcome he actually asked for verbally Apr 23:** a mocked-up follow-up email from one of the Apr 22 meetings, generated from what the OS extracted.
- **Introducing the Playbook** (as entity or doc — to be decided) as the layer that connects "what was extracted" to "what action to take." Without a playbook, a follow-up email is just a summary. With one, the email drives toward the known next step for that stage.
- **Framing to Kyle as outcome-led:** "Here's what comes out today. Here's the draft email. What's missing?" Not: "Let's align on the schema."

## Today's concrete goal

Walk into the Kyle sync with a **side-by-side demo**:

```
Apr 22 meeting transcript
    ↓ (ingested by OS — Meet API + Gmail)
Touchpoint entity
    ↓ (Intelligence Extractor)
Tasks / Decisions / Commitments / Signals / linked entities
    ↓ (Playbook entity + extracted info)
Draft follow-up email to the prospect
```

Kyle's feedback loop: "send this as-is" / "change X, Y, Z." Either way, we learn what a real playbook looks like.

## Systematic path to get there (order matters)

1. **Finish data ingestion hygiene** — set up recurring email fetch, backfill meetings (30-day window includes Apr 22).
2. **Verify the Apr 22 meetings flow through the pipeline** — Foxquilt+Karim and GR Little+Walker become Meetings → Touchpoints → intelligence extracted.
3. **Define the Playbook** — at minimum as a doc, ideally as an entity, describing per-stage: entry criteria, exit criteria, expected next moves, follow-up email structure/intent, signals to watch.
4. **Generate the follow-up email for one or both Apr 22 meetings** — first pass in Claude Code (so we have something to show), then wire up as an Associate skill if time permits.
5. **Package as a one-screen side-by-side for Kyle** — transcript → extracted entities → playbook-driven email.

## The Playbook insight (new)

Craig surfaced this explicitly today: **"Without the playbook, what is the email really trying to accomplish?"**

The playbook is what tells the system: *after a discovery call with a warm agency prospect, the follow-up email should (a) acknowledge specific pain points raised, (b) reiterate our proposed wedge, (c) confirm the next meeting or gate, (d) include any requested materials, (e) reinforce the champion.* Without that prescription, the extractor just dumps what it heard — which is a summary, not a next step.

This is consistent with Kyle's PLAYBOOK-v2 document (per-stage operational detail with entry/exit criteria, cadence, next moves, signals) — and the realization that the playbook itself lives in the system, informs associate behavior, and is the layer that makes extraction → action possible.

Open question: is the Playbook a new entity (with one record per stage, referenced by Deals) or a skill document attached to associates? Leaning entity — it's queryable, versionable, and everything else in the system is an entity.

## How we frame Kyle's over-specification to him

Respectful but direct:

> "I read your prep doc. The thinking in it is useful — it tells me what you want to *see* from the system. But we're not going to debate the schema today. Instead, I want to show you what the system produces right now for one of those Apr 22 meetings, and the follow-up email that comes out the other end when we apply a playbook. You tell me what's missing or wrong — that's a more efficient feedback loop than aligning on field names before you've seen an output."

Two things to be clear on:
- Not rejecting his thinking. The needs in his spec are real (ROI matters, network anchors matter, provenance matters). They'll be absorbed into the playbook or into entity fields as the model teaches us what's actually load-bearing.
- He said it himself Apr 23: **playbook emerges from historical data**. That IS our architecture. We're aligned on the goal. The disagreement is only about how much to pre-specify.

## What carries forward to future sessions

- **The lens:** Kyle's technical specs are aspirational signal, not implementation requirements. Extract intent, ignore field-level detail.
- **The vision:** customer interactions (email + meeting) → Touchpoints → extracted intelligence → Playbook-informed next-step artifacts (emails, proposals, task lists) → human approval → send.
- **The path:** Alliance end-to-end proposal is still the North Star (late-stage wedge), but Kyle now also wants early-stage demo (Apr 22 meetings → follow-up emails).
- **The playbook question:** new Playbook entity or doc-attached-to-skill — resolve during this work.
- **The team-adoption angle:** if we make this visibly useful for Kyle, he'll push the team onto it. That was his Apr 23 "scalability for the rest of the team" line.

## References

- `projects/customer-system/artifacts/2026-04-24-kyle-craig-apr23-sync.md` — Apr 23 Kyle+Craig sync transcript
- `projects/customer-system/artifacts/2026-04-24-kyle-prep-doc-apr24.md` — Kyle's full Apr 24 prep doc (preserved for reference, to be treated as aspirational)
- `projects/customer-system/artifacts/2026-04-23-playbook-as-entity-model.md` — prior insight: the playbook IS the entity model (gaps drive next steps)
- `projects/customer-system/artifacts/2026-04-22-entity-model-brainstorm.md` — locked entity model
- `projects/customer-system/artifacts/2026-04-23-implementation-session.md` — what we built Apr 22-23
