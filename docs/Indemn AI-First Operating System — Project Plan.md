# Indemn AI-First Operating System — Project Plan

# Vision

We're building an AI-first operating system for Indemn. An intelligence layer that gives every team member instant access to company knowledge — meetings, pipeline, customers, communications — through natural conversation.

Claude Code is our first interface. We chose it because it's the most powerful dynamic interface available right now — it can connect to every API we use, search across all our data, and handle complex multi-step workflows. But the real asset isn't the interface. It's the connected intelligence underneath. If something better emerges tomorrow, the intelligence layer moves with us.

This is how Indemn thinks about AI: first principles, always.

# First Principles

These aren't just project guidelines. This is how we build at Indemn.

1\. **Immediate business value on signup.** The moment someone opens Claude Code, they should be able to do something useful — search meetings, pull customer context, find a doc. No setup wizard, no reading docs first.

2\. **Craig builds it, Cam proves it.** Craig is Kyle's technical co-builder. Together they scope the architecture, connect the APIs, and solve problems. Cam is the validation layer — if a COO with minor engineering background can get value, the design is right.

3\. **The OS is the intelligence, not the interface.** The real asset is the connected intelligence layer (meetings, pipeline, customer data, communications). That layer should be interface-agnostic — accessible from Claude Code today, from a custom UI tomorrow, from whatever comes next.

4\. **AI-first means asking "can AI do this?" before anything else.** Before we hire, before we build a manual process, before we create a spreadsheet — can an AI agent handle it? As Cam said: "First principles. So long before we hire anybody anything else we should be asking can AI do this?"

5\. **Kyle is the administrator.** As owner of every software platform Indemn uses, Kyle can grant API access to any system. The project plan with Craig inventories every platform and decides what to expose, to whom, and how.

6\. **Vibe code is fine until someone depends on it.** Clear maturity levels: Experiment (someone trying something), Useful (used regularly, documented), Supported (team depends on it daily, deployed, monitored).

# What's Available Today

When you open Claude Code with the right configuration, you can already:

## Meetings Intelligence (3,141 meetings, 22,000+ extracted items)

\- "What did we discuss with INSURICA last week?"  
\- "Find customer quotes about operational efficiency"  
\- "What objections has Jewelers Mutual raised?"  
\- "Show me Kyle's action items from the last 14 days"

## Pipeline & Deals

\- "Show me the pipeline summary"  
\- "What's the deal status with Branch?"  
\- "Draft an email to Julia at INSURICA about the renewal"

## Google Docs & Drive

\- "List my recent Google Docs"  
\- "Create a doc called 'Call Prep \- INSURICA' in the Customers folder"  
\- "Read the Series A foundation document"

## Slack

\- "What's happening in \#sales?"  
\- "Search Slack for messages about Tillman"  
\- "Post an update to \#dev"

Plus: Linear (engineering tracking), Airtable (bot configs, EventGuard ops), GitHub (code review, productivity), Stripe (revenue analytics), Apollo (company enrichment).

# Platform Inventory — Every API Kyle Controls

## Already Integrated:

\- Gmail — Pipeline API (send, search, draft emails with full context)  
\- Google Docs/Drive — MCP tools (42 tools for docs \+ spreadsheets \+ folders)  
\- Slack — MCP tools (search, post, DMs, threads)  
\- Meetings/Apollo — REST API (3,141 meetings, 22K+ extracted items)  
\- Linear — GraphQL API (issue management, roadmap)  
\- Airtable — REST API (211 bases, bot configs, EventGuard ops)  
\- GitHub — REST API (30 repos, indemn-ai org, read-only)  
\- Stripe — REST API \+ scripts (revenue analytics, MRR, churn)  
\- Apollo — REST API (company enrichment, employee data)

## Not Yet Integrated (Craig to Scope):

\- Vercel — Meetings deployment (Prisma migration 68% remaining) — HIGH PRIORITY  
\- Neon (Postgres) — Direct database access — MEDIUM  
\- Google Calendar — Meeting scheduling, upcoming prep — HIGH  
\- Google Analytics — Website traffic, conversion data — LOW  
\- HubSpot, Zoom/Teams, AWS — TBD

# Roles

## Kyle — Administrator & Co-Builder

\- Owns admin access to every platform  
\- Works with Craig to define architecture and connect APIs  
\- Sets access tiers and governance rules  
\- Final decision on what to expose and to whom

## Craig — Technical Partner

\- Kyle's co-builder for the operating system  
\- Scopes architecture, connects APIs, solves technical problems  
\- Deploys and monitors integrations  
\- Classifies software maturity (Experiment → Useful → Supported)  
\- Team-tier access: Customers folder, Operations folder, all APIs

## Cam — First User & Validation Layer

\- COO, validates the system works for non-engineers  
\- If it works for Cam, it works for the sales team and the company  
\- Executive-tier access: everything Craig has, plus Executive folder and Series A  
\- Feedback drives improvements  
\- Does NOT need to know API URLs or technical architecture

# Phase Timeline

## Phase 1: Foundation (This Week)

\- Finish meetings Prisma migration and deploy to Vercel (Vercel configured, Postgres migrated, 13 services need conversion)  
\- Craig's Claude Code setup with full technical access  
\- Platform inventory review with Craig  
\- Verify Google Drive folder sharing

## Phase 2: Cam's First Experience (After Phase 1\)

\- Design Cam's "first 5 minutes" experience  
\- Cam's simplified Claude Code setup  
\- Cam runs real workflows: search meetings, manage docs, read Slack, draft emails  
\- Feedback loop begins

## Phase 3: Intelligence Layer Expansion (Week 2-3)

\- Cross-system workflows ("Prepare for call with X" pulls meetings \+ pipeline \+ emails \+ Slack)  
\- Weekly summary automation  
\- Follow-up detection  
\- Meetings extraction for product intelligence  
\- Software maturity classification for all scripts

## Phase 4: Extend to Team (Week 3-4)

\- Repeatable onboarding template by role  
\- Identify workflows that should become custom UI vs stay in Claude Code  
\- Connect to Skills architecture (COP-312/313/314)

# Known Challenges & How We're Solving Them

Meetings Prisma migration incomplete  
The meetings database is already on Neon PostgreSQL (225K rows migrated) and the Vercel project is configured. 13 of 19 services still need Prisma conversion (from SQLite imports). Estimated 2-3 focused days to complete. This is Craig's first technical task.

## Google Drive folder placement

Documents created without specifying a folder land in personal Drive. Every CLAUDE.md includes explicit folder IDs and the rule to always specify parentFolderId.

## MCP server memory footprint

Each MCP server uses \~350MB. We run Slack \+ Google Docs. Adding more requires being intentional about which servers are worth the overhead.

## Access tiers

Not everyone should see everything. Four-tier model (Team → Executive → Personal → Archive) is defined in DATA-GOVERNANCE.md and enforced through CLAUDE.md configuration per person.

# Success Criteria

\- Craig can query all APIs (Pipeline, Meetings, Linear, GitHub, Slack, Google Docs)  
\- Cam can search meetings, manage Google Docs, read Slack, draft emails — without knowing any API URLs  
\- Meetings deployed: team can access meeting intelligence without localhost  
\- Cam's first week: captured feedback, acted on it  
\- Cross-system workflows working: "prepare for call with X" pulls from multiple sources  
\- Clear maturity classification for all pipeline scripts

# What This Means for Indemn

This isn't just an internal tool project. This is Indemn practicing what it preaches. We sell AI-powered digital workforce to insurance companies. Our own operations should run the same way — AI-first, connected intelligence, human judgment applied where it matters most.

If we can build an operating system that makes our 15-person team as effective as a 30-person team, that's the same value proposition we sell to customers. And that story — "we run our own company this way" — is one of the most powerful things we can tell investors during Series A.

We're not building a tool. We're building the way Indemn works.  
