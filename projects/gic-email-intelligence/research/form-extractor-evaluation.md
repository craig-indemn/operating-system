# Form Extractor Evaluation

> Evaluation of Dhruv's form-extractor service for replacing Claude Vision in our PDF extraction pipeline.
> Last updated: 2026-04-02

## Verdict: Use it.

The form extractor works for our USLI PDFs. All key fields extracted via OCR. Eliminates Claude Vision cost entirely.

## Service Details

| Item | Value |
|------|-------|
| Repo | `indemn-ai/form-extractor` (private) |
| Deployed | `devformextractor.indemn.ai` (healthy) |
| Hosting | Railway (likely Dhruv's account) |
| Stack | FastAPI + LLMWhisperer (Unstract OCR) + OpenAI GPT-4o |
| Last pushed | 2026-03-31 |
| Already used by | intake-manager pipeline (document processing step) |

## How It Works

1. Upload PDF via `POST /extract/multiple` with `session_id` and `mode=high_quality`
2. LLMWhisperer OCR converts PDF → text (layout-preserving)
3. Raw text returned immediately in the response `files[].raw_text`
4. Combined text retrievable via `GET /extract/session/{id}/combined`
5. Optionally: `POST /extract/single` or `/extract/multiple/full` runs GPT-4o for structured extraction (has a bug currently — `'ChatOpenAI' object is not callable`)

## OCR Modes

| Mode | Use For | Speed | Cost |
|------|---------|-------|------|
| native_text | Digital PDFs, Word docs | Fastest | Cheapest |
| low_cost | Clean printed scans | Fast | Low |
| high_quality | Handwritten, low-quality scans | Slow | Higher |
| form | Forms, checkboxes, structured layouts | Medium | Medium |
| table | Financial reports, tables | Medium | Medium |

Default for PDFs is `table` mode. Our USLI quote PDFs worked well with default settings.

## Test Results — MGL026M2518

**Customer copy (4 pages, 50KB):**
- Text length: 29,212 chars
- All key fields present: quote number, insured name, premium, limits, agent, address, classification code

**Applicant version (16 pages, 523KB):**
- Text length: 54,780 chars
- All key fields present: TRIPLE J, LLC, Condominiums, 62004, 14325, Miami, 33186, $650, Jorge Yara, Annual

## Integration Plan for GIC Pipeline

**Current (expensive):** PDF → Claude Vision multimodal → structured fields
**New (cheap):** PDF → Form Extractor OCR → raw text → Haiku text prompt → structured fields

### What changes:
1. Replace `extractor.py` (multimodal content blocks) with HTTP call to `devformextractor.indemn.ai/extract/multiple`
2. Pass the OCR raw text to Haiku (not Sonnet, not Vision) with the same extraction prompt
3. Keep the same output format (key_details dict) so downstream code doesn't change

### What doesn't change:
- The extraction prompt/schema
- How extractions are stored in MongoDB
- How the automation agent reads extractions

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/extract/multiple` | OCR multiple files → raw text (what we need) |
| POST | `/extract/single` | OCR + GPT-4o extraction (has bug, don't use) |
| POST | `/extract/multiple/full` | OCR + GPT-4o for multiple files |
| GET | `/extract/session/{id}` | Get all docs in a session |
| GET | `/extract/session/{id}/combined` | Get combined text |
| GET | `/extract/session/{id}/stats` | Session statistics |
| POST | `/extract/check-duplicates` | Dedup check |
| GET | `/health` | Health check |

## Concerns

1. **Hosted on Dhruv's Railway** — not in our project. If it goes down, we can't restart it. Should discuss ownership or self-host eventually.
2. **LLMWhisperer API key** — third-party dependency (Unstract). Need to understand cost and rate limits.
3. **The /extract/single bug** — `'ChatOpenAI' object is not callable`. Not blocking for us (we use /extract/multiple + our own LLM), but worth flagging to Dhruv.

## Changelog

| Date | Update | Source |
|------|--------|--------|
| 2026-04-02 | Initial evaluation — tested with 2 USLI PDFs, confirmed all fields extracted | Direct API testing + repo analysis |
