---
ask: "Prompt for Claude.ai to generate the intake manager workflow diagram for the showcase page"
created: 2026-03-23
workstream: content-system
session: 2026-03-23-b
sources:
  - type: codebase
    description: "intake-manager repo — UG Portal, multi-event pipeline, validation, quoting"
---

# Intake Manager Workflow Diagram — Prompt

Create a workflow diagram for Indemn's Intake Manager — a product showcase page on blog.indemn.ai showing how a full underwriting submission pipeline automates the journey from raw submission to quote-ready package.

**What this is:** MGAs, program administrators, and carriers process hundreds of submissions through a complex pipeline: documents arrive from multiple channels, data must be extracted from messy PDFs and applications, every field validated against underwriting guidelines, missing information chased down, and finally quotes generated from one or more carriers. Today this takes days of manual work per submission. Indemn's Intake Manager automates the entire pipeline — from the moment a submission arrives through document processing, AI-powered extraction, rules-based validation, and multi-provider quoting. Submissions accumulate documents over days or weeks, and the system manages the full lifecycle.

**How this relates to Email Intelligence:** Email Intelligence is the smart inbox layer — it classifies and links incoming emails. The Intake Manager is the full pipeline that sits behind it. Email Intelligence is step one; the Intake Manager is the complete workflow. This diagram should show the full pipeline, with email/portal/API intake at the top flowing into the processing stages.

**The workflow — step by step:**

1. **Submissions arrive** — Documents come in through multiple channels: email inbox (powered by Email Intelligence), broker portal upload, API submission, or manual entry. The diagram should show these channels converging. Unlike the Email Intelligence diagram which focused on the inbox, this shows the full channel-agnostic intake. Each submission becomes a **thread** — a container that accumulates emails, documents, and events over time.

2. **Document processing** — Raw documents (PDFs, ACORD forms, applications, loss runs, endorsements) are sent to a document processing engine. OCR and text extraction convert messy documents into readable text. The system deduplicates documents that arrive multiple times. Show this as a processing step with document types going in and structured text coming out.

3. **AI extraction** — An AI model reads the extracted text and pulls structured data: named insured, address, entity type, business description, revenue, coverage limits, effective dates, loss history, driver information, vehicle schedules — whatever fields are relevant to the line of business. Show this as the intelligence step where unstructured documents become structured parameters. Two extraction modes: standard (GPT-4) and deep (Claude) for complex submissions.

4. **Parameter merging** — This is a key differentiator. Submissions don't arrive complete. An agent might send the application on Day 1, loss runs on Day 3, and driver MVRs on Day 7. Each new document adds parameters to the same submission thread. The system merges parameters intelligently using configurable strategies: overwrite, append, keep existing, or newer wins. Show this as an accumulation step — parameters building up over time across multiple events.

5. **Validation** — Extracted parameters are checked against underwriting guidelines. This is rules-based with LLM augmentation — JSON rule definitions per line of business, per organization. Three possible outcomes:
   - **Valid** — all rules pass, submission is clean
   - **Invalid** — auto-decline violations (hard stops)
   - **Needs Review** — some violations flagged for underwriter judgment
   Show this as a decision point with the three paths. Validation is organization-specific — different MGAs have different guidelines, different risk appetites, different hard stops.

6. **Quote generation** — For valid submissions, quotes are generated from one or more carriers. The system supports multiple providers (show 2-3 carrier boxes). Each provider has its own API integration, credential management, and payload formatting. Quotes can be compared side-by-side. Show this as a multi-provider step with carrier logos/labels and quote outputs (premium, limits, terms).

7. **Underwriter dashboard** — The underwriter sees submissions organized by status with a tab-based detail view. For each submission: the full event timeline (every document and email that contributed), all extracted parameters, validation results, and quotes. The underwriter can review, approve, modify parameters, or request additional information. Show this as the final output — a clean dashboard replacing manual spreadsheet tracking.

**What to emphasize visually:**

- **Steps 2-6 are the automated pipeline.** This is what Indemn handles. Visual grouping as "Automated by Indemn" or "Intelligent Pipeline."

- **The multi-event accumulation** (step 4) is the key differentiator. This isn't one-shot processing. Show documents arriving over multiple days feeding into the same submission thread, with parameters merging and the submission becoming more complete over time. This could be visualized as a timeline or a growing progress bar.

- **The multi-channel intake** (step 1) should be prominent. Email, portal, API, manual — the pipeline doesn't care how the submission arrives.

- **The validation decision point** (step 5) should show the three outcomes clearly: Valid → Quote, Invalid → Decline, Needs Review → Underwriter.

- **Multi-provider quoting** (step 6) should show multiple carriers, emphasizing that the system can quote from several carriers simultaneously and compare results.

- **Organization-specific configuration** — somewhere in the diagram, indicate that the validation rules, extraction schemas, and quoting providers are configurable per organization. An annotation or side panel showing "Per-Org Config: underwriting rules, LOB schemas, carrier integrations."

- **Stats comparison** at the bottom: "Manual: Days per submission, spreadsheet tracking, missed deadlines" vs "With Indemn: Minutes to extract, automated validation, multi-carrier quotes"

**Brand guidelines:**
- **Color palette**: Iris (primary purple), Lilac (lighter purple), Eggplant (dark purple).
- **Font**: Barlow
- **Style**: Match previous diagrams — rounded rectangles, purple automation zone, converging inputs, stats comparison at bottom.
- **Do NOT include dark mode CSS.**

**Context on who sees this:**
- Primary audience: MGA operations managers, program administrators, carrier underwriting leadership. These are senior insurance professionals who understand the submission pipeline deeply — use proper terminology (submissions, LOB, ACORD, loss runs, MVRs, binding authority, appetite).
- This page complements the Email Intelligence page — Email Intelligence handles the inbox, Intake Manager handles the pipeline. Some visitors will see both pages.

**What this diagram is NOT:**
- Not a technical architecture diagram (no APIs, databases, or model names).
- Not the same as Email Intelligence — that page covers inbox classification. This page covers the full underwriting pipeline.
- Not limited to email intake — this is channel-agnostic.

**Reference:** Match the visual style of:
- `/Users/home/Repositories/content-system/sites/indemn-blog/public/images/products/email-intelligence-workflow.svg`
- `/Users/home/Repositories/content-system/sites/indemn-blog/public/images/products/document-retrieval-workflow.svg`
