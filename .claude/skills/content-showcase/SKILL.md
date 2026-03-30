---
name: content-showcase
description: Create outcome showcase pages on blog.indemn.ai — brainstorm messaging, design interactive demos and/or video demos, build with parallel sessions, deploy. Use when the user wants to showcase a product, feature, or capability.
---

# Outcome Showcase

Create an outcome page on blog.indemn.ai/outcomes/ from concept through deployment. Five phases: Brainstorm → Diagram Prompt → Plan → Parallel Build → Deploy.

**Announce at start:** "Using content-showcase for [outcome name or topic]"

**Working directory:** The blog repo (engineering-blog at `/tmp/engineering-blog-sync/` or the local clone).

**Brand alignment:** ALWAYS read `projects/content-system/artifacts/2026-03-27-brand-alignment-reference.md` before creating or updating any page. It has the Four Outcomes categories, lexicon rules (banned/required words), Associate marketing names, proof points, messaging principles, and a pre-publish checklist.

## Existing Infrastructure

The showcase system has 7 base components across 11 deployed outcome pages. Content collection is `outcomes` (was `products`). Routes are `/outcomes/<slug>/`.

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
- **Category must be one of:** Revenue Growth, Operational Efficiency, Client Retention, Strategic Control
- **Lexicon:** "Associate" not "agent/bot/chatbot", "capability" not "tool/software", "partner" not "vendor". See brand alignment reference for full list.

### Existing Pages
| Slug | Category | Demo Type | Has Video |
|------|----------|-----------|-----------|
| `submission-automation` | Operational Efficiency | Pipeline + interactive demo | Yes |
| `web-operators` | Operational Efficiency | — | Yes |
| `email-intelligence` | Operational Efficiency | Board/kanban + interactive demo | Yes |
| `quote-and-bind` | Revenue Growth | Chat + parameter panel + quote cards | Yes |
| `claims-intake` | Operational Efficiency | — | Yes |
| `conversational-intake` | Operational Efficiency | Chat + info panel → dashboard | No |
| `document-retrieval` | Operational Efficiency | Chat + workflow steps + inbox mock | No |
| `cross-sell` | Revenue Growth | Chat + coverage profile phases | No |
| `member-support` | Client Retention | Diagram + interactive demo | No |
| `strategy-studio` | Strategic Control | TabbedDemo (video tabs) | No |
| `open-enrollment` | TBD | Placeholder | No |

### Video Demo Reference
For producing animated demo videos (React pages → Playwright recording → Descript assembly → embed), see **`references/video-production.md`**. Covers project setup, design system, animation patterns, recording, trimming, Kling integration, voiceover scripts, and common mistakes.

---

## Phase 1: Brainstorm

Start an adaptive conversation. Ask questions one at a time. Pull context from codebases, project files, and docs.

**Three things must be resolved:**
1. **Who is this for** — the audience
2. **What's the core message** — the one takeaway
3. **What do we demo** — the experience visitors will see (interactive, video, or both)

**Demo types:**
- **Interactive demos** — pre-rendered DOM with JS visibility toggling, vanilla JS state machines, scenario tabs. Best for showing workflows the visitor can explore.
- **Video demos** — animated React pages recorded with Playwright, assembled in Descript with music/VO. Best for showing end-to-end flows, voice calls, pipeline animations. See `references/video-production.md`.
- **Both** — a page can have an embedded video AND an interactive demo. The video gives the overview, the interactive lets visitors explore.

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

The user builds the diagram in Claude.ai while you plan the build. When they provide the HTML file, extract the SVG: `sed -n '<start>,<end>p' source.html > public/images/outcomes/<slug>-workflow.svg`

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
- MDX structure reference (`src/content/outcomes/<existing>.mdx`)
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

1. `git add <files> && git commit -m "Add <outcome> showcase page"`
2. `git push origin main` (or create PR if branch protection is enabled)
3. `vercel --prod --yes` to deploy to blog.indemn.ai
4. Verify live page at `https://blog.indemn.ai/outcomes/<slug>/`

### Embedding Videos
For pages with video demos:
```html
<video controls playsinline style="width: 100%; border-radius: 12px; margin: 2rem 0; box-shadow: 0 4px 24px rgba(0,0,0,0.12);">
  <source src="/videos/outcomes/<slug>.mp4" type="video/mp4" />
</video>
```
Place video files in `public/videos/outcomes/`. Use `controls` (not `autoplay muted`) so viewers can play/pause and hear audio.

---

## Key Principles

- **Every outcome is different.** Don't copy another page's demo structure. Design the visual that best tells THIS outcome's story.
- **The demo is the centerpiece.** Messaging supports the demo, not the other way around.
- **Complete scenario data in the plan.** Reviewers consistently flag missing data as the #1 issue. Write every message, every field, every callout before building.
- **Parallel sessions work.** The A/B split (demo vs supporting) has no integration issues when the interface contract is clear (component name, import path, no props).
- **Plan review catches real issues.** Always run a code-reviewer agent before approving the plan.
- **Reuse components.** OmniChannel, IntegrationModes, and InfinitePages are battle-tested. Import them in MDX rather than rebuilding.
- **Brand alignment is mandatory.** Read the brand alignment reference before touching any page. Four Outcomes categories, lexicon rules, proof points, partner language.
- **"Associate" never "agent."** The only exception is when referring to human insurance agents/brokers or CLI command syntax.
