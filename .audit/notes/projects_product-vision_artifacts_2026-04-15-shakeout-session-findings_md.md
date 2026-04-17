# Notes: 2026-04-15-shakeout-session-findings.md

**File:** projects/product-vision/artifacts/2026-04-15-shakeout-session-findings.md
**Read:** 2026-04-16 (full file — 299 lines)
**Category:** runtime-findings

## Key Claims

- **First boot shakeout** after the consolidated specs were implemented. Tests API + CLI + UI end-to-end.
- **Test env**: Atlas dev cluster (`indemn_os_audit`), uvicorn port 8000, Vite port 5178, baseline commit `f41b505`.
- **Core kernel loop VERIFIED end-to-end**:
  - ActionItem created → stale-check --auto → conditions matched → is_overdue=true
  - `save_tracked()` detected method_invoked, invalidated watch cache
  - Watch on team_member evaluated: is_overdue==true matched
  - Scope resolved via field_path=owner_actor_id → targeted Craig
  - Message created with target_role + target_actor_id + status=pending
  - Queue stats shows pending message
- **19 findings total** — 13 fixed, 4 documented-not-fixed, 2 untested categories (WebSocket live, org deploy).

### Fixed findings (13):

1. **ObjectId JSON serialization** — FastAPI's `jsonable_encoder` can't handle `bson.ObjectId`. Created `kernel/api/serialize.py::to_dict()`, replaced `model_dump()` in API routes.
2. **init_beanie ordering** — entity definitions loaded BEFORE `init_beanie()`. Fixed order.
3. **Motor Database truth check** — `bool()` on Motor Database raises. Fixed by skipping private attrs.
4. **Beanie single-collection inheritance** — `is_root=True` stored all 7 kernel entities in one collection with `_class_id` discriminator; raw Motor inserts bypassed it. Decision: separate collections per kernel entity. Removed `is_root`.
5. **String→ObjectId coercion** — JSON payloads carry ObjectId as strings. Added `_coerce_objectid_fields()`.
6. **date type not BSON-compatible** — mapped `"date"` to `datetime` in factory's TYPE_MAP.
7. **Runtime entity registration** — `register_domain_entity()` inline so new entity types don't require restart.
8. **CORS blocking UI API calls** — FastAPI 307 trailing-slash redirects on cross-origin drop auth headers. Added CORS middleware as outermost.
9. **Entity name resolution from URL slug** — `actionitems` → `Actionitem` regex issue. Created `useEntityNameFromSlug` hook resolving against metadata endpoint.
10. **Watch cache never invalidated** — `invalidate_watch_cache()` existed but never called. Hooked into `save_tracked()` when Role saves. Fixed TTL refresh.
11. **httpx follow_redirects default** — `httpx.Client` defaults False; CLI calls to trailing-slash routes got empty 307. Set `follow_redirects=True`.
12. **Dynamic CLI overrides static commands** — Dynamic command registration clobbered custom command groups for infrastructure entities. Expanded `_STATIC_CLI_ENTITIES`.
17. **Vite proxy `/auth` catches `/auth-events` route** — changed proxy to `/auth/` (trailing slash).

### Documented-not-fixed findings (4):

13. **CLI --help shows "Error 401" on stderr** — dynamic command registration fetches metadata pre-auth. Harmless but noisy.
14. **Hash chain verification recomputes different hashes** — stored chain is correct; `compute_hash()` at verify time vs. write time has serialization inconsistency (likely ObjectId or datetime serialize differently at read vs. write). `indemn audit verify` always reports broken chain.
15. **Generic update endpoint bypasses state machine** — `PUT /api/{entities}/{id}` allows setting status directly, no state-machine validation. Should be restricted.
16. **Bootstrap path doesn't use save_tracked()** — `platform_init` uses Beanie native insert/save; no change records, no watches. Deviates from "ALL saves go through save_tracked()."

### Finding 18 — THE BIG ONE (Finding 0b at runtime):

**Assistant has no tools — cannot execute operations.** Default assistant endpoint (`POST /api/assistant/message`) streams text from Claude but has **no tool definitions**. System prompt says "You can execute any CLI command" but LLM has no mechanism.

**Implemented:**
- Inherits user's session JWT ✓
- Loads entity skills for user's roles (via `_load_skills_for_roles`) ✓
- Execute operations via API — **NOT IMPLEMENTED**.

**Explicit quote from this artifact** (lines 242-245):
> "The assistant can describe what operations are available, but it cannot create entities, transition states, invoke capabilities, or do anything. It's a chatbot, not an agent. The harness pattern gives associates the ability to execute `indemn` CLI commands — the default assistant needs the equivalent via API tool definitions."
> "This is the biggest gap in the system."

### Finding 19 — Dev Anthropic API key has no credits
- Billing/account issue, not code.
- Even if assistant had tools, it couldn't run in dev.

## Architectural Decisions (made during shakeout)

1. **Separate collections for kernel entities** (removed `is_root=True`) — matches spec, eliminates bug class.
2. **Explicit `to_dict()` at each route** (Option A serialization) — no middleware, no custom Pydantic types.
3. **JSON as default CLI format** — "agent-first CLI, agents need complete structured data."
4. **Watch cache invalidation in `save_tracked()`** — the only place that guarantees all Role saves are covered.
5. **Runtime entity registration** — `register_domain_entity()` called inline on definition create + capability enable.

## Layer/Location Specified

- **Findings 1-12, 17 (fixed)**: all patches in kernel code (API, CLI, UI). Kernel-layer implementation.
- **Finding 18 (assistant has no tools)**: refers to `kernel/api/assistant.py` — **confirms Finding 0b is observable at runtime**. The artifact explicitly contrasts the assistant (kernel endpoint, no tools) with the harness pattern (associates with CLI tool-use ability).
- **Finding 14 (hash chain)**: `kernel/changes/hash_chain.py` serialization mismatch. Deferred for spec fix.
- **Finding 15 (generic update bypasses state machine)**: `kernel/api/registration.py` generic update route. Should be restricted.
- **Finding 16 (bootstrap doesn't use save_tracked)**: `kernel/api/admin_routes.py::platform_init`. Noted as intentional but deviates from invariant.

**Finding 0 relevance**:
- **Finding 18 is the runtime manifestation of Finding 0b.** The shakeout session identified "the biggest gap in the system" as the assistant lacking tools — which is the direct consequence of assistant being a kernel endpoint instead of a chat-harness instance.
- The artifact's proposed fix — "add tool definitions to the assistant endpoint" — addresses the symptom but not the root cause. Pass 2 audit argues the proper fix is building `harnesses/chat-deepagents/` and deleting the kernel endpoint.
- The shakeout session did NOT identify the broader Finding 0 (async agents in kernel Temporal worker vs. async-deepagents harness). It was focused on chat/UI flow, not scheduled/async agent execution.

## Dependencies Declared

- Atlas dev cluster (`indemn_os_audit` database)
- Anthropic API (for assistant — no credits in dev)
- FastAPI + Motor + Beanie
- Typer + httpx (CLI)
- React + Vite + TanStack (UI)

## Code Locations Specified

| File | Changes |
|---|---|
| `kernel/api/serialize.py` | NEW — `to_dict()` helper |
| `kernel/api/app.py` | `_ORJSONResponse`, CORS middleware |
| `kernel/api/admin_routes.py` | `to_dict()`, runtime registration, `_resolve_org_slug` |
| `kernel/api/registration.py` | `to_dict()`, `_coerce_objectid_fields()`, skip private attrs |
| `kernel/api/meta.py` | Skip private attrs |
| `kernel/api/{rule,skill,queue,lookup}_routes.py` | `to_dict()` |
| `kernel/api/assistant.py` | **Finding 18 (no tools) — UNFIXED** |
| `kernel/temporal/activities.py` | Removed `model_dump(mode="json")` |
| `kernel/db.py` | `init_beanie` ordering, `register_domain_entity()` |
| `kernel/entity/base.py` | Removed `is_root=True` |
| `kernel/entity/save.py` | Watch cache invalidation on Role save |
| `kernel/entity/factory.py` | `date` → `datetime` |
| `kernel/watch/cache.py` | TTL refresh actually reloads |
| `kernel/cli/*` | JSON default, follow_redirects, static entity list |
| `ui/src/api/hooks.ts` | Trailing slash |
| `ui/src/hooks/useEntityMeta.ts` | NEW — `useEntityNameFromSlug` |
| `ui/src/views/Entity{List,Detail}View.tsx` | Use new hook |

## Cross-References

- indemn-os repo at commit `f41b505` (pre-shakeout baseline)
- 2026-04-14-impl-spec-phase-0-1-consolidated.md (implemented)
- 2026-04-14-impl-spec-phase-2-3-consolidated.md (implemented)
- 2026-04-14-impl-spec-phase-4-5-consolidated.md (implemented)
- 2026-04-14-impl-spec-phase-6-7-consolidated.md (implemented)
- 2026-04-15-comprehensive-audit.md (Pass 1 audit — identified Finding 0, motivated Pass 2)
- 2026-04-16-pass-2-audit.md (closed the methodology gap and confirmed Finding 0 + 0b architecturally)

## Open Questions or Ambiguities

**Untested in shakeout** (noted as remaining):
- WebSocket real-time updates during live entity changes
- UI entity creation form (submit new entity)
- Org deploy (promote source → target)

**Finding 18's proposed fix** (add tools to kernel endpoint) is a LOCAL fix that restores functionality but entrenches Finding 0b architecturally. The deeper fix requires building the chat harness.

**Finding 14 (hash chain)** still open; Pass 2 noted as unresolved.

**Supersedence note for vision map**:
- The 13 fixed findings are architecturally correct fixes at the mechanism level.
- **Finding 18 is a symptom of Finding 0b**; the shakeout session surfaced it but didn't trace to architectural root cause.
- **Finding 15 (generic update bypasses state machine)** is a spec-level bug — the generic `PUT` endpoint should not accept state-machine fields. Should be fixed in the kernel registration code.
- **Finding 16 (bootstrap bypasses save_tracked)** is a minor invariant violation in `platform_init` — acceptable for bootstrap but should be flagged.
- **Finding 14 (hash chain)** is a compliance-critical correctness bug.

**Vision-map implication**: Shakeout confirmed the kernel core loop works end-to-end. But the spec's Finding-0b deviation (assistant as kernel endpoint without tools) surfaces immediately in practice — confirming this is not a hypothetical layer problem but a working implementation that can't do the assistant's job.
