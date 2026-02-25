# Content System

AI-powered content creation pipeline for Indemn and personal brands. Transforms voice-based ideas into polished, publishable content through dynamic extraction, iterative drafting, and multi-platform distribution. Lives in a separate repo (`/Users/home/Repositories/content-system`) with skills symlinked to `~/.claude/skills/`.

## Status
Session 2026-02-25-e complete. Blog OG thumbnails fixed, homepage card layout added.

**Blog site improvements (this session):**
- Fixed Open Graph meta tags — Slack/social unfurls now show Indemn branding instead of Astro stock placeholder
- Generated branded default OG card (Indemn logo on navy background) via `/image-gen` with logo as reference
- Added `heroImage` to blog post frontmatter + fixed `BlogPost.astro` to pass it to `BaseHead` for `og:image`
- Homepage now shows post thumbnails in card layout (image on top, text below)
- Fixed hero image overlap on blog post pages (removed `translateY(-1rem)`)

**Blog posts:**
- "Building Evaluations for Conversational Agents" — Published with images and OG thumbnail, live at blog.indemn.ai
- "Agents That Build Agents" — Draft v13, awaiting review or approval

**Next up:**
1. Author reviews "Agents That Build Agents" v13 — approve or further feedback
2. Generate images for "Agents That Build Agents" when approved
3. Integrate image-gen into content pipeline skills (content-draft, content-publish) so images are generated during drafting

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Content system repo | GitHub repo | /Users/home/Repositories/content-system |
| Indemn blog | Website | blog.indemn.ai |
| Design spec | Doc | content-system/docs/plans/2026-01-30-blog-content-system-design.md |
| System knowledge | Doc | content-system/docs/system-knowledge.md |
| Writing psychology | Doc | content-system/docs/writing-psychology.md |
| Orchestration layer design | Doc | content-system/docs/plans/2026-02-08-orchestration-layer-design.md |
| Master System Prompt (v2026.1) | Google Doc | gog docs cat 1lowazd0cvnX45M3nWP0bzKCZ2IA9G79_NNmmToxYIQM |
| Marketing Material Persona Prompt | Google Doc | gog docs cat 1ibuNPLYOpID063UJpJhVbXwY91mniNvv0SeNnoYscYI |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-23 | [writing-psychology-reference](artifacts/2026-02-23-writing-psychology-reference.md) | Deep research on psychology and craft of writing that grips readers — permanent reference for content system |
| 2026-02-25 | [content-system-architecture](artifacts/content-system-architecture.excalidraw) | Excalidraw diagram of the content pipeline — skills, flow, and integration points ([SVG](artifacts/content-system-architecture.svg)) |

## Decisions
- 2026-02-25: Image generation skill is a general OS tool skill, not content-system-specific. Brand context injected by the caller (content pipeline skills), not the image-gen skill itself.
- 2026-02-25: Nano Banana (gemini-2.5-flash-image) is the default model — fast, reliable, GA. Nano Banana Pro (gemini-3-pro-image-preview) is unreliable in preview, skip for now.
- 2026-02-25: Gemini API free tier has zero image quota — billing required on Google AI Studio.
- 2026-02-23: Content system stays as a separate repo for now; OS project tracks the work and context
- 2026-02-23: Extraction skill should pull from internal sources (Drive, Slack, meetings) before asking the author to repeat information
- 2026-02-23: Context window management matters — drafting should start in a fresh session with brand docs pre-loaded
- 2026-02-23: Brand voice is a single distilled `voice.md` per brand, not YAML guardrails with enforcement logic. Skills read it as context and write in voice naturally. Source Google Docs stay in `references/` for refresh.
- 2026-02-23: Pattern is multi-brand — any brand can have a `voice.md`. Indemn is first implementation.
- 2026-02-25: Evaluations blog post required fresh extraction — original predated The Point/Writing Energy system. Extraction from existing drafts + codebase exploration works well.
- 2026-02-25: "Too dramatic" feedback on Agents post → same writing psychology techniques work at lower intensity. Grounded confidence > manifesto energy for practitioner pieces.
- 2026-02-25: Vercel auto-deploy not connected to content-system repo — requires manual `vercel --prod` from `sites/indemn-blog/`.
- 2026-02-25: Gemini ignores aspect ratio in prompt text — must use `generationConfig.imageConfig.aspectRatio` (e.g., `"16:9"`). Produces native 1344x768.
- 2026-02-25: Always auto-crop generated images before deploying to web — Gemini leaves large white margins around content. Use Pillow with threshold=245.
- 2026-02-25: Excalidraw diagrams use CLI-based rendering (`excalidraw-to-svg` via jsdom), not MCP. Fits OS CLI-first philosophy. Bound text renders via custom post-processing in render.js.
- 2026-02-25: `@excalidraw/utils` must be pinned to `0.1.2` — newer versions changed file structure and break `excalidraw-to-svg`.
- 2026-02-25: Blog posts need `heroImage` in frontmatter pointing to `src/assets/images/` for OG thumbnails. Images in `public/images/` work for inline markdown but not for Astro's `image()` schema helper.
- 2026-02-25: Default blog OG image generated with `/image-gen` using Indemn logo PNG as reference input to Gemini. Replaces Astro stock placeholder.
- 2026-02-25: `BlogPost.astro` must pass `image={heroImage}` to `BaseHead` — was missing, causing all posts to fall back to default OG image.

## Open Questions
- The content-extract skill's "dynamic interview" should know to search internal sources — how to teach it that without bloating the skill?
- Should we set up Vercel git integration for the content-system repo to enable auto-deploy on push?
- The Astro build shows "Duplicate id" warnings — investigate content collection config
