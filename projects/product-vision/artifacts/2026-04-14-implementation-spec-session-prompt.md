---
ask: "The prompt to give to the next Claude Code session to produce implementation specs"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
sources:
  - type: conversation
    description: "Craig's instruction: the next session must read all artifacts and produce implementation specs per build phase"
---

# Implementation Spec Session Prompt

**Copy everything below this line and paste it as the opening message to the new session.**

---

I am Craig, de facto CTO of Indemn. Across 7 sessions we designed and wrote the white paper for "The Operating System for Insurance" — a domain-agnostic kernel built from six primitives (Entity, Message, Actor, Role, Organization, Integration) that any business system can run on.

The white paper is complete. It's the design-level source of truth — WHAT we're building and HOW it works at the architecture level. Your job in this session is to produce **implementation specifications** — the detailed, buildable specs for each phase of the build sequence.

You MUST read ALL of the following files before writing anything. Do not skip any. Do not summarize from file names. Read every file in full.

IMPORTANT: Some files will exceed the Read tool's default token limit. When that happens, use Read with offset and limit parameters to chunk through the file, or use Grep/Bash to extract specific sections. Do NOT move on without the full content. Previous sessions made this mistake and it caused problems.

## Files to read (in this order)

### The white paper (read first — this is the design you're implementing)

projects/product-vision/artifacts/2026-04-13-white-paper.md

### The index (for orientation and the complete decisions list)

projects/product-vision/INDEX.md

### Context documents (the business, product, and strategic foundation)

projects/product-vision/artifacts/context/business.md
projects/product-vision/artifacts/context/product.md
projects/product-vision/artifacts/context/architecture.md
projects/product-vision/artifacts/context/strategy.md
projects/product-vision/artifacts/context/craigs-vision.md

### Session 1 outputs (vision framing)

projects/product-vision/artifacts/2026-03-25-session-notes.md
projects/product-vision/artifacts/2026-03-25-the-operating-system-for-insurance.md
projects/product-vision/artifacts/2026-03-25-why-insurance-why-now.md
projects/product-vision/artifacts/2026-03-25-platform-tiers-and-operations.md
projects/product-vision/artifacts/2026-03-25-associate-architecture.md

### Session 1 domain model

projects/product-vision/artifacts/2026-03-24-associate-domain-mapping.md
projects/product-vision/artifacts/2026-03-25-domain-model-research.md
projects/product-vision/artifacts/2026-03-25-domain-model-v2.md

### Session 2 outputs (entity system, design layers)

projects/product-vision/artifacts/2026-03-30-entity-system-and-generator.md
projects/product-vision/artifacts/2026-03-30-vision-session-2-checkpoint.md
projects/product-vision/artifacts/2026-03-30-design-layer-1-entity-framework.md
projects/product-vision/artifacts/2026-03-30-design-layer-3-associate-system.md

### Session 3 outputs (core primitives, adversarial reviews)

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

### Session 3-4 outputs (primitives resolved, kernel architecture)

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
projects/product-vision/artifacts/2026-04-09-consolidated-architecture.md

### Session 5 outputs (retraces, real-time architecture, Integration as primitive)

projects/product-vision/artifacts/2026-04-10-integration-as-primitive.md
projects/product-vision/artifacts/2026-04-10-gic-retrace-full-kernel.md
projects/product-vision/artifacts/2026-04-10-base-ui-and-auth-design.md
projects/product-vision/artifacts/2026-04-10-eventguard-retrace.md
projects/product-vision/artifacts/2026-04-10-post-trace-synthesis.md
projects/product-vision/artifacts/2026-04-10-crm-retrace.md
projects/product-vision/artifacts/2026-04-10-realtime-architecture-design.md
projects/product-vision/artifacts/2026-04-10-session-5-checkpoint.md

### Session 6 outputs (design sessions, simplification, gap sessions, infrastructure)

projects/product-vision/artifacts/2026-04-10-bulk-operations-pattern.md
projects/product-vision/artifacts/2026-04-11-base-ui-operational-surface.md
projects/product-vision/artifacts/2026-04-11-authentication-design.md
projects/product-vision/artifacts/2026-04-13-documentation-sweep.md
projects/product-vision/artifacts/2026-04-13-simplification-pass.md
projects/product-vision/artifacts/2026-04-13-session-6-checkpoint.md
projects/product-vision/artifacts/2026-04-13-infrastructure-and-deployment.md
projects/product-vision/artifacts/2026-04-13-remaining-gap-sessions.md

### Session 7 output (the white paper — already listed first, but re-read after all artifacts for full context)

projects/product-vision/artifacts/2026-04-13-white-paper.md

That's 66 files. The white paper is the consolidated design. The artifacts are the detailed reasoning behind every decision. You need both to write implementation specs.

## What you're writing

**Implementation specifications for each phase of the build sequence.** The white paper's Section 11 defines seven phases (0-7). Each phase needs an implementation spec that is detailed enough for Craig (with AI) to build from.

### What an implementation spec contains

For each phase:

1. **Scope** — exactly what gets built, what doesn't, and where the boundaries are
2. **Technical decisions** — specific technology choices, patterns, and approaches. This is where MongoDB, Beanie, Pydantic, FastAPI, Typer, Temporal, etc. get specified with reasoning.
3. **Component breakdown** — the specific files, classes, functions, and modules to create
4. **Interfaces** — how components connect to each other, what the contracts are
5. **Data models** — schemas, collections, indexes that need to exist
6. **Acceptance tests** — specific tests that prove the phase is complete
7. **Open questions** — anything that needs research or decision during implementation

### Priority

Start with **Phase 1: Kernel Framework** — this is the critical path. Everything else depends on it. Phase 0 (Development Foundation) can be written alongside or after Phase 1 since it's mostly conventions and setup.

### The relationship between layers

- **White paper** = WHAT and WHY (design level)
- **Implementation spec** = HOW (buildable detail)
- **The artifacts** = the reasoning that informs both

The implementation spec should be consistent with the white paper. Where the white paper leaves room for implementation choice, the spec makes the choice. Where the artifacts contain technical detail the white paper abstracted away (for example, the Beanie entity class patterns from design-layer-1, the message schema from core-primitives-architecture, the Temporal workflow patterns from temporal-integration-architecture), the spec draws on that detail.

## Key guidance

1. **The architecture is FINAL.** The white paper and INDEX.md decisions are authoritative. Do not redesign. The implementation spec decides HOW to build what's already been designed.

2. **Later artifacts supersede earlier ones.** The architecture evolved across sessions. When there's tension between an early artifact and a later one, the later one wins. The white paper reflects the final state.

3. **The simplification pass results are FINAL.** Watch coalescing is a UI concern, not kernel. Rule evaluation traces go in changes collection metadata. "Bootstrap entity" is "kernel entity."

4. **Research before specifying.** Some implementation decisions need current research — library versions, API patterns, deployment configuration. Use web search and documentation. Don't specify based on stale knowledge.

5. **Be specific.** File paths, class names, function signatures, collection schemas, index definitions, configuration formats. The spec should be copy-paste-able into a development session's context.

6. **Flag unknowns.** If something needs a design decision that wasn't made in the white paper or artifacts, flag it clearly. Don't assume.

7. **The build order matters.** Phase 1 must be self-contained and provable before Phase 2 starts. Each phase's spec should be buildable independently given the previous phase is complete.

## After reading everything

1. Tell me you've read all files. Summarize where we are.
2. Propose what the Phase 1 implementation spec should cover — section headings, key decisions to make, what needs research.
3. Ask me questions about anything unclear.
4. Write the Phase 1 spec for my review before moving to other phases.

Do not start writing specs until we've agreed on the approach.
