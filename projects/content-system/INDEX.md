# Content System

AI-powered content creation pipeline for Indemn and personal brands. Transforms voice-based ideas into polished, publishable content through dynamic extraction, iterative drafting, and multi-platform distribution. Lives in a separate repo (`/Users/home/Repositories/content-system`) with skills symlinked to `~/.claude/skills/`.

## Status
Session 2026-03-26b. Brainstormed InsurtechNY Spring conference demo videos with Craig. Two demos designed: FNOL voice call + Smart Inbox workflow. Full scripts and storyboards in artifact.

**Session 2026-03-26b:**
- Brainstormed conference demo video strategy for InsurtechNY Spring booth at Chelsea Piers
- Read Cam's Slack messages and "Webmap - Four Outcomes Navigation" matrix (PDF)
- Mapped all 8 existing showcase pages to Cam's matrix associates
- Evaluated full matrix for voice and web chat demo candidates
- Selected two demos: FNOL (Intake Associate for Claims, voice) + Smart Inbox (Inbox Associate, web workflow)
- Wrote full storyboard and script for both videos (4-act structure each)
- FNOL: personal lines auto claim, phone call with captions, behind-the-scenes reveal
- Smart Inbox: fly-on-the-wall pipeline view, zoom-in/zoom-out on email processing, AMS integration ("no API required"), auto-send toggle
- Identified Option 3 upgrade path: AI video associate avatar for FNOL (booth-stopper version, held for Cam/Kyle feedback)
- Identified future alignment work: rename showcase pages to match matrix language (separate effort)

**Next up:**
1. Produce FNOL demo video (decide production method, build assets, assemble)
2. Produce Smart Inbox demo video
3. Show both to Cam/Kyle for feedback
4. Option 3 upgrade (AI avatar FNOL) if they want it
5. Merge PR #14 on indemn-ai/engineering-blog
6. Add Jonathan (and team) to Vercel engineering-blog project
7. Align showcase page names with Cam's outcome matrix (separate effort)
8. Renewals showcase page
9. Evaluation Engine showcase ("Trust, Not Hope")

**Session 2026-03-26:**
- Synced full blog site (8 product showcase pages, 26 components, workflow SVGs, brand assets) to `indemn-ai/engineering-blog` — PR #14 pending merge
- Copied 7 content skills (content-showcase, content, content-draft, content-extract, content-preview, content-publish, content-teammate) to `.claude/skills/` in team repo
- Included Indemn and The Buzz brand configs; excluded personal and career-catalyst brands
- Stripped personal brand references from skills (Substack/Medium cross-posting, personal voice)
- Simplified content-publish skill to Astro/Vercel only (removed copy-paste and cross-platform workflows)
- Wrote team-oriented CLAUDE.md with deployment instructions (`vercel --prod`, manual)
- Also deployed Member Support page (from Jonathan's IVR Replacement spec) in a prior session
- DM'd Jonathan in Slack with repo access instructions and next steps
- Branch protection on engineering-blog requires PR merge — Craig needs to approve PR #14

**Session 2026-03-23:**
- Built and deployed 4 more showcase pages (Conversational Intake, Email Intelligence, Intake Manager, Cross-Sell)
- Conversational Intake: dual-perspective demo with panel transformation (info collection → CSR dashboard), 2 scenarios (after-hours + live handoff), knowledge retrieval indicators, system messages. New components: FormComparison, KnowledgeSection, NotificationChannels
- Email Intelligence: first non-chat demo — board/kanban UI with 3 action queues, email timeline, analysis sub-tabs (Extracted Data, Gap Analysis, Draft). New components: PipelineSteps, DraftIntelligence
- Intake Manager: submission lifecycle demo with pipeline status bar, completeness tracking, event timeline, 4-tab detail view (Business/Coverage/Validation/Quote), multi-carrier quote comparison. New components: MultiEventTimeline, ValidationRules
- Cross-Sell: coverage profile panel with 4-phase transitions (profile → gap detection → recommendation → outcome), new "opportunity" callout type. New component: CoverageGaps (6 common gap types)
- Enhanced `/content-showcase` skill to capture the refined 5-phase workflow and all technical patterns
- Established code-reviewer agent pattern for plan validation before building
- All pages deployed to blog.indemn.ai via `vercel --prod`
- Saved future cross-sell product ideas to memory (book analysis, life event detection)

**Session 2026-03-22:**
- Built Quote & Bind showcase page at `/products/quote-and-bind/` — deployed to blog.indemn.ai
- Audience: MGA principals, program administrators, wholesale brokers with binding authority
- Interactive demo (1,536 lines): 3 scenarios (Event Insurance, Specialty Commercial/Jewelry, Renters), parameter collection panel, stacking callouts, quote cards, policy confirmation
- New components: InfinitePages (branded distribution channels), IntegrationModes (standalone/AMS/carrier portal)
- Reused OmniChannel component from Document Retrieval page
- Craig built workflow diagram SVG in Claude.ai — 4 channels, eligibility branching, human review, system integrations callout
- Fixed dark mode SVG rendering — stripped `prefers-color-scheme:dark` from both diagram SVGs (blog is always light mode)
- Fixed text contrast on dark-background sections — global `showcase-prose :global()` styles were overriding scoped component white text
- Parallel execution: 2 Claude Code sessions (Session A: demo component, Session B: content + supporting components)
- Also deployed Document Retrieval page (was pending deploy from 2026-03-21)

**Session 2026-03-21:**
- Built Document Retrieval showcase page at `/products/document-retrieval/`
- Brainstormed with Craig using Ian's sales call transcript — scoped workflow: email/phone/chat intake → extraction → validation (completeness + identity) → AMS lookup → carrier retrieval (direct or web operator) → draft reply → optional human approval → delivered
- Created interactive demo component (1,839 lines): 3 scenarios (COI, ID Card, Policy Dec Page), mock chat panel, workflow step visualizer, mock Outlook inbox approval, polished mock documents (styled HTML)
- Created OmniChannel component — email/phone/chat visual section with dark gradient
- Craig built workflow diagram SVG in Claude.ai — integrated into page
- Parallel execution: orchestrated 2 Claude Code sessions (Session A: demo component, Session B: content page + OmniChannel)
- All merged to main in content-system repo

**Session 2026-03-20:**
- Designed `/content-showcase` skill — adaptive brainstorm → demo production → page assembly → deploy
- Skill covers full loop: messaging strategy, demo scripting/building (recordings, diagrams, interactives, video), MDX assembly, review, deployment
- Design doc: `operating-system/docs/plans/2026-03-20-content-showcase-skill-design.md`
- Skill lives in content-system repo at `skills/content-showcase/SKILL.md`, symlinked to `~/.claude/skills/`
- Key design decisions: adaptive conversation (not rigid template), demos can be any type (recording, diagram, interactive, video), single-session workflow, skill does the work directly in-session

**Session 2026-03-10:**
- Rewrote "Building Evaluations for Conversational Agents" → "How We Evaluate Conversational AI Agents"
- Replaced dramatic customer-crisis narrative with practical engineer tone
- Added new content: rubric restructuring (18→3-6 rules), four evaluation modes (single-turn, simulated, replay, voice), autonomous improvement loop, real anonymized outcomes
- Generated 3 new Indemn-branded infographic images via `/image-gen` (evaluation dashboard, four modes, improvement loop), kept original hero
- Iterated on evaluation-dashboard image: dark UI mockup → flat vector infographic (Test Scenarios → Scoring Engine → Component Breakdown). User feedback: mockup gave wrong impression of actual product UI
- Ran 8 image-gen prompting experiments, documented ICS framework and best practices in image-gen skill
- Applied tone learnings from The Buzz newsletter tone review — no self-aggrandizing, no mic-drops, let the work speak
- Deployed to blog.indemn.ai via `vercel --prod`
- Used `op read` for Gemini API key (not `op item get --fields` which returns references, not values)

**Session 2026-03-09:**
- Designed "The Buzz" CTO engineering newsletter — see artifact
- Created `/newsletter` skill with tone review step and delivery workflow

**Session 2026-03-03:**
- Set up Medium account: medium.com/@notesfromthebuild
- Cross-posting workflow confirmed: Substack primary → Medium import via URL

**Blog posts:**
- "How We Evaluate Conversational AI Agents" — Rewritten and republished Mar 10, live at blog.indemn.ai
- "Agents That Build Agents" — Draft v13, awaiting review or approval

**Product showcase pages:**
- Indemn CLI & MCP Server — live at blog.indemn.ai/products/indemn-cli/ (deployed 2026-03-19)
- Document Retrieval — live at blog.indemn.ai/products/document-retrieval/ (deployed 2026-03-22)
- Quote & Bind — live at blog.indemn.ai/products/quote-and-bind/ (deployed 2026-03-22)
- Conversational Intake — live at blog.indemn.ai/products/conversational-intake/ (deployed 2026-03-23)
- Email Intelligence — live at blog.indemn.ai/products/email-intelligence/ (deployed 2026-03-23)
- Intake Manager — live at blog.indemn.ai/products/intake-manager/ (deployed 2026-03-23)
- Cross-Sell — live at blog.indemn.ai/products/cross-sell/ (deployed 2026-03-23)
- Member Support — live at blog.indemn.ai/products/member-support/ (deployed 2026-03-24)

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Content system repo | GitHub repo | /Users/home/Repositories/content-system |
| Team blog repo | GitHub repo | indemn-ai/engineering-blog (PR #14 pending) |
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
| 2026-03-09 | [the-buzz-newsletter-design](artifacts/2026-03-09-the-buzz-newsletter-design.md) | Design an internal CTO engineering newsletter (The Buzz) for CEO communication — newspaper-style PDF + structured markdown |
| 2026-03-20 | [content-showcase-skill-design](../../docs/plans/2026-03-20-content-showcase-skill-design.md) | Design a skill for creating product showcase pages — adaptive brainstorm, demo production, page assembly, deployment |
| 2026-03-20 | [document-retrieval-diagram-prompt](artifacts/2026-03-20-document-retrieval-diagram-prompt.md) | Prompt for Claude.ai workflow diagram — Document Retrieval |
| 2026-03-21 | [quote-bind-diagram-prompt](artifacts/2026-03-21-quote-bind-diagram-prompt.md) | Prompt for Claude.ai workflow diagram — Quote & Bind |
| 2026-03-22 | [conversational-intake-diagram-prompt](artifacts/2026-03-22-conversational-intake-diagram-prompt.md) | Prompt for Claude.ai workflow diagram — Conversational Intake |
| 2026-03-23 | [email-intelligence-diagram-prompt](artifacts/2026-03-23-email-intelligence-diagram-prompt.md) | Prompt for Claude.ai workflow diagram — Email Intelligence |
| 2026-03-23 | [intake-manager-diagram-prompt](artifacts/2026-03-23-intake-manager-diagram-prompt.md) | Prompt for Claude.ai workflow diagram — Intake Manager |
| 2026-03-23 | [cross-sell-diagram-prompt](artifacts/2026-03-23-cross-sell-diagram-prompt.md) | Prompt for Claude.ai workflow diagram — Cross-Sell |
| 2026-03-26 | [conference-demo-video-brainstorm](artifacts/2026-03-26-conference-demo-video-brainstorm.md) | InsurtechNY Spring conference demo videos — FNOL voice + Smart Inbox workflow scripts and storyboards |
| 2026-03-26 | [conference-video-production-plan](artifacts/2026-03-26-conference-video-production-plan.md) | Step-by-step production plan for both conference demo videos — tools, assets, assembly, execution order |

## Decisions
- 2026-03-26: Conference demo videos: FNOL (Intake Associate for Claims, voice) + Smart Inbox (Inbox Associate, web workflow). Selected for audience fit (carrier/distributor/investor room at InsurtechNY), contrast (B2C voice vs B2B workflow), and credibility (Craig actively building Smart Inbox for a customer). AI video associate avatar held as upgrade path.
- 2026-03-26: Conference videos are produced representations, not recordings of live agents. No real FNOL or Smart Inbox agent exists yet — these would be built for customers. Production approach TBD.
- 2026-03-26: Existing showcase pages should be aligned with Cam's "Four Outcomes Navigation" matrix naming — separate effort from video production.
- 2026-03-26: Team blog access via separate repo (`indemn-ai/engineering-blog`) — Craig's content-system stays private (personal brand, video pipeline, full orchestration). Team repo gets only the blog site, selected content skills, and Indemn/Buzz brand configs.
- 2026-03-26: Deployment stays manual (`vercel --prod`) for now — no Vercel git integration. Craig controls when changes go live.
- 2026-03-26: Jonathan's structured JSON format (indemn-product-spec/v1) works well as input to the brainstorm phase of `/content-showcase`. No need for a separate JSON-to-MDX converter.
- 2026-03-23: Enhanced `/content-showcase` skill to 5-phase workflow: Brainstorm → Diagram Prompt → Plan (with code review) → Parallel Build → Deploy. Documented all technical constraints, reusable components, and patterns from 7 deployed pages.
- 2026-03-23: Cross-sell has 4 distinct product approaches: opportunistic (built), renewal (next), book analysis, life event detection. Each is its own showcase page. Saved to memory for future sessions.
- 2026-03-23: Code-reviewer agent before plan approval catches real issues — missing scenario data, ARIA collision risks, missing pubDate, board HTML scoping. Always run before building.
- 2026-03-23: Email Intelligence and Intake Manager are separate products. Email Intelligence is the smart inbox layer (classify, link, stage, extract, draft). Intake Manager is the full pipeline (document processing, extraction, validation, multi-provider quoting). Email Intelligence is step 1; Intake Manager is the complete workflow.
- 2026-03-21: Document Retrieval showcase — scoped from Ian's sales call. Interactive demo with 3 scenarios, mock chat + workflow steps + Outlook inbox approval + styled HTML documents. Workflow diagram built in Claude.ai as SVG. Custom components imported directly in MDX body (no changes to existing infrastructure). Full-bleed CSS breakout pattern for components inside showcase-prose container. Parallel session execution (2 Claude Code agents on worktrees). Messaging: "We understand insurance. We understand your problems. We have the tech to solve them. Let's build this together." Partnership angle, not product pitch.
- 2026-03-20: `/content-showcase` skill — adaptive conversation, not rigid template. Every product page is different. Three must-resolve items before moving past brainstorm: audience, core message, demo approach. Everything else (features, stats, FAQ, walkthrough, CTA) included only if it fits. Demo types: screen recording, diagram/visual, interactive embed, video from visuals. Single-session workflow, skill does all work in-session (only hard handoff is screen recording).
- 2026-03-10: Evaluations blog rewrite — practical builder tone, not dramatic storytelling. Core insight: "the hardest part of building a good AI agent isn't the AI — it's defining what success looks like." Tone calibrated from The Buzz tone review learnings. Images should be infographic/diagram style (Gemini image-gen), not abstract AI art.
- 2026-03-10: Blog images should be conceptual infographics, not UI mockups — mockups give the wrong impression that the image is the actual product dashboard. Flat vector, white background, consistent style across all images in a post.
- 2026-03-10: 1Password `op read "op://vault/item/field"` returns actual secret values. `op item get --fields label=field` returns reference strings. Use `op read` for Gemini API key in image-gen workflows.
- 2026-03-09: "The Buzz" — weekly CTO engineering newsletter for Kyle. Newspaper-style PDF + structured markdown. Created through guided extraction pulling from Linear, Slack, OS projects, git. Dual output for human reading and Claude Code consumption. Own `/newsletter` skill. React-PDF rendering with dedicated component library. Design doc: `artifacts/2026-03-09-the-buzz-newsletter-design.md`
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
