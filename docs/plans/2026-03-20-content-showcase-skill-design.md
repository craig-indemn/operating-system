# Design: Content Showcase Skill

**Date:** 2026-03-20
**Status:** Approved

## Problem

We built a product showcase system on blog.indemn.ai/products/ with 7 reusable Astro components, a products content collection, and a ShowcaseLayout. The first page (Indemn CLI & MCP Server) was built manually over two sessions. Creating the next showcase page should be a guided, repeatable workflow — not ad hoc.

## What the Skill Does

`/content-showcase` guides the creation of a product showcase page from concept through deployed page. It's an orchestrator — it drives the conversation, makes decisions, produces content, builds demos, assembles the page, and deploys. Single-session workflow.

## Phases

### Phase 1: Brainstorm

Adaptive conversation to understand the product and shape the page. Asks questions one at a time, follows the conversation where it goes, pulls context from codebases/projects/docs rather than making the user repeat known information.

**Three things must be resolved before moving on:**
1. Who is this for (audience)
2. What's the core message (one takeaway)
3. What do we demo (what the viewer sees in action)

Everything else — features, stats, FAQ, CTA, walkthrough, narrative body — emerges from the conversation and gets included only if it makes sense for the product. The existing components are all conditionally rendered.

The brainstorm also determines what kind of demos the page needs:
- **Screen recording** — capture real usage
- **Diagram/visual** — workflow, architecture, process (Excalidraw, SVG, custom graphics)
- **Interactive embed** — components built into the page
- **Video from visuals** — diagrams/animations turned into video via the video pipeline

Output: a strategy summary capturing all decisions.

### Phase 2: Demo Production

Works through each demo identified in the brainstorm. Does the work directly in-session:

- **Screen recordings** — produces a detailed script (setup requirements, step-by-step sequence, viewer takeaways, duration target), then the user records and drops the file in `public/demos/`
- **Diagrams/visuals** — creates them in-session
- **Interactive embeds** — builds the components in-session
- **Video from visuals** — produces them using the video pipeline

The only hard handoff is screen recording (inherently manual). Everything else the skill does itself.

### Phase 3: Page Assembly

Drafts the MDX file at `src/content/products/<slug>.mdx`. Populates frontmatter based on what emerged from the brainstorm — only sections that make sense for this product.

Presents the page in sections for review (not a full MDX dump). Each section gets approval or feedback before moving on. If new components are needed beyond the existing 7, builds them in-session.

### Phase 4: Review & Deploy

- Builds the site locally to verify rendering
- Walks through the page with the user for final review
- Applies fixes from feedback
- Deploys via `vercel --prod` from `sites/indemn-blog/`
- Updates relevant project INDEX.md

## Existing Infrastructure

**Working directory:** `/Users/home/Repositories/content-system/sites/indemn-blog/`

**Components** (all conditionally rendered — skip any that don't apply):
- `ShowcaseHero` — full-width hero with gradient background
- `FeatureGrid` — feature cards layout
- `TabbedDemo` — tabbed viewer (video, image, or placeholder)
- `StatsBanner` — stats/metrics display
- `SetupWalkthrough` — per-platform installation steps
- `FAQ` — accordion with JSON-LD structured data
- `ShowcaseCTA` — call-to-action section

**Layout:** `ShowcaseLayout.astro` — handles BaseHead, Header, Footer, scroll animations, FAQ JSON-LD

**Routing:** `pages/products/index.astro` + `pages/products/[...slug].astro`

**Content collection schema** (all optional except core fields):
- Core: title, tagline, description, category, pubDate
- Optional: stats, features, demoTabs, walkthrough, faq, cta, heroImage

**Brand:** Iris/Lilac/Eggplant palette, Barlow font, flourish decorations

**Reference page:** `src/content/products/indemn-cli.mdx` — first showcase page, good template for structure

## Skill Location

Lives in content-system repo at `skills/content-showcase/SKILL.md`, symlinked to `~/.claude/skills/content-showcase`.
