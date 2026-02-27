# Engineering Blog

Indemn's engineering blog at blog.indemn.ai. Covers the Astro site (engineering-blog repo), content pipeline integration, and the marketing website blog link.

## Status

Session 2026-02-27: Set up the full blog deployment pipeline.
- Identified `indemn_website_new_design` as the indemn.ai source (AWS S3/CloudFront, `prod` branch, React/Vite/MUI)
- Added blog link to marketing website nav + footer → PR #205 open (WEB-142 In Review)
- Copied Astro site from content-system into `indemn-ai/engineering-blog` repo
- Added README with contributor guide and CLAUDE.md
- Made content-publish skill brand-agnostic (routes by `method` field in brand config)
- Updated Indemn brand config to publish via `git-pr` to engineering-blog
- Deployed to Vercel → blog.indemn.ai is live from engineering-blog repo

**Next:** Connect Vercel GitHub integration for auto-deploy on push (needs org admin).

## External Resources

| Resource | Type | Link |
|----------|------|------|
| Engineering blog repo | GitHub | indemn-ai/engineering-blog |
| Marketing website repo | GitHub | indemn-ai/indemn_website_new_design |
| Content system repo | GitHub | craig-indemn/content-system |
| Blog site | URL | https://blog.indemn.ai |
| Marketing site | URL | https://indemn.ai |
| Website blog link PR | GitHub PR | indemn-ai/indemn_website_new_design#205 |
| Linear issue | Linear | WEB-142 |
| Vercel project | Vercel | craig-indemns-projects/engineering-blog |

## Decisions

- 2026-02-27: Blog site lives in `indemn-ai/engineering-blog` (Dhruv's repo), not in content-system
- 2026-02-27: Content system publishes to engineering-blog via PR (git-pr method), not direct push
- 2026-02-27: Content-publish skill is brand-agnostic — routes by `method` field in brand config, not by brand name
- 2026-02-27: Marketing website blog link goes in top nav (after About) and footer (Company column)
- 2026-02-27: Marketing website `main` branch is broken (missing hero-consultative component) — work from `prod`

## Open Questions

- Vercel GitHub integration needs org admin to grant access to engineering-blog repo
- Should auto-deploy be on merge to main only, or also preview deploys on PR branches?
- Marketing website PR #205 needs someone with merge access to `prod` branch
