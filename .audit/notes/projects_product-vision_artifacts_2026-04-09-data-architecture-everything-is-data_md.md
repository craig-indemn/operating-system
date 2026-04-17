# Notes: 2026-04-09-data-architecture-everything-is-data.md

**File:** projects/product-vision/artifacts/2026-04-09-data-architecture-everything-is-data.md
**Read:** 2026-04-16 (full file — 309 lines)
**Category:** design-source

## Key Claims

- **Everything in the OS is data stored in the database.** Not files in a git repo. Data.
- "The OS codebase (git) is the PLATFORM. The database is the APPLICATION. You deploy the platform once. Everything else is data managed through the CLI."
- Entity definitions, skills, rules, lookups, associate configurations, role configurations — all in MongoDB.
- **Entity definitions are not Python class files on disk.** They're stored in MongoDB. Entity framework creates Python classes dynamically at runtime via `create_model` + dynamic class creation.
- Changes take effect immediately (or after hot-reload signal). No restart.
- Changes collection records every modification with before/after values. Built-in version control.
- **Environments are orgs.** Dev, staging, prod are just different organizations with the same or similar config.
- S3 for unstructured files (PDFs, images, attachments). Scoped by org_id in path. Referenced by entity fields in MongoDB.
- Temporal Cloud for execution (durable workflows, deployment orchestration, scheduled tasks). No application data — only execution state.
- OTEL backend for observability (traces, spans). Linked to permanent records via correlation_id/trace_id.

## Architectural Decisions

- **Clean split**:
  - OS Codebase (Git) = the PLATFORM (kernel + kernel capabilities + CLI + API + UI — deployed once per release)
  - MongoDB = all configuration AND business data
  - S3 = unstructured files
  - Temporal Cloud = execution state (durable workflows)
  - OTEL = observability traces (ephemeral)
- **Per-org config in MongoDB**: entity definitions, skills, rules, lookups, role configs, associate configs, capability activations.
- **Per-org business data**: entity instances, message_queue, message_log, changes collection.
- **Kernel data (cross-org)**: Organization, Actor, Role definitions (bootstrap entities).
- **Files: S3, not GridFS.** Scoped by org. Referenced by entity fields.
- Built-in version control via changes collection. Every change rollbackable. History queryable. Diffs available. Exports provide snapshots.
- **Clone/diff/deploy semantics**:
  - `indemn org clone gic --as gic-staging` copies entity definitions, skills, rules, lookups, watches, associate configs, role configs.
  - **Does NOT copy**: entity instances (business data), message queue/log.
  - `indemn org diff` shows config differences.
  - `indemn deploy --from-org gic-staging --to-org gic` is a Temporal deployment workflow with validate → apply → verify → rollback-on-failure.
- **Import/export**: YAML format for the export of org configuration.
- **Rollback** is CLI command. "Shows preview of what would be rolled back. Requires confirmation."
- Version control granularity: every entity-def modification, every rule change, every skill update is a change record. Specific-object history available.

## Layer/Location Specified

- **Kernel (Git) = PLATFORM code**, specifically:
  - The kernel (entity framework, condition evaluator, queue processor, Temporal integration)
  - Kernel capabilities (reusable entity methods — auto-classify, fuzzy-search, etc.)
  - CLI implementation
  - API implementation
  - UI implementation
- **MongoDB = all config + business data**:
  - Per-org config: entity defs, skills, rules, lookups, role configs, associate configs, capability activations
  - Per-org business data: entity instances, message_queue, message_log, changes
  - Kernel data: Org/Actor/Role definitions (bootstrap)
- **S3 = files** (org-scoped paths, referenced by MongoDB entities)
- **Temporal Cloud = execution state** (no app data, durable workflow state only)
- **OTEL = ephemeral traces**, linked via correlation_id

**Notable omission:** This artifact does NOT discuss harnesses as a layer. The "Platform" is described as kernel + capabilities + CLI + API + UI. Harnesses aren't mentioned here (this is an earlier artifact, 2026-04-09, before the harness pattern formalization on 2026-04-10).

**Clone/diff/deploy is an important Pass 2 check:**
- What gets cloned = entity definitions + skills + rules + lookups + watches + associate configs + role configs.
- What doesn't = entity instances + message queue + message log.
- "Integrations" is NOT explicitly listed in the clone list here. May be in scope of the consolidated specs (which should treat Integration as bootstrap).
- Version tracking: each cloned org has the same entity-def versions to start; subsequent changes are per-org.

## Dependencies Declared

- MongoDB (config + data + changes collection + queue + log)
- S3 (unstructured files)
- Temporal Cloud (durable workflows — including deployment sagas)
- OTEL Backend (Jaeger/Grafana Tempo — traces, metrics, spans)
- Beanie (MongoDB ODM — used for dynamic Document subclass creation)
- Pydantic (`create_model` for dynamic class creation)

## Code Locations Specified

- Kernel code paths: the kernel directory, CLI directory, API directory, UI directory (no specific paths prescribed)
- Kernel capabilities: in the platform codebase
- No entity class files on disk — entity framework creates them dynamically from MongoDB
- S3 path convention: `s3://indemn-files/{org_id}/{entity}/{filename}`
- Temporal Cloud: execution state store, no path

## Cross-References

- 2026-04-09-architecture-ironing-round-3.md — precursor design iteration
- 2026-04-09-data-architecture-solutions.md — supplementary Session 4 data-architecture decisions (referenced from auth design for tamper-evident changes collection, OrgScopedCollection, AWS Secrets Manager)
- 2026-04-09-entity-capabilities-and-skill-model.md — kernel capabilities referenced here
- 2026-03-30-design-layer-3-associate-system.md — associate entity stored as data

## Open Questions or Ambiguities

- **Hot-reload signal for entity definition changes** — "Changes take effect immediately (or after a hot-reload signal)." Mechanism not specified in this artifact. Likely addressed in implementation spec (e.g., Change Stream on entity_definitions collection → in-process reload).
- **YAML export format** — not fully specified (what exactly is in it? how are relationships serialized?)
- **Rollback semantics** — preview shown, confirmation required. Specific behavior for cascading rollbacks (e.g., rolling back a skill change that affected a running associate) not detailed.
- **Versioning granularity for skills** — changes collection records content. How is skill content diffing surfaced? Full content? Field-level?

**Pass 2 observations:**
- **No architectural-layer deviation expected for data architecture.** The design cleanly separates platform (code in Git) from application (data in MongoDB). Current implementation has this split.
- **Clone/diff/deploy semantics** should be verifiable per comprehensive audit: "Clone (config only, no entity instances) — IMPLEMENTED", "Diff (show config differences between orgs) — IMPLEMENTED", "Export (YAML directory: entities/, roles/, rules/{entity}/, skills/*.md, lookups/, actors/, integrations/, capabilities/) — IMPLEMENTED". This artifact says clone doesn't copy instances; implementation should match.
- **Version tracking within the changes collection** should match design: every entity-def modification, rule change, skill update gets a change record.
- **What's NOT clearly stated here but is in section 3a**: the assignment of "Org lifecycle" as a Pass 2 review subsystem. Per this artifact, the design is clear — implementation should match.
