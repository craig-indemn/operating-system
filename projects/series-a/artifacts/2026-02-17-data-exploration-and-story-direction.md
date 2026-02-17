---
ask: "Pull production data from MongoDB, explore what exists, and iterate toward a data/analytics story for Kyle to supplement the Series A investor pitch"
created: 2026-02-17
workstream: series-a
session: 2026-02-17-a
sources:
  - type: mongodb
    description: "tiledesk database — observatory_conversations, daily_snapshots, precursor_lifts, requests, messages, organizations, structure_agents, bot_tools, knowledge_bases"
  - type: github
    description: "git log from indemn-observability, evaluations, web_operators repos"
---

# Session: Data Exploration & Story Direction

## What Kyle Asked For

Kyle asked Craig to provide analytics and data to supplement the Series A investor pitch. Kyle doesn't have a specific format or data set in mind — he trusts Craig (the data/engineering guy) to figure out what's compelling and bring something they can iterate on together.

## What We Found in MongoDB (tiledesk database)

### Platform-wide totals
- 2,067,835 messages
- 143,040 conversations (since Aug 2023)
- 77,635 leads captured
- 273 agents built across 65 organizations
- 516 knowledge bases, 2,481 tool integrations
- 55 agents active in the last 30 days
- NOTE: "Indemn" org (~1,700 conversations/month) is demos/beta — exclude from customer metrics

### Monthly conversation volumes by customer (last 7 months)
| Customer | Aug 25 | Sep | Oct | Nov | Dec | Jan 26 | Feb* |
|----------|--------|-----|-----|-----|-----|--------|------|
| GIC Underwriters | 1,782 | 1,833 | 2,633 | 1,935 | 2,052 | 2,663 | 1,397 |
| EventGuard | 988 | 1,136 | 6,672 | 831 | 753 | 1,709 | 848 |
| Family First | 324 | 290 | 114 | 374 | 151 | 192 | 39 |
| Distinguished | 443 | 262 | 216 | 155 | 58 | 67 | 21 |
| Bonzah | 158 | 115 | 324 | 166 | 108 | 294 | 43 |
| Open Enrolment | 0 | 0 | 336 | 293 | 162 | 244 | 14 |
| Rankin Insurance | 0 | 0 | 0 | 0 | 2 | 176 | 177 |
*(Feb partial — mid-month)*

### Observatory data (live ~6 weeks, 7,695 conversations analyzed)
- GIC Underwriters: 3,932 conversations (dominant data source)
- EventGuard: 1,486 | Indemn internal: 1,295 | Insurica: 136 | Rankin: 138
- Plus ~25 other agents with smaller volumes
- Outcome groups (excluding bounces): 1,832 success / 1,216 failure / 1,017 partial / 493 unknown
- Craig flagged: "success" is a poor label for the outcome metric — don't frame it as a success rate

### Observatory document structure (rich per-conversation data)
Each conversation record includes:
- `scope`: platform, customer, agent, agent version, distribution
- `time`: started, ended, duration, last activity, closed by/at
- `user`: user ID, language, device, agency code/name, email, name
- `entry`: channel, source URL, referrer, first message
- `metrics`: message count, user messages, self-served depth, CSR intervention depth/steps, CSR name, time to join
- `categories`: status (ai_active, csr_engaged, etc.), system tags
- `classifications`: sentiment, resolution quality, frustrated user, explicit handoff request, intent, sub-intent
- `derived`: handoff precursors, dropoff precursors
- `stages`: platform, customer, agent, entry, intent, resolution path, tool outcome, outcome
- `langsmith`: trace IDs, total tokens, LLM call count, tool call count, KB queries
- `trace_summary`: LLM calls, tool calls, total tokens, total cost, errors

### Daily snapshots (568 total, per-agent and per-customer per-day)
Each snapshot includes:
- **volume**: total conversations, users, avg message count, by channel/device/hour/day
- **outcomes**: resolved autonomous, resolved with handoff, partial, abandoned, timeout, missed handoff — with rates for each
- **experience**: sentiment counts and rates, liked/disliked
- **operations**: handoff requests/completed/missed, automated conversations, handoff completion rate
- **performance**: total tokens, cost, avg/p95/max response time, error rate, KB gap rate, tool success rate
- **content**: intent counts and top intents

### Precursor lift analysis (20,516 records)
Statistical lift calculation: P(Factor | Outcome) / P(Factor | all conversations)
- Frustrated users → 28-46x more likely to abandon
- Tool call failures → 22-27x precursor to abandonment
- Negative sentiment → 33x correlation with unresolved
- Explicit handoff requests missed → 22x lift on missed handoff
- Most high-lift precursors are behavioral (frustration, tool failures) not demographic

### Intent distribution (non-bounce conversations)
- Informational: 2,018
- Service request: 1,116
- Product inquiry: 631
- Handoff request: 564
- Technical: 243

## Git Build Timelines (verified from commit history)

| System | First Commit | Latest Commit | Total Commits (approx) |
|--------|-------------|---------------|----------------------|
| Observatory | 2025-12-22 | 2026-02-10 | ~30 in first 30 days |
| Evaluations | 2026-01-20 | 2026-02-13 | ~30 in first 24 days |
| Web Operators | 2026-02-12 | 2026-02-16 | 23 in 5 days |

Evaluation numbers in the database (7,301 test case details, 12,893 evaluation results) are from testing on only 2 agents — not a volume metric, just initial testing of the system.

## The Story Direction (iterated with Craig)

### What the story IS
- Kyle asked for data/analytics to supplement the investor pitch
- The engineering angle: Indemn knows insurance deeply AND has the engineering ability to leverage every new AI capability and develop original solutions — fast
- The three systems (Observatory, Eval, Web Operators) are evidence that the team can build production infrastructure at speed
- The team automates its own workflows using the same agentic approach it sells to customers — that's the meta-proof
- The full automation loop: customer conversation → back-office transaction → quality monitoring → improvement cycle → repeat

### What the story is NOT
- Not a critique of the existing pitch materials (Cam and Kyle own the fundraising strategy)
- Not financial analysis (previous session's revenue numbers are unverified — Cam/Kyle have the real data)
- Not a standalone document — it supplements what Kyle and Cam are already building
- Not a formatted slide — the format and design is Kyle/Cam's domain, we provide the substance

### The pitch in Craig's words
The core idea: we know insurance AND we can build and ship AI faster than anyone in the space. Every new AI capability that becomes available, we have it in production within days. We develop our own solutions when nothing exists yet (Observatory's precursor analysis, autonomous eval generation, browser automation for legacy insurance software). The impact: insurance distribution is built on manual labor — conversations, data entry, reviews. Indemn automates the full loop, and the platform gets more powerful with every conversation and every AI advancement.

### What's not landing yet
- Craig feels the drafts don't capture the real IMPACT on the insurance industry
- The "built in X days" framing sounds negligent rather than impressive — better to emphasize the team's ability to adopt and ship new capabilities continuously
- The format of a written document/slide isn't right — Craig needs to work with Kyle on the actual pitch format
- The content and spirit are good but need to be translated into whatever format Kyle works in (likely slides with a designer)

## Open Questions for Next Session
- What format does Kyle actually work in for the pitch? Slides? Talking points?
- Should Craig present the raw data/numbers to Kyle and let Kyle decide how to frame them?
- Are the platform totals (2M messages, 143K conversations) accurate for investor use, or do they include too much test/demo traffic?
- Observatory "outcome" classifications need review — Craig flagged the labeling as poor
- How to present the impact story without it sounding like generic AI marketing copy
- Should Stripe revenue data be part of this at all, or is that entirely Cam/Kyle's domain?
