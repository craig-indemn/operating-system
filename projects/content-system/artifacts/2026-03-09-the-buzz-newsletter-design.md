---
ask: "Design an internal engineering newsletter (The Buzz) for CTO-to-CEO communication"
created: 2026-03-09
workstream: content-system
session: 2026-03-09-a
sources:
  - type: slack
    description: "Kyle-Craig DM thread from 2026-03-07 — Kyle's message about CTO communication, documentation, and the raise"
  - type: operating-system
    description: "Content system architecture, brand configs, React-PDF capabilities, existing pipeline skills"
---

# Design: The Buzz — CTO Engineering Newsletter

**Date:** 2026-03-09
**Status:** Approved — ready for implementation

## Problem

Kyle (CEO) and Craig (engineering lead) need a structured communication channel for engineering perspective. Kyle sees what ships but not *why* decisions are made, how systems connect, or what trade-offs are being accepted. He explicitly asked for architecture decisions, model choices, and system documentation — and said it matters for three audiences: the team, customers, and the raise.

A bullet-point status update doesn't do this. Kyle needs Craig's *perspective* — how he thinks about problems, why he chose approach A over B, and what leverage each decision creates for the company.

### Kyle's Words (Slack, 2026-03-07)

> "Start writing more down. Architecture decisions, why you picked one model over another, how systems connect. Doesn't have to be polished — get it wrong, iterate, ask me questions. I'd rather see five rough docs than zero perfect ones. That documentation is going to matter for the team, for customers, and for the raise. You've got the chops to be CTO. This is how we get there — I need to see you operating in that role, and you need the business context to make the right calls."

## Solution

**The Buzz** — a newspaper-style engineering newsletter delivered weekly on Mondays. Each issue covers what shipped, why, and how it fits the big picture. Rendered as a visually distinct PDF for reading, with a structured markdown source that's Claude Code-compatible for Kyle's AI-assisted workflows.

---

## Newsletter Anatomy

Each issue has three types of content:

### Feature Sections

One per major project or initiative that moved during the week. Each covers:

- **What is it?** — The feature, system, or decision in plain terms
- **Why are we doing it?** — Business context, customer need, strategic motivation
- **Why did we build it this way?** — Architecture decisions, trade-offs considered, alternatives rejected
- **What leverage does it give us?** — Compound value, reuse, positioning, competitive advantage
- **How does it fit the big picture?** — Connection to roadmap, Linear initiatives/milestones, company strategy
- **Who worked on it** — Contributors, collaborators
- **Deep links** — Design docs, PRs, Linear issues, OS project artifacts

Sections can vary in length. Some features warrant two paragraphs. Others — especially complex architecture decisions — may run long because the reasoning matters. The format handles this naturally.

### The Commentary

One or more editorial pieces not tied to a specific feature. Craig's perspective on:

- Technology landscape and trends
- Competitor analysis and positioning
- Papers, blog posts, or talks that informed decisions
- Strategic thinking about the platform's future
- Things Kyle should be thinking about for the raise
- What's important right now in the technology space

This is where Craig shares how he thinks — not just what he built.

### The Backlinks Index

A structured reference section at the bottom of every issue. Every link mentioned in the issue, categorized:

- Design documents and architecture docs
- Pull requests and code references
- Linear issues and milestones
- External articles, papers, competitor links
- OS project artifacts

This is what makes The Buzz Claude Code-compatible. When Kyle drops the markdown into a Claude Code session, every reference resolves to real documentation that Claude can follow and analyze.

---

## The Creation Pipeline

The Buzz follows the content system's guided extraction pattern but with a multi-source aggregation step unique to newsletters.

### Step 1: Gather

The session pulls raw material from tools:

- **Linear** — What shipped, what's in progress, which initiatives/milestones moved
- **Slack** — Key conversations, decisions made async, context from channels
- **OS Projects** — INDEX.md status sections, new artifacts, decisions logged
- **Sessions** — What sessions ran during the week, what they produced
- **Git** — PRs merged, branches active, who contributed

### Step 2: Map

Claude organizes the raw material into candidate feature sections and presents them: "Here's what I found this week. Which of these deserve a section? What am I missing? What's the lead story?"

### Step 3: Extract Per Section

For each feature section Craig selects, Claude asks the five key questions:

1. Why this way? What was the trade-off?
2. What leverage does this give us?
3. What should Kyle understand about this?
4. How does this connect to the bigger picture?
5. What documentation exists that I should link to?

Craig talks through each — voice or text. Claude captures the perspective.

### Step 4: Commentary

Claude asks: "What's on your mind beyond the features? Anything you've been reading, a competitor move, something about the raise, a technology bet you're thinking about?"

### Step 5: Draft & Refine

Same iterative loop as the blog pipeline. Draft, feedback, revise. The voice is different — direct CTO-to-CEO, not public-facing. Iteration continues until Craig approves.

### Step 6: Render & Deliver

Generate both the newspaper PDF and the structured markdown. Craig delivers manually via Slack DM (no automation for now).

---

## Visual Format

### Layout (Newspaper-Style PDF via React-PDF)

- **Masthead** — "The Buzz" with issue number, date, and a one-line tagline summarizing the issue (e.g., "Voice evaluations go live, infrastructure hardens for SOC2")
- **Lead Story** — Full-width top section. The biggest thing that week. Longer treatment, full perspective.
- **Feature Sections** — Two-column layout below the lead. Each feature gets a card-style block with headline, commentary, and metadata sidebar (contributors, Linear links, status).
- **The Commentary** — Full-width section below features. Editorial voice, longer-form. Sections can run long when the topic warrants depth.
- **Backlinks Index** — Structured reference table at the bottom. Every doc, PR, Linear issue, and external article categorized and linked.

### Visual Identity

Inherits from the personal brand's bee/honeycomb system:

- **Accent color:** Honey amber (#d97706)
- **Typography:** Barlow font family (already registered in React-PDF)
- **Motifs:** Honeycomb/hex patterns as subtle background elements
- **Aesthetic:** Clean, editorial, structured. Not flashy — a document worth reading.

More structured and editorial than "Notes from the Build." This is an internal document with a specific purpose.

---

## Brand & Voice

### What The Buzz Is

- Craig's engineering perspective rendered in a format worth reading
- A document that makes Kyle smarter about the technology every week
- An artifact that accumulates into evidence for the raise, the team, and the record
- A gateway into deeper documentation via links

### What The Buzz Is NOT

- Not a status report (that's the bullet list in Slack)
- Not a blog post (no need to hook strangers)
- Not polished corporate comms (Kyle said "get it wrong, iterate")

### Voice

Direct, confident, internal. Craig talking to his business partner. No need to explain what Indemn does — Kyle knows. Shorthand where it makes sense, expansive when working through a complex decision. Assumes intelligent, not knowledgeable (Kyle understands business deeply but needs the technical perspective explained).

### Tone Flexibility

Some sections are two paragraphs. Some run long because Craig is working through reasoning and wants Kyle to follow. The newspaper format handles variable-length sections naturally. The lead story gets room to breathe. Feature cards can be tight.

---

## Dual Output: Human + AI

Every issue produces two artifacts:

### 1. The Newspaper PDF

The visual artifact Kyle reads. Newspaper-style layout, Barlow typography, honey amber accents. Designed to be read as a document — scannable sections, clear hierarchy, editorial feel.

### 2. The Structured Markdown

The machine-readable source with frontmatter metadata, proper links, and structured references. When Kyle drops this into Claude Code:

- Claude can follow links to design docs, PRs, and Linear issues
- Claude can answer questions about specific decisions referenced in the newsletter
- Claude can connect information across issues over time
- The backlinks index gives Claude a map of everything referenced

The markdown is the source of truth. The PDF is rendered from it.

---

## Content System Integration

### Brand Config

New brand in the content system:

```
content-system/brands/the-buzz/
  config.yaml    # Format, distribution, visual identity, completion criteria
  voice.md       # CTO-to-CEO voice definition
```

### Completion Criteria

The Buzz equivalent of The Point + Writing Energy gates:

- Every feature section answers the five questions (what, why, why this way, what leverage, big picture)
- Every feature section links to at least one real artifact (design doc, PR, Linear issue)
- The commentary section has a clear "so what" — why Kyle should care
- The backlinks index is complete — nothing referenced without a link
- It reads like Craig talking, not like a generated report

### State Store

Each issue tracked as a content piece: `piece create --idea {id} --format newsletter --platform slack`. The EA skill sees what's in flight, published, or overdue.

### Drafts Structure

```
content-system/drafts/the-buzz-YYYY-MM-DD/
  extraction.md                    # Raw material from tools + Craig's input
  context.md                       # Session state
  draft-v1.md                      # First assembled draft (markdown)
  draft-v2.md                      # After feedback
  the-buzz-YYYY-MM-DD.pdf          # Rendered newspaper PDF
```

### Skill

A new `/newsletter` skill that knows the Gather → Map → Extract → Commentary → Draft → Render pipeline. Separate from `/content` (blog pipeline) but follows the same content system patterns — extraction, drafting, refinement, publishing.

---

## Rendering Pipeline

### Markdown → PDF via React-PDF

1. Draft markdown has structured frontmatter: date, issue number, tagline, sections with type (lead/feature/commentary), contributor tags, link references
2. Node.js script parses markdown into structured JSON — sections, metadata, links
3. React-PDF components render JSON into newspaper layout
4. Output: PDF in the drafts directory

### Component Library

New React-PDF components in the content system:

| Component | Purpose |
|-----------|---------|
| `BuzzMasthead` | Title, issue number, date, tagline |
| `BuzzLeadStory` | Full-width feature with headline, body, metadata sidebar |
| `BuzzFeatureCard` | Compact feature block for two-column grid |
| `BuzzCommentary` | Full-width editorial section, variable length |
| `BuzzBacklinks` | Categorized reference table |
| `BuzzFooter` | Issue info, "The Buzz — Engineering at Indemn" |

### CLI

```bash
node scripts/render-buzz.js drafts/the-buzz-2026-03-10/draft-v2.md
# → drafts/the-buzz-2026-03-10/the-buzz-2026-03-10.pdf
```

---

## Cadence & Distribution

- **Frequency:** Weekly, delivered Monday (may increase to daily in the future)
- **Relationship to Thursday meetings:** The Buzz lands Monday. Kyle reads it. Thursday meeting becomes informed discussion rather than cold walkthrough.
- **Delivery:** Manual — Craig sends via Slack DM. No automation for now.
- **Future:** Part of "the hive" knowledge system. Issues accumulate into a searchable body of engineering perspective. Backlinks create a web of connected documentation.

---

## Future Evolution

- **Daily cadence** — As the system matures and creation becomes faster, move to daily or as-needed publishing
- **Automated gathering** — The gather step can become increasingly automated as more data flows through the OS
- **Hive integration** — Backlinks connect to the broader knowledge system, making every issue a node in the graph
- **Team expansion** — Other engineers could contribute sections, with Craig as editor
- **Investor-facing versions** — Select issues or compilations could be shared externally for the raise

---

## Key Decisions

- 2026-03-09: Newsletter is called "The Buzz" — fits the bee/honeycomb personal brand identity
- 2026-03-09: Dual output — newspaper PDF for reading + structured markdown for Claude Code compatibility
- 2026-03-09: Creation follows guided extraction like blog posts — Claude facilitates, Craig provides perspective
- 2026-03-09: Delivered manually via Slack DM, no automation for now
- 2026-03-09: Own skill (`/newsletter`), not an extension of `/content`
- 2026-03-09: Rendered via React-PDF with dedicated component library in content-system
- 2026-03-09: Weekly Monday cadence, may go daily in the future
- 2026-03-09: Voice is direct CTO-to-CEO — not a status report, not a blog post, not corporate comms

---

## Implementation Steps

1. **Create brand config** — `brands/the-buzz/config.yaml` + `voice.md` in content-system
2. **Build the `/newsletter` skill** — Gather → Map → Extract → Commentary → Draft → Render pipeline
3. **Build React-PDF components** — Masthead, LeadStory, FeatureCard, Commentary, Backlinks, Footer
4. **Build render script** — `scripts/render-buzz.js` that parses markdown → JSON → PDF
5. **Register format** — Add newsletter to EA registry, state store format list
6. **Create first issue** — Run the pipeline end-to-end for the week of 2026-03-10
7. **Iterate** — Refine the format based on Kyle's feedback after the first few issues
