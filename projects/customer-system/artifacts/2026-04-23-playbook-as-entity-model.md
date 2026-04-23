---
ask: "How the playbook, the proposal, and the entity model are the same thing — the key insight from the Apr 22-23 brainstorm"
created: 2026-04-23
workstream: customer-system
session: 2026-04-23-roadmap
sources:
  - type: conversation
    description: "Craig + Claude brainstorming, building on Kyle's Slack messages about extracting datasets from sales calls"
  - type: slack
    description: "Kyle's Apr 23 DMs — 'take the two meetings from yesterday and build a dataset around them that we can trust as updates every time a sales call happens'"
---

# The Playbook IS the Entity Model

## The Insight

The Proposal is the destination. The entities IN the proposal need to be filled out. The process of filling them out IS the playbook.

This reframes everything. The playbook isn't a separate document or process definition. It's the entity model itself. Empty fields are gaps. Gaps tell you what to do next. When the gaps are filled, you have a proposal.

## What Goes Into a Complete Proposal

A proposal for any customer requires these entities to be populated:

| Entity | What It Captures | How It Gets Populated |
|--------|-----------------|----------------------|
| **Company** | Who they are — type, size, tech stack, lines of business | First interaction, research, enrichment |
| **Contacts** | People — decision maker, champion, operators | Meetings, emails, introductions |
| **Operations** | What they do — business processes, volumes, staffing, automation level | Discovery calls, data analysis, customer-shared documents |
| **Opportunities** | Gaps — problems mapped to our AssociateTypes and OutcomeTypes | Analysis of Operations against our product catalog |
| **CustomerSystem** | Their tech stack — what we need to integrate with | Discovery, technical deep-dives |
| **BusinessRelationship** | Who they work with — carriers, agencies, vendors | Discovery, research |
| **Phases** | The delivery plan — what we deploy in what order, at what price | Built from Opportunities + internal pricing decisions |

When these are sufficiently populated, a Proposal is a rendering of them. An LLM reads the entities and writes the narrative.

## The Loop

The process isn't linear. It's a loop:

```
Interaction (meeting, email, call)
    → Intelligence extracted (Tasks, Decisions, Commitments, Signals)
        → Entities populated (Company, Operations, Opportunities, Contacts)
            → Gap analysis (what's still missing?)
                → Next action (schedule call, send email, do analysis, draft proposal)
                    → More interactions
                        → More entity population
                            → When complete enough → Proposal
```

Each interaction teaches us something. What we learn populates entities. What's missing drives the next step. The cycle continues until we know enough to propose.

## Kyle's Meeting Example

Kyle's Apr 23 message: "take the two meetings from yesterday and build a dataset around them that we can trust as updates every time a sales call happens."

The "dataset" he's describing IS the entity population:

1. **FoxQuilt CEO meeting** happens → Touchpoint created
2. **Intelligence Extractor** pulls:
   - Decision: "Karim confirms no-cost pilot structure"
   - Task: "Send demo materials in advance"
   - Commitment: "FDE decision needed (Jonathan vs Craig)"
   - Signal: expansion — "interested in Stripe payment recovery automation"
3. **Entities update**:
   - Company: FoxQuilt — digital MGA, AMS=Epic, email=Gmail, data=BigQuery
   - Operation: "Broker portal web chat — 3 people on it all day"
   - Opportunity: "Broker portal bottleneck → Front Desk Associate"
   - Opportunity: "Payment failure/update flow → Billing Associate"
   - Contact: Karim Jamal (CEO), Nick Goodfellow (VP Insurance Ops, champion)
   - CustomerSystem: Epic (AMS), Gmail, BigQuery, Stripe (PCI hard-no)
4. **Gap analysis**:
   - Missing: FDE assignment (Jonathan or Craig?)
   - Missing: pilot scope document
   - Missing: pricing (deferred to post-pilot)
   - Have enough for: Phase 1 proposal (no-cost pilot)
5. **Next steps generated**:
   - Task: "Decide FDE — Jonathan vs Craig" (assigned to Craig)
   - Task: "Send demo materials to Karim before Apr 22 meeting"
   - Draft email: follow-up to Karim confirming pilot structure

This is exactly what Kyle wants. Every sales call produces this. It's repeatable because the entity model is the same for every customer — only the data differs.

## The Alliance Example

Alliance is further along — most entities are already populated:

**What we HAVE:**
- Company: Alliance Insurance, 10K policies, Broker
- Contacts: Christopher Cook (CEO/Agent), Brian Leftwich (operating lead)
- Operations: Renewal outreach — phone, 4K/year, manual, static email templates
- Opportunities: 80% outbound calls unanswered → Renewal Associate
- CustomerSystem: BT Core, Applied Epic, Dialpad
- Multiple meetings and emails in the timeline

**What's MISSING (gaps = next steps):**
- Updated proposal reflecting the renewal wedge pivot (Apr 8 decision)
- Pricing approval from Cam for compound-outcome proposal
- Confirmation of Phase 2+ scope (CSR prep tool, coverage-gap identification)
- Phone AI timing (blocked by Dialpad stabilization)

**Action:** We have enough to build Proposal v2. The gaps are specific enough to generate Tasks.

## How This Changes the Diagram

The diagram should show:

1. **The loop** — not a linear left-to-right flow. Interactions feed entity population, gaps drive next actions, next actions create more interactions.

2. **The entity model as the playbook** — the entities themselves (with their fields) define what we need to know. Empty = gap. Populated = understood.

3. **The Proposal as emergence** — it's not a separate thing we build. It's what you get when the entities are complete enough. The document is generated from them.

4. **Concrete examples** — Alliance (mature, ready for proposal) and FoxQuilt (early, still populating from meetings).

5. **Kyle's meeting flow** — how a single sales call feeds into the loop and produces actionable outputs.

## Why This Matters

If the entity model IS the playbook, then:

- **Every customer follows the same process** — populate the same entities, same fields. The data differs but the structure is universal.
- **Progress is measurable** — count populated vs empty fields. 80% populated = almost ready for proposal.
- **Next steps are automatic** — gaps generate Tasks. "Operation has no annual_volume" = "ask about volume in next call."
- **New team members have a guide** — the entity model tells you what to learn about a customer. No tribal knowledge needed.
- **AI can drive the process** — an associate can look at the entity state and suggest what to do next. "You have Operations but no Opportunities mapped — do you want me to analyze these against our associate catalog?"
- **Kyle's daily dashboard** — for each prospect, show populated vs missing entities. The dashboard IS the playbook status.

## Connection to Kyle's Playbook Documents

Kyle's PLAYBOOK-v2.md defines per-stage operational detail (CONTACT → DISCOVERY → DEMO → PROPOSAL → NEGOTIATION → PILOT → WON). Each stage has entry/exit criteria, cadence, next moves, and signals.

The entity model maps to this:
- **CONTACT stage** → Company + Contact entities populated (who are they, who do we talk to)
- **DISCOVERY stage** → Operations + CustomerSystem populated (what do they do, what tools do they use)
- **DEMO stage** → Opportunities mapped (we've shown how our products solve their problems)
- **PROPOSAL stage** → Phases defined, Proposal entity created with investment terms
- **NEGOTIATION stage** → Proposal in `sent` → `under_review` state
- **PILOT/WON** → Proposal `accepted`, Associates deployed

The Deal entity's state machine (contact → discovery → demo → proposal → negotiation → signed) tracks which stage. The entity population level SHOULD correspond to the stage — you can't be in PROPOSAL stage if you don't have Operations and Opportunities defined.

This is the systematic process Craig described: "if we can get the structure right where it applies for all customers then we have a systematic way of understanding our customers."
