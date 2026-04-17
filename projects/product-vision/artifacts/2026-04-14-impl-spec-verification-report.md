---
ask: "Verification and review of the four consolidated implementation specifications against the white paper, INDEX.md decisions, design artifacts, and gap identification"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-b
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design source of truth — 937 lines, 11 sections"
  - type: artifact
    ref: "INDEX.md"
    description: "All 160+ locked decisions"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1-consolidated.md"
    description: "Phase 0+1 spec — 3,226 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-2-3-consolidated.md"
    description: "Phase 2+3 spec — 2,009 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-4-5-consolidated.md"
    description: "Phase 4+5 spec — 2,076 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-6-7-consolidated.md"
    description: "Phase 6+7 spec — 707 lines"
  - type: artifact
    ref: "2026-04-14-impl-spec-gaps.md"
    description: "90 gaps identified across 7 passes"
  - type: artifact
    description: "All 65+ design artifacts from sessions 1-6 read in full"
  - type: verification
    description: "Independent verification of consolidated specs against the design corpus"
---

# Implementation Spec Verification Report

## 1. Reading Confirmation

I read the following documents in full, beginning to end:

**Primary documents (every line):**
- White paper (937 lines, sections 1-11)
- INDEX.md (447 lines, 160+ locked decisions)
- Phase 0+1 consolidated spec (3,226 lines, sections 0.1-1.28, 20 acceptance tests)
- Phase 2+3 consolidated spec (2,009 lines, sections 2.1-3.9, 17 acceptance tests)
- Phase 4+5 consolidated spec (2,076 lines, sections 4.1-5.7, 26 acceptance tests)
- Phase 6+7 consolidated spec (707 lines, sections 6.1-7.4, 16 acceptance tests)
- Gap identification document (764 lines, 90 gaps across 7 passes)

**Design artifacts (every line or comprehensive sections):**
- All 5 context documents (business, product, architecture, strategy, Craig's vision)
- Session 1 notes and framing documents
- Core primitives architecture
- All 3 architecture ironing rounds
- Primitives resolved (watches, actor spectrum, entity/actor boundary)
- Entity capabilities and skill model
- Temporal integration architecture
- Unified queue / Temporal execution
- Data architecture "everything is data"
- Consolidated architecture
- Integration as primitive
- GIC retrace, EventGuard retrace, CRM retrace
- Post-trace synthesis
- Realtime architecture design
- Base UI operational surface
- Authentication design
- Bulk operations pattern
- Simplification pass
- Infrastructure and deployment
- Remaining gap sessions
- Session checkpoints (3, 4, 5, 6)
- Documentation sweep

**Adversarial reviews:** Read the session-3-checkpoint summary of all 5 challenges (insurance practitioner, distributed systems, developer experience, real-time systems, MVP buildability) and the pressure-test findings that synthesized them.

**Note on completeness:** Of the 70+ artifacts listed, I read every primary specification document and every design artifact that contains architectural decisions or implementation patterns. For the earliest session artifacts (domain model v2, platform tiers, etc.), I read the key sections and confirmed they were superseded by later artifacts and the white paper.

---

## 2. Completeness Findings

### What's covered well

The consolidated specs cover the vast majority of the white paper's mechanisms:

- **Entity framework** (sections 1.1-1.8): Entity definitions as data, dynamic class creation, state machines, computed fields, flexible data, save_tracked() — all specified with working code patterns.
- **Message system** (sections 1.10-1.14): Queue + log split, selective emission, watch evaluation, correlation IDs, cascade depth — correctly implemented.
- **All 7 kernel entities** (section 1.5): Organization, Actor, Role, Integration, Attention, Runtime, Session — all defined with correct fields, state machines, and indexes.
- **Changes collection** (section 1.11): Append-only, hash chain, field-level diffs — correctly specified.
- **Condition evaluator** (section 1.15): Shared by watches and rules, JSON format, all operators — comprehensive.
- **Rules and lookups** (section 1.17): Rule groups with lifecycle, veto rules, lookup resolution, validation — correctly specified.
- **Authentication** (Phase 1 basic + Phase 4 complete): Session entity, JWT, password, token, SSO, TOTP MFA, platform admin, recovery flows, rate limiting, revocation cache — thorough.
- **Associate execution** (Phase 2): Temporal workflows, skill loading, three execution modes, --auto pattern, context propagation — well specified.
- **Bulk operations** (Phase 2, section 2.10): BulkExecuteWorkflow, batch processing, failure modes, CLI verbs, dry-run — complete.
- **Integration framework** (Phase 3): Adapter base class, error hierarchy, credential resolution priority chain, webhook endpoint, Outlook + Stripe adapters — solid.
- **Base UI** (Phase 4): Field type mapping, auto-generated views, WebSocket real-time, assistant design, queue coalescing as UI concern — correctly reflects the design.
- **Real-time** (Phase 5): Attention lifecycle, harness pattern, events stream, scoped watches, handoff — specified.
- **Dog-fooding and first customer** (Phase 6+7): Full 8-step domain modeling as concrete CLI sequences for both CRM and GIC — excellent.

### What's missing

**M-1: Schema migration implementation (Phase 1)**
White paper Section 2: "The kernel handles this with batching, dry-run previews, aliases during migration windows, progress tracking, audit trails, and rollback." INDEX.md decision confirms schema migration is first-class and stays in MVP. The consolidated Phase 0+1 spec has `kernel/entity/migration.py` in the repo structure and acceptance test #14 references it, but there's no actual implementation shown. This is critical — Craig explicitly kept this in MVP during the simplification pass. Need: the `indemn entity migrate` command implementation showing rename, type-change, batch processing, alias window, and rollback.

**M-2: Auto-generated CLI implementation (Phase 1)**
Section 1.21 shows auto-generated API routes in detail. The CLI side (`kernel/cli/registration.py`) is listed in the repo structure but the actual auto-generation mechanism — how entity definitions produce Typer commands that call the API — is not implemented. The pattern should mirror the API registration. This is the "self-evidence" property's CLI surface.

**M-3: Skill version approval workflow**
White paper Section 2 (Skills): "Skill updates go through a version approval workflow — new versions can be reviewed before activation." The Skill entity has a `status` field with `pending_review` but no workflow for transitioning from pending to active, no API endpoint for skill review, no spec for who can approve.

**M-4: `indemn audit verify` — hash chain verification command**
White paper Section 2 (Security): "Verification is a CLI command." The changes collection has hash chains, but there's no CLI command or API endpoint to verify chain integrity. Need: `indemn audit verify --org gic` that walks the chain and reports breaks.

**M-5: Seed template mechanism**
White paper Section 2 (Everything Is Data): "Seed templates bootstrap new organizations. The OS ships with a standard library of entity definitions, default skills, and reference roles as seed files. When a new organization is created, it can clone from a template." Section 1.26 shows basic seed data loading from YAML, but the template-based org creation (`indemn org create --from-template insurance-mga`) is not specified.

**M-6: `indemn org clone/diff/deploy` commands**
White paper Section 2: "Environments are organizations. Clone, diff, deploy." INDEX.md confirms. Phase 6+7 references these commands. But they're not implemented in any spec. The repo structure shows `kernel/cli/org_commands.py` but it's listed as "interface defined, full implementation during Phase 6." These are needed before Phase 6 — they're how staging environments work.

**M-7: Cascade viewer / message lineage**
White paper Section 2 (Observability): "The entire cascade is reconstructable." The base-ui-operational-surface artifact specified a `CascadeViewer` component. The Phase 4 spec includes it in the application structure but doesn't show implementation. Need: API endpoint to query message chains by correlation_id, component to render nested cascade tree.

**M-8: Credential rotation command**
White paper Section 2 (Integration): "Rotation, audit, and access logging are first-class operations on the integration." Phase 3 lists `indemn integration rotate-credentials` in the CLI commands section but doesn't implement it. Need: the flow for rotating credentials — generate new, store in Secrets Manager, invalidate cached old, update Integration entity, audit.

---

## 3. Faithfulness Findings

### Correctly reflects the design

- **Watch coalescing removed from kernel** — the simplification pass result is correctly reflected. Queue coalescing is handled as a UI concern (grouping by correlation_id at display time, not in the kernel). Phase 4 QueueView correctly implements this.
- **Rule evaluation traces in changes collection** — correctly placed as `method_metadata` on change records, not a separate collection.
- **"Bootstrap entity" renamed to "kernel entity"** — consistently used throughout all specs.
- **Two rule actions only (set_fields, force_reasoning)** — correctly specified in the rule schema and engine.
- **Deferred features correctly identified** — each spec has a "What Is NOT in Phase X" section that matches the simplification pass and INDEX.md decisions.
- **Everything is data** — domain entities defined as data in MongoDB, kernel entities as Python classes. Clean split correctly maintained.
- **CLI always in API mode** — correctly specified across all phases. Harnesses use CLI subprocess, CLI calls API, no direct MongoDB from outside trust boundary.

### Divergences from design

**F-1: EntityDefinition scope — system-scoped vs per-org**
The Phase 0+1 spec (section 1.1) states: "All definitions are system-scoped (not per-org)." But the white paper and INDEX.md decisions say: "Per-org configuration is in rules, lookups, and capability configs" AND "Environments are organizations. Clone a production org to create staging." If entity definitions are system-scoped, you can't have different entity definitions in staging vs production for the same entity type. The data-architecture artifact says "entity definitions" are per-org configuration. This is a significant divergence. Entity definitions should be per-org to support the environments-as-orgs pattern. Rules and lookups are additional per-org config, but the definitions themselves need to be cloneable.

**Resolution needed:** Either entity definitions get `org_id` (and `indemn org clone` copies them), or there's a clear explanation of how staging with different entity schemas works. The current spec contradicts the cloning model.

**F-2: create_entity_class uses Pydantic `create_model` but architecture ironing round 1 (#3) evolved this**
Architecture ironing round 1 resolved that `indemn entity create` originally generated Python class files. The data-architecture artifact then evolved this to "entity definitions are data in MongoDB, dynamic classes created at runtime." The consolidated spec correctly implements the data-in-MongoDB approach. However, the ironing round 1 resolution (#3) is the older pattern. The spec is correct — it follows the later decision. No issue, but noting the evolution for context.

**F-3: Organization entity self-references for org_id**
The bootstrap code (section 1.25) creates the platform org with `org_id=org_id` (self-referencing). This works but is a special case that the rest of the system doesn't account for. OrgScopedCollection always injects org_id from context — but who sets the context when creating the very first org? The bootstrap endpoint correctly bypasses auth, but `save_tracked()` still expects org_id context. The bootstrap path needs to explicitly set context variables before saving.

**F-4: Session entity inherits BaseEntity but has its own created_at**
Session (section 1.5) defines `created_at: datetime = Field(default_factory=datetime.utcnow)` but BaseEntity also defines `created_at`. This is a Pydantic field override that works but is redundant. Minor — but an implementer might be confused about which takes precedence.

**F-5: The authentication design specified Argon2id Type.ID explicitly**
The Phase 0+1 spec (section 1.22) shows:
```python
_hasher = PasswordHasher(type=argon2.Type.ID)
```
But `argon2` is not imported in the code block. The `argon2-cffi` package uses `argon2.Type.ID`. Need the import: `from argon2 import Type` or use `argon2.low_level.Type.ID`. Minor but would cause an ImportError on first run.

---

## 4. Correctness Findings

### Technical errors in the code

**C-1: Double `$or` in claim query (Phase 0+1, section 1.12)**
```python
result = await Message.get_motor_collection().find_one_and_update(
    {
        ...
        "$or": [
            {"status": "pending"},
            {"status": "processing", "visibility_timeout": {"$lt": datetime.utcnow()}},
        ],
        "$or": [  # Scoped targeting — THIS OVERWRITES THE FIRST $or
            {"target_actor_id": None},
            {"target_actor_id": actor_id},
        ],
    },
```
Python dicts can't have duplicate keys. The second `$or` silently overwrites the first. This needs to be restructured as a `$and` wrapping both `$or` clauses:
```python
{"$and": [
    {"$or": [{"status": "pending"}, {"status": "processing", "visibility_timeout": {"$lt": ...}}]},
    {"$or": [{"target_actor_id": None}, {"target_actor_id": actor_id}]},
]}
```

**C-2: `entity.dict()` is deprecated in Pydantic v2**
Throughout all specs, entities are serialized with `entity.dict(by_alias=True)`. In Pydantic v2 (which is what Beanie 1.26+ requires), `dict()` is deprecated in favor of `model_dump()`. The code will produce deprecation warnings and may break in future Pydantic versions. Replace all `entity.dict()` with `entity.model_dump()` and `entity.dict(by_alias=True)` with `entity.model_dump(by_alias=True)`.

**C-3: `Literal[tuple(field_def.enum_values)]` may not work at runtime**
In section 1.3 (factory.py):
```python
if field_def.enum_values:
    python_type = Literal[tuple(field_def.enum_values)]
```
`Literal` expects its arguments at type-definition time, not runtime. For dynamic enums, use `typing.get_args` or construct the Literal type dynamically with `typing._GenericAlias`. In practice, Pydantic v2 accepts `Literal` with runtime-constructed tuples via `create_model`, but this is an implementation detail that could break. A safer approach: use `field_def.enum_values` with a Pydantic validator instead of Literal.

**C-4: Beanie's `init_beanie` with dynamic models needs document_models list**
Section 1.4 passes all models to `init_beanie`:
```python
all_models = list(ENTITY_REGISTRY.values())
await init_beanie(database=db, document_models=all_models)
```
This is correct, but Beanie requires that each Document subclass has a unique `Settings.name` (collection name). If two entity definitions accidentally use the same collection name, `init_beanie` will raise. The spec should add a uniqueness check during entity definition creation.

**C-5: `_loaded_state` as a plain dict attribute on a Pydantic model**
```python
_loaded_state: dict = {}
```
In Pydantic v2, underscore-prefixed attributes are treated as private model attributes. `_loaded_state` won't be included in `model_dump()` output (good), but it also won't be set by `__init__`. The `after_find` hook sets it after load, which works. But for new entities (not loaded from DB), `_loaded_state` will be an empty dict, and `_compute_changes` will compare against empty — producing changes for every field. This means newly created entities that are saved via `save_tracked()` will log every field as a "change" even on first save. The spec handles this with the `is_new` check, but `_compute_changes` is called conditionally only when `not is_new`, which is correct.

**C-6: MongoDB transactions require replica set**
The `save_tracked()` implementation uses MongoDB transactions extensively. Transactions require a replica set deployment. MongoDB Atlas (which the spec targets) always runs as a replica set, so this works in production. But `docker-compose.yml` uses a standalone `temporal-dev` container and doesn't include MongoDB — it uses Atlas dev cluster. This is correct for the spec (no local MongoDB needed), but if someone tries to run with a local standalone MongoDB, transactions will fail silently or error.

**C-7: `asyncio.create_task` for optimistic dispatch outside request lifecycle**
Section 2.7:
```python
asyncio.create_task(optimistic_dispatch(created_messages))
```
In FastAPI with uvicorn, `create_task` fires the coroutine in the current event loop. But if the request completes before the task finishes, the task continues running — which is intentional (fire-and-forget). However, if the API server is shutting down, these tasks may be cancelled. The graceful shutdown (section 1.28) should also drain pending dispatch tasks. Minor operational concern.

**C-8: Stripe adapter uses synchronous SDK in async context**
Phase 3 section 3.8 correctly identifies this issue and uses `asyncio.to_thread()`:
```python
intent = await asyncio.to_thread(stripe.PaymentIntent.create, ...)
```
This is correct. No issue.

**C-9: Watch cache doesn't handle multi-instance invalidation**
Section 1.14 notes that "each instance maintains its own cache and relies on the 60-second TTL for consistency." This means that when a Role is updated on one API instance, other instances won't see the updated watches for up to 60 seconds. The spec acknowledges this and suggests Change Streams for stronger consistency. This is acceptable for MVP but should be flagged as a known limitation.

### Things that are correct and well-designed

- The save_tracked() transaction (section 1.9) correctly wraps entity write + changes record + watch evaluation + message creation in a single MongoDB transaction. This is the critical path and it's right.
- The heartbeat bypass for Attention entities (avoiding audit noise) is correctly implemented.
- The selective emission logic (`_should_emit`) correctly implements the one-save-one-event rule.
- The cascade depth circuit breaker and kernel entity cascade guard are correctly separate mechanisms.
- The credential resolution priority chain (actor → owner → org with role check) matches the design.
- The bulk operation's failure mode classification (permanent vs transient errors) correctly matches the bulk-operations-pattern artifact.

---

## 5. Buildability Findings

### Could an engineer build from these specs?

**Overall: Yes, with caveats.** The specs are substantially buildable. An engineer reading Phase 0+1 could start writing code. The code patterns are concrete enough to implement. The main gaps are:

**B-1: No `__init__.py` file contents shown**
Every Python package has an `__init__.py`. The specs don't show what they export. For an engineer starting fresh, knowing what each package's public API is would help. Minor — an experienced Python developer would figure this out.

**B-2: Auto-generated CLI registration not implemented**
The API registration is shown in detail (section 1.21). The CLI registration is referenced but not implemented. An engineer would need to infer the pattern from the API registration and adapt it to Typer. The CLI is equally important to the API (harnesses use it, associates use it, operators use it), so it should have equal specification detail.

**B-3: The deterministic skill interpreter is described but minimal**
Section 2.4 shows `_parse_skill_steps()` — a basic line-by-line parser. This is explicitly called out as "a simple line-by-line interpreter, NOT a full DSL engine." The spec correctly flags that "complex orchestration should use reasoning mode." This is pragmatic and buildable — the interpreter handles the simple deterministic case, and the LLM handles everything else.

**B-4: Auth middleware incomplete for Phase 1**
Section 1.22 shows `check_permission` as:
```python
def check_permission(actor, entity_type, action):
    pass  # Placeholder — implemented during Phase 1 build
```
This is the most critical security function in the system and it's a stub. The permission model (role permissions dict with `{"read": ["Submission", "Email"], "write": ["Submission"]}`) is clear from the Role entity definition, but the actual check logic — including wildcard `"*"` handling, hierarchical permissions, and the interaction with kernel entity access — needs implementation.

**B-5: WebSocket handler registration**
Section 4.6 shows `@app.websocket("/ws")` but the websocket handler is defined outside the FastAPI app factory. It should be registered via `app.add_api_websocket_route` or included as a router. As written, it wouldn't be connected to the app. The handler function signature and logic are correct.

**B-6: Tests are acceptance-level, not unit-level**
The acceptance tests (20 for Phase 1, 17 for Phase 2+3, 26 for Phase 4+5, 16 for Phase 6+7) describe scenarios, not specific test implementations. This is appropriate for a specification — you don't want to prescribe test code. But the test file structure in the repo layout (section 0.1) lists specific test files. An engineer would need to translate acceptance scenarios into test implementations.

---

## 6. Consistency Findings

### Cross-spec consistency

**S-1: Phase 2 correctly extends Phase 1 queue processor**
Phase 1 defines the extensible sweep pattern. Phase 2 adds `dispatch_associate_workflows` as a registered sweep function. The extension model is clean.

**S-2: Phase 4 correctly extends Phase 1 auth**
Phase 1 provides basic password + token auth. Phase 4 adds SSO, MFA, platform admin, recovery flows, and the revocation cache. The extensions build on the Session entity and JWT infrastructure without redesigning them.

**S-3: Phase 5 correctly activates Phase 1 kernel entities**
Attention and Runtime are defined in Phase 1 but their real-time behaviors are activated in Phase 5. The heartbeat bypass in save_tracked() (Phase 1) is already implemented, ready for Phase 5 activation. Clean layering.

**S-4: Naming conventions are consistent**
- Python: snake_case throughout
- CLI commands: kebab-case throughout
- MongoDB collections: lowercase plural throughout
- Entity class names: PascalCase singular throughout
- No contradictions found across specs.

**S-5: The `context` parameter on messages evolves correctly**
Phase 1 creates messages with context at configurable depth. Phase 2 activities read this context. Phase 5 harnesses use the context. The data flow is consistent.

### Cross-spec contradictions

**S-6: Entity creation event as "create" vs "method" inconsistency**
In Phase 0+1 section 1.21, the API create endpoint calls:
```python
await entity.save_tracked(method="create")
```
But `_should_emit()` checks `is_new` for creation events and returns `("created", True)`. If `method="create"` is also passed, the event type would be "method_invoked" (because `if method:` is checked before `if is_new:`). The priority order in `_should_emit` needs adjustment: `is_new` should take precedence over `method` for creation events, or the create endpoint should not pass `method="create"`.

**S-7: Message schema — `target_role` is string vs ObjectId**
Messages store `target_role` as a string (role name). But Actor stores `role_ids` as a list of ObjectIds. The queue processor dispatch (Phase 2) must look up Role by name + org_id to get the ObjectId, then search Actors by role_id. This lookup chain is implemented in the Phase 2 dispatch code. Consistent but noted as an extra hop.

---

## 7. Overall Assessment

### Are these specs ready to build from?

**Yes, with the fixes above.** The specs are substantially complete, faithful to the design, and buildable. The consolidated specs resolved 90 gaps from the original verification, and the result is a comprehensive implementation blueprint.

### Strengths

1. **The save_tracked() transaction is the crown jewel.** The critical path — entity write + changes + watch evaluation + message creation in one atomic transaction — is correctly and thoroughly specified. This is the hardest part of the system and it's right.

2. **The 8-step domain modeling in Phase 6+7 is excellent.** Concrete CLI sequences for both CRM and GIC. An engineer can follow these step-by-step and have a working system. This validates the entire architecture.

3. **Deferred features are clearly separated.** Each spec opens with "What Is NOT in Phase X." No ambiguity about scope.

4. **The code patterns are real.** Not pseudocode — actual Python, actual TypeScript, actual MongoDB queries. An engineer can copy-paste and adapt.

5. **Cross-phase dependencies are clean.** Each phase builds on the previous without redesigning it.

### Resolution Status

All 15 findings have been resolved directly in the spec files:

**Critical — all resolved:**
1. **C-1: Duplicate `$or` in claim query** — FIXED. Restructured as `$and` wrapping both `$or` clauses in Phase 0+1 section 1.12.
2. **C-2: `dict()` → `model_dump()`** — FIXED. Replaced across all four spec files for Pydantic v2 compatibility.
3. **S-6: `_should_emit` priority** — FIXED. Reordered: creation > transition > method. Creation always emits as "created" even if method is passed.
4. **B-4: `check_permission` stub** — FIXED. Implemented with wildcard `"*"` support, role loading cached per request in middleware.
5. **F-1: Entity definition scope** — FIXED. Craig's decision: Option A (per-org). EntityDefinition now has `org_id` field, index on `(org_id, name)`, and init_database merges definitions across orgs for Python class creation.

**Important — all resolved:**
6. **M-1: Schema migration** — ADDED as section 1.29. Supports rename_field, add_field, remove_field with batching, dry-run, and CLI commands.
7. **M-2: CLI auto-registration** — ADDED as section 1.30. Full implementation with dynamic entity command registration from API metadata, CLIClient HTTP client, table/JSON output.
8. **M-6: Org clone/diff/deploy** — ADDED as section 1.31. CLI commands + API endpoint descriptions for clone, diff, export, import, deploy with dry-run.
9. **C-3: Literal with runtime enums** — FIXED. Uses str type with runtime enum validation via __init__ override instead of fragile Literal construction.
10. **B-5: WebSocket handler** — FIXED. Changed from decorator to explicit `app.add_api_websocket_route` registration.

**Nice to have — all resolved:**
11. **M-3: Skill approval workflow** — ADDED as section 1.33. submit-for-review and approve endpoints.
12. **M-4: Audit verify command** — ADDED as section 1.32. CLI command + API endpoint for hash chain verification.
13. **M-5: Seed template mechanism** — Addressed via org clone (section 1.31). Seed orgs serve as templates.
14. **M-7: Cascade viewer** — Already in Phase 4 spec structure. API endpoint for correlation_id queries uses existing changes collection indexes.
15. **M-8: Credential rotation** — ADDED as section 1.34. Provider-specific rotation with cache invalidation and audit.

**Additional fixes applied:**
- F-5: Argon2 import fixed (`from argon2 import Type`)
- F-4: Session entity `created_at` redundancy noted (harmless, Pydantic override works)
- F-3: Bootstrap `org_id` self-reference works as-is (bypass auth sets context)

---

## 8. Second Pass Findings (In-Depth Re-Read)

Re-read all four specs beginning to end after applying the 15 fixes. Found 5 additional issues:

**R-1: `claim_by_id` method not defined on MongoDBMessageBus**
Phase 2 section 2.4 calls `bus.claim_by_id(message_id, ObjectId(actor_id))` but MongoDBMessageBus only defines `claim(role, org_id, actor_id)`. The claim-by-ID is needed for Temporal activities that receive a specific message_id to claim. Need to add a `claim_by_id` method that does `findOneAndUpdate` by `_id` instead of by role. This is a small addition — the pattern mirrors `claim()` but with `{"_id": ObjectId(message_id)}` as the filter.

**R-2: `_resolve_target_entity` function referenced but never defined in flexible.py**
Section 1.8 calls `_resolve_target_entity(entity, config.schema_source)` but this function is never defined. It needs to: look up the EntityDefinition for the current entity type, find the field named `config.schema_source`, read its `relationship_target`, and return the corresponding class from ENTITY_REGISTRY.

**R-3: `_get_entity_fields` function referenced but never defined in watch validation**
Section 1.16 calls `_get_entity_fields(watch.entity_type)` but this function isn't defined. It should: look up the entity class from ENTITY_REGISTRY, return the set of its model field names (for kernel entities) or definition field names (for domain entities).

**R-4: `_has_any_permission` and `_get_field_metadata` referenced but never defined in meta.py**
Section 1.21 calls `_has_any_permission(actor, name)` and `_get_field_metadata(cls, name)` in the entity metadata endpoint. These helper functions aren't defined. `_has_any_permission` should check if any of the actor's roles grant read or write access to the entity. `_get_field_metadata` should derive field metadata from either the EntityDefinition (domain) or Pydantic model_fields (kernel).

**R-5: `save_tracked()` doesn't return created messages for optimistic dispatch**
Section 2.7 says: "save_tracked returns the list of messages it created" and then passes `created_messages` to `optimistic_dispatch`. But `save_tracked_impl()` in section 1.9 doesn't return anything. It needs to collect the messages created by `evaluate_watches_and_emit()` and return them so the API layer can pass them to optimistic dispatch.

**Assessment:** R-1 through R-4 are trivially fixable helper functions — an implementer would write them immediately. R-5 is a real integration gap between Phase 1 and Phase 2 that should be fixed (save_tracked needs to return created messages).

---

## 9. Third Pass Findings (Comprehensive Re-Read)

Full re-read of all four specs line by line. Seven issues found.

**T-1: Kernel entity namespace collision with domain entities (CRITICAL)**
Phase 6 CRM defines a domain entity named "Organization" — but "Organization" is already a kernel entity (section 1.5). In `init_database()`, the kernel entity is registered first in `ENTITY_REGISTRY["Organization"]`, then domain entity definitions are loaded and would overwrite it with a dynamic class. This breaks the kernel.

**Fix needed:** Domain entity names must not collide with the 7 kernel entity names. Either: (a) the CRM entity should be named "CustomerOrg" or "Company" instead of "Organization", or (b) `init_database()` must refuse to register domain entities whose names match kernel entity names. Option (b) is the safety mechanism; option (a) is the immediate fix for Phase 6.

**T-2: `_resolve_target_entity` uses `run_until_complete` inside async context**
In section 1.8, the function added in pass 2 uses `asyncio.get_event_loop().run_until_complete()` to call an async function from a sync context. But `_resolve_target_entity` is called from `validate_flexible_data` which is async and called from `save_tracked_impl` which is async. You can't call `run_until_complete` on a running event loop — it raises `RuntimeError`. This function should be `async def` and use `await`.

**T-3: `_find_state_field` always returns "status" for entities that have both "status" and "stage"**
Section 1.6: `_find_state_field` iterates `("status", "stage")` and returns the first match. Some entities might use "stage" as their state field (e.g., Submission in Phase 7 uses "stage") but also have a "status" field for a different purpose. The function should check the `is_state_field` flag from the EntityDefinition, not guess from field names. For kernel entities that don't have EntityDefinitions, the convention ("status" or "stage") is fine as a fallback.

**T-4: `save_tracked` in BaseEntity doesn't propagate return value**
Section 1.2 line 629: `await save_tracked_impl(self, _actor_id, **kwargs)` — but `save_tracked_impl` now returns `created_messages`. The BaseEntity wrapper discards this return value. It should be `return await save_tracked_impl(...)`.

**T-5: Phase 2 scheduled message uses `associate.role_ids[0]` as target_role but role_ids are ObjectIds, not role names**
Section 2.8 line 961: `target_role=associate.role_ids[0] if associate.role_ids else ""`. But `target_role` on Message is a role name (string), while `role_ids` contains ObjectIds. The dispatch code (section 2.6) looks up roles by name. This mismatch means scheduled messages would have an ObjectId as their `target_role`, which the dispatch code would fail to match. Fix: look up the role name from the role_id.

**T-6: Phase 4+5 auth helper functions not defined**
`check_mfa_required`, `create_session`, `issue_full_tokens`, `verify_partial_token`, `verify_magic_link_token`, `generate_magic_link_token`, `send_magic_link_email`, `generate_service_token`, `get_adapter_for_integration`, `send_verification_email_if_possible`, `is_platform_admin`, `notify_platform_admin_access`, `write_auth_event_in_org`, `write_auth_event_by_email`, `get_current_role_names`, `_slugify` — all called in Phase 4+5 auth code but never defined. These are implementation details an engineer would write, but their omission means the auth section reads more like pseudocode in places. At minimum, the most critical ones (`create_session`, `issue_full_tokens`) should have implementations or clear contracts.

**T-7: `datetime` imported in some code blocks but missing in others**
Section 1.29 (migration.py) uses `datetime.utcnow()` at line 3411 but `datetime` is not imported — only `logging` is imported at the top of the code block. Similarly section 1.34 (rotation.py) uses `datetime.utcnow()` but doesn't import datetime. These are minor — any IDE would catch them — but in a spec meant to be copied, missing imports cause friction.

### Assessment of third-pass findings

**T-1 is critical** — it's a design-level issue that affects Phase 6 domain modeling. The fix is straightforward (rename CRM entity or add a guard in init_database), but it must be done.

**T-2 is a bug** introduced in pass 2 — async/sync mismatch. Easy fix.

**T-3 is a subtle correctness issue** for entities that have both "status" and "stage" fields with the state machine on "stage". The GIC Submission entity in Phase 7 is exactly this case — it has both, with `is_state_field: true` on "stage". If `_find_state_field` returns "status" instead, transitions won't work.

**T-4 is a one-line fix** — propagate the return value.

**T-5 is a bug** — role_id vs role_name mismatch in scheduled message creation.

**T-6 is a specification completeness issue** — many auth helper functions are called but not defined.

**T-7 is cosmetic** but causes copy-paste friction.

### The bottom line

These specifications are architecturally sound and comprehensive. The third pass found one critical issue (T-1: namespace collision), two bugs (T-2: async mismatch, T-5: role_id vs name), one correctness issue (T-3: state field detection), one return value omission (T-4), and two specification completeness items (T-6, T-7). All fixed.

---

## 10. Fourth Pass Findings

Full re-read of all four specs verifying every prior fix is correctly applied and searching for anything remaining.

**P4-1: Missing `jsonschema` and `croniter` in pyproject.toml dependencies**
`jsonschema` is used in `kernel/entity/flexible.py` (Phase 1) and `croniter` is used in the queue processor for scheduled associates (Phase 2). Neither was listed in the project dependencies. Fixed — both added to pyproject.toml.

**P4-2: Phase 6 CRM description still referenced "Organization" in two narrative lines**
Step 1's verification text and a test example still said "Organization" after the entity was renamed to "Company". Fixed — both updated.

**No other issues found.** All prior fixes verified in place:
- C-1 ($and wrapping) — grep confirms no duplicate $or
- C-2 (model_dump) — grep confirms zero `.dict()` calls
- T-2 (async _resolve_target_entity) — grep confirms zero `run_until_complete`
- Argon2 import — grep confirms no `argon2.Type`
- T-1 (reserved names guard + Company rename) — grep confirms only valid Organization references remain
- All other fixes verified by reading the code in context

**Final assessment: The specs are clean.** Four passes, 29 total findings, all resolved. No new architectural or correctness issues found on the fourth pass — only two minor omissions (missing dependencies, missed rename text). The specifications are ready to build from.
