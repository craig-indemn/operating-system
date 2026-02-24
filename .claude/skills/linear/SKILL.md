---
name: linear
description: Manage Linear issues, search the roadmap, track engineering work using the linearis CLI. Use for project management tasks.
---

# Linear

Issue management and roadmap tracking for Indemn via `linearis` CLI. This skill encodes all company conventions — follow it exactly when creating, updating, or managing issues.

For full conventions reference: `references/linear-conventions.md`

## Prerequisites

- A Linear account with access to the Indemn workspace
- A Personal API Key from Linear (you create this yourself, no admin needed)

## Status Check

```bash
which linearis && echo "INSTALLED" || echo "NOT INSTALLED"
```

```bash
source .env && linearis issues list --limit 1 2>/dev/null && echo "AUTHENTICATED" || echo "NOT AUTHENTICATED"
```

## Setup

### Install
```bash
npm install -g linearis
```

### Authenticate
1. Go to Linear > Settings > Account > Security & Access
2. Create Personal API Key (select Read + Write scopes)
3. Set environment variable in your `.env` file:
```bash
export LINEAR_API_TOKEN="lin_api_..."
```

Rate limit: 1,500 requests/hour. All commands output JSON — pipe to `jq` for filtering.

---

## Indemn Conventions

### Hierarchy

```
Initiatives (strategic outcomes — "how Indemn wins")
  └── Projects (output collections — equivalent to epics)
       └── Issues (atomic work items — equivalent to stories)
```

- **Initiatives** = business outcomes, not feature lists. Optional target dates.
- **Projects** = collections of issues delivering complete shipped output. Can span multiple cycles. One parent initiative.
- **Issues** = atomic work. Must be completable in one cycle by one person. Max 10 story points. Clear "Done" criteria.

### Teams

| Key | Team | Scope |
|-----|------|-------|
| Key | CLI `--team` value | Scope |
|-----|-------------------|-------|
| `AI` | `"Agentic AI"` | AI agents, reasoning, RAG, RLHF, Jarvis, workflow automations |
| `COP` | `"Copilot + Platform"` | Platform UI, AI suggestions, analytics, navigation, RBAC, MFA |
| `FRONT` | `"Insurance Frontends"` | Webchat widget, landing pages, customer-facing UI |
| `WEB` | `"Marketing website"` | Marketing site, SEO, CMS, lead capture, conversions |
| `DEVOPS` | `"DevOps"` | Infrastructure, CI/CD, observability, security, tenant isolation |

**Important**: The `--team` flag requires the full team name (e.g. `--team "Agentic AI"`), not the key (`AI`). Search and filter commands accept either.

### Issue Workflow States

```
Triage → Backlog → Ready for Planning → Soon → Queued → In Progress → Ready for Testing → In Review → Acceptance → Done
                                                              ↑                                ↓
                                                              └──────────── Rework ────────────┘

Terminal: Done, Canceled, Duplicate, Archived
```

| Status | Owner | Meaning |
|--------|-------|---------|
| Triage | Product | New intake from Slack/external. Needs review. |
| Backlog | Product | Relevant, not yet prioritized for a cycle. |
| Ready for Planning | Product | Spec complete, not mapped to a cycle yet. |
| Soon | Product | Candidate for NEXT cycle (set at cycle planning meeting). |
| Queued | Engineering | Committed to current cycle. Engineers pick these up. |
| In Progress | Engineering | Actively being developed. |
| Ready for Testing | Engineering | PR opened, dev complete. Awaiting QA. |
| In Review | QA | QA actively testing (NOT code review). |
| Rework | Engineering+QA | QA found defects. Back to engineering. |
| Acceptance | QA+Engineering | QA passed, PR merged. Candidate for next prod deploy. |
| Done | Engineering Lead | Deployed to production. |
| Canceled | Product+Engineering | Not relevant. |
| Duplicate | Product | Covered by existing issue. |
| Archived | Any | Historical record. |

**When creating issues**: Default to `Backlog`. Use `Queued` only for urgent items committed to the current cycle.

**When updating status**: Follow the transitions above. Don't skip states (e.g., don't go from Backlog → Done).

### Estimation (Fibonacci)

| Effort | Points |
|--------|--------|
| < 4 hours | 1 |
| 4-8 hours (1 day) | 2 |
| 8-16 hours (2 days) | 3 |
| 16-24 hours (3 days) | 5 |
| 24-32 hours (4 days) | 8 |
| 40 hours (5 days) | 10 (cap) |

If an issue exceeds 10 points, break it down using SPIDR: **S**pike, **P**ath, **I**nterface, **D**ata, **R**ules.

### Labels

Always apply relevant labels when creating issues:

| Label | When to use |
|-------|-------------|
| Bug | Didn't work as per spec |
| Regression | Used to work, now broken |
| Improvement | Existing feature made better |
| Feature | Net-new capability |
| Hot Fix | Fix applied directly to production |
| Hot Patch | Improvement applied directly to production |
| Research | Information gathering ahead of key work |
| Spike | Engineering POC to validate a hypothesis |
| Missed Product Spec | Should have been addressed in product sooner |
| Customer Implementation | Work tied to a specific customer |
| Catchment | Issues created ad hoc (e.g. from Slack) |

**Customer labels** (use under "Customer Implementation"): Alliance, Johnson, Tillman, Rankin, Loro, Family First, Jewelers Mutual / EventGuard, Silent Sports (McKay), IIANC, Branch, Distinguished Programs, GIC, Insurica, Union General

### Priority Mapping

| Priority | Flag | Use for |
|----------|------|---------|
| 1 (Urgent) | `--priority 1` | Production down, security issues |
| 2 (High) | `--priority 2` | Current cycle feature work, important bugs |
| 3 (Medium) | `--priority 3` | Next cycle candidates, non-urgent improvements |
| 4 (Low) | `--priority 4` | Backlog, nice-to-have |

### Cycles

- 2-week sprints. Effort split: 70% features, 20% bugs, 10% tech debt.
- Cycle planning: biweekly, plans the NEXT cycle.
- Issues marked "Soon" at planning → "Queued" when cycle starts.
- "Done" means deployed to production, not just merged.

### Escalation

- **Scope conflict**: Post in #dev-squad, tag Kyle. Engineering provides estimates within 48 business hours.
- **Personnel contention**: Alert #dev-squad tagging Kyle for priority call.
- **Cycle creep**: Alert Ganesh + Kyle in #dev-squad with prefix `[CREEP]`.

---

## CLI Reference

### Issues

**List issues:**
```bash
linearis issues list --limit 25
```

**Search issues:**
```bash
linearis issues search "query"
linearis issues search "query" --team AI --status "In Progress"
linearis issues search "query" --assignee USER_ID --project "Project Name"
```
Options: `--team`, `--assignee`, `--project`, `--status` (comma-separated), `--limit`

**Read issue details:**
```bash
linearis issues read AI-280
```
Accepts both identifiers (`AI-280`) and UUIDs.

**Create issue:**
```bash
linearis issues create "Title" \
  --team "Agentic AI" \
  --priority 2 \
  --description "Description" \
  --labels "Bug" \
  --status "Backlog" \
  --project "Automated Testing and Evaluation" \
  --assignee USER_ID \
  --cycle "Cycle Name" \
  --parent-ticket AI-100
```
`--team` is required. All other flags optional.

**Update issue:**
```bash
linearis issues update AI-280 --status "In Progress"
linearis issues update AI-280 --priority 2 --assignee USER_ID
linearis issues update AI-280 --labels "Bug,Regression" --label-by adding
linearis issues update AI-280 --labels "Feature" --label-by overwriting
linearis issues update AI-280 --clear-labels
linearis issues update AI-280 --cycle "Cycle 73"
linearis issues update AI-280 --clear-cycle
linearis issues update AI-280 --parent-ticket AI-100
linearis issues update AI-280 --clear-parent-ticket
linearis issues update AI-280 --project-milestone "Milestone Name"
linearis issues update AI-280 --clear-project-milestone
```

### Comments

```bash
linearis comments create AI-280 --body "Status update: deployed to dev, testing in progress"
```

### Projects

```bash
linearis projects list
```
Note: `--limit` is accepted but not enforced by the Linear SDK — returns all projects.

### Cycles

```bash
linearis cycles list --active
linearis cycles list --team AI
linearis cycles list --team AI --active
linearis cycles list --team COP --around-active 2
linearis cycles read "Cycle 73" --team AI --issues-first 50
```

### Labels

```bash
linearis labels list
linearis labels list --team AI
```

### Users

```bash
linearis users list --active
```

### Teams

```bash
linearis teams list
```

### Documents

```bash
linearis documents list
linearis documents list --project "Automated Testing and Evaluation"
linearis documents list --issue AI-280
linearis documents read DOCUMENT_ID
linearis documents create --title "Title" --content "Markdown content" --project "Project Name" --team AI
linearis documents create --title "Title" --content "Content" --attach-to AI-280
linearis documents update DOCUMENT_ID --title "New Title" --content "New content"
linearis documents delete DOCUMENT_ID
```

---

## Common Workflows

### Post a progress update on an issue
```bash
linearis issues update AI-280 --status "In Progress"
linearis comments create AI-280 --body "Completed X. Next: Y. No blockers."
```

### Create a bug from investigation
```bash
linearis issues create "Description of the bug" \
  --team AI \
  --priority 2 \
  --labels "Bug" \
  --description "Root cause: ... Steps to reproduce: ... Expected: ... Actual: ..."
```

### Check current cycle progress
```bash
linearis cycles list --team AI --active
linearis cycles read "CYCLE_NAME" --team AI --issues-first 50
```

### Find my open work
```bash
linearis issues search "" --assignee USER_ID --status "In Progress,Queued"
```

### Move issue through the workflow
```bash
# Start working
linearis issues update AI-280 --status "In Progress"

# PR opened, dev complete
linearis issues update AI-280 --status "Ready for Testing"

# QA passed, merged
linearis issues update AI-280 --status "Acceptance"

# Deployed to production
linearis issues update AI-280 --status "Done"
```

### Break down a large issue (SPIDR)
```bash
# Create spike first
linearis issues create "Spike: Research approach for X" --team AI --labels "Spike" --priority 3

# Then implementation issues
linearis issues create "Implement X - path A" --team AI --labels "Feature" --priority 2
linearis issues create "Implement X - path B" --team AI --labels "Feature" --priority 2
```
