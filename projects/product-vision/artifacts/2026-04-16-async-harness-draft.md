---
ask: "Gate 2 draft for Craig's review — concrete implementation of `indemn/runtime-async-deepagents` harness. Incorporates all Gate 0 + Gate 1 approvals and all corrections from the review conversation: actual deepagents API, backend factory pattern (LocalShellBackend for MVP, Daytona for prod), thin agent code, `indemn-os` package naming. No code touches `/Users/home/Repositories/indemn-os/` until Craig approves G2.1 + G2.2."
created: 2026-04-16
updated: 2026-04-16
workstream: product-vision
session: 2026-04-16-b
sources:
  - type: artifact
    ref: "2026-04-16-harness-implementation-plan.md"
    description: "Governing plan + approved gates"
  - type: artifact
    ref: "2026-04-16-cli-update-flow.md"
    description: "CLI package strategy (indemn-os + dynamic entity commands)"
  - type: web
    ref: "https://docs.langchain.com/oss/python/deepagents/overview"
    description: "Verified deepagents API + backend model"
  - type: web
    ref: "https://docs.langchain.com/oss/python/deepagents/backends"
    description: "Backend options — LocalShellBackend uses subprocess.run(shell=True)"
---

# Async Harness — Gate 2 Draft (Revised)

**Status:** DRAFT for Craig's review. No code has been written to `/Users/home/Repositories/indemn-os/`. Approval of G2.1 + G2.2 unlocks implementation; G2.3 (kernel code deletion) requires separate sign-off after the harness is verified working.

**Revision notes:** Supersedes the original draft with corrections from the G1.3 refinement (deepagents' LocalShellBackend uses `shell=True`), the clarification that deepagents ships built-in `execute` via the backend (no custom tool wrappers needed), the `indemn-os` package + `indemn` binary naming decision, and the explicit LocalShellBackend/Daytona backend-factory pattern Craig approved.

---

## 1. Decisions Already Locked (reference)

From prior gate approvals — these shape the implementation:

| Gate | Decision |
|---|---|
| G0.1 | Railway per-harness service |
| G0.2 | Shared base image `indemn/harness-base` |
| G0.3 | Repo structure `harnesses/{async,chat,voice}-deepagents/` at `indemn-os` root |
| G0.4 | Image tagging `indemn/runtime-{kind}-{framework}:{version}` (semver releases + `main-{shortsha}` + `latest`) |
| G0.5 | Single CI pipeline on push to main builds all 4 images |
| G1.1 | Task queue naming `runtime-{runtime_id}` |
| G1.2 | Service token via stdout bootstrap on `indemn runtime create` → Railway env var `INDEMN_SERVICE_TOKEN` |
| G1.3 (refined) | **MVP = LocalShellBackend (no sandbox). Pre-prod = Daytona.** Switched via `INDEMN_SANDBOX_TYPE` env var. Both implementations clearly marked in code. Daytona stubbed with `NotImplementedError` until Phase 7 prep. |
| G1.4 | All 5 deepagents middleware modules enabled (via backend + built-ins; no custom middleware list) |
| G1.5 | Straight cutover (Option B) — no phased migration, we're in development |
| Package naming | `indemn-os` on internal PyPI, binary `indemn` (matches 100+ design references) |

Pending Q&A (needs Craig's final lock):
- Q3 (activity arg signature) — recommended: Pydantic model `AgentExecutionInput`, lives in `indemn_os.types`
- Q5 (CLI extraction) — confirmed: extract from `kernel/cli/` to `indemn-os` package

---

## 2. Repository Structure

```
indemn-os/                          # existing repo
  kernel/                           # existing — kernel code (uses indemn-os as a dep)
  kernel_entities/                  # existing — 7 kernel entities
  indemn_os/                        # NEW — pip-installable CLI package
    pyproject.toml                  # package metadata, name=indemn-os, entry_points: indemn=indemn_os.main:app
    src/
      indemn_os/
        __init__.py
        main.py                     # typer app entry
        client.py                   # HTTP client with auth
        registration.py             # dynamic command builder (fetches /api/_meta/entities)
        output.py                   # JSON default formatting
        types.py                    # shared Pydantic models (AgentExecutionInput, etc.)
        [command modules: entity, associate, skill, runtime, queue, events, ...]
  harnesses/                        # NEW
    _base/
      Dockerfile                    # indemn/harness-base:1.0.0
      pyproject.toml
      harness_common/               # shared helpers
        __init__.py
        cli.py                      # subprocess wrapper (harness orchestration calls)
        runtime.py                  # register_instance + heartbeat_loop
        backend.py                  # build_backend() factory (LocalShell vs Daytona)
        logging.py                  # OTEL setup
    async-deepagents/
      Dockerfile                    # inherits indemn/harness-base
      pyproject.toml                # deepagents, temporalio
      main.py                       # Temporal worker entry
      agent.py                      # deepagents agent builder (~10 lines)
  seed/                             # existing
  ui/                               # existing
  tests/                            # existing
  Dockerfile                        # existing (kernel image)
  docker-compose.yml                # existing
  pyproject.toml                    # existing (kernel deps — now depends on indemn-os package)
```

Key points:
- `indemn_os/` is its own package with its own `pyproject.toml`. Published to internal PyPI.
- Kernel depends on `indemn-os` (kernel's own CLI usage imports it). Harnesses depend on `indemn-os` (subprocess usage via `indemn` binary). Symmetric.
- Nothing in `harnesses/` imports kernel code. Ever.
- Not extending NPM `indemn-cli` repo (separate tool, different runtime, different purpose).

---

## 3. `indemn-os` Package (extracted from `kernel/cli/`)

Scope of the extraction:

**Static command modules** — move from `kernel/cli/` to `indemn_os/src/indemn_os/`:
- `main.py` (typer app)
- `client.py` (HTTP client, auth, retry, JSON default)
- `registration.py` (dynamic entity command builder)
- command modules: `entity_commands.py`, `associate_commands.py`, `skill_commands.py`, `role_commands.py`, `actor_commands.py`, `queue_commands.py`, `integration_commands.py`, `lookup_commands.py`, `rule_commands.py`, `runtime_commands.py`, `events_commands.py`, `org_commands.py`, `attention_commands.py`, `bulk_commands.py`, `audit_commands.py`

**Shared types** — new file `indemn_os/src/indemn_os/types.py`:
```python
"""Shared Pydantic models crossing kernel ↔ harness boundaries."""

from pydantic import BaseModel
from typing import Optional


class AgentExecutionInput(BaseModel):
    """Q3 — single typed input for process_with_associate activity.
    
    Used by both kernel ProcessMessageWorkflow (caller) and harness activity (callee).
    Adding optional fields is non-breaking.
    """
    message_id: str
    associate_id: str
    entity_type: str
    entity_id: str
    correlation_id: str
    depth: int
    parent_message_id: Optional[str] = None
    trace_context: Optional[dict] = None


class AgentExecutionResult(BaseModel):
    """Result returned by process_with_associate activity."""
    status: str  # "complete" | "failed" | "needs_human"
    iterations: int
    tools_used: list[str]
    error: Optional[str] = None
```

**Kernel changes**: `kernel/cli/` deleted. Kernel imports from `indemn_os` package instead. Kernel's own CLI entry point (for admin, debugging) shells out to `indemn` or imports `indemn_os.main:app`.

Full rationale + update-flow details in: `2026-04-16-cli-update-flow.md`.

---

## 4. Base Image Dockerfile (`harnesses/_base/Dockerfile`)

```dockerfile
# indemn/harness-base:1.0.0 — shared foundation for all harnesses
FROM python:3.12-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install indemn-os CLI from internal PyPI (pinned version)
# This installs the `indemn` binary on PATH + makes indemn_os importable
ARG INDEMN_OS_VERSION=0.1.0
RUN uv pip install --system indemn-os==${INDEMN_OS_VERSION}

# Install base harness deps (cli wrapper, runtime registration, backend factory, OTEL)
COPY harnesses/_base/pyproject.toml harnesses/_base/uv.lock /tmp/_base/
RUN cd /tmp/_base && uv sync --frozen --no-dev
COPY harnesses/_base/harness_common/ /app/harness_common/

# Runtime env vars — populated at Railway deploy time:
# INDEMN_API_URL            — where kernel API lives (e.g., http://indemn-api.railway.internal:8000)
# INDEMN_SERVICE_TOKEN      — Runtime instance service token
# RUNTIME_ID                — this Runtime's ObjectId
# INDEMN_SANDBOX_TYPE       — localshell (MVP) | daytona (prod)
# DAYTONA_API_KEY_REF       — required only when INDEMN_SANDBOX_TYPE=daytona
# OTEL_EXPORTER_OTLP_ENDPOINT — Grafana Cloud OTLP ingress

# Base image is not runnable alone — entry point set by child images
```

---

## 5. Async Harness Dockerfile (`harnesses/async-deepagents/Dockerfile`)

```dockerfile
FROM indemn/harness-base:1.0.0

WORKDIR /app

# Install async harness deps (deepagents, temporal SDK, LangChain chat models)
COPY harnesses/async-deepagents/pyproject.toml /tmp/async/
RUN cd /tmp/async && uv sync --frozen --no-dev

# Copy harness code
COPY harnesses/async-deepagents/ /app/harness/

# Entry point
CMD ["uv", "run", "python", "-m", "harness.main"]
```

---

## 6. Harness Code

### 6.1 `harnesses/_base/harness_common/cli.py`

Shared subprocess wrapper for HARNESS ORCHESTRATION calls only (register, heartbeat, load context, complete message). Agent's own CLI execution goes through deepagents' built-in `execute`.

```python
"""Subprocess wrapper for harness orchestration CLI calls.

Used for: register_instance, heartbeat, load associate/entity/skill context,
mark message complete/failed. NOT used for agent's runtime tool execution —
that goes through deepagents' LocalShellBackend (MVP) or DaytonaSandbox (prod).
"""

import json
import os
import subprocess
from typing import Any


class CLIError(RuntimeError):
    pass


def indemn(*args: str, timeout: float = 30.0, parse_json: bool = True) -> Any:
    """Run `indemn <args> --json` as subprocess, parse JSON result."""
    env = {
        "INDEMN_API_URL": os.environ["INDEMN_API_URL"],
        "INDEMN_AUTH_TOKEN": os.environ["INDEMN_SERVICE_TOKEN"],
        "PATH": os.environ["PATH"],
        "PYTHONUNBUFFERED": "1",
    }
    for k in ("TRACEPARENT", "TRACESTATE"):
        if k in os.environ:
            env[k] = os.environ[k]
    
    cmd = ["indemn", *args]
    if parse_json and "--json" not in cmd:
        cmd.append("--json")
    
    result = subprocess.run(
        cmd, env=env, capture_output=True, timeout=timeout, check=False,
    )
    if result.returncode != 0:
        raise CLIError(f"CLI failed ({result.returncode}): {result.stderr.decode()[:500]}")
    
    output = result.stdout.decode()
    return json.loads(output) if parse_json and output.strip() else output
```

### 6.2 `harnesses/_base/harness_common/runtime.py`

```python
"""Runtime instance lifecycle — register + heartbeat."""

import asyncio
import logging
import os
from .cli import indemn

RUNTIME_ID = os.environ["RUNTIME_ID"]
log = logging.getLogger(__name__)


async def register_instance() -> dict:
    """Call at harness startup."""
    result = indemn("runtime", "register-instance", "--runtime-id", RUNTIME_ID)
    log.info("Registered instance: %s", result.get("instance_id"))
    return result


async def heartbeat_loop(interval_s: float = 30.0) -> None:
    while True:
        try:
            indemn("runtime", "heartbeat", "--runtime-id", RUNTIME_ID)
        except Exception as e:
            log.warning("Heartbeat failed: %s", e)
        await asyncio.sleep(interval_s)
```

### 6.3 `harnesses/_base/harness_common/backend.py` (THE backend factory)

```python
"""Sandbox backend factory.

Two modes supported via INDEMN_SANDBOX_TYPE env var:
  - localshell : LocalShellBackend (MVP / dev / testing) — no sandbox
  - daytona    : DaytonaSandbox (pre-prod / production)  — per-session isolation

Agent code (agent.py) doesn't change — only the backend instance differs.
"""

import os


def build_backend():
    """Dispatch based on INDEMN_SANDBOX_TYPE env var."""
    sandbox_type = os.environ.get("INDEMN_SANDBOX_TYPE", "localshell")
    
    if sandbox_type == "localshell":
        return _build_localshell_backend()
    elif sandbox_type == "daytona":
        return _build_daytona_backend()
    else:
        raise ValueError(
            f"Unknown INDEMN_SANDBOX_TYPE: {sandbox_type!r}. "
            f"Supported: 'localshell' (MVP) | 'daytona' (production)."
        )


# ============================================================
# MVP / DEV / TESTING — LocalShellBackend
# ============================================================

def _build_localshell_backend():
    """LocalShellBackend — no sandbox. Container is the blast radius.
    
    SECURITY POSTURE (non-production only):
    ----------------------------------------
    deepagents' LocalShellBackend uses subprocess.run(shell=True).
    LLM output feeds directly into a shell interpreter.
    Prompt injection CAN execute arbitrary shell commands inside
    the harness container.
    
    Acceptable during testing/dev because:
      1. We control the prompts (approved + content-hashed skills)
      2. We control the inputs (internal data during dev, not adversarial)
      3. Container isolation from kernel (no MongoDB creds, no kernel code)
      4. Railway container is ephemeral (no persistent corruption)
    
    DO NOT SHIP TO EXTERNAL CUSTOMERS WITH THIS BACKEND.
    Switch INDEMN_SANDBOX_TYPE=daytona before Phase 7.
    """
    from deepagents.backends import LocalShellBackend
    
    return LocalShellBackend(
        root_dir="/workspace",
        env={
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "INDEMN_API_URL": os.environ["INDEMN_API_URL"],
            "INDEMN_AUTH_TOKEN": os.environ["INDEMN_SERVICE_TOKEN"],
        },
    )


# ============================================================
# PRE-PRODUCTION / PRODUCTION — DaytonaSandbox
# ============================================================

def _build_daytona_backend():
    """DaytonaSandbox — per-session isolated VM. Production path.
    
    SECURITY POSTURE (production):
    ------------------------------
    Per-session isolated sandbox. Filesystem, network, and process
    boundaries enforced by Daytona. Prompt injection contained within
    the sandbox.
    
    Config:
      INDEMN_SANDBOX_TYPE=daytona
      DAYTONA_API_KEY_REF=<secret_ref>  — resolved from AWS Secrets Manager
    
    Cold start ~90ms per session. Acceptable for async. Voice latency
    budget re-evaluated per-harness when voice harness ships.
    """
    raise NotImplementedError(
        "Daytona backend not yet implemented. "
        "Enable before Phase 7 (first external customer). "
        "Tracked in: 2026-04-16-harness-implementation-plan.md § 3.1"
    )
```

### 6.4 `harnesses/async-deepagents/agent.py` (~10 lines)

```python
"""deepagents agent builder for the async runtime.

Uses deepagents' built-in execute via the backend. No custom tools.
All 5 middleware modules come automatically with create_deep_agent
and the configured backend (G1.4).
"""

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from harness_common.backend import build_backend


def build_agent(associate: dict, skills: list[str]):
    """Construct the agent from the Associate's config + loaded skills."""
    model_id = associate.get("llm_config", {}).get("model", "anthropic:claude-sonnet-4-6")
    system_prompt = associate.get("prompt", "") + "\n\n---\n\n" + "\n\n".join(skills)
    
    return create_deep_agent(
        model=init_chat_model(model_id),
        system_prompt=system_prompt,
        backend=build_backend(),  # LocalShellBackend (MVP) or Daytona (prod)
    )
```

### 6.5 `harnesses/async-deepagents/main.py` (Temporal worker entry)

```python
"""Async harness entry point.

Subscribes to task queue `runtime-{runtime_id}` (G1.1).
Registers `process_with_associate` activity, migrated from
kernel/temporal/activities.py. Runs outside the kernel trust boundary.
"""

import asyncio
import logging
import os

from temporalio import activity
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.contrib.opentelemetry import TracingInterceptor

from indemn_os.types import AgentExecutionInput, AgentExecutionResult
from harness_common.cli import indemn
from harness_common.runtime import RUNTIME_ID, register_instance, heartbeat_loop
from harness.agent import build_agent

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TASK_QUEUE = f"runtime-{RUNTIME_ID}"


@activity.defn
async def process_with_associate(input: AgentExecutionInput) -> AgentExecutionResult:
    """Agent execution loop. Migrated from kernel/temporal/activities.py.
    
    Harness orchestration uses the CLI for I/O (load context, mark complete).
    Agent's own tool execution uses deepagents' built-in execute via backend.
    """
    # Load associate config + context (harness orchestration, not agent tools)
    associate = indemn("associate", "get", input.associate_id)
    context = indemn(
        "entity", "get", input.entity_type, input.entity_id,
        "--depth", "2", "--include-related",
    )
    
    skill_contents = []
    for skill_ref in associate.get("skills", []):
        skill = indemn("skill", "get", skill_ref)
        skill_contents.append(skill["content"])
    
    # Build agent (thin — deepagents handles everything once backend is set)
    agent = build_agent(associate=associate, skills=skill_contents)
    
    # Run the agent loop
    result = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": f"Process this work:\n\n{context}",
        }],
    })
    
    # Mark the message complete (harness orchestration)
    indemn("queue", "complete", input.message_id)
    
    return AgentExecutionResult(
        status="complete",
        iterations=len(result.get("messages", [])),
        tools_used=[],  # extract from messages if needed
    )


async def main():
    log.info("Starting async-deepagents harness, runtime=%s", RUNTIME_ID)
    log.info("Sandbox type: %s", os.environ.get("INDEMN_SANDBOX_TYPE", "localshell"))
    
    await register_instance()
    
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
    )
    
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        activities=[process_with_associate],
        max_concurrent_activities=10,
        interceptors=[TracingInterceptor()],
        graceful_shutdown_timeout=30,
    )
    
    log.info("Worker listening on queue: %s", TASK_QUEUE)
    
    await asyncio.gather(
        worker.run(),
        heartbeat_loop(interval_s=30.0),
    )


if __name__ == "__main__":
    asyncio.run(main())
```

**Total code footprint**: ~120 lines across 5 files (cli 45 + runtime 25 + backend 55 + agent 15 + main 80). Substantially thinner than the original draft thanks to deepagents' built-ins.

---

## 7. Kernel Dispatch Rewiring

### 7.1 `kernel/temporal/workflows.py::ProcessMessageWorkflow`

```python
from indemn_os.types import AgentExecutionInput

@workflow.defn
class ProcessMessageWorkflow:
    @workflow.run
    async def run(self, message_id: str) -> dict:
        # Claim + load context (kernel activities, kernel queue)
        msg = await workflow.execute_activity(
            claim_message, message_id,
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        # Queue Processor already picked the associate (per Q1 Option D).
        # Load the actor to get runtime_id for dispatch.
        actor = await workflow.execute_activity(
            load_actor, msg.target_actor_id,
            start_to_close_timeout=timedelta(seconds=10),
        )
        runtime_id = actor.get("runtime_id")
        if not runtime_id:
            await workflow.execute_activity(fail_message, message_id, "no_runtime")
            return {"status": "failed", "reason": "no_runtime"}
        
        # Dispatch to this associate's Runtime queue (harness worker picks up)
        agent_input = AgentExecutionInput(
            message_id=message_id,
            associate_id=msg.target_actor_id,
            entity_type=msg.entity_type,
            entity_id=msg.entity_id,
            correlation_id=msg.correlation_id,
            depth=msg.depth,
        )
        result = await workflow.execute_activity(
            "process_with_associate",        # activity name only (string — lives in harness)
            agent_input,
            task_queue=f"runtime-{runtime_id}",  # G1.1
            start_to_close_timeout=timedelta(minutes=10),
            heartbeat_timeout=timedelta(seconds=60),
        )
        
        await workflow.execute_activity(complete_message, message_id, ...)
        return result
```

### 7.2 `kernel/temporal/worker.py` — activity registration changes

```python
# BEFORE
activities=[
    claim_message, load_entity_context,
    process_with_associate,       # REMOVE — lives in async harness now
    complete_message, fail_message,
    process_human_decision,
    process_bulk_batch, preview_bulk_operation,
],

# AFTER
activities=[
    claim_message, load_entity_context,
    load_actor,                   # NEW — for workflow dispatch routing
    complete_message, fail_message,
    process_human_decision,
    process_bulk_batch, preview_bulk_operation,
],
```

### 7.3 `kernel/temporal/activities.py` — add `load_actor`, remove agent loop

```python
@activity.defn
async def load_actor(actor_id: str) -> dict:
    """Load minimal actor config for workflow dispatch routing."""
    from kernel_entities.actor import Actor
    from bson import ObjectId
    actor = await Actor.get(ObjectId(actor_id))
    if not actor:
        raise ValueError(f"Actor {actor_id} not found")
    return {
        "id": str(actor.id),
        "type": actor.type,
        "runtime_id": str(actor.runtime_id) if actor.runtime_id else None,
        "status": actor.status,
    }
```

### 7.4 `kernel/queue_processor.py` — associate selection (Q1 Option D)

Update `dispatch_associate_workflows`:

```python
# For each pending associate-eligible message:
if msg.target_actor_id:
    # Scope already resolved — use that actor
    chosen_actor_id = msg.target_actor_id
else:
    # Find active associates with msg.target_role, pick one
    associates = await Actor.find({
        "type": "associate",
        "role_ids": role_id,
        "status": "active",
    }).to_list()
    if not associates:
        continue  # leave for humans in the role
    chosen_actor_id = _round_robin_pick(associates).id  # MVP: round-robin

# Start workflow (which will dispatch to runtime-{runtime_id} queue)
await temporal_client.start_workflow(
    ProcessMessageWorkflow.run,
    args=[str(msg.id)],
    id=f"msg-{msg.id}",
    task_queue="indemn-kernel",
)
```

### 7.5 `kernel/message/dispatch.py` (optimistic dispatch) — no change

Still starts `ProcessMessageWorkflow` as before. Workflow handles per-Runtime routing.

---

## 8. Kernel Code Deletion List (G2.3 — Irreversible)

Only delete AFTER async harness verified working end-to-end per § 9:

**From `kernel/temporal/activities.py`** — functions to delete:
- `process_with_associate` + `@activity.defn`
- `_execute_deterministic` (markdown skill parser + CLI-via-HTTP execution)
- `_execute_reasoning` (LLM tool-use loop; contains `import anthropic`)
- `_execute_hybrid`
- `_execute_command_via_api` (HTTP dispatch from inside kernel worker)
- `_parse_skill_steps` (line-by-line markdown parser)
- `_parse_simple_condition`
- `_load_skills` (direct MongoDB fetch + hash verify in activity — note: hash verify stays as separate kernel CLI; just not called from activity)
- `import anthropic` line

**From `kernel/cli/`** — entire directory moves to `indemn_os/src/indemn_os/`. After extraction, kernel imports from `indemn_os` package.

**Kernel-side result:**
- `grep -r "import anthropic" kernel/` returns nothing
- `kernel/temporal/activities.py` line count drops from 633 → ~280
- Kernel has no LLM dependencies
- `kernel/cli/` replaced by dependency on `indemn-os` package

---

## 9. Verification Criteria (all must pass before G2.3)

1. **Build verification**
   - `indemn-os` package builds and publishes to internal PyPI
   - `indemn/harness-base:1.0.0` image builds with indemn-os installed
   - `indemn/runtime-async-deepagents:0.1.0-dev.<sha>` image builds
   - `kernel/` image still builds (now depending on `indemn-os` package)

2. **Runtime verification**
   - `indemn runtime create --kind async --framework deepagents` returns Runtime ID + service token
   - Deploy harness to Railway with env vars: `INDEMN_SERVICE_TOKEN`, `RUNTIME_ID`, `INDEMN_SANDBOX_TYPE=localshell`
   - Harness logs: `Registered instance: ...` and `Worker listening on queue: runtime-<id>`
   - `indemn runtime show <id>` → status=active, heartbeat within last 60s

3. **End-to-end verification**
   - Create test associate with `runtime_id = <harness runtime>`
   - Trigger work matching its watch
   - Observe: queue message → ProcessMessageWorkflow starts on `indemn-kernel` → dispatches to `runtime-<id>` queue → harness activity runs → entity updated → message completed
   - OTEL trace shows one correlation_id spanning kernel → harness → kernel → complete

4. **Negative verification (security/invariant)**
   - Harness container has no `MONGODB_URI` env var
   - `grep -r "from kernel" harnesses/` returns nothing (no kernel imports in harness)
   - `pip show indemn-os` in harness container shows indemn-os installed
   - Service token scope enforced (harness can't call admin endpoints)

5. **Switch verification (G1.3)**
   - Set `INDEMN_SANDBOX_TYPE=daytona` → harness startup fails loudly with `NotImplementedError` (not silent fallback)
   - Set `INDEMN_SANDBOX_TYPE=unknown` → harness startup fails with `ValueError`

6. **Migration verification**
   - Route ALL dispatches through async harness
   - Run full pipeline test (GIC-style if test data exists)
   - Kernel's `process_with_associate` never called (not registered, not dispatched to)

**Only after all 6 verification groups pass → G2.3 sign-off → delete kernel code per § 8.**

---

## 10. Remaining Open Questions (need Craig's final lock)

**Q3 — Activity arg signature:** Pydantic model `AgentExecutionInput` in `indemn_os.types`. **Recommended: confirm.**

**Q5 — CLI extraction:** `indemn-os` package, `indemn` binary. **Already confirmed.** Execution detail: is existing `kernel/cli/` structure clean enough to extract 1:1, or do we need refactoring? Spot check of the files during extraction will tell us.

**Q2 re-confirm — Multi-associate dispatch (Option D):** Queue Processor picks the associate at dispatch time. Round-robin for MVP. Least-loaded later if needed. **Confirmed in conversation; capturing here.**

---

## 11. Build Sequence (post-G2 approval)

1. Extract `kernel/cli/` → `indemn_os/` package. Add `pyproject.toml`, publish to internal PyPI (first version).
2. Kernel Dockerfile updates to install `indemn-os` from PyPI instead of local copy.
3. Add `kernel/temporal/activities.py::load_actor`.
4. Update `kernel/temporal/workflows.py::ProcessMessageWorkflow` for per-Runtime dispatch.
5. Update `kernel/temporal/worker.py` activity registration.
6. Update `kernel/queue_processor.py::dispatch_associate_workflows` for associate selection.
7. Create `harnesses/_base/` (Dockerfile + harness_common/ + backend factory).
8. Create `harnesses/async-deepagents/` (Dockerfile + main.py + agent.py).
9. Add CI pipeline step to publish `indemn-os` package + build both images.
10. Add Railway service for async harness with env vars.
11. Run verification § 9 items 1–5.
12. Route all dispatches through harness.
13. **G2.3 sign-off required** — delete kernel code per § 8.
14. Final verification: `grep -r "import anthropic" kernel/` returns nothing.

Nothing past step 11 without Craig's explicit approval.

---

## 12. What This Draft Does Not Cover

- **Chat harness** — separate Gate 3/4 artifact (unblocks Finding 0b).
- **Voice harness** — separate Gate 5/6 artifact.
- **Daytona implementation** — stubbed with `NotImplementedError`. Before Phase 7.
- **Spec updates** — Phase 2-3 + Phase 4-5 consolidated specs need updating to reflect harness pattern. Parallel Track D work.
- **Infrastructure artifact update** — add `indemn-runtime-async-deepagents` to service table.
- **Cost update** — 3 new Railway services + 1 Daytona account line when added. Update cost projections.

---

## 13. Cross-References

- `2026-04-10-realtime-architecture-design.md` — canonical harness pattern design
- `2026-04-16-harness-implementation-plan.md` — governing plan + gates
- `2026-04-16-cli-update-flow.md` — package strategy + entity propagation
- `2026-04-16-vision-map.md` § 4, § 12 — trust boundary + harness pattern
- `2026-04-16-alignment-audit.md` § 2, § 7 — Finding 0 + fix priority
- `2026-04-16-harness-session-handoff.md` — session continuity for next Claude instance
- `2026-04-14-impl-spec-phase-4-5-consolidated.md` § 5.3 — voice harness spec example
- `2026-04-13-infrastructure-and-deployment.md` — Railway deployment shape
- `2026-04-11-authentication-design.md` — default assistant auth pattern, Session entity
- `2026-04-13-documentation-sweep.md` item 11 — `owner_actor_id` on associates
- External: deepagents docs (https://docs.langchain.com/oss/python/deepagents/overview)
- External: deepagents backends (https://docs.langchain.com/oss/python/deepagents/backends)
