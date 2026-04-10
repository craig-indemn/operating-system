---
ask: "How do associates, workflows, and evaluations work on the OS?"
created: 2026-03-30
workstream: product-vision
session: 2026-03-30-a
sources:
  - type: conversation
    description: "Craig and Claude design session, 2026-03-30"
  - type: research
    description: "Deep agents architecture research — deepagents package, middleware stack, sandbox execution"
  - type: local
    description: "Hive blueprint system design — projects/os-development/artifacts/2026-03-24-blueprint-*.md"
---

# Design: Layer 3 — Associate System

## Core Principle: An Associate IS Claude Code for Insurance

The associate is a LangChain deep agent with the same architecture as Claude Code:
- **Skills** (SKILL.md files) describe what it can do — loaded via progressive disclosure
- **Sandbox** with `execute()` provides CLI access — the agent runs `indemn` CLI commands directly
- **Todo list** for multi-step task management
- **Subagents** for parallel/complex sub-tasks
- **Summarization** for long-running operations (auto-compacts at 85% context)
- **Human-in-the-loop** for steps requiring approval

No "tools" abstraction. No client library wrapper. The agent reads its skills, reasons about what to do, and executes CLI commands in a sandbox. The auto-generated entity skills from Layer 2 feed directly into this — they document every CLI command the associate can use.

## Deep Agent Architecture (from `deepagents` package)

`create_deep_agent()` builds a LangGraph StateGraph with middleware stack:

1. **TodoListMiddleware** — planning/task tracking (`write_todos` tool)
2. **MemoryMiddleware** — loads persistent context (AGENTS.md files)
3. **SkillsMiddleware** — progressive disclosure skill loading from SKILL.md files
4. **FilesystemMiddleware** — `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `execute` tools
5. **SubAgentMiddleware** — `task` tool for spawning ephemeral subagents
6. **SummarizationMiddleware** — auto-compacts context at 85% of model capacity
7. **HumanInTheLoopMiddleware** — pause for approval at configured steps

The `execute` tool runs shell commands in the sandbox backend. This is how the associate runs CLI commands:
```
execute("indemn submission create --from-email EMAIL-001 --product PROD-001")
→ returns stdout (JSON result) + stderr + exit code
```

### Sandbox Backends

| Backend | Use Case |
|---------|----------|
| **BaseSandbox** | Production — all operations via `execute()` in an isolated environment |
| **FilesystemBackend** | Skills loading — reads SKILL.md files from disk with virtual path jailing |
| **StateBackend** | Ephemeral — files in agent state, no CLI (testing only) |

**Daytona** is being considered as the sandbox provider:
- Isolated environment per associate invocation
- Pre-configured with `indemn` CLI and associate's auth credentials
- Secure — agent can't escape the sandbox
- Scalable — spin up/down on demand
- Clean up after each invocation
- Potentially free credits for startups

### Web Operators — Same Harness

Web operators (deep agents that interact with external websites/portals) use the same deep agent harness with browser automation capabilities added to the sandbox. Same middleware stack, same skills pattern, same `execute()` mechanism — the sandbox just also has browser tools (Playwright or similar).

Use cases: automating carrier portals that don't have APIs, interacting with AMS systems, scraping data from external sources.

## Associate as an Entity

An Associate is a first-class entity in the platform sub-domain, created and managed through the same CLI as everything else:

```python
class Associate(Entity):
    sub_domain = "platform"

    name: str                          # "GIC Intake Associate"
    type: str                          # "intake", "renewal", "front-desk", "web-operator"
    status: Literal["configured", "testing", "deployed",
                     "active", "paused", "retired"] = "configured"

    # What it can do
    skills: list[str]                  # Skill names to load
    knowledge_bases: list[Link["KnowledgeBase"]]

    # What it can access
    entity_permissions: dict           # {read: ["submission", "email"], write: ["submission", "draft"]}

    # How it connects
    channels: list[dict]               # [{type: "email", provider: "outlook", config: {...}}]
    triggers: list[dict]               # [{type: "event", event: "email.received"}, {type: "schedule", cron: "0 8 * * *"}]

    # Agent configuration
    llm_config: dict                   # {model: "claude-sonnet-4-6", temperature: 0}
    sandbox_config: dict               # {provider: "daytona", image: "indemn-os-sandbox"}

    state_machine = {
        "configured": ["testing"],
        "testing": ["deployed", "configured"],
        "deployed": ["active", "paused"],
        "active": ["paused", "retired"],
        "paused": ["active", "retired"],
    }

    class Settings:
        name = "associates"
```

### Creating an Associate via CLI

```bash
# Create
indemn associate create --name "GIC Intake" --type intake

# Configure skills
indemn associate add-skill ASSOC-001 --skill submission-processing
indemn associate add-skill ASSOC-001 --skill email-classification
indemn associate add-skill ASSOC-001 --skill document-extraction

# Configure entity access
indemn associate configure ASSOC-001 \
  --read "submission,email,carrier,agent,coverage,lob" \
  --write "submission,draft,document,task"

# Connect channels and triggers
indemn associate connect-channel ASSOC-001 --type email --provider outlook --config @outlook.json
indemn associate add-trigger ASSOC-001 --type event --event email.received

# Set LLM config
indemn associate configure ASSOC-001 --model claude-sonnet-4-6 --temperature 0

# Test
indemn associate transition ASSOC-001 --to testing
indemn eval run --associate ASSOC-001 --rubric intake-quality --test-set gic-emails

# Deploy
indemn associate transition ASSOC-001 --to deployed
indemn associate transition ASSOC-001 --to active
```

This is Tier 3 in action. Every step goes through the CLI. An AI agent could execute this entire sequence to create and deploy a new associate.

## How an Associate Runs

### Trigger → Sandbox → Execution → Results

1. **Trigger fires** — event (email.received), schedule (cron), always-on (websocket), or API call
2. **Sandbox provisioned** — Daytona spins up isolated environment with `indemn` CLI pre-installed, authenticated with associate's permissions
3. **Deep agent created** — `create_deep_agent()` with:
   - Skills loaded from associate's skill list (progressive disclosure)
   - Knowledge bases loaded into memory/RAG
   - LLM config from associate entity
   - Sandbox backend pointing to the provisioned environment
4. **Agent reasons and acts** — reads skills, uses todo list for planning, executes CLI commands, handles deviations
5. **Results flow back** — entity state changes (new submissions, drafts, tasks), events emitted, observable via tracing
6. **Sandbox cleaned up** — after completion or timeout

### What the Associate Sees

The associate's sandbox has:
- The `indemn` CLI installed and authenticated (scoped to its org + entity permissions)
- Its skill files available to read
- A workspace for scratch files
- No access to anything outside the sandbox

The associate reads its skills (which describe CLI commands), reasons about the input, executes CLI commands, and produces results. Exactly like Claude Code reading skill files and running bash commands.

### Entity Permissions in the Sandbox

The `indemn` CLI in the sandbox is authenticated with a service token scoped to:
- The associate's organization (org_id)
- The associate's entity permissions (read/write lists)

If the associate tries `indemn policy delete POL-001` and it doesn't have policy write permission, the CLI returns a permission error. The entity layer enforces this, not the sandbox.

## Skills

### Auto-Generated Entity Skills

Every entity in the OS auto-generates a SKILL.md file (from Layer 2's skill generator). These describe all CLI commands for that entity:

```markdown
---
name: submission
description: Create, query, and manage insurance submissions
---
# Submission

The central pre-bind entity. Covers broker-submitted packages and consumer applications.

## Commands
| Command | Description |
|---------|-------------|
| `indemn submission list` | List submissions with filters |
| `indemn submission get <id>` | Get submission details |
| `indemn submission create` | Create a new submission |
| `indemn submission validate <id>` | Check completeness against product schema |
| `indemn submission route <id>` | Route to carrier based on workflow rules |
| `indemn submission extract <id>` | Extract data from attached documents |

## Lifecycle
received → triaged → processing → quoted → bound/declined/expired

[... full documentation ...]
```

### Workflow Skills (Human-Authored)

In addition to entity skills, associates have workflow skills that describe HOW to combine entity operations for specific workflows:

```markdown
---
name: submission-processing
description: Process incoming insurance submissions end-to-end
---
# Submission Processing

## When to Use
When a new email arrives that needs to be processed as an insurance submission.

## Process
1. Classify the email: `indemn email classify --id {email_id}`
2. If not a submission, create a manual review task and stop
3. Identify the product/LOB from the email content
4. Create submission: `indemn submission create --from-email {email_id} --product {product_id}`
5. Extract data from attachments: `indemn submission extract --id {sub_id}`
6. Validate completeness: `indemn submission validate --id {sub_id}`
7. If incomplete:
   - Draft an info request: `indemn draft create --type info-request --submission {sub_id}`
   - The draft will include what's missing based on the validation result
8. If complete:
   - Route to carrier: `indemn submission route --id {sub_id}`

## Important
- Always check the product's form_schema to understand what fields are required
- Some carriers have specific submission requirements — check carrier appetite
- If unsure about classification, escalate to a human via task creation
```

The entity skills tell the associate WHAT operations exist. The workflow skills tell it WHEN and HOW to combine them.

### Skill Composition

An associate is configured with both:
- **Entity skills** (auto-generated): submission, email, carrier, draft, task, etc.
- **Workflow skills** (human-authored or AI-generated): submission-processing, renewal-monitoring, etc.

The entity permissions control which entity skills are available. The workflow skills reference only entities the associate has access to.

## Workflow Entity

For deterministic or hybrid workflows that need to be configurable per customer without writing code:

```python
class Workflow(Entity):
    sub_domain = "platform"

    name: str
    description: str
    trigger: dict               # {type: "event", event: "email.received"} or {type: "schedule", cron: "..."}
    steps: list[dict]           # Ordered steps
    status: Literal["draft", "active", "paused", "deprecated"] = "draft"

    state_machine = {
        "draft": ["active"],
        "active": ["paused", "deprecated"],
        "paused": ["active", "deprecated"],
    }

    class Settings:
        name = "workflows"
```

### Step Types

| Type | What | LLM Required? |
|------|------|---------------|
| **cli** | Execute an `indemn` CLI command | No — deterministic |
| **condition** | Branch based on entity state or previous step output | No — deterministic |
| **associate** | Invoke an associate with an objective | Yes — reasoning |
| **sub-workflow** | Run another workflow (fractal) | No — delegation |
| **wait** | Pause until a condition is met or time elapses | No — timer |

### Creating Workflows via CLI

```bash
# Create
indemn workflow create --name "GIC Intake" --trigger '{"type": "event", "event": "email.received"}'

# Add deterministic steps
indemn workflow add-step WF-001 --type cli \
  --command "indemn email classify --id {email_id}" \
  --output-var "classification"

indemn workflow add-step WF-001 --type condition \
  --if "classification.type == 'new_submission'" \
  --then next --else step-manual

indemn workflow add-step WF-001 --type cli \
  --command "indemn submission create --from-email {email_id}"

# Add associate step for reasoning
indemn workflow add-step WF-001 --type associate \
  --associate extraction-associate \
  --objective "Extract and validate submission data for {submission_id}"

# Add deterministic routing
indemn workflow add-step WF-001 --type cli \
  --command "indemn submission route --id {submission_id}"

# Manual review fallback
indemn workflow add-step WF-001 --id step-manual --type cli \
  --command "indemn task create --type manual-review --email {email_id}"

# Activate
indemn workflow transition WF-001 --to active
```

### Workflow Runner (Decision Deferred)

The workflow runner reads Workflow entities and executes their steps. Runner implementation options:

| Option | Pros | Cons | When |
|--------|------|------|------|
| **Custom runner** (~300-500 lines Python) | Simple, fast to build, no dependencies | Basic error handling, manual recovery | MVP |
| **Temporal** | Durable execution, automatic retries, battle-tested | Operational overhead, learning curve | At scale, high-stakes workflows |
| **Blueprint runner** (from Hive, potentially open-sourced) | Craig knows it, supports agent steps natively | Designed for different runtime (OS sessions vs. platform service) | If open-sourced and adapted |

**Decision: deferred.** The Workflow entity design is the same regardless of runner. Start with a custom runner for MVP. Migrate to Temporal or blueprint engine when reliability requirements demand it.

## Evaluations

### Framework: LangSmith

The existing evaluation framework is built on LangSmith (not LangFuse). It supports rubrics, test sets, and automated scoring.

### Extension for Associates

Current: test web/voice agent conversation quality
OS: test associate workflow outcomes — did the insurance workflow produce the correct result?

### What Associate Evaluations Test

| Evaluation Type | What It Measures |
|-----------------|-----------------|
| **Classification accuracy** | Did it correctly classify the email/input type? |
| **Extraction quality** | Did it extract the right fields from documents? |
| **Workflow correctness** | Did it follow the right steps in the right order? |
| **Entity state correctness** | After processing, are entities in the expected state? |
| **HITL escalation accuracy** | Did it correctly identify when to escalate to a human? |
| **Communication quality** | Are drafted communications accurate and appropriate? |

### Evaluation Flow

```bash
# Create rubric with insurance-specific criteria
indemn rubric create --name "intake-quality" --criteria @rubrics/intake.json

# Create test set with inputs and expected outcomes
indemn test-set create --name "gic-emails"
indemn test-set add-case --test-set gic-emails \
  --input @test-data/email-new-gl-submission.json \
  --expected '{"submission.created": true, "submission.lob": "GL", "submission.status": "triaged"}'

# Run evaluation
indemn eval run --associate ASSOC-001 --rubric intake-quality --test-set gic-emails

# Review results
indemn eval results EVAL-001 --format table
```

The evaluation:
1. Sets up an isolated test environment (test org, test carriers, test products)
2. Feeds each test input to the associate
3. The associate processes it in a sandbox (same as production)
4. Verifies entity state against expected outcomes
5. Scores against rubric criteria
6. Reports results via LangSmith

### Eval-Driven Improvement Loop

Same pattern as current agent evaluation, applied to associates:
1. Run evaluation → identify failures
2. Analyze failures — is it the skill (unclear instructions)? the LLM (bad reasoning)? the data (unexpected format)?
3. Fix the root cause — update skill, adjust LLM config, add training data to knowledge base
4. Re-run evaluation → verify improvement
5. Deploy improved associate

## Key Layer 3 Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent framework | LangChain deep agents (`deepagents` package) | Already used (Jarvis, Intake Manager). Full middleware stack. Skills + sandbox + todo + subagents. |
| CLI interaction | Associates execute CLI commands via `execute()` in sandbox | Same as Claude Code pattern. Skills document CLI commands. No tools abstraction needed. |
| Sandbox provider | Daytona (evaluating) | Isolated, pre-configured, secure, scalable. Potentially free credits. |
| Web operators | Same deep agent harness + browser automation | One framework for all agent types. Browser tools added to sandbox. |
| Associate entity | First-class OS entity, CLI-creatable | Follows same patterns as all entities. Tier 3 compatible. |
| Skills | Auto-generated (entity) + human-authored (workflow) | Entity skills from Layer 2. Workflow skills describe HOW to combine operations. |
| Workflow entity | CLI-creatable, deterministic + associate steps | Configurable per customer. No code changes for new workflows. |
| Workflow runner | Decision deferred — custom for MVP, Temporal at scale | Workflow entity design is runner-agnostic. |
| Evaluations | LangSmith framework, extended for workflow outcomes | Existing framework. Test entity state, not just conversation quality. |
