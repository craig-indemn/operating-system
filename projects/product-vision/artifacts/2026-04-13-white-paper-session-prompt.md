---
ask: "The prompt to give to the next Claude Code session to write the white paper"
created: 2026-04-13
workstream: product-vision
session: 2026-04-13-b
sources:
  - type: conversation
    description: "Craig's instruction: the next session must read all files to achieve context saturation, same as session 6 did"
---

# White Paper Session Prompt

**Copy everything below this line and paste it as the opening message to the new session.**

---

I am Craig, de facto CTO of Indemn. Across 6 sessions we've designed the complete architecture for "The Operating System for Insurance" — a domain-agnostic kernel that any business system can be built on, proven first against insurance.

There are 65+ artifacts capturing the full design across 6 sessions, plus context documents, retraces, adversarial reviews, and gap session outputs. The architecture is COMPLETE at the high level. Your job in this session is to write the white paper — one document that consolidates everything into the definitive specification.

You MUST read ALL of the following files before writing anything. Do not skip any. Do not summarize from file names. Read every file in full.

IMPORTANT: Some files will exceed the Read tool's default token limit. When that happens, use Read with offset and limit parameters to chunk through the file, or use Grep/Bash to extract specific sections. Do NOT move on without the full content. Previous sessions made this mistake and it caused problems.

## Files to read (in this order)

### The index (read first for orientation)

projects/product-vision/INDEX.md

### Context documents (session 1 — the business, product, and strategic foundation)

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

### Read LAST (for orientation after full context)

projects/product-vision/artifacts/2026-04-13-white-paper-session-prompt.md

That's 65 files. It's a lot. It's necessary. The architecture was built iteratively across 6 sessions — decisions were made, revised, pressure-tested, ironed, and finalized. You need the full context to write the definitive document.

## What you're writing

**One document with layered depth.** Not three separate documents. One source of truth.

### Structure

| Section | Nature | What it covers |
|---|---|---|
| **1. Vision** | White paper (readable by anyone) | What the OS is, why insurance, why now, the six primitives, the analogy, the three tiers, the intelligence flywheel, EventGuard as proof |
| **2. Architecture** | White paper + spec | Seven kernel entities, watches, rules/lookups, capabilities, skills, the queue, Temporal, OTEL, security model, data architecture |
| **3. Authentication** | Spec | Session entity, 5 auth methods, MFA policy, platform admin cross-org, recovery flows |
| **4. Base UI** | Spec | Auto-generated operational surface, rendering contract, assistant at the forefront, real-time updates |
| **5. Bulk Operations** | Spec | Pattern (not primitive), CLI verb taxonomy, failure handling, scheduled + ad-hoc unification |
| **6. Infrastructure & Deployment** | Spec | Five services, Railway, trust boundary, CLI API-mode, dispatch pattern, production requirements |
| **7. Development & Operations** | Spec | Repo structure, testing, CI/CD, monitoring, debugging, onboarding, platform upgrades |
| **8. Transition & Domain Modeling** | Spec | Coexistence model, migration path, 8-step domain modeling process |
| **9. Dependencies & Resilience** | Spec | Dependency map, graceful degradation, multi-provider LLM |
| **10. Build Sequence** | Plan | Ordered phases, acceptance criteria, what gets built first (derived from sections 1-9) |

Sections 1-2 are the white paper — what Craig hands to investors, stakeholders, Ryan, Dhruv, Kyle, Cam. Readable by anyone technical or non-technical.

Sections 3-9 are the specification — what an engineer or agent builds from. Detailed, precise, no ambiguity.

Section 10 is the build plan — derived from everything above, written last.

## Key guidance

1. **The architecture is FINAL.** Do not redesign, re-question, or re-litigate decisions. The INDEX.md Decisions section is authoritative. If something seems wrong, it was likely decided after extensive discussion — check the relevant session checkpoint before proposing changes.

2. **Later artifacts supersede earlier ones.** The architecture evolved across sessions. When there's tension between an early artifact and a later one, the later one wins. The most authoritative artifacts are:
   - `2026-04-09-consolidated-architecture.md` (session 4 consolidation — but STALE on session 5-6 additions)
   - `2026-04-10-session-5-checkpoint.md` (comprehensive session 5 state)
   - `2026-04-13-session-6-checkpoint.md` (comprehensive session 6 state)
   - `2026-04-13-simplification-pass.md` (final simplification results)
   - Individual session 6 artifacts (bulk ops, base UI, auth, infrastructure, gap sessions)

3. **The simplification pass results are FINAL.** Two architectural simplifications:
   - Watch coalescing removed from kernel → UI rendering concern
   - Rule evaluation traces → metadata in changes collection
   These are decided. The white paper should reflect the simplified architecture.

4. **"Bootstrap entity" is now called "kernel entity."** Seven kernel entities: Organization, Actor, Role, Integration, Attention, Runtime, Session.

5. **The five 2026-04-07 challenge files are JSON conversation logs** (agent outputs from adversarial reviews). They're very large. Use Python JSON extraction or Grep to read the assistant's review content. The key findings are captured in `2026-04-08-pressure-test-findings.md` — but reading the full reviews gives you the depth of thinking that went into the hardening requirements.

6. **Craig's voice should come through.** This is Craig's vision. The white paper should capture the ambition — "the operating system for insurance," not "a platform with entities." EventGuard proved AI can run insurance. The OS makes it repeatable. That's the story.

7. **Do not add, invent, or embellish.** Every concept in the white paper must trace to a specific artifact. If something isn't in the artifacts, it shouldn't be in the white paper. The architecture was designed through extensive discussion and pressure-testing. The white paper consolidates; it doesn't create.

8. **The document should be beautiful.** Clean structure, clear writing, no jargon where plain language serves. Tables where they help. Code examples where they clarify. The first 20 pages should be readable by someone who's never heard of Indemn. The deeper sections should be precise enough that an engineer can build from them.

## After reading everything

1. Tell me you've read all files. Briefly summarize where we are.
2. Propose an outline for the white paper — section headings, estimated page counts, what goes where.
3. Ask me if the outline is right before you start writing.
4. Then write it section by section, showing me each section for review before moving to the next.

Do not start writing until we've agreed on the outline.
