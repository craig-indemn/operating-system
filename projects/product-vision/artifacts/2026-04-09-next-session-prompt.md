---
ask: "The prompt to use for the next session — reads everything, has complete context, produces the kernel spec"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08/09
---

# Next Session Prompt

Copy everything below the line and use it as the prompt for the next session.

---

Resume the product-vision project. I am Craig, de facto CTO of Indemn. Across 4 sessions we've been designing the architecture for what we're calling "The Operating System for Insurance" — a domain-agnostic kernel that any business system can be built on, proven first against insurance.

There is extensive thinking captured in artifacts across 4 sessions. The design has evolved significantly through iteration, pressure testing against real systems, and multiple rounds of independent review. You MUST read ALL of the following files before responding. Do not skip any. Do not summarize from file names. Read every file in full.

## Context and Vision (Sessions 1-2) — The WHY and WHAT

Read these first. They establish the business context, the vision, and the initial thinking:

```
projects/product-vision/INDEX.md
projects/product-vision/artifacts/context/business.md
projects/product-vision/artifacts/context/product.md
projects/product-vision/artifacts/context/architecture.md
projects/product-vision/artifacts/context/strategy.md
projects/product-vision/artifacts/context/craigs-vision.md
projects/product-vision/artifacts/2026-03-25-session-notes.md
projects/product-vision/artifacts/2026-03-25-the-operating-system-for-insurance.md
projects/product-vision/artifacts/2026-03-25-why-insurance-why-now.md
projects/product-vision/artifacts/2026-03-25-platform-tiers-and-operations.md
projects/product-vision/artifacts/2026-03-25-associate-architecture.md
projects/product-vision/artifacts/2026-03-30-entity-system-and-generator.md
projects/product-vision/artifacts/2026-03-30-vision-session-2-checkpoint.md
```

## Design Evolution (Sessions 3-4) — The HOW and the journey

Read these next. They show how the architecture was designed, challenged, and refined:

Session 3 (initial design + adversarial review):
```
projects/product-vision/artifacts/2026-03-30-design-layer-1-entity-framework.md
projects/product-vision/artifacts/2026-03-30-design-layer-3-associate-system.md
projects/product-vision/artifacts/2026-04-02-core-primitives-architecture.md
projects/product-vision/artifacts/2026-04-02-design-layer-4-integrations.md
projects/product-vision/artifacts/2026-04-02-design-layer-5-experience.md
projects/product-vision/artifacts/2026-04-02-implementation-plan.md
projects/product-vision/artifacts/2026-04-03-message-actor-architecture-research.md
projects/product-vision/artifacts/2026-04-07-challenge-insurance-practitioner.md
projects/product-vision/artifacts/2026-04-07-challenge-distributed-systems.md
projects/product-vision/artifacts/2026-04-07-challenge-developer-experience.md
projects/product-vision/artifacts/2026-04-07-challenge-realtime-systems.md
projects/product-vision/artifacts/2026-04-07-challenge-mvp-buildability.md
projects/product-vision/artifacts/2026-04-08-session-3-checkpoint.md
```

Session 4 (pressure testing against GIC, kernel refinement, Temporal, everything-is-data):
```
projects/product-vision/artifacts/2026-04-08-actor-spectrum-and-primitives.md
projects/product-vision/artifacts/2026-04-08-primitives-resolved.md
projects/product-vision/artifacts/2026-04-08-entry-points-and-triggers.md
projects/product-vision/artifacts/2026-04-08-kernel-vs-domain.md
projects/product-vision/artifacts/2026-04-08-pressure-test-findings.md
projects/product-vision/artifacts/2026-04-08-actor-references-and-targeting.md
projects/product-vision/artifacts/2026-04-09-entity-capabilities-and-skill-model.md
projects/product-vision/artifacts/2026-04-09-capabilities-model-review-findings.md
projects/product-vision/artifacts/2026-04-09-temporal-integration-architecture.md
projects/product-vision/artifacts/2026-04-09-unified-queue-temporal-execution.md
projects/product-vision/artifacts/2026-04-09-data-architecture-everything-is-data.md
projects/product-vision/artifacts/2026-04-09-architecture-ironing.md
projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-2.md
projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-3.md
projects/product-vision/artifacts/2026-04-09-data-architecture-review-findings.md
projects/product-vision/artifacts/2026-04-09-data-architecture-solutions.md
projects/product-vision/artifacts/2026-04-09-session-4-checkpoint.md
```

## The Current Architecture (read LAST)

This consolidates all decisions into one document. Read it after everything else so you understand both the current design AND the reasoning behind each decision:

```
projects/product-vision/artifacts/2026-04-09-consolidated-architecture.md
```

## After Reading Everything

I need you to do the following:

1. **Tell me what you understand** about the vision, the architecture, and where the thinking stands. Focus on the big picture — the kernel primitives, how they compose, and the key design principles. Don't recite back every detail — show me you understand the SYSTEM.

2. **Tell me what questions you have** — things that seem unresolved, contradictory, unclear, or undertested. The session 4 checkpoint lists what's open. You may find more.

3. **Tell me what concerns you** — gaps, risks, assumptions that haven't been validated. Fresh eyes on the whole thing.

4. **Do NOT assume any previous decision is final.** The design evolved significantly across sessions — early decisions were revised or overturned when they didn't hold up. Challenge anything that doesn't make sense.

5. **Keep the big picture in mind.** We've been deep in the weeds on implementation details. I need a partner who can see the forest AND the trees. The system should be simple, intuitive, composable. If something feels over-complicated, say so.

The ultimate goal: turn this architecture into an actionable kernel specification — a document clear enough that an engineer (or an AI agent) can build from it. We're not there yet. There's simplification needed, open questions to close, and the spec itself to write. Help me get there.
