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
- Store API keys and tokens as environment variables in the project `.env` file (repo root, gitignored)
- Never hardcode credentials in skills or scripts
- Connection strings go in env vars, not in CLAUDE.md
- Each skill documents which env vars it needs

## Environment Loading
- **Before running ANY Bash command that uses CLI tools or env vars**, source the project .env file first: `source .env && <command>`
- This applies to: psql, mongosh, curl with auth headers, gog, npx agent-slack, linearis, stripe, vercel, neonctl — any command that depends on credentials
- The `.env` file is always at the repository root
- Never assume env vars are already in the shell — always source explicitly

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

## When Compacting
- Always preserve: the list of available skills, the user's role, which tools are authenticated
- Always preserve: any active task context and decisions made in conversation
- Always preserve: the current active project name and its last known status
