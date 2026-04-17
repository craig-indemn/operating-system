# Notes: context/craigs-vision.md

**File:** projects/product-vision/artifacts/context/craigs-vision.md
**Read:** 2026-04-16 (full file — 107 lines)
**Category:** stakeholder-context

## Key Claims

- **Core thesis (verbatim)**: "If we can create the underlying system that models the entire insurance business — every entity, every workflow, every interaction — and design it to replace or augment our customers' existing systems, then we have something that is the foundation for everything else."
- The platform is the foundation for "agentic agents building agents, migrating companies onto our system, and automating essentially everything within a customer's insurance business."
- **At its core**: "we are modeling the businesses in our space as entities and models and integrating AI into the entire system."
- **Object-oriented insurance system**: every possible thing needed in insurance is modeled as an entity with schemas, state machines, APIs. Compatible with existing systems (AMS, CMS, carrier portals, rating engines), capable of replacing them, AI-native from the ground up.
- **EventGuard/Jewelers Mutual as the proof point**: Indemn already runs an end-to-end insurance program on its own platform; the new system must be able to migrate JM/EventGuard onto it. If it can, it can absorb any customer.
- **Associates as processing nodes**: the associates (Cam's 48-item pricing matrix) are the AI capabilities that operate on domain objects through the platform.
- **Layered architecture**:
  - Domain Objects (nouns: Submission, Quote, Policy, Certificate, Email, Message, actors)
  - Capabilities (verbs: Extract, Validate, Generate, Classify, Route, Notify — Ryan's Layer 3b = what associates DO)
  - Workflow Templates (composed sequences of capabilities, parameterized by customer configuration — Ryan's Layer 3c)
  - Channels (how things enter the system — **AI agents are a CHANNEL, not a separate system**)
  - Customer Configuration (what makes Silent Sports different from GIC different from INSURICA)
- **AI-first design principle**: systems can be interacted with by agents, not just humans. The Indemn CLI (agents creating/evaluating/modifying agents) is the pattern. End state: agents building agents, agents migrating data, agents configuring workflows. **The compounding advantage**: once the domain model exists and is agent-accessible, building new capabilities accelerates exponentially.
- **Moat = the domain model**: insurance-native data model + agent-accessible system + compounding intelligence across every deployment.
- **Political strategy**: must be mindful of how each individual (Ryan/Dhruv/Cam/Kyle) fits in; cannot step on toes; multi-stage engagement; "make it impossible to say no" (business, technical, customer, fundraising angles).
- **The OS (this repo) is both tool + prototype** of the capabilities the platform will provide: CLI tool access, skills architecture, Hive, session mgmt, dispatch — all echoed in the Indemn platform at company scale.

## Architectural Decisions

**Craig's vision is the architectural north star.** It does not specify implementation layers — it specifies the principles those layers must satisfy:

1. **Entity-first**: everything in the insurance business is an entity with schema + state machine + API.
2. **AI-native from the ground up**: not bolted on. CLI / API / skills designed for agent consumption.
3. **AI agents are a channel**, not a separate system. This has direct implications for the harness pattern — agents are clients into the OS, not something the OS embeds/runs.
4. **Compatible + replacement**: must integrate with existing insurance systems AND be capable of replacing them.
5. **Compounding advantage**: once entities + skills + agents are all first-class, building new capabilities compounds. Platform effect.
6. **Associates = processing nodes operating on the platform**, not standalone products.
7. **The CLI pattern**: agents creating/evaluating/modifying agents via CLI is the template. The OS CLI IS the platform's agent interface.

## Layer/Location Specified

- **Platform** = the user interface backed by the domain model (entities + workflows + UI).
- **Associates** = processing nodes (AI capabilities). Operate on domain objects through the platform (i.e., via the platform's interfaces — CLI/API).
- **Channels** = entry points. AI agents are a channel. Voice, chat, email, web forms are channels.
- **Customer Configuration** = per-org differentiation. Implied to be data, not code.
- **Domain Objects** = nouns = entities in the implementation.
- **Capabilities** = verbs = skills/CLI in the implementation.
- **Workflow Templates** = composed capability sequences = skills that orchestrate multiple CLI invocations.

**Finding 0 relevance**:
- "AI agents are a CHANNEL into the insurance platform, not a separate system" — reinforces that agent execution is OUTSIDE the platform core. Agents TALK TO the platform via CLI. The platform doesn't embed LLMs.
- "Associates as processing nodes ON the platform" — associates operate through the platform's interfaces, not embedded in its process.
- **This artifact is foundational evidence for Finding 0**: the vision explicitly places agents outside, as clients. Current implementation places them inside (kernel Temporal worker). Direct contradiction.

## Dependencies Declared

- Existing Indemn CLI (which creates agents, runs evaluations)
- EventGuard/Jewelers Mutual production system (as the migration target)
- OpenTelemetry (referenced elsewhere as observability foundation)
- The rest of the platform stack (implied, not detailed)

## Code Locations Specified

- None. This is a vision statement, not implementation detail.
- The OS repo (this one) is referenced as the prototype: CLI-based tool access, skills architecture, the Hive, session management, dispatch.

## Cross-References

- Ryan's taxonomy (Outcomes → Journeys → Workflows → Capabilities) — Craig adds Domain Objects as the foundational layer
- Cam's 48-item associate matrix (Craig reframes as "processing nodes on a unified platform")
- Kyle's "factory that builds them" framing — Craig: "the factory IS the platform"
- Dhruv's Intake Manager (evolving into the platform core)
- Slack thread with Ryan/Dhruv (March 17) where the Domain Objects + Capabilities + Workflow Templates + Channels + Configuration architecture was first sketched

## Open Questions or Ambiguities

- **How much of existing insurance systems (AMS, CMS, etc.) to integrate vs. replace** is not specified. Left to per-customer strategy.
- **How "workflow templates" compose capabilities** is not fully specified at this level — later artifacts resolve this as skills that invoke CLI commands.
- **"AI-first" at the interface level** — left as a principle; implementation spec is in the white paper + realtime-architecture-design.

**Supersedence note for vision map**:
- Entire vision SURVIVES. This IS the north star. Later artifacts specify the means; this artifact specifies the ends.
- The "AI agents are a channel" statement is ONE of the most load-bearing claims for Finding 0. It's foundational evidence that agent execution must be outside the platform core.
- The moat thesis (insurance-native domain model + agent-accessible + compounding) survives and motivates everything.
