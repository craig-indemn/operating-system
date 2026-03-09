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
  - type: operating-system
    description: "indemn-observability/tools/ — 4 existing React-PDF CLI generators as implementation template"
---

# Design: The Buzz — CTO Engineering Newsletter

**Date:** 2026-03-09
**Status:** Approved — ready for implementation
**Revision:** 2 (post-review)

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

Sections can vary in length. Some features warrant two paragraphs. Others — especially complex architecture decisions — may run long because the reasoning matters. The format handles this naturally. No artificial cap on issue size — the content dictates the length. Some weeks it's a focused deep-dive on one thing, other weeks it's five features and a commentary.

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

## Markdown Template

The markdown is the source of truth. The PDF is rendered from it. Each issue uses this structure:

```yaml
---
issue: 1
date: 2026-03-10
tagline: "Voice evaluations go live, infrastructure hardens for SOC2"
sections:
  - id: voice-evaluations
    type: lead
    contributors: [craig, dhruv]
    linear: [VOI-42, VOI-38]
    links:
      - label: "Design doc"
        url: "/projects/voice-evaluations/artifacts/2026-03-05-eval-framework-design.md"
      - label: "PR"
        url: "https://github.com/indemn-ai/evaluations/pull/47"
  - id: soc2-hardening
    type: feature
    contributors: [craig]
    linear: [INF-12]
    links:
      - label: "Secrets Manager migration plan"
        url: "/docs/plans/2026-03-01-secrets-migration.md"
  - id: ai-agent-landscape
    type: commentary
    links:
      - label: "Anthropic's agent patterns"
        url: "https://anthropic.com/engineering/building-effective-agents"
---

# Voice Evaluations Go Live

Full suite of voice evaluations incorporated into our evaluation framework...

[Craig's full perspective — runs as long as it needs to. This is the lead story,
rendered full-width at the top of the newspaper layout.]

# SOC2 Infrastructure Hardening

Migration away from raw .env to AWS Secrets Manager and Parameter Store...

[Rendered as a feature card in the two-column grid below the lead.]

# Commentary: The AI Agent Evaluation Landscape

Something I've been reading about this week that's worth sharing...

[Full-width editorial section below the features.]

## Backlinks

| Category | Label | Link |
|----------|-------|------|
| Design doc | Eval framework design | /projects/voice-evaluations/artifacts/2026-03-05-eval-framework-design.md |
| PR | Voice eval implementation | https://github.com/indemn-ai/evaluations/pull/47 |
| Linear | VOI-42: Voice eval framework | https://linear.app/indemn/issue/VOI-42 |
| External | Anthropic agent patterns | https://anthropic.com/engineering/building-effective-agents |
```

**Convention:** Frontmatter `sections` array defines metadata (type, contributors, links). Body headings match sections by order. The parser maps them 1:1. Section IDs are stable slugs for cross-issue referencing (e.g., `[see Buzz #3: voice-evaluations]`).

**Link format:** Absolute paths for local files (so they resolve when Kyle moves the file). Full URLs for external resources. The backlinks table at the bottom is the canonical index — inline links in the body reference the same destinations.

---

## The Creation Pipeline

Runs from an OS session with `--add-dir` to the content system. The OS is the command center (data gathering via OS skills); the content system is where output lands.

### Step 1: Gather

The session pulls raw material from OS tools. Default time window: last 7 days. Multi-sprint features get context from prior weeks as needed.

- **Linear** — What shipped, what's in progress, which initiatives/milestones moved (`linearis` CLI)
- **Slack** — Key conversations, decisions made async (`slack_client` via Python SDK)
- **OS Projects** — INDEX.md status sections, new artifacts, decisions logged (file reads)
- **Git** — PRs merged, branches active, who contributed (`gh` CLI)

Tracked repos for git scanning (configurable, start with active repos):
- `indemn-ai/bot-service`
- `indemn-ai/indemn-platform-v2`
- `indemn-ai/evaluations`
- `indemn-ai/indemn-observability`
- `indemn-ai/voice-livekit`
- `indemn-ai/web_operators`
- `indemn-ai/operating-system`

### Step 2: Map

Claude organizes raw material into candidate feature sections, ranked by:
- Customer-facing impact
- Strategic significance for the raise
- Connection to active Linear milestones
- Novelty or architectural significance

Presents them: "Here's what I found this week. Which deserve a section? What am I missing? What's the lead story?" Craig decides what goes in and what doesn't.

### Step 3: Extract Per Section

For each feature section Craig selects, Claude asks:

1. Why this way? What was the trade-off?
2. What leverage does this give us?
3. What should Kyle understand about this?
4. How does this connect to the bigger picture?
5. What are the honest constraints — technical debt accepted, risks, things we're worried about?
6. What documentation exists that I should link to?

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

The Buzz has its own visual identity — distinct from both the Indemn corporate blog and the personal "Notes from the Build" newsletter:

- **Accent color:** Honey amber (#d97706)
- **Typography:** Barlow font family
- **Motifs:** Honeycomb/hex patterns as subtle background elements
- **Aesthetic:** Clean, editorial, structured. Not flashy — a document worth reading.

---

## Brand & Voice

### What The Buzz Is

- Craig's engineering perspective rendered in a format worth reading
- A document that makes Kyle smarter about the technology every week
- An artifact that accumulates into evidence for the raise, the team, and the record
- A gateway into deeper documentation via links
- Source material that can be repurposed for investor decks, team onboarding, and customer case studies via `/content-repurpose`

### What The Buzz Is NOT

- Not a status report (that's the bullet list in Slack)
- Not a blog post (no need to hook strangers)
- Not polished corporate comms (Kyle said "get it wrong, iterate")

### Voice

Direct, confident, internal. Craig talking to his business partner. No need to explain what Indemn does — Kyle knows. Shorthand where it makes sense, expansive when working through a complex decision. Assumes intelligent, not knowledgeable (Kyle understands business deeply but needs the technical perspective explained).

### Voice Calibration

The same information rendered in three wrong voices and the right one:

**Status report (wrong):** "Voice evaluations shipped this week. Tests pass. Coverage at 85%."

**Blog post (wrong):** "We needed to know if our voice agents were actually good. Not 'the demo worked' good — production good. So we built something..."

**Corporate comms (wrong):** "Indemn is pleased to announce the release of our comprehensive voice evaluation framework, enabling real-time quality assessment across all voice agent deployments."

**The Buzz (right):** "Voice evaluations are live. The bet here is that real-time eval scoring during conversations — not post-hoc batch analysis — is what unlocks agent autonomy. We chose Langfuse over building custom because their OTLP trace pipeline already handles the volume, and we can focus on the scoring logic instead of the plumbing. Dhruv and I went back and forth on whether to evaluate at the utterance level or the conversation level — we landed on both, with conversation-level being the default for the dashboard. The leverage: once we trust the scores, we can close the loop and let agents self-improve. That's the flywheel."

### Tone Flexibility

Some sections are two paragraphs. Some run long because Craig is working through reasoning and wants Kyle to follow. The newspaper format handles variable-length sections naturally. The lead story gets room to breathe. Feature cards can be tight.

### Three Audiences

Kyle said documentation matters for the team, customers, and the raise. The Buzz is written CTO-to-CEO, but feature sections are structured so they can be extracted into:
- **Investor decks** — The "what leverage" and "big picture" answers map directly to strategic narrative
- **Customer case studies** — The "why this way" and "what it does" answers describe capabilities
- **Team onboarding** — The "architecture decisions" and deep links provide technical context

This repurposing happens via `/content-repurpose` on demand — The Buzz itself stays in Craig's natural voice.

---

## Dual Output: Human + AI

Every issue produces two artifacts:

### 1. The Newspaper PDF

The visual artifact Kyle reads. Newspaper-style layout, Barlow typography, honey amber accents. Designed to be read as a document — scannable sections, clear hierarchy, editorial feel.

### 2. The Structured Markdown

The machine-readable source with frontmatter metadata, proper links, and structured references. When Kyle drops this into Claude Code:

- Claude can follow links to design docs, PRs, and Linear issues
- Claude can answer questions about specific decisions referenced in the newsletter
- Claude can connect information across issues over time using stable section IDs
- The backlinks index gives Claude a map of everything referenced
- Cross-issue references use the convention `[see Buzz #N: section-id]`

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

| Element | What "Done" Looks Like | Scoring |
|---------|----------------------|---------|
| **The Five Questions** | Every feature section answers: what, why, why this way, what leverage, big picture | Met: all 5 answered. Partial: 3-4 answered. Missing: fewer than 3. |
| **Honest Constraints** | Every feature section includes trade-offs accepted, technical debt, risks, or things we're worried about | Met: specific constraints named. Partial: vague acknowledgment. Missing: everything sounds perfect. |
| **Stakes & Scale** | Feature sections quantify impact where possible — numbers, time saved, capacity unlocked, customers affected | Met: concrete numbers or measurable impact. Partial: qualitative impact only. Missing: no indication of scale. |
| **Deep Links** | Every feature section links to at least one real artifact (design doc, PR, Linear issue) | Met: links resolve to real docs. Partial: links exist but are vague. Missing: no links. |
| **Commentary "So What"** | The commentary section has a clear reason Kyle should care about this topic | Met: clear strategic relevance. Partial: interesting but no connection to Indemn. Missing: no commentary or no point. |
| **Backlinks Complete** | Every reference in the issue appears in the backlinks index | Met: complete index. Missing: orphaned references. |
| **Voice Authenticity** | Uses first person, references specific conversations or decisions, no generic summary language. Reads like Craig wrote it. | Met: sounds like Craig talking. Partial: mostly authentic with some AI-isms. Missing: reads like a generated report. |

### State Store

Each issue tracked as a content piece. The `cs.py` state store needs:
- Add `"slack"` to `PLATFORMS` set
- Update `FORMAT_PLATFORM_MAP["newsletter"]` to include `"slack"`
- Register in EA registry (`skills/ea/registry.yaml`)

```bash
cs piece create --idea {id} --format newsletter --platform slack --brand the-buzz
```

### Drafts Structure

```
content-system/drafts/the-buzz-YYYY-MM-DD/
  extraction.md                    # Raw material from tools + Craig's input
  context.md                       # Session state
  draft-v1.md                      # First assembled draft (markdown)
  draft-v2.md                      # After feedback
  the-buzz-YYYY-MM-DD.pdf          # Rendered newspaper PDF
```

### Published Issues

Published issues archived to `content-system/published/the-buzz/YYYY-MM-DD/` with both the final markdown and PDF. This is the accumulating body of engineering perspective that becomes searchable over time.

### Skill

The `/newsletter` skill lives in the OS at `.claude/skills/newsletter/SKILL.md` — not in the content system. The OS orchestrates (data gathering, extraction, drafting); the content system provides rendering infrastructure and stores output.

The skill knows the Gather → Map → Extract → Commentary → Draft → Render pipeline. Separate from `/content` (blog pipeline) but follows the same content system patterns.

---

## Rendering Pipeline

### Existing Infrastructure

Four working React-PDF CLI generators already exist in `indemn-observability/tools/`:

| Tool | Purpose |
|------|---------|
| `applied-epic-guide` | 5-page branded integration guide |
| `onboarding-guide` | 5-page Outlook/Azure integration guide |
| `demo-summary` | 1-page evaluations demo summary |
| `pitch-slide` | 1-page Series A pitch slide |

All use the same proven pattern:
- `@react-pdf/renderer` v4.3.0 with `renderToBuffer()`
- Barlow fonts registered from filesystem TTF files via `Font.register()`
- CLI execution via `npx tsx generate.tsx [flags]`
- Self-contained Node.js tools, no browser needed

The Buzz renderer follows this exact pattern.

### Markdown → PDF Flow

1. Draft markdown has structured frontmatter (issue metadata, section types, contributors, links)
2. `generate.tsx` parses markdown via `gray-matter` (frontmatter) + `remark` (body AST)
3. Sections matched by order: frontmatter `sections` array maps 1:1 to body headings
4. React-PDF components render each section type into the newspaper layout
5. Output: PDF written to the drafts directory

### Component Library

New React-PDF components for The Buzz:

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
npx tsx generate.tsx drafts/the-buzz-2026-03-10/draft-v2.md
# → drafts/the-buzz-2026-03-10/the-buzz-2026-03-10.pdf
```

Follows the observatory tools pattern: `npx tsx generate.tsx` with flags, `renderToBuffer()` → `writeFileSync()`.

### Assets

Font files and brand assets shared from existing observatory tools or copied to `content-system/tools/the-buzz/assets/`. Honey amber palette and Buzz-specific visual elements defined in the component styles.

---

## Cadence & Distribution

- **Frequency:** Weekly, delivered Monday. Content dictates issue size — no artificial cap.
- **Relationship to Thursday meetings:** The Buzz lands Monday. Kyle reads it. Thursday meeting becomes informed discussion rather than cold walkthrough.
- **Delivery:** Manual — Craig sends via Slack DM. No automation for now.
- **Feedback:** Kyle's reactions and questions tracked in the content system state store. Format iterates based on what he responds to, what he asks about, what he shares with others.
- **Future:** Part of "the hive" knowledge system. Issues accumulate into a searchable body of engineering perspective. Backlinks create a web of connected documentation. Cross-issue references connect themes over time.

---

## Future Evolution

- **Daily cadence** — Shorter format, markdown-only (no PDF), auto-gathered with human confirmation. "The Daily Buzz" vs "The Weekly Buzz" — different format, same brand.
- **Automated gathering** — The gather step becomes increasingly automated as more data flows through the OS
- **Hive integration** — Backlinks connect to the broader knowledge system, making every issue a node in the graph
- **Team expansion** — Other engineers could contribute sections, with Craig as editor
- **Investor-facing repurposing** — Feature sections extracted and polished for investor decks via `/content-repurpose`

---

## Key Decisions

- 2026-03-09: Newsletter is called "The Buzz"
- 2026-03-09: Dual output — newspaper PDF for reading + structured markdown for Claude Code compatibility
- 2026-03-09: Creation follows guided extraction like blog posts — Claude facilitates, Craig provides perspective
- 2026-03-09: Delivered manually via Slack DM, no automation for now
- 2026-03-09: Own skill (`/newsletter`) in the OS, not the content system. OS orchestrates, content system renders and stores.
- 2026-03-09: Rendered via React-PDF following the observatory tools pattern (`npx tsx generate.tsx`, `renderToBuffer()`)
- 2026-03-09: Weekly Monday cadence, content dictates size, may go daily with a lighter format
- 2026-03-09: Voice is direct CTO-to-CEO — not a status report, not a blog post, not corporate comms
- 2026-03-09: The Buzz is its own brand — distinct from both Indemn corporate and personal "Notes from the Build"
- 2026-03-09: Frontmatter for machine metadata, headings for human-readable structure. Parser maps by order.
- 2026-03-09: Kyle's feedback tracked in state store to iterate format over time

---

## Implementation Steps

1. **Create brand config** — `brands/the-buzz/config.yaml` + `voice.md` in content-system
2. **Build the `/newsletter` skill** — SKILL.md in OS at `.claude/skills/newsletter/`, implements Gather → Map → Extract → Commentary → Draft → Render
3. **Update state store** — Add `slack` to platforms, update newsletter format mapping, register in EA registry
4. **Build React-PDF tool** — `content-system/tools/the-buzz/` following observatory pattern: `generate.tsx`, components, assets
5. **Build component library** — Masthead, LeadStory, FeatureCard, Commentary, Backlinks, Footer
6. **Create first issue** — Run the pipeline end-to-end for the week of 2026-03-10
7. **Iterate** — Refine the format based on Kyle's feedback after the first few issues
