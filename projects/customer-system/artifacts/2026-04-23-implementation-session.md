---
ask: "Record everything built, fixed, learned, and decided in the Apr 22-23 implementation session"
created: 2026-04-23
workstream: customer-system
session: 2026-04-23-roadmap
---

# Implementation Session Record — Apr 22-23, 2026

## What We Set Out To Do

Build the customer system entity model on the live OS and get data flowing through it, starting with Alliance Insurance as the first target customer. This is the first real system built on the Indemn OS — it proves the platform AND becomes the company's operating system for managing customers.

## The Big Vision (Why This Matters)

**The playbook IS the entity model.** The entities define what we need to know about any customer. Empty fields are gaps. Gaps drive next steps. When the picture is complete enough, a Proposal emerges — rendered FROM the entities by an AI associate.

Every customer follows the same process: interactions happen → entities get populated → understanding builds → proposal materializes. The entity model makes this systematic and repeatable. New team members have a guide. Progress is measurable. AI can drive the process.

Kyle's framing: "Take the two meetings from yesterday and build a dataset around them that we can trust as updates every time a sales call happens." The "dataset" IS the entity population. Meeting → Touchpoint → Intelligence extracted → Entities updated → Gaps visible → Next steps clear.

## What Was Built

### Entity Model (Wave 1 — COMPLETE)
26 entities live on the OS:
- **9 new**: Email, Document, Touchpoint, Operation, Opportunity, Proposal, Phase, CustomerSystem, BusinessRelationship
- **1 renamed**: AssociateDeployment → Associate (the deployed instance; AssociateType is the catalog)
- **5 updated**: Meeting (+touchpoint), Task (+phase, +touchpoint), Commitment (+phase, +touchpoint), Decision (+touchpoint), Signal (+touchpoint)
- **3 removed**: SuccessPhase (replaced by Phase), TestTask, VerifyTest
- **8 unchanged**: Company, Contact, Deal, Employee, AssociateType, Conference, OutcomeType, Stage

Key naming: "Interaction" renamed to "Touchpoint" because the kernel already has an Interaction entity for chat/voice sessions.

### Associate Wiring (Wave 2 — COMPLETE)
3 AI associates, 3 roles with watches, activated on async runtime:

| Associate | Watches | Produces |
|-----------|---------|----------|
| Email Classifier | Email created | Company link, Contact links → classified/needs_review/irrelevant |
| Touchpoint Synthesizer | Email→classified, Meeting created | Touchpoints, Documents from attachments |
| Intelligence Extractor | Touchpoint created | Tasks, Decisions, Commitments, Signals |

Skills written to filesystem for deepagents progressive disclosure (NOT loaded into system prompt). Each associate also has entity skills for correct CLI syntax.

### Gmail Adapter (Wave 3 — COMPLETE)
- `fetch_emails()` method added to Google Workspace adapter
- `gmail.readonly` scope added to domain-wide delegation
- `fetch_new` capability enabled on Email entity with `fetch_method` config
- `indemn email fetch-new --data '{"user_emails": ["kyle@indemn.ai"], "since": "2026-04-21"}'` works
- Cross-mailbox deduplication using email Message-ID header (not Gmail internal ID)

### Team Email Backfill (Wave 3.5 — IN PROGRESS)
~900 emails ingested from the full team (Kyle, Craig, Cam, Dhruv, Ganesh, George, Peter, Jonathan, Ian, Marlon, Rocky) for the week of Apr 21-23. Pipeline processing:
- ~400+ classified (irrelevant, needs_review, classified, processed)
- 20+ Touchpoints created with real summaries
- 20+ Tasks extracted (real, actionable: "Ship Alliance proposal by Apr 26")
- 4 Decisions, 15 Signals extracted
- ~500 still in queue, processing at 30 concurrent

## Infrastructure Fixes

### Queue Processor Bug
`WorkflowAlreadyStartedError` removed from temporalio SDK in newer versions. Replaced with `RPCError` + `RPCStatusCode.ALREADY_EXISTS`. Two commits to fix (wrong exception class first, then correct one).

### Runtime Service Token
Token was expired/missing. Generated new token, stored hash on Platform Admin actor, updated AWS Secrets Manager and Railway env var. Also fixed a bug where updating auth methods overwrote the password hash (immediately caught and fixed).

### Async Harness — Skills Loading (CRITICAL FIX)
**Problem**: Async harness concatenated ALL skill content into the system prompt. With 5-11 skills per associate, the prompt was enormous, causing LLM timeouts.
**Fix**: Write skills to filesystem and pass paths to `create_deep_agent(..., skills=skill_paths)`. deepagents handles progressive disclosure — agent reads skills on demand via `read_file`. Matches the chat harness pattern.

### Async Harness — Heartbeat During Agent Run (CRITICAL FIX)
**Problem**: Agent heartbeated once at start, then `await agent.ainvoke()` ran for minutes without heartbeating. Temporal's 2-minute heartbeat timeout cancelled the activity (`CancelledError`).
**Fix**: Background asyncio task heartbeats every 30 seconds during `ainvoke()`. Temporal workflow timeout increased from 10min to 30min, heartbeat timeout changed from 2min to 90sec.

### Async Harness — Execute Tool Enforcement
**Problem**: Agents used `write_file` and `task` subagents instead of `execute` with `indemn` CLI commands. Skills told them to use entity skills but agents defaulted to filesystem tools.
**Fix**: DEFAULT_PROMPT explicitly requires `execute` tool for ALL entity operations with concrete examples. "NEVER use write_file to store results. NEVER use task subagents for entity lookups."

### Model Upgrade
Changed async runtime from `google_vertexai:gemini-2.0-flash` to `google_vertexai:gemini-2.5-flash`. Enterprise Vertex AI project (`prod-gemini-470505`) confirmed working. Rate limits resolved.

### Concurrency
Increased `max_concurrent_sessions` from 10 to 30. Processing rate ~3x faster.

## Key Learnings

### 1. Skills Must Use Progressive Disclosure
Loading all skill content into the system prompt is wrong. Skills are written to the filesystem and passed as paths to deepagents. The agent reads them on demand. This is the designed pattern — the async harness was the only one not following it.

### 2. Entity Skills Are Required
Auto-generated entity skills (Email, Company, Contact, etc.) document exact field names, valid states, and CLI commands. Without them, agents guess at CLI syntax and get it wrong. Every associate needs its relevant entity skills loaded.

### 3. The Execute Tool Must Be Explicit
Agents don't innately know that `execute` with `indemn` CLI is how they interact with the OS. The system prompt must explicitly instruct this with examples. Without it, agents default to filesystem tools.

### 4. Heartbeats During Long Operations
Any Temporal activity that runs an LLM agent needs periodic heartbeating. The agent loop can take minutes. A single heartbeat at the start is insufficient.

### 5. Cross-Mailbox Email Dedup
The same email seen from multiple Gmail accounts has different Gmail internal IDs but the same email `Message-ID` header. Dedup must use the header, not the Gmail ID.

### 6. CLI Needs Field Selection
The `email list` command times out with large datasets because email bodies (full HTML) make responses huge. Need a `--fields` or `--exclude-fields` option. This is email-specific but the capability should be general.

## What's Next

### Immediate (pipeline running)
- Let the email backfill finish processing (~500 remaining in queue)
- Monitor output quality — spot-check tasks, touchpoints, classifications

### Wave 3.5 Remaining
- **Set up recurring email fetch** (#26) — automated go-forward for the whole team
- **Alliance email backfill** (#27) — manual curation via `gog` for historical Alliance emails
- **Meeting backfill** (#28) — full 30-day history via existing `indemn meeting fetch-new`

### Wave 4: Human Enrichment
Craig via CLI populates what requires judgment:
- Operations (from Craig's 30-page Alliance analysis)
- Opportunities (mapping problems to AssociateTypes)
- CustomerSystem (BT Core, Applied Epic, Dialpad)
- BusinessRelationship (carriers, agencies)

### Wave 5: Proposal Generation
- Create Proposal v2 + Phases for Alliance
- Link Opportunities, Commitments, Tasks to Phases
- Proposal Writer associate generates the document for Christopher

## Commits on indemn-os main

```
942e992 fix(harness): enforce execute tool for all entity operations
92b35c0 fix(harness): progressive skill disclosure + heartbeat during agent run
3b573f5 fix(gmail): use email Message-ID header for dedup instead of Gmail internal ID
b983261 fix(queue): use RPCError with ALREADY_EXISTS instead of removed WorkflowAlreadyStartedError
11d60a0 fix(queue): move WorkflowAlreadyStartedError import outside try block
fd9ba8e feat(integration): Gmail adapter for email ingestion
```

## Artifacts Produced This Session

| Artifact | What |
|----------|------|
| entity-model-brainstorm.md | Field-level specs for all 22 entities |
| entity-model-design-rationale.md | Thinking, tradeoffs, OS vision fit, associate skills, implementation status |
| playbook-as-entity-model.md | Key insight: entity model IS the playbook, gaps drive next steps |
| system-flow-v4.html | Visual diagram for Kyle — timeline as spine, Alliance journey |
| skills/email-classifier.md | Email Classifier associate skill |
| skills/touchpoint-synthesizer.md | Touchpoint Synthesizer associate skill |
| skills/intelligence-extractor.md | Intelligence Extractor associate skill |
