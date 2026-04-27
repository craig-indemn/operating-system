---
ask: "Capture the Apr 24 design dialogue between Craig and Claude on the Playbook's role, the Opportunity-vs-Problem distinction, the Document/artifact entity pattern, and the Proposal-as-spine principle. Decisions and open questions for future sessions."
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
sources:
  - type: conversation
    description: "Direct exchange between Craig and Claude following the GR Little trace work, refining the vision"
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-22-entity-model-brainstorm.md"
    description: "The entity model this dialogue is refining"
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-24-playbook-entity-vision.md"
    description: "Prior Playbook alignment which this dialogue evolves"
---

# Design Dialogue — Playbook Role, Opportunity, Document, Proposal-as-Spine

Picking up after Claude completed the GR Little manual trace and produced the first information-flow diagram. Craig pushed back on several points. The refinements below are the result.

This document is a living record of the dialogue — preserve verbatim-ish rather than rewriting as decided-fact, because parts are still open.

---

## Topic 1 — Was extraction knowing-what-to-look-for, or responding-to-what-was-said?

**Craig asked:** *"Was that ['send reply with recording + deck' task] because someone said that in the actual meeting, or it seems like you kind of know ahead of time what information should be extracted from the email based on what stage we are in the pipeline?"*

**Claude answered:** Mostly the first, partly the second. The specific tasks / commitments came from direct statements in the transcript — Walker explicitly asked for the recap, Kyle explicitly offered to scrape the site, Walker explicitly committed to booking and looping in team members. But the *filter* for what's worth extracting was stage-aware. Laundry-pickup wouldn't become a Task. Pain-points become structurally important at DISCOVERY in a way they don't later.

**Craig's position:** *"There's nothing wrong with that."* The stage-awareness is legitimate and expected.

**Resolution — Playbook is consulted TWICE per touchpoint:**
1. By the **Intelligence Extractor** — Playbook tells it what entities to look for at this stage (`required_entities`, `expected_next_moves`). Different stages produce different extraction categories. DISCOVERY extracts Operations / Opportunities / pain points. DEMO extracts objections / feedback on AssociateTypes. NEGOTIATION extracts commercial concerns. Same Extractor mechanism, different extraction schema per Playbook record.
2. By the **Artifact Generator** — Playbook tells it what artifact to render (`artifact_intent`).

---

## Topic 2 — Opportunity vs Problem

**Craig asked:** *"Is there another entity for problem or something instead of opportunity? Maybe opportunity should just map to an associate, but general problems we can keep track of."*

**The distinction Craig is drawing:**
- **Problem** (general) — any pain point we hear about in a customer conversation. Not all of them have product fit. Worth tracking because they show the scope of the customer's operational reality.
- **Opportunity** (specific) — a problem that maps to one of our AssociateTypes. It's a candidate for a future Phase in a Proposal.

**Current entity model has Opportunity with `mapped_associate: AssociateType`.** Without a mapping, the Opportunity is malformed. So today there's no home for pain points that aren't (yet) mapped to a product.

**Implication:** we might need a Problem entity for the "we noticed this, no clear product fit yet" case. Or we loosen Opportunity to allow `mapped_associate: null` with state `unmapped → mapped → validated → proposed → addressed → resolved`.

**Status: OPEN — needs resolution in the next session.** Claude has added a note.

**Practical consequence for today:** Today the GR Little transcript surfaced several pain points (after-hours phones, billing inquiries, outbound renewal, web lead conversion). Three of the four cleanly map to our AssociateType catalog (Front Desk Associate, Billing Associate, Renewal Associate). Those are Opportunities. The fourth (web lead conversion — Walker said their web inbound is low, not a priority) has less clear product fit. For today we'll create 3 Opportunities (mapped) and note the web-leads one as a Signal (insight) only. Revisit if-and-when we add Problem.

---

## Topic 3 — Where do drafted artifacts live in the entity graph?

**Craig pointed out:** *"This was already in the vision, I think, of us talking about the Document Entity. I feel like you're missing some information here, about artifacts. I think this concept already has applied in the past in our thinking and we had decided on what we wanted it to look like."*

**What's already designed** (from `2026-04-22-entity-model-brainstorm.md`):
- Email entity = raw Gmail message.
- Document entity = "any file or artifact exchanged or created."
- Proposal entity has `source_document → Document` — Proposal is structured source of truth, Document is the rendered file.

**The gap in today's session:** Claude drafted a follow-up email and saved it as a markdown artifact file in the project. No entity was created. In the real pipeline, a drafted email needs a home in the graph.

**Status: OPEN — needs revisit.** Claude has saved a memory note (`project_customer_system_artifact_entity_pattern.md`) summarizing the question and candidate resolutions:
1. Every artifact renders to a Document (even emails).
2. Drafts = Documents; sent emails = Email entities; rendered Proposals = Documents linked from Proposal.source_document.
3. Document is only for files; Email is its own entity; the Artifact Generator produces the right type for the artifact.

---

## Topic 4 — Proposal is hydrated AS WE GO, not just at PROPOSAL stage

**Craig's position:** *"When the meeting data gets extracted, that should hydrate into the proposal. If we have found any of those pieces of information that are in the proposal entities, they should be put into the proposal. Then at the point where we create an artifact, we already have that information in the proposal that we know we can reference."*

**Resolution — Proposal entity is created at DISCOVERY (empty), hydrated over time:**

- At DISCOVERY: create an empty Proposal entity for the Deal. Opportunities extracted from the touchpoint get linked to it (or at least to the Deal, which the Proposal references).
- Through DEMO, NEGOTIATION: Opportunities validate, Phases form inside the Proposal, commercial terms fill in.
- At PROPOSAL stage: Proposal is full, ready to render.
- PROPOSAL stage's artifact generation = "render the Proposal + its Phases into a Document to share with the customer."

The Proposal is the **spine**. Every artifact along the way references it or its components. The "render the Proposal as a PDF" is the LAST step — everything before it is hydration.

**Consequence for today:** we should create an empty Proposal entity for the GR Little Deal. It has no Phases yet (not enough signal). It has 3 linked Opportunities (from Topic 2's resolution).

---

## Topic 5 — Transcript access for associates

**Craig's position:** *"There's nothing wrong with any one of the associates being able to read the full email transcript but at the same time I mean I think that's probably necessary actually... That doesn't need to be a formal pattern because in the email entity itself we have the full transcript and that email in that touchpoint are linked to the playbook... we have a cli command to do that just like we have a cli command to do everything else."*

**Resolution — no new pattern needed; we already have it.** Associates have CLI; they can traverse the entity graph. Reading a Meeting or Email fully is just `indemn meeting get <id>` / `indemn email get <id>`. No formalization required.

**But there's a scaling refinement Craig raised:** *"We may have many touchpoints with customers with long transcripts so we can't expect the associate's gonna read every single meeting we've ever had. That's kind of the whole point of us having context curation. Ideally the emails would have enough of a summary. If there's information that's relevant in an email it should probably be extracted into an entity in some way."*

**Principle:** the Touchpoint summary (and the extracted entities per touchpoint) ARE the curation. Associates read summaries across many touchpoints to build context, and dive into raw Meeting/Email content only when they need specific detail. Scale is handled by good summarization + good extraction, not by always-load-everything.

**Consequence for personal context (the NICU/twins thing):** details like "Walker has newborn twins" can:
- Live in Contact.notes (if persistent / ongoing)
- Live in Meeting.summary (if ephemeral / one-touchpoint)
- Be surfaced by an associate reading a recent Meeting directly when drafting

Not every personal detail needs to be an entity. But if something IS recurring (Walker always mentions coastal/NCIUA niche, for example), that belongs in structured form — probably Company.specialties or CompanyProfile.

---

## Topic 6 — Playbook drives touchpoints AND artifacts (different outputs per stage)

**Craig's framing:** *"The touchpoints and the artifacts get generated based on different parts of the playbook. The proposal itself is the culmination of everything but the proposal generation — like the actual document artifact generation from the proposal — would just be like the final step."*

**Resolution — the Playbook orchestrates the whole stage, not just the final artifact:**

| Stage | Touchpoint produced | Entities hydrated into Proposal | Artifact produced |
|---|---|---|---|
| CONTACT | First outreach meeting / email | Company basics | Outreach email / meeting-scheduling |
| DISCOVERY | First-discovery call | Operations, Opportunities, CustomerSystem | Follow-up email with wedge recap + booking next step |
| DEMO | Demo meeting | Opportunities validated; objections as Signals | Demo recap with objections addressed, next-step proposed |
| PROPOSAL | Proposal walkthrough meeting | Phases finalized on Proposal | Rendered Proposal Document; cover email |
| NEGOTIATION | Negotiation calls / emails | Commercial terms on Phases; commitments | Revised Proposal draft; objection-response emails |
| VERBAL / SIGNED | Verbal agreement; contract signature | Proposal.state = accepted | Welcome kit; kickoff agenda |

The Playbook at each stage tells the system:
- What a touchpoint at this stage typically looks like (entry_signals to recognize it)
- What entities must be hydrated before we exit (required_entities)
- What moves we expect (expected_next_moves)
- What artifact to produce (artifact_intent)

PROPOSAL stage's artifact_intent is "render the Proposal entity + Phases + Opportunities into the document we send to the customer." Same mechanism as all prior stages. Just a different render target.

---

## What we're applying to GR Little today

1. **Create 3 Opportunity entities** (after-hours phone, billing inquiries, outbound renewal) — each mapped to its AssociateType. The 4th pain (web lead conversion) stays as a Signal since product fit is unclear.
2. **Create an empty Proposal entity** for the Deal. Link the 3 Opportunities to it. No Phases yet.
3. **Carry two questions forward** (Problem-vs-Opportunity distinction; drafted-artifact entity home). Added to memory so next session picks them up.

## What still needs resolution (open)

- **Problem vs Opportunity** — does the general-pain case need its own entity, or does Opportunity loosen to allow unmapped state?
- **Document-as-artifact pattern for emails** — a drafted follow-up email: Email entity with status=drafting, Document with mime_type=rfc822, or some combination?
- **Do Opportunities link to Proposal directly, or to Deal (with Proposal referencing them via Deal)?** Currently the brainstorm has Opportunity → Phase → Proposal. But Opportunity could also link to the Deal and be "claimed" by a Phase when validated.

## What we're doing for the one-pager

Craig asked for simpler — literally one page, no scroll. Architecture-style: entities as nodes, associates as edges, the Playbook's stage-indexed nature visible. Claude to propose an approach before rebuilding so Craig can react without a full do-over cycle.
