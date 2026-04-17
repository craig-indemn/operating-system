# Notes: 2026-04-08-primitives-resolved.md

**File:** projects/product-vision/artifacts/2026-04-08-primitives-resolved.md
**Read:** 2026-04-16 (full file — 275 lines)
**Category:** design-source

## Key Claims

- **Actor = identity + role + queue + output (CLI commands that change entity state).** Common to human, reasoning associate, deterministic associate. What VARIES is only the execution engine. "The OS should not care about this distinction."
- **Minimal associate = role + skills + mode.** That's it. Mode is deterministic / reasoning / hybrid. LLM config only if reasoning/hybrid.
- **Skill IS the program; the actor is the executor; the interpreter can be deterministic or LLM-based.** Same input (skill + context), same output (CLI commands), different execution engine.
- **Watches are actor-centric** ("this role cares about X"), not system-centric routing rules. The computation is identical; the mental model is different. Watches live on roles, not actors.
- **Entity behavior = universal (platform); actor behavior = per-org (application).** Entity does validation, computed fields, state machines, relationships. Actor does business rules, routing decisions, anything org-specific.
- **Org-aware entity validation allowed** — entity validation CAN reference org configuration (universal rule, per-org result).
- **Scheduled tasks are just actors with a time-based trigger.** Associate trigger types: message (watch matched), schedule (cron), external event (webhook, channel open).
- **"The wiring IS the set of watches across all roles."** Not routing rules. Not connections. Not subscriptions. Watches are an intrinsic part of what a Role IS.
- **Integration collapse**: Integration layer collapses into entity framework. "One primitive, not two." An Outlook email IS an Email entity with Outlook implementation. (This is LATER reversed — Integration becomes primitive #6 in 2026-04-10-integration-as-primitive.md.)

## Architectural Decisions

- **4 primitives here**: Entity, Message, Actor, Role. (Organization, Assignment added in kernel-vs-domain the same day; Integration promoted back to primitive #6 two days later.)
- **Execution mode is an actor property, NOT a separate kernel concept.** "Signal in, CLI commands out" — OS is uniform.
- **No routing rules, no connection layer, no subscription layer.** Role watches are sufficient + complete (one mechanism handles sequential pipeline, conditional routing, fan-out, specific conditions).
- **Per-org watch configuration via CLI** — `indemn role add-watch underwriter --entity Assessment --on created --when "needs_review=true"`.
- **Individual actor filtering is UI-level, not a watch.** All actors with same role get same messages.
- **Integration is encapsulated inside entity implementations.** (Later superseded.)

## Layer/Location Specified

- **Entity framework** = PLATFORM (universal behavior across orgs). Lives in kernel code. Instances + configuration live in MongoDB (per org).
- **Actor framework** = APPLICATIONS (per-org configuration). Kernel provides the framework; orgs configure.
- **Scheduled tasks**: infrastructure-level (cron command) or associate-level (scheduled trigger) — no separate primitive.
- **Where agent execution runs**: NOT specified here. This artifact is pre-Temporal and pre-harness. It says "an LLM interpreter for a more ambiguous program" but doesn't place it architecturally.
- **No trust-boundary or deployment-topology claims** in this artifact.

**Relevance to Finding 0**: This artifact establishes the **actor-skill-interpreter model** without placing it in a specific process. Later artifacts (realtime-architecture-design) place the interpreter in a harness image outside the kernel. Specs deviated from that.

## Dependencies Declared

- CLI `indemn role create|add-watch|set-permissions|list --show-watches`
- CLI `indemn actor create|assign|add-role`
- CLI `indemn associate create`
- CLI `indemn schedule create --cron`
- Implicit: a CLI surface that covers all entity operations

## Code Locations Specified

- No specific code paths. The artifact is pure design. Implementation-layer questions deferred to later artifacts.

## Cross-References

- 2026-04-08-actor-spectrum-and-primitives.md (precursor — actor spectrum insight)
- 2026-04-08-kernel-vs-domain.md (next — adds Organization and Assignment primitives, lifts primitive count to 6 kernel, keeps Integration collapsed for now)
- 2026-04-10-integration-as-primitive.md (supersedes the "integration collapse" claim — Integration is primitive #6)
- 2026-04-09-temporal-integration-architecture.md (adds Temporal as execution engine for associates)
- 2026-04-10-realtime-architecture-design.md (places agent execution in harness images outside kernel)

## Open Questions or Ambiguities

**Deliberately open at this point:**
- Where the "LLM interpreter" runs — not specified. Left open for later artifacts.
- Integration collapse vs. Integration as primitive — resolved the OTHER way two days later (Integration IS a primitive).

**Potential trap**: This artifact's "integration collapse" claim was REVERSED. Reading artifacts chronologically, one might incorrectly carry forward the "one primitive, not two" position. The correct later resolution (2026-04-10-integration-as-primitive.md + white paper) is: 6 primitives including Integration.

**Supersedence note for vision map**: "The wiring IS the set of watches across all roles" survives all the way through. Core to the design. Not superseded.
