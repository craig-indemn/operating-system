# Content System

AI-powered content creation pipeline for Indemn and personal brands. Transforms voice-based ideas into polished, publishable content through dynamic extraction, iterative drafting, and multi-platform distribution. Lives in a separate repo (`/Users/home/Repositories/content-system`) with skills symlinked to `~/.claude/skills/`.

## Status
Session 2026-03-03. Personal brand publishing presence fully established — Substack + Medium ready.

**Session 2026-03-03:**
- Set up Medium account: medium.com/@notesfromthebuild
- Updated `brands/personal/config.yaml` with Medium URL and username
- Cross-posting workflow confirmed: Substack primary → Medium import via URL (no API — Medium stopped issuing new integration tokens)

**Session 2026-03-02:**
- Established personal brand identity: "Notes from the Build" — builder-in-public newsletter
- Created `brands/personal/voice.md` — excited, curious, technical-but-accessible, first person
- Updated `brands/personal/config.yaml` — bee/hex/amber visual identity, Substack primary platform
- Generated brand assets via `/image-gen`: logo (bee+hexagon+circuit), banner (honeycomb-to-circuit flow), header
- Created Substack publication at notesfromthebuild.substack.com
- Configured Substack: accent color (#d97706), about page written and saved, logo uploaded
- Bio: "Engineer & builder. Building AI systems, software platforms, and whatever the problem needs."

**Blog posts:**
- "Building Evaluations for Conversational Agents" — Published with images and OG thumbnail, live at blog.indemn.ai
- "Agents That Build Agents" — Draft v13, awaiting review or approval

**Next up:**
1. Write and publish first personal post on Substack
2. Wire content-publish skill to handle Substack/Medium publishing (currently only handles git-based Astro deploy)
3. Author reviews "Agents That Build Agents" v13 — approve or further feedback
4. Integrate image-gen into content pipeline skills

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
| Personal brand Substack | Website | notesfromthebuild.substack.com |
| Personal brand voice doc | Doc | content-system/brands/personal/voice.md |
| Personal brand config | Doc | content-system/brands/personal/config.yaml |
| Personal brand Medium | Website | medium.com/@notesfromthebuild |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-23 | [writing-psychology-reference](artifacts/2026-02-23-writing-psychology-reference.md) | Deep research on psychology and craft of writing that grips readers — permanent reference for content system |
| 2026-02-25 | [content-system-architecture](artifacts/content-system-architecture.excalidraw) | Excalidraw diagram of the content pipeline — skills, flow, and integration points ([SVG](artifacts/content-system-architecture.svg)) |

## Decisions
- 2026-03-03: Medium stopped issuing new integration tokens — no API access for new accounts. Cross-posting via Medium's "Import a story" feature using Substack URL (preserves canonical link).
- 2026-03-02: Personal brand is a named newsletter "Notes from the Build", not a personal blog "Craig Certo". People subscribe to ideas, not people.
- 2026-03-02: Substack primary, Medium cross-post with Substack as canonical source. Medium for discovery, Substack owns the relationship.
- 2026-03-02: Visual identity: bee/hexagon/honeycomb + circuit traces. Honey amber (#d97706) is the signature color. Dark charcoal (#1c1917) for brand assets, light backgrounds for reading.
- 2026-03-02: Personal voice is NOT AI-specific — "builder who happens to be building with AI". Content covers software, systems, startups, learning — whatever Craig is building.
- 2026-03-02: Voice tone: excited, curious, technical-but-accessible. "Talking WITH you, not AT you." Assumes intelligent, not knowledgeable.
- 2026-03-02: Bio: "Engineer & builder. Building AI systems, software platforms, and whatever the problem needs."
- 2026-03-02: No official Substack publishing API exists. Unofficial TypeScript/Python libraries use cookie auth (substack.sid). For now, copy-paste publishing; upgrade to API later if volume justifies.
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
