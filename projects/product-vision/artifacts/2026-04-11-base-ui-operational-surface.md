---
ask: "How does the base UI work as a real-time operational surface? What auto-generates from primitives, what's the assistant's role, how do real scenarios play out?"
created: 2026-04-11
workstream: product-vision
session: 2026-04-11-a
sources:
  - type: conversation
    description: "Craig and Claude working through the base UI as operational surface, reframing Pipeline Dashboard + Queue Health (items 8 and 9 from post-trace synthesis)"
  - type: artifact
    description: "2026-04-10-bulk-operations-pattern.md (prior item 7 design, same structure)"
  - type: artifact
    description: "2026-04-10-base-ui-and-auth-design.md (initial base UI sketch + kernel additions surfaced during the GIC retrace)"
  - type: artifact
    description: "2026-04-10-gic-retrace-full-kernel.md (surfaced pipeline dashboard + queue health as concerns to address)"
  - type: artifact
    description: "2026-04-10-realtime-architecture-design.md (real-time mechanism this builds on: Attention, scoped watches, Change Streams, harness pattern)"
  - type: artifact
    description: "2026-04-10-post-trace-synthesis.md (identified items 8 and 9 in the open design list)"
---

# Base UI as Real-Time Operational Surface

## Context

Items 8 (pipeline dashboard) and 9 (queue health) from the post-trace synthesis, resolved together because they are not two separate features — they are different views of the same underlying surface.

The reframe: **Pipeline Dashboard and Queue Health collapse into the base UI itself.** The base UI is not a separate "dashboard layer" being designed alongside the kernel. It is a real-time operational surface derived from the system definition — a projection of the primitives, not an application on top of them.

Craig's framing: "I want to create a system through the OS and the UI be a natural extension of the system." That's the design principle. When you create an entity, a role, a watch, an integration, the UI reflects it automatically. Adding an entity type doesn't require UI work. Changing permissions changes what a user sees. The UI is derived, not built.

## Design Principles

### 1. UI derives from the system, not the other way around

Entities + roles + watches + permissions + integrations define what the UI shows. No bespoke per-org dashboards at MVP. Adding a domain entity means the UI reflects it immediately — with its fields, state machine, @exposed methods, and any activated kernel capabilities. Removing a permission changes what the role can see and do. The UI is a projection; the system is the source.

### 2. Tables beat charts beat prose, unless data is inherently graphical

Default to interactive tables. Charts are reserved for continuous time-series data where the trajectory's shape matters — and even then, a table with counts and deltas is usually clearer. A "count per state" is a table, not a bar chart. A "throughput per hour" is a table comparing current vs previous windows, not a line chart.

**Test**: if the information fits as cleanly in a table as in a chart, use the table. A table is interactive (sort, filter, drill, act). A chart isn't.

### 3. Interactive tables are the primary data surface

Sort, filter, paginate, drill into rows, take actions on rows. This is where most operational work happens. Row actions correspond to state transitions and @exposed methods the user's role can invoke. Tables are not read-only display — they're the active working surface.

### 4. Forms for create/update, auto-generated

Field types map to form controls (text, number, date, select for enums, entity picker for relationships). Required fields enforced. State machine visualized as "current state + available transition buttons," not a diagram. Simpler is better; no decoration for its own sake.

### 5. Assistant at the forefront

Every human actor has a default associate pre-provisioned with `owner_actor_id` bound to the user, same permissions as the user. The UI surfaces this assistant as a primary input method — a persistent, visible element, not a sidebar companion or hidden keyboard shortcut.

The assistant can execute any CLI command the user has access to. Operating the system via natural language is a first-class surface from day one, with zero incremental kernel work (the mechanism all exists: default associate, CLI, permissions at the entity layer, real-time event streaming).

### 6. Real-time by default

Views subscribe to relevant entity changes via MongoDB Change Streams (filtered by the view's current query and pagination). Updates stream in live. Users see the system churning. No refresh button. No periodic polling. The UI is a live window into the system, not a series of snapshots.

### 7. Nothing new in the kernel

All auto-generated from existing entities, roles, watches, integrations, and bootstrap entities. No `DashboardConfig` for MVP. No `AlertConfig` for MVP. No `Widget` entity for MVP. The auto-generation covers the known workloads. Future customization (configurable widgets, alert thresholds) is additive — added only when forcing functions demand it.

### 8. Simpler is better

Every widget, every view, every control has to earn its place. The default is "don't build it" until a use case demands it. The auto-generated base is minimal, self-evident, and focused on what the primitives naturally support. Decorative or speculative UI is rejected.

## What the Base UI IS

- A **real-time operational surface** users observe and interact with
- A **projection** of the system definition — entities, roles, permissions, integrations
- **Auto-generated** from primitives at platform init, regenerated as definitions change
- **Permission-scoped** by construction — users see and do only what their roles allow
- **Multi-surface** — the same operations are available via UI, CLI, API, and the assistant
- **Admin-first** — the primary user is an internal operator (FDE, admin, ops, underwriter, CSR). Customer-facing UIs (policyholder portals, agent workbenches) are separate products built on the same primitives.

## What the Base UI IS NOT

- Not a dashboard application with specialized per-org views
- Not a separate layer with its own data model
- Not a place for failure notifications or active alerting (deferred to its own design)
- Not a replacement for the CLI or API
- Not prose-heavy — no chat bubbles where tables will do
- Not decorative — no charts for their own sake

## The Rendering Contract

The base UI auto-generates from primitives. Here is what produces what:

| Area | What auto-generates | From |
|---|---|---|
| **Entity list views** | Interactive table per entity type the current role can read. Columns derived from field types. Filters from common fields. Row actions from state machine transitions + @exposed methods the role can invoke. Pagination, sort, filter built in. | Entity definitions, role permissions, role watches |
| **Entity detail views** | Form of all fields with appropriate controls. Relationship fields link to related entity detail views. Current-state badge. Transition buttons for valid transitions from the current state. Action menu for @exposed methods. Sub-tables for `has_many` relationships. Recent changes for this entity (from the changes collection). | Entity definitions, state machine, @exposed methods, permissions |
| **Queue view** | Table of pending messages targeting the current actor's roles. Columns: priority, age, summary, entity context. Sorted by priority then age. Coalesced batches render as a single row with drill-down to individual items. Row actions: claim, complete, defer. | Role watches, message_queue, coalescing config |
| **Role overview widget** | Small dashboard-style widget shown on the role landing page. Table of aggregate counts for the role: queue depth, active attentions held by actors in this role, completion rate in the last N hours, pointer to the state with longest dwell time for watched entities. | Role definition + message_queue + message_log + Attention |
| **Bootstrap entity observability** | Tables for Actors, Roles, Integrations, Runtimes, Attentions. Same auto-generation pattern as domain entities. Row actions: pause, drain, cancel, rotate credentials, close attention, transfer interaction. | Bootstrap entity definitions |
| **Pipeline metric widgets on entity views** | Table of state distribution per entity type (count per state), table of throughput (counts in time windows), table of dwell time per state (avg, p50, p95). Comparison column shows current vs baseline (historical average) where relevant. | Kernel aggregation capabilities activated on entities with state machines |
| **Integration health widget** | Table of Integrations with columns (name, provider, status, last_checked_at, recent_error_count, owner). Row actions link to Integration detail view. | Integration records + recent OTEL events keyed by integration_id |
| **Runtime observability widget** | Table of Runtimes with columns (name, kind, framework, instance_count, instances_healthy, active_sessions). Row actions: drain, scale, view instances. Drill-down to instance detail. | Runtime records + Temporal worker metrics + Attention count |
| **Cascade viewer** | Interactive navigation through messages by correlation_id. Rendered as a nested table (parent → children), click through to individual spans. No graph visualization — nested table. | OTEL traces + message_log, linked by correlation_id |
| **Assistant panel** | Persistent chat with the user's default associate, always accessible via top-bar input. Context-aware of the current view. Can execute any CLI command the user has permission for. | Default associate bound to user via `owner_actor_id`, streaming via `indemn events stream` |

Every cell in this table is kernel-provided. Adding a new entity type means every row that applies populates automatically. No per-entity UI code, ever.

## Kernel Aggregation Capabilities Required

These are reusable entity methods the kernel ships with, activated per entity type via CLI. Same pattern as `auto-classify`, `fuzzy-search`, `stale-check`.

| Capability | Returns | Backing store |
|---|---|---|
| `state-distribution` | Count per state machine value for an entity type | Entity collection (indexed query) |
| `throughput` | Completion/transition counts over configurable time windows, with comparison to baseline | message_log |
| `dwell-time` | Average, p50, p95 time spent in each state | message_log (state transition timestamps) |
| `queue-depth` | Pending message count per role | message_queue |
| `cascade-lineage` | Tree of messages for a given correlation_id | message_log + OTEL traces |

These are read-only aggregation methods. They emit no events. They're callable from CLI, API, and UI identically. The UI widgets are thin wrappers that call these methods and render the results. The assistant can call them directly as CLI commands.

## The Assistant Panel — Primary UI Decision

### Placement: slim always-visible input at the top of every view

**An always-visible assistant input in the top bar of every view** — like a search bar, primary position, persistent. This is the major UI decision of this session and deserves explicit detail.

Every view in the base UI has a top bar:
- **Left**: navigation (entity types, queue, bootstrap observability, cascade viewer)
- **Middle**: slim assistant input with a placeholder like "Ask or tell me to do something — I can do anything you can."
- **Right**: user identity + current role indicator

The input is one line, always visible, focused by keyboard shortcut (`/` or `cmd-k`) from anywhere. It doesn't eat screen real estate. It's present but not dominant.

### The conversation panel

When the user engages (clicks the input or invokes the shortcut and types), a panel slides in from the right (~400-500px wide) showing the conversation thread. Key properties:

- **Overlay, not modal.** Does not hide the current view. Users can still see their table or form. They can click things in the main view while the assistant is responding.
- **Streaming responses** visible token-by-token as the assistant generates them.
- **Inline entity renderings.** When the assistant returns entities, they render as the same interactive table/form components the rest of the UI uses. A query like "show me the oldest triaging submissions" produces a mini interactive table with the same row actions as the full list view. The assistant is not generating prose about data — it renders the data using UI components.
- **ESC closes the panel.** Conversation state persists.
- **Non-blocking.** User keeps working in the main view while the assistant thinks.

### Persistent conversation per user

Each human user has one ongoing conversation thread with their default associate. Reopening the panel shows recent context. Multi-step operational work ("show me overdue items, filter to my accounts, mark these three as escalated") works across the sequence without re-grounding every time.

### Context awareness — implicit

The UI sends a context payload with each assistant turn derived from the user's current state:

```json
{
  "view_type": "EntityDetail",
  "current_entity": {"type": "Submission", "id": "SUB-042"},
  "current_filter": null,
  "role_focus": "underwriter",
  "recent_actions": [...]
}
```

When the user types "what's blocking this?" while looking at SUB-042, the assistant's context includes "the user is looking at Submission SUB-042" and resolves "this" implicitly. No copy-paste of IDs. No awkward grounding.

The deep agent framework already supports extra context per turn. The UI builds the payload from its own state. This is a UI implementation detail, not a kernel concern.

### Real-time assistant updates

Because the conversation panel is a running harness instance — a real-time actor in the session 5 sense — it subscribes to entity events for the user's context via `indemn events stream`. When the user is discussing SUB-042 and SUB-042 changes mid-conversation, the assistant knows about it immediately.

This allows patterns like: "let me know when SUB-042 moves out of triaging" — the assistant watches and responds when the transition happens, without the user refreshing anything.

The conversation panel is just another real-time channel with a running actor, reusing the mechanism from the realtime-architecture design session.

### The complexity ladder

The assistant gives us a graceful complexity ladder across users and situations:

1. **Casual case**: click a row action. Nothing to learn. Walking into the UI, you can operate entities via buttons and forms.
2. **Pattern case**: sort/filter a table, scan for signals. A little practice. Ops users live here.
3. **Instruction case**: type into the assistant in the top bar. Natural language, no CLI syntax to learn. Medium users and any task where clicking is awkward.
4. **Power case**: open a terminal, run CLI commands directly. Full expressive power, scriptable.

Same system, four surfaces, no privileged interface. Each surface is the right weight for its user. The top-bar input threads them together — casual users never touch it, medium users use it when clicking is awkward, power users use it for rapid dispatch alongside CLI.

**A user doesn't strictly need to understand every widget to operate the system.** They can ask the assistant. Widgets exist for visibility, pattern recognition, and fast click-to-action — not exhaustive coverage. Anything the widgets don't surface well, the assistant handles.

### Why this placement vs alternatives

- **Right-side persistent panel** (Claude.ai, Cursor chat): eats screen real estate even when not needed. Present but lower weight — reads as "companion" not "primary surface." Wrong weight for "at the forefront."
- **Cmd-K command palette modal**: great for power users, bad for discoverability. Hidden behind a shortcut that many users never find. A slim visible input bar is zero-discovery and works the same way once you know the shortcut.
- **Floating corner widget**: reads as secondary tool, "help button." Wrong weight entirely.
- **Full-page assistant as home**: too much. Users need to see tables and forms while operating. Data stays primary; the assistant is adjacent, not a replacement.

The top-bar input is **visible but non-dominant**. It is present everywhere but does not demand attention. That is the correct weight for "at the forefront."

### What the assistant is NOT

- **Not Clippy-style.** It only responds when addressed. Silence is the default. No unprompted suggestions.
- **Not a replacement for the UI.** Tables, forms, queue views, state machine controls — those remain the primary data surfaces. The assistant is an input method, not a substitute.
- **Not the only conversational surface.** Users who prefer CLI-based assistants can still open a terminal and run `indemn` commands. The UI chat is one surface among several.

## Real-Time Update Filtering — Design Constraint

A table showing 1,000 submissions cannot subscribe to every Change Stream event on the submissions collection — it would flood. The rendering contract must include a subscription filter tied to the current view's filter and pagination:

- **List views** subscribe to Change Streams filtered by the current query and pagination window. When the user changes the filter or paginates, the subscription is torn down and rebuilt.
- **Detail views** subscribe to Change Streams filtered by the specific entity ID.
- **Assistant conversation panels** subscribe to events scoped to the current context (the specific entity being discussed, the relevant related entities) via scoped watches from session 5.
- **Queue views** subscribe to message_queue changes filtered by the actor's roles.
- **Bootstrap entity views** subscribe by the specific entity ID or by bootstrap entity type.

This is not a design choice being made now — it is a constraint flagged for the implementation. Spec-phase decisions will nail down the exact subscription rebuild semantics on filter change, pagination rules, and backpressure handling if the UI falls behind.

## Bootstrap Entity Observability

The six bootstrap entities (Organization, Actor, Role, Integration, Attention, Runtime) get the same auto-generation treatment as domain entities. No special treatment required beyond what the rendering contract already specifies.

This means:
- The **Runtime** entity list view shows all Runtimes with their status, instance count, framework. Detail view shows the instance list, active Attention count, linked Associates.
- The **Attention** entity list shows active attentions by actor, purpose, TTL, linked Runtime/session.
- The **Integration** list shows all Integrations with health status and last check. Detail view shows configuration, recent errors, credential management actions.
- The **Actor** list shows all actors (human and associate) with their roles and last activity.
- The **Role** list shows all roles with their permissions and watches.
- The **Organization** view is admin-only and typically only relevant to platform administrators.

Ops users can click through to inspect, pause, drain, rotate, transfer, cancel — whatever actions are exposed on each bootstrap entity. Same auto-generation from entity definitions as any other entity. Nothing special beyond inclusion in the default navigation and the role overview widget.

## Worked Examples: Three Scenarios

### Scenario 1: Stripe integration starts failing (EventGuard)

Ops opens the base UI. The landing view for an ops role shows:
- Their queue (messages targeting ops)
- A "Bootstrap Health" section: tables for Integrations, Runtimes, Attentions

The **Integrations table** shows columns (name, type, provider, status, last_checked_at, recent_errors). The Stripe Integration row now shows `status: error` with a count of recent errors derived from its OTEL span events.

Row actions on the Integration row: "View details," "Test connection," "Rotate credentials," "Pause." Ops clicks "View details" and sees the Integration detail view:
- Form of all fields
- Sub-table of recent error events from OTEL
- Buttons: re-test connection, rotate credentials, pause

Meanwhile, the **Payment entity list view** (if ops navigates there) shows payments in error state. Ops can click into a specific Payment, see its recent attempts, click through to the OTEL cascade trace for the failing span.

Live behavior: as new Payment attempts fail, the Integration's error count increments in real time via Change Stream. Ops sees the number go up.

To take action, ops has two paths:
- Click "Rotate credentials" on the Integration row
- Type into the assistant: "rotate the Stripe integration credentials" — the assistant calls `indemn integration rotate-credentials INT-STRIPE-001` with ops's permissions

Same outcome either way.

No alerts fired. No emails sent. Ops was watching the surface and saw it turn red.

### Scenario 2: Runtime instance crashes

The **Runtimes table** in ops's base UI shows a row for RUNTIME-VOICE-001 with `instances: 2/3 healthy` highlighted. Clicking into the row opens the Runtime detail view:
- Form with all Runtime fields
- Sub-table of instances, each showing (instance_id, started_at, last_heartbeat, active_sessions, health)

One instance row shows `last_heartbeat: 3m ago, health: unknown`. Row action: "Mark failed" or "Restart."

Cross-linked from the Runtime view, the **Attentions table** shows 4 active real-time session attentions. One is owned by the dead instance. It is still showing active because the heartbeat has not fully expired. Ops can click "Close" to explicitly end it, or wait for TTL expiration.

The **Interaction list view**, filtered by `runtime_id = RUNTIME-VOICE-001`, shows the affected live calls. Each row has `handling_actor_id`, `status`, and a transfer action. Ops can click "Transfer to role: senior_csr" on any affected interaction, which calls `indemn interaction transfer --to-role senior_csr`. The Runtime's bridging logic from session 5 handles the handoff.

Live behavior: as the deployment platform auto-restarts the instance, the Runtime view updates in real time — a new instance appears in the instances list with a fresh heartbeat. The count goes from 2/3 back to 3/3 without any user refresh.

### Scenario 3: JC spots a GIC bottleneck before it becomes a fire

JC opens the underwriter landing view. Top of the page:
- His queue (messages where he is targeted or unclaimed in underwriter role)
- A **Submission pipeline widget** auto-generated from Submission's state machine:

```
State            Count    Δ last hr    Avg dwell    vs. baseline
received         3        +2           12m          normal
triaging         8        +5           3h 14m       ← elevated
processing       12       +1           2d           normal
quoted           4        0            —            —
```

The "elevated" marker fell out of comparing current average dwell against the historical p50 — same aggregation capability, a second query, presented as an additional table column. No chart. Just a table with a clear signal.

JC clicks the "triaging" row. This filters the Submission list view to `state=triaging`, sorted oldest-first. The filtered list shows which submissions are stuck. For each, JC clicks into the detail view, sees the assessment, sees the linked Interactions (meetings, emails, drafts), and decides whether to act directly or reassign.

Alternative path: JC types into the assistant "show me the oldest triaging submissions and tell me what's blocking each." The assistant runs CLI queries, possibly LLM-synthesizes a summary, and renders the results as an interactive table inline in the conversation panel.

Live behavior: as submissions transition out of triaging, the pipeline widget counts decrease in real time. JC watches them drain. The bottleneck clears.

JC caught it while drinking coffee. No alert. No page. No dashboard app. Just the base UI being the system's live surface.

## What's Decided

1. Pipeline Dashboard and Queue Health collapse into the base UI itself. Not two features — one operational surface.
2. The base UI is a projection of the system definition, not an application on top of it. UI derives from entities, roles, watches, permissions, integrations.
3. Auto-generated from primitives. No bespoke per-org dashboards for MVP.
4. No new kernel entities for dashboards, alerts, or widgets in MVP. `Widget`, `DashboardConfig`, `AlertConfig` deferred until forcing functions demand them.
5. Visualization preference: tables > charts > prose. Charts reserved for data inherently graphical (rare). Tables default. No decoration for its own sake.
6. Interactive tables are the primary data surface. Row actions, sort, filter, drill-down, take-action.
7. Forms auto-generated from entity definitions for create/update. Field types map to controls. State machine rendered as current-state + transition buttons, not a diagram.
8. **Assistant at the forefront**: slim always-visible input at the top of every view, like a search bar. Expands to overlay conversation panel on engagement. Streaming responses, inline entity renderings, non-blocking.
9. Default associate per human actor (via `owner_actor_id` binding from session 5) provides the assistant. Permissions match the user. Can execute any CLI command the user has access to.
10. Assistant is context-aware of the current view — implicit, via UI-built context payload per turn. The user does not need to explicitly reference the current entity.
11. Persistent conversation thread per user. Reopens to recent state. Multi-step work is supported without re-grounding.
12. Real-time updates via MongoDB Change Streams filtered by current view query and pagination. Subscription must be filter-aware and pagination-aware to avoid flooding.
13. Assistant panel is a running harness instance subscribing to `indemn events stream` for scoped events — reuses the real-time mechanism from session 5.
14. Bootstrap entities (Org, Actor, Role, Integration, Attention, Runtime) get the same auto-generation as domain entities. Ops users see them as normal tables with row actions. No special treatment.
15. Kernel aggregation capabilities required: `state-distribution`, `throughput`, `dwell-time`, `queue-depth`, `cascade-lineage`. All read-only, all reusable, all callable from CLI/API/UI identically.
16. Active alerting deferred. Base UI visibility is enough for MVP. Human ops watches the dashboard. Active alerts added later when forcing functions and known thresholds justify the design.
17. CLI commands for observability are auto-generated from kernel entities (Message, Attention, Runtime, Integration) or are thin wrappers around the aggregation capabilities — same auto-generation as domain entity CLI.
18. The assistant gives a graceful complexity ladder: click → pattern-match → instruct → command. Same system, four surfaces, no privileged interface.

## What's Deferred

### To spec phase (not blocking)

- Exact UI component library choice (React-based is assumed but unspecified)
- Styling conventions, color palette, typography
- Keyboard shortcut specifics (which key binds to what)
- Pagination size defaults
- Responsive behavior (mobile, tablet)
- Accessibility conformance
- Export formats (CSV download, PDF export, etc.)
- Assistant panel exact dimensions, animation, positioning

### To future design (when forcing functions appear)

- **`Widget` or `DashboardConfig` entity** — for per-org customization of the default view. Craig flagged this as expected eventually. Deferred until multiple orgs need the same shape of custom dashboard.
- **`AlertConfig` and active alerting** — for automated notifications on thresholds. Probably built as watches on kernel entities (Runtime, Integration, message_queue depth) with actions that invoke notification Integrations. Full design when ops demands it and we have enough data to know the right thresholds.
- **Customizable widgets per-role** — when admins want to reorder or hide default widgets without writing code. Expected second wave.
- **Cross-entity custom views** — when a specific use case needs "submissions joined with quotes joined with pending drafts for underwriters" as a dedicated view. Probably manifests as a custom widget or a saved query.

### To separate UX design work (non-architectural)

- Assistant panel exact visual design (size, position, animation)
- Input placeholder text, empty state design
- How inline entity renderings are visually distinguished from prose responses
- How context-awareness is indicated to the user (does the UI show "Assistant knows: SUB-042"?)
- How streaming is indicated visually
- How the assistant expresses uncertainty, permission errors, or dry-run previews

## Relationship to Prior Decisions

- **Session 5 default chat assistant baked into base UI** (INDEX.md 2026-04-10) — this artifact formalizes that the assistant is the primary input surface, not a secondary helper, and defines its placement and integration into the rendering contract.
- **Session 5 Attention bootstrap entity** — assistant panel sessions use Attention the same way voice/chat harnesses do. One unified mechanism for "an actor is currently doing something in this session."
- **Session 5 Runtime bootstrap entity** — the assistant panel is a running instance of a chat-kind Runtime (or integrated into an existing runtime). Same deployment model as any real-time harness.
- **Session 5 scoped watches and `indemn events stream`** — the mechanism for delivering real-time events to the assistant panel and to UI views filtered by the user's context.
- **Session 5 CLI and API as parallel auto-generated surfaces** — the base UI uses the API, CLI remains available for power users, the assistant uses the CLI via subprocess, same permissions enforced across all three.
- **Session 5 base-ui-and-auth-design** (initial sketch) — this artifact supersedes the base UI portion of that artifact. The auth portion remains separate and is item 10 (still open for its own design session).
- **Session 6 bulk operations pattern** — bulk operations surface in the base UI via two paths: (1) the assistant (users can say "mark all overdue action items") and (2) auto-generated bulk CLI commands accessible through entity list view action menus ("Bulk Transition Selected" on a multi-select table).

## Open Follow-Ups (Not Blocking Architecture)

- **Contextual awareness indicator in the UI.** When the user types something context-dependent ("this," "these," "mine"), should the UI visually surface what context the assistant is using? A small "Context: SUB-042" hint next to the input? UX detail.
- **Multi-window / multi-tab behavior.** If a user opens SUB-042 in one tab and SUB-099 in another, which is the assistant's "current context"? Per-tab conversation? One conversation shared across tabs? UX + implementation detail.
- **Widget ordering on role landing pages.** The default set of widgets the base UI shows — queue, pipeline metrics, bootstrap health — is in some order. That order is a UX call. MVP: alphabetical or kernel-defined default. Post-MVP: per-role configuration.
- **Assistant interruption semantics.** Can a user interrupt a running assistant turn? Cancel a long-running operation the assistant started? These are UX + harness implementation details, not architecture.

## Summary

The base UI is the system made visible. It is the real-time operational surface every human actor uses to observe, interact with, and operate the OS. It is not designed — it is derived. Every element is a projection of primitives that already exist.

The assistant at the forefront is the architectural payoff: natural-language operation of the entire OS from day one, with zero incremental kernel work. It unlocks the complexity ladder from casual-click to power-command without privileged interfaces or hidden shortcuts.

Pipeline Dashboard and Queue Health do not exist as separate features. They are the base UI, with its auto-generated widgets on entity views and its bootstrap entity observability on role landing pages. Items 8 and 9 are resolved.
