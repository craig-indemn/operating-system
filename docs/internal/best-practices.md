# Best Practices: Claude Code Skills & CLAUDE.md

Compiled from Anthropic's official documentation. Sources listed at bottom.

## CLAUDE.md Design

### Keep It Lean
For every line, ask: "Would removing this cause Claude to make mistakes?" If not, cut it. Bloated CLAUDE.md files cause Claude to ignore actual instructions.

### What to Include
- Bash commands Claude cannot guess
- Code style rules that differ from defaults
- Testing instructions and preferred test runners
- Repository etiquette (branch naming, PR conventions)
- Architectural decisions specific to your project
- Developer environment quirks (required env vars)
- Common gotchas or non-obvious behaviors

### What to Exclude
- Anything Claude can figure out by reading code
- Standard language conventions Claude already knows
- Detailed API documentation (link to docs instead)
- Information that changes frequently
- Long explanations or tutorials
- File-by-file descriptions of the codebase

### The Hierarchy
Claude Code reads CLAUDE.md files hierarchically:
1. **Managed policy** (`/Library/Application Support/ClaudeCode/CLAUDE.md`) — org-wide
2. **Project memory** (`./CLAUDE.md` or `./.claude/CLAUDE.md`) — shared via source control
3. **Project rules** (`./.claude/rules/*.md`) — modular, topic-specific, can be path-scoped
4. **User memory** (`~/.claude/CLAUDE.md`) — personal prefs across all projects
5. **Project local** (`./CLAUDE.local.md`) — personal project-specific prefs

Parent directory CLAUDE.md files load in full at launch. Child directory CLAUDE.md files load on demand when Claude reads files in those directories. More specific instructions override broader ones.

### @import Syntax
Reference external files without inlining them:
```markdown
See @docs/architecture.md for system overview.
Git workflow: @docs/git-instructions.md
```
- Both relative and absolute paths work
- Relative paths resolve from the file containing the import
- Recursive imports allowed, max depth of 5 hops
- Not evaluated inside code blocks

## Skills Architecture

### Three-Level Progressive Disclosure
1. **Metadata** (name + description) — always in context, ~100 words. Claude knows what's available.
2. **SKILL.md body** — loads when invoked. Target under 500 lines / 3,000 words.
3. **references/ directory** — loaded only when Claude needs specific detail. Unlimited.

### SKILL.md Sizing
- Target 1,500-2,000 words for the main file
- Detailed content goes in `references/`
- Keep under 500 lines total
- If files in references/ are >10K words, include grep patterns in SKILL.md to help Claude find specific sections

### Frontmatter Options
```yaml
---
name: my-skill                    # Display name, becomes /slash-command
description: What this does       # Helps Claude decide when to auto-load
argument-hint: [issue-number]     # Hint shown during autocomplete
user-invocable: false             # Only Claude can invoke (background knowledge)
disable-model-invocation: true    # Only user can invoke (manual trigger)
allowed-tools: Read, Grep, Glob   # Tools allowed without permission prompts
context: fork                     # Run in isolated subagent context
agent: Explore                    # Subagent type for context: fork
---
```

### Invocation Control
| Setting | User invokes | Claude invokes | Description in context |
|---------|-------------|---------------|----------------------|
| (default) | Yes | Yes | Always |
| `disable-model-invocation: true` | Yes | No | Not loaded |
| `user-invocable: false` | No | Yes | Always |

### Skill Composition
Skills can preload other skills into subagents:
```yaml
---
name: api-developer
skills:
  - api-conventions
  - error-handling-patterns
---
```
Full content of each listed skill is injected into the subagent's context at startup. Subagents do NOT inherit parent skills — you must list them explicitly.

**Limitation**: Subagents cannot spawn other subagents. Max depth is: main conversation -> subagent (with preloaded skills) -> done.

### Building Composed Workflow Skills

Skills fall into three tiers based on what they do:

**Tier 1 — Tool skills (atoms).** One tool, one skill. Postgres, Slack, Google Workspace. These document how to use a specific CLI or API. They're the building blocks.

**Tier 2 — Reference skills (knowledge).** Combine multiple tool skills' knowledge for a domain. Meeting-intelligence knows which tables to query and what the data means. Pipeline-deals knows how to pull from meetings + pipeline API + Slack + email. These add context but don't drive a workflow.

**Tier 3 — Task skills (workflows).** End-to-end actions that orchestrate across tools to produce a deliverable. "Prepare for a call with X" pulls from 5 sources and compiles a briefing. "Generate a weekly summary" aggregates across all systems. These are the skills users and Claude invoke to get things done.

#### When to Use Each Pattern

| Pattern | Where it lives | When to use |
|---------|---------------|-------------|
| **Inline task skill** | `.claude/skills/` | Interactive workflows where the user might jump in mid-flow. Runs in main conversation, has access to conversation history. |
| **Forked task skill** (`context: fork`) | `.claude/skills/` | Self-contained workflows that produce a specific deliverable. Runs in an isolated subagent, keeps the main conversation clean. |
| **Subagent with preloaded skills** | `.claude/agents/` | Complex workflows that need a dedicated system prompt + multiple reference skills injected at startup. Most powerful composition. |

For most workflows, **inline task skills** are the right default. They're simpler, the user can interact mid-flow, and Claude has full conversation context. Use `context: fork` only when the workflow produces a large deliverable that would pollute the main context, or when you want strict isolation.

#### Invocation Design

**Let Claude invoke workflow skills by default.** The `description` field is the routing mechanism — write it so Claude recognizes when to reach for the skill based on natural user questions.

```yaml
---
name: call-prep
description: Prepare for a customer call by pulling context from meetings, pipeline, Slack, and email. Use when the user asks about preparing for a call, what they should know before a meeting, or needs context on a customer before a conversation.
---
```

Use `disable-model-invocation: true` **only** for skills with destructive side effects (sending emails, posting to Slack, deploying). If the skill is read-only intelligence gathering, let Claude invoke it.

#### Composition Model

Task skills reference tool skills and reference skills — they don't duplicate them.

- A task skill says "pull last 5 meeting summaries" and relies on the meeting-intelligence skill's patterns being available
- A subagent uses the `skills:` field to preload reference skills, giving it the query patterns and domain knowledge at startup
- Tool skills stay focused on one tool. Reference skills stay focused on one domain. Task skills orchestrate across both.

#### `$ARGUMENTS` for Parameterization

Task skills accept input via `$ARGUMENTS`. The parameter is whatever follows the skill name, or whatever Claude passes when auto-invoking.

```yaml
---
name: customer-health
description: Analyze a customer's health signals, engagement, and risk factors. Use when the user asks about a customer's status, health, or risk.
---
Analyze customer health for $ARGUMENTS:
1. Pull signals from meetings database
2. Check engagement frequency
3. Review open objections and blockers
4. Compile health assessment
```

User says "how is INSURICA doing?" → Claude invokes with `$ARGUMENTS = "INSURICA"`. User can also run `/customer-health INSURICA` directly.

#### Description Budget

All skill descriptions compete for ~2% of the context window (fallback: 16,000 characters). As you add more skills, keep descriptions concise but specific enough for Claude to route correctly. If skills get excluded, override with `SLASH_COMMAND_TOOL_CHAR_BUDGET`.

### Dynamic Context in Skills
Skills can execute shell commands as preprocessing:
```yaml
---
name: pr-summary
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---
## Context
- PR diff: !`gh pr diff`
- Changed files: !`gh pr diff --name-only`
```
Commands execute immediately and Claude receives the rendered output.

## .claude/rules/ Directory

For modular, path-scoped rules:
```
.claude/rules/
├── code-style.md
├── testing.md
└── security.md
```

Path-scoping via YAML frontmatter:
```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API Rules
All endpoints must include input validation.
```
Rules without `paths` load unconditionally. All `.md` files are discovered recursively.

## Context Management

### The Problem
Context window fills fast. Performance degrades as it fills.

### Solutions
- `/clear` between unrelated tasks
- Subagents for investigation (exploration stays in separate context)
- Auto-compaction summarizes when context fills, preserving key decisions
- `/compact <instructions>` for targeted compaction
- CLAUDE.md compaction rules: "When compacting, always preserve X"

### The Index-and-Explore Pattern
Rather than pre-loading all data, maintain lightweight references (file paths, queries, links) and use them to dynamically load data at runtime. CLAUDE.md should point to where information lives, not contain it all.

### Skill Description Budget
Descriptions load into context with a budget of 2% of context window (fallback: 16,000 characters). Many skills = some may be excluded. Override with `SLASH_COMMAND_TOOL_CHAR_BUDGET`.

## Sources

- [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices)
- [Manage Claude's Memory](https://code.claude.com/docs/en/memory)
- [Extend Claude with Skills](https://code.claude.com/docs/en/skills)
- [Create Custom Subagents](https://code.claude.com/docs/en/sub-agents)
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills)
- [Skill Development Guide](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/skill-development/SKILL.md)
