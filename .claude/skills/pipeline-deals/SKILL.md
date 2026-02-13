---
name: pipeline-deals
description: Check pipeline status, deal context, and customer prep across meetings database and Pipeline API. Use when the user asks about deals, pipeline, or customer prep.
allowed-tools: Bash(psql *), Bash(curl *)
---

# Pipeline & Deals

Pipeline intelligence from two sources: the Neon Postgres database (deals, companies, scoring, stale alerts) and the Pipeline API on Vercel.

**Connection**: `source .env && /opt/homebrew/opt/libpq/bin/psql "$NEON_CONNECTION_STRING" -c "<query>"`

All table and column names are **PascalCase and must be double-quoted**.

## Pipeline API

```bash
source .env && curl -s "https://indemn-pipeline.vercel.app/api/deals" | jq '.'
source .env && curl -s "https://indemn-pipeline.vercel.app/api/pipeline/summary" | jq '.'
source .env && curl -s "https://indemn-pipeline.vercel.app/api" | jq '.'
```

## Database Tables & Key Columns

**Deals**
- `"Deal"` — `"companyId"`, `status`, `"expectedARR"`, `"compositeScore"`, `"isStale"`, `"staleDays"`, `segment`, `"useCase"`, `"opportunityBucket"`, `"ownerId"`
  - `status` (DealStatus enum): `CONTACT`, `DISCOVERY`, `DEMO`, `PROPOSAL`, `NEGOTIATION`, `WON`, `LOST`
  - `segment`: `Enterprise`, `Mid-Market`, `SMB`

**Scoring**
- `"AIScoringResult"` — `"dealId"`, `"compositeScore"`, `"suggestedARR"`, `confidence`, `status`

**Stale Alerts**
- `"StaleAlert"` — `"dealId"`, `reason`, `"suggestedAction"`, `"isResolved"`

**Companies**
- `"Company"` — `id`, `name`, `domain`, `type`, `industry`, `"healthColor"`, `"healthScore"`

**Implementations**
- `"Implementation"` — `"companyId"`, `"customerName"`, `stage`, `"healthStatus"`, `"hasVoiceAgent"`, `"hasChatAgent"`
  - `stage` (ImplementationStage enum): `KICKOFF` → `SCOPING` → `CONFIGURATION` → `TESTING` → `LAUNCH` → `ONBOARDING` → `ACTIVE` → `LIVE` → `EXPAND` → `RENEW` → `ADVOCATE`

## Key JOINs

- Deals to companies: `"Deal"."companyId"` → `"Company".id`
- Scoring to deals: `"AIScoringResult"."dealId"` → `"Deal".id`
- Stale alerts to deals: `"StaleAlert"."dealId"` → `"Deal".id`
- Implementations to companies: `"Implementation"."companyId"` → `"Company".id`

## Full Reference

For complete deal pipeline model, signal-to-deal relationships, email/outreach system, and implementation tracking details, see the meeting-intelligence skill's `references/data-dictionary.md`.
