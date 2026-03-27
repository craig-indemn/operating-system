---
name: content-showcase
description: Create product showcase pages on blog.indemn.ai — brainstorm messaging, design interactive demos, build with parallel sessions, deploy. Use when the user wants to showcase a product, feature, or capability.
---

# Product Showcase

Create a showcase page on blog.indemn.ai/products/ from concept through deployment. Five phases: Brainstorm → Diagram Prompt → Plan → Parallel Build → Deploy.

**Announce at start:** "Using content-showcase for [product name or topic]"

**Working directory:** The repo root (this is the Astro blog site).

## Existing Infrastructure

The showcase system has 7 base components + 17 custom components across 7 deployed pages. You're adding to a mature system.

### Base Components (`src/components/showcase/`)
Rendered from frontmatter via `[...slug].astro`:
- `ShowcaseHero` — title, tagline, category
- `StatsBanner` — key metrics (rendered AFTER MDX content, before FAQ)
- `FAQ` — accordion with JSON-LD for SEO
- `ShowcaseCTA` — call-to-action with primary/secondary buttons
- `FeatureGrid` — feature cards (optional)
- `TabbedDemo` — tabbed video/image viewer (optional)
- `SetupWalkthrough` — installation steps (optional)

### Reusable Custom Components (import in MDX)
- `OmniChannel` — email/phone/chat channel visualization (dark gradient, full-bleed)
- `IntegrationModes` — standalone/AMS/carrier portal cards (alt-bg)
- `InfinitePages` — master product → branded distribution channels (dark gradient)

### Page Rendering Order
`[...slug].astro` renders: Hero → MDX Content → FeatureGrid → TabbedDemo → StatsBanner → SetupWalkthrough → FAQ → CTA. Custom components go in the MDX body between Hero and StatsBanner.

### Technical Constraints
- **No React** — Astro + vanilla JS only. All interactivity via `<script>` tags.
- **Full-bleed breakout** — custom components inside MDX render in a `showcase-prose` container (`max-width: 900px`). Break out with: `width: 100vw; position: relative; left: 50%; margin-left: -50vw;`
- **Dark bg text override** — global `showcase-prose :global(h2/p)` forces dark text. Dark-background components MUST add `!important` overrides on h2/h3/h4/p for white text.
- **SVG diagrams** — no `@media(prefers-color-scheme:dark)` CSS. The blog is always light mode.
- **pubDate required** — content schema requires `pubDate` in frontmatter.
- **CSS prefix** — every component uses a unique 2-letter prefix (`dr-`, `qb-`, `ci-`, `ei-`, `im-`, `cs-`).

### Existing Pages (reference for patterns)
| Page | Demo Type | Key Pattern |
|------|-----------|-------------|
| `indemn-cli` | Video tabs | TabbedDemo from frontmatter |
| `document-retrieval` | Chat + workflow steps + inbox mock | Step-through with behind-the-scenes |
| `quote-and-bind` | Chat + parameter panel + quote cards | Live form populated by conversation |
| `conversational-intake` | Chat + info panel → dashboard transform | Panel transformation mid-demo |
| `email-intelligence` | Board/kanban + timeline + analysis sub-tabs | Operations dashboard simulation |
| `intake-manager` | Pipeline bar + timeline + tab-based detail | Submission lifecycle with completeness tracking |
| `cross-sell` | Chat + coverage profile phases | Profile analysis with gap detection |
| `member-support` | (page exists, no interactive demo yet) | — |

### Video Demo Reference
For producing animated demo videos (React pages → Playwright recording → Descript assembly → embed), see **`references/video-production.md`**. Covers project setup, design system, animation patterns, recording, trimming, Kling integration, and common mistakes.

---

## Phase 1: Brainstorm

Start an adaptive conversation. Ask questions one at a time. Pull context from codebases, project files, and docs.

**Three things must be resolved:**
1. **Who is this for** — the audience
2. **What's the core message** — the one takeaway
3. **What do we demo** — the interactive experience visitors will see

**Demo design is critical.** Each page has a unique interactive demo. Previous demos include:
- Chat conversations with various left-panel types (workflow steps, parameters, coverage profiles, dashboards)
- Board/kanban views with detail panels
- Pipeline visualizations with completeness tracking
- All use pre-rendered DOM with JS visibility toggling, vanilla JS state machines, and scenario tabs

**Video demos** are a first-class demo type. A page can have an embedded video alongside (or instead of) interactive demos. When brainstorm concludes that a video is the right demo, shift into video production mode — see `references/video-production.md` for the complete playbook covering animated React pages, Playwright recording, ffmpeg trimming, Descript assembly, voiceover scripts, and embedding.

The demo should emerge from the product — don't force a pattern from another page. Think about what visual best tells the story.

**Output:** Strategy summary in the conversation: audience, message, demo design, page sections, scenario outlines.

---

## Phase 2: Diagram Prompt

Write a detailed prompt for the user to paste into Claude.ai to generate a workflow diagram SVG.

**Save to:** `docs/diagram-prompts/YYYY-MM-DD-<slug>-diagram-prompt.md`

**The prompt must include:**
- Full workflow steps with descriptions
- What to emphasize visually (automation zone, branching points, human-in-the-loop)
- Brand guidelines (Iris/Lilac/Eggplant, Barlow font)
- **"Do NOT include dark mode CSS"** — critical, causes rendering issues on the light-mode blog
- Audience context (insurance professionals? general business?)
- Reference to match existing diagram styles

The user builds the diagram in Claude.ai while you plan the build. When they provide the HTML file, extract the SVG: `sed -n '<start>,<end>p' source.html > public/images/products/<slug>-workflow.svg`

---

## Phase 3: Plan

Enter plan mode. Design the full implementation with complete scenario data.

**Standard file split:**
- **Session A** (heavy lift): The interactive demo component (`<Name>Demo.astro`, 1400-2000 lines)
- **Session B** (lighter): Supporting visual components + MDX content page

**The plan MUST include (learned from code reviews):**
- Complete scenario scripts: every message, every field/parameter, every callout with step assignments
- Data attributes: `data-total-steps`, `data-*-step` for special transitions
- HTML structure showing the DOM layout
- State machine functions list
- CSS prefix and keyframe names
- Reset logic (especially for panel transformations or tab state)
- `pubDate` in the MDX frontmatter spec
- Full-bleed breakout on ALL custom components
- `!important` text overrides on dark-bg components

**Run a code-reviewer agent** against the plan before approving. It catches missing scenario data, ARIA collision risks, and architectural issues.

---

## Phase 4: Parallel Build

Launch two sessions on isolated worktrees:

**Session A prompt must include:**
- Reference to the plan file
- Instruction to read the primary pattern reference (the most similar existing demo)
- Instruction to read `src/styles/global.css` for CSS variables
- Complete scenario data (or reference to plan)
- All special behavior (panel transforms, sub-tabs, new callout types, etc.)
- Verification step: create temp test page, build, delete

**Session B prompt must include:**
- Reference to the plan file
- MDX structure reference (`src/content/products/<existing>.mdx`)
- Component pattern references (OmniChannel for dark bg, IntegrationModes for cards)
- `pubDate` reminder
- JSX comments only (not HTML comments in MDX)
- Full-bleed breakout requirement on all components
- `!important` text overrides on dark-bg components

**Integration after both complete:**
1. Verify all files exist in the repo
2. Wire in workflow diagram SVG (if available)
3. `npx astro build` — zero errors
4. `npx astro preview` — visual review
5. Commit, push to main (Vercel auto-deploys on merge)

---

## Phase 5: Deploy & Close

1. `git add <files> && git commit -m "Add <product> showcase page"`
2. `git push origin main`
3. `vercel --prod` to deploy to blog.indemn.ai
4. Verify live page at `https://blog.indemn.ai/products/<slug>/`

---

## Key Principles

- **Every product is different.** Don't copy another page's demo structure. Design the visual that best tells THIS product's story.
- **The demo is the centerpiece.** Messaging supports the demo, not the other way around.
- **Complete scenario data in the plan.** Reviewers consistently flag missing data as the #1 issue. Write every message, every field, every callout before building.
- **Parallel sessions work.** The A/B split (demo vs supporting) has no integration issues when the interface contract is clear (component name, import path, no props).
- **Plan review catches real issues.** Always run a code-reviewer agent before approving the plan.
- **Reuse components.** OmniChannel, IntegrationModes, and InfinitePages are battle-tested. Import them in MDX rather than rebuilding.
- **Brand consistency.** Iris/Lilac/Eggplant palette, Barlow font. No dark mode in SVGs. `!important` on dark-bg text.
