---
name: pipeline-deals
description: Check pipeline status, deal context, and prepare for customer calls by pulling from meetings, email, Slack, and CRM data. Use when the user asks about deals, pipeline, or customer prep.
allowed-tools: Bash(psql *), Bash(curl *), Bash(gog *), Bash(npx agent-slack *)
---

# Pipeline & Deals

Cross-system intelligence for pipeline management and customer prep. Pulls from meetings database, Pipeline API, Google Workspace, and Slack.

**Prerequisites**: `/postgres`, `/google-workspace`, and `/slack` skills should be set up.

## Pipeline API

The Pipeline API is hosted on Vercel:
```
https://indemn-pipeline.vercel.app/api/
```

Query it directly:
```bash
curl -s "https://indemn-pipeline.vercel.app/api/deals" | jq '.'
curl -s "https://indemn-pipeline.vercel.app/api/pipeline/summary" | jq '.'
```

Inspect available endpoints:
```bash
curl -s "https://indemn-pipeline.vercel.app/api" | jq '.'
```

## Customer Call Prep Workflow

When preparing for a call with a customer, pull from multiple sources:

### 1. Meeting history
```sql
SELECT m.title, m.date, ma.summary
FROM meetings m
JOIN meeting_analyses ma ON ma.meeting_id = m.id
WHERE m.title ILIKE '%CUSTOMER%'
ORDER BY m.date DESC
LIMIT 5;
```

### 2. Signals and objections
```sql
SELECT type, description, evidence FROM historical_signals WHERE company ILIKE '%CUSTOMER%' ORDER BY created_at DESC LIMIT 10;
SELECT objection, response, response_worked FROM historical_objections WHERE objection ILIKE '%CUSTOMER%' ORDER BY created_at DESC LIMIT 5;
```

### 3. Recent Slack mentions
```bash
npx agent-slack search --query "CUSTOMER_NAME"
```

### 4. Recent emails
```bash
gog gmail search "CUSTOMER_NAME" --max-results 10 --format json
```

### 5. Deal status
```bash
curl -s "https://indemn-pipeline.vercel.app/api/deals?company=CUSTOMER_NAME" | jq '.'
```

### 6. Contact info
```sql
SELECT name, email, role FROM people WHERE company ILIKE '%CUSTOMER%';
```

## Drafting Follow-Up Emails

After gathering context, use Google Workspace to draft:
```bash
gog gmail draft --to "contact@customer.com" --subject "Following up on our conversation" --body "Draft text here"
```

Or create a Google Doc for collaborative prep:
```bash
gog docs create --title "Call Prep - CUSTOMER - DATE" --parent-folder "/Customers"
```

## Pipeline Summary

For a quick pipeline overview:
```bash
curl -s "https://indemn-pipeline.vercel.app/api/pipeline/summary" | jq '.'
```
