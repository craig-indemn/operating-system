---
ask: "Design the document generation MVP for Silent Sports — architecture, components, demo flow, UI"
created: 2026-03-16
workstream: silent-sports
session: 2026-03-16-a
sources:
  - type: google-doc
    ref: "https://docs.google.com/document/d/1LTZ1Lw3lO_8wPWWAEMR_fJ3HvKKql0OXv-NUJYTh6pg/edit"
    name: "Silent Sports — Internal Team Review"
  - type: slack
    description: "Kyle's message in #customer-implementation + thread history"
  - type: conversation
    description: "Brainstorming + 3-way parallel review + research — Craig + Claude, 2026-03-16"
  - type: web
    description: "ACORD 25 form research — field inventory, AcroForm vs XFA validation, pdf-lib proof of concept"
---

# Mint — Document Generation Engine

## Overview

Mint is a standalone, reusable PDF generation engine. It takes structured data and a template name, and produces a PDF. Silent Sports is the first customer, but Mint is designed to serve any customer needing document generation (INSURICA COIs, Union General decline letters, etc.).

The Silent Sports demo pairs Mint with a submissions system and deep agent to show the full workflow: email → extraction → review → document generation.

**Name:** Mint ("mint a certificate")
**Repo:** `craig-indemn/silent-sports-doc-gen`
**Status:** Design complete — ready for implementation planning

## Problem Statement

Silent Sports (McKay Insurance) processes 80-90 applications per month at peak (October), each taking Meg ~15 minutes. The bottleneck is manual data entry and document generation — ACORD 25 certificates, premium disclosures, and member certificates. Scott bypasses AMS360 entirely with a PDF editor (3-4 minutes) because the AMS workflow is too slow. Certificate generation was the #1 hook from the Jan 28 demo — both Scott and Meg brought it up unprompted.

## MVP Demo Scope

**Two document types:**
1. **ACORD 25 Certificate** — industry-standard insurance form, AcroForm fillable PDF
2. **Premium Disclosure** — custom page showing calculated premium breakdown

**Demo flow:**
1. Mock email arrives in inbox (presenter-triggered, not timer-based)
2. Deep agent extracts and validates fields from the submission
3. Review UI shows extracted data — Meg reviews, edits if needed, approves
4. Two PDFs generate instantly — ACORD 25 + Premium Disclosure
5. Documents available for download/preview with processing timeline
6. Also demonstrate full-auto mode (no human review step)

---

## Architecture

### Three Components

**Mint CLI (reusable, any customer)**
Pure PDF generation. Takes fields, produces PDF. Knows nothing about submissions, emails, or workflows.

**Submissions System + CLI (workflow orchestration)**
Manages the Silent Sports submission lifecycle — email ingestion, extraction, review state, document tracking, generation triggering. The agent uses the CLI; the UI uses the REST API.

**Review UI**
Reads from and writes to the submissions system via REST API. Shows inbox, field review, document preview.

### System Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                     Submissions System                            │
│                     (REST API + SQLite)                            │
│                                                                    │
│  CLI: subs ingest | subs get | subs update | subs approve         │
│  API: GET/PATCH /submissions, POST /submissions/:id/approve       │
│  SSE: GET /submissions/stream (real-time updates)                 │
└────────┬──────────────────┬──────────────────┬───────────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────┐  ┌──────────────┐  ┌─────────────────┐
│   Deep Agent     │  │   Review UI   │  │   Mint CLI       │
│   (LangGraph +   │  │   (React +    │  │   (reusable)     │
│    Skills)       │  │    shadcn)    │  │                   │
│                  │  │              │  │ mint generate      │
│ Uses both CLIs:  │  │ Reads/writes │  │ mint validate      │
│ - subs (workflow)│  │ via REST API │  │ mint templates     │
│ - mint (validate)│  │              │  │ mint inspect        │
└─────────────────┘  └──────────────┘  │                   │
                                        │ ┌───────────────┐ │
                                        │ │ Templates     │ │
                                        │ │ - accord-25   │ │
                                        │ │ - premium-disc│ │
                                        │ └───────────────┘ │
                                        │         │         │
                                        │         ▼         │
                                        │    ┌─────────┐   │
                                        │    │   S3    │   │
                                        │    │  Bucket │   │
                                        │    └─────────┘   │
                                        └───────────────────┘
```

### Agent Workflow (CLI-first)

The agent handles extraction and validation only. Generation is triggered by the subs API on approval.

```bash
# 1. Ingest a new submission from email
subs ingest --source email --id <msg-id>

# 2. Get raw submission data
raw=$(subs get SS-001 --format json)

# 3. Agent extracts fields, updates the submission
subs update SS-001 --fields-file /tmp/SS-001-extracted.json

# 4. Validate fields against template schemas
mint validate accord-25 --fields-file /tmp/SS-001-fields.json
mint validate premium-disclosure --fields-file /tmp/SS-001-fields.json

# 5. If valid, mark as ready for review (or auto-approve kicks in)
subs update SS-001 --status review

# Generation happens server-side when UI calls POST /submissions/:id/approve
# or automatically if auto-approve is on (subs API detects this on field update)
```

### Communication Architecture

**All components talk through the submissions system.** No direct agent↔UI communication needed.

- **Agent** reads/writes submissions via the `subs` CLI
- **UI** reads/writes submissions via REST API (same data)
- **Real-time updates** via SSE: `GET /submissions/stream` — the UI subscribes and receives events when submission state changes
- **Mint** is stateless — called by the subs API on approval (never by the agent directly)

**State persistence:** SQLite (single file, zero setup). One `submissions` table.

**The agent is not a long-running process.** It runs extraction and validation, writes results to the submissions system, and exits. Generation is triggered by the subs API — either when the UI calls `/approve` (manual mode) or automatically when the agent writes fields and auto-approve is enabled.

---

## Submission Data Model

The core entity that flows through the entire system:

```typescript
interface Submission {
  id: string;                    // e.g., "SS-001"
  status: "received" | "extracting" | "review" | "approved" | "generating" | "complete" | "error";

  // Source email
  email: {
    from: string;
    to: string;
    subject: string;
    date: string;
    body: string;
    attachments: Array<{
      filename: string;
      mimeType: string;
      url: string;
    }>;
  };

  // Extracted fields — keyed by semantic field name
  fields: Record<string, {
    value: string | number | boolean;
    confidence: "high" | "medium" | "low";
    source: "email_body" | "attachment" | "rate_table" | "calculated" | "default" | "manual";
    edited: boolean;
    required: boolean;
    validationError?: string;
  }>;

  // Rate calculation results
  premium?: {
    glPremium: number;
    surplusLinesTax: number;
    surplusLinesTaxRate: number;   // State-specific (e.g., 0.03 for MT)
    accidentPremium: number;
    policyFee: number;
    total: number;
    rateClass: string;             // e.g., "mountain-bike-race"
    state: string;                 // For state-specific tax rates
  };

  // Generated documents
  documents: Array<{
    template: string;              // "accord-25" | "premium-disclosure"
    status: "pending" | "generating" | "complete" | "error";
    url?: string;                  // S3 signed URL
    generatedAt?: string;
    error?: string;
  }>;

  // Timeline — real measured durations
  timeline: Array<{
    event: string;
    timestamp: string;
    durationMs?: number;
  }>;

  // Auto-generated certificate number (assigned at approval time, incrementing, persisted in SQLite)
  certificateNumber?: string;       // e.g., "SS-2026-0001" — assigned by subs API when status transitions to "approved"

  createdAt: string;
  updatedAt: string;
}
```

**Design choices:**
- Per-field metadata (confidence, source, edited) powers UI indicators and tracks what Meg changed
- `source` distinguishes extracted vs calculated vs default — UI shows calculator icon for computed fields
- Premium as a coherent block that recalculates together when any component changes
- Documents as an array with independent status — handles partial success
- Timeline uses actual measured durations, not hardcoded numbers

---

## Mint CLI (Reusable)

### Commands

```bash
# Generate a document — primary command
mint generate <template> --fields-file <path.json> [--output s3|local]
mint generate <template> --fields '<json>' [--output s3|local]

# List available templates
mint templates

# Show required/optional fields for a template
mint inspect <template>

# Validate fields without generating
mint validate <template> --fields-file <path.json>
mint validate <template> --fields '<json>'
```

**`--fields-file` is the preferred interface** for the agent. Avoids shell escaping issues with JSON-in-arguments. The agent writes a temp JSON file and passes the path.

`--fields` (inline JSON) is available for quick manual testing.

### Output Behavior

```bash
# Success
$ mint generate accord-25 --fields-file /tmp/fields.json
{"status":"ok","url":"https://s3.amazonaws.com/...","template":"accord-25","generatedAt":"2026-03-16T..."}

# Validation failure
$ mint validate accord-25 --fields-file /tmp/fields.json
{"status":"error","error":"VALIDATION_FAILED","message":"Missing required fields","missingFields":["namedInsured","effectiveDate"]}

# Generation failure
$ mint generate accord-25 --fields-file /tmp/bad-fields.json
{"status":"error","error":"GENERATION_FAILED","message":"Field 'INSURED' exceeds maximum length","template":"accord-25"}
```

**All output is JSON on stdout.** Exit code 0 for success, 1 for errors. The agent parses structured output, not stack traces.

### Template Registry

Each template is a directory containing:

```
templates/
  accord-25/
    template.pdf          # Blank AcroForm fillable PDF
    field-map.json        # Semantic name → PDF field name mapping
    schema.json           # Required/optional fields, types, defaults, validation rules
    generator.ts          # Template-specific generation logic
  premium-disclosure/
    PremiumDisclosure.tsx  # React-PDF component
    schema.json           # Field schema
    generator.ts          # Template-specific generation logic
```

**`field-map.json` for ACORD 25** (maps our semantic names to actual PDF field names):
```json
{
  "date": "Date Top",
  "producer": "PRODUCER",
  "namedInsured": "INSURED",
  "insurerA": "INSURER A",
  "insurerANaic": "Insurer A Coverage",
  "glPolicyNumber": "POLICY NUMBERRow1",
  "effectiveDate": "EACH OCCURRENCE Effective Date",
  "expirationDate": "Each Occurrence Expiration Date",
  "eachOccurrence": "fill_46",
  "generalAggregate": "fill_49",
  "productsCompOpsAgg": "PRODUCTS  COMPOP AGGRow1",
  "personalAdvInjury": "fill_48",
  "damageToRentedPremises": "fill_47",
  "medicalExpense": "fill_50",
  "descriptionOfOperations": "DESCRIPTION OF OPERATIONS  LOCATIONS  VEHICLES  EXCLUSIONS ADDED BY ENDORSEMENT  SPECIAL PROVISIONS",
  "certificateHolder": "Certificat Holder",
  "cancellation": "SHOULD ANY OF THE ABOVE DESCRIBED POLICIES BE CANCELLED BEFORE THE EXPIRATION",
  "authorizedRep": "AUTHORIZED REPRESENTATIVE"
}
```

**`schema.json`** (drives `mint validate` and `mint inspect`):
```json
{
  "template": "accord-25",
  "version": "2016/03",
  "fields": {
    "date": { "type": "date", "required": true, "format": "MM/DD/YYYY" },
    "namedInsured": { "type": "string", "required": true, "note": "Generator concatenates namedInsured + insuredAddress into the INSURED PDF field" },
    "insuredAddress": { "type": "string", "required": true, "note": "Concatenated with namedInsured into the INSURED PDF field" },
    "producer": { "type": "string", "required": true, "default": "McKay Insurance\n2211 Plaza Drive\nRocklin, CA 95765" },
    "insurerA": { "type": "string", "required": true, "default": "Markel Insurance Company" },
    "glPolicyNumber": { "type": "string", "required": true },
    "effectiveDate": { "type": "date", "required": true },
    "expirationDate": { "type": "date", "required": true },
    "eachOccurrence": { "type": "currency", "required": true },
    "generalAggregate": { "type": "currency", "required": true },
    "productsCompOpsAgg": { "type": "currency", "required": true },
    "personalAdvInjury": { "type": "currency", "required": true },
    "damageToRentedPremises": { "type": "currency", "required": false },
    "medicalExpense": { "type": "currency", "required": false },
    "certificateHolder": { "type": "string", "required": false },
    "descriptionOfOperations": { "type": "string", "required": false },
    "additionalInsured": { "type": "boolean", "required": false },
    "waiverOfSubrogation": { "type": "boolean", "required": false }
  },
  "validation": [
    { "rule": "expirationDate > effectiveDate", "message": "Expiration date must be after effective date" }
  ]
}
```

### Mint API (for UI)

The Mint service also runs an Express API for browser access:

```
POST /generate
{
  "template": "accord-25",
  "fields": { ... },
  "output": { "destination": "s3" }
}

Success Response (200):
{
  "status": "ok",
  "url": "https://s3.amazonaws.com/...",
  "template": "accord-25",
  "generatedAt": "2026-03-16T..."
}

Error Response (400):
{
  "status": "error",
  "error": "VALIDATION_FAILED",
  "message": "Missing required field: namedInsured",
  "missingFields": ["namedInsured"]
}

Error Response (500):
{
  "status": "error",
  "error": "GENERATION_FAILED",
  "message": "pdf-lib error: field 'INSURED' not found in template",
  "template": "accord-25"
}

GET /templates
GET /templates/:name (equivalent to mint inspect)
```

---

## Submissions System

### CLI

```bash
# Ingest a new submission
subs ingest --source email --id <msg-id>
subs ingest --source file --path <submission.json>

# List submissions
subs list [--status <status>]

# Get a submission
subs get <id> [--format json|table]

# Update extracted fields (and optionally set status/validation errors)
subs update <id> --fields '<json>'
subs update <id> --fields-file <path.json>
subs update <id> --status <status>
subs update <id> --validation-errors '<json>'

# Approve (triggers generation if auto-gen is on)
subs approve <id>

# Add generated document
subs add-doc <id> --template <name> --url <url>

# Set auto-approve mode
subs config set auto-approve true
```

### REST API (for UI)

```
GET    /submissions                    # List all
GET    /submissions/:id                # Get one
PATCH  /submissions/:id                # Update fields
POST   /submissions/:id/approve        # Approve + trigger generation
POST   /submissions/:id/generate       # Re-generate documents
GET    /submissions/stream             # SSE for real-time updates
POST   /submissions/demo-next           # Trigger next mock submission (keyboard shortcut N calls this)

GET    /config                         # Get settings (auto-approve, etc.)
PATCH  /config                         # Update settings
```

### Approval → Generation Call Chain

When the user clicks "Approve & Generate" in the UI:

1. UI calls `POST /submissions/:id/approve`
2. Subs API updates status to `approved`, adds timeline event
3. Subs API updates status to `generating`
4. Subs API calls Mint HTTP API: `POST http://localhost:3200/generate` for each template (ACORD 25, then Premium Disclosure)
5. For each successful generation, subs API updates the submission's `documents[]` array with the S3 URL
6. If both succeed → status `complete`. If one fails → status `complete` with that document marked `error` (partial success).
7. SSE emits `submission:updated` events at each state transition

For **re-generation** (e.g., after editing fields): UI calls `POST /submissions/:id/generate` which repeats steps 3-7.

The subs server imports no Mint code — it calls Mint's HTTP API as an external service. This keeps them decoupled.

### Rate Recalculation

The **subs API owns rate calculation logic.** When a premium-affecting field is patched via `PATCH /submissions/:id`:

1. Subs API detects which fields changed
2. If any premium-input field changed (event type, participant count, coverage limits), the API recalculates the `premium` block using the rate table
3. Returns the updated submission with recalculated premium values
4. UI renders the new values — no rate logic in the browser

For the demo, rate tables are hardcoded in the subs server (Mountain Bike Race rates). For production, rate tables would be configurable per customer.

### State Machine

```
received → extracting → review → approved → generating → complete
                           ↑                     │
                           └─────── error ◄──────┘
```

Auto-approve mode: `received → extracting → approved → generating → complete` (skips `review`).

**Auto-approve trigger:** When auto-approve is on and the agent calls `subs update` with fields, the subs API detects the config setting and automatically transitions to `approved`, then triggers generation. The agent does not need different code paths — it always calls `subs update` with fields and the system handles the rest.

### SSE Event Schema

`GET /submissions/stream` returns Server-Sent Events. The UI subscribes on load via `EventSource`.

**Event types:**

```
event: submission:created
data: {"id":"SS-001","status":"received","email":{"subject":"..."},"createdAt":"..."}

event: submission:updated
data: {"id":"SS-001","status":"review","fields":{...},"updatedAt":"..."}

event: submission:status
data: {"id":"SS-001","status":"generating","updatedAt":"..."}

event: document:generated
data: {"id":"SS-001","template":"accord-25","url":"https://s3...","generatedAt":"..."}

event: submission:error
data: {"id":"SS-001","error":"GENERATION_FAILED","message":"...","template":"premium-disclosure"}
```

**Payload:** Each event sends the minimal changed data (not the full submission object). The UI merges these into its local state. On initial connection, the server sends `submission:created` events for all existing submissions (snapshot replay).

---

## ACORD 25 — Validated Technical Specification

### PDF Form Technology: CONFIRMED AcroForm

**Critical finding from research:** ACORD 25 PDFs exist in both XFA and AcroForm versions. pdf-lib does NOT support XFA. We have confirmed a working AcroForm version:

- **Source:** Texas Specialty Insurance (`texasspecialty.com`) — ACORD 25 (2016/03) AcroForm
- **Fields:** 96 AcroForm fields (92 TextField, 4+ CheckBox)
- **pdf-lib compatibility:** CONFIRMED — `getForm().getFields()` returns all 96 fields
- **Fill + flatten:** CONFIRMED — proof of concept successfully fills fields and generates valid PDF (321KB output)

**XFA versions (like Allegany Group's) crash pdf-lib.** The template.pdf in the repo MUST be the AcroForm version.

### Complete Field Inventory (96 fields)

Organized by form section with our semantic mapping:

**Header**
| PDF Field Name | Semantic Name | Type | Source |
|---------------|---------------|------|--------|
| `Date Top` | date | Date (MM/DD/YYYY) | Auto-generated |
| `PRODUCER` | producer | Text (multiline) | Static — McKay Insurance |
| `INSURED` | namedInsured | Text (multiline) | Submission (name + address concatenated by generator) |

**Insurers (A-E)**
| PDF Field Name | Semantic Name | Type | Source |
|---------------|---------------|------|--------|
| `INSURER A` | insurerA | Text | Static — Markel Insurance Company |
| `INSURER B` | insurerB | Text | Optional |
| `INSURER C` | insurerC | Text | Optional |
| `INSURER D` | insurerD | Text | Optional |
| `INSURER E` | insurerE | Text | Optional |
| `Insurer A Coverage` | insurerANaic | Text | Static — NAIC number |
| `Insurer B Coverage` | insurerBNaic | Text | Optional |
| `Insurer C Coverage` | insurerCNaic | Text | Optional |
| `Insurer D Coverage` | insurerDNaic | Text | Optional |
| `Insurer E Coverage` | insurerENaic | Text | Optional |

**Commercial General Liability**
| PDF Field Name | Semantic Name | Type | Source |
|---------------|---------------|------|--------|
| `GL CGL` | glCgl | CheckBox | Static — checked |
| `Check Box1`-`Check Box4` | glSubtype | CheckBox | Claims-made vs Occurrence |
| `INSR LTRRow1` | glInsrLetter | Text | "A" |
| `ADDL INSRDRow1` | glAdditionalInsured | Text | Y/N |
| `Row1` | glSubrWaived | Text | Y/N (note: ambiguous PDF name — confirmed via field enumeration at index 10) |
| `POLICY NUMBERRow1` | glPolicyNumber | Text | Submission |
| `EACH OCCURRENCE Effective Date` | effectiveDate | Text | Submission (generic name, mapped to GL section) |
| `Each Occurrence Expiration Date` | expirationDate | Text | Submission (generic name, mapped to GL section) |
| `fill_46` | eachOccurrence | Text | Rate table |
| `fill_47` | damageToRentedPremises | Text | Rate table |
| `fill_48` | personalAdvInjury | Text | Rate table |
| `fill_49` | generalAggregate | Text | Rate table |
| `fill_50` | medicalExpense | Text | Rate table |
| `PRODUCTS  COMPOP AGGRow1` | productsCompOpsAgg | Text | Rate table |
| `COMMERCIAL GENERAL LIABILITY` | glPolicyType | Text | "Occurrence" |
| `POLICY` | glAggregateAppliesPer | Text | "Policy" / "Project" / "Loc" |
| `LOC` | glLoc | Text | Location if applicable |
| `PRO JECT` | glProject | Text | Project if applicable |

**Automobile Liability**
| PDF Field Name | Semantic Name | Type | Source |
|---------------|---------------|------|--------|
| `Auto Liability Any Auto` | autoAnyAuto | CheckBox | |
| `All Owned Autos` | autoAllOwned | CheckBox | |
| `Scheduled Autos` | autoScheduled | CheckBox | |
| `Hired Autos` | autoHired | CheckBox | |
| `Non-Owned Autos` | autoNonOwned | CheckBox | |
| `INSR LTRRow2` | autoInsrLetter | Text | |
| `ADDL INSRDRow2` | autoAdditionalInsured | Text | |
| `POLICY NUMBERRow2` | autoPolicyNumber | Text | |
| `COMBINED SINGLE LIMIT Effective Date` | autoEffectiveDate | Text | |
| `COMBINED SINGLE LIMIT Expiration Date` | autoExpirationDate | Text | |
| `fill_52` | autoCombinedSingleLimit | Text | |
| `BODILY INJURY Per person` | autoBodilyInjuryPerson | Text | |
| `fill_54` | autoBodilyInjuryAccident | Text | |
| `BODILY INJURY Per accident` | autoPropertyDamage | Text | |
| `NONOWNED AUTOS` | autoOtherLimit | Text | |

**Umbrella/Excess Liability**
| PDF Field Name | Semantic Name | Type | Source |
|---------------|---------------|------|--------|
| `Excess Umbrella Occur` | umbrellaOccur | CheckBox | |
| `Excess Umbrella LiabilityDeductible` | umbrellaDeductible | CheckBox | |
| `Excess Umbrella Liability Retention` | umbrellaRetention | CheckBox | |
| `INSR LTRRow3` | umbrellaInsrLetter | Text | |
| `ADDL INSRDRow3` | umbrellaAdditionalInsured | Text | |
| `POLICY NUMBERRow3` | umbrellaPolicyNumber | Text | |
| `POLICY EFFECTIVE DATE MMDDYYRow3` | umbrellaEffectiveDate | Text | |
| `POLICY EXPIRATION DATE MMDDYYRow3` | umbrellaExpirationDate | Text | |
| `fill_58` | umbrellaEachOccurrence | Text | |
| `fill_59` | umbrellaAggregate | Text | |
| `EACH OCCURRENCE_2` | umbrellaOccurrence2 | Text | |

**Workers Compensation**
| PDF Field Name | Semantic Name | Type | Source |
|---------------|---------------|------|--------|
| `INSR LTRRow5` | wcInsrLetter | Text | (PDF labels WC section as Row4 in some fields, Row5 in others — verify against enumeration) |
| `POLICY NUMBER...WORKERS COMP...` | wcPolicyNumber | Text | |
| `POLICY EFFECTIVE DATE...WORKERS COMP...` | wcEffectiveDate | Text | |
| `POLICY EXPIRATION DATE...WORKERS COMP...` | wcExpirationDate | Text | |
| `WC STATU TORY LIMITS` | wcStatutoryLimits | Text | |
| `Row1_2` | wcEachAccident | Text | |
| `fill_63` | wcDiseaseEachEmployee | Text | |
| `EL DISEASE  EA EMPLOYEE` | wcDiseasePolicyLimit | Text | |

**Other / Additional Coverage**
| PDF Field Name | Semantic Name | Type | Source |
|---------------|---------------|------|--------|
| `INSR LTRRow6` | otherInsrLetter | Text | |
| `POLICY NUMBEROTHER` | otherPolicyNumber | Text | |
| `POLICY EFFECTIVE DATE MMDDYYOTHER` | otherEffectiveDate | Text | |
| `POLICY EXPIRATION DATE MMDDYYOTHER` | otherExpirationDate | Text | |

**Description & Certificate Holder**
| PDF Field Name | Semantic Name | Type | Source |
|---------------|---------------|------|--------|
| `DESCRIPTION OF OPERATIONS...` | descriptionOfOperations | Text (multiline) | Submission + static |
| `Certificat Holder` | certificateHolder | Text (multiline) | Submission |
| `SHOULD ANY OF THE ABOVE...` | cancellation | Text (multiline) | Static boilerplate |
| `AUTHORIZED REPRESENTATIVE` | authorizedRep | Text | Static — McKay agent name |

### Fields Relevant to Silent Sports Event Insurance

For a typical Silent Sports submission (mountain bike race, trail run), the active fields are:

**Required from submission:** namedInsured, insuredAddress, eventDates, eventType, eventLocation, certificateHolder
**From rate table:** eachOccurrence, generalAggregate, productsCompOpsAgg, personalAdvInjury, damageToRentedPremises, medicalExpense
**Static/default:** producer (McKay), insurerA (Markel), glCgl (checked), occurrence type, cancellation clause, authorized rep
**Auto-generated:** date, certificate number (in description field)

Most auto, umbrella, and workers comp fields will be left blank for Silent Sports event insurance policies. They exist in the template for future customers who need them.

---

## Premium Disclosure Specification

**Generation method:** React-PDF (custom layout, `renderToBuffer` for server-side)

### Fields

| Field | Type | Source |
|-------|------|--------|
| Named Insured | string | Submission |
| Event Name | string | Submission |
| Event Type | string | Submission (e.g., "Mountain Bike Race") |
| Event Dates | string | Submission |
| Event Location | string | Submission |
| GL Premium | currency | Calculated from rate table |
| Surplus Lines Tax | currency | Calculated (state-specific %) |
| Surplus Lines Tax Rate | percentage | State-specific (e.g., 3% for MT) |
| Accident Insurance Premium | currency | Calculated from rate table |
| Policy Fee | currency | Static per rate table |
| Total Premium | currency | Sum of above |
| Rate Class | string | Derived from event type |
| Certificate Number | string | Auto-generated |
| Effective Date | date | Submission |
| Expiration Date | date | Submission |

### `schema.json` for Premium Disclosure

```json
{
  "template": "premium-disclosure",
  "version": "1.0",
  "fields": {
    "namedInsured": { "type": "string", "required": true },
    "insuredAddress": { "type": "string", "required": true },
    "eventName": { "type": "string", "required": true },
    "eventType": { "type": "string", "required": true, "note": "e.g., Mountain Bike Race, Trail Run" },
    "eventDates": { "type": "string", "required": true },
    "eventLocation": { "type": "string", "required": true },
    "effectiveDate": { "type": "date", "required": true },
    "expirationDate": { "type": "date", "required": true },
    "glPremium": { "type": "currency", "required": true, "source": "rate_table" },
    "surplusLinesTax": { "type": "currency", "required": true, "source": "calculated" },
    "surplusLinesTaxRate": { "type": "percentage", "required": true, "source": "state_config" },
    "accidentPremium": { "type": "currency", "required": true, "source": "rate_table" },
    "policyFee": { "type": "currency", "required": true, "source": "rate_table" },
    "total": { "type": "currency", "required": true, "source": "calculated", "note": "Maps from premium.total in submission" },
    "rateClass": { "type": "string", "required": true, "source": "derived" },
    "certificateNumber": { "type": "string", "required": true, "source": "auto_generated" }
  },
  "validation": [
    { "rule": "total == glPremium + surplusLinesTax + accidentPremium + policyFee", "message": "Total must equal sum of components" }
  ]
}
```

**Note:** Fields like `effectiveDate`, `eventType`, and `namedInsured` appear in both ACORD 25 and Premium Disclosure schemas. The submission stores these once; both generators read from the same submission fields. The ACORD 25 field-map maps generic names (`effectiveDate`) to ACORD-specific PDF field names (`glEffectiveDate` → `EACH OCCURRENCE Effective Date`). The Premium Disclosure component receives the generic names directly as props.

### Layout (React-PDF component)

Single page with Indemn branding:
- Header with Silent Sports / McKay Insurance logo area
- Insured and event details section
- Premium breakdown table (line items with amounts, total row highlighted)
- Rate class and tax rate noted as footnotes
- Disclaimer/legal text at bottom (state-specific if needed)

---

## Deep Agent

### Instantiation

```python
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[shell_tool],              # bash/shell execution for CLIs
    system_prompt=SYSTEM_PROMPT,
    skills=["/skills/"],
    backend=FilesystemBackend(root_dir="./agent/skills", virtual_mode=True),
    checkpointer=SqliteSaver(sqlite3.connect("agent.db")),
)
```

The agent has one tool: shell execution. It uses the `subs` and `mint` CLIs for everything.

### Skills

```
agent/skills/
  submission-extraction/SKILL.md    # How to parse submissions into fields
  document-knowledge/
    accord-25/SKILL.md              # ACORD 25 field requirements and mapping
    premium-disclosure/SKILL.md     # Premium Disclosure field requirements
  subs-tool/SKILL.md                # How to use the subs CLI
  mint-tool/SKILL.md                # How to use the mint CLI
```

**Document knowledge is one skill per document type** — scales cleanly as templates grow.

### Agent Flow with Error Handling

```
Input (email/submission)
  → Read Submission Extraction Skill
  → Extract fields into structured JSON
  → subs update <id> --fields-file <path>

  → Read Document Knowledge Skills (accord-25, premium-disclosure)
  → mint validate accord-25 --fields-file <path>
  → mint validate premium-disclosure --fields-file <path>

  → If validation errors:
      → subs update <id> --status review --validation-errors '<json>'
      → Exit (UI shows errors, user fixes fields)

  → If valid + auto-approve:
      → subs update <id> --fields-file <path>
      → Subs API detects auto-approve, transitions to approved, triggers generation internally
      → Agent exits

  → If valid + manual review:
      → subs update <id> --status review
      → Agent exits (UI shows for review, user approves via UI)

  --- BELOW THIS LINE IS SERVER-SIDE (subs API), NOT THE AGENT ---

  → On approval (triggered by subs API — either from UI /approve or auto-approve):
      → Subs API calls Mint HTTP API: POST http://localhost:3200/generate for each template
      → On success: updates submission documents[] with S3 URL
      → On partial failure: marks failed document as error, continues with others
      → Sets status to complete (or error if all documents fail)
      → Emits SSE events at each state transition
```

---

## Review UI

### Tech

React (Vite), TypeScript, shadcn/ui, Tailwind CSS

### Design Direction: "Confident Infrastructure"

- shadcn/ui foundation with Indemn brand customization
- DM Sans for headings (requires Tailwind font-family config + Google Fonts import)
- Indemn palette: Iris (#4752a3), Eggplant (#1e2553), subtle warm gray backgrounds
- Strong status colors: green (approved/complete), amber (needs review), blue (processing), red (error)
- PDF preview via `<iframe src={signedUrl}>` — simplest approach, S3 URLs with CORS

### Screen Structure

#### Screen 1: Inbox

Email-client style. Submission list on the left, email preview on the right.

- Status badges: New → Extracting → Ready for Review → Approved → Generated
- **Demo control:** Hidden keyboard shortcut (e.g., press `N`) triggers next mock submission into inbox with entrance animation. Presenter controls pacing.
- Auto-approve banner when enabled: "Auto-approve is ON — submissions are processed automatically"
- Auto-approved submissions get a distinct badge so Meg can tell them apart from manually reviewed ones
- **Empty state:** "No submissions yet — incoming emails will appear here"

#### Screen 2: Field Review (Core Screen)

Two-panel layout.

**Left panel — Source:**
- Rendered email (from, to, subject, date, body)
- Attachment thumbnails

**Right panel — Extracted Fields:**
Organized into sections:
- **Insured Information** — name, address, phone, email, form of business
- **Event Details** — event name, type, dates, location, expected participants
- **Coverage** — GL limit, accident limit, additional insured
- **Premium Calculation** — GL premium, surplus lines tax, accident premium, policy fee, total

**Field indicators:**
- Green dot: high confidence extraction
- Amber dot: agent's best guess, please confirm
- Calculator icon: computed field (rate_table or calculated source)
- Red outline: validation error with message

**Field editing:**
- Inline editable (click to edit, tab to next)
- Calculated fields are locked by default (show lock icon) — unlockable with a click, but editing triggers recalculation warning
- When a premium component changes, related premium fields recalculate

**Loading state:** Skeleton UI with pulsing fields during extraction
**Error state:** Inline error messages per field, retry button for generation failures

**Bottom bar:**
- "Approve & Generate" (primary)
- "Request More Info" (secondary)

#### Screen 3: Document Preview

Side-by-side document cards after approval.

**Each card:**
- PDF preview via `<iframe src={s3Url}>`
- Document name and generation timestamp
- Download button
- "Regenerate" option
- Individual status (handles partial success — one doc can fail while other succeeds)

**Processing Timeline:**
Horizontal timeline below documents with real measured timestamps:
"Email received → Fields extracted (Xms) → Reviewed by Meg → Documents generated (Xms)"
Timestamps come from the submission's `timeline` array.

**Error state:** If generation failed, show error message with retry button per document.

#### Settings (in Inbox header, not a separate screen)

Auto-approve toggle lives in the Inbox header bar — not a full screen. Reduces screen count, keeps demo focused. Template list is CLI-only (`mint templates`).

---

## Tech Stack Summary

| Component | Technology | Port |
|-----------|-----------|------|
| Mint CLI + Service | Node.js, Express, TypeScript | 3200 |
| Standard Form PDF | pdf-lib (AcroForm filling) | — |
| Custom Layout PDF | @react-pdf/renderer (renderToBuffer for server-side) | — |
| Storage | AWS S3 (signed URLs, 24h expiration for demo) | — |
| Submissions System | Node.js, Express, SQLite (better-sqlite3) | 3100 |
| Submissions CLI | Node.js (bin entry point) | — |
| Deep Agent | Python, LangGraph (deepagents pip dependency), FilesystemBackend | — |
| Agent Skills | Markdown SKILL.md files (one per doc type) | — |
| Review UI | React (Vite), TypeScript, shadcn/ui, Tailwind CSS | 5173 |
| Fonts | DM Sans (headings via Google Fonts), system (body) | — |

**CORS:** Both Express servers (Mint on 3200, Subs on 3100) include CORS middleware allowing requests from the UI origin (`http://localhost:5173`). S3 bucket CORS configured to allow `<iframe>` embedding for PDF preview.

---

## Repo Structure

```
craig-indemn/silent-sports-doc-gen/
├── mint/                        # Reusable PDF generation engine
│   ├── src/
│   │   ├── cli.ts               # CLI entry point (mint generate/validate/inspect/templates)
│   │   ├── server.ts            # Express API (POST /generate, GET /templates)
│   │   ├── engine/
│   │   │   ├── registry.ts      # Template registry
│   │   │   ├── pdf-lib.ts       # AcroForm fill generator
│   │   │   └── react-pdf.ts     # React-PDF generator (renderToBuffer)
│   │   └── templates/
│   │       ├── accord-25/
│   │       │   ├── template.pdf       # AcroForm version (Texas Specialty source)
│   │       │   ├── field-map.json     # Semantic name → PDF field name
│   │       │   ├── schema.json        # Field types, required, defaults, validation
│   │       │   └── generator.ts       # ACORD 25-specific logic
│   │       └── premium-disclosure/
│   │           ├── PremiumDisclosure.tsx  # React-PDF component
│   │           ├── schema.json
│   │           └── generator.ts
│   ├── package.json
│   └── tsconfig.json
│
├── subs/                        # Submissions system
│   ├── src/
│   │   ├── cli.ts               # CLI entry point (subs ingest/get/update/approve/add-doc)
│   │   ├── server.ts            # Express API + SSE endpoint
│   │   ├── db.ts                # SQLite setup and queries
│   │   └── types.ts             # Submission interface (shared with UI)
│   ├── package.json
│   └── tsconfig.json
│
├── agent/                       # Deep agent
│   ├── src/
│   │   ├── agent.py             # LangGraph agent with shell tool
│   │   └── run.py               # CLI entry to trigger agent on a submission
│   ├── skills/
│   │   ├── submission-extraction/SKILL.md
│   │   ├── document-knowledge/
│   │   │   ├── accord-25/SKILL.md
│   │   │   └── premium-disclosure/SKILL.md
│   │   ├── subs-tool/SKILL.md
│   │   └── mint-tool/SKILL.md
│   └── pyproject.toml
│
├── ui/                          # Review UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── SubmissionList.tsx
│   │   │   ├── EmailPreview.tsx
│   │   │   ├── FieldReview.tsx
│   │   │   ├── DocumentCard.tsx
│   │   │   ├── ProcessingTimeline.tsx
│   │   │   └── AutoApproveToggle.tsx
│   │   ├── pages/
│   │   │   ├── Inbox.tsx
│   │   │   ├── Review.tsx
│   │   │   └── Documents.tsx
│   │   ├── hooks/
│   │   │   ├── useSubmissions.ts    # Polling/SSE for submission updates
│   │   │   └── useSubmission.ts     # Single submission state
│   │   ├── lib/
│   │   │   └── api.ts               # REST client for submissions API
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── mock-data/                   # Demo fixtures
│   ├── submissions/
│   │   ├── mountain-bike-race.json
│   │   └── trail-run-event.json
│   └── emails/
│       ├── mountain-bike-race.eml
│       └── trail-run-event.eml
│
├── .env.example                 # MINT_PORT=3200, SUBS_PORT=3100, S3_BUCKET, S3_REGION, AWS creds
└── README.md
```

**Key additions from review:**
- `subs/` directory — submissions system (was implicit, now explicit)
- `hooks/` in UI — SSE/polling for real-time updates
- `.env.example` — configuration reference with port assignments
- Per-template `generator.ts` and `schema.json` — template-specific logic and field schemas (single source of truth; UI and agent get schema via `GET /templates/:name`, no separate schemas/ dir)

---

## What's Mocked vs Real in the Demo

| Component | Demo State | Notes |
|-----------|-----------|-------|
| Email arrival | Mocked | Presenter-triggered (keyboard shortcut `N`), pre-loaded mock emails |
| Submission extraction | Mocked | Agent uses pre-structured JSON from mock-data/ |
| Field validation | Real | mint validate against schema.json |
| Rate calculation | Mocked | Hardcoded rates for Mountain Bike activity type |
| ACORD 25 generation | Real | pdf-lib fills actual AcroForm PDF (verified working) |
| Premium Disclosure generation | Real | React-PDF renders calculated premium page |
| S3 upload | Real | PDFs land in actual S3 bucket with signed URLs |
| Review UI | Real | Fully functional review and approval flow |
| Auto-approve mode | Real | Toggle skips review step |
| Submissions system | Real | SQLite-backed, REST API, SSE updates |

---

## Risk Register

| Risk | Mitigation | Status |
|------|-----------|--------|
| ACORD 25 uses XFA, not AcroForm | Found AcroForm version, pdf-lib proof of concept confirmed | **RESOLVED** |
| pdf-lib can't read ACORD field names | Enumerated all 96 fields from Texas Specialty PDF | **RESOLVED** |
| Agent↔UI communication undefined | Shared submissions system with REST API + SSE | **RESOLVED** |
| No data model for submissions | Full TypeScript interface defined with per-field metadata | **RESOLVED** |
| CLI JSON escaping issues | Added --fields-file option as primary interface | **RESOLVED** |
| Approval→generation call chain undefined | Subs API calls Mint HTTP API on approval, documented call chain | **RESOLVED** |
| Rate recalculation ownership ambiguous | Subs API owns rate logic, recalculates on field patch | **RESOLVED** |
| SSE event schema undefined | Defined 5 event types with payload shapes | **RESOLVED** |
| Field naming inconsistency (namedInsured vs insured) | Standardized on `namedInsured`, documented concatenation in generator | **RESOLVED** |
| Schema duplication (top-level vs per-template) | Removed top-level schemas/, per-template schema.json is source of truth | **RESOLVED** |
| Certificate numbering persistence | Auto-increment in SQLite, `certificateNumber` field in data model | **RESOLVED** |
| Surplus lines tax varies by state | Added state-specific rate to premium model, noted as config point | **NOTED** |
| React-PDF server-side rendering | Use renderToBuffer (not browser pdf() API), prior art in Observatory | **NOTED** |
| CORS for local dev | Both Express servers configured for UI origin, S3 bucket CORS for iframe | **NOTED** |

---

## Future Scope (Not in MVP)

- **Member Certificate** — third document type, custom Silent Sports template with cert numbering
- **Endorsement Documents** — fourth type, lowest priority
- **Real email integration** — IMAP/Gmail API inbox monitoring (replaces mock trigger)
- **Real submission extraction** — PDF parsing, OCR for scanned documents
- **Meg's rate spreadsheet** — full rate engine for all activity types (replaces mocked rates)
- **AMS360 integration** — optional data backfill (WALK phase)
- **Multi-customer** — template management for INSURICA, Union General, etc.
- **Batch generation** — `POST /generate-batch` for multi-document submissions in one call

## Relationship to Kyle's Proposal

This MVP demonstrates the core of CRAWL Phase deliverables:
- ✅ Submission processing (mocked input, real validation)
- ✅ ACORD 25 certificate generation (real, AcroForm filling confirmed)
- ✅ Premium disclosure (real, mocked rates)
- ✅ Email notification concept (inbox view)
- ⬜ Follow-up email drafting (future)
- ⬜ Data export to spreadsheet (future)

The demo answers Kyle's team questions:
- **Technical feasibility:** Yes — proof of concept confirmed pdf-lib fills ACORD 25 AcroForm. 96 fields enumerated and mapped.
- **INSURICA reuse:** Mint is a standalone reusable engine. INSURICA COIs = new template + field mapping in the same registry.
- **Architecture:** Two CLIs (mint for PDF gen, subs for workflow), Skills-driven agent, React UI on shared REST API.
- **Timeline:** 7-11 days is realistic. The hardest technical risk (pdf-lib + ACORD 25 compatibility) is already resolved.
