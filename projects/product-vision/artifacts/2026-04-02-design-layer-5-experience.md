---
ask: "How does the experience layer work — UI, real-time updates, HITL, consumer-facing surfaces?"
created: 2026-04-02
workstream: product-vision
session: 2026-03-30-a
sources:
  - type: conversation
    description: "Craig and Claude design session, 2026-04-02"
  - type: local
    description: "Ryan's wireframes — retail agency (4 screens) + GIC wholesaler (2 new)"
---

# Design: Layer 5 — Experience Layer

## Core Principle: UI Is a Visual Layer on Entity Queries

The UI calls the same API endpoints that the CLI calls and associates use. No separate data layer. One source of truth. The entity framework provides all the data the UI needs.

Ryan's wireframes map directly to entity operations. The Indemn team uses the CLI (with Claude Code or other agentic tools) for maximum productivity. The customer-facing UI renders the same data visually.

## Four Types of Human Users

| User | What They See | Priority |
|------|-------------|----------|
| **Indemn team** | Auto-generated admin UI + CLI | MVP — needed from day one |
| **Insurance professionals (customers)** | Configurable views per Ryan's wireframes | Vision — built after MVP |
| **Tier 3 developers** | CLI + API + developer portal | Vision — built with Tier 3 |
| **End consumers** | Embedded widgets, voice agents, landing pages | Deployment entities — some exist already |

## Wireframe-to-Entity Mapping

| Wireframe View | Customer Type | Primary Entity | Query |
|---------------|--------------|----------------|-------|
| Pipeline | Retail agency | Insured | Active customers with open work |
| Submission Queue | Wholesaler/MGA | Submission | Active submissions by status |
| Customer Workspace | Retail agency | Insured | One customer — policies, submissions, interactions |
| Risk Record | Wholesaler/MGA | Submission | One submission — lines, quotes, documents, interactions |
| Line Workstream | Both | SubmissionLine | LOB-specific application + quoting |
| Carrier Workstream | Both | Interaction | Thread with one carrier on one submission |

The wholesaler view is a CONFIGURATION of the retail view — same components, different primary entity, different column arrangement. One UI codebase serves both through view configuration.

## View Configuration Entity

```python
class ViewConfig(Entity):
    sub_domain = "platform"

    name: str                    # "Pipeline", "Submission Queue"
    view_type: str               # "list", "detail", "workstream"
    primary_entity: str          # "insured", "submission", "policy"
    columns: list[dict]          # For list views — fields, labels, sort
    panels: list[dict]           # For detail views — panel layout
    actions: list[str]           # @exposed methods shown as buttons
    filters: dict                # Default filters
    role_visibility: dict        # Which roles see this view

    class Settings:
        name = "view_configs"
```

```bash
# Configure views per customer type
indemn view-config create --name "Pipeline" --view-type list \
  --primary-entity insured --columns @configs/retail-pipeline.json

indemn view-config create --name "Submission Queue" --view-type list \
  --primary-entity submission --columns @configs/wholesaler-queue.json
```

Role-based visibility (the team's discussion about who sees what) is configured through `role_visibility` on the ViewConfig entity. An agent sees their book. An underwriter sees their queue. An admin sees everything. Configured, not coded.

## Real-Time Updates

Architecture baked in from the start:

```
Entity state changes → event emitted via RabbitMQ
    → WebSocket service subscribes to relevant events
    → Pushes updates to connected UI clients
    → UI re-renders affected components
```

User watching the Submission Queue sees a submission move from "processing" to "quoted" in real time — because the associate that processed it triggered an entity state change → event → WebSocket → UI update.

This scales: as the UI improves over time, the real-time foundation is already there. No retrofit needed.

## Human-in-the-Loop via Draft Entity

No special HITL mechanism. The Draft entity IS the collaboration point between associates and humans:

1. Associate creates a Draft: `indemn draft create --type carrier-response --submission SUB-001 --body "..."`
2. Draft appears in UI as a pending action item
3. Human reviews, edits if needed
4. Human approves or rejects: `indemn draft transition DRAFT-001 --to approved`
5. If approved → system sends the communication via channel adapter
6. If rejected → associate is notified or human writes their own

The Draft lifecycle: `generated → pending_review → approved/rejected/edited → sent`

This works for any HITL scenario — email responses, underwriting decisions, binding approvals, document reviews. The Draft entity has a `type` field that determines what kind of review it is.

## Auto-Generated Admin UI (MVP)

For the Indemn team from day one — basic admin interface auto-generated from entity definitions:

- **Entity list views** — filterable, sortable tables for any entity
- **Entity detail views** — forms showing all fields, relationships, state
- **State machine visualization** — see current state, available transitions, click to transition
- **Relationship navigation** — click through from Policy → Insured → Agency
- **Event log** — see entity events in chronological order
- **Associate monitoring** — status, last invocation, recent activity

Auto-generated means: when a new entity is added to the OS, it automatically appears in the admin UI. Same auto-discovery pattern as API and CLI. No manual UI work needed per entity.

Technology: React app that reads entity schemas from the API metadata endpoint and renders generic forms/tables. Like Django admin but for the OS.

The Indemn team pairs this with CLI + Claude Code for maximum productivity. Admin UI for visual monitoring and quick actions. CLI for power operations and automation.

## Customer-Facing UI (Vision, Not MVP)

Built after MVP. Based on Ryan's wireframes. The entity framework and real-time architecture provide all the infrastructure.

Key components (from Ryan's component inventory — 34 components across levels):
- **Universal** — same for all customer types (navigation, notifications)
- **Configurable** — operator sets parameters (column layout, default filters)
- **Custom** — requires Indemn engineering (specialized visualizations)

The ViewConfig entity handles universal and configurable components. Custom components are built as needed for specific customer requirements.

## Consumer-Facing Surfaces (Deployment Entities)

End consumers interact through surfaces deployed by the OS:

```python
class Deployment(Entity):
    sub_domain = "distribution_delivery"

    program: Link["Program"]
    partner: Optional[Link["DistributionPartner"]]
    surface_type: str           # "web-embed", "landing-page", "voice-endpoint", "outlook-addin"
    surface_config: dict        # Widget type, branding, behavior
    associate: Link["Associate"]  # Which associate powers this surface
    status: Literal["configured", "staging", "live", "paused", "decommissioned"]

    class Settings:
        name = "deployments"
```

```bash
# Deploy a quote widget on a partner website (EventGuard pattern)
indemn deployment create --program PROG-001 --partner PARTNER-001 --surface-type web-embed
indemn deployment configure DEP-001 --widget @widget.json --branding @partner-branding.json
indemn deployment associate DEP-001 --associate quote-bind-associate
indemn deployment activate DEP-001
# → generates embed code, connects associate, starts serving
```

This is how EventGuard's 351 venue pages would work on the OS — each venue is a Deployment entity with venue-specific branding and a Quote & Bind associate. Created and managed via CLI. At scale, an associate or script creates hundreds of deployments programmatically.

Surface types:
- **Web embed** — chat widget, quote form, application form embedded on partner sites
- **Landing page** — standalone pages (like EventGuard venue pages) deployed and hosted
- **Voice endpoint** — phone number routed to a voice associate
- **Outlook add-in** — embedded in email client (the GIC pattern)
- **SMS endpoint** — phone number for text-based interaction

All are Deployment entities. All managed via CLI. All powered by associates.

## Key Layer 5 Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI architecture | Visual layer on entity API — same endpoints as CLI/associates | One source of truth. No separate data layer. |
| View configuration | ViewConfig entity — CLI-creatable, per customer type | Configurable without code changes. Role-based visibility. |
| Real-time | Entity events → RabbitMQ → WebSocket → UI | Baked into architecture from day one. Scales with UI improvements. |
| HITL | Draft entity lifecycle | No special mechanism. Same entity patterns as everything else. |
| Admin UI (MVP) | Auto-generated from entity schemas | Same auto-discovery as API/CLI. Works from day one. Indemn team uses alongside CLI. |
| Customer UI (vision) | React, follows Ryan's wireframes | Built after MVP. Entity framework provides all data. |
| Consumer surfaces | Deployment entity | CLI-creatable. Associates power the interaction. EventGuard pattern at scale. |
| Role-based access | ViewConfig.role_visibility + entity permissions | Who sees what is configuration, not code. |
