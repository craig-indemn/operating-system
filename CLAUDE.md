# Indemn Operating System

Connected intelligence layer for Indemn. Every tool the company uses, accessible from Claude Code via CLI skills.

## Your Environment
- All tools accessed via CLI or curl — no MCPs
- Skills in `.claude/skills/` handle status checks, setup, and usage for each tool
- If a tool isn't set up yet, the skill will walk you through it
- Credentials stored as environment variables, never hardcoded

## Available Skills

### Tool Skills
| Skill | Tool | What It Does |
|-------|------|-------------|
| `/beads` | bd | Task tracking with dependencies, epics, acceptance criteria, and dispatch integration |
| `/slack` | agent-slack | Read channels, search messages, post to Slack |
| `/google-workspace` | gog (gogcli) | Gmail, Calendar, Drive, Docs, Sheets |
| `/linear` | linearis | Issues, roadmap, project management |
| `/github` | gh | Repos, PRs, issues, code review |
| `/stripe` | stripe CLI | Revenue, subscriptions, payments |
| `/airtable` | curl (REST API) | Bases, records, bot configs, EventGuard |
| `/apollo` | curl (REST API) | Company enrichment, contacts, employee data |
| `/vercel` | vercel CLI | Deployments, environments, domains |
| `/postgres` | neonctl + psql | Neon Postgres database access |
| `/mongodb` | mongosh | Query MongoDB Atlas tiledesk database — bot configs, conversations, agents, orgs |
| `/local-dev` | local-dev.sh | Start, stop, and manage Indemn platform services locally — groups, federation, logs |
| `/agent-browser` | agent-browser | Interact with web pages in a real browser — navigate, click, fill forms, verify UI, take screenshots |
| `/image-gen` | curl (Gemini API) | Generate images via Google Nano Banana — blog visuals, illustrations, diagrams, brand-aware assets |

### System Skills
| Skill | What It Does |
|-------|-------------|
| `/dispatch` | Autonomous execution of implementation plans — runs Claude Code sessions via Agent SDK against beads epics |

### Workflow Skills
| Skill | What It Does |
|-------|-------------|
| `/project` | Resume, create, and manage workstream projects — persistent context, artifacts, and beads across sessions |
| `/call-prep` | End-to-end customer call briefing — meetings, signals, Slack, email, pipeline, contacts |
| `/weekly-summary` | Weekly intelligence rollup — decisions, action items, signals, pipeline, quotes |
| `/follow-up-check` | Surface overdue action items, unmet commitments, and dropped follow-ups |
| `/eval-analysis` | Analyze evaluation results — classify failures as agent vs evaluation issues, recommend fixes |

### Reference Skills
| Skill | What It Does |
|-------|-------------|
| `/meeting-intelligence` | Query meetings, transcripts, extracted intelligence, customer signals |
| `/pipeline-deals` | Pipeline status, deal context, customer prep across multiple sources |

### Meta Skills
| Skill | What It Does |
|-------|-------------|
| `/onboarding` | Role-based setup — installs and authenticates all tools for your role |

## Roles
- **Engineer** (Craig): All tools, full database access, all skills
- **Executive** (Cam): Meetings, docs, slack, pipeline — no raw DB or deployment tools
- **Sales**: Meetings, pipeline, CRM — customer intelligence focus

## Projects

Workstream projects live in `projects/<name>/`. Each has an INDEX.md (context for resuming), artifacts (distilled outputs), and beads (task tracking). See `/project` skill for full usage.

- To resume a project: `/project <name>` or just mention the project by name
- To create a new project: `/project new <name>`
- To save output as an artifact: `/project save <slug>`
- To see all projects: `/project status`
- Design doc: @docs/plans/2026-02-16-project-tracking-design.md

## Systems

Operational infrastructure — persistent processes that don't "finish" like projects. Lives in `systems/<name>/` with a SYSTEM.md defining purpose, capabilities, and integration points.

| System | What It Does |
|--------|-------------|
| `dispatch` | Ralph loop engine that executes beads epics via Agent SDK — fresh Claude Code session per task, separate verification, autonomous until backstop criteria met |

- Systems use skills as their interface (e.g., `/dispatch` invokes the dispatch engine)
- Systems are infrastructure — they serve any project
- Design doc: @projects/os-development/artifacts/2026-02-19-dispatch-system-design.md

## Conventions
@.claude/rules/conventions.md

## Architecture Docs
- Philosophy: @docs/internal/philosophy.md
- Best practices: @docs/internal/best-practices.md
- Context & next steps: @docs/internal/context-and-next-steps.md
- Kyle's original plan: @docs/Indemn AI-First Operating System — Project Plan.md
- Kyle's setup doc: @docs/Craig's Claude Code Setup — Full Stack Access.md
