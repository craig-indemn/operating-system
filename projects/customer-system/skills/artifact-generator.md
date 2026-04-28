# Artifact Generator

You produce stage-appropriate artifacts for customer interactions. The mechanism is the same at every Stage; only the Playbook record changes:

```
(Deal + recent Touchpoints + extracted intelligence + Playbook for Deal.stage + raw source content)
  → JSON proposal-data
  → render via tools/render-proposal.js
  → styled PDF
  → Document entity
  → human review queue
```

At DISCOVERY this is a follow-up email. At DEMO it's a recap. At PROPOSAL it's a styled, customer-ready proposal document. At NEGOTIATION it's a revised proposal. At VERBAL/SIGNED it's a kickoff packet. Same mechanism — different `Playbook.artifact_intent` and a different render target.

This skill currently covers the **PROPOSAL stage** (rendered proposal Document) end-to-end with a reusable HTML template + Node renderer. Other stages will share the same mechanism with different output formats.

## How to Execute

Use the `execute` tool to run `indemn` CLI commands AND the renderer:

```
execute("indemn deal get <id> --depth 2")
execute("indemn proposal get <id> --depth 2")
execute("indemn touchpoint list --data '{\"deal\": \"<deal_id>\"}'")
execute("indemn playbook get <id>")
execute("indemn document create --data '{...}'")
execute("indemn document update <id> --data '{...}'")
execute("indemn proposal transition <id> --to internal_review")
execute("node /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/tools/render-proposal.js --data <json> --out <pdf>")
```

All entity reads return JSON. The renderer writes a PDF to disk.

## Triggers

- Watch: `Touchpoint.created` with `scope: external` and `Deal.stage in [DISCOVERY, DEMO, PROPOSAL, NEGOTIATION]`
- Watch: `Touchpoint.transitioned` to `processed` (full intelligence available)
- Watch: `Deal.transitioned` to `proposal` or `negotiation` (new artifact opportunity)

## Procedure

### Step 1 — Resolve the Playbook

Look up the Playbook record for `Deal.stage` at the touchpoint date:

```
indemn playbook list --data '{"stage": "<deal.stage>"}'
```

Read its `artifact_intent` field. This is the spec for what to render. If the Playbook for this stage doesn't exist yet, fail to `needs_review` — humans add a Playbook record before retry.

### Step 2 — Gather inputs from the entity graph

For the customer (resolve via `Touchpoint.deal.company`):

- **Company** + Contacts (decision_maker, day-to-day, champion roles)
- **Deal** with `next_step`, `stage`, recent activity
- **Touchpoints** since the prior artifact for this Deal (or all if first)
- **Extracted intelligence** linked to those Touchpoints: Decisions, Commitments, Signals, Tasks
- **Operations** + **Opportunities** + **CustomerSystem** linked to the Company
- **Proposal** entity (and Phases) for this Deal — at PROPOSAL stage this is the destination; at earlier stages it's the spine being hydrated
- **Prior Documents**: the v1 proposal text (if revising); the Capability Document or analytical artifacts; example proposals from Cam's portfolio
- **Raw source content** when needed: read Touchpoint.source_entity_id (Option B) to pull Meeting transcripts or Email bodies for voice and texture

Use `--depth 2` or `--depth 3` on `indemn deal get` and `indemn company get --include-related` to pull the constellation in one read.

### Step 3 — Compose the proposal-data JSON

Build a JSON payload conforming to the schema below. The JSON cleanly separates **content** (your responsibility) from **presentation** (the template's responsibility).

#### JSON shape

```jsonc
{
  "customer": {
    "name": "Alliance Insurance Services",
    "city_state": "Winston-Salem, NC",
    "decision_maker": "Christopher Cook, CEO"
  },
  "proposal": {
    "title": "Strategic Partnership Proposal v2: Renewal Stewardship as Your Wedge",
    "date": "April 27, 2026",
    "supersedes": "February 11, 2026 Strategic Partnership Proposal: Your Digital Workforce Roadmap",
    "version": 2
  },
  "sections": [
    /* Ordered. Each section has a `type` controlling its rendering. */

    { "type": "framing",
      "heading": "Why This Version",
      "paragraphs": ["...", "..."],
      "bullets": ["...", "..."]
    },

    { "type": "anchor",
      "heading": "What We're Solving — Grounded in Your Data",
      "paragraphs": ["..."],
      "stats_heading": "Your operational reality, by the numbers:",
      "stats": ["<strong>9,516 accounts</strong> across personal + commercial lines", "..."],
      "context_heading": "Where the renewal/rate-review work fits:",
      "context_bullets": ["..."],
      "closing": "Christopher, this is what you described in your April 7 note: ..."
    },

    { "type": "phase",
      "start_new_page": true,                // optional, forces page break before
      "heading": "The Three-Phase Roadmap",  // optional, only on the first phase
      "phase_number": 1,
      "name": "The Wedge — Retention Associate (Compound)",
      "timeline": "Months 1-2",
      "pricing": "$2,500/month, month-to-month",
      "tagline": "The Retention Associate isn't a single bot. It's a <em>compound outcome</em> ...",
      "what_it_does_heading": "Specifically:",
      "what_it_does": ["<strong>Inbox Associate skill</strong> — ...", "..."],
      "outcomes_heading": "What it does on Day 1:",
      "outcomes": ["...", "..."],
      "what_we_need_heading": "What we need from Alliance to make Phase 1 work",
      "what_we_need_paragraphs": ["...", "..."],
      "what_we_need_bullets": ["..."],
      "what_we_deliver_heading": "What we deliver in Phase 1",
      "what_we_deliver_table": {
        "columns": ["Week", "Indemn", "Alliance"],
        "rows": [["Week 1", "...", "..."], ...]
      }
    },

    { "type": "table",
      "start_new_page": true,
      "heading": "Implementation Roles & Commitment",
      "columns": ["Milestone", "Alliance Commitment", "Indemn Responsibility"],
      "rows": [["Week 1: Phase 1 Setup", "...", "..."], ...]
    },

    { "type": "guardrails",
      "heading": "Operational Guardrails (Same as v1)",
      "items": ["<strong>Human-in-the-Loop:</strong> ...", "..."]
    },

    { "type": "investment_summary",
      "heading": "Investment Summary",
      "columns": ["Phase", "Core Outcome", "Terms", "Monthly Investment"],
      "rows": [["1 — Retention Associate (compound)", "...", "Month-to-month", "$2,500"], ...]
    },

    { "type": "next_steps",
      "heading": "Next Steps",
      "items": ["<strong>Approve Phase 1</strong> — ...", "..."],
      "closing": "We'd like to ship Phase 1 outputs to your team within 14 days of authorization."
    }
  ],
  "saas_agreement": { "include": true },
  "signatures": { "customer_label": "For Alliance Insurance Services" }
}
```

#### Section-type reference

| `type` | When to use | Required fields |
|---|---|---|
| `framing` | Opening framing — "Why this version", executive vision, transition message | `heading`, `paragraphs` |
| `anchor` | Customer-pain anchor with quantified stats — the "grounded in your data" beat | `heading`, `paragraphs` (one or more of `stats`, `context_bullets`) |
| `phase` | Each delivery Phase with timeline, pricing, what-it-does, what-we-need, what-we-deliver | `phase_number`, `name`, `timeline`, `pricing` |
| `table` | Standalone tables (Implementation Roles, etc.) | `heading`, `columns`, `rows` |
| `guardrails` | Operational guardrails / safety nets / commitments to the customer | `heading`, `items` |
| `investment_summary` | The pricing table at the end | `heading`, `columns`, `rows` |
| `next_steps` | Numbered call to action | `heading`, `items` |
| `raw_html` | Escape hatch for one-off custom blocks | `html` |

Inline HTML is allowed in any string field (use `<strong>`, `<em>`, etc.) — Handlebars uses `{{{triple-stash}}}` to render unescaped.

### Step 4 — Render the PDF

```
execute("node tools/render-proposal.js --data artifacts/<date>-<customer>-proposal-v<n>.json --out artifacts/<date>-<customer>-proposal-v<n>.pdf --html artifacts/<date>-<customer>-proposal-v<n>.html")
```

The renderer hydrates the template (`templates/proposal/template.hbs`) with the JSON data, embeds the SaaS Agreement partial, and prints to PDF via headless Chrome (puppeteer-core). The hydrated HTML is saved alongside the PDF for review/debugging.

### Step 5 — Update the Document entity

```
indemn document update <document_id> --data '{
  "name": "<Customer> Insurance Services Proposal v<n> (<descriptor>)",
  "source": "manual_upload",
  "mime_type": "application/pdf",
  "file_size": <byte_count>
}'
```

If the Document doesn't yet exist for this Proposal version, create it first and update `Proposal.source_document` to point at it.

### Step 6 — Transition the Proposal to internal_review

```
indemn proposal transition <proposal_id> --to internal_review --reason "Styled v<n> rendered to PDF for human review"
```

### Step 7 — Mark the touchpoint processed

```
indemn touchpoint transition <touchpoint_id> --to processed
```

## Style guidelines (from Cam's proposal portfolio)

The template encodes Cam's visual conventions; your job is the content. These guidelines shape strong proposal *content*. **They were earned through iteration on the Alliance v2 — early drafts were "word vomit" with stat dumps, direct address to the customer, and v1/v2 comparisons. Cam's portfolio is concise.**

1. **Match Cam's section-per-page rhythm.** Cam's v1 is 9 pages: Cover / Unlocking Revenue Capacity / Addressing the Implementation Gap / Three-Phase Roadmap / Implementation Timeline / Implementation Roles & Commitment + Operational Guardrails / Investment Summary + Next Steps / SaaS Agreement / Acceptance & Authorization. Each of the first 5 body sections gets its own page. Use `start_new_page: true` on each major section in the JSON.

2. **Brevity beats completeness.** Cam's "Unlocking Revenue Capacity" is TWO short paragraphs (~80 words). Each Phase: name + Focus line + 3 bullets (Capability / Outcome / Investment). Resist the urge to add stats lists, sub-headings, "What it does on Day 1" detail blocks, or "What we need from Alliance" sub-sections inside a phase. If the content doesn't fit on one page per section, cut it.

3. **No direct address to the customer.** Cam's proposals don't say "Christopher, this is what you described in your April 7 note." They speak about the customer in the third person: "Alliance Insurance manages a book of...". Direct address feels chatty and breaks the formal tone of the portfolio.

4. **No v1/v2 comparison framing.** Cam's proposals don't explain why this version is different from a previous one. The cover's "Supersedes" line tells the customer it's a follow-up. The opening framing should stand on its own. Drop "Why This Version" sections.

5. **Anchor on customer data — but sparingly.** Quantified claims trace to OS entities (Operations, Signals, Capability Document, Peter's data validation). The Alliance v2 opens with "9,516 accounts / 16,744 policies / 3,946 renewing in next 90 days" — three numbers integrated into a sentence. Don't dump 8-bullet stat lists.

6. **Phase-first sequencing matches the customer's most visceral pain.** Alliance v1 led with Lead Capture (missed calls). Alliance v2 leads with Renewal Stewardship (Christopher's proactive ask). The lead Phase is the wedge — choose it from the most-recent-and-most-resonant Decision or Signal.

7. **Specific names beat generic capabilities.** Use the customer's actual carriers, systems, and people. "BT Core Connected App OAuth" not "data integration." "Brian and the AI Roundtable" not "stakeholders." Cam's templates cite Producer names, AMS names, even specific carrier exits.

8. **Compound outcomes over single bots.** Where multiple AssociateTypes deploy together for one Phase outcome, name the compound (e.g., "Retention Associate compound = Inbox + Knowledge + custom skills"). Preserve framing from source Decisions.

9. **Three-phase rhythm: WEDGE / WALK / RUN.** Use Cam's actual phase-name convention (CRAWL/WALK/RUN or WEDGE/WALK/RUN). Phase 1 is month-to-month, narrow, fast. Phase 2 expands. Phase 3 commits longer-term. Each phase: ~5 lines max in the Three-Phase Roadmap section.

10. **Implementation Timeline is its own section.** Days 1–7 / Days 8–30 / Days 31–60 (matching Cam's v1 page 5). 1 short paragraph + 3 bullets per timeline phase.

11. **Implementation Roles & Commitment table is week-by-week.** Each row pairs an Alliance Commitment with an Indemn Responsibility. Concrete, not aspirational. 4-6 rows max.

12. **Operational Guardrails as a sub-section under Implementation Roles** — never its own section, never page-break-before. 3-4 bullets, brief.

13. **Investment Summary closes with the financial picture.** Phase / Core Outcome / Terms / Monthly Investment. Three rows. Bold the dollar values.

14. **Next Steps are 2-3 bullets, no inline labels.** Cam's bullets are simple imperatives: "Approve this roadmap to begin the Phase 1 configuration." Not "**Approve Phase 1** — sign and we begin..."

15. **SaaS Agreement is identical across customers.** Don't customize; the template includes the standard 8-section partial. Title is centered + ALL CAPS.

## Template + tooling location

```
projects/customer-system/
  templates/proposal/
    template.hbs                  # Master HTML structure (cover + sections + signature)
    template.css                  # Brand styling (Barlow, eggplant, iris/lilac swoosh)
    saas-agreement.partial.hbs    # Standard SaaS Agreement (8 sections, identical across customers)
    assets/
      indemn-logo-iris.png        # Logo (renders in puppeteer footer-template)
      Barlow-{Regular,Medium,SemiBold,Bold}.ttf
  tools/
    render-proposal.js            # The renderer (puppeteer-core + handlebars)
    package.json
```

To update brand styling globally (font, color, swoosh placement, page margins): edit `template.css`. All future proposals pick up the change on next render.

To update the SaaS Agreement: edit `saas-agreement.partial.hbs`. All future proposals pick up the change on next render. Existing PDFs are not regenerated automatically — re-render explicitly when the agreement changes.

To add a new section type: add a Handlebars block in `template.hbs` keyed on a new `type` value, add CSS for the new structure, document in the Section-type reference above.

## Output convention

| File | Path |
|---|---|
| Source data (JSON) | `artifacts/<date>-<customer>-proposal-v<n>.json` |
| Hydrated HTML (intermediate) | `artifacts/<date>-<customer>-proposal-v<n>.html` |
| Rendered PDF (deliverable) | `artifacts/<date>-<customer>-proposal-v<n>.pdf` |
| OS Document entity | `Proposal.source_document` → Document with `mime_type: application/pdf`, `file_size: <bytes>` |

The JSON IS the proposal. Re-rendering from the same JSON produces the same PDF. Iterate by editing the JSON and re-running the renderer; never edit the PDF directly.

## When in doubt

- If the entity graph is missing data the Playbook's `artifact_intent` calls for, fail to `needs_review` rather than fabricating. Surface the gap in `Touchpoint.notes` so a human can fill it in.
- If the Playbook for this stage has no `artifact_intent` yet, fail to `needs_review` and flag for Playbook hydration (Phase B3 in roadmap).
- If the rendered output looks wrong (bad page breaks, missing sections, broken table), inspect the hydrated HTML at `artifacts/<...>.html` first — it'll show whether the issue is in the JSON, the template, or the CSS.

## Future evolution

- **Per-stage Playbook records** drive different outputs from the same mechanism. DISCOVERY produces a follow-up email (different template + renderer). DEMO produces a recap (similar). PROPOSAL produces this styled PDF. The renderer pattern generalizes — the template/CSS swap per stage.
- **Customer logo on cover**: today text-only (per design Apr 27). When auto-discovery of customer logos is built (Phase B2 hydration), add a `customer.logo_url` field to the JSON and an `<img>` slot in the cover.
- **Rendering as a service**: today this skill executes the renderer inline via `execute()`. Future: the renderer becomes a separate microservice the associate POSTs JSON to and receives a PDF + Document ID back. Same JSON shape; different transport.
- **Versioned templates**: when the template changes substantively (new section types, new visual conventions), version the template directory and let JSON specify which template version produced it. Enables historical re-rendering.

## Reference

- Trace narrative for the v2 Alliance proposal: `artifacts/2026-04-27-alliance-trace.md`
- Substantive draft (markdown form, content-correct): `artifacts/2026-04-27-alliance-proposal-v2.md`
- Source data (JSON for the renderer): `artifacts/2026-04-27-alliance-proposal-v2.json`
- Rendered output: `artifacts/2026-04-27-alliance-proposal-v2.pdf`
- Cam's portfolio (Drive folder reference): `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`
