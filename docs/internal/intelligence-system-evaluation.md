# Intelligence System Evaluation

> Assessment of Kyle's meetings intelligence database (Neon Postgres).
> Conducted: 2026-02-13
> By: Craig (with Claude Code analysis)

---

## What the System Is

Kyle used Claude Code (via MCPs) to build a meetings intelligence pipeline over ~3 weeks (all created ~Jan 23, 2026). It ingests meetings from 3 sources, stores transcripts as utterances, then runs LLM extraction strategies against them to produce structured intelligence.

The database also contains a CRM layer (companies, contacts, deals, implementations), investor relations tracking, email/outreach management, and Slack monitoring — an attempt to build a unified operational database for the company.

### Data Flow

```
Meeting Sources (Apollo, Granola, Gemini)
    → Meeting record + MeetingUtterance (transcript segments) + MeetingParticipant
    → ExtractionStrategy (prompt template per meeting type)
    → ExtractionRun (execution record)
    → MeetingExtraction (decisions, learnings, problems, objections)
    → Signal (health, expansion, champion, churn_risk, blocker)
    → Quote (tagged by usability: internal, case_study, pitch, testimonial)
    → ActionItem
```

### Scale

| Entity | Count |
|--------|-------|
| Companies | 1,059 |
| Contacts | 5,961 |
| Deals | 1,089 |
| Meetings | 3,141 |
| Utterances | 183,697 |
| Participants | 5,185 |
| Extractions | 14,612 |
| Signals | 3,240 |
| Quotes | 3,681 |
| Action Items | 1,469 |

---

## Documented vs. Actual

| What | Documented | Actual |
|------|-----------|--------|
| Tables | 66 | **123** — 48 completely empty, many are duplicated snake_case/PascalCase pairs |
| Meetings with transcripts | "3,141 with transcripts" | **1,239** have utterance data (39.4%). **0** have the `transcript` column populated. 2,777 (88%) have no text content at all |
| Meetings with extractions | Implied: most | **1,501** (47.8%) have at least one extraction. 363 were processed through the formal ExtractionRun pipeline in Jan 2026; the rest came from migration/direct insertion |
| Meetings with signals | Not documented | **1,152** (36.7%) |
| Meetings with quotes | Not documented | **1,156** (36.8%) |
| Company-linked meetings | Not documented | **366 of 3,141** (11.7%). Of 302 external meetings, only 111 (36.8%) link to a company |
| Signal company linkage | Not documented | Only **902 of 3,240** (27.8%) link to a company |
| Action items usable for follow-up | 1,469 action items | **1** has an owner. **0** have due dates. All 1,469 are `pending` |
| Full-text search indexes | Not documented | **Zero.** No GIN/GiST indexes. Searching utterances = sequential scan over 183K rows |
| Duplicate meetings | "some duplicates" | **Systemic** — most meetings since Sep 2025 appear 2-3x across sources |
| Extraction pipeline status | Implied: ongoing | **Stopped ~Jan 30, 2026.** 377 ExtractionRun records, all from January 2026 |
| Meeting ingestion status | Implied: ongoing | **Stopped ~Jan 30, 2026.** No meetings after that date |

---

## What Works Well

### 1. Extraction quality is good
The extracted decisions, learnings, objections, and problems are genuinely useful, specific, and actionable. Examples from the database:

- "Pilot AI Solution with 2-3 agencies (Alliance, O'Connor, Hosket Ulan) first" (decision)
- "Integrate AI assistant with RAG system and human-in-the-loop capabilities into BT Core platform" (technical decision)
- "Rate card for additional services set at three tiers: $100, $150, $175/hour" (strategic decision)

The categorization (strategic/commitment/process/technical for decisions; sales/product/implementation for learnings; technical/process/timing/trust/price for objections) adds real value.

### 2. The quote system is clever
3,681 quotes pre-tagged by usability and sentiment:

| usableFor | positive | neutral | negative | total |
|-----------|----------|---------|----------|-------|
| internal | 754 | 743 | 307 | 1,804 |
| case_study | 606 | 261 | 83 | 950 |
| pitch | 560 | 105 | 23 | 688 |
| testimonial | 229 | — | — | 229 |

Having 229 ready-to-use testimonials and 950 case study quotes, pre-tagged, is genuinely valuable for Series A preparation.

### 3. The signal model captures real business intelligence
Signal type distribution:

| Signal Type | Count | With Company Link |
|------------|-------|-------------------|
| health | 1,229 | 331 (26.9%) |
| expansion | 1,085 | 279 (25.7%) |
| champion | 685 | 245 (35.8%) |
| churn_risk | 151 | 23 (15.2%) |
| blocker | 88 | 24 (27.3%) |

The signal types map well to what sales/customer success teams need. 100% of signals link to a meeting. Company linkage is the gap.

### 4. The extraction strategy architecture is sound
Different prompt templates for customer vs. internal vs. investor meetings, versioned, with performance tracking (tokens used, duration). 4 active strategies, 3 experimental. Average extraction: ~7,309 tokens, ~14.7 seconds. This is the right abstraction.

---

## What Doesn't Work

### 1. Meetings are not truly searchable
- No full-text search indexes on any text column (all 23 indexes are standard btree)
- `Meeting.transcript` and `Meeting.summary` columns are empty across all 3,141 rows
- To search, you'd ILIKE across 183K utterances with no index — slow and unreliable
- Only 11.7% of meetings link to a company, so you can't filter by company reliably

### 2. The schema is massively bloated
123 tables when ~25-30 would suffice. Parallel table sets exist:

| PascalCase (Prisma) | snake_case (Legacy) | PascalCase Rows | snake_case Rows |
|---------------------|---------------------|-----------------|-----------------|
| MeetingUtterance | meeting_utterances | 183,697 | 189,304 |
| MeetingParticipant | meeting_participants | 5,195 | 5,290 |
| ExtractionRun | extraction_runs | 377 | 395 |
| ExtractionStrategy | extraction_strategies | 7 | 7 |
| ActionItem | action_items | 1,469 | 1,468 |

Additionally, `historical_decisions` (5,515), `historical_learnings` (5,099), `historical_quotes` (3,681), `historical_signals` (3,239), `historical_problems` (2,970), `historical_objections` (1,608) duplicate data from the extraction tables.

48 tables are completely empty — aspirational features never built (playbooks, digests, morning briefs, weekly goals, etc.).

30 tables have no foreign key relationships at all (fully orphaned in the schema).

### 3. The extraction pipeline ran once and stopped
377 ExtractionRun records, all from January 2026, covering 363 distinct meetings. The formal pipeline hasn't run since Jan 30. The remaining ~1,138 meetings with extractions were populated through migration or direct insertion before the ExtractionRun tracking existed.

### 4. Company linkage is broken
Only 11.7% of meetings link to a company via `companyId`. The `MeetingExtraction.companyId` column is almost entirely NULL (4 populated out of 14,612). Signals are slightly better at 27.8% company linkage, but this means most intelligence isn't attributable to a company.

### 5. Action items are unusable
All 1,469 are `pending`. 1 has an owner. 0 have due dates. 235 have a customer name. The follow-up-check workflow skill is effectively non-functional because of this.

### 6. Systemic meeting duplication
Since Granola was added in September 2025, most meetings appear 2x (Apollo + Granola), some 3x (Apollo + Granola + Gemini). Sample from January 2026:

- "Cameron / Kyle - Claude Code" — 3 copies (gemini, granola, apollo)
- "Indemn x Silent Sports Prototype" — 3 copies
- "Indemn & Granada Catch Up" — 3 copies
- Most other meetings — 2 copies

This inflates all counts and would cause duplicate extractions if the pipeline were rerun.

---

## Meeting Sources & Coverage

### Source Distribution
| Source | Meetings | Period |
|--------|----------|--------|
| Apollo | 2,704 | Jan 2025 — Jan 2026 |
| Granola | 426 | Sep 2025 — Jan 2026 |
| Gemini | 11 | Jan 2026 only |

### Meeting Type Distribution
| Type | Count | Description |
|------|-------|-------------|
| internal | 1,642 | General internal |
| internal_sync | 599 | Standups/syncs |
| internal_1on1 | 359 | 1-on-1s |
| internal_dev | 191 | Dev team |
| customer | 141 | Existing clients |
| prospect | 116 | Sales prospects |
| implementation | 45 | Onboarding |
| hiring | 18 | Recruitment |
| investor | 9 | Fundraising |

~89% of meetings are internal. Only ~302 (9.6%) are external-facing.

---

## Schema Inventory

### Tables with meaningful data (worth keeping)
Meeting (3,141), MeetingUtterance (183,697), MeetingParticipant (5,195), MeetingExtraction (14,612), ExtractionRun (377), ExtractionStrategy (7), Signal (3,240), Quote (3,681), ActionItem (1,469), Company (1,059), Contact (5,968), Deal (1,089), AIScoringResult (1,001), Email (425), Activity (318), ImplementationMilestone (228), InvestorFirm (212), DuplicateGroupMember (146), InvestorInteraction (130), InvestorContact (94), TeamUpdate (80), LearnedMatch (71), DuplicateGroup (65), Implementation (19), SlackChannel (28), SlackExtraction (7), User (10), SystemHealth (5), StageConfig (7)

### Tables that are legacy duplicates (candidates for removal)
meeting_utterances (189,304), meeting_participants (5,290), meeting_ai_insights (7,048), historical_decisions (5,515), historical_learnings (5,099), historical_quotes (3,681), historical_signals (3,239), historical_problems (2,970), historical_objections (1,608), action_items (1,468), extraction_runs (395), extraction_strategies (7), granola_meetings (3,224), customer_profiles (44), topics (994), commitments (745), people (247), goals (236), customer_aliases (10)

### 48 empty tables
CallParticipant, Commitment, CompanyMerge, CompanyRelationship, DataAssociation, EmailFeedback, EmailOpen, EmailPattern, Playbook, PlaybookTask, QualificationSession, WeeklyGoal, analyses, business_progress, category_extractions, classification_reviews, customer_contacts, customer_request_extraction_status, customer_requests, daily_review, digest_drafts, digests, extraction_comparisons, extraction_evaluations, extraction_item_feedback, granola_analyses, historical_extraction_status, important_meetings, insights, leadership_moments, learning_corrections, linear_review_queue, meeting_corrections, meeting_duplicates, meeting_goals, meeting_people, meeting_takeaways, meeting_topics, morning_briefs, pattern_extractions, person_companies, playbooks, pursuit_commitments, recordings, strategy_performance, team_member_context, tokens, transcripts

---

## Kyle's Open Questions — Our Answers

### 1. Is the data model right? Too many tables?

Yes, too many. 123 tables when ~25-30 would suffice. The bloat comes from: legacy snake_case duplicates, `historical_*` duplicates, aspirational empty tables, and orphaned config tables. The core model (Meeting → Utterance/Extraction/Signal/Quote → Company/Deal) is sound. The surrounding tables need cleanup.

### 2. Extraction pipeline: Claude on every meeting — right approach?

The LLM extraction with meeting-type-specific prompt strategies is good for **structured intelligence** (decisions, signals, quotes). It should be **complemented by**:

- **Embeddings/vector search** for full-text semantic search across utterances and transcripts. Store in Pinecone (already available). Enables "What did we discuss about X?"
- **Meeting summaries**: Populate the empty `Meeting.summary` column. Cheap LLM call, makes the entire corpus browsable.
- **Full-text search indexes** (GIN on tsvector): For fast keyword search as a complement to semantic search.

Hybrid approach: embed for search, extract for intelligence, summarize for browsing.

### 3. Deployment — Prisma migration incomplete

The dual schema (PascalCase Prisma + snake_case legacy) is the visible symptom. Clean up the schema before deploying — deploying 123 tables to production codifies tech debt.

### 4. Should meetings merge into copilot-server or stay separate?

Stay separate. This is a data warehouse / analytics system. Copilot-server is transactional. Different access patterns, different scaling needs. Keep them independent but queryable from both.

### 5. How to make this data accessible to other Claude Code instances?

What we've already built — skills + psql connection string — is the right answer. Any Claude Code instance with `NEON_CONNECTION_STRING` and the meeting-intelligence skill can query the database. The skill IS the interface.

---

## Impact on Operating System Skills

| Skill | Status | Why |
|-------|--------|-----|
| meeting-intelligence | Partially effective | Query patterns correct, but data gaps (company linkage, search) limit what queries return |
| call-prep | Partially effective | Works for companies with linked meetings/signals (~12%). Sparse results for most |
| follow-up-check | Non-functional | Action items have no owners or due dates |
| weekly-summary | Partially effective | Can aggregate signals/extractions, but limited by the Jan 30 data cutoff |
| pipeline-deals | Unaffected | Pipeline data (deals, companies) is well-populated independently of meetings |

---

## Priority Improvements (When Ready)

1. **Deduplicate meetings** — merge Apollo/Granola/Gemini records for the same meeting
2. **Add full-text search** — GIN indexes on utterance, extraction, signal, and quote text columns
3. **Fix company linkage** — match meetings to companies using participant emails, titles, `relatedCustomer`
4. **Generate meeting summaries** — populate `Meeting.summary` for meetings with transcript data
5. **Drop dead tables** — delete 48 empty tables and snake_case duplicates
6. **Restart ingestion** — fix whatever stopped the pipeline on Jan 30
7. **Backfill extractions** — run the extraction pipeline on the ~700 meetings with transcripts but no extractions
