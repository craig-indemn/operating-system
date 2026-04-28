---
ask: "Draft a Slack message to Dhruv covering everything he needs to act on for the GIC migration to keep moving. Should be one read-and-act message, not a back-and-forth."
created: 2026-04-28
workstream: gic-email-intelligence
session: 2026-04-28-a
sources:
  - type: linear
    description: "DEVOPS-151, 153, 154, 159 issue state + comments"
  - type: github
    description: "indemn-ai/gic-email-intelligence PR #1, branch protection rulesets, repo permissions"
  - type: aws
    description: "github-actions-deploy IAM role inline policy"
---

# Draft Slack message to Dhruv

> Hey Dhruv — quick on the GIC → Indemn infra migration. PR #1 is up and there are three things on your plate. None huge, but they're blocking forward progress so wanted to get them in front of you in one shot.
>
> **1. Review/merge PR #1**
> https://github.com/indemn-ai/gic-email-intelligence/pull/1
>
> 33 migration commits + 1 merge commit reconciling unrelated histories with your `074a1ec` initial commit (your placeholder README got dropped in favor of our migration-ready one — only one was going to survive the merge). Saw your Trivy bump on top, thanks. I just pushed a `docs/security.md` (Phase H.3) on top of yours — let me know if you'd rather see that as a separate PR, easy to revert.
>
> **Recommended merge method: "Create a merge commit"** — preserves the 33-commit granularity for blame/bisect. Squash collapses everything into one commit (loses bisect value); rebase rewrites SHAs and undoes the unrelated-histories merge.
>
> **2. Register self-hosted runners — DEVOPS-159**
> https://linear.app/indemn/issue/DEVOPS-159
>
> Verified the org pattern: per-repo runners on each EC2, not org-level (each existing service has its own `actions-runner-<service>/` dir on dev-services + prod-services). For `indemn-ai/gic-email-intelligence` we need:
> - dev-services (`i-0fde0af9d216e9182`): `actions-runner-gic-email-intelligence/`, name `ip-172-31-43-40-gic`, labels `self-hosted,linux,x64,dev`
> - prod-services (`i-00ef8e2bfa651aaa8`): same dir name, name `ip-172-31-22-7-gic`, labels `self-hosted,linux,x64,prod`
>
> Runner version: 2.334.0 (matches existing org-standard). The DEVOPS-159 description has the full SSM-driven `./config.sh` + `./svc.sh install ubuntu` + start sequence for both hosts. You'll need to issue one fresh registration token per host (single-use, 1h expiry) — `gh api -X POST repos/indemn-ai/gic-email-intelligence/actions/runners/registration-token`.
>
> Reason this is on you and not me: `craig-indemn` only has push/pull/triage on the empty repo — no admin — so I can't issue tokens or set branch protection on `prod`.
>
> **3. Side ask: grant `craig-indemn` admin on `indemn-ai/gic-email-intelligence`**
>
> Would unblock both this and Phase F.2 (branch protection on `prod` branch) so I can run those myself. Also removes the single-point-of-failure concern for cutover-day operations. Branch protection rulesets are already configured by you, so I'm not bypassing controls — just need the bit to apply existing patterns. Easy push-back if you'd rather keep admin tight.
>
> **Heads-up on a Phase I prod blocker (no action needed yet, just for awareness):**
>
> The `github-actions-deploy` IAM role's inline policy `deploy-dev-only` has an explicit `Deny` on `indemn/prod/*`. Smart guard for everyone else, but it'll block the prod deploy job for GIC. Three options on file in DEVOPS-153 comments — recommended is a separate `github-actions-deploy-prod` role with prod allows + branch-scoped trust. Won't bug you on this until we're ready to push the `prod` branch (Phase I, post-soak); just flagging now so it's not a surprise.
>
> Once the runners are up I can take the rest of Phase G dev deploy + 24h soak end-to-end. Thanks 🙏

---

## Notes for Craig before sending

1. **Where to send.** Slack DM to Dhruv. Or whatever the team's preferred channel is for these — `#engineering` if it's a public-async-ok thing.
2. **Tone check.** Light, specific, action-oriented. Three numbered items so he can mentally check them off. The "no action needed yet" Phase I note avoids burying it but doesn't ask for anything from him today.
3. **What I omitted vs what's in DEVOPS-159.** The Slack message just points at Linear; the full step-by-step is in the issue description. Don't restate it in Slack — easier to maintain a single source of truth.
4. **Side ask sequencing.** Items 1 and 2 are required action; item 3 (grant Craig admin) is optional but high-leverage — phrased to make declining easy. If he grants admin, items 1 and 2 become my work to do solo and the conversation is done. If he doesn't, he handles 1 and 2 and we still move forward.
5. **What this message does NOT cover** (intentionally, to avoid scope sprawl):
   - The **port 8080 conflict on dev-services** with `openai-fastapi-app-1` — that's our problem to fix in a follow-up commit on the migration branch (or a separate PR after #1 merges). Not Dhruv's concern.
   - The **dead Cloudflare tunnel** in the live add-in deployment — Phase I.1b concern; will surface to Maribel/JC closer to cutover when the rebuild path is decided.
   - The **JWT_SECRET length** (14 chars, dev-only) — Phase H follow-up; not blocking anything.
6. **Parking lot for follow-up Slacks** if needed:
   - Once runners online: ping back with confirmation + ask Craig to schedule the first dev-deploy soak window
   - Once PR merges: trigger F.3 Amplify rewire (Craig owns)
   - Once both above: trigger Phase G — first dev EC2 deploy, watch logs, 24h soak
