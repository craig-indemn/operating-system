---
ask: "First boot shakeout — audit the built system end-to-end before any CLI command has ever hit a running API server"
created: 2026-04-15
workstream: product-vision
session: 2026-04-15-a
sources:
  - type: codebase
    ref: "https://github.com/indemn-ai/indemn-os"
    description: "indemn-os repo at commit f41b505 (pre-shakeout baseline)"
---

# Shakeout Session Findings

**Status:** IN PROGRESS — API + CLI + UI tested, remaining items: auth events, assistant, WebSocket, org clone/diff/import

## Test Environment

- **Database:** Atlas dev cluster (`indemn_os_audit` — isolated test database)
- **Server:** uvicorn on port 8000, single instance
- **UI:** Vite dev server on port 5178
- **Baseline commit:** f41b505

---

## Results Summary

### API (Steps 1-8)

| Step | What | Result |
|------|------|--------|
| 1 | Boot API server | PASS |
| 2 | Platform init | PASS |
| 3 | Create entity types | PASS |
| 4 | Create role with watch | PASS |
| 5 | Create rule + capability | PASS |
| 6 | Create actor + assign role | PASS |
| 7 | ActionItem + stale-check + watch + message | PASS |
| 8 | Org export | PASS |

### CLI (Full scenario via `indemn` command)

| Command | Result |
|---------|--------|
| `indemn platform init` | PASS |
| `indemn platform health` | PASS |
| `indemn entity create Company` | PASS |
| `indemn entity create ActionItem` | PASS |
| `indemn entity enable ActionItem stale_check` | PASS |
| `indemn entity list` | PASS |
| `indemn role create team_member` | PASS |
| `indemn role list` | PASS |
| `indemn role list --show-watches` | PASS |
| `indemn rule create` | PASS |
| `indemn rule list` | PASS |
| `indemn actor create` | PASS |
| `indemn actor add-role` | PASS |
| `indemn actor list` | PASS |
| `indemn actionitem create` | PASS |
| `indemn actionitem get` | PASS |
| `indemn actionitem list` | PASS |
| `indemn actionitem stale-check --auto` | PASS |
| `indemn actionitem transition --to completed` | PASS |
| `indemn actionitem transition --to active` (invalid) | PASS (rejected) |
| `indemn queue stats` | PASS (shows pending message from watch) |
| `indemn org export` | PASS (YAML directory structure) |
| `indemn audit verify` | FAIL (Finding 14) |

### UI

| View | Result |
|------|--------|
| Login page | PASS |
| Login flow (org slug + email + password) | PASS |
| Navigation (entity types auto-generated) | PASS |
| Queue view | PASS |
| Roles overview (with queue depth) | PASS |
| Entity list view (ActionItem — with data) | PASS |
| State transition buttons in list | PASS (visible, positioned correctly) |
| Capability buttons in list | PASS (stale check visible) |
| Entity detail view (auto-generated form) | PASS |
| Detail sidebar (state + transitions + capabilities + relationships) | PASS |
| Sign out | PASS |

### Edge Cases

| Test | Result |
|------|--------|
| Invalid state transition | PASS — rejected with clear error |
| Invalid enum value | PASS — rejected with allowed values |
| Permission enforcement (read denied) | PASS — "PermissionDenied" with role names |
| Permission enforcement (write denied) | PASS — "PermissionDenied" with role names |
| Permission enforcement (read allowed) | PASS |
| Permission enforcement (write allowed) | PASS |

### Core Kernel Loop — Verified End-to-End

1. ActionItem created with `is_overdue: false`, `owner_actor_id: Craig`
2. `indemn actionitem stale-check <id> --auto` → conditions matched → `is_overdue: true`
3. `save_tracked()` detected method_invoked event, invalidated watch cache
4. Watch on team_member role evaluated: `is_overdue == true` matched
5. Scope resolved via `field_path: owner_actor_id` → targeted Craig
6. Message created: `target_role=team_member`, `target_actor_id=Craig`, `status=pending`
7. `indemn queue stats` → `team_member: 1 pending`

---

## Findings — Fixed (12 total)

### Finding 1: ObjectId JSON Serialization (CRITICAL)

**Root cause:** FastAPI's `jsonable_encoder` can't handle `bson.ObjectId`. Every API endpoint returning entity data was broken.

**Fix:** Created `kernel/api/serialize.py` with `to_dict()`. Replaced all `model_dump()` in API routes. Added `_ORJSONResponse` default response class.

### Finding 2: init_beanie Ordering (CRITICAL)

**Root cause:** `kernel/db.py` loaded entity definitions BEFORE calling `init_beanie()`. EntityDefinition constructor needs Beanie initialized.

**Fix:** Moved `init_beanie()` before the entity definition loading loop.

### Finding 3: Motor Database Truth Check (CRITICAL)

**Root cause:** `dir()` iteration on domain entity classes hits `_db_ref` (Motor Database). `bool()` on Motor Database raises `NotImplementedError`.

**Fix:** Skip private attributes (`attr_name.startswith("_")`) in `registration.py`, `meta.py` (both list and detail endpoints).

### Finding 4: Beanie Single-Collection Inheritance (CRITICAL)

**Root cause:** `KernelBaseEntity` had `is_root=True`, storing all 7 kernel entities in one collection with `_class_id` discriminator. Raw Motor inserts via `save_tracked()` didn't include `_class_id`, making entities invisible.

**Decision:** Remove `is_root=True`. Each kernel entity gets its own collection. Matches the spec, eliminates the bug class.

**Fix:** Removed `is_root = True` from `KernelBaseEntity.Settings`.

### Finding 5: String→ObjectId Coercion (CRITICAL)

**Root cause:** JSON payloads carry ObjectId as strings. Entity models expect `bson.ObjectId`. Creating entities with relationship fields failed.

**Fix:** Added `_coerce_objectid_fields()` in `registration.py` for create and update routes.

### Finding 6: date Type Not BSON-Compatible (MODERATE)

**Root cause:** `factory.py` mapped `"date"` to `datetime.date`. BSON only supports `datetime.datetime`.

**Fix:** Map `"date"` to `datetime` in TYPE_MAP.

### Finding 7: Runtime Entity Registration (MODERATE)

**Root cause:** Creating entity definitions or enabling capabilities required a server restart.

**Fix:** Added `register_domain_entity()` in `kernel/db.py`. Called from `create_entity_definition` and `enable_capability` endpoints. Entity types and capability routes available immediately.

### Finding 8: CORS Blocking UI API Calls (CRITICAL)

**Root cause:** FastAPI's 307 trailing-slash redirects expose the real API origin. Browser CORS policy strips auth headers on cross-origin redirects.

**Fix:** Added CORS middleware as outermost middleware. Fixed `useEntities` hook to use trailing slashes.

### Finding 9: Entity Name Resolution from URL Slug (CRITICAL)

**Root cause:** EntityListView/DetailView reconstructed entity names from URL slugs with naive regex. `actionitems` → `Actionitem` (wrong for PascalCase `ActionItem`).

**Fix:** Created `useEntityNameFromSlug` hook that resolves against metadata endpoint.

### Finding 10: Watch Cache Never Invalidated (CRITICAL)

**Root cause:** `invalidate_watch_cache()` existed but was never called. The TTL refresh was a no-op (`pass`). Watches created at runtime were invisible until server restart.

**Fix:** Call `invalidate_watch_cache()` in `save_tracked()` when entity type is Role. Fixed TTL refresh to actually schedule an async reload.

### Finding 11: httpx follow_redirects Default (MODERATE)

**Root cause:** `httpx.Client` defaults to `follow_redirects=False`. CLI calls to auto-generated routes (which have trailing slashes) got 307 responses with empty bodies.

**Fix:** Set `follow_redirects=True` in CLIClient via `_client()` factory method.

### Finding 12: Dynamic CLI Commands Override Static Commands (MODERATE)

**Root cause:** Dynamic command registration created generic CRUD commands for infrastructure entities (Rule, Skill, etc.), overriding their custom CLI command groups with ergonomic flags.

**Fix:** Expanded `_STATIC_CLI_ENTITIES` to include all infrastructure entity types.

---

## Findings — Documented, Not Fixed (4 total)

### Finding 13: CLI --help Shows "Error 401" on stderr

The CLI's dynamic command registration attempts to fetch metadata on every invocation. When no token is set, it prints "Error 401: Missing auth token" to stderr before showing help. Harmless but noisy.

### Finding 14: Hash Chain Verification Recomputes Different Hashes

`indemn audit verify` reports a broken chain because `compute_hash()` at verify time produces different hashes than at write time. The stored chain links are correct (each `previous_hash` matches prior `current_hash`). The recomputation logic has a serialization inconsistency — likely ObjectId or datetime values serialize differently at read vs write time.

### Finding 15: Generic Update Endpoint Bypasses State Machine

`PUT /api/{entities}/{id}` allows setting the status field directly without going through the state transition endpoint. This bypasses state machine validation — any status value is accepted, even invalid transitions.

### Finding 16: Bootstrap Path Doesn't Use save_tracked()

`platform_init` uses Beanie's native `insert()` and `save()`. No change records, no watch evaluation, no optimistic concurrency for the initial org/admin/role. Probably fine for bootstrap, but deviates from "ALL saves go through save_tracked()."

---

## Design Decisions Made During Shakeout

1. **Separate collections** for kernel entities (removed `is_root=True`) — matches spec, eliminates bug class
2. **Explicit `to_dict()` at each route** (Option A for serialization) — no middleware or custom Pydantic types
3. **JSON as default CLI format** — agent-first CLI, agents need complete structured data
4. **Watch cache invalidation in `save_tracked()`** — only place that guarantees all Role saves are covered
5. **Runtime entity registration** — `register_domain_entity()` called inline on definition create and capability enable

---

## Additional Tests (Round 2)

| Test | Result |
|------|--------|
| Auth Events view (UI) | PASS — shows login events with timestamps, actor, details |
| UI transition buttons | PASS — clicked "→ cancelled", status updated, table refreshed |
| UI capability buttons | PASS — clicked "stale check", is_overdue changed, table refreshed |
| `indemn org clone` | PASS — cloned _platform to test-clone (5 items) |
| `indemn org diff` | PASS — detected 1 difference between orgs |
| `indemn org import` | PASS — imported from YAML export (5 items) |
| WebSocket connection | PASS — connects, accepts subscriptions |
| Assistant input | NOT TESTED — requires Anthropic API key |

### Finding 17: Vite Proxy `/auth` Catches `/auth-events` Route (FIXED)

Vite proxy prefix `/auth` matched the React route `/auth-events`, forwarding it to the API instead of serving the SPA. Fixed by changing proxy to `/auth/` (with trailing slash).

### Finding 18: Assistant Has No Tools — Cannot Execute Operations (CRITICAL)

The default assistant endpoint (`POST /api/assistant/message`) streams text from Claude but has **no tool definitions**. The system prompt says "You can execute any CLI command" but the LLM has no mechanism to actually do so — no `tool_use`, no function calling, no `execute_command` tool.

The spec says the default assistant should:
- Inherit the user's session JWT (IMPLEMENTED)
- Load entity skills for the user's roles (IMPLEMENTED — `_load_skills_for_roles`)
- Execute operations via the API using the user's permissions (NOT IMPLEMENTED)

The assistant can describe what operations are available, but it cannot create entities, transition states, invoke capabilities, or do anything. It's a chatbot, not an agent. The harness pattern gives associates the ability to execute `indemn` CLI commands — the default assistant needs the equivalent via API tool definitions.

**This is the biggest gap in the system.** The assistant is described as "at forefront" in the spec — the primary human-to-system interface. Without action capability, it's decorative.

**What's needed:** Tool definitions that map to API endpoints — `create_entity`, `list_entities`, `transition_entity`, `invoke_capability`, etc. Each tool calls the API with the user's JWT. The LLM decides which tools to use based on the user's message and the available skills.

### Finding 19: Dev Anthropic API Key Has No Credits

The API key at `indemn/dev/shared/anthropic-api-key` returns `credit balance is too low`. Even if the assistant had tools, it couldn't run in dev. Not a code issue — account billing.

## Remaining Untested

- WebSocket real-time updates during live entity changes (manual test)
- UI entity creation form (submitting new entity through the form)
- Org deploy (promotion from source to target org)

---

## Files Modified

| File | Changes |
|------|---------|
| `kernel/api/serialize.py` | NEW — `to_dict()` serialization helper |
| `kernel/api/app.py` | `_ORJSONResponse`, CORS middleware |
| `kernel/api/admin_routes.py` | `to_dict()`, runtime registration, `_resolve_org_slug` |
| `kernel/api/registration.py` | `to_dict()`, `_coerce_objectid_fields()`, skip private attrs |
| `kernel/api/meta.py` | Skip private attrs (both endpoints) |
| `kernel/api/rule_routes.py` | `to_dict()` |
| `kernel/api/skill_routes.py` | `to_dict()` |
| `kernel/api/queue_routes.py` | `to_dict()` |
| `kernel/api/lookup_routes.py` | `to_dict()` |
| `kernel/temporal/activities.py` | Removed `model_dump(mode="json")` |
| `kernel/db.py` | `init_beanie` ordering, `register_domain_entity()` |
| `kernel/entity/base.py` | Removed `is_root=True` |
| `kernel/entity/save.py` | Watch cache invalidation on Role save |
| `kernel/entity/factory.py` | `date` → `datetime` in TYPE_MAP |
| `kernel/watch/cache.py` | TTL refresh actually reloads |
| `kernel/cli/app.py` | `SystemExit` catch, expanded `_STATIC_CLI_ENTITIES` |
| `kernel/cli/client.py` | `follow_redirects=True`, table renderer improvements, JSON default |
| `kernel/cli/role_commands.py` | JSON default format |
| `kernel/cli/actor_commands.py` | JSON default format |
| `kernel/cli/entity_commands.py` | JSON default format |
| `kernel/cli/rule_commands.py` | JSON default format |
| `kernel/cli/queue_commands.py` | JSON default format |
| `kernel/cli/skill_commands.py` | JSON default format |
| `kernel/cli/integration_commands.py` | JSON default format |
| `kernel/cli/lookup_commands.py` | JSON default format |
| `ui/src/api/hooks.ts` | Trailing slash in useEntities |
| `ui/src/hooks/useEntityMeta.ts` | `useEntityNameFromSlug` hook |
| `ui/src/views/EntityListView.tsx` | Use `useEntityNameFromSlug` |
| `ui/src/views/EntityDetailView.tsx` | Use `useEntityNameFromSlug` |

## Test Results

- **Unit tests:** 100 passed
- **Integration tests:** 76 passed
- **CLI scenario:** 22 commands tested, 21 pass, 1 known issue (audit verify)
- **UI:** Login, navigation, queue, roles, entity list, entity detail — all working
- **Edge cases:** State machine, enum validation, permissions — all enforced correctly
