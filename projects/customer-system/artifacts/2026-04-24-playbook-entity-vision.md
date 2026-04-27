---
ask: "Capture the aligned vision for the Playbook entity — what it is, why it exists, how it closes the loop with Proposal generation, how it relates to existing entities"
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
sources:
  - type: conversation
    description: "Craig + Claude alignment session on Apr 24 2026, after Craig corrected the initial Playbook proposal for being (a) seeded from Kyle's PLAYBOOK-v2 doc as-if-it-were-a-spec and (b) routing around a real pipeline bug with a deterministic matcher"
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-23-playbook-as-entity-model.md"
    description: "Prior insight: the entity model IS the playbook; gaps drive next steps. This artifact extends that by naming the Playbook as an explicit entity."
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-24-kyle-craig-apr23-sync.md"
    description: "Kyle's Apr 23 verbal: 'playbook emerges from extractions' — matches the vision here."
---

# Playbook Entity — Vision & MVP

**Status:** aligned Apr 24 2026, not yet implemented. To be seeded with one record (DISCOVERY) for the GR Little end-to-end trace, then extended to DEMO for FoxQuilt.

This artifact is the durable record of what the Playbook is, why it exists, and how it closes the loop with Proposal generation. Future sessions read this to understand where we're going.

---

## What the Playbook is

**The Playbook is the sales motion encoded as data.** Stage-indexed — one record per Stage (DISCOVERY, DEMO, PROPOSAL, NEGOTIATION, ...). Its terminus is the Proposal entity.

Every stage produces some artifact: follow-up email at DISCOVERY, demo agenda and recap at DEMO, the actual proposal document at PROPOSAL, revised proposal or objection response at NEGOTIATION. The Playbook describes *what each of those artifacts must accomplish*, and *what must be true about the entity graph* before the Deal can advance to the next stage.

The whole motion is: **move the Deal from one Stage to the next, hydrating entities along the way, until the Proposal entity can be rendered.** The Playbook is the description of that motion.

---

## Why this matters — the closed loop

Proposal generation is not a special case. It's **artifact generation at the PROPOSAL stage**, driven by the PROPOSAL Playbook record. Same mechanism as the follow-up email at DISCOVERY, same mechanism as the objection handling at NEGOTIATION. Only the Playbook record differs.

This unifies the system. There's no "proposal generator" subsystem separate from "email drafter" subsystem. There's one pattern — `(Deal + recent Touchpoints + extracted intel + Playbook for Deal.stage) → artifact` — and it works for every stage.

The Proposal entity stays as-is: the source of truth for what we're delivering. The PROPOSAL Playbook record's `artifact_intent` is literally "render the Proposal entity + its Phases into the document format we send to customers."

---

## Entity shape (MVP)

One Playbook record per Stage. Low cardinality (7 stages, maybe fewer actively used).

| Field | Type | Purpose |
|---|---|---|
| `stage` | → Stage | Which stage this Playbook applies to. One Playbook per Stage. |
| `description` | str | Human-readable intent: what this stage is about, what we're trying to accomplish here |
| `entry_signals` | list[str] | What in the extracted data tells us a Deal has arrived at this stage |
| `required_entities` | list[str] | Entity types that must be populated with real data before the Deal can exit this stage (e.g., DISCOVERY requires Operation + at least one Opportunity identified; PROPOSAL requires Phase records with linked Opportunities) |
| `expected_next_moves` | list[str] | The moves we expect to make at this stage — phone calls, send materials, book demo, draft proposal |
| `artifact_intent` | str | What the artifact produced at this stage must accomplish. At DISCOVERY: "acknowledge pain raised in the call, confirm the next gate, attach promised materials, reinforce the champion." At PROPOSAL: "render the Proposal entity + its Phases into the document format we send to customers." |

**No state machine.** The Playbook entry itself doesn't transition — it's reference data that describes the stage. Over time it evolves (we refine `artifact_intent` based on what worked), but that's content update, not lifecycle.

**Hydration discipline:** the Playbook's contents are seeded from *intent + what we know works*, then refined from *historical Touchpoint patterns at each stage*. The patterns emerge from extracted data — same discipline as every other entity in this system. We don't import Kyle's PLAYBOOK-v2 field-by-field as spec; we let the historical data teach us what each stage actually looks like in practice.

---

## How it connects to existing entities

| Entity | Relationship |
|---|---|
| **Deal** | `Deal.stage` is the hook. Look up the Playbook where `Playbook.stage == Deal.stage`. No new field on Deal needed. |
| **Stage** | The reference entity that already exists. Playbook has one record per Stage. |
| **Proposal** | The terminus. The PROPOSAL Playbook's `artifact_intent` drives Proposal document generation from Proposal + Phase + Opportunity + AssociateType. Proposal entity shape unchanged. |
| **Phase** | Unchanged. PROPOSAL Playbook reads these to render the proposal doc. |
| **Opportunity** | Unchanged. Playbook may reference "Opportunity must exist and be mapped to an AssociateType" as a `required_entity` for PROPOSAL. |
| **Touchpoint** | Unchanged for MVP. Future refinement: add a `stage` field (what stage was the Deal at when this Touchpoint happened) so we can query historical Touchpoints per stage to inform Playbook hydration. Noted but not required for the demo. |
| **Email / Meeting / Document** | No changes. These flow into Touchpoints, Touchpoints feed Playbook-driven artifact generation. |

---

## The future Artifact Generator associate

Not building this today. Named here so the architectural direction is clear.

**Shape:** an associate whose role watches for `(Deal needs next-move artifact)` signals and produces the stage-appropriate artifact. Inputs: `(Deal + recent Touchpoints + extracted intelligence entities + Playbook for Deal.stage)`. Output: a Document entity (for emails, proposal docs) or a Task entity (for moves like "book a call").

Same pattern for every stage. The Playbook record is what makes the associate stage-aware. When Deal.stage changes, the Playbook it reads changes, and the artifact it produces changes accordingly.

**For today's demo, Claude-in-this-conversation is that associate.** I read the same inputs and produce the artifact. Wiring it as an autonomous associate is a follow-up iteration.

---

## What this implies for other entities and automations (not yet implemented)

These are *implications* of the Playbook direction, not work for today. Noting them so future sessions can evaluate them in context:

1. **Touchpoint.stage field** — to support historical pattern queries per stage. Low cost to add; high value for Playbook refinement.
2. **Stage transition as a capability** — when a Deal's related entities satisfy the current Playbook's `required_entities`, propose a transition to the next stage. Rule-driven via `--auto`, LLM fallback.
3. **Intelligence Extractor becomes stage-aware** — extract different categories of intelligence at DISCOVERY (pain points, tech stack) vs DEMO (objections, competitors) vs NEGOTIATION (commercial concerns). The Playbook record at the Deal's current stage is the context.
4. **Artifact Generator associate** — the one above.
5. **Post-signing playbooks** — same entity pattern extends to Customer Success / Delivery post-Proposal. Different stages, same mechanism. Not in scope for the sales Playbook but the pattern generalizes.

---

## What to do in the demo (GR Little → FoxQuilt)

For the two-hour demo window today:

1. **Create Playbook entity definition** — 6 fields above, one record per Stage, no state machine.
2. **Seed one Playbook record: DISCOVERY** — describing what a first-discovery call's follow-up should accomplish. Minimal but real — intent + required entities + artifact intent.
3. **Run GR Little end-to-end** — Company created, Walker added as Contact, Meeting → Touchpoint → extracted intel. Verify each step works and *why*.
4. **Generate GR Little follow-up email** — Claude reads (Deal at DISCOVERY + Touchpoint + extracted intel + DISCOVERY Playbook) → drafts the email.
5. **If time: seed DEMO Playbook + run FoxQuilt** — Karim/Nick call, extract, draft.
6. **Show Kyle** — side by side: transcript → entities → Playbook → draft email. "Here's what the OS produces. Here's what you'd have sent. Tell me what's missing."

The Playbook in the demo is minimal. The point is to prove the mechanism works end-to-end, not to have a complete playbook library.

---

## Guardrails from the Apr 24 alignment discussion

These corrections shaped this artifact. Preserving them so we don't re-make the same mistakes:

- **Don't import Kyle's PLAYBOOK-v2 field-by-field as the Playbook seed.** Kyle is not a systems engineer; his doc is intent expressed in Claude Code's language. The Playbook hydrates from data we extract, not from Kyle's wishlist. Use Kyle's doc for *what the stages feel like*, not for entity schema.
- **Don't route around pipeline bugs with deterministic matchers.** The LLM can classify an email to a Company. If 446 Companies got created, the fundamental issue is in how the associate is run — data given, tool flow, or skill prompt — not the LLM's capability. Find the root cause, don't bypass it.
- **Vision IS the MVP.** The Playbook's MVP is minimal (one record) but it instantiates the full vision (stage-indexed, artifact-generating, terminating in Proposal). Don't collapse the concept to something less just to ship faster.
- **First principles trace, one meeting at a time.** The two-hour window is better spent running GR Little cleanly end-to-end than firing 72 meetings through and hoping it works.

---

## Open questions (for Kyle sync + future sessions)

- Does each Playbook's `artifact_intent` produce exactly one artifact per Touchpoint, or does it sometimes produce multiple (e.g., a follow-up email + an internal Slack summary)? Leaning: one artifact per Playbook invocation; multiple Playbooks could be wired per stage if we need multiple artifact types.
- When a Deal is at DISCOVERY but has multiple Touchpoints since the last artifact was produced, does the Playbook aggregate across them or produce one artifact per Touchpoint? Probably the former, but surfaces when we actually try to generate.
- Touchpoint.stage field — add now or when the pattern-querying use case lands? Leaning: when it lands.
- How do stage transitions actually happen? Manual for now (Craig transitions Deal.stage). Eventually rule-driven via `--auto` when `required_entities` are satisfied.
