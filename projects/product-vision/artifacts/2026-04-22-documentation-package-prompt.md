---
ask: "Session prompt for creating the definitive OS documentation package"
created: 2026-04-22
workstream: product-vision
session: 2026-04-22-customer-system
---

# Session Prompt: OS Documentation Package

## COPY EVERYTHING BELOW THIS LINE INTO THE NEW SESSION

---

I am Craig, de facto CTO of Indemn. Over 7 sessions we designed and built the Indemn Operating System — a domain-agnostic kernel built from six primitives (Entity, Message, Actor, Role, Organization, Integration) that any business system can run on. Insurance is where we start.

The design lives across 100+ artifacts in this repository. Some of it was synthesized into higher-level documents. But there is no single, complete, authoritative technical package that captures EVERYTHING a developer needs to know — not just the vision, but every nuance of how the system works in practice.

**Your job: produce that package.**

## What the package is for

1. **Developers** who will help build the OS — they need to read these documents and know exactly how every subsystem works, what the architectural decisions are and why, how data flows, what the code structure is
2. **A landing page** for the OS — the white paper becomes the readable entry point, with links to deeper technical docs
3. **AI sessions** (Claude Code) that build on the OS — they read these docs and know how to use the CLI, define entities, configure watches, build associates
4. **Stakeholders** (investors, partners) — the white paper and vision sections give them the story without the technical depth

## Step 1: Read EVERYTHING

You MUST read every file listed below. No shortcuts. No skimming. Use offset/limit for large files. The depth of thinking in these artifacts is what makes the documentation valuable — if you skip files, you'll produce a surface-level document.

### The existing synthesis documents (read these FIRST for orientation)

1. `projects/product-vision/artifacts/2026-04-13-white-paper.md` — the 11-section vision document
2. `projects/product-vision/artifacts/2026-04-16-vision-map.md` — 23-section design synthesis from 104 files. THIS IS THE AUTHORITATIVE DESIGN REFERENCE.
3. `projects/product-vision/CLAUDE.md` — session bootstrap, artifact index, design integrity rules
4. `projects/product-vision/INDEX.md` — full project history, all artifacts listed, all decisions (there are 100+ decisions in this file)

### The implementation specs

5. `projects/product-vision/artifacts/2026-04-14-impl-spec-phase-0-1-consolidated.md` — kernel framework spec
6. `projects/product-vision/artifacts/2026-04-14-impl-spec-phase-2-3-consolidated.md` — associate execution + integrations spec
7. `projects/product-vision/artifacts/2026-04-14-impl-spec-phase-4-5-consolidated.md` — base UI + real-time spec
8. `projects/product-vision/artifacts/2026-04-17-wiring-audit.md` — 139 behaviors audited across all subsystems

### The built system

9. `/Users/home/Repositories/indemn-os/CLAUDE.md` — the builder's manual (entity types, field syntax, watches, rules, associates, auth, deployment, debugging)
10. `/Users/home/Repositories/indemn-os/README.md` — team entry point
11. `/Users/home/Repositories/indemn-os/docs/getting-started.md` — CLI guide
12. `/Users/home/Repositories/indemn-os/indemn_os/src/indemn_os/init_commands.py` — the CLAUDE.md and domain-modeling skill templates that `indemn init` creates

### The session handoffs (capture what was learned during building)

13. `projects/product-vision/artifacts/2026-04-20-session-handoff.md` — universal session handoff
14. `projects/customer-system/artifacts/2026-04-21-session-handoff.md` — customer system session handoff
15. `projects/customer-system/artifacts/2026-04-20-meeting-ingestion-plan.md` — meeting ingestion design
16. `projects/customer-system/artifacts/2026-04-21-deal-entity-evolution.md` — Deal + SuccessPhase design

### The original design artifacts (read for nuance the synthesis may have flattened)

Read the white paper, vision map, and impl specs first. Then go through these for details the synthesis documents may not fully capture. You don't need to read all 100+ — focus on the ones that cover topics where the synthesis feels thin.

**Session checkpoints** (comprehensive state-of-the-world at each session's end):
17. `projects/product-vision/artifacts/2026-04-08-session-3-checkpoint.md`
18. `projects/product-vision/artifacts/2026-04-09-session-4-checkpoint.md`
19. `projects/product-vision/artifacts/2026-04-10-session-5-checkpoint.md`
20. `projects/product-vision/artifacts/2026-04-13-session-6-checkpoint.md`

**Key design artifacts** (where specific subsystems were designed in depth):
21. `projects/product-vision/artifacts/2026-04-09-unified-queue-temporal-execution.md` — THE unified queue insight
22. `projects/product-vision/artifacts/2026-04-09-data-architecture-everything-is-data.md` — everything is data
23. `projects/product-vision/artifacts/2026-04-10-realtime-architecture-design.md` — Attention, Runtime, harness pattern, scoped watches, handoff
24. `projects/product-vision/artifacts/2026-04-10-integration-as-primitive.md` — Integration as 6th primitive
25. `projects/product-vision/artifacts/2026-04-11-authentication-design.md` — auth end-to-end
26. `projects/product-vision/artifacts/2026-04-11-base-ui-operational-surface.md` — UI as projection of system definition
27. `projects/product-vision/artifacts/2026-04-10-bulk-operations-pattern.md` — bulk ops
28. `projects/product-vision/artifacts/2026-04-13-infrastructure-and-deployment.md` — 5 services, Railway, cost model
29. `projects/product-vision/artifacts/2026-04-13-remaining-gap-sessions.md` — dev workflow, dependencies, operations, transition, domain modeling process
30. `projects/product-vision/artifacts/2026-04-13-simplification-pass.md` — what was simplified and what was kept
31. `projects/product-vision/artifacts/2026-04-09-architecture-ironing.md` — round 1 (7 inconsistencies)
32. `projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-2.md` — round 2 (5 issues)
33. `projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-3.md` — round 3 (7 issues)

**Adversarial reviews** (where the design was pressure-tested):
34. `projects/product-vision/artifacts/2026-04-07-challenge-insurance-practitioner.md`
35. `projects/product-vision/artifacts/2026-04-07-challenge-distributed-systems.md`
36. `projects/product-vision/artifacts/2026-04-07-challenge-developer-experience.md`
37. `projects/product-vision/artifacts/2026-04-07-challenge-realtime-systems.md`
38. `projects/product-vision/artifacts/2026-04-07-challenge-mvp-buildability.md`

**Retraces** (where the kernel was validated against real workloads):
39. `projects/product-vision/artifacts/2026-04-10-gic-retrace-full-kernel.md`
40. `projects/product-vision/artifacts/2026-04-10-eventguard-retrace.md`
41. `projects/product-vision/artifacts/2026-04-10-crm-retrace.md`
42. `projects/product-vision/artifacts/2026-04-10-post-trace-synthesis.md`

### The customer system (first real domain — proves the OS works)

43. `projects/customer-system/INDEX.md` — project status, all decisions
44. `projects/customer-system/artifacts/2026-04-14-problem-statement.md` — 7 problem concepts
45. `projects/customer-system/artifacts/2026-04-14-system-capabilities.md` — 130 capabilities
46. `projects/customer-system/artifacts/2026-04-14-vision-and-trajectory.md` — phased roadmap
47. `projects/customer-system/artifacts/2026-04-14-phase-1-domain-model.md` — 14 entities
48. `projects/customer-system/artifacts/2026-04-14-domain-model-thinking.md` — entity criteria, kernel vs domain

## Step 2: Assess What Exists vs What's Missing

After reading everything, produce a gap assessment:

- **What the white paper covers well** — and what it glosses over
- **What the vision map covers well** — and what nuances from the original artifacts got flattened
- **What the impl specs cover** — and where they're stale (the architecture changed during building)
- **What the CLAUDE.md covers** — and what a developer still wouldn't know after reading it
- **What's NOT documented anywhere** — things that are only in Craig's head or in the code

Specific areas to assess:
1. Entity framework: definition → dynamic class → API/CLI/skill generation. Complete?
2. save_tracked() flow: optimistic concurrency → computed fields → entity write → changes record → watch evaluation → message creation. All nuances captured?
3. Watch system: evaluation, caching, scope resolution (field_path, active_context), entity-local constraint. Complete?
4. Rule engine: conditions, actions (set_fields, force_reasoning), groups, lookups, --auto pattern. Complete?
5. Associate lifecycle: trigger → claim → process → complete/fail. Harness pattern. Skill loading. Complete?
6. Integration system: adapters, credential resolution (actor → owner → org), inbound webhooks. Complete?
7. Authentication: methods, sessions, MFA, platform admin, recovery flows. Complete?
8. Real-time: Attention, Runtime, harness, handoff, scoped watches, events stream. Complete?
9. Observability: changes collection, message log, OTEL traces, correlation IDs. Complete?
10. Deployment: services, trust boundary, Railway, local dev, CI/CD. Complete?
11. Domain modeling process: the 8 steps, entity criteria, kernel vs domain. Complete?
12. Development workflow: repo structure, testing, parallel sessions, conventions. Complete?

## Step 3: Produce the Package

Based on the assessment, produce documents that fill every gap. The package lives in the indemn-os repo under `docs/`. The structure:

```
docs/
  white-paper.md          # Already exists — update if needed
  getting-started.md      # Already exists — update if needed
  architecture/
    overview.md           # System architecture with diagrams (ASCII/Mermaid)
    entity-framework.md   # How entities work end-to-end
    watches-and-wiring.md # How watches, messages, and the queue work
    rules-and-auto.md     # Rules, lookups, capabilities, --auto pattern
    associates.md         # Actor model, skills, harness, execution lifecycle
    integrations.md       # Adapters, credentials, webhooks
    authentication.md     # Auth methods, sessions, MFA, platform admin
    realtime.md           # Attention, Runtime, handoff, scoped watches
    observability.md      # Changes, messages, OTEL, tracing
    infrastructure.md     # Services, deployment, local dev, CI/CD
    security.md           # Org isolation, credential management, skill integrity, audit
  guides/
    domain-modeling.md    # The 8-step process with worked examples
    adding-entities.md    # Step-by-step: define an entity, see it in the system
    adding-watches.md     # Step-by-step: configure watches on a role
    adding-associates.md  # Step-by-step: create a skill, deploy an associate
    adding-integrations.md # Step-by-step: connect an external system
    development.md        # Local dev setup, testing, deploying, conventions
```

### Requirements for each document

- **No hand-waving.** Every mechanism described in full detail — not "watches evaluate conditions" but exactly HOW conditions are evaluated, what operators exist, what entity-local means in practice, what happens when a condition matches.
- **Include the WHY.** Not just what the system does but why it was designed that way. The adversarial reviews and architecture ironing sessions are full of "we considered X but chose Y because Z."
- **Include diagrams.** ASCII or Mermaid for data flows, message cascading, save_tracked() sequence, harness communication, deployment topology.
- **Include CLI examples.** Every concept should have a concrete CLI command showing how you'd actually do it.
- **Reference the code.** File paths for key implementations (e.g., "Watch evaluation: `kernel/watch/evaluator.py`").
- **Capture the nuances.** The things that aren't obvious: selective emission (only state transitions + @exposed methods emit), entity-local watch conditions (no cross-entity reads), heartbeat bypass, bootstrap cascade guard, the difference between claiming and assignment.

### Quality bar

A senior developer who has never seen this system should be able to read the architecture docs and:
1. Understand exactly what the OS is and why it's designed this way
2. Set up a local development environment
3. Define a new entity type and see it working end-to-end
4. Configure watches that route entity changes to the right roles
5. Create an associate that processes work from the queue
6. Connect an external system via an integration adapter
7. Debug any issue using the trace system
8. Deploy changes to production

If they can't do all 8, the documentation is incomplete.

## Step 4: Diagrams

Produce diagrams (Mermaid format for rendering) for at minimum:
1. **System architecture** — the 5 services, trust boundary, what's inside/outside
2. **save_tracked() sequence** — the atomic transaction that is the core invariant
3. **Message cascade** — entity change → watch evaluation → message creation → associate processing → more entity changes
4. **Harness communication** — how a harness connects to the OS via CLI subprocess
5. **Authentication flow** — login, token refresh, session management
6. **Entity lifecycle** — definition → dynamic class → API/CLI/skill/UI auto-generation
7. **Deployment topology** — Railway services, MongoDB Atlas, Temporal Cloud, external dependencies

## What to write to

- Architecture docs: `/Users/home/Repositories/indemn-os/docs/architecture/`
- Guide docs: `/Users/home/Repositories/indemn-os/docs/guides/`
- Update white paper if needed: `/Users/home/Repositories/indemn-os/docs/white-paper.md`
- Commit to the indemn-os repo on main

## Important notes

- The vision IS the MVP. Don't simplify or cut scope. Document what was designed, not a simplified version.
- Where the code diverges from the design (things not yet built), note it clearly: "Designed but not yet implemented."
- The white paper is already good — don't rewrite it. Supplement it with the architecture and guide docs.
- Use the indemn-os CLAUDE.md as the compact reference. The architecture docs are the comprehensive reference.
