---
ask: "Document how the indemn CLI is packaged, how updates flow through the system, how consumer surfaces consume it, and what requires rebuilding vs. what flows automatically. This is foundational to how the OS evolves and needs to be captured coherently, not scattered across chat decisions."
created: 2026-04-16
workstream: product-vision
session: 2026-04-16-b
sources:
  - type: artifact
    ref: "2026-04-16-harness-implementation-plan.md"
    description: "Locked decisions on indemn-os package naming + gate structure"
  - type: artifact
    ref: "2026-04-16-async-harness-draft.md"
    description: "Uses indemn-os package as a dependency"
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "CLI auto-generation from entity definitions"
  - type: artifact
    ref: "2026-04-15-shakeout-session-findings.md"
    description: "Finding 11 (follow_redirects) + shakeout-confirmed CLI patterns"
---

# CLI Update Flow — How the `indemn` CLI Evolves

**Purpose:** Foundational document for how the CLI is packaged, distributed, consumed, and updated. Written to prevent the architecture-level misunderstandings that came up during Gate 2 review.

**Decision locked 2026-04-16:** Package name is `indemn-os` (on internal PyPI). Binary is `indemn`. Published as its own pip-installable package, separate from the NPM `indemn-cli` (which is a different tool for current-system infrastructure).

---

## 1. The Core Insight

**The CLI has two layers of commands, and they update through entirely different paths:**

| Layer | Examples | Where defined | Update requires |
|---|---|---|---|
| **Static** | `indemn runtime create`, `indemn entity create`, `indemn associate create`, `indemn skill update`, `indemn queue show`, `indemn events stream`, `indemn trace cascade`, `indemn audit verify` | Python source in `indemn_os/` package | New package release + container rebuild |
| **Dynamic** | `indemn email classify`, `indemn submission transition`, `indemn actionitem list`, `indemn policy bind`, `indemn <any-entity> <any-method>` | **Generated at CLI startup** from `/api/_meta/entities` | Just create/modify the entity — nothing else |

This split is why the CLI can feel "magical" — you define a new entity type and suddenly commands appear for it everywhere, without anyone deploying anything.

---

## 2. The Static Layer

**What lives here**: core OS operations that are fixed across deployments — the ~30 command groups that exist regardless of what domain entities you've defined.

**Structure in the `indemn-os` package**:
```
indemn_os/src/indemn_os/
  main.py              # typer app entry, indemn = main:app
  client.py            # HTTP client with auth + retry + follow_redirects
  registration.py      # dynamic command builder (reads /api/_meta/entities at startup)
  output.py            # JSON default format (per shakeout decision)
  auth.py              # token handling (INDEMN_AUTH_TOKEN env var)
  types.py             # shared Pydantic models (AgentExecutionInput, etc.)
  # static command modules:
  entity_commands.py, associate_commands.py, skill_commands.py,
  role_commands.py, actor_commands.py, runtime_commands.py,
  queue_commands.py, events_commands.py, attention_commands.py,
  integration_commands.py, lookup_commands.py, rule_commands.py,
  bulk_commands.py, audit_commands.py, org_commands.py,
  trace_commands.py, platform_commands.py
```

**Updating static commands**:
- Code change in `indemn_os/`
- Version bump (`indemn-os==X.Y.Z`)
- Publish to internal PyPI
- Rebuild the 4 images that install `indemn-os`:
  - `indemn-kernel` (the kernel image uses indemn-os for its own admin CLI usage)
  - `indemn/harness-base:X.Y.Z` (inherited by all harnesses)
  - All three harness images (voice, chat, async) rebuild from new base
- Railway redeploys the 4 services

**How often this happens**: infrequent. New kernel-level capabilities, bug fixes, formatting changes. Semantic versioning applies normally.

---

## 3. The Dynamic Layer

**What lives here**: per-entity commands that didn't exist in any code until the entity was defined — `indemn email classify` exists because someone created an `Email` entity type.

**How it works**:
1. At CLI startup, `registration.py` calls `GET /api/_meta/entities` on the kernel API
2. Response lists all entity types with their fields, state machines, exposed methods, capabilities
3. CLI builds a Typer subcommand tree dynamically — one subtree per entity
4. For each entity: CRUD commands (`create`, `get`, `list`, `update`, `delete`), transition command (`transition --to X`), per-capability commands (e.g., `classify --auto`), per-exposed-method commands
5. Commands are registered before argument parsing — `indemn email classify EMAIL-001 --auto` routes correctly

**The `/api/_meta/entities` endpoint** is the contract. Its shape is the kernel's promise to the CLI. Changes to this shape are breaking changes that require both kernel and CLI to bump together.

---

## 4. Update Flows (the three cases)

### Case A — You add a new STATIC command

Example: kernel team ships `indemn runtime migrate` for moving Runtimes between clusters.

```
1. Code change in indemn_os/src/indemn_os/runtime_commands.py
2. Bump version: indemn-os 0.1.0 → 0.2.0
3. Publish to internal PyPI: `uv publish` (or equivalent)
4. Rebuild containers that pin indemn-os version:
   - indemn-kernel
   - indemn/harness-base (and children)
5. Railway redeploys
6. Users on their dev machines: `pip install --upgrade indemn-os==0.2.0`
```

Infrequent. Normal package versioning.

### Case B — You create a new ENTITY type

Example: `indemn entity create Claim --fields '{"policy_id": {"type": "objectid", "required": true}, "incident_date": {"type": "datetime", "required": true}, "status": {"type": "str", "enum_values": ["filed", "investigating", "approved", "denied", "paid"], "is_state_field": true}}' --state-machine '{"filed": ["investigating"], "investigating": ["approved", "denied"], "approved": ["paid"]}'`

```
Kernel-side (all automatic, ~seconds):
1. CLI → API: POST /api/entities with the definition
2. Kernel writes EntityDefinition doc to MongoDB
3. kernel/db.py::register_domain_entity() hot-registers /api/claims/* routes (shakeout Finding 7 fix — no restart required)
4. /api/_meta/entities now returns "Claim" in its response

Consumer-side (automatic on next CLI invocation):
5. Next time anyone runs indemn (your laptop, async harness subprocess, chat harness subprocess, Claude Code, UI assistant, Tier 3 customer), the CLI fetches /api/_meta/entities at startup, sees Claim, builds the subcommand tree:
   - indemn claim create --policy-id X --incident-date Y
   - indemn claim get CLM-001
   - indemn claim list --status filed
   - indemn claim transition CLM-001 --to investigating
   - indemn claim update CLM-001 --field value
   - indemn claim delete CLM-001 (if permitted)
6. Plus any capabilities you've enabled — indemn claim auto-classify, etc.
```

**No container rebuild. No redeploy. No version bump.**

### Case C — You modify an existing entity (add field, enable capability, add @exposed method)

Example: `indemn entity modify Email --add-field '{"priority": {"type": "str", "enum_values": ["low", "normal", "high", "urgent"], "default": "normal"}}'`

Same as Case B. Kernel updates definition, `/api/_meta/entities` reflects the change, next CLI invocation sees the new field. Existing documents get Pydantic defaults. No migration needed for additive changes.

For destructive changes (rename, type change), use `indemn entity migrate` (schema migration is first-class per white paper).

---

## 5. Consumer Surfaces

**Every consumer uses the SAME `indemn-os` package and the SAME `indemn` binary.** Nothing is special-cased.

| Consumer | Install location | Auth | Special notes |
|---|---|---|---|
| **Craig on his laptop** | `pip install indemn-os` into local Python env | `INDEMN_AUTH_TOKEN` env var (user's session JWT or API key) | Direct terminal use, ad-hoc ops |
| **Claude Code sessions** | Same as above | Inherited from shell env | Uses `indemn` commands as regular shell tools |
| **Kernel container** | Installed in Dockerfile | Admin context (bypass auth or internal service token) | Kernel's own admin/migration scripts use the CLI |
| **Async harness** | Installed in harness-base image | `INDEMN_SERVICE_TOKEN` env var (Runtime instance token) | Subprocess calls from harness code (cli.py wrapper) AND from deepagents' execute tool |
| **Chat harness** | Same | User's Session JWT (injected at session start) | Same subprocess pattern; user's permissions enforced |
| **Voice harness** | Same | Associate service token OR user JWT depending on kind | Same pattern |
| **UI Assistant** | (Chat harness instance — already covered) | Same as chat harness | N/A — UI doesn't directly install CLI |
| **Base UI proper** | Doesn't install CLI | User Session JWT | Uses kernel API directly (not via CLI) |
| **Tier 3 customer developers** | `pip install indemn-os` on their laptop/CI | Customer's API key | Public-facing workflow (post-MVP) |

**Key point**: the harness containers have the CLI installed at image build time. Individual CLI invocations inside a running container are fresh subprocesses — each one fetches `/api/_meta/entities` at startup, sees the current state, builds commands. No per-container reload, no cache bust, no container rebuild for new entities.

---

## 6. What Requires a Rebuild vs. What Flows Automatically

| Change | Rebuild containers? | Redeploy Railway? | Notes |
|---|---|---|---|
| New entity type (`indemn entity create X`) | **No** | **No** | Case B — automatic via `/api/_meta/entities` |
| Add field to entity | **No** | **No** | Case C |
| Remove/rename field | **No** | **No** | Kernel handles via migration CLI |
| Enable capability on entity | **No** | **No** | Hot-registered per shakeout Finding 7 |
| Add @exposed method (Tier 3 custom code) | **Maybe** | **Maybe** | If custom Python code added to kernel, yes. If it's a data-level activation, no. |
| Change to static CLI command | **Yes** | **Yes** | Case A — new `indemn-os` version |
| Change to kernel API endpoint structure | **Yes** | **Yes** | Kernel rebuild + typically `indemn-os` rebuild for contract consistency |
| Associate config change | **No** | **No** | Data-level; loaded fresh per session by the harness |
| Skill content change | **No** | **No** | Data-level; loaded by associate at session start (version-approved) |
| Rule creation/modification | **No** | **No** | Data-level |
| Runtime deployment config change | **Sometimes** | **Yes** | If image version changes, yes. If just env vars, just redeploy. |
| New kernel entity type (7→8) | **Yes** | **Yes** | Kernel entities are hand-written Python classes |
| Sandbox switch `INDEMN_SANDBOX_TYPE=daytona` | **No** | **Yes** | Env var change, Railway restart of harness service |

**Rule of thumb**: if it's DATA in MongoDB (entity definitions, skills, rules, lookups, actor configs, integrations), no rebuild. If it's CODE in `indemn_os/` or `kernel/`, rebuild.

---

## 7. Package Repository Setup (implementation requirement for Track A)

This is the operational side of making the CLI package work. Needs to exist before Gate 2 implementation can ship.

**Registry choice**: internal PyPI OR GitHub Packages OR AWS CodeArtifact. My recommendation: **GitHub Packages** for MVP — you already use GitHub, it's built-in, no new infra.

**Publishing workflow**:
1. `indemn-os` package has its own `pyproject.toml` with version + metadata
2. CI workflow on push to main:
   - Runs tests against the CLI
   - If version in pyproject.toml bumped: `uv publish` or `poetry publish` to GitHub Packages
   - Tags the commit with `indemn-os-vX.Y.Z`
3. Consumer Dockerfiles pin a specific version: `uv pip install indemn-os==0.1.0`
4. Consumer CI/CD bumps pinned version when ready to uptake new CLI

**Authentication** for internal consumption:
- GitHub Packages uses GitHub tokens for auth
- Railway services get a read-only `PIP_EXTRA_INDEX_URL` + auth token env var
- Dockerfile uses build args to install from private registry

**Versioning semantics**:
- **Major** (1.0.0 → 2.0.0): breaking changes to CLI surface or to `/api/_meta/entities` contract. Requires kernel bump in lockstep.
- **Minor** (0.1.0 → 0.2.0): new static commands, new optional CLI flags, new Pydantic model fields with defaults.
- **Patch** (0.1.0 → 0.1.1): bug fixes, formatting, internal refactors.

For MVP, we're in `0.x.y` (pre-1.0) so breaking changes are allowed in minors. Still bump patch for fixes.

---

## 8. Key Invariants

These must hold for the system to work as documented:

1. **`/api/_meta/entities` is the contract.** Breaking changes to its shape require kernel + CLI in lockstep.
2. **The CLI has no direct MongoDB access.** All operations go through the API.
3. **Every CLI invocation is a fresh subprocess.** No long-lived CLI daemon. No cross-invocation cache.
4. **The binary name is `indemn`.** Matches every design reference. Not `indemn-os` (package name) or `indemn-cli` (NPM tool).
5. **`indemn-os` package is kernel-independent.** It imports NOTHING from `kernel/`. Harnesses depend only on `indemn-os`.
6. **Entity-specific commands are always discovered, never hardcoded.** If you see `indemn email classify` written in the CLI source code, something's wrong.

---

## 9. What This Document Doesn't Cover

- **Per-package testing strategy** — CLI has its own test suite separate from kernel's, TBD during extraction.
- **Customer-facing CLI documentation** — generated from Typer help text + entity metadata; separate concern.
- **CLI performance at scale** — `/api/_meta/entities` caching strategy for long-lived processes (not applicable to harness subprocesses, but relevant for a user's interactive shell).
- **Plugin architecture for Tier 3** — if customers want to extend the CLI with their own commands, that's post-MVP. Today, customer-specific commands come via `@exposed` methods on their entities (which auto-generate dynamically).

---

## 10. Cross-References

- `2026-04-16-harness-implementation-plan.md` — harness hosting + gates
- `2026-04-16-async-harness-draft.md` — uses this package
- `2026-04-13-white-paper.md` § 2 (Entity — operations auto-generated), § 3 (CLI always in API mode)
- `2026-04-14-impl-spec-phase-0-1-consolidated.md` § 1.30 (CLI auto-registration)
- `2026-04-15-shakeout-session-findings.md` Finding 11 (follow_redirects), decision on JSON default format
- `2026-04-13-remaining-gap-sessions.md` (repo structure + CI/CD pattern)
