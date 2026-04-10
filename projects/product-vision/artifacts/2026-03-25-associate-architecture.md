---
ask: "How do associates work technically — agent architecture, skills, evaluations, and how they connect to the OS?"
created: 2026-03-25
workstream: product-vision
session: 2026-03-25-a
sources:
  - type: conversation
    description: "Craig describing the associate architecture, 2026-03-25"
  - type: local
    description: "Existing agent architecture: bot-service (V1), platform-v2 (V2), Jarvis, Indemn CLI, evaluation framework"
---

# Associate Architecture — How Associates Work on the OS

## What an Associate IS

An associate is a LangChain deep agent configured with skills that operate on domain objects via CLI/API. It's the evolution of Indemn's V2 agent architecture — same underlying harness (deep agent, LangChain, LangFuse observability), but now with the full OS domain model to work with.

## The Evolution

### Today — Agents That Talk
- V1 agents (bot-service): Production agents serving customers. Conversation-focused.
- V2 agents (platform-v2): Config-driven agents with component/connector abstraction.
- Jarvis: A V2 deep agent that builds other agents — already "agents building agents."
- Web operators: Deep agents that interact with web interfaces to automate legacy system interactions.
- All focus on: conversations (web chat, voice), with some tool use.

### On the OS — Associates That Transact
- Same underlying harness: deep agents, LangChain, modern agent framework
- Architecture will be redesigned/modernized from current V2
- Extended with: skills that operate on OS domain objects via CLI/API
- Associates don't just converse — they create submissions, generate quotes, issue policies, process payments, produce documents
- The OS domain model gives them the insurance business to operate on

### What Changes vs. What Stays
**Stays:**
- Deep agent architecture (LangChain-based)
- Skills model (like Claude Code skills)
- LangFuse observability
- CLI as control plane
- Evaluation framework (rubrics, test sets)
- Bot-service as deployment/hosting layer (or its evolution)

**Changes:**
- Agents get access to the full OS domain model (not just conversation tools)
- Skills become insurance-specific capability definitions
- Evaluations extend to workflow outcomes, not just conversation quality
- Configuration model supports the "48 associates are configurations of one system" concept
- CLI expands from agent management to full OS management

## The Skills Model

Skills on the OS work exactly like Claude Code skills: a document that describes how to use a tool.

### Claude Code Skill:
```
# Slack Skill
Status check: verify auth
Usage: client.chat_postMessage(channel, text)
Patterns: search, send, read history
```

### OS Associate Skill:
```
# Submission Processing Skill
When a new email arrives in the intake channel:
1. Classify the email: `indemn email classify --id {email_id}`
2. Extract submission data: `indemn submission extract --email {email_id} --schema {form_schema}`
3. Validate completeness: `indemn submission validate --id {submission_id}`
4. If incomplete, draft request: `indemn draft create --type info-request --submission {submission_id}`
5. If complete, route to underwriting: `indemn submission route --id {submission_id} --rules {workflow_rules}`
```

The associate reads its skills, understands what CLI/API calls to make, and executes them against real domain objects with real state machines.

## How an Associate Gets Built

Using the CLI (Tier 3 tooling — same tools Indemn uses internally):

```bash
# Create the associate
indemn associate create --name "Intake Associate" --type intake

# Add skills
indemn associate add-skill --associate intake --skill submission-processing
indemn associate add-skill --associate intake --skill email-classification
indemn associate add-skill --associate intake --skill document-extraction

# Configure domain access (which entities it can read/write)
indemn associate configure --associate intake \
  --read "submission,email,carrier,agent,coverage,lob" \
  --write "submission,draft,document,task"

# Connect channels
indemn associate connect-channel --associate intake --channel email --provider outlook
indemn associate connect-channel --associate intake --channel web --widget intake-form

# Deploy for a specific organization
indemn associate deploy --associate intake --org gic-underwriters

# Run evaluation
indemn eval run --associate intake --rubric submission-quality --test-set gic-submissions
```

This is the Tier 3 experience. Indemn builds every associate in the catalog this way. Platform customers get the same tools.

## How an Associate Runs

When deployed, an associate is a running deep agent that:

1. **Listens** on its configured channels (email inbox, web widget, voice line, API endpoint)
2. **Receives** input (an email, a chat message, a form submission, a scheduled trigger)
3. **Reads its skills** to determine what to do (like Claude Code reading a skill file)
4. **Executes CLI/API calls** against the OS domain model:
   - Creates/updates entities (submissions, quotes, policies)
   - Triggers workflows (validation, routing, quoting)
   - Generates outputs (drafts, documents, communications)
5. **Produces output** through configured channels (email response, web update, document, notification)
6. **Surfaces HITL checkpoints** where human review is needed (draft approval, underwriting decision, binding authorization)

All observable via LangFuse. All evaluable via the evaluation framework.

## Evaluation Framework Extension

### Today: Conversation Evaluations
- Web agent evaluations: response quality, accuracy, tone, tool use
- Voice agent evaluations: understanding, response quality, call handling
- Rubrics define what "good" looks like
- Test sets provide scenarios to evaluate against

### On the OS: Workflow Evaluations
Same framework, extended to insurance workflow outcomes:

**Intake Associate Evaluation:**
- Did it correctly classify the email type?
- Did it extract the right fields from the submission?
- Did it identify missing information?
- Did it route to the correct carrier based on appetite rules?
- Did the drafted response include all necessary information?

**Renewal Associate Evaluation:**
- Did it correctly identify policies approaching renewal?
- Did it accurately calculate premium change %?
- Did it correctly flag remarket candidates (>15% increase)?
- Did the drafted communication include the right policy details?

**Quote & Bind Associate Evaluation:**
- Did it collect all required applicant information?
- Did it correctly check eligibility against carrier appetite?
- Did it present accurate pricing?
- Did the bind execute correctly (policy created, payment processed)?

**General Workflow Evaluations:**
- Did the associate follow the correct workflow steps?
- Did it properly handle edge cases?
- Did it escalate to HITL at the right moments?
- Did it produce the correct domain object state changes?

These evaluations run automatically. Associates improve through eval-driven iteration — the same pattern the evaluation framework already supports, applied to insurance-specific workflows.

## Existing Building Blocks

What already exists that the associate architecture builds on:

| Component | Current State | OS Evolution |
|-----------|--------------|--------------|
| Bot-service (V1) | Production agents, conversation-focused | Hosting/deployment layer for associates |
| Platform-v2 (V2) | Config-driven agents, component/connector | Architecture basis for associate harness |
| Jarvis | Agent that builds agents | Prototype of Tier 3 (agents building agents on the platform) |
| Web operators | Deep agents automating web interfaces | Integration pattern for legacy system connectivity |
| Indemn CLI | Agent creation, evaluation, exports | Expands to full OS control plane |
| Evaluation framework | Rubrics, test sets, automated quality | Extends to insurance workflow evaluations |
| LangFuse | Agent observability, trace analysis | Same — observability for all associates |
| Skills (Claude Code pattern) | Craig's OS uses skills for every tool | Associate skills for every domain operation |
| MCP server | API access to agent management | API access to full OS |

## The Key Architectural Decisions (To Be Made)

1. **V2 redesign scope** — How much of platform-v2 architecture carries over vs. is redesigned for the OS?
2. **Bot-service role** — Does bot-service evolve into the associate hosting layer, or is it replaced?
3. **Skill format** — What's the exact specification for an OS skill? (Markdown like Claude Code? YAML? Code?)
4. **Domain access control** — How does the system enforce which entities an associate can read/write?
5. **Workflow execution** — How do WorkflowDefinition and WorkflowExecution relate to the agent's skill execution?
6. **Multi-agent coordination** — Some workflows involve multiple associates (e.g., intake associate hands off to quoting associate). How is this orchestrated?
7. **State management** — How does the agent maintain context across multi-step workflows?
