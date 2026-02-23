# Content System

AI-powered content creation pipeline for Indemn and personal brands. Transforms voice-based ideas into polished, publishable content through dynamic extraction, iterative drafting, and multi-platform distribution. Lives in a separate repo (`/Users/home/Repositories/content-system`) with skills symlinked to `~/.claude/skills/`.

## Status
Session 2026-02-23-a complete. Shook out the EA → content → content-extract pipeline flow. All routing and state tracking works. Found critical gap: Indemn brand voice documents (Master System Prompt + Marketing Persona Prompt) exist in Google Drive but aren't wired into the content skills. These contain strict terminology rules, tone guidance, proof points, and competitive positioning that must be loaded during extraction/drafting.

**Active content:** "Agents That Build Agents" blog post (idea-7e636b01, piece cp-0ca41039). Extraction ~75% complete, paused. Resume context at `content-system/drafts/2026-02-23-agents-that-build-agents/context.md`.

**Next up (run `bd ready` in this project dir):**
1. Wire Indemn brand voice docs into content skills (kxp.6) — unblocks everything
2. Resume extraction + full pipeline test through preview (kxp.5)
3. Design Indemn guardrails feature (kxp.4)

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Content system repo | GitHub repo | /Users/home/Repositories/content-system |
| Indemn blog | Website | blog.indemn.ai |
| Design spec | Doc | content-system/docs/plans/2026-01-30-blog-content-system-design.md |
| System knowledge | Doc | content-system/docs/system-knowledge.md |
| Orchestration layer design | Doc | content-system/docs/plans/2026-02-08-orchestration-layer-design.md |
| Master System Prompt (v2026.1) | Google Doc | gog docs cat 1lowazd0cvnX45M3nWP0bzKCZ2IA9G79_NNmmToxYIQM |
| Marketing Material Persona Prompt | Google Doc | gog docs cat 1ibuNPLYOpID063UJpJhVbXwY91mniNvv0SeNnoYscYI |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|

## Decisions
- 2026-02-23: Content system stays as a separate repo for now; OS project tracks the work and context
- 2026-02-23: Brand voice docs must be wired into content skills before resuming drafting — this is the critical path
- 2026-02-23: Extraction skill should pull from internal sources (Drive, Slack, meetings) before asking the author to repeat information
- 2026-02-23: Context window management matters — drafting should start in a fresh session with brand docs pre-loaded

## Open Questions
- How to wire brand voice docs into skills: download to `brands/indemn/references/`, add gog commands to skill prerequisites, or build into brand config?
- Should guardrails be a validation step (separate skill) or integrated into content-refine?
- Is the blog deployed to Vercel yet, or still local-only?
- The content-extract skill's "dynamic interview" should know to search internal sources — how to teach it that without bloating the skill?
