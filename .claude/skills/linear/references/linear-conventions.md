# Linear Conventions — Indemn

Source: Ganesh Iyer's "Tying strategy to development" doc (Google Doc, Feb 2026)

## Hierarchy

```
Initiatives (strategic outcomes — "how Indemn wins")
  └── Projects (output collections — closest to epics)
       └── Issues (atomic work items — closest to stories)
```

- **Initiatives** = business outcomes, not backlogs. Optional target dates. Map to Kyle's "Strategic Tracks".
- **Projects** = collections of issues delivering complete output (shipped code). Can span multiple cycles. One parent initiative (pick the most compelling if multiple apply). Include supplemental research in project body.
- **Issues** = atomic work, completable in one cycle by one person. Max 10 story points. Clear "Done" criteria.

## Teams (5)

| Key | Team | Scope |
|-----|------|-------|
| AI | Agentic AI | AI agents, reasoning, RAG, RLHF, Jarvis, workflow automations |
| COP | Copilot + Platform | Platform UI, AI suggestions, analytics, navigation, RBAC, MFA |
| FRONT | Insurance Frontends | Webchat widget, landing pages, customer-facing UI |
| WEB | Marketing Website | Marketing site, SEO, CMS, lead capture, conversions |
| DEVOPS | DevOps | Infrastructure, CI/CD, observability, security, tenant isolation |

## Issue Workflow States (12)

```
Triage → Backlog → Queued → In Progress → Ready for Testing → In Review → Acceptance → Done
                                    ↑                              ↓
                                    └──────── Rework ──────────────┘

Terminal states: Done, Canceled, Duplicate, Archived
```

| # | Status | Owner | Entry Condition | Transitions To |
|---|--------|-------|-----------------|----------------|
| 1 | **Triage** | Product | External/Slack intake | Backlog, Queued, Canceled, Duplicate |
| 2 | **Backlog** | Product | Relevant but not prioritized | Queued |
| 3 | **Ready for Planning** | Product | Spec complete (e.g. vibe coding solution) but not mapped to cycle | Queued |
| 4 | **Soon** | Product | Candidate for NEXT cycle (from cycle planning meeting) | Queued |
| 5 | **Queued** | Engineering | Committed to current cycle, sprint-ready | In Progress |
| 6 | **In Progress** | Engineering | Dev started | Ready for Testing |
| 7 | **Ready for Testing** | Engineering | PR opened, dev complete | In Review |
| 8 | **In Review** | QA | QA testing started (NOT code review) | Acceptance, Rework |
| 9 | **Rework** | Engineering+QA | Defects found in testing | In Progress |
| 10 | **Acceptance** | QA+Engineering | QA passed, PR merged to dev/main | Done |
| 11 | **Done** | Engineering Lead | Deployed to production | (terminal) |
| 12 | **Canceled** | Product+Engineering | Not relevant | (terminal) |
| 13 | **Duplicate** | Product | Covered by existing issue | (terminal) |
| 14 | **Archived** | Product+Engineering | Historical record, auto-archive | (terminal) |

**Key flow notes:**
- Issues start in Backlog (organic) or Triage (from Slack/external)
- "Soon" = marked for next cycle at planning meeting. Product specs them before cycle starts.
- "Queued" = current cycle, engineers can pick up
- "Ready for Testing" = PR opened. "In Review" = QA actively testing (not code review)
- "Acceptance" = merged, candidate for next prod deploy. "Done" = deployed to prod.

## Cycles

- 2-week sprints (planning to move to 2-week dev + 1-week cooldown = 3 weeks)
- Cycle planning: biweekly, led by Kyle. Plans the NEXT cycle, not current.
- Effort allocation: 70% feature/product, 20% bug fixes, 10% tech debt/research
- Release: first Monday after cycle end. Retrospective: first Tuesday after cycle end.

## Estimation (Fibonacci)

| Effort | Story Points |
|--------|-------------|
| < 4 hours (0.5 days) | 1 |
| 4-8 hours (1 day) | 2 |
| 8-16 hours (2 days) | 3 |
| 16-24 hours (3 days) | 5 |
| 24-32 hours (4 days) | 8 |
| 40 hours (5 days) | 10 (cap) |

- Cap: 10 points. If > 10, break down using SPIDR.
- If estimates miss by >30% for 3 cycles in a row, flag in retrospective.

## SPIDR Breakdown Method

When an issue exceeds 10 points, split by:
1. **Spike** — Separate research/POC from implementation
2. **Path** — Separate user workflows into individual issues
3. **Interface** — Start with minimal v1, extend in follow-up issues
4. **Data** — Cover different data types in separate issues
5. **Rules** — Generalize business rules first, add nuance in subsequent issues

## Labels (workspace-level)

| Label | Purpose |
|-------|---------|
| Bug | Didn't work as per spec |
| Regression | Used to work, now broken |
| Improvement | Better way to do something existing |
| Feature | Net-new capability |
| Customer Implementation | Customer request or long-term project |
| Hot Fix | Fix applied directly to production |
| Hot Patch | Improvement applied directly to production |
| Catchment | Issues created ad hoc (e.g. from Slack) |
| Missed Product Spec | Should have been addressed sooner |
| Migrated | Originally from another service |
| Workflow automations | External workflow (Airtable, n8n) |
| Research | Information gathering ahead of key work |
| Spike | Engineering POC to validate a hypothesis |

**Customer labels** (under "Customer Implementation" group): Alliance, Johnson, Tillman, Rankin, Loro, Family First, Jewelers Mutual/EventGuard, Silent Sports (McKay), IIANC, Branch, Distinguished Programs, GIC, Insurica, Union General

**Outcome tags** (on Initiatives): Strategic Control, Client Retention, Operational Efficiency, Revenue Growth

## Escalation Protocol

1. **Scope conflict**: Product posts in #dev-squad, engineering provides estimates within 48 business hours
2. **Personnel contention**: Alert #dev-squad tagging Kyle. He makes the final call on priority.
3. **Cycle creep**: Alert Ganesh + Kyle in #dev-squad with prefix `[CREEP]` immediately

## Priority Levels

Linear uses P0-P4 (Urgent, High, Medium, Low, No priority). Align with cycle allocation:
- P0/P1: Hot fixes, production issues → Queued immediately
- P2: Feature work for current/next cycle
- P3: Backlog items
- P4: Nice-to-have, future consideration
