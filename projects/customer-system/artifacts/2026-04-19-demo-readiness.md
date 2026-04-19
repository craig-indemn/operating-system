---
ask: "CEO demo readiness assessment — what works, what to show, what to note"
created: 2026-04-19
workstream: customer-system
session: 2026-04-19-a
sources:
  - type: browser-testing
    description: "Full headed browser test suite against production Railway deployment — 15 test scenarios"
---

# Demo Readiness Assessment — 2026-04-19

## Verdict: Ready to Demo

The Indemn OS is live with the first real domain (customer system), 87 companies of real data, and a working AI assistant. The self-evidence property is proven end-to-end: define entities and navigation, list views, detail views, state machines, skills, CLI commands, API endpoints, and assistant knowledge all exist immediately.

---

## Demo Flow (Recommended)

### 1. Login
- URL: https://indemn-ui-production.up.railway.app
- Org: `_platform` / Email: `craig@indemn.ai`
- Clean login page, "Indemn OS" branding

### 2. Navigation
- Show the sidebar: **Operations** (Queue, Roles, Observability), **Entities** (15 domain entities), **System** (7 kernel entities)
- Point out: all 15 domain entities appeared automatically when we defined them. No custom UI code.

### 3. Company List
- 87 real companies. Search "GIC" → 1 result. Filter by "customer" → only customers.
- Smart column ordering: name, type, cohort first. No notes/urls cluttering the table.
- Pagination: 50/page with Previous/Next.

### 4. Company Detail (GIC Underwriters)
- Click into GIC. Show all fields editable in-place.
- **Enum dropdowns**: type (MGA_MGU), cohort (Core_Platform), source (Existing) — all as `<select>`.
- **Relationship resolution**: owner=Platform Admin, standin=Jonathan Chen — names, not ObjectIds.
- **State machine**: "customer" badge in green. Buttons: → expanding, → churned, → paused.
- **Transition**: Click → expanding. Confirm dialog appears. State changes. Transitions update.
- **Entity pickers**: standin field shows "Jonathan Chen" with clear button. Click → dropdown of actors.
- **Date picker**: follow_up_date has native calendar icon.
- Scroll to bottom: Save button, notes field with rich data.

### 5. The Assistant
- Type "What is the ARR for this company?" in the top bar while viewing GIC.
- Panel slides in. Sends message. **Responds: "The ARR for this company is 70000."**
- The assistant has context — knows which entity the user is viewing, knows the schema.
- Input at bottom of panel for follow-up questions.
- This is the vision: AI as a channel into the platform, not a separate system.

### 6. Other Entities
- **Contacts**: 92 records, company relationships, role enums.
- **Stages**: 7 pipeline stages with probabilities (Contact 5% → Signed 100%).
- **OutcomeType**: The Four Outcomes framework — Revenue Growth, Operational Efficiency, Client Retention, Strategic Control.
- **Roles view**: 4 roles with live queue depth.

### 7. The Pitch
- "We defined 14 entities. The system auto-generated everything else. CLI, API, UI, documentation, permissions, assistant knowledge. This is what an object-oriented insurance system looks like."

---

## What Works (Verified via Browser Testing)

| Feature | Status | Evidence |
|---------|--------|----------|
| Login/auth | Working | Clean form, JWT tokens, sign out |
| Navigation grouping | Working | Entities/System/Admin — no infrastructure clutter |
| Entity list views | Working | Auto-generated tables for all 14+ entity types |
| Search (name) | Working | "GIC" → 1 result, API-backed regex search |
| State filter | Working | Dropdown filters by stage/status, API-backed |
| Pagination | Working | 50/page, Previous/Next, "Showing X-Y" or "No results" |
| Smart column ordering | Working | name/title first, enums, then numbers; noise hidden |
| Entity detail views | Working | All fields editable, proper input types |
| Enum dropdowns | Working | Fields with enum_values render as `<select>` |
| ObjectId resolution (list) | Working | Relationship fields show entity names in tables |
| ObjectId resolution (detail) | Working | Sidebar shows "owner: Platform Admin" not "a34d3824" |
| Entity pickers | Working | Searchable dropdown, resolved names, clear button |
| Date pickers | Working | Native `<input type="date">` with calendar icon |
| State badges | Working | Color-coded (green=customer, yellow=prospect, red=churned) |
| State transitions | Working | Buttons for valid transitions from current state |
| Transition confirmation | Working | window.confirm with entity name and target state |
| Error handling on actions | Working | try/catch + alert on transitions, capabilities |
| Back navigation | Working | "← Back to X list" link on detail views |
| URL bookmarking | Working | /:entityType/:entityId routes via React Router |
| Roles view | Working | Role cards with live queue depth |
| Observability | Partial | Queue depth works, state distribution cards empty |
| Assistant connection | Working | Dynamic discovery, WebSocket to chat harness |
| Assistant context | Working | Knows current entity, schema, data |
| Assistant panel input | Working | Text input + Send button at bottom of panel |
| Assistant streaming | Working | Thinking indicator, token-by-token response |
| Real-time WebSocket | Working | Connection established, subscriptions active |
| WebSocket reconnect cap | Working | Stops after 20 attempts instead of infinite loop |

---

## Known Limitations (Post-Demo)

### Assistant
1. **First response latency**: 10-15 seconds on cold start (LLM initialization in chat harness)
2. **Skill tuning needed**: Assistant knows entity data from context but may struggle with complex CLI operations (e.g., "create a task for GIC"). Entity skills document CLI commands but the agent needs better system prompt guidance.
3. **No conversation persistence across page reloads**: Messages stored in localStorage, but the WebSocket session (Interaction + Attention) is created fresh each time. LangGraph checkpointer is wired but thread continuity depends on Interaction ID reuse.

### UI
4. **State distribution cards empty**: The `/api/metrics/state-distribution/{entityName}` endpoint returns empty. The aggregation endpoint is a stub — needs implementation to count entities per state.
5. **Changes timeline may show "No changes"**: For entities created via bulk import (API POST), the trace endpoint returns change records but the timeline component may not match the response shape for all entity types. Needs field-level verification.
6. **"companys" pluralization**: Auto-pluralization appends "s" naively. URL shows `/companys/` not `/companies/`. Cosmetic — consistent between API and UI.
7. **No column selection UI**: Smart defaults work but users can't customize which columns they see. Per-user preferences would require actor settings or localStorage.
8. **No bulk actions in UI**: Checkboxes + bulk transition not implemented. Available via CLI (`indemn company bulk-transition`).
9. **Test entities still in database**: TestTask, VerifyTest from prior E2E testing. Hidden from navigation but exist in MongoDB. Harmless.

### Kernel/API
10. **Bulk-create via Temporal broken**: org_id not propagated to Temporal worker. Workaround: individual creates work fine. Fix: include org_id in BulkOperationSpec.
11. **No search param on kernel entity endpoints**: The `?search=` parameter was added to domain entity routes but kernel entity routes (Actor, Role, etc.) don't have it.
12. **Hash chain verification broken**: Known from the wiring audit (Finding 14). `indemn audit verify` fails due to ObjectId/datetime serialization mismatch in hash computation.

### Infrastructure
13. **VITE_DEFAULT_ASSOCIATE_ID not embedded at build time**: Railway env vars may not be available during Vite build step. The dynamic discovery (API lookup after login) works as a reliable fallback.
14. **Chat harness uses Gemini (Vertex AI)**: The `Unrecognized FinishReason enum value: 15` warning in logs comes from the Google proto library. Non-fatal but noisy.

---

## Session Summary — 2026-04-19

### Commits to indemn-os (20 total)
1. `437c367` — CLI trailing slash fix (14 paths)
2. `01b9872` — Decimal serialization (insert path)
3. `238f33a` — Decimal serialization (update path)
4. `f2359c8` — Bulk-create reads CSV client-side
5. `c789d06` — Tier 1 UI: navigation, ObjectId resolution, assistant wiring
6. `15bbbe6` — Assistant discovery uses apiClient
7. `5958cb2` — Assistant discovery re-runs after login
8. `6bde337` — Tier 2 UI: search, enums, pagination, transitions, changes, pickers
9. `f4bce81` — TypeScript errors fix (ChangeRecord type alignment)
10. `15572b9` + `698d580` — Cache bust + node_modules cleanup
11. `7f2a80e` — Tier 3 UI: smart columns, assistant context, observability
12. `dd476a9` — Code review fixes: trailing slashes, error handling, ResolvedLink consolidation
13. `eea3302` — Remaining review: panel input, reconnect cap, auth context, metrics split
14. `d0c2de4` — API: state field resolution + search support in list endpoint

### Data in the OS
| Entity | Count |
|--------|-------|
| Companies | 87 |
| Contacts | 92 |
| Associate Types | 24 |
| Conferences | 2 |
| Stages | 7 |
| Outcome Types | 4 |
| Human Actors | 14 |
| Roles | 4 (harness_service, platform_admin, team_member, test_task_processor) |
| Entity Definitions | 14 customer + 3 test + 1 Interaction |
| Auto-Generated Skills | 24 (23 entity + 1 associate) |
| OS Assistant | 1 (active, 23 skills loaded, chat runtime) |

### Bugs Found and Fixed
| # | Bug | Where | Fix |
|---|-----|-------|-----|
| 1 | CLI 401 on collection endpoints (trailing slash redirect strips auth) | CLI | Added `/` to all collection paths |
| 2 | Decimal serialization failure on insert | Kernel save.py | _convert_decimals() in _serialize_entity() |
| 3 | Decimal serialization failure on update | Kernel save.py | Update path uses _serialize_entity() |
| 4 | Bulk-create sent local file path to remote API | CLI bulk_commands.py | Read CSV client-side, send parsed rows |
| 5 | State filter hardcoded "status" field name | Kernel registration.py | Resolve via _state_field_name |
| 6 | No search support in list API | Kernel registration.py | Added ?search= with regex on name/title |
| 7 | Changes timeline queried non-existent endpoint | UI hooks.ts | Fixed to use /api/trace/entity/ |
| 8 | TypeScript build failed silently (ChangeRecord types) | UI hooks.ts + ChangeTimeline | Fixed field mapping |
| 9 | Actor list --type mapped to status param | CLI actor_commands.py | Changed to type param |
| 10 | Missing trailing slashes in entity_commands + bulk_monitor | CLI | Added trailing slashes |
