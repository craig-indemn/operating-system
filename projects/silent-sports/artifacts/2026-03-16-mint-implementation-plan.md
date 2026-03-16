---
ask: "Create a comprehensive implementation plan for Mint that can be executed by parallel Claude Code agents after context wipe"
created: 2026-03-16
workstream: silent-sports
session: 2026-03-16-a
sources:
  - type: artifact
    ref: "projects/silent-sports/artifacts/2026-03-16-mint-design-spec.md"
    name: "Mint Design Spec v3 (THE SOURCE OF TRUTH)"
---

# Mint — Implementation Plan

## CRITICAL: Design Spec Is The Source Of Truth

**Before writing ANY code, every agent MUST read the design spec:**

```
docs/DESIGN.md
```

(This is a copy of `projects/silent-sports/artifacts/2026-03-16-mint-design-spec.md` placed in the repo for local access.)

The design spec has been through 4 review cycles and is fully validated. It contains:
- Complete architecture with system diagram
- TypeScript data model for submissions
- CLI command specifications with exact output formats
- REST API contracts with request/response shapes
- SSE event schema with 5 event types and payload examples
- ACORD 25 field inventory (96 AcroForm fields mapped to semantic names)
- Premium Disclosure schema with all 16 field types
- Approval → generation call chain (subs API calls Mint HTTP API)
- Rate recalculation ownership (subs API owns it)
- Port assignments (Mint: 3200, Subs: 3100, UI: 5173)
- Repo structure

**DO NOT DEVIATE from the design spec.** If something seems unclear, re-read the spec. If it's genuinely not covered, document the decision in a code comment and proceed.

---

## Situation Context

**What this is:** Mint is a document generation system for insurance operations. It generates PDFs from structured data — ACORD 25 certificates (industry-standard form filling) and Premium Disclosures (custom React-PDF layout).

**Why we're building it:** Silent Sports (McKay Insurance) is a customer Indemn is re-engaging. Certificate generation is the hook — their current process takes 15 min per application (80-90/month at peak). Kyle (CEO) has a Crawl/Walk/Run proposal where this is the CRAWL deliverable at $1,500/mo.

**What the demo shows:** Mock email arrives → agent extracts fields → Meg reviews in UI → approves → two PDFs generate instantly (ACORD 25 + Premium Disclosure). Also shows full-auto mode (no human review).

**What ACORD 25 is:** The ACORD 25 is the "Certificate of Liability Insurance" — the most widely used proof-of-insurance document in the U.S. Every insurance agency uses these. It's a standard PDF form with fillable fields for insured name, coverage limits, policy numbers, etc. We fill these fields programmatically using the `pdf-lib` library's AcroForm support. The PDF has 96 fillable fields — we've already enumerated them all and tested filling them.

**Architecture (three components + shared state):**
- **Mint CLI + Service** (Node.js, port 3200) — reusable PDF generation. pdf-lib for ACORD 25 AcroForm, React-PDF for Premium Disclosure. This is a SEPARATE reusable tool — any customer can use it.
- **Submissions System** (Node.js, port 3100) — workflow orchestration. REST API + SSE + SQLite. Owns the submission lifecycle, rate calculation, and triggers generation by calling Mint's HTTP API on approval.
- **Review UI** (React + shadcn, port 5173) — inbox, field review, document preview.
- **Deep Agent** (Python, LangGraph) — extraction and validation only. Uses `subs` and `mint` CLIs via shell. Does NOT generate documents — that's the subs API's job.

**Key technical validation already done:**
- ACORD 25 AcroForm PDF downloaded and tested. pdf-lib successfully enumerates 96 fields and fills them. Proof of concept generated a valid 321KB PDF.
- The fillable ACORD 25 PDF URL: `https://www.texasspecialty.com/PDF/Acords/Acord-25-Certificate-Fillable.pdf`

**Repo:** `craig-indemn/silent-sports-doc-gen`

---

## Execution Model

This plan is designed for **parallel execution by independent Claude Code agents**. Each wave contains tasks that can run simultaneously. Waves must execute sequentially — each wave depends on the previous wave being complete.

Each task specifies:
- **What to build** — deliverable
- **Design spec sections to read** — specific sections of the design spec
- **Inputs** — what it depends on from previous waves
- **Outputs** — what it produces for downstream tasks
- **Acceptance criteria** — how to verify it's done

---

## Git Workflow

**Each parallel task works on its own branch.** This prevents merge conflicts.

- **Wave 0:** Task 0.1 pushes directly to `main`.
- **Wave 1:** Each agent creates a branch from `main`: `feat/mint-engine`, `feat/submissions`, `feat/mock-data`. Each agent commits only to their own branch. A coordinator merges all Wave 1 branches to `main` before Wave 2 starts.
- **Wave 2:** Each agent creates a branch from the merged `main`: `feat/review-ui`, `feat/deep-agent`. Merged to `main` before Wave 3.
- **Wave 3:** Works directly on `main`.

Branch naming: `feat/<task-slug>`. Commit messages: `<component>: <description>` (e.g., `mint: add ACORD 25 generator`).

---

## Technical Conventions

### Node.js

- **Node.js >= 20** required (native fetch, ES modules support)
- **Package manager:** npm (not pnpm, not yarn)
- **Monorepo:** npm workspaces — root `package.json` has `"workspaces": ["mint", "subs", "ui"]`
- **TypeScript execution:** Use `tsx` (TypeScript Execute) — fast, zero-config. Add as devDependency in each package.
  - CLI bin entries: `#!/usr/bin/env tsx`
  - Dev scripts: `"dev": "tsx watch src/server.ts"`
- **TSConfig for mint/:** Must include `"jsx": "react-jsx"` for React-PDF `.tsx` components
- **CLI availability:** After `npm install` at root (workspaces link bins automatically), CLIs are available via `npx mint` and `npx subs` from the repo root. The agent (Task 2.2) should invoke them as `npx --workspace=mint mint validate ...` and `npx --workspace=subs subs get ...`.

### Python

- **Python 3.11+** required
- **`deepagents`:** Install via `pip install deepagents`. This is a published PyPI package (the LangGraph-based agent framework used across Indemn's platform). Use `create_deep_agent()` with `FilesystemBackend` as shown in the design spec. Do NOT fall back to langgraph or any other framework — deepagents is required.
- **Virtual environment:** `python -m venv agent/.venv && source agent/.venv/bin/activate && pip install -e agent/`

### S3

- **For Wave 1-2 development:** Use `--output local` for all PDF generation. PDFs write to `output/` directory. No S3 credentials needed.
- **For Wave 3 integration:** Create an S3 bucket, configure CORS (allow GET from `http://localhost:5173`, allow `Content-Type` and `Range` headers), set credentials in `.env`.

### Environment

- Copy `.env.example` to `.env` before starting work
- For Wave 1-2: only `MINT_PORT=3200` and `SUBS_PORT=3100` are needed (defaults work without .env)
- For Wave 3: add S3 credentials and bucket name

### Rate Table (Hardcoded for Demo)

All agents building mock data or the rate calculation module must use these exact values:

**Mountain Bike Race (Bozeman, MT):**
- GL Premium: $2,500
- Surplus Lines Tax: $75 (3% of GL)
- Accident Insurance Premium: $800
- Policy Fee: $250
- **Total: $3,625**
- Rate Class: "mountain-bike-race"
- State: "MT"
- Surplus Lines Tax Rate: 0.03

**Trail Run Event (Missoula, MT):**
- GL Premium: $1,800
- Surplus Lines Tax: $54 (3% of GL)
- Accident Insurance Premium: $500
- Policy Fee: $250
- **Total: $2,604**
- Rate Class: "trail-run"
- State: "MT"
- Surplus Lines Tax Rate: 0.03

---

## Wave 0: Repo Scaffold (Sequential — Run First)

### Task 0.1: Create Repo and Monorepo Structure

**Read design spec sections:** "Repo Structure", "Tech Stack Summary"

**Deliverable:** Initialize `craig-indemn/silent-sports-doc-gen` with the exact directory structure from the design spec.

**Steps:**
1. Create the GitHub repo under `craig-indemn`
2. Initialize npm workspaces monorepo:
   - Root `package.json` with `"workspaces": ["mint", "subs", "ui"]`
   - Scripts: `"dev:mint": "npm -w mint run dev"`, `"dev:subs": "npm -w subs run dev"`, `"dev:ui": "npm -w ui run dev"`, `"dev:all": "concurrently \"npm run dev:mint\" \"npm run dev:subs\" \"npm run dev:ui\""`
   - Add `concurrently` as root devDependency
3. Initialize each package:
   - `mint/package.json`: express, pdf-lib, @react-pdf/renderer, react, @aws-sdk/client-s3, commander, cors. devDeps: tsx, typescript, @types/node, @types/express, @types/react. Bin: `"mint": "src/cli.ts"`. Dev script: `"dev": "tsx watch src/server.ts"`
   - `subs/package.json`: express, better-sqlite3, commander, cors. devDeps: tsx, typescript, @types/node, @types/express, @types/better-sqlite3. Bin: `"subs": "src/cli.ts"`. Dev script: `"dev": "tsx watch src/server.ts"`
   - `ui/package.json`: (Vite scaffolded via `npm create vite@latest ui -- --template react-ts`)
4. Create `tsconfig.json` in mint/ and subs/. For mint/: include `"jsx": "react-jsx"` for React-PDF TSX support.
5. Create `.env.example`:
   ```
   MINT_PORT=3200
   SUBS_PORT=3100
   S3_BUCKET=
   S3_REGION=us-east-1
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   ```
6. Create `.gitignore`: `node_modules/`, `dist/`, `.env`, `*.db`, `output/`, `.venv/`
7. Create all directories from the design spec repo structure (empty dirs with .gitkeep where needed):
   - `mint/src/engine/`, `mint/src/templates/accord-25/`, `mint/src/templates/premium-disclosure/`
   - `subs/src/`
   - `agent/src/`, `agent/skills/submission-extraction/`, `agent/skills/document-knowledge/accord-25/`, `agent/skills/document-knowledge/premium-disclosure/`, `agent/skills/subs-tool/`, `agent/skills/mint-tool/`
   - `mock-data/submissions/`, `mock-data/emails/`, `mock-data/mint-test/`
   - `output/`
8. Create `agent/pyproject.toml` with dependencies: deepagents, langchain-anthropic, langgraph. Python >= 3.11.
9. Copy the design spec into the repo as `docs/DESIGN.md`
10. Download the ACORD 25 AcroForm PDF from `https://www.texasspecialty.com/PDF/Acords/Acord-25-Certificate-Fillable.pdf` and save as `mint/src/templates/accord-25/template.pdf`
11. Run `npm install` at root to install all workspace dependencies
12. Push to `main`

**Acceptance criteria:**
- `npm install` succeeds at root (workspaces install all packages)
- `npx mint --help` and `npx subs --help` are reachable (even if they just error — bin entries exist)
- All directories from the design spec exist
- `.env.example`, `.gitignore`, `docs/DESIGN.md` exist
- `mint/src/templates/accord-25/template.pdf` is a valid PDF (not HTML redirect)
- Design spec is readable at `docs/DESIGN.md`

**Outputs:** Initialized repo on `main`. All subsequent tasks branch from here.

---

## Wave 1: Core Engines (Parallel — 3 agents)

### Task 1.1: Mint PDF Generation Engine

**Branch:** `feat/mint-engine`

**Read design spec sections:** "Mint CLI (Reusable)", "Template Registry", "ACORD 25 — Validated Technical Specification", "Premium Disclosure Specification"

**Deliverable:** The `mint/` package — CLI and Express API that generates PDFs from templates.

**Note on types:** The Mint engine does NOT import the Submission type. It receives a flat `Record<string, string | number | boolean>` of field values. Define your own local types in `mint/src/types.ts` for template schemas and field maps based on the design spec.

**Steps:**

1. **Template registry** (`mint/src/engine/registry.ts`):
   - Scan `mint/src/templates/` directories
   - Each template has: `schema.json`, `field-map.json` (ACORD 25 only), `generator.ts`
   - Registry exposes: `getTemplate(name)`, `listTemplates()`, `validateFields(name, fields)`

2. **ACORD 25 generator** (`mint/src/templates/accord-25/`):
   - The `template.pdf` should already be in place from Task 0.1. Verify it's a valid PDF with `pdf-lib` (`getForm().getFields()` should return 96 fields). If the download failed in 0.1, download it now from the URL in the Situation Context section.
   - Create `field-map.json` exactly as specified in the design spec — copy the JSON object verbatim from the "field-map.json for ACORD 25" section.
   - Create `schema.json` exactly as specified in the design spec — copy from the "schema.json" section under ACORD 25.
   - `generator.ts`: loads template.pdf with pdf-lib, maps fields via field-map.json. Key logic:
     - Concatenate `namedInsured` + `\n` + `insuredAddress` for the `INSURED` PDF field
     - Convert boolean `additionalInsured`/`waiverOfSubrogation` to "Y"/"N" strings
     - Check the `GL CGL` checkbox as a static default
     - Fill all text fields via `form.getTextField(pdfFieldName).setText(value)`
     - Flatten form after filling
     - Return buffer
   - Static defaults: producer = "McKay Insurance\n2211 Plaza Drive\nRocklin, CA 95765", insurerA = "Markel Insurance Company"

3. **Premium Disclosure generator** (`mint/src/templates/premium-disclosure/`):
   - Create `schema.json` exactly as specified in the design spec — copy from the "schema.json for Premium Disclosure" section.
   - `PremiumDisclosure.tsx`: React-PDF component using `@react-pdf/renderer`
   - Single page layout: header area, insured/event details section, premium breakdown table (line items with amounts, total row highlighted), rate class and tax rate as footnotes, disclaimer text at bottom
   - Use DM Sans font — download the TTF files and register with `Font.register()` from `@react-pdf/renderer`. Place font files in `mint/src/templates/premium-disclosure/fonts/`.
   - `generator.ts`: receives fields, passes to React component, renders to buffer via `renderToBuffer` (NOT the browser `pdf()` API)

4. **pdf-lib generator** (`mint/src/engine/pdf-lib.ts`):
   - Generic form filler: takes template PDF bytes + field-map + field values
   - Maps semantic field names to PDF field names
   - Handles text fields (`setText`) and checkboxes (`check`/`uncheck`)
   - Flattens form after filling
   - Returns PDF buffer

5. **React-PDF generator** (`mint/src/engine/react-pdf.ts`):
   - Generic renderer: takes a React component + props, calls `renderToBuffer`
   - Returns PDF buffer

6. **S3 upload** (`mint/src/engine/s3.ts`):
   - Upload buffer to S3, return signed URL (24h expiration)
   - When `--output local`: write to `output/<template>-<timestamp>.pdf`, return the file path
   - Skip S3 entirely if no AWS credentials configured (default to local)

7. **CLI** (`mint/src/cli.ts`):
   - `mint generate <template> --fields-file <path> [--output s3|local]`
   - `mint generate <template> --fields '<json>' [--output s3|local]`
   - `mint validate <template> --fields-file <path>`
   - `mint validate <template> --fields '<json>'`
   - `mint templates`
   - `mint inspect <template>`
   - All output is JSON on stdout. Exit code 0 for success, 1 for errors.
   - Error format: `{ "status": "error", "error": "VALIDATION_FAILED"|"GENERATION_FAILED", "message": "..." }`
   - Use `commander` for CLI parsing

8. **Express API** (`mint/src/server.ts`):
   - `POST /generate` — same logic as CLI generate, default `--output local` unless S3 configured
   - `GET /templates` — list all templates
   - `GET /templates/:name` — return schema.json for a template
   - CORS enabled for `http://localhost:5173`
   - Port from `MINT_PORT` env var (default 3200)

**Acceptance criteria:**
- `npx mint generate accord-25 --fields-file mock-data/mint-test/accord-25-fields.json --output local` produces a valid PDF in `output/`
- `npx mint generate premium-disclosure --fields-file mock-data/mint-test/premium-disclosure-fields.json --output local` produces a valid PDF
- `npx mint validate accord-25 --fields '{"date":"03/16/2026"}'` returns validation errors for missing required fields
- `npx mint inspect accord-25` returns the schema JSON
- `npx mint templates` lists both templates
- Express API responds at `http://localhost:3200/generate`
- Create test field files in `mock-data/mint-test/` with the Mountain Bike Race data from the Rate Table section above

---

### Task 1.2: Submissions System

**Branch:** `feat/submissions`

**Read design spec sections:** "Submission Data Model", "Submissions System" (CLI + REST API + State Machine + Approval→Generation Call Chain + Rate Recalculation + SSE Event Schema)

**Deliverable:** The `subs/` package — CLI, REST API, SQLite database, SSE stream.

**Steps:**

1. **Types** (`subs/src/types.ts`):
   - Implement the `Submission` TypeScript interface exactly as specified in the design spec
   - Export for use across the subs package

2. **Database** (`subs/src/db.ts`):
   - SQLite via `better-sqlite3`
   - Schema:
     ```sql
     CREATE TABLE submissions (
       id TEXT PRIMARY KEY,
       status TEXT NOT NULL DEFAULT 'received',
       data TEXT NOT NULL,  -- JSON blob of full Submission object
       createdAt TEXT NOT NULL,
       updatedAt TEXT NOT NULL
     );
     CREATE TABLE config (
       key TEXT PRIMARY KEY,
       value TEXT NOT NULL
     );
     CREATE TABLE cert_counter (
       id INTEGER PRIMARY KEY AUTOINCREMENT
     );
     ```
   - The `data` column stores the full Submission JSON. Individual fields (status, createdAt, updatedAt) are duplicated as columns for querying.
   - CRUD functions: createSubmission, getSubmission, listSubmissions, updateSubmission, approveSubmission
   - Certificate number format: `SS-{year}-{counter:04d}` (e.g., "SS-2026-0001"). Assigned when status transitions to `approved`. Insert into cert_counter, use lastInsertRowid.

3. **Rate calculation** (`subs/src/rates.ts`):
   - Hardcoded rate table — use the exact values from the "Rate Table" section in this plan
   - Function: `calculatePremium(fields)` → returns the premium block matching the design spec interface
   - Recalculates when `PATCH /submissions/:id` changes premium-affecting fields (eventType, eachOccurrence, generalAggregate, etc.)
   - Surplus lines tax = glPremium × surplusLinesTaxRate (0.03 for MT)

4. **Generation trigger** (`subs/src/generate.ts`):
   - Called by the approve endpoint and auto-approve logic
   - Calls Mint HTTP API (`POST http://localhost:3200/generate`) for each template (accord-25, then premium-disclosure)
   - On success: updates submission `documents[]` with URL and timestamp
   - On failure: marks that document as `error` with error message, continues to next template
   - After both: set status to `complete` (even with partial failure — individual doc status shows the error)
   - Updates `timeline` array with generation events and durations

5. **SSE manager** (`subs/src/sse.ts`):
   - Track connected clients (array of Response objects)
   - Emit function: `broadcast(event, data)` writes to all clients
   - 5 event types matching design spec exactly:
     - `submission:created` — full submission summary (id, status, email.subject, createdAt)
     - `submission:updated` — changed fields only (id, status, fields, updatedAt)
     - `submission:status` — status-only change (id, status, updatedAt)
     - `document:generated` — single doc complete (id, template, url, generatedAt)
     - `submission:error` — error details (id, error, message, template)
   - On initial connection: replay `submission:created` for all existing submissions

6. **CLI** (`subs/src/cli.ts`):
   - `subs ingest --source email --id <msg-id>` / `subs ingest --source file --path <path>`
   - `subs list [--status <status>]`
   - `subs get <id> [--format json|table]`
   - `subs update <id> --fields '<json>'` / `--fields-file <path>` / `--status <status>` / `--validation-errors '<json>'`
   - `subs approve <id>`
   - `subs add-doc <id> --template <name> --url <url>`
   - `subs config set auto-approve <true|false>`
   - All output is JSON on stdout. Exit 0 success, 1 error.

7. **REST API** (`subs/src/server.ts`):
   - `GET /submissions` — list all
   - `GET /submissions/:id` — get one
   - `PATCH /submissions/:id` — update fields. If premium-affecting fields change, recalculate premium. If auto-approve is on and fields are complete, auto-transition to approved and trigger generation.
   - `POST /submissions/:id/approve` — approve + assign cert number + trigger generation (calls Mint HTTP API)
   - `POST /submissions/:id/generate` — re-generate documents (for regeneration after field edits)
   - `POST /submissions/demo-next` — reads mock files from `mock-data/submissions/` in alphabetical order, maintains a cursor in the config table. After last file, wraps around to the first.
   - `GET /submissions/stream` — SSE endpoint
   - `GET /config` / `PATCH /config` — settings (auto_approve)
   - CORS enabled for `http://localhost:5173`
   - Port from `SUBS_PORT` env var (default 3100)

8. **State machine enforcement:**
   - Valid transitions: received→extracting→review→approved→generating→complete, with error reachable from generating
   - Auto-approve: received→extracting→approved→generating→complete (skips review)
   - Reject invalid transitions with 400 error

**Acceptance criteria:**
- `npx subs ingest --source file --path mock-data/submissions/mountain-bike-race.json` creates a submission (use a test JSON you create, or wait for Task 1.3 mock data)
- `npx subs get SS-001 --format json` returns the full submission
- `npx subs update SS-001 --fields '{"eventType":"mountain-bike-race"}'` updates fields and premium recalculates
- `npx subs approve SS-001` changes status to approved (generation will fail if Mint isn't running — that's expected; verify status transition works)
- `curl http://localhost:3100/submissions/stream` shows SSE events when submissions change
- `curl -X POST http://localhost:3100/submissions/demo-next` creates a new submission from mock data

---

### Task 1.3: Mock Data

**Branch:** `feat/mock-data`

**Read design spec sections:** "What's Mocked vs Real in the Demo", "ACORD 25 — Fields Relevant to Silent Sports", "Premium Disclosure Specification"

**IMPORTANT:** Use field names and premium values from the design spec and the Rate Table section in this plan. Do NOT reference `mint/src/templates/` schema.json files — they are being built in parallel by another agent.

**Deliverable:** The `mock-data/` directory with realistic demo fixtures.

**Steps:**

1. **Mountain Bike Race submission** (`mock-data/submissions/mountain-bike-race.json`):
   - Full Submission object matching the TypeScript interface in the design spec
   - Email from "Jake Morrison <jake@mountainbikeadventures.com>" to "submissions@silentsportsinsurance.com"
   - Subject: "Insurance Application - Bozeman Mountain Bike Race June 2026"
   - Body: realistic email requesting event insurance for a 3-day mountain bike race in Bozeman, MT. Include event dates (June 15-17, 2026), expected 200 participants, venue (Gallatin National Forest trails).
   - Pre-extracted fields with confidence scores: high for name/address/dates, medium for coverage limits
   - Premium: use the exact Mountain Bike Race values from the Rate Table section ($2,500 GL, $75 tax, $800 accident, $250 fee, $3,625 total)
   - Status: "received"
   - Empty documents array, empty timeline

2. **Trail Run Event submission** (`mock-data/submissions/trail-run-event.json`):
   - Email from "Sarah Chen <sarah@montanatrailrunners.org>"
   - Trail Run event in Missoula, MT, September 2026, 150 participants
   - Use the exact Trail Run values from the Rate Table section ($1,800 GL, $54 tax, $500 accident, $250 fee, $2,604 total)
   - Status: "received"

3. **Mock emails** (`mock-data/emails/`):
   - `mountain-bike-race.eml` — realistic email with headers and body matching submission #1
   - `trail-run-event.eml` — matching submission #2

4. **Test fields for direct Mint CLI testing:**
   - `mock-data/mint-test/accord-25-fields.json` — flat JSON with all fields needed by ACORD 25 (use field names from design spec schema.json: namedInsured, insuredAddress, effectiveDate, expirationDate, eachOccurrence, generalAggregate, etc.)
   - `mock-data/mint-test/premium-disclosure-fields.json` — flat JSON with all Premium Disclosure fields (namedInsured, eventName, eventType, glPremium, surplusLinesTax, total, etc.)

**Acceptance criteria:**
- All JSON files parse correctly (`node -e "JSON.parse(require('fs').readFileSync('file.json'))"`)
- Field names match the design spec's schema.json specifications (docs/DESIGN.md sections "schema.json" for ACORD 25 and "schema.json for Premium Disclosure")
- Premium calculations are internally consistent (total = GL + tax + accident + fee)
- Mock emails have valid .eml format with From, To, Subject, Date headers and readable body text

---

## Wave 2: UI + Agent (Parallel — 3 agents)

### Task 2.1a: Review UI — Foundation + Inbox

**Branch:** `feat/review-ui`

**Read design spec sections:** "Review UI" — Tech, Design Direction, Screen 1: Inbox

**Inputs from Wave 1:** Subs REST API contract (in design spec), mock data (Task 1.3)

**Deliverable:** UI project setup with Inbox page working.

**Steps:**

1. **Project setup** (if Vite wasn't scaffolded in 0.1, scaffold it now):
   - Vite + React + TypeScript
   - `npx shadcn@latest init` — choose: New York style, Slate base color, CSS variables yes
   - Install shadcn components: `npx shadcn@latest add badge button card input switch skeleton separator scroll-area`
   - Install React Router: `npm install react-router-dom`
   - Add DM Sans font via Google Fonts link in `index.html`
   - Configure Tailwind with Indemn color palette as CSS variables:
     ```css
     --iris: #4752a3;
     --eggplant: #1e2553;
     --lime: #e0da67;
     --lilac: #a67cb7;
     ```
   - Status colors: green-500 (complete), amber-500 (review), blue-500 (processing), red-500 (error)

2. **Submission type** (`ui/src/types.ts`):
   - Define the `Submission` type locally (matching the design spec interface). Do NOT import from subs/ — the UI has its own copy based on the API contract.

3. **API client** (`ui/src/lib/api.ts`):
   - fetch-based REST client for subs API at `http://localhost:3100`
   - Functions: `listSubmissions()`, `getSubmission(id)`, `updateSubmission(id, fields)`, `approveSubmission(id)`, `regenerateSubmission(id)`, `triggerDemoNext()`, `getConfig()`, `updateConfig(config)`

4. **SSE hook** (`ui/src/hooks/useSubmissions.ts`):
   - Connect to `http://localhost:3100/submissions/stream` via `EventSource`
   - Handle 5 event types from design spec:
     - `submission:created` → add to list
     - `submission:updated` → merge fields into existing entry
     - `submission:status` → update status only
     - `document:generated` → append to documents array
     - `submission:error` → set error on submission
   - On initial mount, also call `listSubmissions()` as a fallback
   - Export `useSubmission(id)` for single-submission views

5. **Inbox page** (`ui/src/pages/Inbox.tsx`):
   - Split layout: SubmissionList on left (scrollable), email preview on right
   - Status badges using shadcn Badge with status-specific colors
   - Auto-approve toggle in header bar (shadcn Switch)
   - Banner when auto-approve is on: "Auto-approve is ON — submissions are processed automatically"
   - Auto-approved submissions get a distinct "Auto" badge
   - Empty state: "No submissions yet — incoming emails will appear here"
   - Keyboard shortcut: `useEffect` listening for `N` key → calls `triggerDemoNext()`
   - New submissions animate in (CSS transition on opacity + translateY)
   - Click submission → navigate to `/submissions/:id/review`

6. **Components:**
   - `SubmissionList.tsx` — list item with status badge, email subject, timestamp
   - `EmailPreview.tsx` — rendered email (from, to, subject, date, body)
   - `AutoApproveToggle.tsx` — switch in header with label

7. **Routing** (`ui/src/App.tsx`):
   - `/` → Inbox
   - `/submissions/:id/review` → Review (placeholder)
   - `/submissions/:id/documents` → Documents (placeholder)

**Acceptance criteria:**
- UI renders at `http://localhost:5173`
- Pressing `N` calls the demo-next endpoint (verify in network tab; works fully when subs API is running)
- Submission list renders with correct status badges
- Clicking a submission shows email preview on right
- Auto-approve toggle calls PATCH /config
- Empty state displays when no submissions exist
- Routing works — clicking a submission navigates to /submissions/:id/review

---

### Task 2.1b: Review UI — Field Review + Documents

**Branch:** `feat/review-ui` (same branch as 2.1a — this task runs AFTER 2.1a)

**Read design spec sections:** "Review UI" — Screen 2: Field Review, Screen 3: Document Preview

**Inputs:** Task 2.1a complete (project setup, API client, hooks, routing in place)

**Deliverable:** Field Review and Document Preview pages.

**Steps:**

1. **Field Review page** (`ui/src/pages/Review.tsx`):
   - Two-panel layout: email preview left, extracted fields right
   - Left panel: reuse `EmailPreview` component from 2.1a
   - Right panel: fields organized into sections:
     - **Insured Information** — namedInsured, insuredAddress
     - **Event Details** — eventName, eventType, eventDates, eventLocation
     - **Coverage** — eachOccurrence, generalAggregate, personalAdvInjury, additionalInsured
     - **Premium Calculation** — glPremium, surplusLinesTax, accidentPremium, policyFee, total
   - Field indicators:
     - Green dot (●) for confidence: "high"
     - Amber dot (●) for confidence: "medium" or "low"
     - Calculator icon (🔢 or similar) for source: "calculated" or "rate_table"
     - Red outline + error message for fields with validationError
   - Inline editing: click field → becomes input → tab/enter saves → calls `PATCH /submissions/:id`
   - Calculated fields (source: "calculated"/"rate_table"): show lock icon, disabled by default
   - Skeleton loading when status is "extracting"
   - Bottom bar: "Approve & Generate" primary button → calls `POST /submissions/:id/approve` → navigates to documents page. "Request More Info" secondary button (visual only for demo).

2. **Document Preview page** (`ui/src/pages/Documents.tsx`):
   - Side-by-side cards for each document in `submission.documents[]`
   - Each card (`DocumentCard` component):
     - PDF preview: `<iframe src={doc.url} />` when status is "complete"
     - Document template name + generation timestamp
     - Download button (link to doc.url with download attribute)
     - "Regenerate" button → calls `POST /submissions/:id/generate`
     - Status-specific display: spinner when "generating", error message + retry when "error"
   - Processing Timeline component below cards:
     - Horizontal timeline reading from `submission.timeline[]`
     - Each event shows label + duration since previous event
     - Simple flex layout with dots and lines between events

3. **Components:**
   - `FieldReview.tsx` — the full editable field form with sections and indicators
   - `DocumentCard.tsx` — PDF preview card with actions
   - `ProcessingTimeline.tsx` — horizontal timeline from submission.timeline

**Acceptance criteria:**
- Field Review page shows all field sections with correct indicators
- Editing a field sends PATCH request (verify in network tab)
- Calculated fields show lock icon and are not editable by default
- "Approve & Generate" button calls approve endpoint and navigates to documents
- Document Preview shows iframe PDF previews when URLs are available
- Processing timeline renders events from submission.timeline
- Error states display (red outline for field errors, error message for failed documents)
- Loading states display (skeleton for extracting, spinner for generating)

---

### Task 2.2: Deep Agent

**Branch:** `feat/deep-agent`

**Read design spec sections:** "Deep Agent" (Instantiation, Skills, Agent Flow with Error Handling)

**Inputs from Wave 1:** Subs CLI (Task 1.2), Mint CLI (Task 1.1)

**Deliverable:** The `agent/` package — LangGraph agent with skills.

**CLI invocation from agent:** The agent runs in the repo root. Invoke CLIs as:
- `npx --workspace=subs subs get SS-001 --format json`
- `npx --workspace=mint mint validate accord-25 --fields-file /tmp/fields.json`

**Steps:**

1. **Skills** (`agent/skills/`):
   - `submission-extraction/SKILL.md` — For the demo: read mock submission data, extract all fields needed by both templates. Document the complete field list the agent must extract:
     - Shared: namedInsured, insuredAddress, effectiveDate, expirationDate, certificateHolder
     - ACORD 25 only: glPolicyNumber, eachOccurrence, generalAggregate, productsCompOpsAgg, personalAdvInjury, damageToRentedPremises, medicalExpense, additionalInsured, waiverOfSubrogation, descriptionOfOperations
     - Premium Disclosure only: eventName, eventType, eventDates, eventLocation, glPremium, surplusLinesTax, surplusLinesTaxRate, accidentPremium, policyFee, total, rateClass
   - `document-knowledge/accord-25/SKILL.md` — ACORD 25 field requirements. Required vs optional. Default values. Use `npx --workspace=mint mint inspect accord-25` to get the schema.
   - `document-knowledge/premium-disclosure/SKILL.md` — Premium Disclosure field requirements and calculation notes.
   - `subs-tool/SKILL.md` — Full `subs` CLI reference with examples using `npx --workspace=subs subs ...`
   - `mint-tool/SKILL.md` — Mint CLI reference (validate and inspect only). Explicit note: "NEVER call `mint generate` — generation is triggered server-side on approval."

2. **Agent** (`agent/src/agent.py`):
   - Use `deepagents` library: `create_deep_agent()` with `FilesystemBackend`
   - Model: `anthropic:claude-sonnet-4-20250514`
   - Single tool: shell execution (subprocess.run with capture_output=True)
   - System prompt: "You are an insurance document processing agent. You extract fields from submissions and validate them against document templates. You NEVER generate documents — generation happens server-side when a submission is approved. Use the subs CLI to read and update submissions. Use the mint CLI to validate fields."
   - Skills pointed at `agent/skills/`

3. **Runner** (`agent/src/run.py`):
   - CLI entry point: `python -m agent.src.run <submission-id>`
   - Loads the agent, invokes it with the submission ID
   - Agent flow:
     1. `subs get <id>` → read current submission
     2. Extract fields from the mock email/data (for demo, read the pre-structured fields from the submission)
     3. `subs update <id> --fields-file <path>` → write extracted fields
     4. `mint validate accord-25 --fields-file <path>` → check ACORD 25 fields
     5. `mint validate premium-disclosure --fields-file <path>` → check Premium Disclosure fields
     6. If validation passes: `subs update <id> --status review`
     7. If validation fails: `subs update <id> --status review --validation-errors '<errors>'`

4. **Dependencies** (`agent/pyproject.toml`):
   - `deepagents`, `langchain-anthropic`
   - Python 3.11+

**Acceptance criteria:**
- `cd <repo-root> && python -m agent.src.run SS-001` processes a mock submission (requires subs and mint services running)
- Agent reads the submission, writes extracted fields, validates against both templates, and sets status to "review"
- Skills files exist and contain accurate, usable CLI documentation
- Agent does NOT call `mint generate`

---

## Wave 3: Integration + Demo Polish (Sequential)

### Task 3.1: End-to-End Integration Test

**Inputs:** All Wave 1 + Wave 2 tasks merged to `main`.

**Steps:**
1. Set up S3:
   - Create an S3 bucket (e.g., `indemn-mint-demo`)
   - Configure CORS: allow GET from `http://localhost:5173`, allow Content-Type and Range headers
   - Set S3 credentials in `.env`
2. Start all services: `npm run dev:all`
3. Walk through the full manual demo flow:
   - Open UI at localhost:5173
   - Press `N` → verify submission appears in inbox
   - Run agent: `python -m agent.src.run SS-001`
   - Verify fields populate in field review screen
   - Edit a field, verify premium recalculates
   - Click "Approve & Generate"
   - Verify both PDFs generate and appear in document preview
   - Verify processing timeline shows real timestamps
   - Download both PDFs — verify ACORD 25 has filled fields, Premium Disclosure has correct amounts
4. Test auto-approve mode:
   - Toggle auto-approve ON
   - Press `N` → verify second submission flows through automatically
5. Test error handling:
   - Approve a submission with missing fields → verify validation errors
   - Kill Mint service, approve → verify partial failure in UI
6. Fix any integration issues found

**Acceptance criteria:**
- Both demo flows (manual + auto) complete end-to-end
- PDFs are valid and downloadable
- ACORD 25 shows: insured name, McKay Insurance as producer, Markel as insurer, coverage limits, policy number, dates
- Premium Disclosure shows: correct premium breakdown matching rate table values
- SSE drives real-time UI updates
- Error states display correctly

### Task 3.2: Demo Polish

**Steps:**
1. Review and polish mock data — make emails realistic and professional
2. Verify DM Sans font renders correctly in Premium Disclosure PDF
3. Verify PDF preview works in iframe (S3 CORS)
4. Test the `N` keyboard shortcut with both mock submissions
5. Write `README.md` with: project overview, prerequisites (Node 20+, Python 3.11+), setup steps, demo walkthrough
6. Create `demo.sh` that: copies .env.example to .env (if not exists), runs npm install, starts all services, prints URLs

**Acceptance criteria:**
- `./demo.sh` starts the system (after S3 credentials are configured)
- README has complete setup and demo instructions
- Both mock submissions produce professional-looking PDFs

---

## Dependency Graph

```
Wave 0: [0.1 Repo Scaffold]
              │
              ▼
Wave 1: [1.1 Mint Engine] ─── [1.2 Submissions] ─── [1.3 Mock Data]
         (parallel)            (parallel)              (parallel)
              │                     │                       │
              └─────── merge to main ───────────────────────┘
                              │
                              ▼
Wave 2: [2.1a UI Foundation] → [2.1b UI Review+Docs] ─── [2.2 Deep Agent]
         (sequential)           (sequential)                (parallel)
              │                     │                          │
              └─────── merge to main ──────────────────────────┘
                              │
                              ▼
Wave 3: [3.1 Integration Test] → [3.2 Demo Polish]
```

---

## Agent Assignment

| Wave | Task | Branch | Estimated Effort |
|------|------|--------|-----------------|
| 0 | 0.1 Repo Scaffold | main | 30 min |
| 1 | 1.1 Mint Engine | feat/mint-engine | 3-4 hours |
| 1 | 1.2 Submissions System | feat/submissions | 3-4 hours |
| 1 | 1.3 Mock Data | feat/mock-data | 1 hour |
| 2 | 2.1a UI Foundation + Inbox | feat/review-ui | 2-3 hours |
| 2 | 2.1b UI Review + Documents | feat/review-ui | 2-3 hours |
| 2 | 2.2 Deep Agent | feat/deep-agent | 2-3 hours |
| 3 | 3.1 Integration | main | 2-3 hours |
| 3 | 3.2 Demo Polish | main | 1-2 hours |

**Total estimated effort:** ~17-23 hours of agent time. With parallelization: ~11-14 hours wall clock.

---

## Rules for All Agents

1. **Read the design spec first.** It is at `docs/DESIGN.md` in the repo. Every field name, API contract, CLI output format, and architectural decision is in there.

2. **Do not deviate from the design.** If you think something should be different, document it as a code comment but implement as specified.

3. **Use exact port numbers.** Mint: 3200, Subs: 3100, UI: 5173.

4. **Use exact field names.** `namedInsured`, not `insuredName`. `effectiveDate`, not `policyEffectiveDate`. The field-map.json and schema.json in the design spec are canonical.

5. **JSON output from all CLIs.** Exit code 0 success, 1 error. Error format: `{ "status": "error", "error": "<CODE>", "message": "<human-readable>" }`.

6. **TypeScript for Node.js.** Use `tsx` for execution. The `Submission` interface is in the design spec — subs/ implements it as the canonical type, mint/ and ui/ define their own local types based on what they need from the API contract.

7. **Test as you go.** Each task has acceptance criteria. Verify them before marking complete.

8. **Commit to your branch.** Never push to main during Wave 1 or Wave 2. Use the branch assigned to your task.

9. **Default to `--output local` for PDF generation during development.** S3 is not needed until Wave 3.

10. **Use the rate table values from this plan.** Mountain Bike Race: $3,625 total. Trail Run: $2,604 total. These must match across mock data, rate calculation, and generated PDFs.
