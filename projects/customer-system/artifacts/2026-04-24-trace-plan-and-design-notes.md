---
ask: "Capture the plan for tracing GR Little end-to-end through the entity system, plus the open design question Craig surfaced about reliable Company/Contact identity, before executing"
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
sources:
  - type: conversation
    description: "Craig + Claude Apr 24 alignment before executing the GR Little trace"
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-24-playbook-entity-vision.md"
    description: "The aligned Playbook entity vision this trace will instantiate"
---

# GR Little Trace — Plan & Design Notes

This artifact captures two things before we start writing to the system:

1. **The trace plan** — what we're about to do for GR Little, step by step.
2. **An open design question Craig surfaced** — how does the system reliably avoid duplicate Company/Contact records when something new arrives (email, meeting, form submission, conference lead). Not tackling today, but don't lose it.

---

## The trace plan (GR Little, Apr 22 meeting)

Goal: take the existing Apr 22 meeting through every stage of the entity flow, end to end, and watch what actually happens at each step. When something breaks, find the root cause, don't bypass. Produce a stage-appropriate follow-up email at the end.

### Pre-state (read already, no writes yet)

- Meeting `69eb94a92b0a50861892382a` exists, transcript + summary + 3 participants intact. `company: null`, `touchpoint: null`.
- Five duplicate GR Little Company records exist in the DB. Authoritative choice: **`69eb95f22b0a508618923977`** — "G.R. Little Agency", Broker, domain `grlittle.com`, website `http://www.grlittle.com` (Apr 24 16:10 UTC, most complete).
- Two Walker Ross Contact duplicates exist, both with `email: null`, both pointing to a different Company record. Will consolidate.
- No Heather Contact exists.
- No GR Little Deal exists.
- Two prior Kyle→GR Little emails (Apr 23) exist in inconsistent states (one `processed` with a Company link, one `classified` with no Company).
- A `Playbook` entity definition exists with the wrong shape (integration/timeline/metrics fields). Zero records. Will drop and recreate per the aligned vision.

### Steps

1. **Hydrate authoritative Company** — keep `69eb95f2...3977` as GR Little's canonical record. Flag the other 4 as duplicates to clean up later (not today — Bug #23 makes bulk-delete unreliable and this isn't the critical path).
2. **Hydrate Contacts** — consolidate to one Walker Ross Contact with `email: walker.ross@grlittle.com`, pointing to the authoritative Company. Create one Heather Contact (`heatherf@grlittle.com`) pointing to the same Company.
3. **Create GR Little Deal** — linked to the authoritative Company, `stage: DISCOVERY` (per Kyle's read: first-discovery call, warm, calendly_inbound path).
4. **Drop the existing stale Playbook entity definition and recreate it** with the aligned shape: `stage, description, entry_signals, required_entities, expected_next_moves, artifact_intent`. See `2026-04-24-playbook-entity-vision.md` for the vision.
5. **Seed one Playbook record: DISCOVERY.** Minimal but real — intent + required entities + artifact intent for a first-discovery follow-up email.
6. **Link the meeting to the Company manually.** Set `meeting.company` to the authoritative Company ID. This is the step the Synthesizer would do in an ideal run — we're doing it by hand here to decouple the hydration from the broken classifier flow so we can see what happens next.
7. **Trigger the synthesizer against this one meeting.** Either unsuspend the actor and let a fresh watch fire, or invoke the capability directly. Watch the trace. When the Touchpoint gets created (or doesn't), examine why.
8. **Trigger the intelligence extractor against the Touchpoint.** Watch what extracted entities (Tasks, Decisions, Commitments, Signals) come out. Verify they're right.
9. **Generate the follow-up email.** Claude-in-this-conversation reads `(Deal at DISCOVERY + Touchpoint + extracted intel + DISCOVERY Playbook)` and drafts the email. This is what an Artifact Generator associate will do in a later iteration; today it's us.

At every step: if something doesn't work, understand why. Don't paper over it.

---

## Open design question — reliable entity identity across intake paths

**The question:** When the system encounters a new interaction (email inbound, meeting ingested, conference lead captured, form submitted), how does it reliably decide "this is a Company we already have" vs "this is new, create it"? Same for Contact-to-Company linking.

**Why it matters:** The 5-duplicate-GR-Little mess and the 446-vs-90 Company explosion are both this question, unanswered. The current Synthesizer + Email Classifier associates are making the call inside an LLM context that sometimes has enough information and sometimes doesn't. The result is inconsistent: domain `grlittle.com` matches sometimes, doesn't other times, and we end up with 5 records.

**What Craig said explicitly (Apr 24):**

> "There's nothing wrong in concept with a company being created based on an email. It's just a matter of, you know, can we identify if there's already one there correctly before creating a new one?"

> "We want contacts to be linked to companies and we want there to be a process for that to happen reliably."

**Principles we've aligned on:**

- **Creation can happen at first touch.** A new @foxquilt.com sender with no existing Company is a legitimate trigger to create a Company. Same for a meeting with a participant on an unknown domain. Same for a conference lead. The when-it's-created question has several correct answers — whichever touch happens first.
- **The reliable-identity problem is the hard part.** Not when, but *did we already have this one?*
- **It is not an LLM-capability question.** The LLM can obviously read an email and decide. The breakdown is upstream — what tools/data does the associate have when it makes the decision, what's the search mechanism, what's the tie-breaker when there are multiple near-matches.
- **Don't route around it with a deterministic domain-match rule.** That was the earlier bad proposal. The right answer gives the associate the lookup tools to do it reliably and the skill that says when to ask vs when to create.

**Shape of possible future work (brainstorm, not a plan):**

- A general `entity_resolution` capability — given a candidate (domain, name, email), return all existing Company records that plausibly match. Associates call it before creating.
- A `needs_review` state for ambiguous matches — surface to a human queue rather than guess. Queue is small in practice because most matches are clean.
- Contact-level version of the same: given `(email, name, company_id)`, does this Contact already exist?
- Canonicalization patterns for name variation ("GR Little", "G. R. Little Agency", "G.R. Little Agency", "GR Little Insurance" all being the same org).
- The answer likely lives at the kernel capability layer, not in each individual skill — so it's reusable for Company, Contact, and any future entity with identity questions.

**What we're NOT doing today:** fixing this. For the GR Little trace, Craig and Claude are manually picking the authoritative Company and pointing things at it. This is a knowingly manual step. The real fix is a future piece of work driven by this note.

---

## Signpost for future sessions

If a future session is about:
- **Running the pipeline at scale again** → this question must be answered first, or the duplicate explosion will recur.
- **Designing the Artifact Generator associate** → this question shapes what tools that associate has for entity lookup.
- **Onboarding a new customer through any intake channel** (email, conference, form) → the same reliability discipline applies.

The design work lives somewhere between a new kernel capability (`entity_resolution`) and a skill pattern that every intake-associate uses. Exact shape TBD — it needs its own scoping session when we get to it.
