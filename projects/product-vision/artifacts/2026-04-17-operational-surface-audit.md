---
ask: "Systematic operational surface audit — verify every CLI command, API endpoint, and observability path from the design actually exists in the implementation. Surfaced after deployment shakeout found gaps the 4-pass audit missed."
created: 2026-04-17
workstream: product-vision
session: 2026-04-17-a
sources:
  - type: codebase
    ref: "/Users/home/Repositories/indemn-os"
    description: "Every subsystem checked for real implementation (not stubs)"
  - type: artifact
    ref: "2026-04-16-vision-map.md"
    description: "Design claims cross-referenced against code"
  - type: artifact
    ref: "Consolidated specs (Phase 0-1, 2-3, 4-5)"
    description: "CLI commands and API endpoints referenced in specs"
---

# Operational Surface Audit

**Date:** 2026-04-17
**Context:** During deployment shakeout of the async harness (Track A), multiple operational gaps were found that the 4-pass audit missed. The audit verified mechanisms and architecture but didn't verify that every designed CLI command, API endpoint, and observability path existed as working code. This audit closes that gap.

## Methodology

1. Extracted every `indemn` CLI command referenced in design artifacts (vision map, white paper, remaining-gap-sessions, consolidated specs, harness draft)
2. Listed every actual CLI command and subcommand via `indemn --help`
3. Cross-referenced design vs reality
4. Deep-explored all 15 kernel subsystems for real implementation (not stubs)
5. Identified gaps at each surface level: mechanism, API, CLI, E2E

## Finding: All 15 Kernel Subsystems Implemented

Every kernel subsystem has real, working logic — not stubs:

1. Entity framework (factory + registration + auto-generation)
2. save_tracked (atomic transaction: entity + changes + watches)
3. Watch system (evaluator + cache with 60s TTL + scope resolution)
4. Rule engine (conditions + lookups + group status + veto)
5. State machine (validated transitions, _state_field_name)
6. Auth (JWT + opaque service tokens + rate limiting + revocation cache)
7. Org lifecycle (clone/diff/deploy/export/import)
8. Schema migration (rename/add/remove with batching + dry-run)
9. Bulk operations (per-batch transactions, error classification)
10. Integration adapters (Outlook + Stripe, credential chain, retry)
11. Observability (OTEL spans + structured JSON logging)
12. Queue processor (sweep loop, scheduled associates, zombie detection)
13. Temporal client (Cloud + local, API key + TLS)
14. Seed loading (YAML with org_id scoping, idempotent)
15. Capability system (@exposed decorator, auto-registered routes)

## Gaps Found During Deployment Shakeout (Fixed in Session)

These were found and fixed during the Track A deployment:

| Gap | Root cause | Fix |
|---|---|---|
| Runtime register-instance + heartbeat endpoints | @exposed methods not on Runtime entity | Added as @exposed methods |
| Service token creation endpoint | No API endpoint for harness provisioning | Added POST /api/_platform/service-token |
| Queue complete/fail CLI commands + API endpoints | Standard queue verbs not implemented | Added CLI commands + API endpoints |
| Auth middleware: opaque service tokens | Only JWT path existed | Added indemn_ prefix detection + hash lookup |
| add-role accepts actor_id | Only email lookup, service actors have no email | Extended to accept actor_id |
| ObjectId coercion for kernel entities | Coercion only handled relationship targets | Generic coercion via Pydantic field annotations |
| Harness CLI calls: associate → actor | CLI has actor, not associate command | Fixed in harness code |
| Harness CLI calls: entity slug singular | CLI registers as entity_name.lower(), not plural | Fixed in harness code |
| Harness CLI: --json auto-append | CLI outputs JSON by default, flag not accepted | Removed auto-append |
| Temporal graceful_shutdown_timeout | Newer temporalio requires timedelta, not int | Fixed in both kernel + harness workers |
| Temporal Cloud auth in harness | Missing api_key + tls=True | Added to harness main.py |
| OTEL not wired to Grafana | init_tracing used wrong exporter + env var names | Switched to opentelemetry-instrument entry point |
| MongoDB private link URI | Atlas cluster used peered endpoint | Switched to public endpoint |
| Dockerfile missing indemn_os/ | CLI package extracted but not copied in Docker | Updated Dockerfile |
| uv.lock in .gitignore | Railway uses .gitignore for uploads | Removed from .gitignore |

## Remaining Gaps — Complete List

### Priority 1: Blocks Phase 6

| # | Gap | Design reference | Status |
|---|---|---|---|
| 1 | G2.3 kernel code deletion | Harness draft § 8, alignment audit | APPROVED by Craig 2026-04-17 — ready to execute |
| 2 | `indemn trace entity {id}` | Vision map § 14, remaining-gap-sessions | NOT BUILT |
| 3 | `indemn trace cascade {correlation_id}` | Vision map § 14, remaining-gap-sessions | NOT BUILT |
| 4 | `indemn runtime create` with service token stdout | Harness draft G1.2 | NOT BUILT (manual 3-API-call process works) |
| 5 | OTEL → Grafana pipeline verification | Vision map § 14 | WIRED, NOT VERIFIED |
| 6 | Chat harness (Gates 3-4) | Vision map § 4, § 9, § 12, alignment audit Finding 0b | NOT BUILT |
| 7 | `indemn interaction transfer` | Vision map § 12, realtime-architecture-design | NOT BUILT |
| 8 | Step 4 spec catch-up (D.1, D.2) | Track D from implementation plan | NOT DONE |

### Priority 2: Operational surface completion

| # | Gap | Design reference | Status |
|---|---|---|---|
| 9 | `indemn runtime transition` | Phase 5 spec | Auto-CRUD works; static command not built |
| 10 | `indemn bulk retry` | Vision map § 10 | NOT BUILT |
| 11 | `indemn integration health` | Vision map § 7 | NOT BUILT |
| 12 | `indemn platform upgrade` | White paper § 7, vision map § 20 | NOT BUILT |
| 13 | Grafana dashboards | Vision map § 14, infrastructure-and-deployment | NOT CONFIGURED |

### Priority 3: Voice (Phase 5 completion)

| # | Gap | Design reference | Status |
|---|---|---|---|
| 14 | Voice harness (Gates 5-6) | Vision map § 4, § 12, Phase 5 spec § 5.3 | NOT BUILT |

## Open Question: Assistant in Base UI

The base UI assistant panel is designed as a running chat-harness instance (per base-ui-operational-surface lines 167, 306, 346 and authentication-design lines 463-482). Key design claims:

1. Assistant IS a chat-harness instance, not a kernel endpoint
2. Authenticates via user's session JWT (injected at session start)
3. Context: UI sends current-view payload per turn (entity being viewed, current filters)
4. Real-time: subscribes to `indemn events stream` for mid-conversation entity changes
5. "The conversation panel is a running harness instance — a real-time actor"

This means the chat harness (Gap #6) must support:
- Session JWT auth (user's identity, not service token)
- Per-turn context injection from the UI
- `indemn events stream` integration for real-time awareness
- The assistant is the DEFAULT associate provisioned per human actor

**This needs to be fully scoped against the design before implementation.**

## Methodology Note

The 4-pass audit (2026-04-15/16) checked mechanism alignment and architectural-layer placement. This operational surface audit checks whether the mechanisms are accessible through their designed interfaces (CLI, API, observability). Both are needed — the first catches "is it in the right place?" and the second catches "can you actually use it?"

Future work should include an operational surface check as part of every pass, not just mechanism/architecture verification.
