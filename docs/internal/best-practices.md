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
- [Skill Development Guide](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/skill-development/SKILL.md)
