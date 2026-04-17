# Notes: 2026-04-07-challenge-developer-experience.md

**File:** projects/product-vision/artifacts/2026-04-07-challenge-developer-experience.md
**Read:** 2026-04-16 (raw JSON agent transcript — sampled first 3KB + last 5KB; agent summary read in full)
**Category:** design-pressure-test

## Key Claims

Raw transcript of an agent playing "developer evaluating the OS for Insurance" platform. Pressure tests developer experience:
1. Onboarding learning curve
2. Entity class pattern intuitiveness
3. Routing rules complexity (config vs code)
4. CLI as universal interface ergonomics
5. Hello-world complexity
6. Value vs building on AWS/GCP directly

Agent's findings:

**Strengths identified:**
- Entity-to-everything auto-generation is "the killer feature"
- Associate model (AI agents via CLI in sandboxes, guided by auto-generated skills) is "architecturally sound and novel"
- Four-primitive model is clean
- Insurance domain model is the real IP

**Weaknesses identified:**
- Routing rule format undefined (later resolved as watches + condition language)
- Observability and debugging not addressed (later: OTEL + correlation IDs + changes collection + audit CLI)
- "Simple primitives" framing understates real concept count developers must learn
- Testing patterns absent (later: Phase 0 testing strategy)
- **YAML-vs-Python entity definition ambiguity** (later resolved: JSON in MongoDB, dynamic classes)
- Timeline (1-2 weeks for foundation) aggressive
- Lock-in risk real

**Would-choose-this-over-AWS criterion**: "A working Phase 1 with one entity proving the full stack end-to-end."

## Architectural Decisions

This pressure test identified concerns that were addressed in later artifacts:
- Routing rule format → watches (later in 2026-04-10-realtime-architecture-design.md)
- Observability → OTEL + correlation IDs + changes collection (2026-04-09-data-architecture-solutions.md + white paper)
- Entity definition location → JSON in MongoDB, dynamic classes (2026-04-09-data-architecture-everything-is-data.md)
- Testing strategy → Phase 0 unit/integration/e2e layering

No new architectural decision introduced HERE — this is a challenge, later addressed.

## Layer/Location Specified

- No new layer claims. This is a pressure-test transcript.
- Agent flags YAML-vs-Python ambiguity which later resolved (Python classes dynamic from JSON data).

## Dependencies Declared

- None new; evaluates what's in 2026-04-02 artifacts.

## Code Locations Specified

- None new.

## Cross-References

- 2026-04-02-core-primitives-architecture.md (evaluated by this test)
- 2026-04-02-design-layer-4-integrations.md
- 2026-03-30-design-layer-1-entity-framework.md (YAML vs Python ambiguity)
- Informs: 2026-04-08-pressure-test-findings.md (consolidates all 5 challenges)

## Open Questions or Ambiguities

Questions raised and later resolved:
- Routing rule format → watches
- Observability → OTEL + changes + correlation IDs
- YAML vs Python entity definitions → JSON data + dynamic classes
- Testing patterns → spec layers
- Timeline — build attempts showed actual pace

**No Finding 0-class deviation identified by this challenger.** The developer-experience review did not surface the harness pattern issue (that emerged later from the real-time session). This challenge focused on framework ergonomics.
