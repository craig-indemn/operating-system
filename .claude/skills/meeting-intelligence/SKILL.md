---
name: meeting-intelligence
description: Query meeting transcripts, extracted intelligence (decisions, quotes, signals, objections), and customer insights from the Neon Postgres database. Use when the user asks about meetings, customers, or company intelligence.
allowed-tools: Bash(psql *)
---

# Meeting Intelligence

Query Indemn's meeting intelligence database — 3,211 meetings with transcripts, extracted decisions, quotes, signals, objections, learnings, and customer profiles.

**Prerequisite**: The `/postgres` skill must be set up (psql installed, `NEON_CONNECTION_STRING` set).

## How to Use This

Don't hardcode queries. The database schema may evolve. Always:
1. Check available tables: `psql "$NEON_CONNECTION_STRING" -c "\dt"`
2. Inspect table structure before querying: `psql "$NEON_CONNECTION_STRING" -c "\d tablename"`
3. Then write your query based on the actual schema

## Known Table Categories

**Core meeting data:**
- `meetings` — title, date, source, duration, host, category
- `meeting_utterances` — full transcripts with speaker, timestamps
- `meeting_participants` — who attended, speaking time, utterance count
- `meeting_analyses` — AI-generated summaries, insights, action items

**Extracted intelligence:**
- `historical_decisions` — decisions made, categorized, with rationale
- `historical_quotes` — notable quotes with speaker, sentiment, context
- `historical_signals` — champion/expansion/churn/blocker/health signals by company
- `historical_objections` — objections raised, responses given, effectiveness
- `historical_learnings` — lessons learned, categorized
- `historical_problems` — problems identified, severity, customer

**CRM-adjacent:**
- `people` — contacts with company, role, interaction history
- `customer_profiles` — aggregated intelligence per customer
- `customer_contacts`, `person_companies` — relationship mapping

**Workflow:**
- `extraction_runs` — tracks processing history
- `action_items`, `commitments` — meeting follow-ups
- `daily_reviews`, `morning_briefs` — operational outputs

## Common Query Patterns

**What did we discuss with a customer?**
```sql
SELECT m.title, m.date, ma.summary
FROM meetings m
JOIN meeting_analyses ma ON ma.meeting_id = m.id
WHERE m.title ILIKE '%CUSTOMER_NAME%'
ORDER BY m.date DESC
LIMIT 10;
```

**Customer signals (expansion, churn risk, etc.):**
```sql
SELECT type, description, evidence, created_at
FROM historical_signals
WHERE company ILIKE '%CUSTOMER_NAME%'
ORDER BY created_at DESC;
```

**Recent action items:**
```sql
SELECT * FROM action_items
ORDER BY created_at DESC
LIMIT 20;
```

**Quotes about a topic:**
```sql
SELECT quote, speaker_name, sentiment, context
FROM historical_quotes
WHERE quote ILIKE '%operational efficiency%'
ORDER BY created_at DESC;
```

**Objections and how they were handled:**
```sql
SELECT objection, category, response, response_worked
FROM historical_objections
WHERE objection ILIKE '%pricing%'
ORDER BY created_at DESC;
```

These are starting points. Inspect the actual schema columns before running queries — the column names above are based on Kyle's documentation and may differ slightly in the database.
