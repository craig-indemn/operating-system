# Philosophy: Indemn Operating System Architecture

## Core Belief

Claude Code is an expert at using CLIs. If we provide well-documented skills that describe how to use CLIs, Claude Code will be a wizard at everything. This is simpler, lighter, more debuggable, and more composable than any alternative.

## CLI-First, Not MCP-First

MCPs (Model Context Protocol servers) are the default recommendation for connecting Claude Code to external services. We reject this as the primary pattern for the following reasons:

1. **Memory overhead**: Each MCP server consumes ~350MB of RAM. Running 5+ MCPs means 1.5GB+ just for connectors.
2. **Black box**: MCP servers are opaque processes. When something fails, debugging means reading someone else's server code.
3. **Fragile**: MCP servers crash, hang, lose connections. They add failure modes to every session.
4. **Redundant**: Most services already have excellent CLIs or simple REST APIs. The MCP is just a wrapper around the same API, adding complexity for no gain.

**Our approach**: For every service, use the best available CLI tool. If no CLI exists, write a thin `curl` wrapper documented in a skill. Claude Code executes CLI commands via Bash — no intermediary process needed.

## Skills Architecture: Three Tiers

Every tool skill follows the same three-section structure:

### Tier 1: Status Check
A command that verifies the tool is installed and authenticated. Claude runs this before attempting to use the tool. If it fails, Claude knows to run setup.

### Tier 1.5: Prerequisites
Before setup, the skill must clearly state what's required for it to work — credentials, accounts, admin access, third-party approvals. Each prerequisite states: what it is, whether you can self-service it or need someone else, and who to ask if you can't self-service. If onboarding hits a wall, the user should know exactly why and what to do about it without leaving the skill. No one should ever be surprised by a `redirect_uri_mismatch` or a missing API key with no explanation of where to get it.

### Tier 2: Setup
Step-by-step instructions to install and authenticate. No ambiguity, no "ask Kyle" — the skill contains everything needed, or explicitly states what credentials to obtain and from where.

### Tier 3: Usage
How to actually use the tool. Common commands, patterns, gotchas. Heavy detail goes in `references/` to keep the main SKILL.md lean.

## Composition: Skills That Use Skills

Simple tool skills (slack, postgres, google-workspace) are the atoms. Composed skills (meeting-intelligence, pipeline-deals) are the molecules — they combine multiple tool skills to accomplish domain-specific tasks.

A composed skill doesn't re-document how to query Postgres. It references the postgres skill and focuses on what queries to run, what the data means, and how to interpret results.

## Lazy Loading: Index, Don't Inline

The CLAUDE.md is an index. It tells Claude what's available, not how everything works. Information loads on demand:

1. **Always loaded**: CLAUDE.md (~50 lines) + skill names/descriptions (~100 words each)
2. **Loaded on invoke**: Full SKILL.md body (under 500 lines)
3. **Loaded on demand**: `references/` files, only when Claude needs specific detail

This keeps the context window clean. Claude knows what tools exist, but only loads the manual for the tool it's currently using.

## Role-Based Access

Not everyone needs everything. The onboarding skill detects the user's role and sets up only what they need:

- **Engineer**: All tools, full database access, all skills
- **Executive**: Meetings, docs, slack, pipeline — no raw database, no deployment tools
- **Sales**: Meetings, pipeline, CRM — focused on customer intelligence

## Maturity Levels

Every integration has a maturity classification:

- **Experiment**: Someone built it, it works for them, undocumented edge cases
- **Useful**: Used regularly, documented in a skill, known limitations noted
- **Supported**: Team depends on it daily, monitored, tested, maintained

New integrations start as Experiment. They graduate by being used, documented, and proven reliable.

## No Magic, No Abstraction for Abstraction's Sake

If a `curl` command does the job, we don't wrap it in a script. If a script does the job, we don't build a service. The right amount of complexity is the minimum needed for the current task. Three similar `curl` commands in a skill is better than a premature CLI wrapper.

We build the next layer of abstraction only when the current one has proven insufficient through actual use.
