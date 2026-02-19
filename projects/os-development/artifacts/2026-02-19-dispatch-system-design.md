---
ask: "How to build an operating system that orchestrates Claude Code sessions to do dev work across repos, with persistent context, skills integration, and autonomous execution loops"
created: 2026-02-19
workstream: operating-system
session: 2026-02-19
sources:
  - type: web
    description: "Claude Agent SDK docs — overview, Python API reference, skills integration, quickstart"
    ref: "https://platform.claude.com/docs/en/agent-sdk/overview"
  - type: web
    description: "Claude Code headless/programmatic docs — CLI flags, session management, multi-repo"
    ref: "https://code.claude.com/docs/en/headless"
  - type: web
    description: "Ralph Wiggum loop pattern — autonomous iteration, stop hooks, backstop criteria"
    ref: "https://github.com/snarktank/ralph"
  - type: web
    description: "Agent SDK Max plan billing workaround (Issue #559)"
    ref: "https://github.com/anthropics/claude-agent-sdk-python/issues/559"
  - type: web
    description: "Claude Code multi-repo context loading, --add-dir, CLAUDE.md hierarchy"
    ref: "https://code.claude.com/docs/en/memory"
  - type: web
    description: "Agent Skills in SDK — setting_sources, Skill tool, filesystem discovery"
    ref: "https://platform.claude.com/docs/en/agent-sdk/skills"
---

# Design: Dispatch System & Operating System Architecture

**Date:** 2026-02-19
**Status:** Draft — design conversation complete, ready for implementation

## Problem

The operating system is the command center for all work — it has skills (tool connections), projects (memory/context), and the ability to connect to every service we use. But when dev work needs to happen in service repos (bot-service, indemn-platform-v2, web_operators, etc.), there's no mechanism to orchestrate that work autonomously from the OS. Today, you manually context-switch between the OS and repos, losing continuity.

## Vision

The OS creates well-defined specs. A dispatch system executes those specs by running autonomous Claude Code sessions in target repos, with managed context and verification loops, until the work meets acceptance criteria. The OS is the brain; dispatch is the hands.

---

## Architecture: Three Primitives

### Skills (capabilities — "I can do X")
- Tool skills: slack, github, postgres, mongodb, etc.
- Workflow skills: call-prep, weekly-summary, follow-up-check
- System skills: content-*, dispatch, project
- Everything is a skill. Skills are the atoms of the OS.

### Projects (memory — "I'm working on Y")
- Each project has INDEX.md, artifacts/, .beads/
- Projects accumulate context, decisions, and artifacts over time
- Projects eventually complete
- Projects create well-defined **specs** for work that needs doing
- Projects reference target repos where code lives

### Systems (processes — "I produce Z through this process")
- Persistent operational workflows that don't "finish"
- Each system has skills + state + configuration
- Systems are cross-cutting — any project can use any system
- Examples: content creation, dispatch/execution

**Key relationships:**
- Projects USE systems (dispatch a feature, create content)
- Systems USE skills (dispatch uses claude CLI, content uses vercel for publishing)
- Skills are stateless atoms; projects accumulate state; systems are persistent infrastructure

---

## Directory Structure

```
operating-system/
├── CLAUDE.md                     # Index of everything
├── .claude/skills/               # ALL skills
│   ├── slack/                    # Tool skill
│   ├── github/                   # Tool skill
│   ├── project/                  # Meta skill
│   ├── dispatch/                 # System skill (NEW)
│   ├── content/                  # System skill (exists, symlinked from content-system)
│   └── ...
│
├── projects/                     # Memory layer
│   ├── web-operator/
│   ├── platform-development/
│   └── ...
│
├── systems/                      # Operational infrastructure (NEW)
│   └── dispatch/                 # Dispatch engine
│       ├── SYSTEM.md             # System definition
│       ├── engine.py             # The ralph loop (Python, Agent SDK)
│       ├── workflows/            # Workflow-specific prompt templates
│       └── sessions/             # Completed session logs
│
└── docs/
```

**Note:** Content system stays as a separate repo for now. Moving it in is a future step.

---

## Dispatch System Design

### Core Concept: Ralph Wiggum Loop

Dispatch is a **ralph loop** — a persistent iteration loop that grinds through a spec task by task until everything passes verification.

```
1. Read the spec (task list with pass/fail status)
2. Pick the next incomplete task
3. Spawn a FRESH Claude Code session with managed context
4. Session works on the single task
5. Run verification (tests, separate Claude session, or both)
6. If pass: mark done, commit, record learnings
7. If fail: loop with failure as new context
8. Repeat until all tasks pass or max iterations hit
```

### Critical Design Principle: Fresh Context Per Task

Each task gets its own **fresh context window**. No token carryover between tasks. The dispatch engine controls exactly what context goes into each session:

- The spec (what to do)
- Learnings from previous tasks (append-only file)
- Git history (what code already exists)
- Project-specific context (decisions, constraints from INDEX.md)
- Repo CLAUDE.md (code conventions, loaded automatically via cwd)
- OS skills (available via --add-dir or setting_sources)

**Why fresh context matters:**
- Each task gets maximum context window for its specific work
- No pollution from previous tasks
- If a task fails, retry just that task
- Clear separation of concerns
- More robust than accumulating context

### State Machine: Three Files

The entire dispatch state is three persistent artifacts:

1. **The spec** — JSON/YAML with tasks, acceptance criteria, pass/fail status
2. **Learnings file** — append-only, carries forward between iterations
3. **Git history** — the actual code, accumulates across tasks

### Verification

Verification can be:
- **Automated**: tests pass, typecheck passes, linter clean
- **Claude-judged**: a SEPARATE fresh Claude session reviews the work against acceptance criteria
- **Both**: automated checks first, then Claude review

The verifier is always a separate session from the implementer — independent judgment.

---

## Technical Implementation

### Mechanism: Agent SDK (Python)

The dispatch engine is a Python application using the `claude-agent-sdk` package.

**Package:** `claude-agent-sdk` (installed, v0.1.38)

**Auth options:**
1. `claude -p` via subprocess — uses Claude Code subscription (guaranteed to work)
2. Agent SDK with `CLAUDE_CODE_OAUTH_TOKEN` — uses subscription billing via SDK
   - Run `claude setup-token` to get token
   - Export as env var
   - Confirmed working per GitHub Issue #559 (closed as completed)

**Nested session issue:** SDK/CLI cannot run inside a Claude Code session by default. Must unset `CLAUDECODE` env var or use `env -u CLAUDECODE python3 engine.py`.

### Key SDK Capabilities

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Implement the scoring UI component",
    options=ClaudeAgentOptions(
        cwd="/path/to/target/repo",              # Work IN the target repo
        add_dirs=["/path/to/operating-system"],   # Access OS files
        setting_sources=["user", "project"],      # Load CLAUDE.md + skills
        allowed_tools=["Skill", "Read", "Write", "Edit", "Bash", "Glob", "Grep", "Task"],
        permission_mode="acceptEdits",            # Autonomous execution
        system_prompt={"type": "preset", "preset": "claude_code", "append": context},
        max_turns=40,
        max_budget_usd=10.0,
        output_format={"type": "json_schema", "schema": {...}},  # Structured output
    ),
):
    ...
```

**Critical settings:**
- `setting_sources=["user", "project"]` — loads CLAUDE.md AND skills from both `~/.claude/skills/` and the repo's `.claude/skills/`
- `"Skill"` in `allowed_tools` — enables skill invocation in dispatched sessions
- `add_dirs` — gives access to OS files (project context, learnings)
- `cwd` — sets working directory to target repo
- `output_format` with JSON schema — structured verification results

### Skills Availability in Dispatched Sessions

Skills work in SDK sessions. With `setting_sources=["user", "project"]`:
- Skills in `~/.claude/skills/` are available (user-level)
- Skills in `<cwd>/.claude/skills/` are available (project-level)
- OS tool skills should be symlinked to `~/.claude/skills/` for global access

### Multi-Repo Context

When a dispatched session runs in a target repo:
1. **Repo CLAUDE.md** — auto-loaded (it's the cwd)
2. **Parent CLAUDE.md** — `/Users/home/Repositories/CLAUDE.md` auto-loaded (parent directory traversal)
3. **OS CLAUDE.md** — loaded via `add_dirs` pointing at operating-system/
4. **OS files** — accessible via `add_dirs` (project INDEX.md, learnings, etc.)
5. **Skills** — available via `setting_sources` + `~/.claude/skills/` symlinks

### CLI Alternative

If SDK auth doesn't work with subscription, `claude -p` is the fallback:

```bash
env -u CLAUDECODE claude -p "$PROMPT" \
  --append-system-prompt-file context.md \
  --add-dir /path/to/operating-system \
  --output-format json \
  --json-schema '{"type":"object","properties":{"status":{"type":"string"}}}' \
  --allowedTools "Read,Write,Edit,Bash,Glob,Grep" \
  --max-turns 30 \
  --max-budget-usd 5
```

**Note:** Skills do NOT load in `claude -p` mode. Only in SDK with `setting_sources`.

---

## The Dispatch Skill

The dispatch skill lives at `.claude/skills/dispatch/SKILL.md`. It tells the interactive OS session how to invoke the dispatch engine.

**What it does:**
1. Takes a spec from a project (well-defined tasks + acceptance criteria)
2. Confirms target repo and workflow with user
3. Runs the Python dispatch engine via Bash
4. Parses results
5. Updates project state (INDEX.md, beads, artifacts)

**The skill is the interface. The engine is the implementation.**

---

## The Spec Format

Specs are created in the OS (by you + Claude during project work). They define:

```yaml
name: "Scoring UI Component"
project: platform-development
target_repo: /Users/home/Repositories/indemn-platform-v2
backstop: "npm test passes AND scoring UI renders correctly"

tasks:
  - id: 1
    description: "Create ScoringTable component with rubric results display"
    acceptance: "Component renders rubric items with pass/fail indicators"
    passes: false
  - id: 2
    description: "Add overall score calculation and display"
    acceptance: "Score percentage shown, calculated from rubric results"
    depends_on: [1]
    passes: false
  - id: 3
    description: "Wire ScoringTable into evaluation detail view"
    acceptance: "Clicking an eval shows scoring tab with real data"
    depends_on: [1, 2]
    passes: false

context:
  index: projects/platform-development/INDEX.md
  decisions:
    - "Use React with Tailwind for new UI components"
    - "Evaluation data comes from /api/evaluations/:id endpoint"
  files_to_read:
    - "src/components/evaluations/"
    - "src/api/evaluations.ts"
```

---

## Integration with Projects

The flow:
```
1. You work in the OS on a project
2. Through conversation, you build a well-defined spec
3. You say "dispatch this"
4. Dispatch skill:
   a. Reads project INDEX.md for additional context
   b. Writes spec to systems/dispatch/specs/
   c. Runs engine.py with the spec
   d. Engine grinds through tasks (ralph loop)
   e. Results return
5. Dispatch skill:
   a. Updates project INDEX.md with what was accomplished
   b. Saves artifact if significant
   c. Marks beads complete
   d. Reports summary
```

---

## SYSTEM.md Convention

Like projects have INDEX.md, systems have SYSTEM.md:

```markdown
# System Name

What this system does in one paragraph.

## Capabilities
What this system can produce or do.

## Skills
| Skill | Purpose |
|-------|---------|
| /dispatch | Entry point — takes a spec, runs the loop |

## State
Where runtime state lives.

## Dependencies
What tools/skills this system requires.

## Integration Points
- Reads from: project specs, INDEX.md context
- Produces: code changes, PRs, verification results
- Reports to: project artifacts and beads
```

---

## What Was Tested

### claude-agent-sdk installation
- **Result:** Installed successfully via `uv pip install claude-agent-sdk` (v0.1.38)
- **Python:** 3.12.12 at `/Users/home/Repositories/.venv/bin/python3`
- **uv:** 0.9.22 at `/opt/homebrew/bin/uv`

### SDK auth with subscription (no API key)
- **Result:** Blocked by nested session detection. Running the SDK from within a Claude Code session fails with "Claude Code cannot be launched inside another Claude Code session"
- **Workaround:** Must unset `CLAUDECODE` env var: `env -u CLAUDECODE python3 engine.py`
- **Still untested:** Whether the SDK authenticates with the subscription after bypassing the nested check. Needs manual test outside of Claude Code.
- **Alternative auth:** `claude setup-token` + `CLAUDE_CODE_OAUTH_TOKEN` env var (confirmed working per GitHub Issue #559)

### claude -p with subscription
- **Status:** Known to work. `claude -p` uses whatever auth is configured. Subscription auth is the default.

---

## Open Questions

1. **SDK + subscription auth:** Does the SDK authenticate with the Claude Code subscription after bypassing the nested session check? Need to test `env -u CLAUDECODE python3 test_sdk.py` manually.
2. **Skills in dispatched sessions:** Confirmed possible with `setting_sources=["user", "project"]` + `Skill` in `allowed_tools`. Need to verify OS skills are accessible when cwd is a different repo.
3. **Spec format:** YAML above is a starting point. Should it be JSON (easier to parse programmatically) or Markdown (easier to write in conversation)?
4. **OS tool skills symlinks:** Which skills should be symlinked to `~/.claude/skills/` for global access? All of them? Just the tool skills?
5. **Verification strategy:** When should verification be automated (tests) vs Claude-judged (separate session)? Both?
6. **Engine error handling:** What happens when a task exceeds max iterations? Skip and continue? Abort? Report and ask?

---

## Next Steps (Priority Order)

1. **Test SDK auth manually** — run `env -u CLAUDECODE python3 test_sdk.py` from a terminal (outside Claude Code) to verify subscription auth works
2. **Create systems/ directory** — establish the convention, write first SYSTEM.md for dispatch
3. **Build dispatch engine** — Python ralph loop using SDK (or claude -p fallback), spec-driven, fresh context per task
4. **Build dispatch skill** — `.claude/skills/dispatch/SKILL.md` following OS skill conventions
5. **Define spec format** — finalize the format, build a template
6. **Symlink OS skills** — make tool skills globally accessible for dispatched sessions
7. **Integration test** — dispatch a small task to a real repo, verify full loop works
8. **Connect to projects** — wire dispatch results back into INDEX.md and beads

---

## Key Decisions Made

- 2026-02-19: OS architecture has three primitives: Skills (capabilities), Projects (memory), Systems (processes)
- 2026-02-19: Dispatch is a skill + system, not a separate tool. It fits within the OS's existing patterns.
- 2026-02-19: Dispatch uses the Ralph Wiggum loop pattern — persistent iteration, fresh context per task, file-based state
- 2026-02-19: Each task gets its own fresh context window. The system controls what context goes in. No multi-turn accumulation.
- 2026-02-19: Verification is always a SEPARATE session from implementation — independent judgment
- 2026-02-19: Agent SDK (claude-agent-sdk v0.1.38) is installed. CLI fallback (claude -p) available if SDK auth doesn't work.
- 2026-02-19: Content system stays as a separate repo for now. Moving it into systems/ is a future step.
- 2026-02-19: GSD is out of scope — building our own dispatch that fits the OS patterns

---

## Technical Reference

### Claude Code CLI (v2.1.47)
- Location: `/Users/home/.local/bin/claude`
- Auth: subscription (no API key)

### Key CLI Flags for Dispatch
| Flag | Purpose |
|------|---------|
| `-p "prompt"` | Headless/non-interactive mode |
| `--append-system-prompt-file` | Inject context without replacing default prompt |
| `--add-dir` | Add additional directories (OS access from repo) |
| `--output-format json` | Structured JSON output with metadata |
| `--json-schema '{...}'` | Validate output against schema |
| `--allowedTools "Read,Edit,Bash"` | Pre-approve tools for autonomous execution |
| `--max-turns N` | Limit agentic turns |
| `--max-budget-usd N` | Spending cap |
| `--resume $session_id` | Continue a specific session |

### Key SDK Options for Dispatch
| Option | Purpose |
|--------|---------|
| `cwd` | Set working directory to target repo |
| `add_dirs` | Additional directories (OS access) |
| `setting_sources=["user", "project"]` | Load CLAUDE.md + skills |
| `allowed_tools=["Skill", ...]` | Enable skills + tools |
| `permission_mode="acceptEdits"` | Autonomous execution |
| `system_prompt={"type": "preset", "preset": "claude_code", "append": "..."}` | Extend default prompt |
| `output_format={"type": "json_schema", "schema": {...}}` | Structured output |
| `max_turns` | Turn limit |
| `max_budget_usd` | Budget limit |
| `hooks` | Pre/post tool use callbacks |
| `agents` | Define custom subagents |

### CLAUDE.md Hierarchy (loads automatically)
1. Parent directories above cwd (traverses up to /) — loaded at launch
2. cwd CLAUDE.md — loaded at launch
3. Child directories — loaded on demand when files accessed
4. `--add-dir` directories — loaded if `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`

### Nested Session Workaround
SDK and `claude -p` cannot run inside a Claude Code session by default. Bypass:
```bash
env -u CLAUDECODE python3 engine.py
# or
env -u CLAUDECODE claude -p "..."
```
