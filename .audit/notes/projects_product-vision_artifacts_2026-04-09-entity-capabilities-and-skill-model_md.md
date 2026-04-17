# Notes: 2026-04-09-entity-capabilities-and-skill-model.md

**File:** projects/product-vision/artifacts/2026-04-09-entity-capabilities-and-skill-model.md
**Read:** 2026-04-16 (full file — 251 lines)
**Category:** design-source

## Key Claims

- Three layers for entity operations:
  1. **Kernel capabilities** — reusable Python operations built into the OS (code)
  2. **Per-org configuration** — rules, thresholds, patterns, mappings (data via CLI)
  3. **Skills** — markdown orchestration that associates read
- **Entity methods aren't custom code per entity.** They're kernel capabilities activated on an entity type and configured per org.
- Capability library (universal, code in kernel):
  - `auto-classify` — Evaluate rules against entity fields, set classification
  - `fuzzy-search` — Text similarity search with configurable threshold
  - `pattern-extract` — Extract structured data from text using patterns
  - `stale-check` — Find entities past time/count/value thresholds
  - `auto-route` — Determine routing/assignment based on field rules
  - `external-sync` — Push/pull entity data to/from external system
  - `auto-link` — Match entities across types using references/fuzzy match
  - `rule-evaluate` — Generic rule evaluation — match conditions, return actions
- **Library grows over time**. New capability = OS code addition. Activating/configuring is always CLI.
- **`--auto` pattern**: try deterministic rules first, flag for reasoning if insufficient. Returns `needs_reasoning` with context if no match.
- **Skills stay markdown.** Always. They describe orchestration and reasoning.
- Rejected alternatives for skill format: custom DSL (GET/CHECK/RUN), Python code as skills, embedded code in markdown, always-LLM.
- "AWS model": new services (capabilities) are built by engineers. Using them is configuration + CLI.

## Architectural Decisions

- **Kernel capabilities = Python code in the OS, universally available.** The capability library is part of the kernel, not per-entity code.
- **Per-org configuration = rules and lookups stored as data** (Rule and Lookup entities), created via CLI, no code.
- **Skill interpreter reads markdown.** Skills are markdown files describing orchestration and calling CLI commands. The LLM executes them.
- **LLM invocation only when deterministic path fails** (the `--auto` pattern's `needs_reasoning` return value).
- **No per-org code.** An FDE or associate sets up a new org entirely via CLI — no Python required.
- **Tier 3 adapter/capability contribution**: new capability needing a kernel addition = "Indemn engineer (or Tier 3 developer) builds it and adds it to the OS."
- **Deterministic mode for associates** — e.g., Stale Checker: `--mode deterministic`. No LLM, just executes the one command.
- **Capability activation is per-entity-type**, configured with `--evaluates <rule-type>` and `--sets-field <field>` parameters.

## Layer/Location Specified

- **Kernel capabilities**: "Code (Python, maintained by Indemn/Tier 3 developers)" — live in the kernel codebase as code additions. Code location.
- **Per-org configuration**: "Data (created via CLI, stored as entities)" — data in MongoDB, not code. Data location.
- **Skills**: "Markdown (read by LLM, readable by humans)" — data, stored in database, loaded by associates at invocation.
- **Capability registry**: implied to be part of the kernel (capabilities are "code in the OS"). Not stated where specifically; follows from "kernel capability" framing.

**Skill interpreter/execution:**
- This artifact does NOT explicitly place the skill interpreter in the kernel vs. outside.
- It says "The LLM is only invoked when kernel capabilities can't handle it" — implying the LLM-invoking component is somewhere that can call the capability library.
- **Later resolved** by 2026-04-10-realtime-architecture-design.md: the skill-interpreting agent runs in a harness (outside kernel). The harness calls the CLI, which calls the kernel's capability code, which returns `needs_reasoning` back to the harness.
- **The `--auto` capability itself runs kernel-side.** When `indemn email classify --auto` is called, the kernel evaluates rules against the entity. The call site (the CLI call) may come from anywhere — human, associate in harness, another automation — but the evaluation is kernel-side.

**Deterministic associates** (like the Stale Checker with `--mode deterministic`) are interesting — they don't use LLM. The design says they "read the skill, executes the one command." This is likely still sandbox/harness-based execution per the Layer 3 artifact; they just skip the LLM reasoning step.

## Dependencies Declared

- Python (for capability code)
- MongoDB (for Rule, Lookup, Skill entities)
- CLI (for all configuration)
- LLM (Claude / similar) for reasoning fallback when `--auto` returns `needs_reasoning`
- Regex engine (for pattern-extract capability)
- Fuzzy match library (for fuzzy-search capability)

## Code Locations Specified

- **Kernel capabilities**: Python code "in the OS kernel". No specific directory named in this artifact.
- **Capability registry**: referenced as a lookup concept; no specific file path.
- **Rules and Lookups**: data in MongoDB, not code. Created/managed via CLI.

## Cross-References

- 2026-04-08-primitives-resolved.md
- 2026-04-08-actor-references-and-targeting.md
- 2026-03-30-design-layer-3-associate-system.md — the associate system that reads skills and executes CLI
- 2026-04-10-realtime-architecture-design.md — resolves WHERE the LLM-based skill interpreter runs (in harness)

## Open Questions or Ambiguities

- **Where the skill interpreter/agent runs is not explicitly stated here.** It's implicit that it's a separate thing calling the CLI, but the artifact doesn't name the location. Resolved by the realtime architecture design.
- **Rule engine location**: not explicit. "Kernel evaluates rules" language — so rule engine is in the kernel. Confirmed by Pass 1 audit which verified rule engine in `kernel/rule/engine.py`.
- **Skill schema and integrity**: this artifact says skills are markdown. Doesn't detail tamper-evidence or version approval (those are in the white paper + base UI design and auth design).

**Pass 2 check on skill execution location**: Per this artifact and the realtime architecture design, the skill interpreter (deterministic interpreter or LLM) runs in the harness (outside kernel). The current code has the skill interpreter inside `kernel/temporal/activities.py::_execute_reasoning` (LLM path) and corresponding deterministic path also in the kernel. **Skill execution location is wrong in the current code — it's a secondary consequence of Finding 0.**

**Pass 2 check on capability library**: This artifact says capabilities are Python code in the kernel — which aligns with the current implementation (capabilities in `kernel/capability/`). No layer deviation expected here.

**Pass 2 check on skill tamper-evidence**: Skills are stored in DB, versioned through changes collection, updatable through CLI. Per the white paper § Security, "Skills are tamper-evident. Content hashes are computed on creation and verified on load." This is a kernel-side function (hash check at load time). Current code has `kernel/skill/integrity.py` — needs verification that this integrity is actually invoked when skills are loaded by the (currently kernel-side) agent execution.
