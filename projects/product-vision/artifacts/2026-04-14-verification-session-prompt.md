---
ask: "Session prompt for comprehensive verification and review of implementation specifications against the white paper and all design artifacts"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
---

# Verification Session Prompt

You are Craig, de facto CTO of Indemn. Across 8 sessions we designed the "Operating System for Insurance" — a domain-agnostic kernel built from six primitives. The white paper is the design. The implementation specifications are the build plan.

Your job in this session is **verification and review**. You must read the design and the specs, then verify the specs are faithful, complete, correct, and buildable.

## What you MUST read (in this order)

### 1. The white paper (the design source of truth)

projects/product-vision/artifacts/2026-04-13-white-paper.md

### 2. The INDEX.md (all decisions)

projects/product-vision/INDEX.md

### 3. The implementation specifications (what you're verifying)

projects/product-vision/artifacts/2026-04-14-impl-spec-phase-0-1-consolidated.md
projects/product-vision/artifacts/2026-04-14-impl-spec-phase-2-3-consolidated.md
projects/product-vision/artifacts/2026-04-14-impl-spec-phase-4-5-consolidated.md
projects/product-vision/artifacts/2026-04-14-impl-spec-phase-6-7-consolidated.md

### 4. The gap identification (the verification checklist — were all gaps actually resolved?)

projects/product-vision/artifacts/2026-04-14-impl-spec-gaps.md

### 5. The key design artifacts (the reasoning behind the design)

Read ALL of these. They contain the specific patterns, decisions, and rationale that the specs must be faithful to. Do not skip any. Use offset/limit to chunk large files.

Context documents:
- projects/product-vision/artifacts/context/business.md
- projects/product-vision/artifacts/context/product.md
- projects/product-vision/artifacts/context/architecture.md
- projects/product-vision/artifacts/context/strategy.md
- projects/product-vision/artifacts/context/craigs-vision.md

Session 1 outputs:
- projects/product-vision/artifacts/2026-03-25-session-notes.md
- projects/product-vision/artifacts/2026-03-25-the-operating-system-for-insurance.md
- projects/product-vision/artifacts/2026-03-25-why-insurance-why-now.md
- projects/product-vision/artifacts/2026-03-25-platform-tiers-and-operations.md
- projects/product-vision/artifacts/2026-03-25-associate-architecture.md

Domain model:
- projects/product-vision/artifacts/2026-03-24-associate-domain-mapping.md
- projects/product-vision/artifacts/2026-03-25-domain-model-research.md
- projects/product-vision/artifacts/2026-03-25-domain-model-v2.md

Session 2:
- projects/product-vision/artifacts/2026-03-30-entity-system-and-generator.md
- projects/product-vision/artifacts/2026-03-30-vision-session-2-checkpoint.md
- projects/product-vision/artifacts/2026-03-30-design-layer-1-entity-framework.md
- projects/product-vision/artifacts/2026-03-30-design-layer-3-associate-system.md

Session 3:
- projects/product-vision/artifacts/2026-04-02-core-primitives-architecture.md
- projects/product-vision/artifacts/2026-04-02-design-layer-4-integrations.md
- projects/product-vision/artifacts/2026-04-02-design-layer-5-experience.md
- projects/product-vision/artifacts/2026-04-02-implementation-plan.md
- projects/product-vision/artifacts/2026-04-03-message-actor-architecture-research.md

Adversarial reviews:
- projects/product-vision/artifacts/2026-04-07-challenge-insurance-practitioner.md
- projects/product-vision/artifacts/2026-04-07-challenge-distributed-systems.md
- projects/product-vision/artifacts/2026-04-07-challenge-developer-experience.md
- projects/product-vision/artifacts/2026-04-07-challenge-realtime-systems.md
- projects/product-vision/artifacts/2026-04-07-challenge-mvp-buildability.md
- projects/product-vision/artifacts/2026-04-08-session-3-checkpoint.md

Session 3-4 resolution:
- projects/product-vision/artifacts/2026-04-08-actor-spectrum-and-primitives.md
- projects/product-vision/artifacts/2026-04-08-primitives-resolved.md
- projects/product-vision/artifacts/2026-04-08-entry-points-and-triggers.md
- projects/product-vision/artifacts/2026-04-08-kernel-vs-domain.md
- projects/product-vision/artifacts/2026-04-08-pressure-test-findings.md
- projects/product-vision/artifacts/2026-04-08-actor-references-and-targeting.md
- projects/product-vision/artifacts/2026-04-09-entity-capabilities-and-skill-model.md
- projects/product-vision/artifacts/2026-04-09-capabilities-model-review-findings.md

Session 4 (Temporal, data architecture, ironing):
- projects/product-vision/artifacts/2026-04-09-temporal-integration-architecture.md
- projects/product-vision/artifacts/2026-04-09-unified-queue-temporal-execution.md
- projects/product-vision/artifacts/2026-04-09-data-architecture-everything-is-data.md
- projects/product-vision/artifacts/2026-04-09-architecture-ironing.md
- projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-2.md
- projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-3.md
- projects/product-vision/artifacts/2026-04-09-data-architecture-review-findings.md
- projects/product-vision/artifacts/2026-04-09-data-architecture-solutions.md
- projects/product-vision/artifacts/2026-04-09-session-4-checkpoint.md
- projects/product-vision/artifacts/2026-04-09-consolidated-architecture.md

Session 5 (retraces, real-time):
- projects/product-vision/artifacts/2026-04-10-integration-as-primitive.md
- projects/product-vision/artifacts/2026-04-10-gic-retrace-full-kernel.md
- projects/product-vision/artifacts/2026-04-10-base-ui-and-auth-design.md
- projects/product-vision/artifacts/2026-04-10-eventguard-retrace.md
- projects/product-vision/artifacts/2026-04-10-post-trace-synthesis.md
- projects/product-vision/artifacts/2026-04-10-crm-retrace.md
- projects/product-vision/artifacts/2026-04-10-realtime-architecture-design.md
- projects/product-vision/artifacts/2026-04-10-session-5-checkpoint.md

Session 6 (design sessions, simplification, infrastructure):
- projects/product-vision/artifacts/2026-04-10-bulk-operations-pattern.md
- projects/product-vision/artifacts/2026-04-11-base-ui-operational-surface.md
- projects/product-vision/artifacts/2026-04-11-authentication-design.md
- projects/product-vision/artifacts/2026-04-13-documentation-sweep.md
- projects/product-vision/artifacts/2026-04-13-simplification-pass.md
- projects/product-vision/artifacts/2026-04-13-session-6-checkpoint.md
- projects/product-vision/artifacts/2026-04-13-infrastructure-and-deployment.md
- projects/product-vision/artifacts/2026-04-13-remaining-gap-sessions.md

That's 70+ files. Read every one. Some are raw JSON (the adversarial reviews) — extract the review text. Use offset/limit to chunk large files. Do not move on without the full content.

## What you're verifying

After reading everything, verify:

### A. Completeness
For every mechanism in the white paper (Sections 1-11), is there a corresponding specification in the implementation specs? Check:
- Every entity field mentioned in the white paper
- Every CLI command pattern
- Every API endpoint pattern
- Every mechanism (watches, rules, --auto, scoped watches, bulk operations, etc.)
- Every security measure (OrgScopedCollection, credential storage, skill hashing, hash chain, etc.)
- Every operational concern (health checks, logging, deployment, graceful shutdown, etc.)

### B. Faithfulness
Do the specs correctly reflect the design decisions? Check:
- Does the spec match the INDEX.md decisions (160+ locked decisions)?
- Are there any places where the spec diverges from the white paper?
- Are deferred features correctly identified as deferred (not accidentally implemented or accidentally omitted)?
- Does the simplification pass result show correctly (watch coalescing removed from kernel, rule traces in changes collection)?

### C. Correctness
Is the code correct? Check:
- Python type annotations and Pydantic model definitions
- MongoDB query patterns (do indexes support the queries?)
- Beanie integration patterns (does create_model work with Document this way?)
- Temporal workflow/activity patterns (does the SDK work this way?)
- FastAPI route registration patterns
- Auth flow correctness (JWT, session management, MFA challenge)
- Transaction boundaries (are the right things in the same transaction?)

### D. Buildability
Could an engineer build from these specs? Check:
- Are there undefined functions that are called?
- Are there circular dependencies?
- Are there missing imports or references?
- Are there ambiguous patterns where two approaches are described but neither is chosen?
- Are the acceptance tests specific enough to be implemented?

### E. Internal Consistency
Do the four specs work together? Check:
- Do Phase 2 specs correctly use Phase 1 components?
- Do Phase 4 specs correctly extend Phase 1 auth?
- Do Phase 5 specs correctly activate Phase 1 kernel entities?
- Are naming conventions consistent across all specs?
- Are there contradictions between specs?

## How to report

After reading everything, produce an artifact:

`2026-04-14-impl-spec-verification-report.md`

Structure:
1. **Reading confirmation** — confirm you read every file, note any that were problematic
2. **Completeness findings** — what's missing from the specs that the design requires
3. **Faithfulness findings** — where the specs diverge from the design
4. **Correctness findings** — technical errors in the code
5. **Buildability findings** — things an implementer would get stuck on
6. **Consistency findings** — cross-spec contradictions
7. **Overall assessment** — are these specs ready to build from?

For each finding, reference:
- The specific spec section (e.g., "Phase 0+1 section 1.9")
- The specific white paper section or artifact it should match
- The specific issue
- Suggested fix (if obvious)

Be thorough. Be honest. If the specs are good, say so. If they have problems, enumerate every one. Craig needs to know the true state before building.

## Key guidance

1. **Read everything yourself.** Do not use subagents. You need the full context to do meaningful verification.

2. **Later artifacts supersede earlier ones.** The architecture evolved. When there's tension between session 2 artifacts and session 6 artifacts, session 6 wins. The white paper reflects the final state.

3. **The simplification pass results are FINAL.** Watch coalescing is a UI concern, not kernel. Rule evaluation traces go in changes collection metadata. "Bootstrap entity" is "kernel entity."

4. **The specs should be buildable.** Not just architecturally correct — actually buildable. An engineer should be able to read Phase 0+1 and start writing code.

5. **Be ruthlessly honest.** Craig said "there's no room for error." If you find problems, say so clearly. Don't soften findings.
