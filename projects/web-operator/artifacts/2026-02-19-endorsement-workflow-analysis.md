---
ask: "Understand the endorsement verification workflow, what the team has done recently, and what's needed for Monday's demo"
created: 2026-02-19
workstream: web-operator
session: 2026-02-19-a
sources:
  - type: gmail
    description: "Johnson Insurance email thread — George's Feb 16 call recap, MaeLena's Feb 17 response with ECM CAP CHG guide and error test case"
  - type: gmail
    description: "Gemini meeting notes — Feb 16 Johnson Insurance Sync, Feb 13 Web Agent Discussion, Feb 10 Johnson workflow review, Feb 9 Craig/George scope discussion"
  - type: slack
    description: "#customer-implementation — full web operator thread including Rudra's Feb 18 update, Dhruv's productionalization points, Craig's architecture discussion, George's call recap, cost analysis thread"
  - type: slack
    description: "Craig-Kyle DM — origin of web operator initiative, operating system connection"
  - type: github
    description: "web_operators repo — CLAUDE.md, HANDOFF.md (15 sessions), framework-architecture.md, git log (23 commits, 3 contributors), paths/ecm_cap_renewal/path_v1.md"
  - type: gmail
    description: "Downloaded ECM CAP CHG guide.docx (1.4MB, 9 annotated screenshots) to web_operators/docs/"
---

# Endorsement Workflow Analysis & Demo Preparation

## Part 1: Project Overview

### What This Is

A reusable web automation framework where an LLM agent (Claude Opus 4.6 via Deep Agents/LangGraph) operates a browser via Agent Browser CLI to complete tasks. It follows structured "path documents" (markdown playbooks) and improves over successive runs.

**Customer**: Johnson Insurance (largest Everett Cash Mutual agency)
**Contract**: $10,000/year, signed Feb 4, 2026
**Primary contact**: MaeLena Apperson (Operations Coordinator, maelena@gojohnsonins.com)
**Account lead**: Kyle Geoghan
**PM**: George Remmer (Rem)

### The Problem

Johnson's VA spends significant time manually processing ECM policy documents into Applied Epic. Coventus (their RPA) pulls docs from ECM and attaches them in Epic every Monday night. The bottleneck is the last mile — manual data verification/entry from the documents into Applied Epic. No API access (Applied Epic API-SDK is a separate paid add-on they don't have), so it's full web operator automation.

### Three Phases

| Phase | What | Status |
|-------|------|--------|
| **Endorsements (CHG)** | Verify endorsement changes match docs, update premium, close/reassign | Active — guide + test data received Feb 17 |
| **Renewals (POL3)** | Full renewal processing (FOP/CAP) | POL3 activities now in sandbox |
| **Billing/Invoices** | Carrier invoice processing | Deferred by customer |

---

## Part 2: The Endorsement Verification Workflow

### Key Insight

From the Feb 16 call with Johnson, George's biggest takeaway: **"We don't even have to edit docs. Just confirm whether or not they WERE edited correctly."**

The account manager already made the policy change before submitting the endorsement. The operator's job is **verification, not data entry**.

### Workflow Steps (from MaeLena's ECM CAP CHG Guide)

**Step 1: Open the CHG3 Activity**
- CHG3 activities are assigned to Indemn by Automation with note "endorsement decs attached"
- The activity description tells you what change was made (e.g., "Eff: 3/28/2025 Delete VW All track, add Honda Prologue BAUT Endorsement Request")
- Association field shows which policy (e.g., "Policy - BAUT - CAP104137")
- Click the hyperlinked activity code to open it

**Step 2: Open the Endorsement PDF**
- Access > Attachments > locate and open the .pdf attached by automation
- This is the **revised declaration** from the carrier showing the policy AFTER the change
- Marked "REVISED DECLARATION" with the specific change described

**Step 3: Read All Activity Notes**
- Click "View All Notes" (blue link on right side above notes box)
- Notes contain history of what was submitted — automation note says "endorsement decs attached", earlier notes from the account manager describe the actual change request
- Multiple notes may exist from different people across different dates

**Step 4: Compare Notes vs. PDF (THE KEY VERIFICATION)**
- Do the notes describe a change that matches what the revised declaration shows?
- If an item was supposed to be added → confirm it appears on the decs
- If an item was supposed to be removed → confirm it's no longer on the decs
- This is the core value of the operator — catching mismatches

**Step 5: Open the Policy Line and Confirm Changes in Epic**
- Navigate to the policy via double-clicking the policy line or the service summary row
- **Critical**: If multiple changes have been submitted on the policy, look at the Service Summary rows to select the CORRECT change being checked
- Open the policy and verify the specific change exists:
  - Vehicles tab: Are added vehicles present? Are removed vehicles gone?
  - Additional Interests: Are new secured parties (e.g., Honda Lease Trust) added?
  - Any other tabs affected by the specific change

**Step 6: Update Premium**
- Servicing/Billing > Line tab > Enter total premium from PDF > Click Calculate (commission)
- Switch to Policy tab > Click Calculate for BOTH premium and commission
- Both Calculate buttons must be pressed (Line first, then Policy)

**Step 7: Issue the Endorsement**
- Actions > Issue/Not Issue Endorsement > Finish
- This changes the service summary row status from "Submitted" to "Issued"

**Step 8: Close Out the Activity**
- Go back to the CHG activity
- **If everything correct**: Add note "decs checked and policy issued", close activity as successful
- **If errors found**: Note what the errors were, **reassign to Sheryll Bausin**, set follow up to today, do NOT close the activity

### Test Data Provided by MaeLena (Feb 17)

| Test Case | Account | What to Expect |
|-----------|---------|----------------|
| **Correct submission** | Dry Ridge Farm, LLC | Standard vehicle trade — delete VW All track, add 2025 Honda Prologue. Should verify cleanly. |
| **Error case** | Bill Kistler | 4 intentional errors: wrong effective date, wrong VIN, vehicle not removed, line not updated/submitted. Operator should catch ALL errors and reassign to Sheryll Bausin. |

### Endorsement vs. Renewal — Key Differences

| Aspect | Endorsement (CHG) | Renewal (POL3) |
|--------|-------------------|----------------|
| Scope | Verify ONE specific change | Cross-reference ENTIRE policy |
| Input | Notes describe the change + revised PDF | Full renewal declaration PDF |
| Verification | Change matches notes + PDF + Epic | Every field in every tab matches |
| Complexity | ~5 min task manually | ~20+ min task manually |
| Error handling | Reassign to Sheryll Bausin | Create RNWL activity for MaeLena |
| Issue action | Issue/Not Issue **Endorsement** | Issue/Not Issue **Policy** |
| Volume | 20-50/week batched Monday nights | Separate cadence |

---

## Part 3: What the Team Has Done

### Contributors

| Person | Role | Commits | Focus |
|--------|------|---------|-------|
| Craig Certo | Framework design | 17 | Middleware, harness, path structure, model benchmarking |
| Rudra Thakar | Tech lead | 3+ | Running the agent, path refinement, cost optimization, endorsement workflow |
| Dhruv Rajkotia | Architecture | 3 | Docs cleanup, productionalization, session management |

### Development Timeline

| Date | Milestone |
|------|-----------|
| Feb 4 | Contract signed, kickoff email |
| Feb 5 | MaeLena sends Epic credentials + 27 activities |
| Feb 9-10 | Initial sync calls, API research (no API access confirmed) |
| Feb 11 | Craig shares proposal doc, team alignment |
| Feb 12 | Framework scaffolding, first smoke tests, PDF reader tool |
| Feb 13 | Phases 1-4 complete (173 tests), Rudra starts CAP flow, cost concerns raised ($13/run) |
| Feb 15 | Craig pushes middleware optimizations (observation masking, state injection, stall detection) |
| Feb 16 | First full CAP run (199 steps, 20.5 min), stall detection rewrite, call with Johnson |
| Feb 17 | Rudra restructures paths (10→8 steps, per-activity pipeline), MaeLena sends endorsement guide + POL3 activities |
| Feb 18 | Rudra: cost down to ~$3/run, working on endorsement verification (cross-check PDFs against notes + policy) |

### Rudra's Latest Update (Feb 18, Slack)

> Focused on making the agent cheaper to run and more reliable. Key improvements include:
> - The agent now reuses previous context intelligently instead of reprocessing everything from scratch each run, which has brought the cost per run down from ~$18 to ~$3
> - Every run now logs a full cost breakdown in real time
> - Each run is fully isolated — no more interference between runs
> - Added guardrails to prevent common navigation mistakes
>
> Working on Next: updating the agent's workflow to cross-check PDFs against notes, cross-check PDFs against policy details (partially done), and automatically create a note activity once verification is complete.

Rudra is out Feb 19 for a family function.

### Recent Repo Changes (since Feb 16)

| Commit | Date | What |
|--------|------|------|
| `434aee9` | Feb 17 | Restructured paths from 10→8 steps with per-activity pipeline loop. Fixes bug where PDF and policy could come from different accounts. |
| `48dcae0` | Feb 18 | Enhanced CAP renewal paths and agent functionality (on indemn/main, not yet origin/main) |
| `ed98514` | Feb 18 | Gitignore cleanup (.cursor/, run_summary.md, step_4_pdf_data.md) |

New remote branch: `indemn/feat-web-operator-improvement`

### Key Technical Discoveries from Live Runs

- Applied Epic's `File → Exit` is the only reliable way to return to Home (SPA hash routing doesn't work)
- Epic uses custom ASI web components that sometimes hide inputs from accessibility tree
- `dispatchEvent(new MouseEvent('contextmenu', ...))` doesn't work in Angular — need real mouse commands
- Green progress bar (`.progress-box`) must disappear before trusting table contents — tables show "No items found" while still loading
- "Show Only Important Policy Documents" link replaces broken search filter for attachments

### Framework Architecture

| Module | Role |
|--------|------|
| `agent.py` | Assembles Deep Agent with tools, skills, middleware |
| `middleware.py` | Observation masking, state injection, progress-aware stall detection |
| `path_parser.py` | Parses structured markdown paths into dataclasses |
| `executor.py` | Streams LangGraph events, captures trajectory |
| `runner.py` | Creates run dirs, writes trajectory.jsonl + outcome.json |
| `comparison.py` | Cross-run evaluation and batch config |
| `resume.py` | Resume-from-step support |
| `tools.py` | Shell subprocess wrapper + visual PDF reader |

### Cost Analysis

| Stage | Cost/Run | Notes |
|-------|----------|-------|
| Early prototype | ~$13-18 | Uncontrolled runs, 1000 steps |
| Current (Feb 18) | ~$3 | Context reuse, stall detection, guardrails |
| Target (open source) | ~$0.10 | Once path is well-established |
| Monthly estimate | ~$40 | 400 runs/month at $0.10 |

Craig's cost strategy: Refine paths using Claude Code subscription (free Opus), run execution on cheaper/faster models. Open source models fine-tuned for browser use often match frontier performance at their specific task.

---

## Part 4: Production Operations Model

From the Feb 16 call with Johnson:

- **Volumes**: 20-50 endorsements batched Monday nights via Coventus RPA
- **Schedule**: Trigger Tuesday noon, fallback run Wednesday morning
- **Notifications**: None needed — add notes to activities, use Epic's built-in reporting
- **Auth**: Same login as sandbox (Enterprise ID: JOHNS87, no MFA)
- **Password resets**: Every ~3 months (end of April), need to design handler
- **Session constraint**: Epic only supports one active session per account

### Architecture Decisions (Craig + Dhruv aligned)

1. MongoDB as source of truth, filesystem for execution — pull configs at session start into unique session workspace, clean up after
2. Sequential execution first — one active run at a time (Epic session limitation)
3. Standalone instance for web operators (not co-located with production services)
4. Deployment: EventBridge scheduling → Lambda triggers → SQS for concurrency
5. Agent Browser sessions for future concurrency when workflows allow it

---

## Part 5: Critical Gap — No Endorsement Path

The `paths/` directory currently contains:
- `ecm_cap_renewal/` — renewal workflow (POL3), 8 steps, cross-references every tab
- `ecm_fop_renewal/` — renewal workflow (POL3), 8 steps, same structure
- `template/` — blank template

**There is no endorsement-specific path.** The existing paths are designed for the much more complex renewal workflow where every field in every tab is cross-referenced against the PDF. The endorsement workflow is fundamentally different — it only verifies ONE specific change described in the activity notes.

Rudra is building endorsement verification logic, but it appears to be within the existing renewal structure rather than as a separate, simpler endorsement path.

---

## Part 6: What's Needed for Monday's Demo

### Must-Have

1. **New endorsement path** (`paths/ecm_cap_endorsement/path_v1.md`)
   - Simpler than the renewal path — focused on the verification workflow
   - Steps: Login → Open CHG3 → Read notes → Open PDF → Compare notes vs PDF → Open policy → Verify specific change → Update premium → Issue endorsement → Close/reassign activity
   - Must handle both success case (close activity) and error case (reassign to Sheryll Bausin)

2. **Validate against Dry Ridge Farm, LLC** (correct submission)
   - Standard vehicle trade — should pass cleanly, issue endorsement, close activity

3. **Validate against Bill Kistler** (error case)
   - Should catch: wrong effective date, wrong VIN, vehicle not removed, line not updated
   - Should reassign to Sheryll Bausin with error notes

### Should-Have

4. **Model benchmarking** — once the path works reliably with Opus, test with:
   - Claude Sonnet 4.6 (cheaper, faster)
   - Claude Haiku 4.5 (cheapest Anthropic option)
   - Open source models fine-tuned for browser use
   - Use the existing comparison framework (`src/framework/comparison.py`) for side-by-side evaluation

5. **Speed optimization** — endorsement should be much faster than renewal since scope is narrower. Target: under 5 minutes per endorsement.

### Open Questions

- How to handle Epic password resets (every ~3 months, next expected end of April)?
- Who is Sheryll Bausin exactly — need full name / Epic user ID for reassignment
- What does the `indemn/feat-web-operator-improvement` branch contain?
- Is the Feb 18 code on `indemn/main` (2 commits ahead of `origin/main`) ready to merge?
- Does Rudra's endorsement work overlap with or replace the need for a new endorsement path?
