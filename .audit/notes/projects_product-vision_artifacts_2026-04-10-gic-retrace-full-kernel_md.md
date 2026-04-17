# Notes: 2026-04-10-gic-retrace-full-kernel.md

**File:** projects/product-vision/artifacts/2026-04-10-gic-retrace-full-kernel.md
**Read:** 2026-04-16 (full file — 515 lines)
**Category:** design-retrace

## Key Claims

- **First retrace (GIC = B2B insurance email pipeline)** against the updated 6-primitive kernel (Entity, Message, Actor, Role, Org, Integration).
- **End-to-end flow traced**: scheduled Outlook sync (Email sync associate) → extraction (if attachments) → hybrid classification (rules first, LLM fallback) → linking (pattern → fuzzy → LLM) → assessment (reasoning) → draft generation (reasoning) → human review (JC/Maribel) → outbound send → scheduled stale detection → ops triage.
- **Every step is a Temporal workflow claim on the unified MongoDB queue.**
- **Watches handle all orchestration** — zero `processing_status` orchestration fields on Email; each step emerges from the previous step's emitted event.
- **The `--auto` pattern** eliminates LLM waste: classification, linking, completeness-check try deterministic rules/patterns first, LLM on fallback.
- **Correlation ID chains full pipeline** (8+ hops, same correlation_id throughout).
- **Multi-entity atomicity via MongoDB transactions** for single-turn operations (linker creates Submission + updates Email; assessor creates Assessment + updates Submission stage).

## What Surfaced (6 findings, all additive)

### 1. Bulk event emission → queue spikes (NEW KERNEL FEATURE — watch coalescing)
- 50 stale submissions flagged in one txn → 50 messages in ops queue → Maribel sees 50 rows at once.
- **Proposed**: `coalesce` config on watches. Batch messages from same correlation_id within a window into one queue item with summary + drill-down.
- **Status**: LATER **REMOVED FROM KERNEL** per 2026-04-13-simplification-pass.md. Coalescing is UI-only (group by correlation_id). No `coalesce` field on watches, no `batch_id` on messages, no grouping logic in emission path.

### 2. Pipeline overview ≠ queue (auto-generated dashboards)
- Ops/leadership wants state distribution, throughput, queue depth, integration health — these are aggregations, not queue items.
- **Resolution**: Auto-generated dashboards in base UI. Sourced from: entity state machine distribution, message_log throughput, queue depth per role, Temporal workflow history, Integration status. No new primitives — just rendering layer.
- **Later formalized** as `state-distribution`, `throughput`, `dwell-time`, `queue-depth`, `cascade-lineage` kernel capabilities in base-ui-operational-surface.md.

### 3. Human-in-progress soft-lock (ephemeral entity locks)
- JC opens a draft to review, walks to meeting, another user grabs it. Race on review.
- **Proposed**: `indemn entity lock` — ephemeral informational locks. Heartbeat keeps alive, auto-expires.
- **Later formalized** as **Attention** entity in 2026-04-10-realtime-architecture-design.md (unifies UI soft-lock + active routing context).

### 4. Multi-LOB draft consolidation — DOMAIN CONCERN, not kernel
- One email requests GL + Umbrella → 2 Submissions → 2 Drafts → 2 emails sent.
- **Resolution**: skill-level decision, not kernel mechanism. Draft writer skill coalesces by source_email_id.

### 5. Queue and integration health tooling
- First-class CLI needed: `indemn queue show/stats`, `indemn associate health`, `indemn integration health`, `indemn trace cascade`, `indemn metrics throughput`.
- **Later**: these CLI surfaces in Phase 0-1/2-3 specs.

### 6. Computed field mapping scope (method activation config vs Lookup)
- `stage → ball_holder` mapping is intrinsic behavior → belongs on method activation, not a Lookup.
- **Later formalized** as item 6 in documentation-sweep.md.

## Architectural Decisions

- **6 primitives validated** for B2B insurance pipeline. No primitive changes.
- **Watches as wiring survives the pressure test**: zero orchestration code.
- **Unified queue works for mixed human+associate roles**: rollout is a role assignment change, not infrastructure.
- **`--auto` pattern pays off**: cost scales with edge case complexity, not volume.
- **Temporal wraps each associate's execution** for durability.
- **Scheduled work = synthetic queue items targeting a role** (minor aesthetic vs. real events; acceptable).

## Layer/Location Specified

- **Entity CLI/API**: kernel auto-generated.
- **Integration resolution + adapter dispatch**: kernel (`kernel/integration/*`).
- **Adapter credentials**: AWS Secrets Manager (external), fetched via `secret_ref`.
- **Temporal workflows** per associate claim: in this artifact, still unspecified whether worker is kernel or harness. The retrace says "the workflow executes the command" without specifying the worker's deployment.
- **Method activation configs**: stored on entity definition (MongoDB `entity_definitions`).
- **Rules + Lookups**: MongoDB collections, per-org scoped.
- **Watch evaluation**: kernel, cached, sub-ms.
- **Message_queue + message_log**: MongoDB collections.
- **Changes collection + hash chain**: MongoDB, kernel-managed.
- **Auto-generated dashboards**: base UI (Phase 4).
- **Ephemeral entity locks**: became Attention entity later.
- **Email adapter dispatch**: `kernel/integration/adapters/outlook.py` (kernel).

**Finding 0 relevance**:
- GIC retrace does NOT directly resolve worker location. The phrase "the workflow executes the command" allows either in-kernel or harness interpretation.
- EventGuard retrace (same day) locks in the harness location via the mid-conversation event delivery requirement.
- Realtime-architecture-design (same day) finalizes harness = deployable image outside kernel.
- Implication: GIC's async-heavy pipeline would, per the final design, run in `indemn/runtime-async-deepagents:1.2.0` image. Currently runs in kernel Temporal worker → Finding 0.

## Dependencies Declared

- Microsoft Graph API (Outlook adapter)
- OCR + LLM providers (for PDF extraction)
- Anthropic (LLM for reasoning)
- Temporal Cloud
- MongoDB Atlas
- AWS Secrets Manager
- S3 (attachments + extraction)

## Code Locations Specified

- Entity set: `Email, Extraction, Submission, Assessment, Draft, Carrier, Agent`.
- Method activations: `auto-classify, auto-link, external-sync, pdf-extract, completeness-check, fuzzy-search, stale-check, computed-field`.
- Rules: classification hard rules + veto + reference patterns + required-field rules.
- Lookups: `usli-prefix-lob`, `carrier-name-variations`.
- Roles: `email_sync, extractor, classifier, linker, assessor, draft_writer, underwriter, operations, stale_checker`.
- Associates: one per role + one outbound sender.
- Implementation mapping (Pass 2):
  - `kernel/integration/adapters/outlook.py` — the Outlook adapter
  - `kernel/temporal/activities.py::process_with_associate` — runs the classifier/linker/assessor/draft-writer workflows (Finding 0 code site)
  - `kernel/rule/*`, `kernel/capability/*`, `kernel/watch/*` — provide the `--auto` pattern + watch evaluation + capability registry

## Cross-References

- 2026-04-09 architecture-ironing rounds 1, 2, 3 (encoded decisions)
- 2026-04-09 consolidated-architecture.md (pre-retrace state)
- 2026-04-09 unified-queue-temporal-execution.md (queue model)
- 2026-04-10-integration-as-primitive.md (primitive #6; adapter dispatch)
- 2026-04-10-eventguard-retrace.md (second retrace — real-time + inbound webhooks)
- 2026-04-10-crm-retrace.md (third retrace — actor-level Integrations)
- 2026-04-10-post-trace-synthesis.md (routing document for items)
- 2026-04-10-realtime-architecture-design.md (resolves ephemeral locks as Attention, scoped watches, Runtime, harness pattern)
- 2026-04-10-bulk-operations-pattern.md (resolves bulk as kernel pattern)
- 2026-04-11-base-ui-operational-surface.md (resolves dashboards)
- 2026-04-13-simplification-pass.md (REMOVES watch coalescing from kernel)
- 2026-04-13-documentation-sweep.md (resolves computed-field scope as item 6)

## Open Questions or Ambiguities

- **Worker location** — implicit in "workflow executes the command"; made explicit one day later in realtime-architecture-design. Retrace author did NOT surface this as an issue; they took "workflow runs the command" as valid at any deployment location.
- **Multi-LOB drafts** — domain skill concern; kernel supports; skill decides.
- **Queue health tooling** — data exists, CLI surface to be defined.

**Supersedence note**:
- Watch coalescing as kernel feature (Finding 1): REMOVED from kernel per simplification-pass (now UI-only).
- Ephemeral locks (Finding 3): RESOLVED/GENERALIZED as Attention entity (realtime-architecture).
- Computed field scope (Finding 6): RESOLVED as item 6 in documentation-sweep (on method activation config, not Lookup).
- All other findings survive.
- **GIC pipeline structure SURVIVES**. The retrace is the canonical B2B email-pipeline reference.
