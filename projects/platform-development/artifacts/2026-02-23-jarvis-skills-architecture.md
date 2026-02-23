---
ask: "Implement Jarvis skills architecture — replace subagents with modular SKILL.md files"
created: 2026-02-23
workstream: platform-development
session: 2026-02-23-a
sources:
  - type: github
    ref: "https://github.com/indemn-ai/percy-service"
    description: "percy-service repo — all changes on main branch"
  - type: ec2
    description: "Dev EC2 at ec2-44-196-55-84.compute-1.amazonaws.com"
---

# Jarvis Skills Architecture Implementation

## What Was Done

Replaced the monolithic subagent architecture (rubric_creator + test_set_creator) with the deepagents library's built-in skills framework. Jarvis is now a single agent whose capabilities are determined by which skills are loaded via SKILL.md files.

### Commits on main (6 total)

1. **`6085ef9`** — `feat: Jarvis skills architecture — replace subagents with modular SKILL.md files`
   - Deleted 3 legacy flat-format skill files
   - Created 3 new SKILL.md skills in subdirectory format (eval-orchestration, rubric-creation, test-set-creation)
   - Wired up skills/backend support in DeepAgentComponent (FilesystemBackend with virtual_mode=True)
   - Added jarvis_evaluation_v2 template (Sonnet 4.6, skills-based, no subagents)
   - Made template ID configurable via JARVIS_TEMPLATE_ID env var (defaults to v2)
   - Removed skills/ from .dockerignore

2. **`22f5886`** — `fix: Strengthen JARVIS_CORE_PROMPT to mandate reading skills before acting`
   - Agent was skipping skill reading and jumping to tool calls

3. **`49721b0`** — `fix: Correct API payload format in evaluation skills`
   - Connector expects agent_id at tool input level, not inside data dict

4. **`1f73bdb`** — `fix: Remove get_agent/list_agents from v2 eval template connectors`
   - Created EVALUATION_V2_CONNECTOR_IDS (only eval tools, no agent-builder tools)
   - Jarvis kept calling get_agent (V2 API) instead of bot_context (eval service)

5. **`e8c45ee`** — `fix: Make data field descriptions explicit about required content`
   - Updated RubricsInput and TestSetsInput data field descriptions to explicitly state required fields (name, rules/items)

6. **`1bd5a9a`** — `fix: Stop headless Jarvis from polling run status indefinitely`
   - Updated eval-orchestration SKILL.md to tell headless mode to report IDs and STOP
   - Jarvis was burning tokens in an infinite polling loop checking run status every ~2 seconds

### Dev EC2 State

- Container running at `/opt/percy-service` on `ec2-44-196-55-84.compute-1.amazonaws.com`
- SSH: `ssh -i /Users/home/Repositories/ptrkdy.pem ubuntu@ec2-44-196-55-84.compute-1.amazonaws.com`
- Port: 8013 (host) -> 8000 (container)
- Template `jarvis_evaluation_v2` seeded in MongoDB
- `jarvis-default` agent recreated from v2 template
- Skills files verified at `/app/skills/evaluations/` inside container

### Test Runs Against Wedding Bot (bot_id: 676be5cbab56400012077f4a)

- **Org ID**: `676be5a7ab56400012077e7d` (EventGuard org, field is `id_organization`)
- **Attempt 1**: 404 — Jarvis called `get_agent` (V2 API) instead of `bot_context` → fixed by strengthening prompt
- **Attempt 2**: 404 — Still calling `get_agent` → fixed by removing agent-builder tools from v2 connectors
- **Attempt 3**: 422 — `bot_context` worked! But rubric creation sent empty `data` dict → fixed payload docs in skills
- **Attempt 4**: 422 — Still empty `data` — Jarvis generates content but doesn't pass it in `data` field → improved field descriptions
- **Attempt 5**: COMPLETED — job `jarvis_job_c30ef7b4ccb1`, triggered at 20:04:31 UTC
  - Rubric created: `09cecb50-1f06-42fa-a9f0-8d97bc004332` (5 universal rules)
  - Test set created: `7be041da-19d8-4a58-a975-f3275166e1d7` (14 items: 8 scenarios, 6 single-turn)
  - Eval run: `b17c6fff-ea7b-40ce-9f6c-fabe8defce40` — completed in ~13 minutes

### End-to-End Evaluation Results

| Metric | Value |
|--------|-------|
| Items completed | 14/14 |
| Items passed | 9/14 (64.3%) |
| Criteria passed | 45/51 (88.2%) |
| Rubric rules passed | 65/69 (94.2%) |
| Component: general | 69.0% (20/29) |
| Component: prompt | 98.2% (54/55) |
| Bot model | gpt-5.2 (OpenAI) |

### V2 Rubric (5 universal rules — correct!)

| Rule | Severity | Purpose |
|------|----------|---------|
| No Hallucination or Fabrication | high | No invented facts, policy numbers, or coverage details |
| Professional and User-Friendly Tone | medium | Warm, professional, no bold text or jargon |
| Stays Within Wedding Insurance Domain | medium | No off-topic assistance (tax, medical, legal) |
| Seeks Clarification Instead of Assuming | high | Ask rather than pre-fill missing parameters |
| Response Coherence and Clarity | low | Clear, grammatical, logically structured responses |

Compare to v1 rubric which had **18 workflow-specific rules** including things like "validates state before generating quote" and "enforces minimum cancellation budget" — rules that only apply during quoting, not universally.

### Failures Identified (Real Bot Issues)

| Item | Type | What Failed |
|------|------|-------------|
| Greeting | single_turn | Bot doesn't identify itself as Indemn/EventGuard |
| Non-Contact Data Modification | scenario | Doesn't handle modification requests gracefully |
| Human Handoff | scenario | Tool execution error during handoff process |
| Quote Modification | scenario | Can't re-quote after budget change |
| Off-Topic Diversion | scenario | Loses flow state after FAQ redirect |

All 5 failures identify real problems with the Wedding Bot, not evaluation calibration issues.

### Known Issue: LengthFinishReasonError

One rubric evaluator hit OpenAI's 32K completion token limit. LangSmith wrapped this as a `key='wrapper'` error result. The sync code correctly skips it with a warning. Non-blocking — the evaluation still completed.

### What's Working
- Skills framework fully wired: deepagents FilesystemBackend → SkillsMiddleware → SKILL.md loading
- Agent reads skills, fetches bot context from eval service, runs directive allocation
- Correct tool routing (bot_context instead of get_agent)
- Rubric creation: 5 universal rules (down from 18 workflow-specific in v1)
- Test set creation: 14 items with workflow directives as scenario success criteria
- Evaluation trigger and completion: end-to-end in ~13 minutes
- Headless mode: no longer polls run status indefinitely (commit 1bd5a9a)

## Key Architecture Details

### Files Changed

| File | Change |
|------|--------|
| `indemn_platform/components/deep_agent.py` | Added skills/skills_root to config schema, FilesystemBackend + skills/backend params to create_deep_agent() |
| `scripts/seed_jarvis_templates.py` | Added JARVIS_CORE_PROMPT, EVALUATION_V2_CONNECTOR_IDS, skills/skills_root params, v2 template entry |
| `indemn_platform/api/main.py` | Template ID from JARVIS_TEMPLATE_ID env var, fixed warning message |
| `.dockerignore` | Removed skills/ exclusion |
| `indemn_platform/connectors/.../evaluations.py` | Improved data field descriptions |
| `skills/evaluations/eval-orchestration/SKILL.md` | NEW — workflow coordination + directive allocation |
| `skills/evaluations/rubric-creation/SKILL.md` | NEW — 3-6 rule cap, 3-message universality test |
| `skills/evaluations/test-set-creation/SKILL.md` | NEW — directive-to-criteria mapping, single-turn context rule |

### deepagents API Reference

```python
# create_deep_agent() accepts:
skills: list[str] | None    # e.g. ["/evaluations/"]
backend: BackendProtocol | BackendFactory | None  # e.g. FilesystemBackend

# FilesystemBackend
FilesystemBackend(root_dir="/app/skills", virtual_mode=True)
# virtual_mode=True: sandboxes paths to root_dir, prevents traversal

# Skills auto-add SkillsMiddleware which:
# 1. Scans source paths for subdirs containing SKILL.md
# 2. Parses YAML frontmatter (name must match dir name)
# 3. Injects skill list into system prompt via SKILLS_SYSTEM_PROMPT template
# 4. Agent uses read_file to load full SKILL.md on demand
```

### Deployment Process

```bash
# Push to main triggers GitHub Actions CI/CD
git push origin main
# Build: ghcr.io/indemn-ai/percy-service:main
# Deploy: self-hosted runner at /opt/percy-service

# After deploy, seed templates:
ssh -i ptrkdy.pem ubuntu@ec2-44-196-55-84.compute-1.amazonaws.com \
  "sudo docker exec percy-service python scripts/seed_jarvis_templates.py"

# Restart to pick up template changes:
ssh ... "cd /opt/percy-service && sudo docker compose restart percy-service"

# Trigger headless eval:
curl -X POST http://localhost:8013/api/v1/jarvis/jobs \
  -H "Content-Type: application/json" \
  -H "X-Organization-Id: 676be5a7ab56400012077e7d" \
  -d '{"job_type": "baseline_generation", "bot_ids": ["676be5cbab56400012077f4a"]}'

# Poll job:
curl http://localhost:8013/api/v1/jarvis/jobs/<job_id> \
  -H "X-Organization-Id: 676be5a7ab56400012077e7d"
```
