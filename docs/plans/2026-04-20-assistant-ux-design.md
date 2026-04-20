# Assistant UX Design — Indemn OS

**Date:** 2026-04-20
**Status:** Approved

## Thesis

The assistant is a full operator — a resizable split pane that works in tandem with entity views as a peer surface into the same system. It's context-aware (knows what you're looking at) but never constrained to it. Entity views are one lens; the assistant is the lens that can look at anything.

---

## 1. Layout & Pane Behavior

The assistant is a **resizable split pane on the right side** of the screen.

- **Default state:** Collapsed (vertical grab handle or button on right edge)
- **Open state:** Resizable from ~300px to 60% of viewport width. User drags the divider.
- **Persistence:** Open/closed state and width stored in localStorage. Survives navigation and refresh.
- **Input lives in the pane** when open. When collapsed, `/` and `Cmd+K` shortcuts open it.
- **Non-blocking:** Entity views resize to fill remaining space. No overlay, no modal.

Shell layout:
```
[Sidebar | Entity View (flex-1) | Divider | Assistant Pane (user-controlled width)]
```

All sections always in the DOM. Assistant pane collapses to 0 width when closed.

---

## 2. Conversation Model & Persistence

**One active conversation at a time. Full history accessible.**

- **Active conversation:** Tied to an `Interaction` entity. Messages flow through chat harness, persisted via LangGraph MongoDB checkpointer (keyed by Interaction ID).
- **Resume on reconnect:** Pane opens → UI sends last `interaction_id` in WebSocket connect → harness loads checkpoint → agent remembers full history.
- **New conversation:** Button creates new Interaction, clears pane, starts fresh. Old Interaction stays in database.
- **Conversation history:** Dropdown/list at top of pane showing past conversations (last 20). Each shows: first message preview + timestamp. Click to switch — reconnects with that `interaction_id`.
- **Visual indicator:** "Resumed from [date]" divider when loading a previous conversation.

**Agent memory across resume:**
- Full conversation transcript (messages + tool calls)
- Entity context from previous turns
- Does NOT remember current UI state (fresh context sent each turn)

---

## 3. Context Awareness (Convenience, Not Constraint)

**The assistant knows what you're looking at. It never limits what it can do.**

Every message includes a context payload:
- `view_type`: "list", "detail", "create", "queue", "observability"
- `entity_type`: current entity type name
- `entity_id`: if on detail view
- `entity_data`: full entity record from cache
- `active_filters`: search text + state filter + column filters
- `visible_columns`: which columns are toggled on

**Implicit resolution:** "What's the ARR?" while looking at GIC → resolves from context.

**No constraint:** Context is a preamble, not a scope limiter. Agent's skills cover ALL entities. Can query, create, transition anything regardless of current view.

**Context badge:** Subtle text at top of pane: "Context: Company — GIC". Disappears on queue/root.

---

## 4. Inline Rendering & Entity Display

**Structured data renders as interactive components.**

- **Entity tables (list):** Compact interactive table inline in conversation. State badges, clickable names, max ~10 rows with "Show all (N)" link.
- **Entity cards (single):** Card with key fields, state badge, "View →" link to detail.
- **Tool calls:** Collapsible block showing command. Result renders as entity component above.
- **Markdown:** Explanations, summaries, analysis — standard markdown.
- **Click-to-navigate:** Any entity name in a response is a link to its detail view.

**Rendering decision by message type:**
- `type: "response"` → Markdown
- `type: "entity_list"` → Compact EntityTable
- `type: "entity_detail"` → EntityCard
- `type: "tool_call"` → Collapsible command block
- `type: "tool_result"` → Parse as entity data → render component; fall back to code block

---

## 5. Entity Detection (Harness-Level)

**Option A: Harness parses CLI output.** The LLM runs CLI commands naturally. The harness detects entity data in tool results and sends typed messages to the UI.

Detection logic: if a tool result is valid JSON containing objects with `_id` fields → send as `type: "entity_list"` (array) or `type: "entity_detail"` (single object).

Benefits:
- LLM doesn't need special formatting instructions
- Works for any entity type automatically (entity-agnostic)
- Zero prompt engineering for rendering
- Any CLI command returning entity JSON automatically renders as interactive tables

---

## 6. System Prompt & Agent Behavior

**The agent is an operator, not a chatbot.**

Core principles:
- **Action bias:** "When the user asks a question that can be answered by querying data, query it. Don't explain how you would query it. Don't ask permission to look things up."
- **Context handling:** "Use [UI Context] for implicit resolution. If context is insufficient, ask."
- **Destructive confirmation:** Terminal transitions (churned, lost, cancelled, deleted), entity creation, bulk operations → confirm first. Reads, non-terminal transitions, updates → execute immediately.
- **Conciseness:** "Lead with the answer. Don't repeat the question. Show the data."
- **Entity-agnostic:** Skills loaded dynamically from whatever entity definitions exist. Prompt never mentions specific entity types.

---

## 7. Verification Plan (E2E, No Assumptions)

Every piece verified against live system before shipping:

1. **Agent executes CLI** — "list all companies with stage customer" → agent runs command → harness detects entities → UI renders table
2. **Context resolution** — Navigate to GIC, ask "what's the ARR?" → answers from context without command
3. **Cross-entity queries** — From any view, "show me all contacts at GIC" → not scoped to current view
4. **Persistence across refresh** — 3-turn conversation → refresh → messages visible AND agent remembers
5. **Resume from history** — Switch between conversations → verify agent context restores
6. **Entity rendering** — Lists as tables, singles as cards, clickable links navigate
7. **Pane behavior** — Resize, navigate, collapse, reopen → state persists
8. **Destructive confirmation** — "Transition GIC to churned" → agent confirms before executing
9. **Real-world queries** — 10 natural questions a team member would ask. Time responses. Verify accuracy.

---

## 8. What's NOT In This Design (Deferred)

- **Push navigation** — assistant changing what the entity view shows (emergent from inline click-to-navigate instead)
- **Multi-conversation concurrent** — one active at a time is sufficient
- **Handoff to human** — mode switching between associate and human bridge (future)
- **Voice** — voice harness integration with this UX (separate design)
- **Active alerting** — assistant proactively surfacing information (deferred per vision)
