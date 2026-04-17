# Notes: 2026-04-09-session-4-checkpoint.md

**File:** projects/product-vision/artifacts/2026-04-09-session-4-checkpoint.md
**Read:** 2026-04-16 (full file — 175 lines)
**Category:** session-checkpoint

## Key Claims

Session 4 (2026-04-08/09) resolved the wiring question and hardened the architecture. **12 phases** of design evolution:

1. GIC deep-dive (3 parallel research agents)
2. Wiring question resolved: **watches on roles**
3. Actor spectrum (deterministic/reasoning/hybrid — same framework)
4. Entity polymorphism for integrations (collapse Layer 4 into Layer 1 — LATER REVERSED)
5. Kernel vs. domain separation (primitives: Entity + Message + Actor + Role + Organization — 5 here)
6. Entry points and triggers (3 trigger types: message, schedule, direct invocation)
7. Assignment simplified (NOT a primitive; domain concern)
8. Kernel capabilities model (reusable entity methods via CLI)
9. Temporal integration (execution engine for associates only; MongoDB is universal queue)
10. Everything is data (entity defs + skills + rules + configs in MongoDB)
11. 3 rounds of architecture ironing (19 inconsistencies resolved)
12. Security/operations hardening (14 findings with solutions)

**33 architectural decisions DECIDED** through session 4 — enumerated in checkpoint.

## Architectural Decisions (from this checkpoint)

5 kernel primitives at this point: Entity, Message, Actor, Role, Organization. (Integration promoted to primitive #6 in session 5.)

22 architectural decisions + 6 security decisions + 5 infrastructure decisions. Key:
- Watches as wiring
- One condition language (JSON)
- Kernel capabilities = entity methods (unified)
- Skills are markdown
- Everything is data
- Temporal for associate execution (NOT human queues)
- Unified MongoDB queue
- OTEL baked in
- Changes collection + hash chain
- Assignment is domain concern
- Schema migration first-class
- Rolling restart on entity type changes (Beanie for all)
- Seed YAML + template org
- Capability schema versioning
- Scheduled = queue items
- Real-time = queue entry + direct invocation in parallel
- Generic Temporal workflow (claim → process → complete)
- OrgScopedCollection
- AWS Secrets Manager for credentials
- Skill content hashing + version approval
- Rule validation at creation (state fields excluded from set-fields)
- Sandbox contract (Daytona)

## Layer/Location Specified

- All kernel primitives: kernel code.
- Associate execution: Temporal workflows — **location not yet specified in this checkpoint**. Left open until session 5.
- Harness pattern not yet designed.

**Finding 0 relevance**: This checkpoint documents decisions made in session 4. Crucially, agent execution location is left OPEN here. Session 5 (April 10) formalizes the harness pattern — placing agent execution outside the kernel. Phase 2-3 consolidated spec subsequently deviates from that session 5 resolution.

## Dependencies Declared

- MongoDB Atlas (all data)
- Temporal Cloud ($100/mo)
- S3 (files)
- OTEL backend (Grafana Cloud)
- AWS Secrets Manager
- Daytona (sandbox)
- Railway (MVP) → ECS (scale)
- ~$200/mo MVP cost

## Code Locations Specified

- None in checkpoint directly. Points to artifacts containing design.

## Cross-References

- Session 3 checkpoint (precursor)
- All session 4 artifacts (10+ new, listed)
- Session 5 checkpoint (adds Integration primitive, Attention, Runtime, harness pattern)
- Session 6 checkpoint (gap sessions, simplification pass, white paper)

## Open Questions or Ambiguities

Listed as "STILL OPEN" at end of session 4:
- GIC pipeline full retrace against final architecture (done in session 5)
- EventGuard, CRM traces (done in session 5)
- Testing/debugging CLI (gap session #3/4 in session 6)
- Declarative system definition
- Bulk operations (designed session 6)
- Rule composition details (session 5 + consolidated specs)
- No single source of truth document (white paper in session 6)
- Simplification pass (session 6)
- Implementation build order (white paper Section 10, phase specs)
- Stakeholder engagement
- First entity to hand-build

**Supersedence note**: All session 4 decisions SURVIVE. Session 5 adds Integration as 6th primitive, Attention + Runtime as new bootstrap entities, harness pattern, scoped watches, watch coalescing, owner_actor_id, handoff mechanics. Session 6 adds authentication design (Session as 7th kernel entity), base UI operational surface, bulk operations pattern, simplification pass (removes watch coalescing from kernel), documentation sweep.
