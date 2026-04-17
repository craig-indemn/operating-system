# Notes: 2026-04-07-challenge-mvp-buildability.md

**File:** projects/product-vision/artifacts/2026-04-07-challenge-mvp-buildability.md
**Read:** 2026-04-16 (JSON transcript — 2 lines; embedded prompt + agent response)
**Category:** design-pressure-test

## Key Claims

- Pressure test by "pragmatic startup CTO" persona. Focus: shipping reality vs. plan.
- **4-6 weeks is NOT realistic** for the planned scope. Realistic: 10-14 weeks for something a customer could touch.
- **Hidden delays**: MongoDB schema iteration (base Entity class evolves 3+ times), state machine edge cases, auth + multi-tenancy nuance, last 20% of every integration.
- **Over-engineered for MVP**:
  - 44 entities across 9 sub-domains (should be 5: Contact, Policy, Submission, Quote, Payment)
  - Auto-generated everything (build 3-5 by hand first, THEN extract the generator)
  - Full message routing (simple task queue for MVP)
  - AI associates as sandboxed-CLI deep agents (for MVP: Claude API + structured output + human review)
  - Auto-generated React UI (hand-build one beautiful screen for demo)
- **Under-engineered**:
  - No testing strategy specified
  - No error handling / recovery / transactions / idempotency / rollback
  - No monitoring, logging, metrics, alerting, health checks
  - No data migration strategy (schema-flexible ≠ schema-free)
  - No compliance/audit trails
  - No carrier data normalization (this is where 50% of insurance-tech time goes)
- **"Internal CRM first" strategy — MIXED**:
  - Good: build platform, use it to manage INSURANCE customers (exercises insurance flows)
  - Bad: build platform, use it for COMPANY operations (tracks leads, not insurance)
- **AI-parallel-sessions claim**: schema generation works (~3-4x multiplier); integration works poorly (inconsistent interpretations, shared dependency conflicts, illusion of progress). Requires tight coordination + clear contracts before parallel sessions start.
- **What to ship first (for Series A)**: 10-minute demo showing email → extract → submission → carrier match → quote request, with AI narration + human approval gates. 5 entities (Contact, Submission, Quote, Policy, Activity), one workflow, one AI associate, one beautiful UI dashboard. 10 weeks with buffer.

## Architectural Decisions

- **Ship smallest thing that proves thesis** — not smallest architecture, smallest EXPERIENCE.
- **Reduce from 44 entities to 5 (or 7) for MVP.**
- **Hand-build the first entities, extract the generator later.**
- **Don't build framework before knowing what pattern to generate** (auto-generators are traps before they're force multipliers).
- **Don't put LLM in entity write path** (same as distributed-systems pressure test).
- **Find one friendly agency for realistic dog-fooding** (not use our own CRM).

## Layer/Location Specified

- No specific layer/location claims. This is a buildability review, not architecture.
- Implicit: the proposed architecture is sound at scale but wrong-sized for MVP.

**Finding 0 relevance**: This pressure test DID NOT address agent execution location. Its concerns are scope and timeline, not architectural layer.

## Dependencies Declared

- Claude API
- MongoDB + FastAPI + Beanie + Pydantic
- React (hand-built, not generated)

## Code Locations Specified

- No paths. Recommends starting with:
  - 5 entities (Contact, Submission, Quote, Policy, Activity)
  - One intake associate using Claude API directly (not sandboxed CLI deep agent)
  - One hand-built React dashboard
  - FastAPI backend, MongoDB, proper auth, org scoping, submission intake webhook

## Cross-References

- Other pressure tests (realtime, distributed, insurance-practitioner, developer-experience)
- Feeds into: pressure-test-findings (synthesis), implementation-plan revisions, white paper

## Open Questions or Ambiguities

- **Timeline**: the subsequent 6-phase implementation plan compressed to 6 weeks. The final 8-phase white paper extended substantially. In practice (Phase 6 dog-fooding pending, Phase 7 first customer pending), this pressure test's estimate is proving directionally correct.
- **Scope**: the 44-entity count was reduced significantly in subsequent artifacts. The current kernel has ~7 kernel entities + ability to configure domain entities via CLI — NOT 44 kernel entities. The domain can have many entities per deployment (44+), but none are in kernel code.

**Supersedence note**:
- The 5-entity MVP proposal was NOT literally adopted (the kernel entity set is 7, reflecting architectural needs).
- The "build 3-5 by hand, extract the generator" principle WAS adopted: the 7 kernel entities are hand-written (Python classes with `KernelBaseEntity`); domain entities use the CLI-driven dynamic definition pattern.
- "No full deep-agent runtime for MVP" — PARTIALLY. The current code has `_execute_reasoning` in kernel (not deep-agent with middleware). Full deepagents is deferred to harness pattern (Finding 0).
- "Find friendly agency for dogfooding" — reflects in Phase 7 (GIC).
