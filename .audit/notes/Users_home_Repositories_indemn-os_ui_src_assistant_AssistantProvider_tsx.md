# Notes: /Users/home/Repositories/indemn-os/ui/src/assistant/AssistantProvider.tsx

**File:** /Users/home/Repositories/indemn-os/ui/src/assistant/AssistantProvider.tsx
**Read:** 2026-04-16 (full file — 82 lines)
**Category:** code-ui

## Key Claims

- React provider for assistant state (messages, isOpen, isStreaming).
- `sendMessage(content)` — POST to `/api/assistant/message` with user JWT, reads streaming text response.
- `togglePanel` — toggles `isOpen`.
- Builds context from `window.location.pathname`: `{view_type, current_path}`.
- Renders children + `AssistantPanel`.

## Architectural Decisions

- Assistant UI uses HTTP POST + streaming text response (not WebSocket).
- Auth: user's JWT via Bearer header (matches design — "inherits user's session").
- Context: minimal (view_type + path) — much simpler than the design's expected context (view_type, current_entity, current_filter, role_focus, recent_actions).
- Streaming: reads response body as chunks, updates last message reactively.
- Error handling: replaces streaming message with error text if fetch fails.

## Layer/Location Specified

- UI code: `ui/src/assistant/AssistantProvider.tsx`.
- Runs in browser.
- Talks to kernel API endpoint `/api/assistant/message` (in kernel/api/assistant.py).

**Layer issue (inherited from kernel side):**
- Per design, the assistant should be a running chat-harness instance, not a kernel endpoint. The UI would connect via WebSocket to the chat-harness runtime (which lives outside the kernel).
- Current implementation has UI calling a kernel API endpoint, which then calls Anthropic directly (no tools, no harness).
- The UI provider here does NOT cause Finding 0 — it follows whatever the backend provides. The layer issue is on the backend side (`kernel/api/assistant.py`).

## Dependencies Declared

- React: `useState`, `useCallback`, `ReactNode`
- `./useAssistant` — context definition
- `./AssistantPanel` — UI panel
- `../api/client.getToken` — retrieves user's JWT from client storage
- `window.location.pathname` — for context building

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/ui/src/assistant/AssistantProvider.tsx`
- Related:
  - `ui/src/assistant/useAssistant.ts` — context definition
  - `ui/src/assistant/AssistantPanel.tsx` — panel UI
  - `ui/src/assistant/AssistantInput.tsx` — top-bar input
  - `ui/src/api/client.ts` — HTTP client + token storage

## Cross-References

- Design: 2026-04-11-base-ui-operational-surface.md §4.7 The Assistant
- Phase 4-5 spec §4.7 Assistant Hook
- Kernel endpoint: `kernel/api/assistant.py::assistant_message`

## Open Questions or Ambiguities

**Pass 2 findings:**
- **UI implements HTTP + streaming pattern matching the kernel-endpoint assistant.** If the assistant were a proper chat-harness, the UI would likely use WebSocket (per realtime-architecture-design's harness pattern for chat), and the connection management would be different (long-lived WebSocket vs. one-shot HTTP POST).
- **Context is minimal** — just view_type + path. Per design (base-ui-operational-surface.md §4.7):
  ```
  {
    "view_type": "EntityDetail",
    "current_entity": {"type": "Submission", "id": "SUB-042"},
    "current_filter": null,
    "role_focus": "underwriter",
    "recent_actions": [...]
  }
  ```
  Current implementation has only `{view_type, current_path}`. Additional context (current_entity, filter, role_focus, recent_actions) is missing. Needs richer context building in future iterations.
- **No inline entity rendering** in this provider — streaming just builds a text string. The design calls for "inline entity renderings" but implementation uses plain text. Deferred to post-MVP per spec.

**Secondary observations:**
- Auth is handled at the fetch level via `getToken()` — consistent with the user-session-inheritance design.
- Error recovery is minimal — user sees "Error: could not reach assistant" with no retry.
- The streaming uses `TextDecoder().decode()` on each chunk — handles partial UTF-8 characters potentially incorrectly; typically OK for English but edge case in multi-byte chars.

This UI provider is a reasonable implementation for the kernel-endpoint-based assistant. When the architecture moves to chat-harness, this provider will need to be rewritten to use WebSocket and handle structured messages with tool results and entity renderings.
