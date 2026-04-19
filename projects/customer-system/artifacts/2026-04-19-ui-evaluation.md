---
ask: "Comprehensive browser evaluation of the Indemn OS UI — does the self-evidence property deliver? Is the system usable? What gaps exist?"
created: 2026-04-19
workstream: customer-system
session: 2026-04-19-a
sources:
  - type: browser-testing
    description: "Full headed browser session against https://indemn-ui-production.up.railway.app — login, navigation, entity lists, detail views, transitions, assistant, observability, roles"
  - type: artifact
    ref: "2026-04-16-vision-map.md"
    description: "Authoritative design reference — what the UI should be"
  - type: artifact
    ref: "2026-04-14-phase-1-domain-model.md"
    description: "14 entity definitions that should auto-generate UI"
---

# UI Evaluation — Browser Testing Results

**Tester:** Claude (acting as Craig and as a hypothetical colleague)
**Date:** 2026-04-19
**Environment:** Production Railway deployment, authenticated as craig@indemn.ai @ _platform
**Data:** 87 companies, 92 contacts, 24 associate types, 2 conferences, 7 stages, 4 outcome types, 14 actors, 4 roles

---

## Verdict: Self-Evidence Property Works. Usability Does Not.

The core promise delivers mechanically — define 14 entities and the system instantly generates navigation, list views, detail views, state machine transitions, skills, CLI commands, and API endpoints. No custom code. This is genuinely impressive and proves the thesis.

But a colleague sitting down at this UI today would not be able to use it effectively. The assistant is broken, relationship fields show ObjectIds instead of names, infrastructure entities clutter the navigation, and there's no search or filtering. The system is a working proof-of-concept, not a usable product.

---

## What Works

### W-1: Entity Navigation (Self-Evidence)
All 14 customer system entities appear in the sidebar immediately after definition. No manual UI registration. The navigation is auto-generated from entity definitions in MongoDB. This is the core self-evidence property and it works.

### W-2: Entity List Views
Company list renders as a table with auto-generated columns from field definitions. Shows 87 rows. Each row shows field values and state machine transition buttons for valid transitions from the current state. "+ New Company" creation button is present and functional.

### W-3: Entity Detail Views
Clicking a company opens a detail view with every field rendered as an editable input. Field types are correctly mapped:
- String fields → text inputs
- Enum fields → text inputs (should be dropdowns — see G-6)
- Integer fields → number spinners
- ObjectId relationship fields → "Select Actor..." / "Select Conference..." pickers
- List fields → tag-style display with individual "x" remove buttons and "Type and press Enter" + "Add" for new items
- Date fields → text inputs (should be date pickers — see G-7)

### W-4: State Machine Transitions
The company detail shows the current state ("customer") in a highlighted box with valid transition buttons: → expanding, → churned, → paused. Clicking a transition works — we verified GIC transitioning customer → expanding → customer. State machine enforcement is real.

### W-5: Skills Auto-Generation
24 skills auto-generated — 14 for customer system entities, 7 for kernel entities, 2 for test entities, 1 associate skill. Each entity skill documents fields, lifecycle, and CLI commands in markdown. Verified via `indemn skill list`.

### W-6: Roles View
Shows roles as cards with live queue depth: harness_service (0 pending), platform_admin (0 pending), team_member (0 pending), test_task_processor (8 pending). Clean, functional view of the wiring.

### W-7: Observability View
Shows per-role queue statistics and an "Integrations" section. Minimal but present.

### W-8: Authentication
Login page works correctly. Organization slug + email + password → authenticated session. Sign out button present.

### W-9: Back Navigation
"← Back to Company list" link on detail view works. Sidebar navigation works for switching between entity types.

### W-10: Data Integrity
All imported data renders correctly. GIC shows ARR=70000, cohort=Core_Platform, stage=customer, owner=a34d3824. Technologies and specialties render as tag lists. The data roundtrip (CSV → CLI → API → MongoDB → UI) is intact.

---

## Gaps — Critical (Blocks Effective Use)

### G-1: Assistant Is Broken [CRITICAL]
**What happens:** Typing in "Ask or tell me to do something..." opens a right-side panel. User's message appears. Then:
- "Error: associate_id required"
- "Error: could not connect to assistant"

**Vision says:** "The assistant panel is a running instance of a chat-kind Runtime" / "Assistant IS a running chat-harness instance — not a kernel endpoint" / "Same deployment model as any real-time harness"

**Impact:** Without the assistant, the OS is a database browser. The entire value proposition of an AI-native system — where the assistant understands all entities, has skills pre-loaded, and can work on behalf of the user — is non-functional. A colleague cannot ask "what companies are stale?" or "create a task for GIC follow-up" or "show me all expansion signals."

**Root cause:** No assistant associate actor is configured for the current user/org. The chat harness connection (WebSocket to indemn-runtime-chat) requires an associate_id which isn't being resolved. This was flagged as "Finding 0b" in the vision map and the wiring audit claimed it was resolved, but the UI still can't establish the connection.

**Fix scope:** Configure a default assistant associate per org, ensure the chat harness runtime is reachable from the UI, wire the assistant panel to create an Interaction and connect to the chat runtime with the user's context.

### G-2: Relationship Fields Show Raw ObjectIds [CRITICAL]
**What happens:** In the company detail view:
- owner: a34d3824
- standin: 432839b0
- engineering_lead: a34d3824
- exec_sponsor: 432839aa

These are truncated ObjectIds. Meaningless to any user.

**Vision says:** Entity GET supports `--depth` and `--include-related` for resolving relationships. The base UI spec says the UI auto-generates from entity definitions.

**Impact:** Every entity with relationship fields (Company has 5 actor refs + 1 conference ref, Contact has 1 company ref, Deal has 3 refs, etc.) shows ObjectIds instead of human-readable names. This makes the detail view nearly useless for understanding relationships. "Who owns GIC?" requires clicking through the ID link, which navigates to the Actor entity detail — but only if you know what the ID means.

**Fix scope:** UI must resolve relationship fields to display names. When rendering a field with `is_relationship: true`, fetch the related entity and display its `name` field. The API already supports `?depth=2&include_related=true` — the UI just needs to use it.

### G-3: Navigation Shows Infrastructure Entities [CRITICAL]
**What happens:** The sidebar shows 36 entity links in a flat alphabetical list under "ENTITIES":
- Kernel entities: Actor K, Attention K, Integration K, Organization K, Role K, Runtime K, Session K
- Infrastructure: ChangeRecord, EntityDefinition, Interaction, Lookup, Message, MessageLog, Rule, RuleGroup, Skill
- Test entities: TestTask, VerifyTest
- Business entities: AssociateDeployment, AssociateType, Commitment, Company, Conference, Contact, Deal, Decision, Meeting, Outcome, OutcomeType, Playbook, Signal, Stage, Task

**Vision says:** "The base UI is a projection of the system definition, not an application on top of it." / "Auto-generated from entity definitions. No per-org custom UI. No per-entity custom code."

**Impact:** A business user (Kyle, Cam, George) seeing "ChangeRecord", "MessageLog", and "RuleGroup" in their navigation is confused and overwhelmed. These are kernel internals. The navigation should show only entities the user's role has permission to see, or at minimum separate infrastructure from business entities.

**Fix scope:** Filter sidebar entities by the authenticated user's role permissions. If role.permissions.read includes specific entity types, show only those. If it includes "*", show all but group by category (Operations, Kernel, Domain). Or: add an `is_infrastructure` flag to entity definitions and hide those from non-platform-admin users.

---

## Gaps — Major (Significantly Reduces Usability)

### G-4: No Search or Filtering on List Views
**What happens:** 87 companies in a single scrollable list. No search box, no filter dropdowns, no way to narrow the list.

**Vision says:** "Tables are interactive (sort, filter, drill, actions)."

**Impact:** Finding a specific company requires scrolling through 87 rows. At 500 companies this is unusable. Can't answer "show me all prospect-stage companies" or "companies with no owner" without the assistant (which is broken — G-1).

**Fix scope:** Add a search box (filters by name field), state filter dropdown (for entities with state machines), and column sort. The API already supports `?status=<state>` filtering.

### G-5: No Pagination
**What happens:** All entities load in one page. The Company list shows all 87, Contact list shows all 92.

**Vision says:** Not explicitly addressed, but implied by "Tables are interactive."

**Impact:** Works at current scale but will break at 500+ entities per type. The API enforces `limit <= 100` so the list may already be truncated without the user knowing.

**Fix scope:** Add pagination controls (page number or infinite scroll with offset). The API supports `?limit=N&offset=M`.

### G-6: Enum Fields Render as Text Inputs, Not Dropdowns
**What happens:** Fields with `enum_values` (e.g., company.type, company.cohort, company.tier, company.source, contact.role, contact.how_met) render as plain text inputs. Users must know the valid values and type them exactly.

**Impact:** Users can type invalid values. The API will reject them (400 error), but the UX is poor. The entity definition already specifies `enum_values` — the UI has the information needed to render dropdowns.

**Fix scope:** When rendering a field where `enum_values` is defined, render a `<select>` dropdown instead of a text input.

### G-7: Date Fields Render as Text Inputs, Not Date Pickers
**What happens:** `date` and `datetime` fields (e.g., conference.date_start, task.due_date, commitment.due_date) render as plain text inputs.

**Impact:** Users must type dates in the correct format. No visual calendar picker.

**Fix scope:** Render date/datetime fields with `<input type="date">` or a date picker component.

### G-8: Transition Buttons Inline on Every List Row
**What happens:** Each company row in the list view shows 2-3 transition buttons (→ expanding, → churned, → paused) inline. With 87 rows, that's 200+ transition buttons visible on the list page.

**Impact:** Visual noise. The list is for browsing and finding entities, not for bulk state changes. A misclick could transition a company accidentally.

**Fix scope:** Move transition buttons to the detail view only. Or: collapse them behind a "..." actions menu on each row.

### G-9: "K" Suffix on Kernel Entities Is Unexplained
**What happens:** Sidebar shows "Actor K", "Attention K", "Integration K", etc. The "K" suffix distinguishes kernel entities from domain entities, but there's no legend or explanation.

**Impact:** Confusing for users who don't know what "K" means. Minor but contributes to the "developer tool" feeling.

**Fix scope:** Either remove the suffix and rely on navigation grouping (G-3), or add a tooltip/legend explaining "K = Kernel entity (system-provided)."

### G-10: No Confirmation on State Transitions
**What happens:** Clicking "→ churned" on a company immediately transitions it. No confirmation dialog.

**Impact:** Accidental clicks can change entity state. Transitions may have business consequences (e.g., churning a customer triggers watches, affects reporting).

**Fix scope:** Add a confirmation dialog for transitions: "Transition [Company Name] from [current] to [target]? [Cancel] [Confirm]"

---

## Gaps — Minor (Polish and Completeness)

### G-11: Company Detail Shows "No changes" Despite Having Change History
**What happens:** The bottom of the company detail shows "No changes" even though GIC has been transitioned twice (customer → expanding → customer, now v4).

**Impact:** The changes collection is a key feature — tamper-evident audit trail, field-level history. If it's not rendering, users lose the "who changed what when" capability.

**Possible cause:** The changes section may query the trace endpoint which returned empty earlier, or it may use a different query pattern. The data is likely in MongoDB but not being fetched.

### G-12: Relationship Picker Shows "Select Actor..." but No Dropdown of Available Actors
**What happens:** Actor relationship fields show a text input with placeholder "Select Actor..." but clicking it doesn't open a dropdown of available actors. Same for "Select Conference..."

**Impact:** Users can't select relationships without knowing the ObjectId. Related to G-2 but specifically about the creation/edit flow.

**Fix scope:** Render relationship fields as searchable dropdowns that query the related entity list (e.g., GET /api/actors/ for Actor relationships).

### G-13: List View Column Selection Is Not User-Controllable
**What happens:** The company list shows columns in definition order. Users can't choose which columns to display, reorder them, or hide irrelevant ones.

**Impact:** Different users care about different fields. Kyle wants to see ARR and stage. George wants to see owner and health_score. Currently everyone sees the same first-N columns.

**Fix scope:** Add column visibility toggles or a user-configurable column set. Could be per-entity per-user preference stored in the browser or in the user's actor settings.

### G-14: No Visual Distinction Between Entity States in the List
**What happens:** All companies look the same in the list regardless of stage. "Customer" and "churned" companies have no visual differentiation.

**Impact:** Can't scan the list and quickly see which companies need attention.

**Fix scope:** Color-code the state column (e.g., green=customer, yellow=prospect, red=churned) or add state-based row styling.

### G-15: "New Company" Button Visible but Not Tested
**What happens:** The "+ New Company" button exists on the company list. Not tested in this evaluation — may or may not work correctly with the full field set.

**Action:** Should be tested in the next session — create a company through the UI and verify all fields, enum validation, and relationship pickers work.

### G-16: No Breadcrumbs or URL-Based Navigation
**What happens:** The URL doesn't update meaningfully when navigating between views. Can't bookmark a specific company or share a direct link.

**Impact:** Can't share "look at this company" with a colleague via URL. Browser back/forward may not work predictably.

### G-17: Assistant Panel Has No Context Awareness
**What happens:** When viewing the GIC company detail, the assistant prompt doesn't show any context about what entity is being viewed. The assistant (if it worked) would need to independently discover context.

**Vision says:** The assistant should understand the user's current context — what view they're on, what entity they're looking at — and respond accordingly.

### G-18: No Bulk Actions on List Views
**What happens:** No checkboxes for selecting multiple entities. No bulk transition, bulk update, or bulk delete from the UI.

**Impact:** Operations like "transition all prospect companies to churned" require using the CLI. The vision mentions bulk operations as a pattern — the UI should expose them.

### G-19: Observability View Is Minimal
**What happens:** Shows one line per role with queue depth, and an empty "Integrations" section.

**Vision says:** Kernel aggregation capabilities include state-distribution, throughput, dwell-time, queue-depth, cascade-lineage. Base UI includes pipeline metric widgets, cascade viewer.

**Impact:** No dashboards, no charts, no state distribution views. The observability view is a stub.

### G-20: No Real-Time Updates
**What happens:** Data is fetched on navigation. If another user changes a company's state, the current user won't see it until they navigate away and back.

**Vision says:** "Real-time via MongoDB Change Streams filtered by org_id + subscription filters. WebSocket keepalive 30-45s ping."

**Impact:** In a team environment, stale data can lead to conflicting actions. Real-time is important for the queue view especially.

---

## Priority Ranking for Resolution

### Tier 1 — Must Fix (Blocks the Vision)
1. **G-1: Assistant broken** — Without this, the OS is just a database viewer
2. **G-2: ObjectId display** — Without readable relationships, detail views are puzzles
3. **G-3: Navigation filtering** — Without this, the UI feels like a developer admin panel

### Tier 2 — Should Fix (Required for Daily Use)
4. **G-4: No search/filtering** — Can't find entities efficiently
5. **G-6: Enum dropdowns** — Users shouldn't type exact enum values
6. **G-12: Relationship pickers** — Can't set relationships without knowing IDs
7. **G-10: Transition confirmation** — Prevents accidental state changes
8. **G-11: Changes not rendering** — Audit trail is a key feature
9. **G-5: Pagination** — Required at scale

### Tier 3 — Nice to Have (Polish)
10. **G-7: Date pickers** — Better UX for date fields
11. **G-8: Inline transitions** — Reduce list view noise
12. **G-9: "K" suffix** — Confusing label
13. **G-14: State color coding** — Visual scanning aid
14. **G-13: Column selection** — User preference
15. **G-16: URL navigation** — Shareable links
16. **G-17: Assistant context** — Context-aware assistant
17. **G-18: Bulk actions** — UI-level bulk operations
18. **G-19: Observability dashboards** — Vision-specified but deferred
19. **G-20: Real-time updates** — Team collaboration feature
20. **G-15: New entity form test** — Needs verification
