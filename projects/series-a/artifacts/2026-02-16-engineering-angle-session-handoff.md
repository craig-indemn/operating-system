---
ask: "How can the CTO/engineering perspective supplement the Series A with data and technical story that makes investors' jaws drop?"
created: 2026-02-16
workstream: series-a
session: 2026-02-16-b
sources:
  - type: google-drive
    description: "35 documents across Series A, Operations, and Context Files folders — all downloaded to source-docs/"
  - type: codebase
    description: "Read CLAUDE.md and README for web_operators/, evaluations/, and indemn-observability/ repos"
---

# Session Handoff: Engineering Angle for Series A

## What Happened This Session

### Phase 1: Downloaded and analyzed all 35 Series A docs
- 9 files from Series A folder (Cam's Takes, Investor Update, Deal Model, Revenue Model, Customer Stories, JM Story, Outreach Tracker, Project Plan)
- 18 files from Operations folder (Four Outcomes, Revenue Defense, Compendium, Messaging, Objection Handling, Customer Segments, Collaboration Plan, Associate Suite, Brand Guidelines, Business Architecture, Customer Intelligence Library, Strategic Plan, Prospects Tracker, plus extras)
- 8 files from Context Files folder (Company Overview, Market Analysis, ICPs, GTM Strategy, Communications Philosophy, Master Context, System Prompt, Tailored Value Props)
- All saved locally in `projects/series-a/source-docs/` organized by folder
- Full analysis saved as artifact: `artifacts/2026-02-16-series-a-comprehensive-analysis.md`

### Phase 2: Course correction from Craig
Craig redirected the approach. Key points:

1. **Don't critique Cam's fundraising strategy** — Cam knows what he's doing, and the team already raised seed. The initial analysis was too critical and overstepped.

2. **The real angle is the engineering story** — Craig is building frontier agentic AI infrastructure. Web operators automating browser workflows, deep agents for end-to-end evaluation, observatory analytics for understanding conversation outcomes. The investment is in the PEOPLE and SYSTEM, not just revenue metrics.

3. **This should be iterative and conversational** — Don't make sweeping claims or pull data without discussing it. Work together to figure out what data tells the best story.

### Phase 3: Explored what Craig has actually built

**Web Operators** (`/Users/home/Repositories/web_operators/`)
- Reusable framework where an LLM agent operates a browser to complete complex tasks
- First use case: automating insurance policy renewals (FOP and CAP) in Applied Epic for Johnson Insurance / Everett Cash Mutual
- Uses Deep Agents (LangGraph) + Agent Browser CLI for browser interaction
- Self-learning loop: run -> capture trajectory -> refine path document -> run again -> improve
- Middleware pipeline: observation masking (manage context), state injection (working memory), loop detection (prevent runaway)
- Path documents are structured markdown playbooks — versioned, SHA-256 hashed, with per-step metrics
- Run comparison, metrics aggregation, batch config generation across models
- Resume from failure with dependency validation
- 173 tests across 10 files, 4 phases complete, API layer in design (FastAPI + MongoDB + EC2)
- Applied Epic is a notoriously complex Angular SPA with custom ASI web components — this is hard automation

**Evaluation System** (`/Users/home/Repositories/evaluations/`)
- End-to-end agentic evaluation harness: datasets, test cases, evaluator configs, runs
- Three test types: single-turn, multi-turn simulated (LLM plays the customer), multi-turn replay (replay historical conversations)
- Evaluator types: correctness, hallucination, conciseness, relevance, toxicity, custom LLM judges, code evaluators
- LangSmith integration with MongoDB mirroring for internal access
- FastAPI backend (port 8002) + React UI frontend (port 5174)
- Craig describes this as "one of the most complex agents we have" — AI creating scenarios, creating rubrics, running simulations, reviewing results

**Observatory / Observability** (`/Users/home/Repositories/indemn-observability/`)
- Full analytics platform for AI chatbot conversations in insurance
- Central innovation: **precursor analysis** — lift calculation showing WHY outcomes happen, not just what happened
  - `lift = P(Factor | Outcome) / P(Factor | all conversations)`
  - lift > 1.5 = precursor (predicts outcome), lift < 1.0 = protective
- Outcome tracking: resolved_autonomous, resolved_with_handoff, partial_then_left, unresolved_abandoned, missed_handoff, etc.
- Flow/Sankey visualization of conversation journeys (stage-based, scope-adaptive)
- Structure view: Platform -> Customer -> Agent architecture diagram with tool/KB connections
- Comparison/export: outcome vs outcome, path vs path, CSV/JSON export
- Cohort analysis: any selection creates a cohort that can be analyzed for precursors
- 17 specification documents, all phases complete (backend + frontend)
- Ingestion pipeline: MongoDB (tiledesk) + LangSmith traces -> observatory_conversations -> aggregations
- PDF report generation capability
- Data lives in MongoDB tiledesk database in observatory_* collections

**The story these three systems tell together:**
Indemn doesn't just build chatbots. They build agents that operate enterprise software (web operators), they have analytics to understand exactly how agents perform and why (observatory with precursor analysis), and they have infrastructure to continuously improve agents using AI itself (evaluation harness). The platform is the moat, not any individual agent. And the team ships at frontier speed.

## Where to Pick Up Next Session

### Immediate next step: Pull Observatory data from MongoDB
- Use the `/mongodb` skill to query observatory collections in the tiledesk database
- Key collections to explore: `observatory_conversations`, `daily_snapshots`, `precursor_lifts`, `flow_paths`, `flow_links`, `category_distributions`
- Work iteratively with Craig to discover what data tells the most compelling story
- Don't make assumptions — look at the data together and discuss

### The approach going forward
- **Iterative and conversational** — not "here's my analysis," but "here's what I found, what do you think?"
- **Start with Observatory data** — conversation volumes, resolution rates, outcomes, precursor insights across customers
- **Then consider Stripe** — revenue data to complement the conversation/engagement data
- **Frame around what Craig is building** — web operators, eval system, observatory as the technical differentiators
- **The pitch**: investment in people + system that operates at the frontier of agentic AI, not just a revenue story

### Craig's framing (in his words)
- "We are at the frontier of agentic automation, building web operators to automate browser actions, building agents to perform end to end sales workflows, we can build almost anything"
- "I genuinely believe we can automate anything that is currently manual barring legitimate human judgement required"
- "We are in tune with advancements as they happen in the AI space and in literal days can implement capabilities using frontier technologies"
- "The investment is not only in our finances, our customers, even the technology we have itself, but also an investment into our system and our company energy and company PEOPLE who are on the ball"

## Open Questions (Updated)
- What Observatory data is currently populated? Which customers have data?
- What date ranges does the observatory data cover?
- What's the most impressive precursor insight the observatory has surfaced?
- How many conversations are tracked across all customers?
- Can we get resolution rate trends over time per customer?
- What does the web operator run data look like? Any completed runs with success metrics?
- What evaluation runs have been completed? What do the results show?
