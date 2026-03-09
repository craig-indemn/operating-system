---
name: newsletter
description: Create The Buzz CTO engineering newsletter — gather data from Linear, Slack, Git, and OS projects, extract Craig's perspective per section, draft in structured markdown, render newspaper-style PDF via React-PDF. Use when the user mentions newsletter, The Buzz, or weekly engineering update.
argument-hint: [week-date]
---

# The Buzz — CTO Engineering Newsletter

## Overview

Pipeline for creating The Buzz, Craig's weekly CTO engineering newsletter for Kyle. Gathers data from Linear, Slack, Git, and OS projects; extracts Craig's perspective per section; drafts structured markdown; renders newspaper-style PDF.

**Two repos involved:**
- **Operating system** (this repo) — data gathering via OS skills (slack, linear, github, project)
- **Content system** (`/Users/home/Repositories/content-system/`) — brand config, voice doc, drafts, React-PDF renderer

Session must have `--add-dir /Users/home/Repositories/content-system`.

**Announce at start:** "Starting The Buzz #N for week of [date]. Gathering data..."

## When to Use

**Always:**
- Starting a new issue
- Resuming an in-progress issue
- Rendering a final draft

**Sometimes:**
- Quick gather to see what's available this week

**Never:**
- Editing non-newsletter content (use `/content` instead)

## Prerequisites

- Content system accessible via `--add-dir`
- `brands/the-buzz/` exists in content-system
- `tools/the-buzz/node_modules` installed in content-system
- OS skills authenticated: slack, linear, github

## Status Check

```bash
test -f /Users/home/Repositories/content-system/brands/the-buzz/config.yaml && \
test -d /Users/home/Repositories/content-system/tools/the-buzz/node_modules && \
echo "READY" || echo "RUN SETUP"
```

## Pipeline

### Step 1: Gather

Default: last 7 days. Override with `$ARGUMENTS` (e.g., `/newsletter 2026-03-10`).

```bash
# Linear — completed and in-progress issues
linearis-proxy.sh issues list --limit 50 --state completed --updated-after YYYY-MM-DD
linearis-proxy.sh issues list --state started --updated-after YYYY-MM-DD
```

```bash
# Git — merged PRs per tracked repo
for repo in bot-service indemn-platform-v2 evaluations indemn-observability voice-livekit web_operators operating-system; do
  gh pr list --repo indemn-ai/$repo --state merged --search "merged:>=YYYY-MM-DD" --json title,number,author,url,mergedAt
done
```

```bash
# Slack — key conversations (use the slack skill's execution model)
REPO_ROOT=$(git rev-parse --show-toplevel) && SLACK_PY=$(/usr/bin/python3 -c "import slack_sdk" 2>/dev/null && echo /usr/bin/python3 || echo python3) && PYTHONPATH="$REPO_ROOT/lib" $SLACK_PY << 'PYEOF'
from slack_client import get_client
client = get_client()
results = client.search_messages(query="from:craig after:YYYY-MM-DD", count=30)
for m in results["messages"]["matches"]:
    ch = m["channel"]["name"]
    print(f"#{ch}: {m['text'][:120]}")
PYEOF
```

```bash
# OS Projects — read status sections
for idx in /Users/home/Repositories/operating-system/.claude/worktrees/newsletter/projects/*/INDEX.md; do
  echo "=== $(dirname $idx | xargs basename) ==="
  sed -n '/^## Status/,/^## /p' "$idx" | head -20
done
```

Tracked repos: bot-service, indemn-platform-v2, evaluations, indemn-observability, voice-livekit, web_operators, operating-system

### Step 2: Map

Present candidates ranked by:
1. Customer-facing impact
2. Strategic significance for the raise
3. Connection to active Linear milestones
4. Novelty / architectural significance

Ask Craig: **"Which deserve a section? What am I missing? What's the lead story?"**

### Step 3: Extract (per section)

For each section Craig selected, ask these six questions:

1. Why this way? What was the trade-off?
2. What leverage does this give us?
3. What should Kyle understand about this?
4. How does this connect to the bigger picture?
5. What are the honest constraints — technical debt, risks, things we're worried about?
6. What documentation exists that I should link to?

### Step 4: Commentary

Ask Craig: **"What's on your mind beyond the features? Anything you've been reading, a competitor move, something about the raise, a technology bet you're thinking about?"**

### Step 5: Draft

Create drafts folder and files:
```
/Users/home/Repositories/content-system/drafts/the-buzz-YYYY-MM-DD/
  extraction.md    # Gathered raw material + Craig's answers
  context.md       # Session state (current step, what's done, what's next)
  draft-v1.md      # First draft with frontmatter template
```

**Before drafting:** Read `/Users/home/Repositories/content-system/brands/the-buzz/voice.md`. Apply voice calibration. First person, Craig's perspective. Check against completion criteria in `brands/the-buzz/config.yaml`.

Present draft. Iterate: feedback → revise (draft-v2, v3...). Never overwrite — preserve all versions.

### Step 5.5: Tone Review (CRITICAL — do not skip)

Before rendering, review every section for these anti-patterns:

**Self-aggrandizing** — Cut any mic-drops ("Built it."), self-mythologizing ("I'm setting the standard"), or transformation narratives ("I used to be X, now I'm Y"). Let the work speak for itself.

**Condescending to Kyle** — Cut any teacher-voice ("worth understanding"), reading instructions ("sit with this one"), or assumptions Kyle would underestimate ("further along than you'd think"). Kyle is smart. He'll get it.

**Status-report voice** — Cut bland product copy ("real time saver"), unnecessary recaps of work Kyle is driving, and dismissive phrasing about Kyle's concerns.

**The test for every sentence:** "Would Craig actually say this to Kyle over coffee?" If it sounds like a keynote, a LinkedIn post, or a status report, rewrite it.

Also check:
- Say "this week" for upcoming work (newsletter delivers Monday), not "next week"
- Don't announce things Kyle already knows — reference naturally
- "Every agent gets coverage" not "every customer gets access" — be precise

### Step 6: Render

```bash
cd /Users/home/Repositories/content-system/tools/the-buzz && \
npx tsx generate.tsx \
  --input /Users/home/Repositories/content-system/drafts/the-buzz-YYYY-MM-DD/draft-vN.md \
  --output /Users/home/Repositories/content-system/drafts/the-buzz-YYYY-MM-DD/the-buzz-YYYY-MM-DD.pdf
```

Show Craig the PDF for review before delivery.

### Step 7: Deliver

Send via Slack DM to Kyle (UFK4DNNHG):
1. Open DM with Kyle
2. Send introductory message
3. Upload PDF in thread (title: "The Buzz #N — DATE")
4. Upload markdown source in thread (title: "The Buzz #N — Markdown Source")

Use the `/slack` skill's execution model for file uploads.

## Resuming Mid-Pipeline

On startup, check for existing in-progress issue:

```bash
ls /Users/home/Repositories/content-system/drafts/the-buzz-*/context.md 2>/dev/null
```

If found, read context.md to determine current stage:
- Has extraction.md but no draft → resume at Step 5 (Draft)
- Has draft-vN.md but no PDF → resume at feedback/refine or Step 6 (Render)
- Has PDF → issue is complete, start a new one

Also check state store:
```bash
python3 /Users/home/Repositories/content-system/scripts/cs.py piece list --format newsletter --brand the-buzz --status in_progress --json
```

## State Store Integration

```bash
# Create idea + piece on startup
python3 /Users/home/Repositories/content-system/scripts/cs.py idea create --title "The Buzz #N — YYYY-MM-DD" --brand the-buzz --source direct
python3 /Users/home/Repositories/content-system/scripts/cs.py piece create --idea {id} --format newsletter --platform slack --brand the-buzz

# Update at transitions
python3 /Users/home/Repositories/content-system/scripts/cs.py piece update {id} --status draft --draft-version N
```

Graceful degradation: if cs.py fails, continue without state store. Log a warning.

## Quick Reference

| User Says | Action |
|-----------|--------|
| "Let's do the newsletter" / "/newsletter" | Start at Gather |
| "Continue the buzz" | Check drafts/ and context.md, resume at appropriate step |
| "Render the newsletter" | Jump to Step 6 |
| "/newsletter 2026-03-10" | Start for specific week |

## Key Files

| File | Purpose |
|------|---------|
| `/Users/home/Repositories/content-system/brands/the-buzz/voice.md` | Voice calibration — read before drafting |
| `/Users/home/Repositories/content-system/brands/the-buzz/config.yaml` | Completion criteria, brand config |
| `/Users/home/Repositories/content-system/drafts/the-buzz-YYYY-MM-DD/` | Working directory for current issue |
| `/Users/home/Repositories/content-system/tools/the-buzz/generate.tsx` | PDF renderer |

## Rendering Notes

- **Ligature fix:** Barlow font GSUB tables are stripped via fonttools. If fonts are replaced, re-strip: `python3 -c "from fontTools.ttLib import TTFont; f=TTFont('file.ttf'); del f['GSUB']; f.save('file.ttf')"`
- **Logo:** Indemn_PrimaryLogo_Iris.png at `tools/the-buzz/assets/indemn-logo.png`. Aspect ratio 4.33:1 — set width proportional to height.
- **Banner:** Generate via `/image-gen` skill with Indemn brand colors (iris/eggplant), 21:9 aspect ratio. Save to drafts folder as `banner.png`.
- **Page 3 layout:** Commentary in left column (flex: 3), backlinks in right sidebar (flex: 2). Don't put commentary on same page as features — causes orphaned headings.
- **Colors:** Indemn brand palette defined in `generate.tsx` as `const c = { iris, lilac, eggplant, lime, ... }`. Must match `brands/the-buzz/config.yaml`.

## Red Flags

- Never draft without reading voice.md first
- Never skip extraction questions — Craig's perspective IS the product
- **Never skip the tone review (Step 5.5)** — AI drafts consistently produce self-aggrandizing and condescending language that Craig will reject
- Always present candidates and let Craig choose sections
- Always get approval before rendering final PDF
- Never use relative paths to content-system — always absolute
- Don't say "next week" — the newsletter delivers Monday, so upcoming work is "this week"

## Archive

After delivery, archive to `content-system/published/the-buzz/YYYY-MM-DD/` with both markdown and PDF.
