# Notes: /Users/home/Repositories/indemn-os/ui/src/assistant/useAssistant.ts

**File:** /Users/home/Repositories/indemn-os/ui/src/assistant/useAssistant.ts
**Read:** 2026-04-16 (full file — 27 lines)
**Category:** code-ui

## Key Claims

- Defines `AssistantMessage` interface: `{id, role: "user"|"assistant", content}`.
- Defines `AssistantContextType` interface: `{messages, isOpen, isStreaming, togglePanel, sendMessage}`.
- Creates `AssistantContext` with default no-op values.
- Exports `useAssistant()` hook — thin wrapper around `useContext(AssistantContext)`.

## Architectural Decisions

- Standard React context pattern for sharing assistant state across the UI.
- Message schema is minimal: id, role, content — plain text only.
- Default context values are no-ops (prevents crashes if hook used outside provider).

## Layer/Location Specified

- UI code: `ui/src/assistant/useAssistant.ts`.
- Runs in browser.
- Pure React — no external dependencies.

**No layer concerns for this file.** It's just a React context helper.

## Dependencies Declared

- `react` — `createContext`, `useContext`.

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/ui/src/assistant/useAssistant.ts`
- Context provider: `ui/src/assistant/AssistantProvider.tsx`
- Consumers: `ui/src/assistant/AssistantInput.tsx`, `AssistantPanel.tsx`

## Cross-References

- Design: 2026-04-11-base-ui-operational-surface.md §4.7 (assistant UI pattern)
- Phase 4-5 spec §4.7 Assistant Hook (named `useAssistant`)

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- `AssistantMessage.content` is a string — limits the ability to render structured content (entities, tool results). Design mentions "inline entity renderings" which would require richer content type (e.g., `string | EntityCard | ToolResult`). Current implementation is text-only (matches deferred scope).
- Role field only has "user" | "assistant" — no "tool" role for tool-use interleaving (which Claude API supports). If assistant gains tools, this should expand.

This is a minimal, idiomatic React context hook. No architectural concerns.
