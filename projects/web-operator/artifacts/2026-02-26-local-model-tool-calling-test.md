---
ask: "Can we get a local open-source model running with tool calling for the web operator, so Rudra doesn't need Claude API?"
created: 2026-02-26
workstream: web-operator
session: 2026-02-26-a
sources:
  - type: web
    description: "Research on best open-source models for tool calling in 2026 — Qwen3, Llama 4 Scout, DeepSeek"
  - type: github
    ref: "github.com/indemn-ai/web-operators"
    name: "feat-web-operator-improvement branch — config.py, agent.py"
  - type: local
    description: "Ollama + LangChain tool calling tests on M4 Pro 24GB"
---

# Local Model Tool Calling for Web Operator

## Context

Rudra messaged Craig on Slack (2026-02-26):

> I have created this branch for web operator where the flow that I created is static as it uses scripts to execute the path. So there will be concerns when we have changes in the UI and is also not scalable. I have tried using different models locally like ollama:llama3.1:8b, ollama:qwen3:8b but no success in tool calling. Can you please help me if we can find a better way to tackle this challenge.

His problem: the 8B models he tried can't do reliable tool calling. He needs a local model that works with his framework so he's not paying for Claude API on every run.

## Hardware

- **Machine:** Apple M4 Pro, 24GB unified RAM
- **Ollama:** v0.13.5 (installed at `/opt/homebrew/bin/ollama`)
- **Python:** 3.12.12 (venv at `/Users/home/Repositories/.venv/bin/python3`)

## Research: Best Local Models for Tool Calling (Feb 2026)

| Model | Params (Active) | Size on Disk | Tool Calling Quality | Notes |
|-------|-----------------|-------------|---------------------|-------|
| **Qwen3 14B** | 14B (dense) | 9.3GB | Good | Already installed. Works. Slow (27-33s/turn). |
| **Qwen3 30B-A3B** | 30B (3B active MoE) | 18GB | Excellent | Downloaded. Works. Faster (12-20s/turn after warmup). |
| **Qwen3-Coder 30B-A3B** | 30B (3B active MoE) | ~18GB | Best for agentic | Not tested yet. Built specifically for tool calling. |
| **Llama 4 Scout** | 109B (17B active MoE) | ~11-12GB Q4 | Good | Not tested yet. Fits in 24GB. |
| **Llama 3.1 8B** | 8B | ~4.7GB | Poor | Rudra tested — didn't work. Too small. |
| **Qwen3 8B** | 8B | ~4.7GB | Poor | Rudra tested — didn't work. Too small. |

**Key insight:** 8B models are too small for reliable tool calling. You need 14B+ dense or a large MoE model. The Qwen3 30B-A3B is the sweet spot for this hardware — 30B total params but only 3B active per inference, so it runs fast while having enough capacity for complex tool use.

Sources:
- [Ollama Tool Calling Docs](https://docs.ollama.com/capabilities/tool-calling)
- [Qwen3 on Ollama](https://ollama.com/library/qwen3)
- [Best Ollama Models for Tool Calling](https://clawdbook.org/blog/openclaw-best-ollama-models-2026)
- [Llama 4 Scout on Ollama](https://ollama.com/library/llama4:scout)

## What We Tested

### Test 1: Raw Ollama API — Single Tool Call

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3:14b",
  "messages": [{"role": "user", "content": "What is the weather in San Francisco?"}],
  "tools": [{"type": "function", "function": {"name": "get_weather", ...}}],
  "stream": false
}'
```

**Result:** Model correctly called `get_weather({"location": "San Francisco, CA"})`. Includes chain-of-thought reasoning in a `thinking` field. ~15s total (7.8s model loading, 5.5s generation).

### Test 2: Raw Ollama API — Multi-Tool + Multi-Turn

Simulated a browser automation scenario: navigate → fill field → click → identify next action. Provided 5 browser-like tools (navigate, fill_field, click, screenshot, extract_text).

**Result:** Model correctly:
- Called `navigate` first
- Called `fill_field` with reasonable CSS selector
- Called `click` on the first activity
- Reasoned through CSS selector choices in thinking

**Issue:** Thinking mode generates 500-1000 tokens of reasoning per turn, slowing things down. The `think: false` option and `/no_think` tag in system prompt didn't fully suppress it — it's baked into the Qwen3 chat template.

### Test 3: LangChain `init_chat_model` + Ollama — End-to-End

This is the critical test because Rudra's framework uses `init_chat_model(config.model_name)`.

```python
from langchain.chat_models import init_chat_model
model = init_chat_model("ollama:qwen3:14b")
model_with_tools = model.bind_tools([navigate, fill_field, click, screenshot])
```

**Required package:** `langchain-ollama` (installed via `uv pip install langchain-ollama` into venv).

**Multi-turn test result (Qwen3 14B):**

| Turn | Action | Time |
|------|--------|------|
| 1 | `navigate({'url': 'https://epic.example.com'})` | 27.2s |
| 2 | `fill_field({'selector': "input[placeholder='Enterprise ID']", 'value': 'ENT001'})` | 33.1s |
| 3 | `click({'selector': 'button'})` | 31.8s |
| 4 | [text] "Login successful. Now on the Dashboard..." | 16.9s |

### Test 4: Qwen3 30B-A3B (MoE) — Speed Comparison

**Multi-turn test result (Qwen3 30B-A3B):**

| Turn | Action | Time |
|------|--------|------|
| 1 | `navigate({'url': 'https://epic.example.com'})` | 47.4s (cold start — loading 18GB) |
| 2 | `fill_field({'selector': 'input#enterprise-id', 'value': 'ENT001'})` | 20.3s |
| 3 | `click({'selector': 'button#login'})` | 12.4s |
| 4 | [text] "Login successful..." | 12.9s |

**After warmup, 30B-A3B is ~2x faster per turn** (12-20s vs 27-33s) because it only activates 3B params per forward pass.

## How to Wire Into Rudra's Framework

### The Integration Point

In `src/framework/config.py`:
```python
@dataclass
class AgentConfig:
    model_name: str = "anthropic:claude-sonnet-4-5-20250929"  # ← change this
```

In `src/framework/agent.py`:
```python
model = init_chat_model(config.model_name, thinking={"type": "disabled"})
```

### What Rudra Needs to Do

1. **Add dependency:** `langchain-ollama` to `pyproject.toml`
2. **Install ollama** on his machine and pull the model: `ollama pull qwen3:30b-a3b`
3. **Change one config value:**
   ```python
   model_name: str = "ollama:qwen3:30b-a3b"
   ```
4. **Note on `thinking` param:** The `init_chat_model` call passes `thinking={"type": "disabled"}` which is an Anthropic-specific param. May need to conditionally pass it only for Anthropic models, or wrap in a try/except.
5. **Note on alignment model:** `config.alignment_model` is also set to `"anthropic:claude-haiku-3"` for stall detection. This would also need to change to an ollama model for fully local operation.

### Test 5: Real Browser Automation (Proof of Concept)

Wrote a minimal standalone script (`test_ollama_browser.py`) that bypasses the deepagents framework and tests just: model → tool call → agent-browser → real browser → result → model.

The script gives the model a single `local_execute` tool and a system prompt listing agent-browser CLI commands. Task: navigate to example.com, extract title and heading, close browser.

**Result — Qwen3 14B successfully drove a real browser:**

| Turn | Time | Action | Result |
|------|------|--------|--------|
| 1 | 28.9s | `agent-browser navigate https://example.com --headed` | Browser opened, page loaded |
| 2 | 15.8s | `agent-browser eval "document.title"` | "Example Domain" |
| 3 | 9.6s | `agent-browser eval "document.querySelector('h1').textContent"` | "Example Domain" |
| 4 | 11.1s | `agent-browser close` | Browser closed |
| 5 | 11.6s | [text response] Reported results accurately | Correct summary |

**Total: 78.1s, 5 turns, all correct.** The model followed instructions precisely — one command at a time, observed results, decided next step.

## Test 6: Rudra's Full Framework with Ollama

Attempted to run Rudra's `create_web_operator()` framework with ollama models. Two issues discovered:

### Issue 1: 30B-A3B OOM
The 30B-A3B model (18GB on disk) crashed with "model runner has unexpectedly stopped" when loaded alongside the framework's large system prompt (skills, middleware, path content, guardrails). 18GB model + framework context exceeds 24GB unified RAM.

### Issue 2: Model Ignores Path, Uses Epic Tools
When run with 14B, the model called `epic_login` instead of following the test path's instructions to use `local_execute`. The framework hardcodes 14 Epic-specific tools in `agent.py` — the model sees these specialized tools and gravitates toward them regardless of what the path document says.

**Root cause:** `create_web_operator()` always loads all Epic tools. To test with non-Epic paths, the tool list would need to be configurable — which is exactly the kind of generalization we'd do when building the reusable framework.

### The `thinking` Param
`init_chat_model("ollama:qwen3:14b", thinking={"type": "disabled"})` is silently accepted — no error. Ollama ignores the Anthropic-specific param.

## What Still Needs Testing

- **Quality on real Applied Epic DOM** — the model needs to handle complex, messy HTML and make correct CSS selector decisions from actual page content
- **Running through the full framework** — requires either Epic credentials or making the tool list configurable in `agent.py`
- **Qwen3-Coder 30B-A3B** — potentially better for agentic tool calling, not tested
- **Llama 4 Scout** — 17B active MoE, might be faster/better, not tested
- **Context window limits** — Qwen3 default is 4096 tokens in ollama, may need `num_ctx` override for longer workflows with large DOM content
- **30B-A3B with reduced context** — could work if we lower `num_ctx` or use a Q4 quantization that fits in RAM

## Recommendation

**For Rudra:**
1. Use `qwen3:14b` for local development and testing — it works, fits in 24GB RAM, and does reliable tool calling (10-29s per turn)
2. Add `langchain-ollama` to `pyproject.toml` dependencies
3. The model swap is one config change: `model_name = "ollama:qwen3:14b"`
4. The `thinking` param in `agent.py` is compatible — no code change needed
5. The `alignment_model` for stall detection should also change from `anthropic:claude-haiku-3` to an ollama model

**For the framework:**
- The hardcoded tool list in `agent.py` is the next generalization target — making tools configurable would let the same framework run different automation paths (not just Epic)
- The 30B-A3B MoE is faster per-turn but needs more RAM — would work on a 32GB+ machine or with aggressive quantization

## Honest Assessment: Is Qwen3 14B Powerful Enough?

**No.** Tool calling works mechanically, but the model lacks the reasoning depth for complex multi-step enterprise browser automation.

### What We Observed

- **Simple task (example.com):** Perfect. 5 turns, all correct, followed instructions precisely.
- **Real Applied Epic workflow:** Created a reasonable 9-step plan, then skipped all actual steps and jumped to `epic_update_activity` with hallucinated data. Did not follow the path document.

This is not a tool calling problem — it's an **instruction-following and multi-step reasoning** problem on long, complex prompts.

### What Benchmarks Confirm

- Browser-Use benchmark: even frontier models barely crack 60% on complex browser automation. Gemini 2.5 Flash (a much larger model) scored only 35%.
- On dynamic complex sites (Booking.com), open-source agents achieve only 27.3% accuracy.
- Claude Sonnet 4.5 scores 61.4% on OSWorld — industry leader for browser automation.
- For complex tool integration, Claude Sonnet was "far ahead in both quality and structure" and "the only one that got it right on the first try."
- Qwen3 14B scores 65.1 on Tau2-Bench (simple tool use), but that measures basic function calling, not complex multi-step workflows.

### Why It Fails on This Task

1. **Long context instruction following** — path document is ~7K tokens of step-by-step instructions. 14B can't maintain adherence over a multi-turn workflow.
2. **Sequential multi-step reasoning** — Applied Epic workflow is 20-50+ tool calls in sequence. Model needs coherence across all of them.
3. **Complex DOM interpretation** — Applied Epic is a messy SPA with virtualized tables, popups, dynamic sidebars.
4. **Speed compounds errors** — at 28-32s/turn, sessions timeout and pages change while the model thinks.

### What Rudra Should Do

- **Keep Claude API for production** — it works, cost per run is manageable.
- **Consider hosted open-source API** (Qwen3-235B, DeepSeek-V3.2 via Together/Fireworks) — cheaper than Claude, far more capable than local 14B.
- **His scripts approach is the right optimization** — deterministic scripts handle DOM interaction, model just orchestrates. But even orchestration proved too complex for 14B.

### Sources

- [Browser-Use Benchmark](https://browser-use.com/posts/ai-browser-agent-benchmark)
- [Best AI Browser Agents 2026](https://www.firecrawl.dev/blog/best-browser-agents)
- [Qwen3 vs Claude vs GPT-4 Agent Tasks](https://composio.dev/blog/qwen-3-coder-vs-kimi-k2-vs-claude-4-sonnet-coding-comparison)
- [Qwen3 Official Blog](https://qwenlm.github.io/blog/qwen3/)
- [Top Agentic LLMs 2026](https://www.adaline.ai/blog/top-agentic-llm-models-frameworks-for-2026)

## Hosted API Testing: Gemini 2.5 Flash

### Why Gemini

After researching hosted open-source APIs (Together AI, Fireworks, DeepInfra, DeepSeek direct), we chose **Google Gemini 2.5 Flash** for testing:

| | Gemini 2.5 Flash | Claude Sonnet 4.5 | Claude Haiku 4.5 |
|---|---|---|---|
| Input $/M | $0.15 | $3.00 | $1.00 |
| Output $/M | $0.60 | $15.00 | $5.00 |
| Multimodal | Yes | Yes | Yes |
| Tool calling | Excellent | Best | Excellent |
| Context | 1M | 200K | 200K |
| Savings vs Sonnet | **95%** | — | ~70% |

Reasons: cheapest multimodal option with excellent tool calling, `langchain-google-genai` already installed in the project, Google Cloud reliability, 1M context window.

**Together AI issues:** `langchain-together` package (max v0.3.1) is incompatible with the project's `langchain-core` 1.2.x (uses removed `pydantic_v1`). Qwen3-235B requires a dedicated GPU endpoint (not serverless). Would need OpenAI-compatible wrapper which adds complexity.

### Integration Changes

1. **`agent.py` patched** — made `thinking` param conditional (Anthropic-only):
   ```python
   model_kwargs = {}
   if config.model_name.startswith("anthropic:"):
       model_kwargs["thinking"] = {"type": "disabled"}
   elif config.model_name.startswith("ollama:"):
       model_kwargs["num_ctx"] = 16384
   ```

2. **`langchain-openai` added** — `uv add langchain-openai` (needed for Together AI's OpenAI-compat endpoint, also useful generally)

3. **Anthropic `cache_control` blocks** — Gemini silently ignores them. `SmartCacheMiddleware` works without errors (no benefit, no harm).

4. **API key** — `GOOGLE_API_KEY` added to `.env` in both web_operators and operating-system repos.

### Test Results

**Basic connectivity:** Works. Sub-1.2s per call. Tool calling correct.

**Framework integration:** Works. Gemini made the right tool calls:
- Turn 1: `write_file` (wrote working memory) + `epic_login` (correct Step 1 action)
- Turn 2: Retried `epic_login` after failure (correct retry behavior)
- Response time: ~2s per turn (vs 28-33s with local Qwen3 14B)

**Login failure:** `epic_login` script fails because the Epic Identity Provider popup tab's credential form isn't found. The script looks for "Usercode"/"Password" text on the popup tab but gets the main tab's SIGNON page content instead. This is a **login script bug**, not a model issue — would fail with any model. Needs investigation into why `agent-browser tab switch 1` isn't properly switching context, or whether the IDP form is in an iframe.

### What's Needed Next

1. **Fix the login script** — the `tab switch` to the IDP popup isn't working correctly. Either the tab content isn't being read from the right tab, or the IDP form is inside an iframe that `document.body.innerText` can't see. Need to debug with the browser visible.
2. **Complete a full run** — once login works, run the full CAP renewal path with Gemini to evaluate quality.
3. **Compare Gemini vs Haiku** — Haiku ($1/$5) is 70% cheaper than Sonnet and requires zero code changes (same Anthropic provider, caching works). Gemini ($0.15/$0.60) is 95% cheaper but needs the provider-specific patches above. Quality comparison needed.
4. **Alignment model** — `config.alignment_model` is still set to `anthropic:claude-haiku-3`. If going fully non-Anthropic, this also needs to change.

## Files Created

| File | Location | Purpose |
|------|----------|---------|
| `test_ollama_browser.py` | `/Users/home/Repositories/web_operators/test_ollama_browser.py` | Standalone proof-of-concept: Ollama + agent-browser |
| `paths/test_basic/path_v0.md` | `/Users/home/Repositories/web_operators/paths/test_basic/path_v0.md` | Simple test path for framework testing |
| `paths/test_basic/context.md` | `/Users/home/Repositories/web_operators/paths/test_basic/context.md` | Test path context |
| `paths/test_basic/guardrails.md` | `/Users/home/Repositories/web_operators/paths/test_basic/guardrails.md` | Test path guardrails |

## Setup Steps (for reproducing)

```bash
# 1. Get on Rudra's branch
cd /Users/home/Repositories/web_operators
git checkout -b local-model-test indemn/feat-web-operator-improvement

# 2. Install deps
uv sync
uv add langchain-ollama

# 3. Pull the model
ollama pull qwen3:14b

# 4. Run the proof-of-concept
uv run python test_ollama_browser.py

# 5. Run the full framework (once tool list is configurable)
uv run python -m src.main \
  --path paths/test_basic/path_v0.md \
  --path-version v0 \
  --model "ollama:qwen3:14b"
```
