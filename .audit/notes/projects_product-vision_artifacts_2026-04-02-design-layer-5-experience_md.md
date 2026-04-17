# Notes: 2026-04-02-design-layer-5-experience.md

**File:** projects/product-vision/artifacts/2026-04-02-design-layer-5-experience.md
**Read:** 2026-04-16 (full file — 182 lines)
**Category:** design-source (Layer 5 early — experience layer)

## Key Claims

- **UI is visual layer on entity queries** — same API endpoints as CLI + associates. No separate data layer.
- Four types of human users: Indemn team (MVP), Insurance professionals (vision), Tier 3 developers (vision), End consumers (deployment entities).
- Wireframes (Ryan's) map directly to entity operations. Wholesaler view = configuration of retail view (same components, different primary entity).
- **ViewConfig entity** — CLI-creatable, per customer type. `role_visibility` field for role-based access.
- Real-time: Entity events → RabbitMQ → WebSocket → UI updates (NOTE: RabbitMQ later replaced with MongoDB Change Streams).
- **HITL via Draft entity lifecycle** — no special mechanism. `generated → pending_review → approved/rejected/edited → sent`.
- Auto-generated admin UI (MVP) — React app reading entity schemas from metadata endpoint.
- Customer-facing UI (vision, post-MVP).
- **Consumer-facing surfaces via Deployment entity** — web embed, landing page, voice endpoint, Outlook add-in, SMS endpoint.

## Architectural Decisions

- **One source of truth** — UI uses same API as CLI and associates.
- **ViewConfig as CLI-configurable entity** (later NOT implemented — superseded by auto-generation from entity definitions only; per white paper, "no custom UI code per entity or per org" and ViewConfig deferred as DashboardConfig/AlertConfig/Widget post-MVP).
- **Real-time via RabbitMQ** (this stage) — later REPLACED by MongoDB Change Streams per 2026-04-11-base-ui-operational-surface.md.
- **Draft entity for HITL** — no separate HITL mechanism.
- **Auto-generated admin UI** — later formalized as the Base UI (2026-04-11-base-ui-operational-surface.md).
- **Deployment entity for consumer surfaces** — retained in the final architecture.

## Layer/Location Specified

- UI code separate from kernel (consumes API).
- React app reading API metadata endpoint for auto-generation.
- WebSocket service as real-time push layer (at this stage, separate service listening to RabbitMQ).
- Customer-facing UI deferred.

**Later evolution:**
- ViewConfig as separate entity → dropped; auto-generation from entity definitions covers all cases, customization deferred.
- RabbitMQ for real-time → replaced by MongoDB Change Streams.
- "Live" surfaces via Deployment entity → retained.

## Dependencies Declared

- React, REST/GraphQL API.
- RabbitMQ (later Change Streams).
- WebSocket service.
- Ryan's wireframes (34 components across levels).

## Code Locations Specified

- Admin UI in separate React app ("like Django admin but for the OS").
- WebSocket service separate from API.

Later resolved:
- UI in `ui/src/` (React + Vite).
- WebSocket integrated into kernel API (`kernel/api/websocket.py`).

## Cross-References

- Ryan's wireframes (retail agency, GIC wholesaler).
- Later: 2026-04-11-base-ui-operational-surface.md (SUPERSEDES the UI portion, drops ViewConfig as separate entity).
- 2026-04-10-realtime-architecture-design.md (real-time mechanism refined with harness pattern + Change Streams).

## Open Questions or Ambiguities

- Should ViewConfig be a first-class entity or handled via auto-generation from role? — later resolved: pure auto-generation for MVP.
- Real-time architecture — later refined.

**No Finding 0-class deviation.** UI-as-API-consumer principle retained; ViewConfig abstraction deferred; real-time moved from RabbitMQ to Change Streams. Implementation matches the later refinements.
