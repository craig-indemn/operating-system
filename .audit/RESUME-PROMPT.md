# Resume Prompt — Paste This to Continue the Audit

Copy everything between the `---` lines below into the next session's first message.

---

You are resuming a multi-session vision-vs-implementation audit. The previous session ran out of context mid-work. All state is preserved on disk. Your job is to continue without loss of accuracy and complete the audit.

**DO NOT START WORK OR ANSWER ANY QUESTIONS YET. DO THIS SEQUENCE FIRST:**

## Step 1: Read the handoff (required)

```
Read /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/SESSION-HANDOFF.md
```

This document contains: the user's end objective, current state of the audit, full list of files read and remaining, the synthesized vision map so far, Finding 0 status, and step-by-step instructions for resumption.

## Step 2: Verify audit infrastructure

Run these commands to confirm state:

```bash
cat /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/manifest.yml | head -10
ls /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/ | wc -l
```

Expected: manifest shows `Spec-vs-Implementation Pass 2 (Architectural Layer)` audit with 104 total files, 58 checked. `.audit/notes/` directory has 59 structured note files.

If numbers differ, STOP and tell the user — something has changed since handoff.

## Step 3: Read the Pass 2 audit report (already published)

```
Read /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-16-pass-2-audit.md
```

This is the completed Pass 2 audit. It confirms Finding 0 (agent execution in wrong architectural layer) and Finding 0b (assistant-as-kernel-endpoint instead of chat-harness). Do not rewrite this — build on it.

## Step 4: Read the 3 most architecturally-important existing notes

These are the primary evidence for Finding 0. Read them so you understand the depth of analysis already done:

```
Read /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-10-realtime-architecture-design_md.md
Read /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/Users_home_Repositories_indemn-os_kernel_temporal_activities_py.md
Read /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/.audit/notes/projects_product-vision_artifacts_2026-04-14-impl-spec-phase-2-3-consolidated_md.md
```

## Step 5: Confirm you understand the work

Tell the user in one sentence: what's been done, what's remaining, and what you're about to do first.

Expected answer shape: "58 of 104 files checked with notes on disk. 46 design artifacts remain to read (Tier S priority list in handoff). Finding 0 confirmed structurally. I'm about to continue the read-next loop starting with [Tier S file]."

Wait for user confirmation before proceeding.

## Step 6: Execute the remaining work (only after user confirms)

Per SESSION-HANDOFF.md § "Next session — step-by-step resumption":

1. **Continue Pass 3 reading** using the systematic-audit skill. The 46 remaining files are listed in SESSION-HANDOFF.md § "Remaining 46 files to read" — in Tier S (18) / Tier A (9) / Tier B (6) / Tier C (13) priority order.

   For each remaining file:
   - Use `bash /Users/home/Repositories/operating-system/.claude/skills/systematic-audit/read-next.sh` to get the next file in manifest order
   - OR read Tier S files out of order by reading directly with Read tool + writing notes to the correct path + running `bash .claude/skills/systematic-audit/validate-notes.sh <source-file-path>` to mark checked
   - Notes go to `.audit/notes/<slug>.md` where slug = source path with `/` and `.` replaced by `_`
   - Notes MUST contain these sections (validator enforces): `**File:**`, `**Read:**`, `**Category:**`, `## Key Claims`, `## Architectural Decisions`, `## Layer/Location Specified`, `## Dependencies Declared`, `## Code Locations Specified`, `## Cross-References`, `## Open Questions or Ambiguities`

2. **After manifest is 100% checked**, run `bash /Users/home/Repositories/operating-system/.claude/skills/systematic-audit/cross-reference.sh` to regenerate the matrix with all 104 files.

3. **Build final vision map** at `projects/product-vision/artifacts/<today>-vision-map.md`. Extend the partial vision map in SESSION-HANDOFF.md § "Vision map — synthesized from the 58 files read so far." Organize by subsystem. For conflicts, later artifacts override earlier (user's explicit rule).

4. **Execute Pass 4 — the implementation audit.** For every architectural claim in the vision map, check the implementation in `/Users/home/Repositories/indemn-os/`. Code file scope is listed in SESSION-HANDOFF.md § "Pass 4 code file scope" — 23 already read in Pass 2 + ~60 more likely needed.

5. **Produce discrepancy report** at `projects/product-vision/artifacts/<today>-alignment-audit.md`. Structure per SESSION-HANDOFF.md § "Produce discrepancy report."

## Critical rules

- **Do NOT skip files.** User pushed back explicitly against pruning. All 46 remaining files get read.
- **Do NOT re-read what's already on disk.** 58 files have notes. The manifest is truth for what's done.
- **Do NOT trust your own memory** — read the file, write notes, validate.
- **Do NOT rewrite the Pass 2 audit.** It's complete and accurate. Build on it.
- **Later artifacts override earlier uncertain decisions** — user's explicit rule for the vision map.
- **Notes are concise** — extract architectural claims + supersedence relationships + Finding 0-class risks. Skip field-level detail unless it changes the architecture.
- **The synthesis-gate hook is active.** `.claude/settings.local.json` blocks Write to audit/report/finding files until manifest is 100% checked. This is by design.

## The user's end objective (quoted)

> "Identify every single discrepancy so that we can ensure what is implemented matches the vision. That is the end objective: to have the vision being implemented exactly."

Treat this as the definition of "done." The final deliverable is the discrepancy report listing every misalignment between vision (design artifacts) and implementation (code in `/Users/home/Repositories/indemn-os/`).

---
