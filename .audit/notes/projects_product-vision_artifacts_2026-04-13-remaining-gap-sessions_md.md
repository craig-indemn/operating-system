# Notes: 2026-04-13-remaining-gap-sessions.md

**File:** projects/product-vision/artifacts/2026-04-13-remaining-gap-sessions.md
**Read:** 2026-04-16 (full file — 366 lines)
**Category:** design-source (5 gap sessions at white-paper level)

## Key Claims

Five gap sessions completed at white-paper level depth:

### 1. Development Workflow
- **Repository structure**: one git repo, modular monolith. `kernel/`, `seed/`, `harnesses/`, `ui/`, `tests/`. **Explicitly lists `harnesses/voice-deepagents/` and `harnesses/chat-deepagents/`** as separate Docker images per realtime-architecture-design.
- **Testing**: 3 layers — Unit (`tests/unit/`) + Integration (`tests/integration/`, uses Atlas dev cluster) + E2E (`tests/e2e/`).
- **CI/CD**: GitHub Actions on push to main → Railway auto-deploy. Lint + unit + integration tests in CI; E2E on-demand/schedule.
- **Parallel AI sessions**: git worktrees (Craig's existing pattern). Independent work parallel; shared infrastructure single-session.
- **CLAUDE.md for OS repo**: Phase 0 deliverable. Project structure, how-to-add-entity, how-to-add-capability, conventions, trust boundary, API-mode-only CLI rule.

### 2. Dependencies & Resilience
- **Dependency map with blast radius**:
  - **MongoDB Atlas** = only single point of failure (3-node HA replica set, 99.995% SLA).
  - **Temporal Cloud down** → associates stop; humans continue via unified queue; backlog replays on recovery.
  - **LLM down** → deterministic operations continue via `--auto` pattern.
  - **Secrets Manager down** → cached credentials serve.
  - **S3 down** → only file ops affected.
  - **Railway down** → stateless workers recover on restart.
  - **Grafana Cloud down** → monitoring blind, zero app impact.
- **Multi-provider LLM resilience** — LLM-provider-agnostic. Single provider outage scoped to associates using that provider.
- **What to build**: credential cache with TTL, Temporal retry policies, health endpoint (degraded status), base UI graceful degradation banner.

### 3. Operations
- **Customer onboarding**: Tier 1 self-service, **Tier 2 FDE via platform admin session** (primary), Tier 3 developer self-service signup.
- **Day-to-day monitoring surfaces**: base UI queue/pipeline/bootstrap + CLI + Grafana Cloud + Railway dashboard + Atlas dashboard + Temporal Cloud dashboard.
- **Debugging workflow**: identify → locate (`indemn trace`) → diagnose (Grafana spans + changes collection) → act → verify.
- **Platform upgrades**: `indemn platform upgrade --dry-run` → `indemn platform upgrade` — rollable, auditable.
- **Backup/DR**: Atlas backups + Temporal durable workflows + S3 versioning + changes collection as config backup + `indemn org export`/`import`.

### 4. Transition & Coexistence
- **Current system and new OS are COMPLETELY SEPARATE**: different codebases, databases, compute. No bridge layer.
- **Team allocation**: Craig full-time on OS + AI; Dhruv maintains current system + validates OS design; others continue customer work until ready to shift.
- **Migration model**: new customers → OS. Existing customers migrate when OS can do what current system does + concrete benefit. **Not forced, not on timeline.**
- **Per-migration mini-project**: model workflows → set up integrations → run parallel with same inputs → compare outputs → cut over → decommission.
- **First migration candidate**: GIC (Craig built both systems; OS designed around GIC pipeline).
- **Current system as R&D for OS**: GIC email → entity + watch + associate pattern. INSURICA renewals → scheduled monitoring. EventGuard E2E → real-time autonomous flow. Union General → intake + extraction + routing.

### 5. Domain Modeling Process
- **8-step process (formalized from three retraces)**:
  1. Understand the business (narrative)
  2. Identify entities (nouns, state machines, relationships)
  3. Identify roles and actors (permissions, watches)
  4. Define rules and configuration (per-org logic)
  5. Write skills (behavioral instructions in markdown)
  6. Set up integrations (per-customer external systems)
  7. Test in staging
  8. Deploy and tune
- **Universal pattern**: entry point → entity → watches → associates → state changes → more watches → human checkpoint or final state.
- **Per-customer vs kernel split** — table of what's universal vs. what varies.

### 17 decisions + 7 deferred items identified.

## Architectural Decisions

- **Harnesses are separate Docker images** in `harnesses/` dir. Explicitly listed (voice-deepagents + chat-deepagents; async-deepagents not mentioned here either).
- **MongoDB Atlas is the only SPOF**.
- **Multi-provider LLM coexistence** as a resilience feature.
- **Tier 2 is the primary onboarding path** via FDE + platform admin session.
- **Current system and OS are fully separated** — no bridge.
- **8-step domain modeling process** standardized from retraces.
- **Real-time implementation deferred to per-component spec** (not in white paper).

## Layer/Location Specified

- **Repository structure**:
  ```
  indemn-os/
    kernel/
    seed/
    harnesses/
      voice-deepagents/
      chat-deepagents/
    ui/
    tests/
    Dockerfile (multi-entry-point)
    docker-compose.yml
    pyproject.toml
    CLAUDE.md
  ```
- **Harness images**: separate deployables per kind+framework.
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/e2e/`.
- **CLAUDE.md**: at repo root, conventions enforcement.

**Finding 0 relevance**:
- The `harnesses/` directory is EXPLICITLY in the repository structure per this artifact.
- Voice + chat harness dirs listed. **Async harness NOT listed here either** — same omission as infrastructure-and-deployment.
- This confirms the drift: by 2026-04-13, the infrastructure + repo-structure documents both list voice + chat harnesses but not async. The async agent execution "goes to kernel Temporal Worker by default" in both infra docs — and this is the direct cause of Finding 0.
- **Per realtime-architecture-design** (earlier, 2026-04-10), async-deepagents IS listed as one of 3 harness images. Later infra docs (2026-04-13) dropped it. **This is the spec drift that propagated to implementation.**

## Dependencies Declared

- Git + Git worktrees
- GitHub Actions (CI)
- Railway (CD)
- Atlas dev cluster (integration tests)
- Temporal dev server (local)
- Grafana Cloud (monitoring)
- pyproject.toml / uv (Python deps)
- LiveKit (voice harness)
- WebSocket (chat harness)

## Code Locations Specified

- `kernel/` — all kernel code (entity, message, watch, rule, capability, auth, api, cli, queue_processor, temporal_worker, temporal_workflows)
- `seed/entities/`, `seed/skills/`, `seed/roles/`
- `harnesses/voice-deepagents/`, `harnesses/chat-deepagents/` — **no async-deepagents listed**
- `ui/src/`, `ui/package.json`
- `tests/unit/`, `tests/integration/`, `tests/e2e/`
- `Dockerfile` (multi-entry-point)
- `docker-compose.yml`
- `pyproject.toml`
- `CLAUDE.md`

## Cross-References

- 2026-04-13-infrastructure-and-deployment.md (infrastructure context; this artifact builds on it)
- 2026-04-13-session-6-checkpoint.md (gap session list)
- 2026-04-10-realtime-architecture-design.md (specifies 3 harness images; this artifact lists only 2)
- 2026-04-11-base-ui-operational-surface.md (monitoring surfaces)
- 2026-04-11-authentication-design.md (platform admin model)
- 2026-04-10-crm/eventguard/gic-retrace (8-step domain modeling formalized from these)

## Open Questions or Ambiguities

- **Async-deepagents harness omission**: same as infrastructure-and-deployment. The repository structure in this artifact lists voice + chat + NOT async. **This is a cross-artifact drafting omission that directly caused Finding 0.**
- **Real-time implementation**: deferred to per-component spec (not in white paper). Phase 5 consolidated spec's voice harness example is the closest thing to an implementation spec — chat + async remain unimplemented.

**Supersedence note**:
- 17 decisions + universal pattern + 8-step process SURVIVE.
- **Harness directory listing is incomplete**: per realtime-architecture-design, 3 images (voice, chat, async) are required. This artifact + infrastructure artifact both show only 2. For the vision map, the authoritative answer is 3 (per the earlier, more thorough design artifact).
- Tier 2 as primary onboarding path SURVIVES.
- Coexistence model (no bridge) SURVIVES.
