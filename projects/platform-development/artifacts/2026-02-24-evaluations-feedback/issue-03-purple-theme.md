---
ask: "Deep dive into COP-325 Issue 3: Purple theme colors don't match copilot-dashboard Angular host"
created: 2026-02-24
workstream: platform-development
session: 2026-02-24-a
sources:
  - type: github
    description: "indemn-platform-v2/ui/src — constants.ts, TestSetDetail.tsx, ComponentScoreBadge.tsx, ScopeFilterChips.tsx, QuestionSetDetail.tsx, RubricsList.tsx, QuestionSetsList.tsx"
  - type: github
    description: "copilot-dashboard/src — _variables.scss ($brand-primary: #1E40AF), bot-details.component.scss, sidebar.component.scss"
  - type: linear
    description: "COP-325 Issue 3 screenshot"
---

# Issue 3: Purple Theme — Federated Components Don't Match Angular Host Colors

## Feedback (from Dhruv)

The Evaluation Run card and Agent Card use green/purple accent colors that don't match the copilot-dashboard brand.

## Assessment

The React evaluation components are federated into the Angular copilot-dashboard via Shadow DOM (`createShadowMount`). The Angular host app uses a **blue/slate** color scheme:

- **`$brand-primary: #1E40AF`** — dark blue (buttons, tabs, active states)
- **`tw-text-blue-600`** — links, breadcrumbs
- **`tw-bg-blue-100`** / **`tw-border-blue-200`** — sidebar, light accents
- **`tw-text-slate-800`** — body text
- **`tw-bg-white`** / **`tw-bg-[#F6F8FA]`** — backgrounds

The React components use Tailwind `purple-500` which appears nowhere in the Angular app. This creates a visual mismatch where the federated evaluation UI looks like it belongs to a different product.

### Federated mount points (all affected)

These React components are mounted into Angular via `createShadowMount`:
1. **AgentOverview** → `AgentDetailV1` → `EvaluationSection`, `ComponentScoreBadge`
2. **EvaluationsPanel** → `RubricsManager`, `TestSetsManager` (contains `TestSetDetail`, `RubricsList`, `QuestionSetDetail`, `QuestionSetsList`, `ScopeFilterChips`)
3. **EvaluationRunDetail** → `FederatedEvaluationRunDetail` → `EvaluationSummaryDashboard`, `TestResultCard`, `EvaluationMatrix`
4. **OrgEvaluations** — org-level evaluations page

### Violation 1: Scenario type badges and filter — `TestSetDetail.tsx`

Line 120 — scenario type badge:
```tsx
scenario: 'bg-purple-500/10 text-purple-500',
```

Line 211 — scenario filter button active state:
```tsx
? 'bg-purple-500 text-white'
```

Single-turn uses `bg-blue-500/10 text-blue-500` — already in the blue family but light. Scenarios use purple which clashes.

### Violation 2: Scope indicator color — `constants.ts`

Line 7:
```ts
prompt: '#8b5cf6',
```

This is Tailwind purple-500 hex. Applied as `style={{ backgroundColor: ... }}` on scope indicator dots in:
- `QuestionSetDetail.tsx` line 295
- `RubricsList.tsx` line 232
- `QuestionSetsList.tsx` line 232
- `ScopeFilterChips.tsx` line 55

### Violation 3: `bg-background` in federated containers (Issue 4 — card background)

Several components apply `bg-background` specifically in federated mode. In the React light theme, `--color-background` resolves to `#f8f9fc` (light blue-gray). The Angular host uses `tw-bg-white` (`#ffffff`). This creates a subtle tinted background behind the federated components that doesn't match the host.

Federated-specific `bg-background` usages:
- `AgentDetailV1.tsx` line 225: `"p-6 w-7/8 space-y-8 bg-background"` (federated path)
- `AgentDetailV1.tsx` line 237: `"p-6 w-7/8 bg-background"` (federated path)
- `AgentDetailV1.tsx` line 258: `"p-6 w-7/8 bg-background"` (federated path)
- `FederatedEvaluationRunDetail.tsx` line 149: `"p-6 w-7/8 space-y-8 bg-background"` (federated path)
- `FederatedEvaluationRunDetail.tsx` line 163: `"p-6 w-7/8 bg-background"` (federated path)
- `EvaluationsPanel.tsx` line 127: `"p-6 w-7/8 bg-background"` (federated path)

### Violation 4: ComponentScoreBadge — `ComponentScoreBadge.tsx`

Lines 47-53 use Tailwind default semantic colors (`text-green-600 bg-green-100`, etc.) instead of the design system tokens used everywhere else in the evaluation UI (`text-success bg-success/10`). Not purple, but inconsistent with the rest of the federated components.

## Resolution

All changes use the Angular host's blue family to maintain visual consistency across federation.

### 1. TestSetDetail.tsx — scenario badges and filter → blue shades

Use lighter blue for single-turn, darker blue (closer to Angular's `$brand-primary: #1E40AF`) for scenarios:

```tsx
// Line 118-121 — getTypeBadge styles
const styles: Record<string, string> = {
  single_turn: 'bg-blue-500/10 text-blue-500',     // keep — already blue family
  scenario: 'bg-blue-800/10 text-blue-800',         // was purple-500 → dark blue
};
```

```tsx
// Line 199-201 — single-turn filter button (already blue, keep)
typeFilter === 'single_turn'
  ? 'bg-blue-500 text-white'
  : 'bg-surface-2 text-muted hover:text-foreground'
```

```tsx
// Line 209-211 — scenario filter button
typeFilter === 'scenario'
  ? 'bg-blue-800 text-white'                        // was purple-500
  : 'bg-surface-2 text-muted hover:text-foreground'
```

### 2. constants.ts — prompt scope color → Angular brand primary

```ts
export const SCOPE_COLORS: Record<string, string> = {
  prompt: '#1E40AF',        // was '#8b5cf6' (purple) → Angular $brand-primary
  knowledge_base: '#3b82f6', // blue-500 — keep, already in blue family
  function: '#10b981',       // emerald — semantic green for functions, keep
  general: '#6b7280',        // gray — keep
};
```

This affects scope indicator dots in `QuestionSetDetail`, `RubricsList`, `QuestionSetsList`, and `ScopeFilterChips`.

### 3. Federated containers — `bg-background` → `bg-transparent`

Replace `bg-background` with `bg-transparent` in all federated paths so the Angular host's white background shows through:

- `AgentDetailV1.tsx` lines 225, 237, 258: replace `bg-background` with `bg-transparent`
- `FederatedEvaluationRunDetail.tsx` lines 149, 163: replace `bg-background` with `bg-transparent`
- `EvaluationsPanel.tsx` line 127: replace `bg-background` with `bg-transparent`

### 4. ComponentScoreBadge.tsx — Tailwind defaults → design system tokens

```tsx
// Lines 47-53
if (percentage >= SCORE_THRESHOLDS.SUCCESS * 100) {
  colorClass = 'text-success bg-success/10';         // was text-green-600 bg-green-100
  Icon = CheckCircle;
} else if (percentage >= SCORE_THRESHOLDS.WARNING * 100) {
  colorClass = 'text-warning bg-warning/10';         // was text-yellow-600 bg-yellow-100
  Icon = AlertTriangle;
} else {
  colorClass = 'text-error bg-error/10';             // was text-red-600 bg-red-100
  Icon = XCircle;
}
```

This aligns with the semantic color pattern used by `EvaluationRunDetail.tsx` status badges and `scoring.ts` color classes.

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `ui/src/components/evaluation/TestSetDetail.tsx` | purple → blue-800 (badges + filter) | 120, 211 |
| `ui/src/components/evaluation/constants.ts` | `#8b5cf6` → `#1E40AF` (prompt scope) | 7 |
| `ui/src/pages/AgentDetailV1.tsx` | `bg-background` → `bg-transparent` in federated paths | 225, 237, 258 |
| `ui/src/federation/components/FederatedEvaluationRunDetail.tsx` | `bg-background` → `bg-transparent` in federated paths | 149, 163 |
| `ui/src/components/evaluation/EvaluationsPanel.tsx` | `bg-background` → `bg-transparent` in federated path | 127 |
| `ui/src/components/evaluation/ComponentScoreBadge.tsx` | Tailwind defaults → design system tokens | 47-53 |

**Note:** This also resolves Issue 4 (card background color `#f8f9fc`).

## Complexity

Low — color value replacements across 6 files. No logic changes.

## Linear Response (draft)

> Fixed (also covers Issue 4 — card background). Aligned all federated evaluation components to match the copilot-dashboard's blue/slate palette:
> - Scenario badges/filters now use `blue-800` (matching `$brand-primary`) instead of `purple-500`
> - Prompt scope indicator color now uses `#1E40AF` instead of `#8b5cf6`
> - Removed `#f8f9fc` tinted background from federated containers — now transparent so the Angular host's white background shows through
> - Component score badges now use the shared design system tokens (`text-success`, `text-warning`, `text-error`)
