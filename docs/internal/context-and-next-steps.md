# Context: Why We're Doing This & Next Steps

## Origin

Kyle (CEO, Indemn) built an intelligence layer across Indemn's tools — meetings, pipeline, CRM, communications — accessible through Claude Code. He documented this in two files:

1. **"Indemn AI-First Operating System — Project Plan"** — the vision, platform inventory, roles, phase timeline, and success criteria
2. **"Craig's Claude Code Setup — Full Stack Access"** — step-by-step setup for Google Docs MCP, Slack MCP, Neon Postgres access, and a starter CLAUDE.md

Kyle's approach used MCPs for Google Docs and Slack, REST APIs for other services, and direct Postgres access for the meetings intelligence database.

## What Craig Decided

Craig (Technical Partner) reviewed Kyle's documents and established a different technical direction:

**CLI-first, not MCP-first.** Instead of running MCP servers (~350MB each), use CLI tools that already exist for most services. Claude Code is an expert at using CLIs. Well-documented skills describing CLI usage patterns are simpler, lighter, and more debuggable than MCP wrappers.

**Skills architecture.** Each tool gets a skill with three sections: status check, setup, and usage. Skills compose into higher-level workflows. The CLAUDE.md stays lean as an index — skills load on demand.

**Role-based onboarding.** An onboarding meta-skill detects the user's role and walks them through setting up only the tools they need.

## Tool Decisions (From Research)

| Service | Tool | Type | Auth |
|---------|------|------|------|
| Slack | `agent-slack` | Third-party CLI (AI-agent focused) | Browser token or bot token |
| Google Workspace (Gmail, Calendar, Drive, Docs) | `gog` (gogcli) | Third-party unified CLI | OAuth (one-time browser, auto-refresh) |
| Linear | `linearis` | Third-party CLI | `LINEAR_API_KEY` env var |
| GitHub | `gh` | Official CLI | `gh auth login` |
| Stripe | `stripe` | Official CLI | `STRIPE_API_KEY` env var |
| Vercel | `vercel` | Official CLI | `VERCEL_TOKEN` env var |
| Neon Postgres | `neonctl` + `psql` | Official CLI | `NEON_API_KEY` env var + connection string |
| Airtable | `curl` wrapper | REST API (no CLI exists) | Personal Access Token |
| Apollo.io | `curl` wrapper | REST API (no CLI exists) | API key |
| Google Analytics | Deferred | Not needed now | — |

## The Meetings Intelligence System

Kyle built a system that processes 3,211 meetings into structured intelligence:

**Database**: Neon Postgres — **66 tables** (not 55 as originally described), 8 custom enum types, 62 foreign key relationships
**Connection**: `postgresql://neondb_owner:REDACTED_NEON_PASSWORD@ep-dark-hat-ah6i1mwb-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require`

**Key data** (verified by direct database exploration):
- 3,141 meetings, 183,697 utterances from 3 sources (Apollo, Granola, Gemini)
- 14,612 meeting extractions: decisions (5,691), learnings (4,691), problems (2,622), objections (1,608)
- 3,240 business signals: health, expansion, champion, churn_risk, blocker, insight
- 3,681 quotes with sentiment and usability tags
- 1,089 deals, 1,001 AI scoring results
- Table/column names are PascalCase (must double-quote in SQL)

**Full schema documented in**:
- `.claude/skills/postgres/references/schema-guide.md` — all 66 tables, columns, types, relationships
- `.claude/skills/meeting-intelligence/references/data-dictionary.md` — domain meaning, query patterns, JOIN reference

**Kyle's open questions** (to be addressed now that database is explored):
1. Is the data model right? 66 tables — too many? Too few?
2. Extraction pipeline runs Claude on every meeting — right approach vs embeddings/RAG/hybrid?
3. Deployment — Vercel config exists, Prisma migration incomplete (13/19 services)
4. Should meetings merge into copilot-server or stay separate?
5. How to make this data accessible to other Claude Code instances?

## Current Onboarding Status (as of 2026-02-13)

### Tools — All Authenticated
| Tool | Status | Notes |
|------|--------|-------|
| GitHub (`gh`) | Working | Authenticated to indemn-ai org as craig-indemn |
| Vercel (`vercel`) | Working | Authenticated as craig-indemn |
| Postgres (`psql`) | Working | 3,141 meetings confirmed, psql at `/opt/homebrew/opt/libpq/bin/psql` |
| Linear (`linearis`) | Working | 25 issues accessible, `LINEAR_API_TOKEN` bridged in `.env` |
| Google Workspace (`gog`) | Working | Authenticated as craig@indemn.ai via Craig's own GCP project |
| Stripe (`stripe`) | Working | Authenticated via `stripe login` (sandbox account) |
| Slack (`agent-slack`) | Working | craig@indemn, imported from Slack Desktop |
| Airtable (curl) | Working | 201 bases accessible via PAT |
| Neonctl | Installed | Auth not run yet (optional — only for branch management) |

### Tools — Deferred
| Tool | What's Needed |
|------|--------------|
| Apollo (curl) | API key from Apollo.io Settings > Integrations (requires paid plan) |

### Environment Setup
- All env vars stored in `operating-system/.env` (gitignored)
- `~/.zshrc` sources `.env` automatically via: `[ -f "$HOME/Repositories/operating-system/.env" ] && source "$HOME/Repositories/operating-system/.env"`
- `LINEAR_API_TOKEN` bridge from `LINEAR_API_KEY` — handled in `.env`
- `NEON_CONNECTION_STRING` — set in `.env`
- `AIRTABLE_PAT` — set in `.env`

### Known Issues
- `psql` installed at `/opt/homebrew/opt/libpq/bin/psql` — not on PATH by default, use full path
- `stripe login` connected to sandbox account — for production data, use live API key
- `craig_secret.json` (Google OAuth credentials) is in repo root — gitignored, do not commit
- Database uses PascalCase identifiers — must double-quote table/column names in SQL

## What's Built So Far

- Repository structure: `operating-system/` with `.claude/skills/` for all tools
- CLAUDE.md as lean index
- 9 tool skills with accurate commands (slack, google-workspace, linear, github, stripe, airtable, apollo, vercel, postgres)
- 1 onboarding meta-skill with prerequisites table
- 2 composed skills (meeting-intelligence, pipeline-deals)
- Rules file for conventions
- Google Workspace: 5 per-service reference files (gmail, calendar, drive, docs, sheets) with verified commands
- Postgres: full schema guide (66 tables) and domain data dictionary
- Airtable + Apollo: API spec reference files
- Internal docs: philosophy, best practices, context
- .gitignore for credentials

## Next Steps

### Completed
1. ~~**Finish onboarding**~~ — 8/9 tools authenticated (Apollo deferred — needs paid plan)
2. ~~**Set environment variables**~~ — `.env` file in repo, sourced from `~/.zshrc`
3. ~~**Test each skill end-to-end**~~ — all tools verified with real commands
4. ~~**Fix skill documentation**~~ — corrected wrong CLI commands in Slack, Linear, Google Workspace, Postgres, and Onboarding skills

### Short Term
5. **Answer Kyle's extraction pipeline questions** — now informed by real schema data
6. **Build the first composed workflow** — "prepare for call with X" pulling from meetings + pipeline + slack
7. **Validate Google Workspace deep** — test Calendar, Drive, Docs, Sheets with real data (Gmail confirmed)
8. **Get Apollo API key** — requires paid plan, check with Kyle

### Medium Term
9. **Onboard Cam** — use the onboarding skill to set up an executive-tier config
10. **Cross-system workflows** — weekly summaries, follow-up detection, meeting prep automation
11. **Maturity classification** — mark each integration as Experiment/Useful/Supported based on actual reliability
