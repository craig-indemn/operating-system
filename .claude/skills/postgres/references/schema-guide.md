# Neon Postgres Schema Reference — Meetings Intelligence Database

> **Database**: `neondb` on Neon Postgres
> **Total Tables**: 66
> **Last profiled**: 2026-02-11

## Connection

```
Connection string stored in .env as NEON_CONNECTION_STRING — do not hardcode credentials in committed files.
```

---

## Table of Contents

1. [Custom Enum Types](#custom-enum-types)
2. [Core Entity Tables](#1-core-entity-tables)
3. [Meeting & Transcript Tables](#2-meeting--transcript-tables)
4. [Extracted Intelligence Tables](#3-extracted-intelligence-tables)
5. [CRM / Deal Pipeline Tables](#4-crm--deal-pipeline-tables)
6. [Email & Outreach Tables](#5-email--outreach-tables)
7. [Implementation / Customer Success Tables](#6-implementation--customer-success-tables)
8. [Investor Relations Tables](#7-investor-relations-tables)
9. [Slack Integration Tables](#8-slack-integration-tables)
10. [Data Quality & Matching Tables](#9-data-quality--matching-tables)
11. [AI & Scoring Tables](#10-ai--scoring-tables)
12. [System / Workflow Tables](#11-system--workflow-tables)

---

## Custom Enum Types

### CompanyType
| Value | Description |
|-------|-------------|
| `BROKER` | Insurance broker |
| `MGA_MGU` | Managing General Agent / Managing General Underwriter |
| `CARRIER` | Insurance carrier |
| `OTHER` | Other company type (default) |

### DealStatus
| Value | Order | Description |
|-------|-------|-------------|
| `CONTACT` | 1 | Initial engagement (stale after 14 days) |
| `DISCOVERY` | 2 | Qualification and needs analysis (stale after 7 days) |
| `DEMO` | 3 | Founder demo (stale after 5 days) |
| `PROPOSAL` | 4 | Reviewing proposal (stale after 3 days) |
| `NEGOTIATION` | 5 | Finalizing contract terms (stale after 2 days) |
| `WON` | 6 | Deal closed, beginning implementation |
| `LOST` | 7 | Deal did not close |
| `CLOSED` | 8 | (Terminal state) |

### GtmSegment
| Value |
|-------|
| `DIGITAL_PRODUCT` |
| `BROKER_RESOURCES` |
| `AGENT_NETWORK` |

### HealthStatus
| Value |
|-------|
| `ON_TRACK` |
| `AT_RISK` |
| `BLOCKED` |

### ImplementationStage
| Value | Order |
|-------|-------|
| `KICKOFF` | 1 |
| `SCOPING` | 2 |
| `CONFIGURATION` | 3 |
| `TESTING` | 4 |
| `LAUNCH` | 5 |
| `ONBOARDING` | 6 |
| `ACTIVE` | 7 |
| `LIVE` | 8 |
| `EXPAND` | 9 |
| `RENEW` | 10 |
| `ADVOCATE` | 11 |

### InvestorType
| Value |
|-------|
| `VC` |
| `CVC` |
| `ANGEL` |
| `STRATEGIC` |
| `FAMILY_OFFICE` |
| `OTHER` |

### InvestorTier
| Value |
|-------|
| `A` |
| `B` |
| `C` |
| `D` |

### InvestorStatus
| Value | Order |
|-------|-------|
| `RESEARCH` | 1 |
| `TARGET` | 2 |
| `COLD` | 3 |
| `WARM_INTRO` | 4 |
| `CONTACTED` | 5 |
| `INITIAL_MEETING` | 6 |
| `FOLLOW_UP` | 7 |
| `PARTNER_MEETING` | 8 |
| `DEEP_DIVE` | 9 |
| `INTEREST` | 10 |
| `STRONG_INTEREST` | 11 |
| `TERM_SHEET` | 12 |
| `COMMITTED` | 13 |
| `INVESTED` | 14 |
| `DECLINED` | 15 |
| `PASSED` | 16 |
| `DORMANT` | 17 |

---

## 1. Core Entity Tables

### User
**Purpose**: Internal Indemn team members.
**Row count**: 10

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `email` | text | NOT NULL | | Unique email (e.g., `kyle@indemn.ai`) |
| `name` | text | NOT NULL | | Full name (e.g., `Kyle Geoghan`) |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Indexes**: PK on `id`, UNIQUE on `email`.
**Referenced by**: `Deal.ownerId`, `Activity.userId`, `EmailAccount.userId`.

---

### Company
**Purpose**: Companies in the sales pipeline and customer base — primarily insurance industry firms.
**Row count**: 1,059

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `name` | text | NOT NULL | | Company name |
| `companyType` | CompanyType | NOT NULL | `OTHER` | BROKER (252), MGA_MGU (243), CARRIER (96), OTHER (468) |
| `website` | text | YES | | Company website URL (479 populated) |
| `domain` | text | YES | | Domain name, unique (567 populated) |
| `linkedinUrl` | text | YES | | LinkedIn profile URL (466 populated) |
| `notes` | text | YES | | Free-form notes |
| `airtableId` | text | YES | | Legacy Airtable record ID (unique) |
| `rawData` | jsonb | YES | | Raw imported data |
| `apolloId` | text | YES | | Apollo.io ID (633 populated, unique) |
| `annualRevenue` | double precision | YES | | Annual revenue |
| `employeeCount` | integer | YES | | Number of employees (459 populated) |
| `foundedYear` | integer | YES | | Year founded |
| `headquarters` | text | YES | | HQ location string |
| `industry` | text | YES | | Industry (459 populated; top: `insurance` at 385) |
| `googleDriveFolderId` | text | YES | | Google Drive folder ID |
| `googleDriveFolderUrl` | text | YES | | Google Drive folder URL |
| `healthColor` | text | YES | | `green` (75), `yellow` (12), `red` (1) — only 88 populated |
| `healthScore` | integer | YES | | 0-100 score (88 populated) |
| `lastMeetingAt` | timestamp(3) | YES | | Last meeting date (0 populated) |
| `meetingCount` | integer | YES | | Number of meetings (88 populated) |
| `timezone` | text | YES | | Company timezone |
| `amsNotes` | text | YES | | Agency management system notes |
| `amsSystem` | text | YES | | AMS used by the company |
| `employeeRange` | text | YES | | Employee range string |
| `hqCity` | text | YES | | HQ city |
| `hqCountry` | text | YES | | HQ country |
| `hqState` | text | YES | | HQ state |
| `phone` | text | YES | | Phone number |
| `specialties` | text[] | YES | `ARRAY[]::text[]` | Specialty areas |
| `subIndustry` | text | YES | | Sub-industry |
| `technologies` | text[] | YES | `ARRAY[]::text[]` | Technologies used |

**Indexes**: PK on `id`, UNIQUE on `airtableId`, `apolloId`, `domain`.
**Referenced by**: Many tables including `Deal`, `Contact`, `Meeting`, `Signal`, `Quote`, `Activity`, `Email`, `Implementation`, `TeamUpdate`, `SlackChannel`, etc.

---

### Contact
**Purpose**: Individual contacts at companies. Linked to companies via `companyId`.
**Row count**: 5,961

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `email` | text | NOT NULL | | Unique email address |
| `firstName` | text | YES | | First name (5,958 populated) |
| `lastName` | text | YES | | Last name (5,940 populated) |
| `title` | text | YES | | Job title (5,799 populated) |
| `phone` | text | YES | | Phone number (5,450 populated) |
| `isPrimary` | boolean | NOT NULL | `false` | Whether this is the primary contact (198 are primary) |
| `linkedinUrl` | text | YES | | LinkedIn URL (5,708 populated) |
| `companyId` | text | NOT NULL | | FK to Company |
| `apolloId` | text | YES | | Apollo.io contact ID (5,828 populated, unique) |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Indexes**: PK on `id`, UNIQUE on `email`, `apolloId`. Index on `companyId`.
**FK**: `companyId` -> `Company(id)` CASCADE DELETE.
**Referenced by**: `Email.contactId`, `Activity.contactId`, `ScheduledOutreach.contactId`, `CallRecording.contactId`, `SlackExtraction.contactId`.

---

## 2. Meeting & Transcript Tables

### Meeting
**Purpose**: Core meeting records from various sources. Central entity in the extraction pipeline.
**Row count**: 3,141
**Date range**: 2000-01-01 to 2026-01-30

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key (UUIDs or source-prefixed like `apollo-...`, `gemini-...`) |
| `source` | text | NOT NULL | | `apollo` (2,704), `granola` (426), `gemini` (11) |
| `sourceId` | text | YES | | External ID from the source system |
| `title` | text | NOT NULL | | Meeting title (e.g., person names or topic) |
| `date` | timestamp(3) | NOT NULL | | Meeting date/time |
| `durationSeconds` | integer | YES | | Duration in seconds |
| `transcript` | text | YES | | Full transcript text |
| `notes` | text | YES | | Meeting notes |
| `summary` | text | YES | | AI-generated summary |
| `meetingType` | text | YES | | `internal` (1,642), `internal_sync` (599), `internal_1on1` (359), `internal_dev` (191), `customer` (141), `prospect` (116), `implementation` (45), `hiring` (18), `investor` (9) |
| `hostName` | text | YES | | Host name |
| `hostEmail` | text | YES | | Host email |
| `recordingUrl` | text | YES | | Recording URL |
| `autoClassified` | boolean | NOT NULL | `false` | Whether type was auto-classified |
| `relatedCustomer` | text | YES | | Customer name string |
| `companyId` | text | YES | | FK to Company |
| `category` | text | YES | | `internal` (1,629), `internal_sync` (553), `internal_1on1` (357), `prospect` (208), `internal_dev` (172), `customer` (111), `partner` (85), `hiring` (14), `investor` (9), `past` (3) |
| `visibility` | text | YES | `private` | `private` (3,079), `team` (62) |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Indexes**: PK on `id`, UNIQUE on `(source, sourceId)`. Indexes on `companyId`, `date`, `meetingType`, `visibility`.
**FK**: `companyId` -> `Company(id)` SET NULL.
**Referenced by**: `MeetingUtterance`, `MeetingParticipant`, `MeetingExtraction`, `ExtractionRun`, `ActionItem`, `Quote`, `Signal`.

---

### MeetingUtterance
**Purpose**: Individual speaker utterances (transcript segments) within a meeting.
**Row count**: 183,697 (across 1,239 distinct meetings)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `meetingId` | text | NOT NULL | | FK to Meeting |
| `speakerName` | text | NOT NULL | | Speaker name (e.g., `Kyle Geoghan`) |
| `text` | text | NOT NULL | | Utterance text content |
| `startMs` | integer | NOT NULL | | Start time in milliseconds |
| `endMs` | integer | NOT NULL | | End time in milliseconds |
| `sequenceOrder` | integer | YES | | Order within meeting (0-based) |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Indexes**: PK on `id`. Indexes on `meetingId`, `(meetingId, sequenceOrder)`, `(meetingId, startMs)`, `speakerName`.
**FK**: `meetingId` -> `Meeting(id)` CASCADE DELETE.
**Avg utterance duration**: ~14.7 seconds.

---

### MeetingParticipant
**Purpose**: People who participated in a meeting.
**Row count**: 5,185 (across 1,711 distinct meetings)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `meetingId` | text | NOT NULL | | FK to Meeting |
| `name` | text | NOT NULL | | Participant name |
| `email` | text | YES | | Participant email |
| `isInternal` | boolean | YES | | 3,208 internal, 1,977 external |
| `company` | text | YES | | Company name string |
| `title` | text | YES | | Job title |
| `isHost` | boolean | NOT NULL | `false` | Whether this person hosted (currently all false) |
| `speakingTimeMs` | integer | YES | | Total speaking time in ms (currently unpopulated) |
| `utteranceCount` | integer | NOT NULL | `0` | Count of utterances (currently all 0) |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Indexes**: PK on `id`. Indexes on `meetingId`, `company`, `email`.
**FK**: `meetingId` -> `Meeting(id)` CASCADE DELETE.

---

## 3. Extracted Intelligence Tables

### MeetingExtraction
**Purpose**: AI-extracted insights from meeting transcripts. The primary extraction output table.
**Row count**: 14,612

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `meetingId` | text | NOT NULL | | FK to Meeting |
| `extractionType` | text | NOT NULL | | `decision` (5,691), `learning` (4,691), `problem` (2,622), `objection` (1,608) |
| `text` | text | NOT NULL | | Extracted text content |
| `category` | text | YES | | Category within extraction type (see below; 13,688 populated) |
| `personName` | text | YES | | Person associated (0 populated) |
| `resolved` | boolean | NOT NULL | `false` | Whether the item is resolved |
| `resolution` | text | YES | | Resolution description |
| `severity` | text | YES | | Severity level (0 populated) |
| `confidence` | text | YES | | For `learning` type only: `insight` (2,483), `worked` (1,721), `didnt_work` (487) |
| `companyId` | text | YES | | FK to Company (4 populated) |
| `context` | text | YES | | Additional context (2,548 populated) |
| `extractedDate` | timestamp(3) | YES | | Date extracted (2,610 populated) |
| `participants` | jsonb | YES | | Participant info (2,521 populated) |
| `rationale` | text | YES | | Reasoning (795 populated) |
| `responseWorked` | boolean | YES | | Whether response to objection worked (35 populated) |
| `reversible` | boolean | YES | | Whether decision is reversible (2,521 populated) |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Category values by extractionType**:

| extractionType | Categories (by count) |
|---------------|----------------------|
| `decision` | `strategic` (1,931), `commitment` (1,183), NULL (924), `process` (895), `technical` (428), `product` (325) |
| `learning` | `sales` (2,628), `product` (1,303), `implementation` (591), `support` (142), `process` (12) |
| `objection` | `technical` (501), `process` (470), `timing` (190), `trust` (181), `price` (155), `competition` (69) |
| `problem` | `process` (1,123), `technical` (805), `communication` (279), `resource` (268), `integration` (85) |

**Indexes**: PK on `id`. Indexes on `meetingId`, `extractionType`, `companyId`.
**FK**: `meetingId` -> `Meeting(id)` CASCADE DELETE.

---

### ExtractionRun
**Purpose**: Tracks each AI extraction run against a meeting transcript. Links meetings to extraction strategies.
**Row count**: 377

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `meetingId` | text | NOT NULL | | FK to Meeting |
| `strategyId` | text | NOT NULL | | FK to ExtractionStrategy |
| `meetingType` | text | YES | | `customer` (208), `internal` (161), `investor` (4), `vendor` (4) |
| `resultJson` | jsonb | YES | | Full extraction result |
| `tokensUsed` | integer | YES | | LLM tokens consumed (avg: ~7,309) |
| `durationMs` | integer | YES | | Extraction duration in ms (avg: ~14,711) |
| `error` | text | YES | | Error message if failed (1 has error) |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Indexes**: PK on `id`. Indexes on `meetingId`, `strategyId`, `createdAt`, `meetingType`.
**FK**: `meetingId` -> `Meeting(id)` CASCADE DELETE; `strategyId` -> `ExtractionStrategy(id)` RESTRICT DELETE.

---

### ExtractionStrategy
**Purpose**: Defines the AI extraction prompt and schema for different meeting types.
**Row count**: 7

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `name` | text | NOT NULL | | Strategy name |
| `version` | integer | NOT NULL | `1` | Version number |
| `meetingTypes` | text[] | YES | `ARRAY[]::text[]` | Which meeting types this strategy handles |
| `promptTemplate` | text | NOT NULL | | LLM prompt template |
| `outputSchema` | jsonb | YES | | Expected output JSON schema |
| `isActive` | boolean | NOT NULL | `false` | Whether currently active |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Active strategies**: Customer Meeting Extraction v1 (v2, 210 runs), Internal Meeting Extraction v1 (156 runs), Investor Meeting Extraction v1 (4 runs), Vendor/Partner Meeting Extraction v1 (4 runs).
**Inactive**: Customer Success, Sales Prospect, Internal Tech (from category-extraction, 1 run each).

---

### Signal
**Purpose**: Business signals extracted from meetings — buying signals, risk indicators, etc.
**Row count**: 3,240

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `meetingId` | text | NOT NULL | | FK to Meeting |
| `companyId` | text | YES | | FK to Company |
| `signalType` | text | NOT NULL | | `health` (1,229), `expansion` (1,085), `champion` (685), `churn_risk` (151), `blocker` (88), `insight` (2) |
| `text` | text | NOT NULL | | Signal description |
| `personName` | text | YES | | Person associated with signal |
| `sentiment` | text | YES | | `positive` (2,877), `negative` (274), `neutral` (89) |
| `meetingDate` | timestamp(3) | YES | | Meeting date denormalized |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Indexes**: PK on `id`. Indexes on `meetingId`, `companyId`, `signalType`.
**FK**: `meetingId` -> `Meeting(id)` CASCADE DELETE; `companyId` -> `Company(id)` SET NULL.

---

### Quote
**Purpose**: Notable quotes from meeting participants — for case studies, pitches, testimonials.
**Row count**: 3,681
**Date range**: 2024-03-06 to 2026-01-28

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `meetingId` | text | NOT NULL | | FK to Meeting |
| `companyId` | text | YES | | FK to Company |
| `speakerName` | text | NOT NULL | | Who said it |
| `text` | text | NOT NULL | | The quote text |
| `context` | text | YES | | Context around the quote |
| `sentiment` | text | YES | | `positive` (2,152), `neutral` (1,114), `negative` (415) |
| `usableFor` | text | YES | | `internal` (1,804), `case_study` (950), `pitch` (688), `testimonial` (229), `product` (5), `insight` (3), `thought_leadership` (1), `competitive` (1) |
| `meetingDate` | timestamp(3) | YES | | Meeting date denormalized |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Indexes**: PK on `id`. Indexes on `meetingId`, `companyId`, `speakerName`.
**FK**: `meetingId` -> `Meeting(id)` CASCADE DELETE; `companyId` -> `Company(id)` SET NULL.

---

### ActionItem
**Purpose**: Action items extracted from meetings.
**Row count**: 1,469

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `meetingId` | text | NOT NULL | | FK to Meeting |
| `description` | text | NOT NULL | | What needs to be done |
| `owner` | text | YES | | Person responsible |
| `dueDate` | timestamp(3) | YES | | Due date |
| `status` | text | NOT NULL | `pending` | All currently `pending` |
| `category` | text | YES | | `other` (913), `meeting` (240), `writeup` (184), `implementation` (75), `proposal` (56) |
| `customer` | text | YES | | Customer name |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Indexes**: PK on `id`. Indexes on `meetingId`, `owner`, `status`.
**FK**: `meetingId` -> `Meeting(id)` CASCADE DELETE.

---

## 4. CRM / Deal Pipeline Tables

### Deal
**Purpose**: Sales pipeline deals/opportunities. Central CRM entity tied to companies.
**Row count**: 1,089

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `expectedARR` | double precision | YES | | Expected annual recurring revenue (1,087 populated) |
| `closeConfidence` | integer | YES | | Close confidence % (257 populated) |
| `priority` | text | YES | | `Low` (61), `Medium` (57), `High` (41), etc. (168 populated) |
| `notes` | text | YES | | Deal notes |
| `customerNotes` | text | YES | | Customer-specific notes |
| `nextStep` | text | YES | | Next action (278 populated) |
| `lastContactedAt` | timestamp(3) | YES | | Last contact date |
| `daysSinceContact` | integer | YES | | Days since last contact |
| `lastModifiedInSource` | timestamp(3) | YES | | Last modified in source system |
| `isStale` | boolean | NOT NULL | `false` | Whether deal is stale |
| `staleDays` | integer | NOT NULL | `0` | Days stale |
| `airtableId` | text | YES | | Legacy Airtable ID (unique) |
| `originalStatus` | text | YES | | Status before any changes |
| `companyId` | text | NOT NULL | | FK to Company |
| `ownerId` | text | YES | | FK to User |
| `status` | DealStatus | NOT NULL | `CONTACT` | `CONTACT` (817), `DISCOVERY` (201), `LOST` (37), `WON` (18), `NEGOTIATION` (10), `DEMO` (6) |
| `excitementLevel` | text | YES | | `High` (3), `Very High` (1) |
| `expectedCloseTiming` | text | YES | | Expected close timing |
| `leadTier` | integer | YES | | Lead tier ranking |
| `reachoutBucket` | text | YES | | `2026-target` (31) |
| `reachoutMessage` | text | YES | | Outreach message |
| `relationshipStrength` | integer | YES | | Relationship strength score |
| `apolloId` | text | YES | | Apollo.io ID (unique) |
| `companyFitScore` | integer | YES | | Company fit score |
| `compositeScore` | double precision | YES | | Composite deal score (713 populated) |
| `eagernessScore` | integer | YES | | Eagerness score |
| `milestoneScore` | integer | YES | | Milestone score |
| `relationshipScore` | integer | YES | | Relationship score |
| `useCaseScore` | integer | YES | | Use case score |
| `weightedValue` | double precision | YES | | Weighted pipeline value |
| `focusAddedAt` | timestamp(3) | YES | | When marked as focus account |
| `isFocusAccount` | boolean | NOT NULL | `false` | Whether this is a focus account |
| `segment` | text | YES | | `Enterprise` (109), `Mid-Market` (90), `SMB` (86) |
| `solutionInterest` | text | YES | | What solution the company is interested in (302 populated, mostly unique) |
| `useCase` | text | YES | | Primary use case (294 populated) |
| `focusTags` | text[] | YES | `ARRAY[]::text[]` | Focus tags |
| `closedAt` | timestamp(3) | YES | | When deal closed |
| `firstContactAt` | timestamp(3) | YES | | First contact date |
| `proposalSentAt` | timestamp(3) | YES | | Proposal sent date |
| `opportunityBucket` | text | YES | | `Broker Resources` (123), `Agent Network` (95), `Digital Products` (60) |
| `referenceCustomer` | text | YES | | Reference customer name |
| `customNotes` | text | YES | | Custom notes |
| `nextStepNotes` | text | YES | | Notes about next steps |
| `referralSource` | text | YES | | Referral source (0 populated) |
| `gtmSegment` | GtmSegment | YES | | `DIGITAL_PRODUCT` (71), `BROKER_RESOURCES` (21), `AGENT_NETWORK` (3) |

**Indexes**: PK on `id`, UNIQUE on `airtableId`, `apolloId`. Indexes on `companyId`, `ownerId`, `status`, `isStale`.
**FK**: `companyId` -> `Company(id)` CASCADE DELETE; `ownerId` -> `User(id)` SET NULL.
**Referenced by**: Many tables including `AIScoringResult`, `Activity`, `Email`, `DraftEmail`, `LeadResearch`, `OutreachCadence`, `OutreachSuggestion`, `StaleAlert`, `Task`, `ScheduledOutreach`, `DealOutreach`, `QualificationSession`, `PrepSession`, `SlackExtraction`, `CallRecording`.

---

### StageConfig
**Purpose**: Configuration for each deal pipeline stage — display settings and staleness thresholds.
**Row count**: 7

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `stage` | DealStatus | NOT NULL | | Unique stage (maps to DealStatus enum) |
| `order` | integer | NOT NULL | | Display order |
| `name` | text | NOT NULL | | Human-readable name |
| `color` | text | NOT NULL | | CSS color class |
| `description` | text | NOT NULL | | Stage description |
| `exitCriteria` | text | YES | | Criteria to exit this stage |
| `prepWork` | text | YES | | Prep work for this stage |
| `staleThresholdDays` | integer | NOT NULL | `7` | Days before deal is considered stale |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Indexes**: PK on `id`, UNIQUE on `stage`.

---

### Activity
**Purpose**: Activity log / timeline for companies, contacts, and deals.
**Row count**: 318

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `type` | text | NOT NULL | | `email_received` (104), `note` (73), `win` (43), `enrichment` (30), `email_sent` (16), `status_change` (11), `slack_win` (8), `slack_request` (6), `blocker_detected` (6), `call` (6), `champion_identified` (5), `captain_update` (4), and others |
| `description` | text | NOT NULL | | Activity description |
| `metadata` | jsonb | YES | | Additional metadata |
| `occurredAt` | timestamp(3) | NOT NULL | | When the activity occurred |
| `companyId` | text | YES | | FK to Company |
| `contactId` | text | YES | | FK to Contact |
| `dealId` | text | YES | | FK to Deal |
| `userId` | text | YES | | FK to User |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Indexes**: PK on `id`. Indexes on `companyId`, `dealId`, `occurredAt`.
**FK**: All optional FKs to `Company`, `Contact`, `Deal`, `User` with SET NULL on delete.

---

### StaleAlert
**Purpose**: Alerts for deals that have gone stale (no recent activity).
**Row count**: 24

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | NOT NULL | | FK to Deal |
| `reason` | text | NOT NULL | | Reason for staleness (e.g., `no_response`) |
| `context` | text | YES | | Additional context |
| `suggestedAction` | text | YES | | Suggested next action |
| `draftEmail` | text | YES | | Draft follow-up email |
| `isResolved` | boolean | NOT NULL | `false` | All 24 currently unresolved |
| `resolvedAt` | timestamp(3) | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Indexes**: PK on `id`. Indexes on `dealId`, `isResolved`.
**FK**: `dealId` -> `Deal(id)` CASCADE DELETE.

---

### Task
**Purpose**: Tasks associated with deals.
**Row count**: 5

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `title` | text | NOT NULL | | Task title |
| `description` | text | YES | | Task description |
| `dueDate` | timestamp(3) | NOT NULL | | Due date |
| `isCompleted` | boolean | NOT NULL | `false` | Completion status |
| `completedAt` | timestamp(3) | YES | | Completion date |
| `dealId` | text | NOT NULL | | FK to Deal |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Indexes**: PK on `id`. Indexes on `dealId`, `dueDate`, `isCompleted`.
**FK**: `dealId` -> `Deal(id)` CASCADE DELETE.

---

### AutoAction
**Purpose**: Automated actions taken by the system (e.g., flagging deals for review based on signals).
**Row count**: 26

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | NOT NULL | | FK to Deal |
| `companyName` | text | NOT NULL | | Company name |
| `actionType` | text | NOT NULL | | All `flag_review` |
| `trigger` | text | NOT NULL | | `blocker_detected` (13), `close_signal_meeting` (11), `unresolved_objections` (1), `auto_pipeline_multi_signal` (1) |
| `triggerEmailId` | text | YES | | Triggering email ID |
| `fieldChanged` | text | NOT NULL | | `none` (25), `status` (1) |
| `previousValue` | text | YES | | Previous field value |
| `newValue` | text | YES | | New field value |
| `reviewed` | boolean | NOT NULL | `false` | Whether reviewed |
| `reviewedAt` | timestamp(3) | YES | | Review date |
| `reviewedBy` | text | YES | | Who reviewed |
| `reverted` | boolean | NOT NULL | `false` | Whether reverted |
| `revertedAt` | timestamp(3) | YES | | Revert date |
| `revertReason` | text | YES | | Reason for revert |
| `additionalContext` | text | YES | | Additional context |
| `confidence` | text | NOT NULL | `high` | `medium` (13), `high` (13) |
| `explanation` | text | NOT NULL | | Explanation of action |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Indexes**: PK on `id`. Indexes on `dealId`, `actionType`, `reviewed`, `createdAt`.

---

### LeadResearch
**Purpose**: AI-generated research summaries for leads.
**Row count**: 5

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | NOT NULL | | FK to Deal (unique) |
| `status` | text | NOT NULL | `pending` | |
| `lastResearchedAt` | timestamp(3) | YES | | |
| `meetingCount` | integer | NOT NULL | `0` | |
| `quoteCount` | integer | NOT NULL | `0` | |
| `healthScore` | double precision | YES | | |
| `champions` | text[] | YES | `ARRAY[]::text[]` | |
| `keyQuotes` | jsonb | YES | | |
| `painPoints` | jsonb | YES | | |
| `relationshipSummary` | text | YES | | |
| `suggestedOpeners` | jsonb | YES | | |
| `warningFlags` | jsonb | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Indexes**: PK on `id`, UNIQUE on `dealId`.
**FK**: `dealId` -> `Deal(id)` CASCADE DELETE.

---

### QualificationSession
**Purpose**: Deal qualification sessions (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | NOT NULL | | FK to Deal |
| `level` | text | NOT NULL | | Qualification level |
| `status` | text | NOT NULL | `in_progress` | |
| `responses` | jsonb | NOT NULL | | Qualification responses |
| `startedAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `completedAt` | timestamp(3) | YES | | |

---

### PrepSession
**Purpose**: Meeting preparation sessions. One per deal.
**Row count**: 1

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | NOT NULL | | FK to Deal (unique) |
| `agenda` | text[] | YES | `ARRAY[]::text[]` | Agenda items |
| `goals` | text | NOT NULL | `''` | Goals |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### PrepInsights
**Purpose**: AI-generated meeting preparation insights.
**Row count**: 1

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | NOT NULL | | FK to Deal (unique) |
| `briefing` | jsonb | NOT NULL | | Briefing data |
| `smartAgenda` | jsonb | NOT NULL | | Smart agenda |
| `objections` | jsonb | NOT NULL | | Expected objections |
| `relationships` | jsonb | NOT NULL | | Relationship data |
| `riskAssessment` | jsonb | NOT NULL | | Risk assessment |
| `personalContext` | jsonb | NOT NULL | | Personal context |
| `generatedAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `expiresAt` | timestamp(3) | NOT NULL | | |

---

### WeeklyGoal
**Purpose**: Weekly sales targets (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `weekStart` | timestamp(3) | NOT NULL | | Week start date (unique) |
| `proposalTarget` | integer | NOT NULL | `5` | |
| `replyRateTarget` | double precision | NOT NULL | `0.4` | |
| `proposalsSent` | integer | NOT NULL | `0` | |
| `proposalReplies` | integer | NOT NULL | `0` | |
| `dealsAdvanced` | integer | NOT NULL | `0` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### Commitment
**Purpose**: Commitments tracked from meetings (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `description` | text | NOT NULL | | |
| `owner` | text | YES | | |
| `status` | text | NOT NULL | `pending` | |
| `category` | text | YES | | |
| `customer` | text | YES | | |
| `meetingId` | text | YES | | |
| `meetingTitle` | text | YES | | |
| `meetingDate` | timestamp(3) | YES | | |
| `companyId` | text | YES | | |
| `dealId` | text | YES | | |
| `completedAt` | timestamp(3) | YES | | |
| `dismissedAt` | timestamp(3) | YES | | |
| `dismissReason` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

## 5. Email & Outreach Tables

### EmailAccount
**Purpose**: Connected email accounts (OAuth tokens).
**Row count**: 1

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `email` | text | NOT NULL | | Email address (unique) |
| `provider` | text | NOT NULL | | Email provider |
| `accessToken` | text | NOT NULL | | OAuth access token |
| `refreshToken` | text | NOT NULL | | OAuth refresh token |
| `expiresAt` | timestamp(3) | NOT NULL | | Token expiry |
| `userId` | text | NOT NULL | | FK to User |
| `lastSyncAt` | timestamp(3) | YES | | Last sync time |
| `syncStatus` | text | NOT NULL | `idle` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### Email
**Purpose**: Tracked emails (all outbound from `kyle@indemn.ai`).
**Row count**: 425
**Date range**: 2025-10-08 to 2026-02-11

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `gmailId` | text | NOT NULL | | Gmail message ID (unique) |
| `threadId` | text | NOT NULL | | Gmail thread ID |
| `subject` | text | YES | | Email subject |
| `snippet` | text | YES | | Short preview snippet |
| `body` | text | YES | | Full email body |
| `fromEmail` | text | NOT NULL | | Sender email |
| `toEmails` | text[] | YES | | Recipient emails |
| `ccEmails` | text[] | YES | | CC emails |
| `sentAt` | timestamp(3) | NOT NULL | | Send date |
| `isInbound` | boolean | NOT NULL | | All false (outbound only) |
| `hasAttachments` | boolean | NOT NULL | `false` | |
| `labels` | text[] | YES | | Gmail labels |
| `needsResponse` | boolean | NOT NULL | `false` | 5 need response |
| `responseReceived` | boolean | NOT NULL | `false` | |
| `daysSinceEmail` | integer | YES | | Days since sent |
| `companyId` | text | YES | | FK to Company |
| `contactId` | text | YES | | FK to Contact |
| `dealId` | text | YES | | FK to Deal |
| `firstOpenedAt` | timestamp(3) | YES | | First open time |
| `openCount` | integer | NOT NULL | `0` | Number of opens |
| `trackingId` | text | YES | | Email tracking pixel ID (unique) |
| `wasOpened` | boolean | NOT NULL | `false` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Indexes**: PK on `id`, UNIQUE on `gmailId`, `trackingId`. Indexes on `companyId`, `contactId`, `dealId`, `sentAt`, `threadId`, `trackingId`.
**FK**: `companyId` -> `Company`, `contactId` -> `Contact`, `dealId` -> `Deal` (all SET NULL).
**Referenced by**: `EmailOpen.emailId`.

---

### EmailOpen
**Purpose**: Email open tracking events (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `emailId` | text | NOT NULL | | FK to Email |
| `openedAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `ipAddress` | text | YES | | |
| `userAgent` | text | YES | | |

---

### DraftEmail
**Purpose**: AI-generated draft emails for outreach.
**Row count**: 12

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `companyId` | text | YES | | FK to Company |
| `companyName` | text | NOT NULL | | |
| `dealId` | text | YES | | FK to Deal |
| `contactName` | text | NOT NULL | | |
| `contactEmail` | text | YES | | |
| `subject` | text | NOT NULL | | Email subject |
| `body` | text | NOT NULL | | Email body |
| `context` | text | NOT NULL | | Context for generation |
| `priorEmails` | jsonb | YES | | Previous email thread |
| `meetings` | jsonb | YES | | Related meetings |
| `dealNotes` | text | YES | | |
| `priority` | text | NOT NULL | `medium` | `high` (6), `medium` (5), `low` (1) |
| `status` | text | NOT NULL | `pending` | `pending` (10), `skipped` (2) |
| `feedback` | text | YES | | |
| `scheduledFor` | timestamp(3) | YES | | |
| `sentAt` | timestamp(3) | YES | | |
| `reviewedAt` | timestamp(3) | YES | | |
| `reviewedBy` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### EmailPattern
**Purpose**: Email templates by scenario (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `name` | text | NOT NULL | | Template name |
| `description` | text | YES | | |
| `scenario` | text | NOT NULL | | Usage scenario |
| `companyType` | text | YES | | Target company type |
| `subjectTemplate` | text | NOT NULL | | Subject line template |
| `bodyTemplate` | text | NOT NULL | | Body template |
| `successRate` | double precision | YES | | Measured success rate |
| `useCount` | integer | NOT NULL | `0` | |
| `isActive` | boolean | NOT NULL | `true` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### EmailFeedback
**Purpose**: Feedback on emails sent (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | |
| `outreachId` | text | YES | | |
| `companyName` | text | NOT NULL | | |
| `contactName` | text | YES | | |
| `originalSubject` | text | NOT NULL | | |
| `originalBody` | text | NOT NULL | | |
| `finalSubject` | text | YES | | |
| `finalBody` | text | YES | | |
| `context` | text | YES | | |
| `feedbackType` | text | NOT NULL | | |
| `feedbackNotes` | text | YES | | |
| `aiSuggestions` | jsonb | YES | | |
| `wasOpened` | boolean | YES | | |
| `gotReply` | boolean | YES | | |
| `replyWasPositive` | boolean | YES | | |
| `lessonsLearned` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### OutreachSequence
**Purpose**: Multi-step outreach sequences (e.g., follow-up cadences).
**Row count**: 3

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `name` | text | NOT NULL | | `Re-engagement` (default), `Post-Demo`, `Post-Proposal` |
| `description` | text | YES | | |
| `isDefault` | boolean | NOT NULL | `false` | Re-engagement is default |
| `isActive` | boolean | NOT NULL | `true` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### OutreachStep
**Purpose**: Individual steps within an outreach sequence.
**Row count**: 10

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `sequenceId` | text | NOT NULL | | FK to OutreachSequence |
| `stepNumber` | integer | NOT NULL | | Step order (1-based) |
| `name` | text | NOT NULL | | Step name |
| `dayOffset` | integer | NOT NULL | | Days after sequence start |
| `subjectTemplate` | text | YES | | Subject template |
| `bodyTemplate` | text | YES | | Body template |
| `replyToThread` | boolean | NOT NULL | `true` | Whether to reply in thread |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Sequences detail**:
- **Re-engagement**: Step 1 (day 0, Initial Outreach, new thread), Step 2 (day 3, Follow-up 1), Step 3 (day 7, Follow-up 2), Step 4 (day 14, Break-up Email)
- **Post-Demo**: Step 1 (day 0, Demo Follow-up), Step 2 (day 3, Check-in), Step 3 (day 7, Decision Check)
- **Post-Proposal**: Step 1 (day 0, Proposal Sent), Step 2 (day 3, Proposal Check-in), Step 3 (day 7, Decision Push)

---

### DealOutreach
**Purpose**: Tracks a deal's active outreach sequence.
**Row count**: 2

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | NOT NULL | | FK to Deal |
| `sequenceId` | text | NOT NULL | | FK to OutreachSequence |
| `status` | text | NOT NULL | `active` | |
| `currentStep` | integer | NOT NULL | `1` | |
| `startedAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `pausedAt` | timestamp(3) | YES | | |
| `completedAt` | timestamp(3) | YES | | |
| `primaryThreadId` | text | YES | | Gmail thread ID |
| `primaryContactId` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Indexes**: PK on `id`, UNIQUE on `(dealId, sequenceId)`. Indexes on `dealId`, `sequenceId`, `status`.

---

### ScheduledOutreach
**Purpose**: Individual scheduled outreach emails.
**Row count**: 14

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | NOT NULL | | FK to Deal |
| `contactId` | text | YES | | FK to Contact |
| `dealOutreachId` | text | YES | | FK to DealOutreach |
| `stepId` | text | YES | | FK to OutreachStep |
| `scheduledFor` | timestamp(3) | NOT NULL | | When to send |
| `status` | text | NOT NULL | `scheduled` | `scheduled` (10), `cancelled` (3), `sent` (1) |
| `toEmail` | text | NOT NULL | | Recipient email |
| `subject` | text | NOT NULL | | Email subject |
| `body` | text | NOT NULL | | Email body |
| `replyToThreadId` | text | YES | | Thread to reply in |
| `sentAt` | timestamp(3) | YES | | Actual send time |
| `emailId` | text | YES | | Resulting Email record ID |
| `gmailThreadId` | text | YES | | Gmail thread ID |
| `failureReason` | text | YES | | If send failed |
| `isAdHoc` | boolean | NOT NULL | `false` | Whether ad-hoc (not from sequence) |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### OutreachCadence
**Purpose**: Tracks outreach cadence metrics per deal.
**Row count**: 6

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | NOT NULL | | FK to Deal (unique) |
| `currentChannel` | text | NOT NULL | `email` | |
| `touchCount` | integer | NOT NULL | `0` | |
| `lastTouchAt` | timestamp(3) | YES | | |
| `nextTouchAt` | timestamp(3) | YES | | |
| `emailAttempts` | integer | NOT NULL | `0` | |
| `emailOpens` | integer | NOT NULL | `0` | |
| `emailReplies` | integer | NOT NULL | `0` | |
| `linkedinAttempts` | integer | NOT NULL | `0` | |
| `callAttempts` | integer | NOT NULL | `0` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### OutreachSuggestion
**Purpose**: AI-generated outreach suggestions for deals.
**Row count**: 6

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | NOT NULL | | FK to Deal |
| `channel` | text | NOT NULL | | Channel (e.g., email) |
| `priority` | text | NOT NULL | | Priority level |
| `suggestedFor` | timestamp(3) | NOT NULL | | Suggested send date |
| `subject` | text | YES | | Suggested subject |
| `body` | text | YES | | Suggested body |
| `reasoning` | text | NOT NULL | | Why this outreach |
| `contextUsed` | jsonb | YES | | Context data used |
| `status` | text | NOT NULL | `pending` | |
| `finalSubject` | text | YES | | Final subject (after edits) |
| `finalBody` | text | YES | | Final body |
| `sentAt` | timestamp(3) | YES | | |
| `wasOpened` | boolean | YES | | |
| `gotReply` | boolean | YES | | |
| `replyPositive` | boolean | YES | | |
| `recipientTimezone` | text | YES | | |
| `scheduledFor` | timestamp(3) | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### RefinementLog
**Purpose**: Logs of AI email refinement (editing drafts based on instructions).
**Row count**: 2

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | YES | | |
| `suggestionId` | text | YES | | |
| `instructions` | text | NOT NULL | | Refinement instructions |
| `originalSubject` | text | NOT NULL | | |
| `originalBody` | text | NOT NULL | | |
| `refinedSubject` | text | NOT NULL | | |
| `refinedBody` | text | NOT NULL | | |
| `success` | boolean | NOT NULL | `true` | |
| `error` | text | YES | | |
| `durationMs` | integer | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

---

### VoiceProfile
**Purpose**: Email writing voice/style profile (learned from user's emails).
**Row count**: 1

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `userId` | text | NOT NULL | | FK-like to User (unique) |
| `greetingPatterns` | text[] | YES | `ARRAY[]::text[]` | |
| `closingPatterns` | text[] | YES | `ARRAY[]::text[]` | |
| `ctaPatterns` | text[] | YES | `ARRAY[]::text[]` | CTA patterns |
| `signaturePhrases` | text[] | YES | `ARRAY[]::text[]` | |
| `avgSentenceLength` | double precision | NOT NULL | `0` | |
| `avgParagraphCount` | double precision | NOT NULL | `0` | |
| `avgEmailLength` | double precision | NOT NULL | `0` | |
| `formalityScore` | double precision | NOT NULL | `0.5` | |
| `exampleOpeners` | jsonb | YES | | |
| `exampleFollowUps` | jsonb | YES | | |
| `exampleClosings` | jsonb | YES | | |
| `emailsAnalyzed` | integer | NOT NULL | `0` | |
| `lastAnalyzedAt` | timestamp(3) | YES | | |
| `analysisVersion` | integer | NOT NULL | `1` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

## 6. Implementation / Customer Success Tables

### Implementation
**Purpose**: Customer implementation projects (post-sale onboarding).
**Row count**: 19

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `customerName` | text | NOT NULL | | Customer name |
| `primaryContact` | text | YES | | Primary contact name |
| `primaryEmail` | text | YES | | Primary contact email |
| `stage` | ImplementationStage | NOT NULL | `KICKOFF` | `ACTIVE` (4), `LIVE` (4), `SCOPING` (4), `TESTING` (3), `CONFIGURATION` (2), `KICKOFF` (2) |
| `healthStatus` | HealthStatus | NOT NULL | `ON_TRACK` | `ON_TRACK` (18), `AT_RISK` (1) |
| `startedAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `targetLaunchDate` | timestamp(3) | YES | | |
| `launchedAt` | timestamp(3) | YES | | |
| `hasVoiceAgent` | boolean | NOT NULL | `false` | Whether implementation includes voice |
| `hasChatAgent` | boolean | NOT NULL | `false` | Whether implementation includes chat |
| `hasEmailAgent` | boolean | NOT NULL | `false` | Whether implementation includes email |
| `amsType` | text | YES | | AMS system type |
| `crmType` | text | YES | | CRM type |
| `integrationNotes` | text | YES | | |
| `implementationLead` | text | YES | | Lead person |
| `teamMembers` | text[] | YES | | Team member names |
| `risks` | jsonb | YES | | Identified risks |
| `blockers` | text[] | YES | | Active blockers |
| `notes` | text | YES | | |
| `lastUpdateSummary` | text | YES | | |
| `companyId` | text | YES | | FK to Company (unique) |
| `actualDaysToLaunch` | integer | YES | | |
| `targetDaysToLaunch` | integer | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Referenced by**: `ImplementationMilestone`, `ImplementationStageHistory`, `ImplementationTask`, `VoiceImplementation`.

---

### ImplementationMilestone
**Purpose**: Milestones within an implementation project.
**Row count**: 228 (71 completed)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `name` | text | NOT NULL | | Milestone name |
| `description` | text | YES | | |
| `stage` | ImplementationStage | NOT NULL | | Stage this milestone belongs to |
| `isCompleted` | boolean | NOT NULL | `false` | |
| `completedAt` | timestamp(3) | YES | | |
| `dueDate` | timestamp(3) | YES | | |
| `implementationId` | text | NOT NULL | | FK to Implementation |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### ImplementationStageHistory
**Purpose**: Tracks stage transitions for implementations.
**Row count**: 17

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `implementationId` | text | NOT NULL | | FK to Implementation |
| `fromStage` | ImplementationStage | YES | | Previous stage |
| `toStage` | ImplementationStage | NOT NULL | | New stage |
| `changedAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `changedBy` | text | YES | | Who changed it |
| `daysInPreviousStage` | integer | YES | | Days spent in previous stage |

---

### ImplementationTask
**Purpose**: Tasks within an implementation project.
**Row count**: 35

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `implementationId` | text | NOT NULL | | FK to Implementation |
| `title` | text | NOT NULL | | Task title |
| `description` | text | YES | | |
| `owner` | text | YES | | Person responsible |
| `ownerType` | text | NOT NULL | `internal` | All `internal` |
| `dueDate` | timestamp(3) | YES | | |
| `completedAt` | timestamp(3) | YES | | |
| `status` | text | NOT NULL | `pending` | All `pending` |
| `category` | text | YES | | (None populated) |
| `priority` | text | NOT NULL | `medium` | |
| `source` | text | NOT NULL | `manual` | All `meeting` |
| `sourceMeetingId` | text | YES | | Meeting that generated this task |
| `sourceContext` | text | YES | | Context from source |
| `sourcePlaybookId` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### VoiceImplementation
**Purpose**: Voice agent implementation details within a broader implementation.
**Row count**: 6

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `implementationId` | text | NOT NULL | | FK to Implementation (unique) |
| `useCases` | text[] | YES | `ARRAY[]::text[]` | e.g., `{intake,quotes}`, `{billing,service}` |
| `phoneNumbers` | text[] | YES | `ARRAY[]::text[]` | Assigned phone numbers |
| `agentPersona` | text | YES | | |
| `customNotes` | text | YES | | |
| `configuredAt` | timestamp(3) | YES | | |
| `liveAt` | timestamp(3) | YES | | |
| `totalCallsHandled` | integer | NOT NULL | `0` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### Playbook
**Purpose**: Implementation playbooks (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `name` | text | NOT NULL | | |
| `description` | text | YES | | |
| `agentType` | text | YES | | |
| `stage` | ImplementationStage | YES | | |
| `isDefault` | boolean | NOT NULL | `false` | |
| `isActive` | boolean | NOT NULL | `true` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Referenced by**: `PlaybookTask`.

---

### PlaybookTask
**Purpose**: Tasks within a playbook template (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | |
| `playbookId` | text | NOT NULL | | FK to Playbook |
| `title` | text | NOT NULL | | |
| `description` | text | YES | | |
| `category` | text | YES | | |
| `priority` | text | NOT NULL | `medium` | |
| `ownerType` | text | NOT NULL | `internal` | |
| `dayOffset` | integer | NOT NULL | `0` | |
| `reference` | text | NOT NULL | `start` | |
| `sortOrder` | integer | NOT NULL | `0` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

## 7. Investor Relations Tables

### InvestorFirm
**Purpose**: Investor firms being tracked for fundraising.
**Row count**: 212

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `name` | text | NOT NULL | | Firm name |
| `type` | InvestorType | NOT NULL | `VC` | `VC` (166), `ANGEL` (32), `CVC` (14) |
| `website` | text | YES | | |
| `location` | text | YES | | |
| `tier` | InvestorTier | NOT NULL | `C` | `D` (85), `A` (49), `C` (41), `B` (37) |
| `status` | InvestorStatus | NOT NULL | `RESEARCH` | `RESEARCH` (37), `INVESTED` (36), `CONTACTED` (25), `DECLINED` (25), `TARGET` (21), `COLD` (18), etc. |
| `investorTags` | text[] | YES | `ARRAY[]::text[]` | |
| `stagePreference` | text | YES | | Investment stage preference |
| `checkSizeMin` | integer | YES | | Minimum check size |
| `checkSizeMax` | integer | YES | | Maximum check size |
| `leadOrSupport` | text | YES | | Lead or support investor |
| `introPerson` | text | YES | | Person who can intro |
| `relationshipLevel` | text | YES | | |
| `priorityRating` | text | YES | | |
| `brianRating` | integer | YES | | Internal rating |
| `compositeScore` | double precision | YES | | Composite score (max 200) |
| `fitScore` | integer | YES | | |
| `relationshipScore` | integer | YES | | |
| `urgencyScore` | integer | YES | | |
| `notes` | text | YES | | |
| `whyGoodFit` | text | YES | | |
| `whyNotFit` | text | YES | | |
| `airtableId` | text | YES | | Legacy Airtable ID (unique) |
| `airtableFirmId` | text | YES | | |
| `lastContactedAt` | timestamp(3) | YES | | |
| `lastInteractionAt` | timestamp(3) | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Indexes**: PK on `id`, UNIQUE on `airtableId`. Indexes on `type`, `tier`, `status`, `compositeScore`.
**Referenced by**: `InvestorContact`, `InvestorInteraction`.

---

### InvestorContact
**Purpose**: Contacts at investor firms.
**Row count**: 94

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `firmId` | text | NOT NULL | | FK to InvestorFirm |
| `name` | text | NOT NULL | | |
| `email` | text | YES | | |
| `linkedinUrl` | text | YES | | |
| `phone` | text | YES | | |
| `title` | text | YES | | |
| `isPrimary` | boolean | NOT NULL | `false` | |
| `isDecisionMaker` | boolean | NOT NULL | `false` | |
| `notes` | text | YES | | |
| `relationship` | text | YES | | |
| `airtableId` | text | YES | | (unique) |
| `lastContactedAt` | timestamp(3) | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### InvestorInteraction
**Purpose**: Interactions with investor firms (all outbound email).
**Row count**: 130

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `firmId` | text | NOT NULL | | FK to InvestorFirm |
| `contactId` | text | YES | | FK to InvestorContact |
| `type` | text | NOT NULL | | All `email` |
| `direction` | text | NOT NULL | `outbound` | All `outbound` |
| `occurredAt` | timestamp(3) | NOT NULL | | |
| `subject` | text | YES | | |
| `notes` | text | YES | | |
| `outcome` | text | YES | | |
| `nextStep` | text | YES | | |
| `nextStepDueAt` | timestamp(3) | YES | | |
| `airtableId` | text | YES | | (unique) |
| `emailId` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

## 8. Slack Integration Tables

### SlackChannel
**Purpose**: Monitored Slack channels.
**Row count**: 28

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key (Slack channel ID like `C04K591D29Y`) |
| `name` | text | NOT NULL | | Channel name |
| `category` | text | NOT NULL | | `product` (10), `customer` (7), `operations` (6), `alerts` (5) |
| `companyId` | text | YES | | FK to Company (for customer channels) |
| `isActive` | boolean | NOT NULL | `true` | |
| `lastScannedAt` | timestamp(3) | YES | | |
| `scanFrequency` | text | NOT NULL | `4h` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### SlackExtraction
**Purpose**: Intelligence extracted from Slack messages.
**Row count**: 7

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `channelId` | text | NOT NULL | | FK to SlackChannel |
| `channelName` | text | NOT NULL | | |
| `messageTs` | text | NOT NULL | | Slack message timestamp (unique) |
| `messageUrl` | text | NOT NULL | | |
| `authorId` | text | NOT NULL | | Slack user ID |
| `authorName` | text | NOT NULL | | |
| `messageText` | text | NOT NULL | | |
| `extractionType` | text | NOT NULL | | All `customer` |
| `signalType` | text | NOT NULL | | `win` (3), `request` (3), `blocker` (1) |
| `confidence` | double precision | NOT NULL | | |
| `extractedData` | jsonb | YES | | |
| `companyId` | text | YES | | FK to Company |
| `dealId` | text | YES | | FK to Deal |
| `contactId` | text | YES | | FK to Contact |
| `processed` | boolean | NOT NULL | `false` | |
| `processedAt` | timestamp(3) | YES | | |
| `activityId` | text | YES | | |
| `linearId` | text | YES | | Linear issue ID |
| `reviewed` | boolean | NOT NULL | `false` | |
| `reviewedAt` | timestamp(3) | YES | | |
| `reviewedBy` | text | YES | | |
| `wasAccurate` | boolean | YES | | |
| `correctedCompanyId` | text | YES | | |
| `correctedDealId` | text | YES | | |
| `matchConfidence` | double precision | YES | | |
| `matchMethod` | text | YES | | |
| `reviewNotes` | text | YES | | |
| `status` | text | NOT NULL | `pending` | `pending` (5), `approved` (2) |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

---

### TeamUpdate
**Purpose**: Team updates from Slack (CDD reports and status updates).
**Row count**: 80

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `companyId` | text | YES | | FK to Company |
| `customerName` | text | NOT NULL | | |
| `canonicalName` | text | YES | | Normalized company name |
| `source` | text | NOT NULL | `slack` | All `slack` |
| `slackMessageId` | text | YES | | |
| `slackChannel` | text | YES | | |
| `slackMessageUrl` | text | YES | | |
| `postedBy` | text | YES | | Person who posted |
| `postedAt` | timestamp(3) | NOT NULL | | |
| `updateType` | text | NOT NULL | `cdd` | `cdd` (57), `status` (23) |
| `updates` | jsonb | NOT NULL | | Structured update data |
| `todos` | jsonb | NOT NULL | | Todo items from update |
| `rawText` | text | YES | | Raw message text |
| `processed` | boolean | NOT NULL | `false` | |
| `processedAt` | timestamp(3) | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

## 9. Data Quality & Matching Tables

### DuplicateGroup
**Purpose**: Groups of potentially duplicate company records.
**Row count**: 65

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `status` | text | NOT NULL | `pending` | `merged` (42), `pending` (23) |
| `matchScore` | double precision | NOT NULL | | Score 0.85-1.0 (avg 0.956) |
| `matchReason` | text | NOT NULL | | Reason for match |
| `reviewedAt` | timestamp(3) | YES | | |
| `reviewNotes` | text | YES | | |
| `mergedIntoId` | text | YES | | ID of surviving record |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### DuplicateGroupMember
**Purpose**: Members within a duplicate group.
**Row count**: 146

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `groupId` | text | NOT NULL | | FK to DuplicateGroup |
| `companyId` | text | NOT NULL | | Company ID |
| `companyName` | text | NOT NULL | | |
| `normalizedName` | text | NOT NULL | | Normalized for matching |
| `isPrimary` | boolean | NOT NULL | `false` | Whether this is the primary/surviving record |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Indexes**: UNIQUE on `(groupId, companyId)`.

---

### CompanyAlias
**Purpose**: Alternative names for companies (for matching).
**Row count**: 10

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `alias` | text | NOT NULL | | Alternative name (unique) |
| `canonicalName` | text | NOT NULL | | Canonical company name |
| `companyId` | text | YES | | FK to Company |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

---

### CompanyMerge
**Purpose**: Log of company merge operations (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `sourceCompanyId` | text | NOT NULL | | Merged-from company |
| `sourceCompanyName` | text | NOT NULL | | |
| `targetCompanyId` | text | NOT NULL | | Merged-into company |
| `targetCompanyName` | text | NOT NULL | | |
| `mergedData` | jsonb | YES | | What was merged |
| `duplicateGroupId` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

---

### CompanyRelationship
**Purpose**: Parent-subsidiary relationships (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `parentId` | text | NOT NULL | | Parent company |
| `parentName` | text | NOT NULL | | |
| `subsidiaryId` | text | NOT NULL | | Subsidiary company |
| `subsidiaryName` | text | NOT NULL | | |
| `relationType` | text | NOT NULL | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

**Indexes**: UNIQUE on `(parentId, subsidiaryId)`.

---

### LearnedMatch
**Purpose**: Cached company name matching patterns (for fuzzy matching).
**Row count**: 71

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `inputPattern` | text | NOT NULL | | The input text pattern (e.g., `alchemy`, `bonza`) |
| `inputType` | text | NOT NULL | `company_name` | All `company_name` |
| `matchedId` | text | NOT NULL | | Matched company ID |
| `matchedName` | text | NOT NULL | | Matched company name |
| `confidence` | double precision | NOT NULL | `1.0` | Match confidence |
| `useCount` | integer | NOT NULL | `1` | Times used |
| `lastUsedAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Indexes**: UNIQUE on `(inputPattern, inputType)`.

---

### StagedRecord
**Purpose**: Staging area for incoming records (e.g., call recordings) before matching to companies.
**Row count**: 4

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `recordType` | text | NOT NULL | | All `call` |
| `status` | text | NOT NULL | `pending` | `created` (3), `matched` (1) |
| `rawData` | jsonb | NOT NULL | | Raw incoming data |
| `companyName` | text | YES | | Extracted company name |
| `companyDomain` | text | YES | | Extracted domain |
| `contactEmail` | text | YES | | Extracted contact email |
| `contactName` | text | YES | | Extracted contact name |
| `matchedCompanyId` | text | YES | | Matched company |
| `matchedDealId` | text | YES | | Matched deal |
| `matchedContactId` | text | YES | | Matched contact |
| `matchConfidence` | double precision | YES | | |
| `matchReasoning` | text | YES | | |
| `createdCompanyId` | text | YES | | Newly created company (if no match) |
| `createdDealId` | text | YES | | Newly created deal |
| `createdContactId` | text | YES | | Newly created contact |
| `createdCallId` | text | YES | | Created call recording |
| `reviewedBy` | text | YES | | |
| `reviewedAt` | timestamp(3) | YES | | |
| `reviewNotes` | text | YES | | |
| `wasCorrect` | boolean | YES | | |
| `errorMessage` | text | YES | | |
| `processedAt` | timestamp(3) | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Referenced by**: `MatchLog.stagedRecordId`.

---

### MatchLog
**Purpose**: Logs of AI matching decisions (for auditing and learning).
**Row count**: 4

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `stagedRecordId` | text | NOT NULL | | FK to StagedRecord |
| `matchType` | text | NOT NULL | | All `company` |
| `searchQuery` | text | NOT NULL | | What was searched |
| `candidatesFound` | integer | NOT NULL | | Number of candidates |
| `candidates` | jsonb | NOT NULL | | Candidate records |
| `decision` | text | NOT NULL | | `created` (3), `matched` (1) |
| `selectedId` | text | YES | | Selected match ID |
| `confidence` | double precision | NOT NULL | | |
| `reasoning` | text | NOT NULL | | AI reasoning |
| `modelUsed` | text | NOT NULL | | LLM model used |
| `promptTokens` | integer | YES | | |
| `responseTokens` | integer | YES | | |
| `wasCorrect` | boolean | YES | | Human feedback |
| `correctId` | text | YES | | Correct ID if wrong |
| `feedbackNotes` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |

---

### DataAssociation
**Purpose**: Association attempts between data sources and companies (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `associationType` | text | NOT NULL | | |
| `sourceId` | text | NOT NULL | | |
| `sourceData` | jsonb | YES | | |
| `targetCompanyId` | text | YES | | |
| `confidence` | double precision | NOT NULL | | |
| `matchSignals` | jsonb | NOT NULL | | |
| `reasoning` | text | NOT NULL | | |
| `status` | text | NOT NULL | `pending` | |
| `wasCorrect` | boolean | YES | | |
| `correctedCompanyId` | text | YES | | |
| `correctedCompanyName` | text | YES | | |
| `reviewedAt` | timestamp(3) | YES | | |
| `reviewedBy` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

## 10. AI & Scoring Tables

### AIScoringResult
**Purpose**: AI-generated deal scoring (composite scores and ARR estimates).
**Row count**: 1,001

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `dealId` | text | NOT NULL | | FK to Deal |
| `suggestedARR` | double precision | YES | | AI-suggested ARR ($24K-$70K range, avg $34.4K) |
| `suggestedScores` | jsonb | NOT NULL | | Breakdown scores |
| `compositeScore` | double precision | YES | | 1.4-3.9 range, avg 2.12 |
| `confidence` | text | NOT NULL | `medium` | `low` (997), `medium` (4) |
| `signalStrength` | double precision | YES | | |
| `signalsUsed` | jsonb | NOT NULL | | Signals that fed scoring |
| `explanation` | text | NOT NULL | | AI explanation text |
| `arrReasoning` | text | YES | | ARR estimate reasoning |
| `scoreReasons` | jsonb | YES | | Breakdown of score reasons |
| `status` | text | NOT NULL | `pending` | `approved` (708), `pending` (292), `rejected` (1) |
| `humanARR` | double precision | YES | | Human-overridden ARR |
| `humanScores` | jsonb | YES | | Human-overridden scores |
| `reviewedAt` | timestamp(3) | YES | | |
| `reviewedBy` | text | YES | | |
| `reviewNotes` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Indexes**: PK on `id`. Indexes on `dealId`, `status`, `confidence`, `createdAt`.
**FK**: `dealId` -> `Deal(id)` CASCADE DELETE.

---

## 11. System / Workflow Tables

### SystemHealth
**Purpose**: Health status of background sync jobs.
**Row count**: 5

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `syncType` | text | NOT NULL | | Unique: `slack_scan`, `daily_close`, `daily_sync`, `daily_intelligence`, `morning_brief` |
| `status` | text | NOT NULL | `unknown` | All currently `success` |
| `lastRunAt` | timestamp(3) | YES | | Last execution time |
| `lastSuccessAt` | timestamp(3) | YES | | Last successful execution |
| `durationMs` | integer | YES | | Execution duration |
| `metadata` | jsonb | YES | | Run metadata (counts, results) |
| `errorMessage` | text | YES | | |
| `consecutiveFails` | integer | NOT NULL | `0` | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Sync types**:
- `slack_scan`: Scans Slack channels for signals
- `daily_close`: End-of-day pipeline snapshot
- `daily_sync`: Full daily sync (email, deals, signals)
- `daily_intelligence`: Generates daily intelligence report
- `morning_brief`: Morning briefing for leadership

---

### Conversation
**Purpose**: AI assistant conversations (likely the chat UI for the CRM).
**Row count**: 32

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `messages` | jsonb | NOT NULL | | Array of messages |
| `totalMessages` | integer | NOT NULL | `0` | Avg 2.09, max 5 |
| `hasEmailDraft` | boolean | NOT NULL | `false` | 9 have drafts |
| `emailsSent` | integer | NOT NULL | `0` | |
| `toolsUsed` | text[] | YES | | |
| `status` | text | NOT NULL | `pending` | All `pending` |
| `rating` | integer | YES | | |
| `reviewNotes` | text | YES | | |
| `reviewedAt` | timestamp(3) | YES | | |
| `hasError` | boolean | NOT NULL | `false` | |
| `errorMessage` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### Feedback
**Purpose**: User feedback on the system.
**Row count**: 5

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `type` | text | NOT NULL | | `opportunity` (3), `general` (1), `bug` (1) |
| `title` | text | NOT NULL | | |
| `description` | text | NOT NULL | | |
| `pagePath` | text | YES | | Page where feedback was given |
| `status` | text | NOT NULL | `open` | `open` (3), `resolved` (2) |
| `priority` | text | YES | | |
| `resolution` | text | YES | | |
| `category` | text | YES | | |
| `entityId` | text | YES | | |
| `entityType` | text | YES | | |
| `customerName` | text | YES | | |
| `opportunityId` | text | YES | | |
| `signalType` | text | YES | | |
| `sourceId` | text | YES | | |
| `sourceType` | text | YES | | |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

---

### CallRecording
**Purpose**: Call recordings linked to companies/contacts/deals.
**Row count**: 5

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `source` | text | NOT NULL | | `manual`, `test`, `conference` |
| `externalId` | text | YES | | External ID (unique) |
| `title` | text | YES | | |
| `recordingUrl` | text | YES | | |
| `audioFilePath` | text | YES | | |
| `duration` | integer | YES | | Duration in seconds |
| `recordedAt` | timestamp(3) | NOT NULL | | |
| `transcriptText` | text | YES | | |
| `transcriptStatus` | text | NOT NULL | `pending` | `pending` (1), `completed` (4) |
| `aiAnalysis` | jsonb | YES | | |
| `summary` | text | YES | | |
| `keyPoints` | text[] | YES | | |
| `objections` | text[] | YES | | |
| `commitments` | text[] | YES | | |
| `sentiment` | text | YES | | `positive` (1) |
| `dealTemperature` | text | YES | | |
| `suggestedNextAction` | text | YES | | |
| `companyId` | text | YES | | FK to Company |
| `contactId` | text | YES | | FK to Contact |
| `dealId` | text | YES | | FK to Deal |
| `createdAt` | timestamp(3) | NOT NULL | CURRENT_TIMESTAMP | |
| `updatedAt` | timestamp(3) | NOT NULL | | |

**Referenced by**: `CallParticipant.callId`.

---

### CallParticipant
**Purpose**: Participants in call recordings (empty table).
**Row count**: 0

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | text | NOT NULL | | Primary key |
| `name` | text | NOT NULL | | |
| `email` | text | YES | | |
| `isInternal` | boolean | NOT NULL | `false` | |
| `callId` | text | NOT NULL | | FK to CallRecording |

---

## Useful Query Patterns

### Get all extractions for a company
```sql
SELECT me.* FROM "MeetingExtraction" me
JOIN "Meeting" m ON me."meetingId" = m.id
WHERE m."companyId" = '<company_id>'
ORDER BY m.date DESC;
```

### Get signals for active deals
```sql
SELECT s.*, d.status as "dealStatus", c.name as "companyName"
FROM "Signal" s
JOIN "Meeting" m ON s."meetingId" = m.id
JOIN "Company" co ON s."companyId" = co.id
JOIN "Deal" d ON d."companyId" = co.id
WHERE d.status NOT IN ('WON', 'LOST')
ORDER BY m.date DESC;
```

### Get meeting with utterances and participants
```sql
SELECT m.title, m.date, mp.name, mp."isInternal",
  mu.text, mu."startMs"
FROM "Meeting" m
JOIN "MeetingParticipant" mp ON mp."meetingId" = m.id
LEFT JOIN "MeetingUtterance" mu ON mu."meetingId" = m.id
WHERE m.id = '<meeting_id>'
ORDER BY mu."startMs";
```

### Pipeline summary
```sql
SELECT d.status::text, count(*), sum(d."expectedARR") as total_arr
FROM "Deal" d
GROUP BY d.status
ORDER BY d.status;
```

### Recent customer quotes suitable for case studies
```sql
SELECT q.text, q."speakerName", q.sentiment, c.name as "companyName", m.date
FROM "Quote" q
JOIN "Meeting" m ON q."meetingId" = m.id
LEFT JOIN "Company" c ON q."companyId" = c.id
WHERE q."usableFor" = 'case_study' AND q.sentiment = 'positive'
ORDER BY m.date DESC
LIMIT 20;
```
