# Notes: 2026-04-11-base-ui-operational-surface.md

**File:** projects/product-vision/artifacts/2026-04-11-base-ui-operational-surface.md
**Read:** 2026-04-16 (full file — 366 lines)
**Category:** design-source

## Key Claims

- Resolves items 8 (Pipeline Dashboard) and 9 (Queue Health) from post-trace synthesis. They collapse into the base UI itself — "not two features — one operational surface."
- **Base UI is a projection of the system definition**, not an application on top of it. UI derives from entities, roles, watches, permissions, integrations.
- Rendering contract: every UI element auto-generates from primitives at platform init, regenerates as definitions change.
- **Tables > charts > prose.** Charts reserved for data inherently graphical (rare). Tables are the primary interactive surface.
- Forms auto-generated from entity definitions; state machine shown as current-state + transition buttons, NOT a diagram.
- **Assistant at the forefront**: slim always-visible input at top of every view, persistent — "like a search bar, primary position."
- Assistant panel is a RUNNING HARNESS INSTANCE subscribing to `indemn events stream` for scoped events — reuses the real-time mechanism from session 5 (realtime-architecture-design).
- Assistant's permissions exactly match the user's (via `owner_actor_id` binding to user's default associate).
- "The assistant can execute any CLI command the user has access to."
- Real-time by default via MongoDB Change Streams filtered by current view query and pagination.
- Bootstrap entities (Org, Actor, Role, Integration, Attention, Runtime) use the SAME auto-generation as domain entities. No special treatment.
- Kernel aggregation capabilities: `state-distribution`, `throughput`, `dwell-time`, `queue-depth`, `cascade-lineage`. Read-only, reusable, callable from CLI/API/UI identically.
- No new kernel entities for dashboards, alerts, or widgets in MVP. `Widget`, `DashboardConfig`, `AlertConfig` deferred.
- Complexity ladder: click → pattern-match (sort/filter) → instruct (assistant) → command (CLI). Same system, four surfaces, no privileged interface.
- "A user doesn't strictly need to understand every widget to operate the system. They can ask the assistant."

## Architectural Decisions

- **UI derives from the system**: entities + roles + watches + permissions + integrations define what the UI shows.
- No bespoke per-org dashboards at MVP.
- Adding a domain entity means UI reflects it immediately. Changing permissions changes what the role can see and do.
- Auto-generation is the ONLY UI construction path for MVP. Future customization is additive.
- **Assistant is always-visible, top-bar input** — not sidebar, not modal, not floating widget, not full-page home. "Visible but non-dominant."
- Assistant panel: overlay, not modal (does not hide current view). Streaming responses. Inline entity renderings using same UI components as rest of the app. ESC closes. Persistent conversation per user.
- Context-awareness: UI sends context payload per assistant turn (view_type, current_entity, current_filter, role_focus, recent_actions). Implicit grounding of "this" etc.
- Assistant panel is a running HARNESS INSTANCE, receiving scoped events via `indemn events stream`. "The conversation panel is just another real-time channel with a running actor, reusing the mechanism from the realtime-architecture design session."
- Real-time update filtering is a design constraint: subscription rebuilt on filter change / pagination change. Flagged for implementation spec.

## Layer/Location Specified

**THIS ARTIFACT DIRECTLY TIES THE ASSISTANT TO THE HARNESS PATTERN.**

Critical claims (line 167, 306, 346-347):
- "Because the conversation panel is a running harness instance — a real-time actor in the session 5 sense — it subscribes to entity events for the user's context via `indemn events stream`."
- "The conversation panel is just another real-time channel with a running actor, reusing the mechanism from the realtime-architecture design session."
- "The assistant panel is a running instance of a chat-kind Runtime (or integrated into an existing runtime). Same deployment model as any real-time harness."

This explicitly places the assistant's execution in a **chat-kind Runtime harness instance**, running outside the kernel. NOT in the API server. NOT as a stripped-down endpoint. It is a harness following the pattern from the realtime-architecture-design artifact.

**The kernel's role for the assistant:**
- Provides the user's default associate entity (with `owner_actor_id` bound to the user)
- Provides the CLI the assistant calls
- Provides `indemn events stream` for scoped real-time updates
- Handles the user's session JWT (injected into the assistant's harness per auth design line 463-482)
- Provides Change Streams for live UI updates

**The harness's role for the assistant:**
- Runs the deep agent / LLM loop
- Calls `execute_command` (or equivalent) to invoke CLI commands
- Subscribes to `indemn events stream` for scoped events
- Streams responses back to the UI (via WebSocket to the chat runtime)
- Manages the conversation thread state

**Rendering contract table (line 91-103)** — each cell auto-generates from primitives:
- Entity list views from entity definitions + role permissions + role watches
- Entity detail views from entity definitions + state machine + @exposed methods + permissions
- Queue view from role watches + message_queue + coalescing config
- Role overview widget from role definition + message_queue + message_log + Attention
- Bootstrap entity observability (Actors, Roles, Integrations, Runtimes, Attentions)
- Pipeline metric widgets from kernel aggregation capabilities
- Integration health widget from Integration records + OTEL
- Runtime observability widget from Runtime records + Temporal worker metrics + Attention count
- Cascade viewer from OTEL traces + message_log
- **Assistant panel**: "Persistent chat with the user's default associate, always accessible via top-bar input. Context-aware of the current view. Can execute any CLI command the user has permission for."

**Kernel aggregation capabilities** are kernel code activated per entity type via CLI (same pattern as `auto-classify`, `fuzzy-search`, `stale-check`).

## Dependencies Declared

- MongoDB Change Streams (for real-time UI updates)
- React-based UI component library (assumed but unspecified)
- `indemn events stream` (for scoped real-time event delivery to assistant panel harness)
- OTEL traces + message_log (for cascade viewer, throughput, dwell-time)
- Temporal worker metrics (for Runtime observability widget)
- Entity framework (for auto-generation)
- Role framework (for permission-based rendering)
- Default associate + `owner_actor_id` (for assistant panel)

## Code Locations Specified

- **Base UI codebase**: React-based (assumed). No specific paths. "Kernel-provided" is the framing.
- **Kernel aggregation capabilities**: kernel code, activated per entity via CLI.
- **Assistant panel harness**: a chat-kind Runtime instance (per realtime-architecture-design). NOT in the kernel. NOT in the API server. A harness image.
- **UI components** (interactive tables, forms, queue views) are auto-generated per entity — not custom-coded per entity type.
- The artifact explicitly says: "Adding a new entity type means every row that applies populates automatically. No per-entity UI code, ever."

## Cross-References

- 2026-04-10-bulk-operations-pattern.md (bulk ops surface in UI via assistant + auto-generated CLI)
- 2026-04-10-base-ui-and-auth-design.md (initial sketch — this artifact supersedes the UI portion)
- 2026-04-10-gic-retrace-full-kernel.md (surfaced pipeline dashboard + queue health)
- 2026-04-10-realtime-architecture-design.md (provides Attention, scoped watches, Change Streams, harness pattern)
- 2026-04-10-post-trace-synthesis.md (items 8 and 9)
- 2026-04-11-authentication-design.md (auth portion — handles default assistant's user session inheritance)

## Open Questions or Ambiguities

From the artifact itself (Open Follow-Ups):
- Contextual awareness indicator in UI (should UI show "Context: SUB-042" next to input?)
- Multi-window/multi-tab behavior (per-tab conversation? shared?)
- Widget ordering on role landing pages (MVP: alphabetical; post-MVP: per-role config)
- Assistant interruption semantics (can user cancel a running assistant turn?)

Deferred:
- UI component library choice (React-based assumed but unspecified)
- Styling conventions, keyboard shortcuts, pagination defaults
- Responsive behavior (mobile, tablet)
- Accessibility conformance
- Export formats
- Future `Widget` / `DashboardConfig` / `AlertConfig` entities

**Pass 2 critical observation:**
- **This artifact is the second independent confirmation of Finding 0's architectural claim.** The assistant MUST be a harness instance per this design. Current implementation has `kernel/api/assistant.py` — a stripped-down endpoint inside the API server process that streams text from Claude WITHOUT tools and WITHOUT the harness pattern. Per this design, that's architecturally wrong: the assistant should be a chat-runtime harness instance that the user's browser connects to (via WebSocket, per realtime-architecture-design), NOT an endpoint in the kernel's API server.
- **Kernel aggregation capabilities** should be verifiable in code: state-distribution, throughput, dwell-time, queue-depth, cascade-lineage. Per comprehensive audit: state_distribution + queue_depth in `aggregations.py` + `admin_routes.py` — CONFIRMED PRESENT.
- **Tables-over-charts discipline** is a UI behavioral expectation, checkable by reviewing the UI code (no chart components for things that should be tables).
- **Auto-generated-only discipline** is checkable by reviewing UI code (no per-org or per-entity custom UI code).

**The assistant-as-harness claim from this artifact + the assistant-via-harness-JWT claim from auth design + the three-harness-images claim from realtime-architecture = THREE independent statements that agent execution (including the assistant) lives in harness images outside the kernel.** Finding 0 is not a single-artifact claim; it's a cross-artifact consistent design that the implementation violates.
