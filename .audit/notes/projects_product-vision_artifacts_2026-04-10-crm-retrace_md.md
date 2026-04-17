# Notes: 2026-04-10-crm-retrace.md

**File:** projects/product-vision/artifacts/2026-04-10-crm-retrace.md
**Read:** 2026-04-16 (full file — 537 lines)
**Category:** design-retrace

## Key Claims

- **Third pressure test** (after GIC = B2B insurance and EventGuard = consumer real-time insurance). Purpose: validate kernel is domain-agnostic (no insurance concepts), validate actor-level integrations at scale (60 actor-level + 5-10 org-level for 15-person team), validate dog-fooding story.
- **Domain entities used**: Organization (customer), Contact, Deal, Meeting, MeetingIntelligence, ActionItem, Interaction, HealthSignal, Note. **Zero insurance-specific fields.**
- **Integration primitive validated at scale**: owner field (org vs. actor) is the only thing distinguishing org-shared and personal integrations. 60+ actor-level integrations work identically.
- **Credential resolution via owner_actor_id** — NEW addition surfaced here. Associate with `owner_actor_id` uses resolution chain:
  1. Associate's own personal Integration → use it.
  2. `owner_actor_id`'s personal Integration (with audit) → use it.
  3. Org-level Integration with role access → use it.
  4. Fail.
- **Privacy scoping for personal-integration-derived content**: metadata shared (from/to/subject/preview/timestamp), full content owner-scoped in S3 (`actor/{actor_id}/...`). Configurable per Integration (`full_shared` / `metadata_shared` / `owner_only`).
- **Read-heavy operations ("query capabilities")**: entity methods that aggregate across graph without mutations — e.g., `indemn organization compile-briefing`. Not a new primitive; a naming of a pattern.
- **Multi-source entity enrichment**: Contact informed by meetings (extractions), emails (personal Gmail sync), Slack (workspace bot + personal DMs), notes. Interaction's `source_integration_id` records provenance.
- **Cross-actor queue visibility for ops/leadership** = unscoped watches (default org-wide); **actor_context scoping** narrows to owner's entities.

## Architectural Decisions

- **Kernel is domain-agnostic**: validated across 3 shape dimensions — B2B insurance pipeline, consumer real-time insurance, generic B2B intelligence. "Every row is different. The kernel is the same. That's the story."
- **Owner-bound associate pattern**: `owner_actor_id` field on Actor (or specifically on Associate subtype). One-field kernel addition + resolver check + audit logging.
- **Consent and lifecycle for owner-bound associates**:
  - Consent required at creation (recorded in changes)
  - Revocable by owner via `indemn associate remove-owner`
  - Transferable with new owner's consent
  - On owner deprovisioning: paused; platform admin reviews
- **Privacy as Integration-level policy, not kernel rule**: Integration declares `content_visibility`. Kernel enforces via S3 path structure + IAM.
- **Entity methods can be read-only aggregations** (query capabilities). Doesn't need new primitive; just naming.
- **Scope: actor_context confirmed as cross-cutting need** (also surfaced in EventGuard).

## Layer/Location Specified

- **Actor schema**: add `owner_actor_id: Optional[ObjectId]` field. Kernel-level.
- **Credential resolver**: `kernel/integration/resolver.py` — extended to check `owner_actor_id`'s Integrations. Kernel-level.
- **Integration schema**: add `content_visibility` field. Kernel-level.
- **S3 path structure**: `s3://indemn-files/{org_id}/actor/{actor_id}/{entity_type}/{entity_id}/` for owner-scoped content vs. `s3://indemn-files/{org_id}/{entity_type}/{entity_id}/` for org-scoped.
- **S3 IAM policy**: infrastructure-level, not kernel code.
- **Org-level associates (Meeting Intelligence Processor, Health Monitor, Follow-up Checker, Weekly Summary Writer)** = async scheduled associates → **per design, run in the async-deepagents harness** (per 2026-04-10-realtime-architecture-design).
- **Personal sync associates (Craig's Gmail Sync, etc.)** = async scheduled associates with `owner_actor_id` → **also run in async-deepagents harness**.
- **CRM Assistant ("what's the story with INSURICA?")** = interactive chat → **chat-deepagents harness instance**.

**Finding 0 relevance**:
- ALL CRM associates (meeting processor, health monitor, follow-up checker, weekly summary, personal syncs, CRM Assistant) require harness infrastructure per design.
- Current implementation has NONE of the harnesses; everything runs as kernel Temporal activities (for async) or is missing (chat/voice).
- The CRM retrace would completely fail in the current code — Phase 6 (Dog-Fooding) is specifically Indemn CRM, and it's blocked on Finding 0.

## Dependencies Declared

- Granola (meeting transcription bot + webhooks)
- Gemini Meet (transcription)
- Slack (workspace bot + personal user tokens)
- Gmail / Google Calendar / Google Drive
- Linear
- Postgres (meetings DB / pipeline API)
- S3 (for content, with path-based ACL)
- AWS Secrets Manager (for each actor-level Integration secret)
- Temporal (for workflows)
- LLM provider (for extraction + synthesis)

## Code Locations Specified

- Conceptual (no absolute paths):
  - CRM entity set: `Organization, Contact, Deal, Meeting, MeetingIntelligence, ActionItem, Interaction, HealthSignal, Note`
  - Method activations on entities (`extract-intelligence`, `stale-check`, `health-score`, `compile-briefing`, `sync-from-source`)
  - Rules: health scoring thresholds, action item priority
  - Roles + watches: `team_member, account_owner, ops, executive, meeting_processor, health_monitor, personal_sync`
  - Associates: one per function (shared) + one per (actor × integration type) for personal syncs
  - Generic webhook: `POST /webhook/{provider}/{integration_id}` (already covered by integration-as-primitive + documentation-sweep)
- Implementation mapping:
  - Phase 6 spec (dog-fooding) implements this. Phase 6 not yet implemented per white paper status.

## Cross-References

- 2026-04-10-gic-retrace-full-kernel.md (first retrace)
- 2026-04-10-eventguard-retrace.md (second retrace — surfaced inbound webhook + actor-context watches + bulk ops)
- 2026-04-10-post-trace-synthesis.md (routing document for findings)
- 2026-04-10-integration-as-primitive.md (Integration primitive + owner model — extended here via owner_actor_id)
- 2026-04-10-realtime-architecture-design.md (adds Runtime; Associate gains `owner_actor_id`)
- 2026-04-11-authentication-design.md (formalizes default-assistant + owner-bound-service-token patterns)
- 2026-04-13-documentation-sweep.md (formalizes items 11 + 12 from this retrace)
- Phase 6-7 consolidated spec (implements this)

## Open Questions or Ambiguities

Deferred by the retrace:
- Exact privacy policy default per Integration type (resolved in documentation-sweep: actor-owned = metadata_shared, org-owned = full_shared).
- S3 IAM policy structure (infrastructure).
- Whether query capabilities need a special marker (resolved: just @exposed methods that are read-only).
- Whether "Associates with owner_actor_id" needs a new entity type (resolved in documentation-sweep: Associate is a subtype of Actor; owner_actor_id is a field on that subtype).

**Supersedence note for vision map**:
- **`owner_actor_id` pattern** — SURVIVES, formalized in documentation-sweep + authentication-design.
- **Content visibility policy** — SURVIVES, formalized in documentation-sweep.
- **Query capabilities pattern** — SURVIVES as a documentation note, not architectural change.
- **Multi-source entity enrichment** — SURVIVES as a pattern.
- **Kernel domain-agnosticism** — SURVIVES (validated).

**Finding 0 implication**: Phase 6 dog-fooding is blocked by Finding 0. Not just the kernel API endpoint assistant — every scheduled CRM associate would need to run in the async harness that doesn't exist.
