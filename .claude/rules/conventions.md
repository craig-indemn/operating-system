# Operating System Conventions

## CLI-First
- Access all external services via CLI tools or curl. No MCPs.
- If a CLI is available, use it. If not, use curl with the REST API.
- Document CLI patterns in skills, not inline in CLAUDE.md.

## Skills Pattern
- Every tool has a skill in `.claude/skills/{tool}/SKILL.md`
- Every skill has: status check, setup instructions, usage patterns
- Heavy documentation goes in `references/`, not the main SKILL.md
- Composed skills reference tool skills, they don't duplicate them

## Credentials
- **Shared infrastructure secrets** (MongoDB URIs, Redis, RabbitMQ, API keys) live in **AWS Secrets Manager** under `dev/shared/*` and `prod/shared/*`
- **Personal tokens** (Airtable PAT, Linear token, Slack tokens, Langfuse keys, Neon connection string) live in **1Password** vault `indemn-os`
- Access secrets through **wrapper scripts only** — never source `.env` or reference secret env vars directly
- A PreToolUse guard hook blocks `.env` reads, `printenv`, and secret variable echoing
- The `.env` file contains only non-secret config (AWS account ID, region, aliases)
- Never hardcode credentials in skills, scripts, or CLAUDE.md

## Tool Access (Secrets Proxy)
Wrapper scripts in `scripts/secrets-proxy/` pull credentials at runtime. They're on PATH via SessionStart hook.

| Tool | Wrapper | Example |
|------|---------|---------|
| mongosh | `mongosh-connect.sh` | `mongosh-connect.sh dev tiledesk --eval 'db.stats()'` |
| psql | `psql-connect.sh` | `psql-connect.sh -c 'SELECT 1'` |
| curl (Airtable) | `curl-airtable.sh` | `curl-airtable.sh "https://api.airtable.com/v0/meta/bases"` |
| curl (Langfuse) | `curl-langfuse.sh` | `curl-langfuse.sh /api/public/traces?limit=10` |
| linearis | `linearis-proxy.sh` | `linearis-proxy.sh issues list --limit 5` |
| curl (Apollo) | `curl-apollo.sh` | `curl-apollo.sh /api/v1/mixed_companies/search '{"q":"Acme"}'` |
| slack | `slack-env.sh` | `slack-env.sh python3 -c "from slack_client import ..."` |
| local-dev.sh | `local-dev-aws.sh` | `local-dev-aws.sh start platform --env=dev` |

**Already secure** (no wrapper needed): `gh`, `gog`, `stripe`, `vercel`, `aws`, `op`

## Database
- Read-only unless explicitly authorized
- Understand the schema dynamically — don't hardcode table names or column lists
- Use the postgres skill for Neon Postgres connection patterns, meeting-intelligence skill for domain queries
- Use the mongodb skill for MongoDB Atlas connection patterns and tiledesk operational data

## Projects
- Workstream projects live in `projects/<name>/` with INDEX.md, artifacts/, and .beads/
- Artifacts are distilled outputs, not raw data dumps — summarize and organize before saving
- Every artifact has a metadata header with `ask`, `created`, `workstream`, `session`, and `sources`
- Artifact slugs: lowercase, hyphenated, descriptive (e.g. `google-drive-inventory`)
- INDEX.md is the source of truth for resuming — if it's not there, it doesn't exist for resume purposes
- Update INDEX.md at end of session: refresh Status, add new artifacts/decisions/links
- Beads are scoped per-project — always `cd` into the project directory before running `bd` commands
- Commit project state after closing a session

## Systems
- Systems live in `systems/<name>/` with a SYSTEM.md defining purpose, capabilities, dependencies, and integration points
- Systems are operational infrastructure — persistent processes that don't "finish" like projects
- Systems use skills as their interface (the skill is in `.claude/skills/<name>/`, the engine is in `systems/<name>/`)
- Systems serve any project — they're cross-cutting infrastructure
- The OS has three primitives: Skills (capabilities), Projects (memory), Systems (processes)

## Sessions
- Use `/sessions` skill (or `session` CLI directly) to create, list, attach, close, and monitor Claude Code sessions
- Session names should match project names — alphanumeric + hyphens (e.g. `voice-evaluations`, `platform-dev`)
- All sessions start in OS repo worktrees (`.claude/worktrees/<name>`); external repos added via `--add-dir`
- Session state files live in `sessions/{uuid}.json` (gitignored, runtime state)
- Hooks update state automatically — do not manually edit session state files
- Close sessions defensively with `session close <name>` — it commits, pushes, and updates INDEX.md before exiting
- Use `session destroy <name>` only for unresponsive sessions — it preserves the worktree for inspection
- Default permission mode is `bypassPermissions`; use `--permissions acceptEdits` for production-touching sessions
- The `/sessions` skill reads session state and project INDEX.md files to provide unified briefings

## When Compacting
- Always preserve: the list of available skills, the user's role, which tools are authenticated
- Always preserve: any active task context and decisions made in conversation
- Always preserve: the current active project name and its last known status
