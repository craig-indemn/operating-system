# Notes: 2026-03-30-vision-session-2-checkpoint.md

**File:** projects/product-vision/artifacts/2026-03-30-vision-session-2-checkpoint.md
**Read:** 2026-04-16 (full file — 208 lines)
**Category:** session-checkpoint

## Key Claims

- Session 2 established "Operating System for Insurance" framing (vs earlier "factory/lab").
- Consolidates 7 session-2 artifacts: the-operating-system-for-insurance, why-insurance-why-now, platform-tiers-and-operations, associate-architecture, entity-system-and-generator, plus v1 vision docs.
- Vision is substantially complete; next phase is design.
- Craig: vision → design → implementation → priorities → roles → time → execution → roadmap.
- Late additions: CRM/AMS as core OS capability, build vs buy decision (build from scratch, use MongoDB not Postgres), entity generator as OS kernel, product configuration vs custom entities (users don't create new entities, OS provides complete domain model), SMS via Twilio.

## Architectural Decisions

- **MongoDB (not Postgres)** — "team already uses it everywhere, document model fits insurance's inherent field variability."
- **Build from scratch**, don't adopt CRM framework.
- **Generator as OS kernel** — declarative entity definition → auto-generate everything.
- **Skills serve three audiences** — AI associates, Tier 3 developers, engineers.
- **Product configuration vs custom entities** — OS provides complete domain model; users configure, don't create new entities (with Tier 3 exception).
- **Dog-food the OS for Indemn's own CRM** — first customer is Indemn itself.

## Layer/Location Specified

- No new layer specifications beyond what's in the 7 summarized artifacts.
- Confirms: modular monolith, MongoDB, generator kernel.
- Still pre-dates harness pattern (Session 5) and "everything is data" (Session 4).

## Dependencies Declared

- Same as summarized artifacts: Beanie/MongoDB, FastAPI, Typer, RabbitMQ (later changed), Claude Code, LangFuse.

## Code Locations Specified

- None specific; references the 7 summarized artifacts.

## Cross-References

- All 7 session-2 artifacts (already read in manifest or being read).
- vision/2026-03-25-the-vision.md + vision-v1.md.
- context/ stakeholder docs.

## Open Questions or Ambiguities

Listed in artifact: Tier 3 pricing, website alignment, product showcases, customer migration, competitive positioning, revenue projections.

**Session checkpoint. Summarizes session 2 outputs. No new architectural-layer claims beyond the summarized artifacts. Next phase: design.**
