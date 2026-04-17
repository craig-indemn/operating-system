# Notes: 2026-04-02-implementation-plan.md

**File:** projects/product-vision/artifacts/2026-04-02-implementation-plan.md
**Read:** 2026-04-16 (full file — 211 lines)
**Category:** design-source (early implementation plan — pre-primitives-resolved)

## Key Claims

- Arc: Craig's personal OS → Indemn's company OS → Customer's insurance OS. Same framework at every scale.
- 6 phases (at this stage):
  - **Phase 0**: Development framework (CLAUDE.md, skills, conventions)
  - **Phase 1**: Core framework (base Entity class, mixins, @exposed, auto-registration)
  - **Phase 2**: Complete entity vertical (9 parallel sessions across sub-domains)
  - **Phase 3**: Associate runtime + integration adapters
  - **Phase 4**: Indemn runs on the OS (internal dog-fooding)
  - **Phase 5**: First external customer
- Timeline: ~4-6 weeks.
- 10+ parallel Claude Code sessions enabled by framework.
- Deep agents + OS CLI in sandbox (Daytona evaluation).

## Architectural Decisions

- **Phase 0 precedes all code** — conventions must exist before 10+ parallel sessions write code.
- **Mixin-based Entity** (StateMachineMixin, EventMixin, PermissionsMixin, AutoRegisterMixin) — later SUPERSEDED by 2026-04-02-core-primitives-architecture.md ("One Entity class with uniform capabilities, configuration-driven activation. No mixins.").
- **Phase 2 parallel sessions** by sub-domain (A-I: Core Insurance, Risk & Parties, Submission & Quoting, Policy Lifecycle, Financial, Distribution & Delivery, Platform-Agents, Platform-Operations, Reference Tables).
- **RabbitMQ event bus** — later superseded by MongoDB messages.
- **Phase 4 = Indemn runs on OS** — dog-fooding.
- **Phase 5 = first external customer** — the Series A proof.

**Phase numbering evolution:**
- This artifact: 6 phases (0-5).
- Final white paper: 8 phases (0-7).
- Final phase numbering differs because the architecture evolved:
  - Phase 2 (this artifact = entity vertical) → split into Phase 1 (kernel framework) + Phase 6 (dog-fooding) in the final.
  - Phase 3 (this artifact = associates + integrations) → split into Phase 2 (associate execution) + Phase 3 (integrations) in the final.
  - Phase 4 (this artifact = Indemn on OS) → became Phase 6 (dog-fooding) in the final.
  - Phase 5 (this artifact = first external customer) → became Phase 7 in the final.
  - NEW in final: Phase 4 (Base UI), Phase 5 (Real-Time — harness pattern).

## Layer/Location Specified

- Modular monolith, one deployable unit — RETAINED in final.
- Repository structure (core/, domains/, api/, cli/, skills/) — later changed to (kernel/, kernel_entities/, seed/, ui/, tests/).
- Auto-generated admin UI served as React app — RETAINED (now `ui/src/`).
- **No explicit kernel/harness boundary at this stage** — pre-dates harness pattern (Session 5).

## Dependencies Declared

- Beanie, FastAPI, Typer, RabbitMQ, LangChain deepagents, Daytona sandbox.

## Code Locations Specified

- Repository structure: core/, domains/, api/, cli/, skills/ — later changed.
- Per-sub-domain organization — later changed to kernel/kernel_entities split.

## Cross-References

- Supersedes/foreshadows:
  - 2026-04-02-core-primitives-architecture.md (same day, contradicts mixin approach)
  - Phase structure later resolved in 2026-04-13-white-paper.md § 11 (build sequence) — 8 phases
  - 2026-04-14 consolidated specs — implement the 8-phase structure

## Open Questions or Ambiguities

- Mixin vs uniform Entity class — resolved same day in core-primitives-architecture.md (uniform).
- RabbitMQ vs MongoDB for messages — resolved same day in core-primitives-architecture.md (MongoDB).
- Daytona vs local Docker for sandbox — later resolved: Daytona candidate but implementation has no sandbox (Finding 0 consequence).

**No Finding 0-class deviation from this artifact specifically.** It's a phasing plan that was later refined to the 8-phase structure. The current implementation follows the refined 8-phase structure. This artifact's "Phase 3 = associate runtime + integrations" became the final Phase 2 + Phase 3 — also consistent with how things were built.
