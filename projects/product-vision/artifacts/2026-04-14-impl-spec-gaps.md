---
ask: "Comprehensive gap identification across all implementation specs — what's missing, underspecified, or wrong relative to the white paper and design artifacts"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
sources:
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1.md"
    description: "Phase 0+1 base spec"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1-addendum.md"
    description: "Phase 0+1 addendum"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-2-3.md"
    description: "Phase 2+3 spec"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-4-5.md"
    description: "Phase 4+5 spec"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-6-7.md"
    description: "Phase 6+7 spec"
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Cross-referenced for completeness"
  - type: verification
    description: "Line-by-line cross-reference of specs against white paper sections, INDEX.md decisions, and all 65 design artifacts"
---

# Implementation Spec Gaps — Verification Pass 1

## Method

Read each spec against:
1. White paper sections (the design source of truth)
2. INDEX.md decisions (160+ locked decisions)
3. Key artifacts where implementation detail was specified (design layers, ironing rounds, capabilities model, temporal integration, authentication design, base UI design, realtime architecture, bulk operations, infrastructure, gap sessions)

Every gap is a mechanism, pattern, or decision that IS in the final design but is NOT in the implementation specs — or is present but underspecified to the point where an implementer would have to go back to the artifacts.

---

## Phase 0+1 Gaps (18)

### Entity Framework

**G-01: `build_event_metadata()` undefined**
Referenced in emit code (section 1.11) but never defined. Must produce:
```json
{
  "method": "classify",
  "state_transition": {"from": "received", "to": "triaging"},
  "fields_changed": ["status", "classification"]
}
```
Source: architecture-ironing-round-3 (event granularity: one save = one event, full change metadata)

**G-02: Dynamic entity relationships**
Beanie `Link["Carrier"]` requires compile-time type references. Dynamic models created via `create_model()` can't reference other dynamic models by name at creation time. The data architecture review flagged this: "Circular references between dynamic classes need two-pass resolution." No approach specified in the spec.
Source: data-architecture-review-findings (#8), data-architecture-solutions (#8)

**G-03: Flexible data validation mechanism**
`flexible_data_schema` field exists on EntityDefinition but the spec doesn't specify: how schemas are defined (JSON Schema? Pydantic model reference?), where they're stored (separate collection? on the Product entity?), how validation is triggered during entity save.
Source: white paper Section 2 (Entity — flexible data governed by a schema)

**G-04: `MessageLog` class not defined**
Referenced in message flow (complete_message moves from queue to log) but never defined as a Beanie Document with its own collection name, indexes, and settings.
Source: white paper Section 2 (Message — hot queue + cold log), architecture-ironing-round-1 (#2)

**G-05: Message-to-log transfer atomicity**
Phase 2's `complete_message` activity does insert to log + delete from queue. Must be in a MongoDB transaction to prevent: message in both collections (crash after insert, before delete) or message in neither (crash after delete, before insert).
Source: pressure-test-findings (#5 — visibility timeout and claiming)

**G-06: `older_than` operator implementation**
Referenced in OPERATORS dict but the actual datetime comparison logic isn't shown. Needs to: parse duration strings ("7d", "30m", "24h"), compare entity field (datetime) against now - duration.
Source: entity-capabilities-and-skill-model (stale-check example: "last_activity_at older_than 7d")

**G-07: `evaluate_rules()` function not defined**
`auto_classify` calls `evaluate_rules()` but this function is never implemented. Must: load active rules for org+entity_type+capability, evaluate each rule's conditions against entity data, handle priority ordering, detect veto rules, resolve lookup references in rule actions, return match/no-match/veto result with full context.
Source: capabilities-model-review-findings (rule composition, veto detection, evaluation traces)

**G-08: Veto rule detection logic**
`auto_classify` checks `result["vetoed"]` but the rule engine doesn't show how veto rules (action=force_reasoning) are distinguished from positive rules (action=set_fields) or how a veto overrides a positive match.
Source: white paper Section 2 (Rules have exactly two actions: set_fields and force_reasoning)

**G-09: Watch cache implementation**
`watch/cache.py` in repo structure but never defined. Needs: data structure (dict keyed by org_id+entity_type), loading from Role entities, 60-second TTL, immediate invalidation when any Role in the org is saved (kernel entity cache invalidation), multi-instance consideration (for MVP single instance is fine, but the invalidation mechanism should be documented).
Source: consolidated-architecture (cached evaluation of routing rules, 60s TTL), architecture-ironing-round-3 (#5 — bootstrap circularity, cache invalidation on bootstrap entity save)

**G-10: `Skill` entity class not defined**
Referenced throughout (skill loading, content hashing, versioning, approval workflow) but never defined as a Beanie Document with fields: name, content, content_hash, version, status (active/pending_review/deprecated), type (entity/associate), entity_type (for entity skills), created_by, created_at, updated_at, org_id.
Source: data-architecture-everything-is-data (skills as data in MongoDB), white paper Section 2 (Skills)

**G-11: @exposed methods not registered as API routes**
`kernel/api/registration.py` shows CRUD routes (list, get, create, update, transition) but doesn't show how kernel entity @exposed methods (e.g., `Organization.clone()`, `Integration.rotate_credentials()`) become additional API endpoints. The @exposed decorator is defined in the addendum but the API registration for these methods is missing.
Source: design-layer-1-entity-framework (auto-registration of @exposed methods), white paper Section 2 (Entity — operations auto-generated)

**G-12: Capability activation CLI commands**
`indemn entity enable Email auto-classify --evaluates classification-rule` is referenced throughout but the CLI command definition and the API endpoint backing it are not specified. Also: `indemn entity add-method` (from the GIC retrace), `indemn entity disable`.
Source: entity-capabilities-and-skill-model, gic-retrace-full-kernel

**G-13: Entity management CLI completeness**
Several critical CLI commands are referenced but not fully specified as implementations:
- `indemn entity modify` (add/remove/deprecate fields)
- `indemn entity enable` / `indemn entity disable` (capability activation)
- `indemn entity migrate` (rename, type-change — in addendum but as a function, not as CLI command → API endpoint → function chain)
- `indemn entity cleanup` (remove deprecated fields)
Source: data-architecture-everything-is-data, data-architecture-solutions (#12)

**G-14: Org management commands**
White paper specifies but spec doesn't cover:
- `indemn org clone gic --as gic-staging` — clone all configuration (definitions, skills, rules, roles, associates, integrations) without entity instances
- `indemn org diff gic-staging gic` — show configuration differences
- `indemn deploy --from-org gic-staging --to-org gic` — promote configuration with validation and rollback
- `indemn org export gic > config.yaml` / `indemn org import --from-file config.yaml`
Source: white paper Section 2 (Everything Is Data — environments are organizations), data-architecture-everything-is-data

**G-15: Platform upgrade mechanism**
White paper says: "Kernel capability upgrades declare configuration schema versions. Entity definitions store which version they use. Upgrades include migration scripts." None of this is specified:
- How capabilities declare their config schema version
- How entity definitions track which capability version they use
- `indemn platform upgrade --dry-run` command
- Migration script format and execution
Source: white paper Section 8 (Platform Upgrades), data-architecture-review-findings (#10)

**G-16: Health endpoint implementation**
`health.py` in repo structure but not defined. Must check: MongoDB connectivity, Temporal Cloud connectivity, AWS Secrets Manager connectivity. Return: healthy/degraded/unhealthy with per-dependency status.
Source: white paper Section 7 (Production Requirements), white paper Section 10 (What Needs to Be Built)

**G-17: `_previous_state` capture on entity load**
`save_tracked()` references `self._previous_state` for computing field-level changes (old vs new values). This must be captured when the entity is loaded from MongoDB. Mechanism not specified — could be Beanie's document state tracking (`use_state_management = True`) or a manual snapshot on load.
Source: implied by the changes collection design (field-level before/after values)

**G-18: Watch creation validation — entity-local constraint**
Watches can only reference fields on the changed entity (no cross-entity lookups during evaluation). This constraint should be validated when a watch is created or modified via CLI. If someone tries to add a watch condition referencing `submission.carrier.name`, it should be rejected.
Source: white paper Section 2 (Watches — watch conditions are entity-local), pressure-test-findings (#3)

---

## Phase 2+3 Gaps (13)

### Phase 2 — Associate Execution

**G-19: Temporal TracingInterceptor setup**
OTEL integration is a core principle. The temporal-integration-architecture artifact says: "TracingInterceptor auto-creates OTEL spans for every workflow + activity execution." The worker setup must include:
```python
from temporalio.contrib.opentelemetry import TracingInterceptor
worker = Worker(
    client, task_queue="indemn-kernel",
    interceptors=[TracingInterceptor()],
    ...
)
```
Source: temporal-integration-architecture (OTEL section)

**G-20: Human-in-the-loop via Temporal Signals**
The ProcessMessageWorkflow is linear (claim→process→complete). Missing: a HumanReviewWorkflow variant where the workflow waits indefinitely for a human signal. The temporal-integration-architecture artifact shows:
- Workflow starts from watch match (e.g., Assessment:created WHERE needs_review=true)
- Workflow WAITS for signal (indefinitely)
- Human sees it in queue (UI queries Temporal for pending workflows by role)
- Human clicks Approve/Reject → UI signals the Temporal workflow
- Workflow resumes → executes remaining activities
- Timer: if no action in N hours → escalation
Source: temporal-integration-architecture (Human-in-the-Loop section), unified-queue-temporal-execution

**G-21: `process_with_associate` activity implementation**
The most important activity is a stub. Must specify:
- How deterministic skills are parsed into executable steps (the interpreter question — still open from the design)
- How CLI commands are executed (via HTTP to the API, not subprocess from inside the Temporal worker)
- How the LLM is invoked (system prompt with skill + entity context, tool calls for CLI commands, iterative until completion)
- How multi-entity operations work within one actor turn (all saves in same correlation context, depth propagation)
- How the --auto result (needs_reasoning) feeds back to the LLM within the same turn
Source: actor-spectrum-and-primitives, entity-capabilities-and-skill-model, primitives-resolved

**G-22: Context propagation through associate execution**
When an associate processes a message and its CLI commands cause entity saves, the correlation_id and depth must propagate. The chain is: Temporal activity → HTTP API call → save_tracked(). The API call must carry correlation_id and parent_depth as parameters (headers or body) so that save_tracked() can propagate them through nested watch evaluations.
Source: architecture-ironing-round-3 (#1 — event granularity), core-primitives-architecture (cascade depth tracking)

**G-23: Temporal Worker production configuration**
Missing: max_concurrent_activities (prevent overloading MongoDB), graceful_shutdown_timeout, task_queue naming convention, multiple worker instances consideration, rate limiting for LLM calls.
Source: data-architecture-review-findings (#13 — thundering herd after Temporal recovery), infrastructure-and-deployment

**G-24: BulkExecuteWorkflow completeness**
The spec shows a basic loop. Missing from bulk-operations-pattern artifact:
- Per-entity error classification (permanent: StateMachineError, ValidationError, PermissionDenied, EntityNotFound; transient: VersionConflict first attempt, network, lock timeout)
- Dry-run mode (preview without committing)
- Progress reporting via Temporal workflow queries
- `--failure-mode=abort` option (workflow stops at first error)
- Workflow terminal states: completed, completed_with_errors, failed
- CLI commands: `indemn bulk status <workflow_id>`, `indemn bulk list`, `indemn bulk cancel`, `indemn bulk retry`
Source: bulk-operations-pattern (complete specification)

**G-25: Deterministic skill execution approach**
The white paper says "skills are markdown, always." But `execute_deterministic()` must parse markdown into executable steps. The design explored three options (YAML, Python, formalized markdown) but never locked a format. The spec must either specify the parsing approach or flag this as a decision to make during implementation.
Source: pressure-test-findings (#7 — deterministic skill format specification)

### Phase 3 — Integration Framework

**G-26: OAuth token refresh**
Outlook, Gmail, and other OAuth-based adapters need transparent token refresh. Must: detect 401 response, read refresh token from Secrets Manager, call provider's token endpoint, write new access+refresh tokens to Secrets Manager, retry the original request. Without this, Outlook integration breaks within 1 hour.
Source: integration-as-primitive (credential resolution, rotation)

**G-27: Adapter error hierarchy**
Standardized exception classes that the kernel handles uniformly:
```python
class AdapterError(Exception): pass
class AdapterAuthError(AdapterError): pass      # → refresh credentials, retry
class AdapterRateLimitError(AdapterError): pass  # → exponential backoff, retry
class AdapterTimeoutError(AdapterError): pass    # → retry with longer timeout
class AdapterNotFoundError(AdapterError): pass   # → fail, surface to operator
class AdapterValidationError(AdapterError): pass # → fail, don't retry
```
Source: impl-spec-phase-2-3 section 3.9 (identified as open question but never resolved)

**G-28: Credential cache invalidation on rotation**
If `indemn integration rotate-credentials INT-001` runs while a Temporal worker has cached the old credentials, the worker's operations will fail. Need either: cache keyed by credential version, Change Stream on Integration entity invalidates cache, or credential TTL short enough that rotation is self-healing.
Source: white paper Section 10 (credential caching with TTL)

**G-29: Integration health monitoring**
Which process runs periodic health checks, how often, what constitutes a "test" per adapter (email: attempt fetch, payment: validate API key, voice: check room server). Updates `last_checked_at` and `last_error` on Integration entity.
Source: white paper Section 8 (Monitoring), base-ui-operational-surface (Integration health widget)

**G-30: Adapter versioning migration**
`indemn integration upgrade INT-001 --to outlook_v3 --dry-run` — the flow for upgrading an Integration to a new adapter version. Must validate new adapter compatibility, preview changes, apply, audit.
Source: integration-as-primitive (adapter versioning via provider_version field)

**G-31: Stripe adapter async correctness**
The spec shows synchronous `stripe.PaymentIntent.create()` inside an `async def`. Must either use the async Stripe client (`stripe.PaymentIntent.create_async()`) or run in an executor (`await asyncio.to_thread(stripe.PaymentIntent.create, ...)`).
Source: technical correctness

---

## Phase 4+5 Gaps (20)

### Phase 4 — Base UI

**G-32: Field type → form control mapping**
The rendering contract that makes auto-generation concrete:

| Field Type | Form Control | Display Control |
|---|---|---|
| str | text input | text |
| int, float, decimal | number input | formatted number |
| bool | checkbox | yes/no badge |
| date | date picker | formatted date |
| datetime | datetime picker | formatted timestamp |
| enum (Literal) | select dropdown | badge |
| objectid (relationship) | entity picker (search + select) | linked name |
| list | multi-value input | comma-separated or chips |
| dict | JSON editor (code mirror) | collapsible JSON |
| text (long string) | textarea | truncated with expand |

Source: base-ui-operational-surface (rendering contract), white paper Section 5 (Forms Are Auto-Generated)

**G-33: Entity metadata endpoint — full contract**
GET /api/_meta/entities must return enough for complete UI generation:
```json
{
  "name": "Submission",
  "collection": "submissions",
  "fields": [
    {"name": "named_insured", "type": "str", "required": true, "label": "Named Insured"},
    {"name": "stage", "type": "str", "enum_values": ["received", "triaging", ...], "is_state_field": true}
  ],
  "state_machine": {"received": ["triaging"], ...},
  "current_state_transitions": {"triaging": ["processing", "awaiting_agent_info"]},
  "capabilities": [{"name": "auto_classify", "cli": "indemn submission classify --auto"}],
  "relationships": [{"field": "carrier_id", "target": "Carrier", "label": "Carrier"}],
  "permissions": {"read": true, "write": true, "transition": true}
}
```
Source: base-ui-operational-surface (rendering contract maps primitives to UI elements)

**G-34: WebSocket subscription management**
The base-ui-operational-surface artifact specifies: "Views subscribe to entity changes in real time, filtered by the current query and pagination." Must rebuild subscription when user changes filters, pages, or views. The spec shows a basic Change Stream but not filter-aware subscriptions.
Source: base-ui-operational-surface (real-time by default)

**G-35: SSO provider discovery at login**
Login page must discover which identity_provider Integrations exist for the org. Pre-auth endpoint (no token required):
```
GET /auth/providers?org=gic
→ [{name: "Okta", integration_id: "INT-001", type: "oidc"}]
```
Source: authentication-design (SSO section)

**G-36: MFA challenge flow**
After password success, if role requires MFA:
1. Issue a temporary partial-auth token (can only be used for MFA challenge)
2. Return `{requires_mfa: true, mfa_type: "totp", partial_token: "..."}`
3. Client presents TOTP input
4. Client submits TOTP + partial_token → `POST /auth/mfa/verify`
5. Server validates TOTP, upgrades to full session, issues access token
Source: authentication-design (MFA policy section, forcing function #1)

**G-37: Platform admin session flow**
Full flow:
1. Platform admin authenticated in _platform org
2. `POST /api/platform/sessions` with `{target_org_id, work_type, duration_hours}`
3. Kernel creates temporary Session in target org with platform_admin_context
4. Returns access token scoped to target org
5. Session auto-expires at duration limit (4h default, 24h max)
6. Every action audited in target org's changes collection with platform admin identity
Source: authentication-design (Platform Admin Cross-Org section)

**G-38: Recovery flows**
Three recovery scenarios from the auth design:
- Password reset: `POST /auth/reset-password` → sends magic link via email Integration → clicking link verifies token → set new password → all existing sessions revoked
- MFA backup codes: pre-generated at MFA enrollment, stored hashed in Secrets Manager. On challenge screen, "Use backup code" → validates → prompts for MFA re-enrollment
- Emergency access: platform admin creates incident session with full audit
Source: authentication-design (Recovery Flows section)

**G-39: Claims refresh mechanism**
When role is revoked: kernel sets `claims_stale=true` on all active Sessions for that actor. On next API request: auth middleware detects stale claims → auto-refreshes access token with updated role set → returns new token in response header → client uses new token. User sees permission change on next interaction without re-login.
Source: authentication-design (Role Changes and Session Handling), white paper Section 4

**G-40: Pre-auth rate limiting**
```python
# In auth middleware:
# Count failed attempts by (ip_address, email_hash)
# Use a MongoDB collection for cross-instance coordination
# Default threshold: 5 failures in 10 minutes → 30-minute lockout
# Per-org configurable
# Audit: auth.brute_force_lockout event in changes collection
```
Source: authentication-design (pre-auth rate limiting section)

**G-41: Auth audit event types**
The changes collection must record specific auth event types:
`auth.login_attempt`, `auth.login_success`, `auth.login_failure`, `auth.session_created`, `auth.session_refreshed`, `auth.session_revoked`, `auth.mfa_enrolled`, `auth.mfa_challenged`, `auth.mfa_verified`, `auth.mfa_reset`, `auth.password_changed`, `auth.method_added`, `auth.method_removed`, `auth.role_granted`, `auth.role_revoked`, `auth.lifecycle_transitioned`, `auth.platform_admin_access`, `auth.brute_force_lockout`
Source: authentication-design (auth events in changes collection)

**G-42: Revocation cache bootstrap on startup**
On API instance startup: query Sessions revoked in last 15 minutes (= max access token lifetime), populate in-memory revocation cache. This prevents a newly-started instance from accepting revoked tokens until the Change Stream catches up.
Source: authentication-design (revocation cache lifecycle)

### Phase 5 — Real-Time

**G-43: Heartbeat bypass detection**
In `save_tracked()`, detect heartbeat-only updates:
```python
if set(changed_fields) <= {"last_heartbeat", "expires_at"} and isinstance(self, Attention):
    # Direct MongoDB update, skip changes collection and watch evaluation
    await self.get_motor_collection().update_one(
        {"_id": self.id},
        {"$set": {"last_heartbeat": now, "expires_at": new_expiry}}
    )
    return
```
Source: realtime-architecture-design (heartbeat semantics)

**G-44: Attention TTL cleanup process**
A background sweep (in the queue processor or a separate loop):
- Query Attention records where `expires_at < now` and `status = "active"`
- Transition each to `status = "expired"`
- Emit Attention:expired event (watches can react — e.g., notify ops of abandoned sessions)
- Frequency: every 30 seconds
Source: realtime-architecture-design (heartbeat semantics, zombie detection)

**G-45: Zombie detection and recovery**
When an Attention expires (Runtime instance crashed):
- If purpose is `real_time_session`: the linked Interaction should be transitioned to an error or abandoned state
- If the Interaction had an active consumer connection: the connection is already dead (Runtime crashed). Consumer must reconnect, which creates a new session.
- Ops watch can catch `Attention:expired WHERE purpose=real_time_session` and alert
Source: realtime-architecture-design (zombie claim detection)

**G-46: Runtime deployment orchestration**
`indemn runtime transition RUNTIME-001 --to deploying` needs to trigger actual container deployment. Options:
- Railway API call (Railway has a deployment API)
- Manual process (operator deploys the Docker image, then runs the transition command)
- For MVP: manual process with CLI commands to verify deployment health before transitioning to active
Source: infrastructure-and-deployment, realtime-architecture-design

**G-47: Events stream Change Stream pipeline**
The actual MongoDB pipeline for filtering events:
```python
pipeline = [
    {"$match": {
        "fullDocument.org_id": org_id,
        "$or": [
            {"fullDocument.target_actor_id": actor_id},
            {"fullDocument.target_actor_id": None, "fullDocument.target_role": {"$in": actor_roles}},
        ],
    }},
]
if interaction_id:
    # Also match events about entities related to this Interaction
    pipeline[0]["$match"]["$or"].append(
        {"fullDocument.entity_id": interaction_related_entity_ids}
    )
```
Source: realtime-architecture-design (indemn events stream specification)

**G-48: Scoped watch → Runtime notification path**
When active_context resolution finds an Attention with runtime_id, how does the event reach the running harness? The mechanism: the event is written to message_queue as normal (with target_actor_id set). The harness's `events stream` subprocess is watching message_queue via Change Stream filtered by that actor_id. The event appears in the stream, the harness receives it, feeds it to the agent. No separate notification mechanism needed — the events stream IS the notification path.
Source: realtime-architecture-design (Part 2: Scoped Watches, Part 3: Runtime)

**G-49: Handoff state consistency**
When `indemn interaction transfer INT-001 --to-actor cam@indemn.ai`:
1. Old actor's Attention is closed (transition to "closed")
2. Interaction.handling_actor_id updated to new actor
3. Existing messages in queue targeting old actor for this interaction: they stay in the queue with the old target_actor_id. If the old actor hasn't claimed them, they become visible to the new actor only after the old claims expire (visibility timeout). For immediate transfer: the transfer command should re-target pending messages.
4. Runtime detects Interaction change via Change Stream on the Interaction document
5. Runtime switches mode based on new handling actor type (if associate → run in process; if human → bridge via queue)
Source: realtime-architecture-design (handoff section), white paper Section 2 (Handoff)

**G-50: Three-layer config merge order**
For customer-facing sessions, configuration merges across three layers:
```
Runtime defaults → Associate override → Deployment override
```
Example: Runtime has default LLM model. Associate overrides with specific model. Deployment overrides with venue-specific greeting. Implementation: deep merge at session start in the harness, with later layers winning over earlier.
Source: white paper Section 2 (Three-layer customer-facing flexibility), realtime-architecture-design

**G-51: Human voice client Integration**
When a human takes over a live voice call:
1. Human's UI connects to a voice client (browser WebRTC or phone bridge)
2. The voice client connection is an Integration (system_type=voice_client, owner_type=actor, owner_id=human)
3. Runtime bridges the human's audio stream into the existing call room
4. The associate can observe (Attention purpose=observing) or disconnect
5. Transfer back: `indemn interaction transfer --to-role quote_assistant`
Source: realtime-architecture-design (human voice clients as Integrations), white paper Section 2

---

## Phase 6+7 Gaps (4)

**G-52: Org export/import format**
What gets exported: entity definitions, skills, rules, lookups, role configurations, associate configurations, capability activations, integration configurations (without secrets). What doesn't: entity instances, messages, changes, sessions, attentions. Format: YAML or JSON, one file or directory of files.
Source: data-architecture-everything-is-data (org export/import)

**G-53: Parallel run mechanism**
For GIC migration: how same emails go to both old system and new OS. Options:
- Email forwarding rule in Outlook (BCC to a second inbox)
- The new OS polls the same Outlook inbox (read-only, doesn't mark as read)
- Manual: export batch of emails, feed into both systems
Source: white paper Section 9 (Transition — run both systems in parallel with same inputs)

**G-54: Accuracy comparison tooling**
Compare old system classification/linking/assessment against new OS output. Needs:
- Export old system decisions for a set of emails
- Run same emails through new OS
- Generate comparison report (match/mismatch per email, per classification, per link)
- Surface mismatches for investigation
Source: white paper Section 9 (compare outputs, cut over when confident)

**G-55: Domain modeling as CLI sequence**
The 8-step process should be a concrete checklist with specific CLI commands, not just narrative. For each step: what CLI command, what input, what output, what to verify before proceeding.
Source: white paper Section 3 (Domain Modeling), remaining-gap-sessions (Domain Modeling Process)

---

## Summary

| Phase | Gap Count | Most Critical |
|---|---|---|
| Phase 0+1 | 18 | G-02 (dynamic relationships), G-07 (evaluate_rules), G-09 (watch cache), G-14 (org management) |
| Phase 2+3 | 13 | G-20 (HITL signals), G-21 (process_with_associate), G-26 (OAuth refresh), G-24 (bulk operations) |
| Phase 4+5 | 20 | G-36 (MFA flow), G-37 (platform admin), G-48 (scoped→runtime), G-49 (handoff consistency) |
| Phase 6+7 | 4 | G-55 (domain modeling as CLI) |
| **Total** | **55** | |

---

## Pass 2 Findings: INDEX.md Decisions Cross-Reference

Went through all 160+ decisions in the INDEX.md. Seven additional gaps found that Pass 1 missed:

**G-56: Compliance mode flag on associates**
Decision (2026-04-10): "If compliance requires guaranteed LLM-free execution, a mode flag raises on needs_reasoning instead of falling back." The Actor entity has a `mode` field (deterministic/reasoning/hybrid) but no `strict_deterministic` flag that would RAISE an error when a capability returns needs_reasoning, instead of falling back to LLM. This is a specific compliance scenario.
Source: INDEX.md decision "Deterministic associates collapsed into hybrid"

**G-57: Bootstrap entity cascade guard**
Decision (architecture-ironing-round-3, #5): "The kernel detects when a watch evaluation would trigger a change to the same bootstrap entity type being evaluated. Self-referencing cascades on bootstrap entities are blocked at depth 1." This is NOT the same as the generic cascade depth circuit breaker (G-08 area). This is a specific guard for kernel entities: if modifying a Role triggers a watch that tries to modify a Role, it's blocked immediately.
Source: architecture-ironing-round-3 (bootstrap circularity)

**G-58: Tier 3 self-service signup flow**
Decision (2026-04-11): "Tier 3 self-service signup MVP scope: org + first admin + password + email verification + first API key. NOT in MVP: billing, plans, email domain verification, sub-user invitation, OAuth app management." The endpoint flow (website form → create org + actor + password method + verification email → verify → issue API key) is not in any spec.
Source: authentication-design, white paper Section 4

**G-59: Default assistant auth inheritance**
Decision (2026-04-11): "The default associate (owner_actor_id = user) authenticates via the user's session JWT, not a separate service token. Audit attributed as 'user X via default associate performed Y.'" The Phase 4 spec mentions the assistant but doesn't specify this auth pattern — it's distinct from owner-bound scheduled associates which use their own service tokens.
Source: authentication-design (default assistant section)

**G-60: Lookup bulk import from CSV**
Decision (2026-04-10): "Lookups are mapping tables. Bulk-importable from CSV, maintained by non-technical users." The CLI command `indemn lookup import --from-csv data.csv` is not in the specs.
Source: white paper Section 2 (Capabilities — Lookups), capabilities-model-review-findings (#3)

**G-61: bulk_operation_id = temporal_workflow_id**
Decision (2026-04-10 session 6): "Coupling accepted for simplicity. The operation spec beyond Temporal retention is not persisted." This deliberate coupling should be documented in the spec — it's a specific simplification with known trade-offs.
Source: INDEX.md bulk operations decisions

**G-62: Explicit deferred features list**
Multiple decisions establish what's NOT in MVP: active alerting, WebAuthn/passkeys, per-operation MFA re-verification (`requires_fresh_mfa`), DashboardConfig/AlertConfig/Widget entities, Tier 3 billing/plans/sub-users/OAuth app management, saga-style cross-batch rollback, `bulk_apply` DSL for multi-entity rows, visual rule builder, rule chaining. Each phase spec should have a "Not in this phase" section listing what's explicitly deferred.
Source: simplification-pass, authentication-design, bulk-operations-pattern, capabilities-model-review-findings

---

## Updated Summary

| Phase | Pass 1 | Pass 2 | Total |
|---|---|---|---|
| Phase 0+1 | 18 | 4 (G-56, G-57 apply here) | 20 |
| Phase 2+3 | 13 | 2 (G-60, G-61 apply here) | 15 |
| Phase 4+5 | 20 | 3 (G-58, G-59 apply here) | 22 |
| Phase 6+7 | 4 | 0 | 4 |
| Cross-cutting | 0 | 1 (G-62 applies to all) | 1 |
| **Total** | **55** | **7** | **62** |

## Verification Status

- [x] Pass 1: Line-by-line against white paper sections
- [x] Pass 2: Cross-reference against INDEX.md decisions list (160+ decisions)
- [x] Pass 3: Internal consistency check

## Pass 3 Findings: Internal Consistency

Cross-phase references, contradictions, and implicit dependencies that should be explicit:

**G-63: Queue processor scope by phase**
Phase 1 defines `queue_processor.py` as a minimal sweep process. Phase 2 adds Temporal dispatch to it. The spec should clarify: Phase 1 queue processor handles ONLY visibility timeout recovery and escalation deadline checks. Phase 2 ADDS Temporal workflow dispatch for associate-eligible messages. This is additive, not a replacement.

**G-64: Temporal activity auth context**
Phase 2 activities run in the Temporal worker (inside trust boundary, direct MongoDB access). But `save_tracked()` requires `actor_id` and `org_id`. The activity receives `associate_id` as a parameter, but how does it establish the auth/scoping context? It needs to: load the associate's org_id, set it as the active context for OrgScopedCollection, and pass actor_id to save_tracked(). This context-setting mechanism for Temporal activities is not specified.

**G-65: Harness CLI authentication**
Phase 5 harness uses CLI subprocess (`indemn` commands). CLI operates in API mode (HTTP to API server). The harness runs on Railway internal network. But: how does the CLI authenticate? It needs a service token for the associate. The token must be either: injected as an environment variable (`INDEMN_CLI_TOKEN`), passed via CLI flag (`--token`), or read from a config file. The provisioning of this token (created when the associate is created, stored where?) is not specified.

**G-66: Queue processor dispatch uses role name vs role_id**
Phase 2's dispatch code searches for associates by role: `Actor.find({"role_ids": role.id})`. But the message has `target_role` as a string (role name), not an ObjectId. The dispatch must: look up the Role by name + org_id to get the role_id, then search Actors by role_id. This lookup chain is implicit.

**G-67: Phase 1 queue processor vs Phase 2 queue processor**  
The base Phase 0+1 spec includes queue_processor.py with a basic sweep loop. Phase 2 adds Temporal dispatch to the same file. This means Phase 1's queue processor needs to be designed so that Phase 2's additions are clean extensions, not rewrites. The interface should be: the queue processor has a list of "sweep functions" that run each cycle. Phase 1 registers: check_visibility_timeouts, check_escalation_deadlines. Phase 2 adds: dispatch_associate_workflows.

---

- [x] Pass 4: Implementability check

## Pass 4 Findings: Implementability

Testing: "Could I sit down and build Phase 1 from this spec without going back to the artifacts?"

**G-68: Beanie + OrgScopedCollection integration pattern**
The spec defines OrgScopedCollection as a wrapper around raw Motor collections. But Beanie's normal query path (`Entity.find({...})`, `Entity.get(id)`) goes directly to MongoDB without the wrapper. The spec needs to resolve: do we override Beanie's find/find_one/get class methods on BaseEntity to always inject org_id? Do we use OrgScopedCollection only for raw queries and trust Beanie's own methods with a custom query filter? Do we abandon Beanie's query methods entirely and use OrgScopedCollection for everything? This is a fundamental architecture question that determines how every query in the system works.

Options:
- **Option A**: Override BaseEntity class methods to inject org_id from a context variable (set by auth middleware). Beanie queries work normally but always include org_id.
- **Option B**: Use OrgScopedCollection for all queries, bypass Beanie's query methods. More explicit but loses Beanie's convenience.
- **Option C**: Use Beanie with custom Document class that overrides `find` and `find_one` to always include org_id from async context.

Recommendation: Option A or C — override at the BaseEntity level using Python's contextvars to store the current org_id (set by auth middleware per request).

**G-69: API query parameters (filtering, pagination, sorting)**
The auto-generated list endpoints show basic `GET /api/{entity}s` with limit/offset. But real queries need: field-based filtering (status=active, carrier_id=CARR-001), pagination (offset/limit or cursor-based), sorting (by field, ascending/descending), field selection (partial responses for efficiency). The spec doesn't specify: what filter syntax is accepted in query parameters? How are relationship filters handled? How does pagination work for the base UI's entity list views?

**G-70: CLI startup and entity discovery**
The CLI operates in API mode (HTTP client). On each invocation it needs to know what entity types exist. The spec says "fetch entity metadata from API" but doesn't specify: is this cached? What's the endpoint? What if the API is down? How fast is it? If the CLI fetches metadata on every invocation, that adds network latency to every command.

Recommendation: `GET /api/_meta/entities` returns the entity registry. CLI caches it locally with a short TTL (30 seconds). `--no-cache` flag for fresh fetch.

**G-71: Auth context propagation to entity layer**
The auth middleware sets `request.state.org_id` and `request.state.actor` on each FastAPI request. But the entity layer (BaseEntity, OrgScopedCollection, save_tracked()) needs access to this context without it being passed as a parameter through every function call. The spec needs to specify: use Python `contextvars` to store current org_id and actor_id, set in auth middleware, read in entity operations. This is the mechanism that makes OrgScopedCollection work automatically.

```python
# kernel/scoping/context.py
from contextvars import ContextVar

current_org_id: ContextVar[str] = ContextVar("current_org_id")
current_actor_id: ContextVar[str] = ContextVar("current_actor_id")
current_correlation_id: ContextVar[str] = ContextVar("current_correlation_id", default=None)

# Set in auth middleware:
current_org_id.set(str(actor.org_id))
current_actor_id.set(str(actor.id))

# Read in entity operations:
org_id = current_org_id.get()
```

---

## Final Summary

| Phase | Gaps |
|---|---|
| Phase 0+1 | 22 (G-01 through G-18, plus G-56, G-57, G-68, G-71) |
| Phase 2+3 | 16 (G-19 through G-31, plus G-60, G-61, G-64) |
| Phase 4+5 | 23 (G-32 through G-51, plus G-58, G-59, G-65) |
| Phase 6+7 | 4 (G-52 through G-55) |
| Cross-cutting | 5 (G-62, G-63, G-66, G-67, G-69, G-70) |
| **Total** | **71** |

## Verification Status

- [x] Pass 1: Line-by-line against white paper sections (55 gaps)
- [x] Pass 2: Cross-reference against INDEX.md decisions (7 additional)
- [x] Pass 3: Internal consistency check (5 additional)
- [x] Pass 4: Implementability check (4 additional)
- **Total: 71 gaps identified across 4 verification passes**

---

## Pass 5 Findings: Artifact-Specific Mechanisms

Traced through the key design artifacts that contain implementation detail the white paper abstracted away. Checking whether those specific patterns made it into the specs.

**G-72: Flexible data cross-entity schema resolution**
The design-layer-1 artifact showed `data: FlexibleData = FlexibleData(schema_from="product.form_schema")`. This means: when saving an entity with flexible data, the kernel must resolve the schema reference (load the related Product, read its form_schema), validate the `data` dict against that schema. For different products, the same entity type validates differently. This is cross-entity schema resolution at save time — more complex than G-03 captured. Needs: schema storage format, resolution mechanism, validation approach (JSON Schema? Pydantic dynamic model?), error reporting on validation failure.
Source: design-layer-1-entity-framework (FlexibleData field)

**G-73: Multi-entity operations as exposed commands**
The design-layer-1 artifact had `class BindingService` with exposed methods orchestrating across Submission, Quote, and Policy. The white paper evolved this to kernel capabilities. But the question remains: how does a multi-entity operation (create Policy + update Quote + transition Submission) get registered as a single CLI/API command? Capabilities are per-entity-type. A "bind" operation spans three entity types. Is this a kernel capability on Policy that internally modifies the other entities? Is it a separate "service" concept? The spec doesn't address multi-entity orchestration as a registered command.
Source: design-layer-1-entity-framework (cross-entity operations), white paper Section 2 (implied but not explicit)

**G-74: Context enrichment depth resolution**
Messages carry entity context at a configurable depth (watch has `context_depth` parameter). But the resolution mechanism — follow entity relationships to depth N, load the related entity data, attach it to the message — is not specified. At depth 1: just the changed entity. At depth 2: the entity + directly related entities (resolved via relationship fields). How are relationships followed? Which fields are relationship references? How much data per related entity is included?
Source: core-primitives-architecture (context management), architecture-ironing (#6 — context depth)

**G-75: MessageBus abstraction interface**
One of the 10 hardening requirements (2026-04-07): "MessageBus abstraction — interface for swappable backend." The spec writes directly to MongoDB collections. No abstraction layer exists. The requirement was that message publish/consume should go through an interface so the backend (MongoDB now, RabbitMQ later) can be swapped without changing application code.
Source: core-primitives-architecture (hardening requirement #8), session-3-checkpoint

**G-76: Temporal Schedules vs application-level cron**
The temporal-integration-architecture artifact specified Temporal Schedules for recurring tasks: `indemn schedule create --name email-sync --workflow EmailSyncWorkflow --cron "*/1 * * * *"`. The spec instead shows the queue processor checking cron expressions in application code. These are different: Temporal Schedules are managed by Temporal Cloud (durable, visible in Temporal UI, pausable), application cron is custom code in the queue processor. Decision needed: which approach?
Source: temporal-integration-architecture (Scheduled Tasks section)

**G-77: Temporal workflow versioning**
For deploying new associate logic: the temporal-integration-architecture artifact says "new workers with new code, in-flight workflows continue with old version, new workflows use new version." The Temporal Python SDK supports this via `workflow.patched()` or Build ID-based versioning. Not mentioned in the spec.
Source: temporal-integration-architecture (Workflow Versioning section)

**G-78: Message claim sort order**
The claim query must sort by priority descending, then created_at ascending (highest priority first, oldest first within same priority). The unified-queue artifact showed this explicitly. The Phase 2 spec's `claim_message` activity has `sort` parameter but the actual values aren't consistently specified.
Source: unified-queue-temporal-execution

**G-79: Refresh token rotation overlap window**
Auth design specifies: "Rotated on refresh with 30s overlap window for race handling." When a refresh token is used, both the old and new tokens are valid for 30 seconds. This prevents concurrent requests from the same client from failing. Implementation: the old refresh token hash stays in Secrets Manager for 30s before deletion.
Source: authentication-design (hybrid JWT + Session model)

**G-80: `process_bulk_batch` activity implementation**
The BulkExecuteWorkflow calls `process_bulk_batch` but this activity is never defined. Must: query entities by filter (with pagination from `processed` offset), open a MongoDB transaction, iterate entities in the batch, apply the operation per entity, handle per-entity errors (permanent = skip+record, transient = raise for Temporal retry), commit the transaction, emit per-entity events within the transaction, return batch result with error details.
Source: bulk-operations-pattern (execution section, failure handling section)

**G-81: Bulk dry-run implementation**
`--dry-run` flag on bulk operations needs: execute the filter query, count affected entities, optionally preview first N entities and what would change, report without committing. The workflow should have a dry_run parameter that skips the write transaction and returns only the preview.
Source: bulk-operations-pattern (dry-run as safety net)

---

## Pass 6 Findings: Edge Cases and Operational Concerns

Thinking about what happens in production. What goes wrong? What does an operator need?

**G-82: Connection pool configuration per service**
The infrastructure artifact specifies explicit maxPoolSize per service:
- API Server: maxPoolSize=50 (async Motor, connections shared across requests)
- Queue Processor: maxPoolSize=10 (low query volume)
- Temporal Worker: maxPoolSize=30
These values must be in the configuration/code for each entry point. Not specified in the specs.
Source: infrastructure-and-deployment (Production Requirements #3)

**G-83: Structured logging format**
White paper says logs ship to Grafana Cloud via OTEL. But the actual log format (structured JSON? OTEL log export?), log levels, and what gets logged at each level are not specified. Associates executing CLI commands should log each command and its result. Entity saves should log the entity type and ID. Watch evaluations should log match/no-match. Rule evaluations should log which rules matched.
Source: infrastructure-and-deployment (Log shipping), white paper Section 7

**G-84: Graceful shutdown for all services**
When Railway deploys a new version, old instances drain. The API server must: stop accepting new requests, finish in-flight requests, close WebSocket connections cleanly, close MongoDB connections. The Temporal worker must: stop polling for new tasks, finish running activities, call `worker.shutdown()`. The queue processor must: stop its sweep loop, finish any in-flight dispatches. None of this is specified.
Source: infrastructure-and-deployment (Rolling deployments)

**G-85: Error response format**
The API returns errors on validation failure, permission denial, entity not found, state machine violation, version conflict, etc. The error response format should be consistent:
```json
{
  "error": "StateMachineError",
  "message": "Cannot transition from 'received' to 'closed'. Valid: ['triaging']",
  "entity_type": "Submission",
  "entity_id": "..."
}
```
Not specified anywhere.
Source: general API design best practice, implied by the CLI needing to parse errors

**G-86: Idempotency utilities for message processing**
Hardening requirement #6 (2026-04-07): "Idempotent message processing utilities." The framework should provide helpers for actors to check "have I already processed this?" before taking non-idempotent actions (sending emails, creating entities).
Source: core-primitives-architecture (hardening requirement #6)

---

## Updated Final Summary

| Phase | Gaps |
|---|---|
| Phase 0+1 | 27 |
| Phase 2+3 | 22 |
| Phase 4+5 | 23 |
| Phase 6+7 | 4 |
| Cross-cutting | 10 |
| **Total** | **86** |

## Verification Status

- [x] Pass 1: White paper sections (55)
- [x] Pass 2: INDEX.md decisions (7)
- [x] Pass 3: Internal consistency (5)
- [x] Pass 4: Implementability (4)
- [x] Pass 5: Artifact-specific mechanisms (10)
- [x] Pass 6: Edge cases and operational concerns (5)
---

## Pass 7 Findings: Final Sweep

One more pass through the white paper with fresh eyes, plus Phase 0 implementation artifacts.

**G-87: UI graceful degradation for dependency failures**
White paper Section 10 says: "Graceful degradation in the base UI — status banner for degraded dependencies, not a full error page." When Temporal is down (associates stop but humans continue) or an Integration is in error state, the UI should show a status indicator, not crash. Not specified in Phase 4.
Source: white paper Section 10 (What Needs to Be Built)

**G-88: Dockerfile for multi-entry-point kernel image**
Phase 0 references "Dockerfile — kernel image (multi-entry-point)" but doesn't specify the content. Needs to install Python dependencies, copy kernel code, and support three different CMD values for the three services (api, queue_processor, temporal_worker).
Source: Phase 0 acceptance criteria, infrastructure-and-deployment

**G-89: docker-compose.yml for local development**
Phase 0 references "docker-compose.yml — Local dev: API + queue processor + temporal dev server" but doesn't specify the services, ports, environment variables, or how Temporal dev server is configured.
Source: Phase 0 development environment, remaining-gap-sessions (Development Workflow)

**G-90: Temporal retry policies as concrete values**
Phase 2 shows `RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=5), backoff_coefficient=2.0)` for the process activity. But the white paper says "retry policies on ALL workflow activities." Each activity needs its own retry policy tuned to its nature: claim_message (fast retry, low attempts), load_entity_context (fast retry), process_with_associate (slow retry for LLM rate limits, more attempts), complete_message (fast retry). Not all activities should have the same policy.
Source: white paper Section 10 (What Needs to Be Built)

---

## Final Count

| Pass | Description | Gaps Found | Cumulative |
|---|---|---|---|
| 1 | White paper sections | 55 | 55 |
| 2 | INDEX.md decisions | 7 | 62 |
| 3 | Internal consistency | 5 | 67 |
| 4 | Implementability | 4 | 71 |
| 5 | Artifact-specific mechanisms | 10 | 81 |
| 6 | Edge cases and operations | 5 | 86 |
| 7 | Final sweep | 4 | 90 |
| **Total** | | | **90** |

## Verification Status

- [x] Pass 1: White paper sections
- [x] Pass 2: INDEX.md decisions
- [x] Pass 3: Internal consistency
- [x] Pass 4: Implementability
- [x] Pass 5: Artifact-specific mechanisms
- [x] Pass 6: Edge cases and operational concerns
- [x] Pass 7: Final sweep
- **Total: 90 gaps across 7 verification passes**
- **Confidence: HIGH** — I've exhausted the angles I can think of. Remaining gaps would surface during implementation, not during specification review.

## Next Steps

These 86 gaps need to be resolved and incorporated into consolidated, clean specs — one per phase group. The gaps range from:
- **Missing function implementations** (G-07, G-21) — need actual code
- **Missing mechanism specifications** (G-02, G-68) — need design decisions
- **Missing CLI/API surface** (G-12, G-13, G-14) — need endpoint definitions
- **Missing flow specifications** (G-20, G-36, G-37) — need step-by-step flows
- **Explicit documentation of decisions** (G-56, G-61, G-62) — need text

Consolidation approach: rewrite each phase spec from scratch, incorporating the original content, the addendum content, and the gap resolutions into one authoritative artifact per phase group.
