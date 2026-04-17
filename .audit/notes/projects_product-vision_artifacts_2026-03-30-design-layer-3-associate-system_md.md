# Notes: 2026-03-30-design-layer-3-associate-system.md

**File:** projects/product-vision/artifacts/2026-03-30-design-layer-3-associate-system.md
**Read:** 2026-04-16 (full file — 401 lines)
**Category:** design-source

## Key Claims

- Core principle: "An associate IS Claude Code for insurance" — same architecture.
- The associate is a LangChain **deep agent** with the same architecture as Claude Code: Skills (SKILL.md) + Sandbox with `execute()` + Todo list + Subagents + Summarization + Human-in-the-loop.
- Explicitly: "**No 'tools' abstraction. No client library wrapper.** The agent reads its skills, reasons about what to do, and executes CLI commands in a sandbox."
- Uses `deepagents` package's `create_deep_agent()` function to build a LangGraph StateGraph with middleware stack (TodoList, Memory, Skills, Filesystem, SubAgent, Summarization, HumanInTheLoop).
- The `execute` tool runs shell commands in the sandbox backend. Example: `execute("indemn submission create --from-email EMAIL-001 --product PROD-001")`.
- Sandbox backends: BaseSandbox (production — all ops via execute() in isolated environment), FilesystemBackend (skills loading), StateBackend (testing only).
- **Daytona being considered** as sandbox provider: isolated per-invocation, pre-configured with indemn CLI + auth credentials, secure escape-proof, scalable spin up/down, clean up after each invocation.
- Web operators (browser automation agents for carrier portals) use the **same deep agent harness + browser automation capabilities added to the sandbox**. Same middleware stack, same skills pattern, same `execute()` mechanism.
- Associate is an Entity (first-class OS entity, CLI-creatable, Tier 3 compatible).
- Workflow is an Entity. Runner options: custom, Temporal, or blueprint runner. **Decision deferred** — workflow entity design is runner-agnostic.
- Evaluations use LangSmith framework; test associate workflow outcomes (entity state correctness, HITL escalation accuracy, etc.).

## Architectural Decisions

- **Agent framework: LangChain deep agents (deepagents package).** Rationale: already used (Jarvis, Intake Manager). Full middleware stack. Skills + sandbox + todo + subagents.
- **CLI interaction via `execute()` in sandbox.** Same as Claude Code pattern. "Skills document CLI commands. No tools abstraction needed."
- **Sandbox provider: Daytona** (evaluating at time of writing). Isolated, pre-configured, secure, scalable.
- **Web operators use same harness**. One framework for all agent types. Browser tools added to sandbox.
- **Associate = first-class OS entity**, CLI-creatable. Same pattern as all entities.
- **Skills: auto-generated (entity) + human-authored (workflow).** Entity skills tell WHAT operations exist; workflow skills tell WHEN and HOW to combine them.
- **Permission enforcement at entity layer, not sandbox layer.** "If the associate tries `indemn policy delete POL-001` and it doesn't have policy write permission, the CLI returns a permission error. The entity layer enforces this, not the sandbox."
- **Workflow runner decision deferred.** Custom for MVP, Temporal at scale, blueprint runner if open-sourced. The Workflow entity design is runner-agnostic.
- **Skill composition through entity permissions.** Entity permissions control which entity skills are available; workflow skills reference only entities the associate has access to.

## Layer/Location Specified

This is the earliest design document for the associate system. It pre-dates the harness-pattern formalization (which came in 2026-04-10-realtime-architecture-design.md). Key layer statements:

- **The deep agent runs in a sandbox** (Daytona). Not in the kernel. Not in the API server. Not in the Temporal worker. In an isolated sandbox per invocation.
- **Sandbox has the indemn CLI pre-installed and authenticated.** The agent only has access to what the CLI allows.
- **Associates act through CLI commands via `execute()`.** "The agent reads its skills, reasons about what to do, and executes CLI commands in a sandbox."
- **Web operators share the sandbox + harness pattern.** Browser automation capabilities are "added to the sandbox" — same mechanism as CLI execution.
- **Trigger → Sandbox → Execution → Results flow** (line 146-156):
  1. Trigger fires (event, schedule, always-on, API call)
  2. Sandbox provisioned (Daytona spins up isolated environment with indemn CLI pre-installed)
  3. Deep agent created (`create_deep_agent()` with skills, knowledge bases, LLM config, sandbox backend)
  4. Agent reasons and acts (reads skills, uses todo list, executes CLI commands, handles deviations)
  5. Results flow back (entity state changes, events emitted, observable via tracing)
  6. Sandbox cleaned up (after completion or timeout)

**The sandbox is the agent's execution boundary.** The agent never has direct database access, never has kernel-level privileges, only has the CLI scoped to its associate's permissions.

This design does NOT explicitly say "the agent runs outside the kernel trust boundary in a separate image" — that formalization came later in 2026-04-10-realtime-architecture-design.md. But the structure is completely consistent: sandbox-based execution where the agent talks to the kernel through CLI with service-token auth.

**The Workflow runner, by contrast, is less clearly placed.** Line 319-329 leaves the runner implementation open: custom Python runner, Temporal, or blueprint engine. No explicit layer prescription.

## Dependencies Declared

- `deepagents` package (LangChain deep agents) — the core framework
- LangGraph (StateGraph, middleware stack)
- Daytona (sandbox provider — evaluating)
- `indemn` CLI (installed in the sandbox)
- LangSmith (evaluation framework — not LangFuse)
- Browser automation (Playwright or similar — for web operators, added to sandbox)
- Claude Code as reference architecture

## Code Locations Specified

- **`deepagents` package** — external library, imported
- **Sandbox** — runs in Daytona (external)
- **CLI** — pre-installed in sandbox image
- **Skills** — stored in OS (auto-generated entity skills + human-authored workflow skills), loaded via progressive disclosure from SKILL.md files
- **Workflow runner** — Python (~300-500 lines for custom MVP), or Temporal, or blueprint engine. Exact codebase location not specified; it's the orchestrator that reads Workflow entities and dispatches steps.

## Cross-References

- 2026-04-10-realtime-architecture-design.md — FORMALIZES what this artifact introduces: the harness pattern, Runtime entity, one image per kind+framework combo, ~60-line harness script
- 2026-04-09-entity-capabilities-and-skill-model.md — the skill model (entity skills auto-generated, workflow skills human-authored)
- 2026-04-09-data-architecture-everything-is-data.md — the entity framework
- Hive blueprint system (referenced as possible workflow runner)
- Jarvis, Intake Manager (existing Indemn agents using deepagents)

## Open Questions or Ambiguities

- **Sandbox provider**: Daytona is explicitly "being considered" but not locked. Line 55-62.
- **Workflow runner**: explicitly deferred. "Start with a custom runner for MVP. Migrate to Temporal or blueprint engine when reliability requirements demand it." Line 329.
- **Relationship between Workflow entity and the associate's deep agent loop**: The Workflow entity has step types including `associate` (invoke an associate with an objective). But this artifact doesn't resolve how the workflow runner interacts with the sandbox-based associate execution. This was resolved later in the realtime architecture design (Runtime entity + harness pattern + Temporal task queue for async runtimes).
- **No explicit kernel/image boundary stated here.** The boundary is implied by the sandbox (agent lives in sandbox), but the formal "harnesses are separate deployable images outside the kernel's trust boundary" language came in 2026-04-10-realtime-architecture-design.md.

**Pass 2 check on sandbox**: The comprehensive audit's section 3a asks: "Is sandbox execution implemented? Per design, sandboxes wrap agent execution. With agent execution in-kernel, where would sandboxes go?" Per this artifact + the realtime architecture design, sandboxes wrap agent execution in the harness. The current kernel code (per Finding 0) has no harness, so sandbox execution is also not present — the agent loop in `kernel/temporal/activities.py` does not run in Daytona or any sandbox. This is a **secondary consequence of Finding 0**.
