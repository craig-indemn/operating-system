---
ask: "Complete the remaining gap sessions at white-paper level: Development Workflow, Dependencies & Resilience, Operations, Transition & Coexistence, Domain Modeling Process"
created: 2026-04-13
workstream: product-vision
session: 2026-04-13-b
sources:
  - type: conversation
    description: "Craig and Claude completing the remaining five gap sessions efficiently at white-paper level depth"
  - type: artifact
    description: "2026-04-13-infrastructure-and-deployment.md (infrastructure context these sessions build on)"
  - type: artifact
    description: "2026-04-13-session-6-checkpoint.md (established the gap session list and the layered approach)"
  - type: artifact
    description: "2026-04-11-base-ui-operational-surface.md (monitoring surfaces referenced by operations)"
  - type: artifact
    description: "2026-04-11-authentication-design.md (platform admin model referenced by operations and transition)"
---

# Remaining Gap Sessions — White Paper Level

## Context

Five gap sessions completed in one pass at white-paper level depth. Per Craig's guidance: the white paper needs 100% high-level coverage. Deeper implementation specs happen per-component when building. These sessions provide the "what and why" — the "how exactly" is deferred to per-component specs with proper research.

Also established in this session: **Real-time Implementation** (voice/chat/assistant harness implementation details) is deferred to a per-component spec, not the white paper. The session 5 conceptual model (Attention, Runtime, harness pattern, handoff, scoped watches) plus the infrastructure deployment shape provides sufficient white-paper-level coverage.

---

## 1. Development Workflow

### Repository structure

The OS is one Git repository. Modular monolith.

```
indemn-os/
  kernel/                    # The kernel framework
    entity.py                # Base Entity class + dynamic class creation
    message.py               # Message schema + queue operations
    watch.py                 # Watch evaluation + scope resolution
    rule.py                  # Condition evaluator (shared by watches + rules)
    capability.py            # Kernel capability library
    auth/                    # Auth middleware, session management, JWT
    api/                     # FastAPI app, auto-registration, auth endpoints, webhook handler
    cli/                     # Typer app, auto-registration, API client mode
    queue_processor.py       # Sweep process
    temporal_worker.py       # Temporal worker entry point
    temporal_workflows.py    # Generic workflows (claim→process→complete, bulk_execute)
  
  seed/                      # Standard library definitions
    entities/                # Seed YAML for standard entity types
    skills/                  # Seed markdown for standard skills
    roles/                   # Seed YAML for standard roles
  
  harnesses/                 # Real-time harnesses (separate Docker images)
    voice-deepagents/        # LiveKit + deepagents harness
    chat-deepagents/         # WebSocket + deepagents harness
  
  ui/                        # Base UI (React)
    src/
    package.json
  
  tests/                     # All tests
    unit/                    # Entity class tests, rule evaluator tests, etc.
    integration/             # Multi-entity operations, watch firing, queue flow
    e2e/                     # Full pipeline tests
  
  Dockerfile                 # Kernel image (multi-entry-point)
  docker-compose.yml         # Local dev stack
  pyproject.toml             # Python dependencies (uv)
  CLAUDE.md                  # Conventions for any session working on this codebase
```

### Testing strategy

Three layers:

| Layer | What it tests | How | When |
|---|---|---|---|
| **Unit** | Individual functions: entity class creation, rule evaluation, condition matching, state machine transitions, auth method validation, JWT signing | `pytest tests/unit/` — fast, no external dependencies, mocked DB | Every commit |
| **Integration** | Multi-component flows: entity save → watch fires → message in queue, rule evaluation with lookups, auth flow end-to-end, bulk operations | `pytest tests/integration/` — uses Atlas dev cluster, Temporal dev server | Every PR |
| **E2E** | Full scenarios from the retraces: GIC stale check, EventGuard quote flow, CRM overdue sweep | `pytest tests/e2e/` — uses Atlas dev cluster + Temporal | Pre-deploy, on-demand |

Key principle: entity behavior is the most-tested layer. Every entity type gets auto-generated test scaffolding (CRUD, state machine transitions, permission enforcement). Entity methods (kernel capabilities) get tested with real MongoDB.

Per-component spec deferred: exact fixture patterns, test data management, associate/skill testing approach, performance tests.

### CI/CD

Push to `main` → GitHub Actions runs tests → on success, Railway auto-deploys.

| Step | What | Where |
|---|---|---|
| Lint | ruff + type checking | GitHub Actions |
| Unit tests | `pytest tests/unit/` | GitHub Actions |
| Integration tests | `pytest tests/integration/` against Atlas dev cluster | GitHub Actions |
| Build | Docker image | Railway (triggered by push) |
| Deploy | Rolling deploy to Railway services | Railway |

E2E tests run on-demand or on a schedule, not on every push.

### Parallel AI sessions

Craig's existing pattern: git worktrees via the OS session manager. Each Claude Code session gets its own worktree, works in isolation, merges to main.

For the OS codebase:
- **Independent work** (different entity types, different capabilities, different tests): parallel sessions, each in their own worktree, merge independently.
- **Shared infrastructure** (base Entity class, API framework, auth middleware): single session at a time. Changes here cascade to everything.
- **Convention**: CLAUDE.md defines patterns all sessions follow. Any session that touches shared infrastructure must update CLAUDE.md if conventions change.

### CLAUDE.md for the OS repo

Written when the repo is created (Phase 0 of the build sequence). Contents: project structure, how to add an entity, how to add a capability, how to add a test, how to run locally, naming conventions, the trust boundary, the API-mode-only CLI rule. Kept lean per the existing CLAUDE.md philosophy.

---

## 2. Dependencies & Resilience

### The dependency map

| Dependency | What depends on it | If it goes down |
|---|---|---|
| **MongoDB Atlas** | Everything — entities, queue, auth, config | **Full outage.** The single point of failure. Protected by Atlas HA (3-node replica set, automatic failover, 99.995% SLA on M10+). |
| **Temporal Cloud** | Associate execution, bulk ops, scheduled tasks | **Associates stop.** Humans continue via the unified queue. Backlog replays automatically on recovery. |
| **LLM Providers** (Anthropic, OpenAI, others) | Associate reasoning (LLM fallback in the `--auto` pattern) | **LLM-dependent processing stops.** Deterministic operations continue (rules, lookups, state transitions). Different associates may use different providers — a single provider outage only affects associates on that provider. |
| **AWS Secrets Manager** | Credential resolution for Integrations, auth | **New credential fetches fail.** Existing sessions continue (JWT self-contained). Cached credentials serve until TTL expires. |
| **AWS S3** | File storage (PDFs, attachments, certificates) | **File operations fail.** Everything else works. 99.99% SLA. |
| **Railway** | All compute | **Full outage.** Automatic recovery — workers are stateless, MongoDB has data, Temporal has workflow state. |
| **Grafana Cloud** | Monitoring, OTEL traces | **Monitoring goes blind.** Zero application impact. OTEL export is fire-and-forget. |

### The key insight

**MongoDB Atlas is the only single point of failure.** Everything else degrades gracefully:

- Temporal down → humans continue via unified queue
- LLM down → `--auto` pattern continues deterministic processing
- Secrets Manager down → cached credentials serve
- S3 down → only file operations affected
- Railway down → stateless workers recover on restart

### Multi-provider LLM resilience

The OS is **LLM-provider-agnostic**. Associates specify their model in configuration (`llm_config` on Associate and Runtime entities). Multiple providers can coexist across different associates in the same org. A single provider outage affects only the associates using that specific provider. This is a resilience advantage worth calling out in the white paper.

### What we need to build

- **Credential caching with TTL** in the API server: fetch from Secrets Manager at startup, cache in memory, refresh every N minutes. Serve from cache if refresh fails.
- **Temporal retry policies** on all workflow activities: exponential backoff, max attempts, timeout per activity.
- **Health endpoint** that checks MongoDB, Temporal, Secrets Manager connectivity. Returns degraded status for non-critical dependency failures.
- **Graceful degradation in the base UI**: banner for degraded status, not full error page.

Per-component spec deferred: exact retry policies, cache TTL values, health check thresholds, degradation UI design.

---

## 3. Operations

### Customer onboarding flow

Three tiers, with Tier 2 as the primary path for Indemn's current model ("we build most things for the customer"):

| Tier | Who sets up | What happens |
|---|---|---|
| **Tier 1** (out of box) | Customer self-service | Clone from template org → configure via UI/CLI → go live |
| **Tier 2** (configured) | FDE via platform admin session | Create org → define entities → configure rules/skills → set up integrations → create associates → test in staging → deploy |
| **Tier 3** (developer) | Customer's engineers | Self-service signup → API key → build with CLI/API → deploy on platform |

Tier 2 onboarding checklist:

1. Create Organization via platform admin
2. Define domain entities (or clone from template if standard)
3. Configure per-org rules, lookups, capability activations
4. Set up Integrations (email, carrier APIs, payment, etc.)
5. Create roles with watches
6. Create associates with skills
7. Create human actors, assign roles, send invitations
8. Test pipeline end-to-end in staging org
9. Deploy (promote staging config to production org)
10. Monitor and tune rules based on real data

### Day-to-day monitoring

Covered by the base UI design + infrastructure design. Monitoring surfaces:

| Surface | Shows | Used by |
|---|---|---|
| **Base UI queue view** | Pending work per role, age, priority | Ops, team leads |
| **Base UI pipeline widgets** | Entity state distribution, throughput, bottleneck pointers | Ops, account managers |
| **Base UI bootstrap observability** | Integration health, Runtime status, Attentions, Actors | Ops, platform admin |
| **CLI** | `indemn queue stats`, `indemn integration health`, `indemn trace cascade` | Ops, engineers |
| **Grafana Cloud** | OTEL traces, latency, error rates | Engineers |
| **Railway dashboard** | Service health, resource usage, deploy history | Engineers |
| **Atlas dashboard** | Database performance, connections, queries | Engineers |
| **Temporal Cloud dashboard** | Workflow execution, queue depth, worker health | Engineers |

### Debugging workflow

1. **Identify**: ops sees it in base UI (queue growing, integration error, bottleneck) or external monitoring alert
2. **Locate**: `indemn trace entity ENTITY-ID` for recent changes and cascade membership. `indemn trace cascade CORRELATION-ID` for the full event tree.
3. **Diagnose**: drill into specific OTEL span in Grafana — timing, errors, rule evaluation metadata in changes collection
4. **Act**: fix root cause via CLI or base UI (update rule, rotate credential, restart service, reassign to human)
5. **Verify**: watch the fix propagate through the live base UI

### Platform upgrades

`indemn platform upgrade --dry-run` → `indemn platform upgrade`. Applies capability schema migrations, updates seed definitions. Rolling deploy of new kernel code. Zero downtime. Auditable and rollbackable.

### Backup and disaster recovery

- **MongoDB Atlas**: automatic backups, point-in-time recovery (M10+)
- **Temporal Cloud**: fully durable workflow state
- **S3**: versioning enabled
- **Configuration**: changes collection IS the backup. `indemn org export` for YAML snapshots. `indemn org import` for restore.

No additional backup infrastructure needed for MVP.

---

## 4. Transition & Coexistence

### The physical separation

The current system and the new OS are **completely separate**. Different codebases, different infrastructure, different databases. They don't share resources and they don't need to communicate.

| | Current system | New OS |
|---|---|---|
| **Codebase** | Multiple repos (bot-service, copilot-server, platform-v2, voice-service, etc.) | One repo (`indemn-os`) |
| **Database** | MongoDB Atlas `tiledesk` database | MongoDB Atlas, new database(s) |
| **Compute** | Railway (existing deployments) | Railway (new project) |
| **Maintained by** | Dhruv, Rudra, Jonathan, Peter | Craig (with AI) |
| **Serves** | All 18 current customers | New customers + eventually migrated existing ones |

### The coexistence model

They run side by side indefinitely. No shared state, no message passing, no bridge layer. The current system keeps serving current customers as-is. The OS is built and deployed independently.

**Team allocation during transition:**
- **Craig**: builds the OS full-time with AI
- **Dhruv**: maintains current system production. Participates in OS design validation. Transitions to OS when ready.
- **Rest of team**: continues current customer work. Shifts to OS as it absorbs workloads.

**No one is asked to stop what they're doing.** The OS is additive work until it's ready.

### When customers move

- **New customers** go on the OS from the start (once it's production-ready)
- **Existing customers** migrate when the OS can do what the current system does for them AND the migration has a concrete benefit
- **Not forced, not on a timeline.** Each migration is its own mini-project:
  1. Model their workflows on the OS
  2. Set up integrations
  3. Run both systems in parallel (same inputs, compare outputs)
  4. Cut over when confident
  5. Decommission the old configuration

**First migration candidate**: GIC. Craig built both systems. The OS kernel was designed by tracing GIC's pipeline. The domain model is already proven.

### What the current system teaches the OS

Every bespoke customer implementation is R&D for the OS:
- GIC email intelligence → entity + watch + associate pipeline pattern
- INSURICA renewals → scheduled monitoring + threshold alerting
- EventGuard end-to-end → real-time autonomous flow
- Union General submissions → intake + extraction + routing

The current system is the proving ground. The OS is the generalization.

### What the white paper says

Short and honest: "The OS is built alongside the current system. Current customers are unaffected. New customers go on the OS. Existing customers migrate when the OS proves it can serve them better. The timeline is determined by OS readiness, not by an arbitrary deadline."

---

## 5. Domain Modeling Process

### The process (formalized from the three retraces)

**Step 1: Understand the business.** What does this company actually do day to day? What are the workflows? Who are the people? What systems do they use? What's painful? Output: a narrative understanding, not a technical document.

**Step 2: Identify the entities.** What are the nouns? What data does this business create, manage, and act on? For each: fields, lifecycle (state machine), relationships. Test: can you describe the business entirely in terms of these entities and their states?

**Step 3: Identify the roles and actors.** Who participates? What types of participants? For each role: what entities can they access (permissions)? What entity changes do they care about (watches)? Which roles are humans? Which could be associates? Test: for every entity state change, is there a role whose watch catches it?

**Step 4: Define the rules and configuration.** What per-org business logic exists? Classification rules, routing thresholds, required fields, lookup tables. These parameterize kernel capabilities. Test: can you trace through the common case entirely with rules (no LLM)?

**Step 5: Write the skills.** For each associate role: behavioral instructions in markdown. What CLI commands does it use? When does it need reasoning vs following a procedure? Test: can a human reading the skill understand what the associate does?

**Step 6: Set up integrations.** What external systems does this customer use? For each: org-level or actor-level? Which adapter exists? If no adapter exists, that's a kernel contribution (new adapter code).

**Step 7: Test in staging.** Create a staging org, apply all configuration, run the pipeline with realistic data. Validate watches fire, associates process correctly, humans see the right queue items.

**Step 8: Deploy and tune.** Promote to production. Monitor. Tune rules based on real data — the `needs_reasoning` rate tells you which deterministic rules are missing. The system gets more deterministic over time as rules are added for patterns the LLM keeps handling.

### The universal pattern

Every system traced follows the same structure:

```
Entry point (email, webhook, chat, form, schedule)
  → Creates an entity
    → Watches fire
      → Associates process (deterministic first, reasoning if needed)
        → Entity state changes
          → More watches fire
            → Eventually reaches a human checkpoint or a final state
```

Domain modeling fills in WHAT entities, WHAT watches, WHAT rules, and WHAT skills populate this universal structure for a specific business.

### What varies per customer vs what's universal

| Universal (kernel) | Per-customer (domain) |
|---|---|
| Entity framework, state machines, CLI/API | Which entities, which fields, which states |
| Watches as wiring mechanism | Which watches on which roles |
| Rules + lookups evaluator | Which rules, which thresholds, which mappings |
| Kernel capabilities | Activation and configuration per entity |
| Associate execution (Temporal, harness) | Which skills, which mode, which model |
| Authentication, sessions, permissions | Which roles, who has them, MFA policy |

The kernel is built once. The domain modeling process is repeated per customer. Reusable components grow over time: standard entity templates, proven skills, common rule patterns, existing adapters.

---

## What's Decided Across All Five Sessions

1. **Repository structure**: one repo, modular monolith, kernel/ + seed/ + harnesses/ + ui/ + tests/
2. **Testing**: three layers (unit, integration, e2e), entity behavior most-tested, real MongoDB for integration tests
3. **CI/CD**: GitHub Actions → Railway auto-deploy on push to main
4. **Parallel AI sessions**: git worktrees, independent work in parallel, shared infrastructure single-session
5. **CLAUDE.md**: written at Phase 0, lean, conventions for all sessions
6. **MongoDB Atlas is the single point of failure**: everything else degrades gracefully
7. **LLM-provider-agnostic**: multiple providers coexist, single provider outage scoped to its associates
8. **Credential caching with TTL**: fetch from Secrets Manager at startup, serve from cache on failure
9. **Health endpoint with degraded status**: non-critical dependency failures show degraded, not error
10. **Customer onboarding**: Tier 2 is primary path (FDE builds for customer via platform admin session)
11. **Debugging path**: identify → locate → diagnose → act → verify, fully supported by existing primitives
12. **Current system and OS are completely separate**: different codebases, databases, compute. No bridge layer.
13. **No one stops current work**: OS is additive. Team shifts when OS is ready.
14. **New customers → OS. Existing customers → migrate when beneficial.** GIC is first migration candidate.
15. **Domain modeling is an 8-step process**: understand → entities → roles → rules → skills → integrations → test → deploy+tune
16. **The universal pattern**: entry point → entity → watches → associates → state changes → more watches → human checkpoint or final state
17. **Real-time implementation deferred to per-component spec**: white paper has conceptual coverage from session 5; implementation details (LiveKit + deepagents composition, WebSocket protocol, STT/TTS pipeline) researched when building

## What's Deferred to Per-Component Specs

- Test fixture patterns, test data management, associate testing approach
- Exact CI configuration (GitHub Actions YAML)
- Exact CLAUDE.md content for the OS repo
- Exact retry policies, cache TTLs, health check thresholds
- Customer-facing degradation UI design
- Per-customer migration playbooks
- Real-time harness implementation (deepagents ↔ LiveKit, WebSocket sessions, assistant panel connection)

## The Complete Gap Session Scorecard

| Session | Status | Artifact |
|---|---|---|
| Infrastructure & Deployment | **Complete** | `2026-04-13-infrastructure-and-deployment.md` |
| Real-time Implementation | **Deferred** to per-component spec (white paper covered by session 5 conceptual model) | — |
| Development Workflow | **Complete** | This artifact |
| Dependencies & Resilience | **Complete** | This artifact |
| Operations | **Complete** | This artifact |
| Transition & Coexistence | **Complete** | This artifact |
| Domain Modeling Process | **Complete** | This artifact |

**All gap sessions complete. The white paper has 100% high-level coverage. Ready for the writing phase.**
