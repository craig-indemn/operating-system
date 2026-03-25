---
ask: "What are the strategic priorities, political dynamics, and stakeholder considerations?"
created: 2026-03-25
workstream: product-vision
session: 2026-03-24-a
sources:
  - type: google-doc
    ref: "1dQMvFcrFx_n_W0GGsq4bPl3EPpyAADjQ3W3W3GLhOfQ"
    name: "Revenue Engines -- Kyle + Cam Alignment"
  - type: google-doc
    ref: "1TjyiXxHvTmgZQC84SqlgKjytISa3Kc2gHcg8Kz_1NKg"
    name: "Cam Bridge -- Context Layer Design Doc"
  - type: google-doc
    ref: "1NzrLstUfqnvvOOWb-RFceBDIMsGK3wpJgFby_k3NYcs"
    name: "Constraint Removal -- AI Thought Piece"
  - type: meeting-notes
    description: "Craig/Cam 1:1 (Mar 23), Craig/Kyle Sync (Mar 19)"
  - type: conversation
    description: "Craig's statements during product-vision session, 2026-03-24/25"
---

# Strategy Context

## Cam's Priorities and Worldview

### What Cam Cares About:
- **Organizational discipline** as the moat — "not demonstration, discipline"
- **Website as a discipline** — not a one-time project, always evolving, staying 2-3 steps ahead of the prospect
- **Product map** — needs clear distinction between core offerings (low implementation lift) and new builds
- **Sales team utilization** — 52 marketing sheets exist but aren't being used. Accessibility problem.
- **Direction** — "Direction is the difference between a rocket engine and an explosion." Lack of direction = leadership problem, not people problem.
- **Conference demos** — 3 excellent demos focused on customer outcomes, not backend
- **Round three the first time** — context layer so nobody asks Kyle for routine customer info

### Cam's Context Layer (his design, Mar 22):
7-phase plan: Claude Project for Cam → Pipeline Dashboard onboarding → Meetings API to production → Slack Bot MVP → Meeting Intelligence Pipeline → Proactive Intelligence → Individual Claude Code setups.

Success metric: "Cam stops asking Kyle for routine customer context (2 weeks)."

The vision: every person at Indemn can ask "what's the story with [customer]?" and get a complete, current answer without interrupting anyone.

### What Cam has said that matters:
- "What you gave me the last time was the perfect thing to give me the first time." (= 2 free FTEs of recovered productivity)
- Acknowledged Craig's product pages are excellent and "fit into the continuity of the website's flow"
- Concerned about engineering time on content when marketing sheets already exist
- Wants Craig, Cam, Kyle, and Ryan meeting biweekly for big-picture alignment
- Predicted AI-personalized real-time web experiences for each visitor in 2 years

## Kyle's Priorities and Worldview

### What Kyle Cares About:
- **Revenue engines as the moat** — "What we're going to do, nobody else is doing — we're going to sell insurance policies with agents."
- **Joint venture model** — "EventGuard without having to start EventGuard." Find carrier partners, build revenue engines, share economics.
- **Omni-channel workflow automation** — the Series A pitch point
- **Self-service account creation** — customers start their own instance on trial
- **Speed** — "Ship it" mentality. Don't wait for approvals.
- **Three tiers** — middle market machine + enterprise us-strategically + product partnerships

### Kyle's Constraint Removal framework:
Insurance's primary constraint = ACCESS. Generative AI removes it entirely. Like refrigeration didn't make seasonal eating better — it made seasons irrelevant to food.

Looking for: the "Wikipedia of insurance + AI" — the thing with no predecessor. Not just better insurance operations, but something that couldn't exist before.

### What Kyle has said that matters:
- "We need the capital and team to integrate communication systems to manage customers across the entire policy life cycle"
- "EventGuard is where we need the most formal process because of our JM contracts"
- MHL incident: Kyle's technical explanation killed a 90% deal. Fix: don't put Kyle on calls unless Strategic Control outcome.
- "Ship these improvements together, track each in Linear"
- Wants to build Indemn's own website using their own tools — dogfood the technology

## Ryan's Position and Value

### What Ryan Brings:
- Insurance domain taxonomy (Outcomes → Journeys → Workflows → Capabilities)
- UX/product architecture for the platform (wireframes, IA, component inventory, interaction flows)
- The "organizational clarity" voice — identified the risk of "building useful things in isolation"
- Pressure-testing perspective: "Would everyone agree, or would definitions and assessments vary?"
- Smart about when AI should vs. could be used (referenced Aon's approach)

### What Ryan has produced (March 17-23):
- Retail agency wireframes v2 (4 screens)
- GIC wholesaler wireframes + interaction flow
- Placement flows (3 operator scenarios)
- Information architecture
- Component inventory (34 components)
- Consolidated Google Doc with all materials shared to group

### Ryan's key concerns:
- "Seeing an emerging risk of building useful things in isolation, then discovering they weren't designed to connect"
- "Pressing deadlines forced hands — without deliberate awareness of shortcuts being taken"
- Wants system architecture diagrams and shared vocabulary
- Suggested Kyle formalize delegation for architecture work: "otherwise, very easy to slide it off whenever there's a near-term client ask"

## Dhruv's Position and Value

### What Dhruv Brings:
- Built the Intake Manager — the most mature domain model in the company
- Estimates 50-70% of the platform foundation already exists
- Vision for no-code modular platform: users define workflows by chaining components
- Deep technical understanding of extraction, validation, quoting pipelines

### Dhruv's key responses:
- Detailed mapping of IM to Ryan's taxonomy layers (3b capabilities, 3c workflows)
- Listed all domain objects already first-class: Submission, Quote, Parameter, Extraction, Workflow, FormSchema, Event
- Proposed 4 next steps: doc gen as pluggable capability, plug-and-play capabilities, outbound communication, conversational HITL
- On AI vs. non-AI: explained why AI extraction was necessary (form variation, conditional logic compounds)
- Said he'd review Ryan's consolidated materials (Mar 23) — hasn't responded yet

### Critical consideration:
Dhruv's buy-in is the most important. He maintains production AND his work is the platform kernel. He needs to see his Intake Manager as the foundation being built upon, not replaced. The platform vision must honor his architecture decisions while extending them.

## Craig's Political Strategy

### The approach:
- Must be mindful of how each person fits in — no toe-stepping
- Multi-stage engagement, not a document dump
- Make it impossible to say no — every angle addressed
- The delivery process is itself a design problem

### Engagement sequence:
1. **Ryan first** — validate domain model against insurance reality. Low risk, high value. Already thinking this way.
2. **Dhruv second** — show how unified model extends his Intake Manager. His code = the foundation.
3. **George third** — pressure test with EventGuard end-to-end. Concrete validation.
4. **Then Kyle and Cam** — with domain validation and engineering alignment already in hand.

### Key dynamics to manage:
- Cam wants direction and discipline; Craig provides the technical direction
- Kyle wants speed and revenue; the platform enables scaling
- Ryan wants organizational clarity; the domain model provides the shared vocabulary
- Dhruv wants his work valued; the platform is built ON his work
- Ganesh wants involvement; Linear organization gives him a role without blocking critical path

### Craig's role in this:
Architect and owner of the platform vision. Drives the roadmap. Builds the foundation. Owns the OS that executes the work. The de facto CTO making the case for how technology takes the company to the next level.

## The Broader Vision (Craig's Insurance Lab)

Not just a platform — a lab where insurance gets reinvented. The ultimate expression:

Get a cohort of 5 insurance companies. Each joins the Indemn lab. Digitize their entire operation on the platform. Model their business, configure associates, connect channels. AI runs their insurance. Weeks, not months.

This is what makes the vision captivating:
- Not "we unified our codebase"
- Not "we built a better CRM"
- **"Bring us your business, and AI will run it."**

Each company in the cohort proves a different facet:
- A carrier launching a new specialty product (like JM/EventGuard)
- An MGA automating their submission pipeline (like GIC)
- A retail agency digitizing their front office (like INSURICA)
- A program admin standing up new distribution (like Union General)
- A wholesale broker transforming email operations (like GIC email)

This is the Series A story: the platform exists, it works, here are 5 companies running on it, give us $10M to scale to 50.

## What Needs to Be True Before Series A

The vision needs to be READY before funding. When money arrives, scale — don't figure things out.

1. Domain model designed and core entities built
2. At least one associate working on the new platform across two customer types (configuration proof)
3. Portal (Ryan's wireframes) alive on the new platform
4. End-to-end proof (one real scenario running entirely on new platform)
5. The story is proven, not promised

## Timing and Priority Conflicts

Current reality:
- Team is doing custom work per customer, not building platform
- Every customer implementation takes engineering time
- No clear roadmap distinguishing new builds from core offerings
- Cam: "a lack of discipline and poor communication waste valuable time"
- Conference demos needed immediately
- Website launch imminent
- Series A conversations active (Framework VP)

The platform work must coexist with customer delivery. Craig's vision: build the new platform alongside the current system. Current implementations inform the platform design. The new platform is additive, not disruptive.
