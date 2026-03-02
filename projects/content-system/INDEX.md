# Content System

AI-powered content creation pipeline for Indemn and personal brands. Transforms voice-based ideas into polished, publishable content through dynamic extraction, iterative drafting, and multi-platform distribution. Lives in a separate repo (`/Users/home/Repositories/content-system`) with skills symlinked to `~/.claude/skills/`.

## Status
Session 2026-03-02: Context review and personal brand launch planning.

**Previous session (2026-02-25-e):** Excalidraw skill built, blog OG thumbnails fixed, homepage card layout added.

**Indemn blog posts:**
- "Building Evaluations for Conversational Agents" — Published with images and OG thumbnail, live at blog.indemn.ai
- "Agents That Build Agents" — Draft v13, awaiting review or approval

**Personal brand launch — IN PROGRESS:**
Craig is setting up his personal publishing presence. The content system has `brands/personal/config.yaml` configured with Substack as primary (`craigcerto.substack.com`), Medium and LinkedIn as cross-post channels. But the actual accounts/platforms haven't been created yet and the brand identity needs to be thought through before launch.

**Decisions needed before launch:**
1. **Brand identity** — Does "Craig Certo" work as the brand, or use a nickname / pen name / brand name? This affects account names across all platforms.
2. **Platform setup** — Which platforms to create accounts on now vs later? Current config assumes Substack (primary), Medium (cross-post), LinkedIn (cross-post). Also consider: Beehiiv (newsletter alternative to Substack), X/Twitter, personal blog site.
3. **Newsletter strategy** — What's the newsletter about? Frequency? Free vs paid tiers? What's the value prop for subscribers?
4. **Visual brand** — The config has colors (blue/purple/amber) and typography (Inter) but no logo, no header image, no visual identity beyond that.
5. **Voice doc** — Indemn has a `voice.md` sourced from Google Docs. Personal brand needs one too. The config has tone guidelines ("personal, technical, direct — Engineer sharing what actually works") but no full voice doc.
6. **First content** — What's the inaugural post? Sets the tone for everything that follows.

**Next up:**
1. Start a dedicated session to work through brand identity and platform decisions
2. Create accounts on chosen platforms
3. Build out `brands/personal/voice.md`
4. Update `brands/personal/config.yaml` with final platform decisions
5. Write and publish first personal brand piece
6. Also still pending: review "Agents That Build Agents" v13 for Indemn blog

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
- **Personal brand name/handle** — "Craig Certo" or something else? Affects all platform account names.
- **Substack vs Beehiiv** — Config currently says Substack. Beehiiv has better analytics and monetization. Worth evaluating before committing.
- **Platform scope** — How many platforms to set up at launch vs grow into? Risk of spreading too thin vs building cross-platform presence early.
- **Newsletter angle** — Pure technical writing? AI engineering focus? Broader "building and shipping" theme? Needs to be specific enough to attract subscribers but broad enough to sustain.
- The content-extract skill's "dynamic interview" should know to search internal sources — how to teach it that without bloating the skill?
- Should we set up Vercel git integration for the content-system repo to enable auto-deploy on push?
- The Astro build shows "Duplicate id" warnings — investigate content collection config
