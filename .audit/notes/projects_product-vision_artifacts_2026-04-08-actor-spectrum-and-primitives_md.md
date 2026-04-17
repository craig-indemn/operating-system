# Notes: 2026-04-08-actor-spectrum-and-primitives.md

**File:** projects/product-vision/artifacts/2026-04-08-actor-spectrum-and-primitives.md
**Read:** 2026-04-16 (full file — 118 lines)
**Category:** design-source

## Key Claims

- **Core insight**: "Everything is CLI. If it's in the CLI, an associate can do it. If an associate can do it, a deterministic process can do it too. The CLI is the universal interface."
- **The deterministic/reasoning split is NOT a separate mechanism**. ONE framework where sometimes the actor reasons (LLM) and sometimes follows fixed procedure, same messages/queues/entities/CLI around it.
- **Entity polymorphism for integrations** (Integration-as-Entity, later walked back): `indemn email fetch-new` works regardless of Outlook vs Gmail; external system detail encapsulated in entity implementation.
- **Primitives compose into everything**: messaging + queue + role-based visibility are primitives, not features bolted on.
- **The Actor as Executor, Skill as Program**: actor = "something that receives a signal and executes CLI commands in response"; skill IS the specification; interpreter can be deterministic or LLM-based; OS doesn't care which.
- **Three skill modes**: fully deterministic, fully reasoning, hybrid. All three are programs executing CLI commands. Different execution engines.
- **Integration collapse proposed**: Layer 4 (Integrations) into Layer 1 (Entity). One primitive, not two. LATER REVERSED (Integration restored as primitive #6 on 2026-04-10).

## Architectural Decisions

- **One actor framework for all execution modes**. No separate deterministic vs reasoning infrastructure.
- **Scheduled tasks are associates with time-based triggers** (no separate primitive).
- **Queue is universal. CLI is universal. Messaging is universal.**
- **"I don't want to waste LLM processing on things that can be done deterministically" — the `--auto` pattern's motivation.**
- **Integration collapsed into Entity** (later REVERSED — Integration is primitive #6).

## Layer/Location Specified

- **CLI = universal interface** — no distinction between who invokes it (human, LLM agent, deterministic script).
- **Actor location NOT specified** — stays open. This artifact says "the actor is the executor" but doesn't place the interpreter in a process.
- **Integration embedded in Entity** — entity polymorphism pattern (later reverted).

**Finding 0 relevance**: The "CLI is the universal interface" principle is the FOUNDATION of the harness pattern. If CLI is universal, and agents call the CLI, then agents are just another client — they can run anywhere (in-process, external image, sandboxed). This artifact established the conceptual basis; 2026-04-10-realtime-architecture-design.md formalized it as "harness = deployable image outside kernel, uses CLI via subprocess."

## Dependencies Declared

- CLI (universal surface)
- Entity framework (with polymorphism)
- Messaging/queue/role system
- LLM (for reasoning-mode skills)

## Code Locations Specified

- No paths. Conceptual.
- Examples of deterministic/reasoning/hybrid skills shown in prose + pseudo-code.

## Cross-References

- Feeds into: kernel-vs-domain (same-day), primitives-resolved (same-day), pressure-test-findings, integration-as-primitive (reverses integration collapse)

## Open Questions or Ambiguities

Listed at end of artifact (4 open questions, resolved in primitives-resolved.md):
1. Minimal definition of Actor
2. How does a Role declare "what comes to me" → watches
3. Where does entity end and actor begin → entity = universal, actor = per-org
4. Scheduled task = actor with time-based trigger → yes

**Supersedence note**:
- "Everything is CLI" principle SURVIVES.
- Actor-skill-interpreter model SURVIVES.
- Three skill modes SURVIVE.
- **Integration collapse REVERSED** — Integration reinstated as primitive #6 two days later.
- "Actor location not specified" → CLOSED as "harness image outside kernel" per April 10 realtime-architecture-design.
