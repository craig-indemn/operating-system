# Notes: 2026-04-13-white-paper.md

**File:** projects/product-vision/artifacts/2026-04-13-white-paper.md
**Read:** 2026-04-16 (full file — 936 lines)
**Category:** design-source

## Key Claims

- The OS is six primitives (Entity, Message, Actor, Role, Organization, Integration) + seven kernel entities (Organization, Actor, Role, Integration, Attention, Runtime, Session).
- Two-layer architecture: **kernel** (platform, six primitives + mechanisms) vs **domain** (everything built on top — stored as data, no kernel changes needed).
- Every entity defined through CLI auto-generates CLI/API/docs/UI/skill. Self-evidence is the defining property.
- "The OS runs as **five services from one kernel image plus additional service types**" — three kernel processes (API Server, Queue Processor, Temporal Worker) share one image; Base UI and Harnesses are additional service types with their own images.
- **Trust boundary is explicit**: inside = API Server, Queue Processor, Temporal Worker (three kernel processes with db creds); outside = Base UI, harnesses, CLI, Tier 3 apps (API-authenticated only).
- "**CLI in API mode**": CLI always operates as HTTP client to API server. "One behavior regardless of context — local development, production, a harness calling it in subprocess, an engineer running commands remotely."
- Harnesses are explicitly called "one image per runtime kind and framework combination" — voice harness, chat harness.
- "Each harness is a thin piece of glue code — roughly 60 lines — that loads the associate's configuration at session start and uses the CLI for all OS interactions."
- Assistant: "Every human actor has a default associate — an AI assistant pre-provisioned with the same permissions as the user." Operates through same CLI and API as every other associate. "It can execute any operation the user has permission for."
- Bulk operations are a kernel-provided pattern composed from existing primitives (messages + durable workflows + transactions + selective emission), not a separate primitive.
- Authentication: seven methods, Session as seventh kernel entity, MFA role-level with actor/org overrides, platform admin cross-org sessions with time/work-type tags.
- Build sequence phases: 0=foundation, 1=kernel framework, 2=associate execution, 3=integration framework, 4=base UI, 5=real-time, 6=dog-fooding, 7=first external customer.
- Phase 5 "at least one harness proving the pattern (for example, a chat harness bridging a WebSocket server to the kernel via CLI)".

## Architectural Decisions

- **Kernel is domain-agnostic**: no insurance concepts in kernel. Insurance is one domain. Kernel proven against 3 workloads including a zero-insurance B2B case.
- **Everything is data**: entities, skills, rules, lookups, roles, configurations — all stored in database, all managed via CLI. Environments are organizations (dev/staging/prod as separate orgs on same kernel).
- **One save, one event**: selective emission — only state transitions, exposed operations, and entity creation/deletion produce events. Field-only updates are silent.
- **Atomic save-and-emit transaction**: entity save + watch evaluation + message writes = single transaction. "If any part fails, none of it commits."
- **Optimistic dispatch + sweep backstop**: after transaction commits, API fires-and-forgets a workflow start. Queue Processor sweeps for undispatched messages as reliability backstop.
- **Unified queue**: human and AI actors share the same message queue; human claims via UI, associates claim via durable workflow. This enables gradual rollout.
- **Actor spectrum**: deterministic ↔ reasoning, with hybrid via `--auto` pattern (deterministic first, LLM fallback).
- **Credentials never in DB**: Integration entities store reference to external secrets manager. Kernel reads credentials at runtime.
- **Tables over charts**: default UI is interactive tables. Charts reserved for time-series.
- **Auto-generation only for Base UI**: "It is not a bespoke dashboard application with per-organization custom views. No custom UI code per entity. No custom UI code per organization."
- **WebSocket keepalive requirement**: proxy drops idle WebSocket after 60s. All WebSocket handlers — including real-time UI channel AND chat harness — must send ping frames every 30-45s.

## Layer/Location Specified

- **Kernel processes (inside trust boundary, share one image):** API Server, Queue Processor, Temporal Worker
  - API Server: "The gateway. REST API, WebSocket for real-time UI updates, webhook endpoints, authentication endpoints. The only service that faces the internet. Every CLI command, every UI interaction, every harness operation, every Tier 3 API call goes through it."
  - Queue Processor: "A lightweight internal sweep. Catches undispatched workflows, runs escalation checks, creates scheduled queue items. Not the primary dispatch path — a reliability backstop."
  - Temporal Worker: "Executes associate workflows — the generic claim-process-complete cycle, bulk operations, platform deployments."

- **Outside trust boundary (separate deployable images):** Base UI, Harnesses
  - Base UI: "A static application served independently. Connects to the API server only — no direct database access."
  - Harnesses: "One image per runtime kind and framework combination. For example, a voice harness or a chat harness. Each connects to the API server through internal networking and uses the CLI for all OS operations."

- **CRITICAL TENSION**: The white paper says Temporal Worker "executes associate workflows — the generic claim-process-complete cycle" — but the harness section says agent execution happens in harnesses outside the kernel. Resolved only by reading the source design artifact (2026-04-10-realtime-architecture-design.md); white paper is ambiguous on this specifically.
- Assistant per §5: "operates through the same CLI and API as every other associate" — implicitly aligns assistant with harness pattern (it's a user-bound associate).
- Harness code living location: "Harnesses — the glue code per runtime kind and framework — live separately, each producing its own deployable image" (§ Repository Structure)
- Seed files live in their own directory.
- Kernel code lives in one directory.

## Dependencies Declared

- Database (MongoDB implied by wording) — single point of failure. Multi-node replica set with automatic failover.
- Workflow engine (Temporal implied) — durable workflow state. Associate execution depends on it. Graceful degradation: humans continue through unified queue if down.
- LLM providers — per-associate configurable. Multi-provider resilience by configuration.
- Secrets Manager — credential storage. Cached with TTL.
- File Storage — documents/attachments.
- Compute Platform — managed hosting.
- Observability Platform — traces shipped.
- WAF — before first external customer.

## Code Locations Specified

- **Kernel code**: "one directory" (per § Repository Structure)
- **Seed files**: "their own directory"
- **Harnesses**: "live separately, each producing its own deployable image"
- **Base UI**: "own directory with its own build"
- **Tests**: organized by layer — unit, integration, end-to-end

The white paper does not prescribe specific file paths beyond these directory-level commitments.

## Cross-References

- 2026-04-10-realtime-architecture-design.md — source for Runtime/Attention/harness pattern detail (referenced implicitly by § "Attention, Runtime, and Real-Time")
- 2026-04-11-authentication-design.md — source for § 4 Authentication
- 2026-04-11-base-ui-operational-surface.md — source for § 5 Base UI
- 2026-04-10-bulk-operations-pattern.md — source for § 6 Bulk Operations
- 2026-04-10-integration-as-primitive.md — source for Integration primitive treatment
- 2026-04-09-data-architecture-everything-is-data.md — source for § "Everything Is Data"
- 2026-04-09-entity-capabilities-and-skill-model.md — source for Skills + Capabilities + --auto pattern
- 2026-03-30-design-layer-3-associate-system.md — source for Actor/associate system
- 2026-04-13-simplification-pass.md — referenced implicitly (white paper post-simplification state)

## Open Questions or Ambiguities

- **The white paper does not resolve the ambiguity** about whether the agent execution loop (skill interpreter, LLM tool-use loop, execute_command) runs inside the Temporal Worker process (kernel-side, with db access) OR inside a Harness process (outside trust boundary, CLI-only). Both readings are supported by the text:
  - "Temporal Worker. Executes associate workflows — the generic claim-process-complete cycle, bulk operations, platform deployments" → reads as kernel-side execution
  - "Each harness is a thin piece of glue code — roughly 60 lines — that loads the associate's configuration at session start and uses the CLI for all OS interactions" → reads as agent code in harness
  - This is the exact ambiguity that Finding 0 traces to. The source design artifact (2026-04-10-realtime-architecture-design.md) resolves it; the white paper summary does not.
- "Configurable widgets and custom dashboards may be added in the future when forcing functions demand it" — deferred.
- "Active alerting is deferred. The mechanism will likely be watches on kernel entities with actions that invoke notification integrations."
- Fresh MFA re-verification "deferred beyond MVP, where session-level MFA verification is sufficient."
- Tier 3 billing, plan selection, team invitation "deferred beyond MVP."
- Content visibility rules for personal integrations — default stated, but configurable per integration with no schema committed.
