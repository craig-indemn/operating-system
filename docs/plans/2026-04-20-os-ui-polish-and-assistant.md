# OS UI Polish & Assistant Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix critical UI bugs (horizontal scroll, changes timeline, relationship display), upgrade the assistant model, and polish the base UI for daily team use.

**Architecture:** All changes target the `indemn-os` repo. UI changes are in `ui/src/` (React + TypeScript + TanStack Table + Tailwind). Backend changes are in `kernel/api/` (Python/FastAPI). Harness changes are in `harnesses/chat-deepagents/` (Python/deepagents). The UI auto-generates from entity definitions — no per-entity custom code.

**Tech Stack:** React 18, TypeScript, TanStack React Table v8, Tailwind CSS, react-hook-form, @tanstack/react-query, Starlette WebSocket, deepagents, LangChain

**Repo:** `/Users/home/Repositories/indemn-os/`

---

## Task 1: Fix Horizontal Scrolling on Entity Tables

**Files:**
- Modify: `ui/src/views/EntityListView.tsx:98`
- Modify: `ui/src/layout/Shell.tsx:13`

**Step 1: Add width constraint to EntityListView root div**

In `ui/src/views/EntityListView.tsx` line 98, change:
```tsx
<div>
```
to:
```tsx
<div className="min-w-0">
```

The `overflow-x-auto` on the table wrapper (`EntityTable.tsx:133`) is correct but has no effect because the parent div can expand infinitely. `min-w-0` overrides the default `min-width: auto` on flex children, allowing the content to shrink and the overflow to kick in.

**Step 2: Verify Shell layout passes width constraint**

In `ui/src/layout/Shell.tsx` line 13, verify `main` has proper overflow:
```tsx
<main className="flex-1 p-6 overflow-auto">{children}</main>
```
This is correct. The fix in Step 1 is sufficient because `min-w-0` on the child allows the flex container to constrain it.

**Step 3: Test**
- Open any entity list with many columns (e.g., Company with 20+ fields)
- Verify horizontal scroll bar appears
- Verify scrolling reveals all columns
- Verify sidebar stays fixed during horizontal scroll

**Step 4: Commit**
```bash
git add ui/src/views/EntityListView.tsx
git commit -m "fix(ui): enable horizontal scrolling on entity list tables"
```

---

## Task 2: Fix Changes Timeline (API Response Field Mismatch)

**Files:**
- Modify: `kernel/api/trace_routes.py:89`

**Step 1: Rename `events` to `timeline` in trace entity response**

In `kernel/api/trace_routes.py` line 86-95, change:
```python
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "events": timeline[:limit],
        "sources": {
            "changes": len(changes),
            "messages": len(messages),
            "message_logs": len(message_logs),
        },
    }
```
to:
```python
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "timeline": timeline[:limit],
        "sources": {
            "changes": len(changes),
            "messages": len(messages),
            "message_logs": len(message_logs),
        },
    }
```

The UI hook at `ui/src/api/hooks.ts:63` expects `trace.timeline`. The API currently returns `trace.events`. This single field name mismatch causes the timeline to always show "No changes."

**Step 2: Also fix field name consistency in change entries**

In `kernel/api/trace_routes.py` line 59, the change entries use short names `old`/`new`:
```python
"changes": [{"field": fc.field, "old": fc.old_value, "new": fc.new_value} for fc in c.changes],
```
Change to use the canonical names that match the ChangeRecord schema:
```python
"changes": [{"field": fc.field, "old_value": fc.old_value, "new_value": fc.new_value} for fc in c.changes],
```

The UI hook at `hooks.ts:77-78` already handles both (`c.old_value ?? c.old`), but this makes the API consistent with the schema.

**Step 3: Test**
- Open any entity detail view (e.g., a Company that's been transitioned)
- Verify the "Recent Changes" section shows entries instead of "No changes"
- Verify each entry shows timestamp, change type, and field-level old/new values

**Step 4: Commit**
```bash
git add kernel/api/trace_routes.py
git commit -m "fix(api): rename trace response field 'events' to 'timeline' matching UI hook"
```

---

## Task 3: Upgrade Assistant Model to Gemini 3 Flash

**Files:**
- Modify: `harnesses/chat-deepagents/agent.py:20`

**Step 1: Change default model**

In `harnesses/chat-deepagents/agent.py` line 20, change:
```python
    model_id = llm_config.pop("model", "google_vertexai:gemini-2.0-flash")
```
to:
```python
    model_id = llm_config.pop("model", "google_vertexai:gemini-3-flash-preview")
```

Gemini 3 Flash scores 78% on SWE-bench (vs ~40% for 2.0 Flash) with significantly better agentic reasoning. It's the latest Flash model on Vertex AI.

**Step 2: Commit**
```bash
git add harnesses/chat-deepagents/agent.py
git commit -m "feat(chat-harness): upgrade default model to gemini-3-flash-preview"
```

**Step 3: Deploy and test**
- Redeploy chat harness on Railway
- Open the UI assistant panel
- Ask: "List all companies with status customer"
- Verify the assistant uses the execute tool to run `indemn company list --status customer`
- Verify it returns meaningful results

---

## Task 4: Fix Relationship Display (ObjectIds to Names)

**Files:**
- Modify: `ui/src/api/hooks.ts:20-28`
- Modify: `ui/src/components/ResolvedLink.tsx:21-23`

**Step 1: Add depth parameter to entity detail fetch**

In `ui/src/api/hooks.ts` lines 20-28, change `useEntity`:
```typescript
export function useEntity(entityName: string, entityId: string) {
  return useQuery({
    queryKey: ["entity", entityName, entityId],
    queryFn: () =>
      apiClient<Record<string, unknown>>(
        `/api/${entityName.toLowerCase()}s/${entityId}`
      ),
    enabled: !!entityId,
  });
}
```
to:
```typescript
export function useEntity(entityName: string, entityId: string) {
  return useQuery({
    queryKey: ["entity", entityName, entityId],
    queryFn: () =>
      apiClient<Record<string, unknown>>(
        `/api/${entityName.toLowerCase()}s/${entityId}?depth=2&include_related=true`
      ),
    enabled: !!entityId,
  });
}
```

**Step 2: Improve ResolvedLink loading state**

In `ui/src/components/ResolvedLink.tsx` lines 21-23, change:
```typescript
  const displayName = data
    ? String(data.name || data.email || data.title || entityId.slice(-8))
    : entityId.slice(-8) + "\u2026";
```
to:
```typescript
  const displayName = data
    ? String(data.name || data.email || data.title || entityId.slice(-8))
    : "Loading\u2026";
```

Users see "Loading..." instead of a cryptic truncated ObjectId while async resolution happens.

**Step 3: Test**
- Open any Company detail view
- Verify relationship fields (owner, standin, engineering_lead) show human names
- Verify clicking a relationship link navigates to the related entity

**Step 4: Commit**
```bash
git add ui/src/api/hooks.ts ui/src/components/ResolvedLink.tsx
git commit -m "fix(ui): resolve relationship ObjectIds to names via depth=2 fetch"
```

---

## Task 5: Add Toast Notification System

**Files:**
- Create: `ui/src/components/Toast.tsx`
- Create: `ui/src/context/ToastContext.tsx`
- Modify: `ui/src/main.tsx` (wrap app in ToastProvider)
- Modify: `ui/src/views/EntityDetailView.tsx` (replace alert() calls)
- Modify: `ui/src/views/EntityCreateView.tsx` (add success toast)

**Step 1: Create Toast component and context**

Create `ui/src/context/ToastContext.tsx`:
```tsx
import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

interface Toast {
  id: string;
  message: string;
  type: "success" | "error" | "info";
}

interface ToastContextType {
  toast: (message: string, type?: Toast["type"]) => void;
}

const ToastContext = createContext<ToastContextType>({ toast: () => {} });

export function useToast() {
  return useContext(ToastContext);
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: Toast["type"] = "info") => {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ toast: addToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`px-4 py-2 rounded shadow-lg text-sm text-white transition-all ${
              t.type === "success" ? "bg-green-600" :
              t.type === "error" ? "bg-red-600" : "bg-gray-700"
            }`}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
```

**Step 2: Wrap app in ToastProvider**

In `ui/src/main.tsx`, wrap the app component in `<ToastProvider>`.

**Step 3: Replace alert() calls in EntityDetailView**

In `ui/src/views/EntityDetailView.tsx`, replace all `alert(...)` calls with `toast(message, "error")`.

Replace the transition error handler (line 77):
```tsx
alert(`Transition failed: ${err instanceof Error ? err.message : String(err)}`);
```
with:
```tsx
toast(`Transition failed: ${err instanceof Error ? err.message : String(err)}`, "error");
```

Do the same for capability errors (line 96) and method errors (line 117).

Add success feedback after transition (line 75, before `refetch()`):
```tsx
toast(`Transitioned to ${to}`, "success");
```

**Step 4: Add success toast on entity creation**

In `ui/src/views/EntityCreateView.tsx` line 52, before `navigate(...)`:
```tsx
toast(`${entityName} created`, "success");
```

**Step 5: Commit**
```bash
git add ui/src/context/ToastContext.tsx ui/src/main.tsx ui/src/views/EntityDetailView.tsx ui/src/views/EntityCreateView.tsx
git commit -m "feat(ui): add toast notification system, replace alert() calls"
```

---

## Task 6: Add Pagination Count and Page Indicator

**Files:**
- Modify: `ui/src/views/EntityListView.tsx:178-201`

**Step 1: Show total count and page number**

In `ui/src/views/EntityListView.tsx` lines 178-201, replace the pagination section:
```tsx
      {/* Pagination */}
      <div className="flex items-center justify-between mt-4 text-sm text-gray-500">
        <span>
          {(entities?.length || 0) > 0
            ? `Showing ${page * PAGE_SIZE + 1}–${page * PAGE_SIZE + (entities?.length || 0)}`
            : "No results"}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-3 py-1 border rounded disabled:opacity-30 hover:bg-gray-50"
          >
            ← Previous
          </button>
          <span className="px-2 py-1 text-gray-400">Page {page + 1}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={(entities?.length || 0) < PAGE_SIZE}
            className="px-3 py-1 border rounded disabled:opacity-30 hover:bg-gray-50"
          >
            Next →
          </button>
        </div>
      </div>
```

Adds "Page N" indicator between Previous/Next buttons.

**Step 2: Commit**
```bash
git add ui/src/views/EntityListView.tsx
git commit -m "feat(ui): add page indicator to entity list pagination"
```

---

## Task 7: Add Form Validation for Required Fields

**Files:**
- Modify: `ui/src/components/EntityForm.tsx:20-51`

**Step 1: Add validation rules from entity meta**

In `ui/src/components/EntityForm.tsx`, update the form to use validation:
```tsx
export function EntityForm({ meta, entity, onSave, isCreate }: Props) {
  const {
    control,
    handleSubmit,
    formState: { isDirty, isSubmitting, errors },
  } = useForm({ defaultValues: entity as Record<string, unknown> });

  const editableFields = meta.fields.filter(
    (f) => !f.name.startsWith("_") && !SYSTEM_FIELDS.has(f.name)
  );

  return (
    <form onSubmit={handleSubmit(onSave)} className="space-y-4">
      {editableFields.map((field) => (
        <div key={field.name}>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {field.description || field.name.replace(/_/g, " ")}
            {field.required && <span className="text-red-500 ml-0.5">*</span>}
          </label>
          <FormField
            field={field}
            control={control}
            rules={field.required ? { required: `${field.name.replace(/_/g, " ")} is required` } : undefined}
          />
          {errors[field.name] && (
            <p className="text-red-500 text-xs mt-1">
              {String(errors[field.name]?.message || "Required")}
            </p>
          )}
        </div>
      ))}
      {meta.permissions.write && (
        <button
          type="submit"
          disabled={(!isDirty && !isCreate) || isSubmitting}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
        >
          {isSubmitting ? "Saving..." : "Save"}
        </button>
      )}
    </form>
  );
}
```

**Step 2: Update FormField to accept rules prop**

In `ui/src/components/FormField.tsx`, add `rules` to the props and pass them to the Controller from react-hook-form.

**Step 3: Commit**
```bash
git add ui/src/components/EntityForm.tsx ui/src/components/FormField.tsx
git commit -m "feat(ui): add form validation for required fields with error messages"
```

---

## Task 8: Populate Create Form Defaults from Entity Definition

**Files:**
- Modify: `ui/src/views/EntityCreateView.tsx:21-27`

**Step 1: Use field defaults from meta**

In `ui/src/views/EntityCreateView.tsx` lines 21-27, change:
```tsx
  const emptyEntity: Record<string, unknown> = {};
  for (const field of meta.fields) {
    if (!field.name.startsWith("_")) {
      emptyEntity[field.name] = "";
    }
  }
```
to:
```tsx
  const emptyEntity: Record<string, unknown> = {};
  for (const field of meta.fields) {
    if (!field.name.startsWith("_") && !["org_id", "version", "created_at", "updated_at", "created_by"].includes(field.name)) {
      emptyEntity[field.name] = field.default != null ? field.default : "";
    }
  }
```

This respects default values defined in entity definitions (e.g., `status: "prospect"` for Company, `stage: "contact"` for Deal).

**Step 2: Commit**
```bash
git add ui/src/views/EntityCreateView.tsx
git commit -m "feat(ui): populate create form with field defaults from entity definition"
```

---

## Task 9: Add Contextual Empty States

**Files:**
- Modify: `ui/src/components/EntityTable.tsx:232-241`

**Step 1: Improve empty state with contextual message**

In `ui/src/components/EntityTable.tsx` lines 232-241, change:
```tsx
            {table.getRowModel().rows.length === 0 && (
              <tr>
                <td
                  colSpan={allColumns.length}
                  className="px-4 py-8 text-center text-gray-400 text-sm"
                >
                  No data
                </td>
              </tr>
            )}
```
to:
```tsx
            {table.getRowModel().rows.length === 0 && (
              <tr>
                <td
                  colSpan={allColumns.length}
                  className="px-4 py-12 text-center text-sm"
                >
                  <p className="text-gray-400">No results found</p>
                  {(columnFilters.length > 0) && (
                    <button
                      onClick={() => setColumnFilters([])}
                      className="mt-2 text-blue-600 hover:underline text-xs"
                    >
                      Clear filters
                    </button>
                  )}
                </td>
              </tr>
            )}
```

**Step 2: Commit**
```bash
git add ui/src/components/EntityTable.tsx
git commit -m "feat(ui): contextual empty states with clear-filter action"
```

---

## Task 10: Persist Column Visibility to localStorage

**Files:**
- Modify: `ui/src/components/EntityTable.tsx:33`

**Step 1: Use localStorage for column visibility**

In `ui/src/components/EntityTable.tsx`, replace line 33:
```tsx
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
```

Add a storageKey prop to the component and use it:
```tsx
// Add to Props interface:
  storageKey?: string;

// Replace state initialization:
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>(() => {
    if (!storageKey) return {};
    try {
      const stored = localStorage.getItem(`col-vis-${storageKey}`);
      return stored ? JSON.parse(stored) : {};
    } catch { return {}; }
  });
```

Add an effect to persist changes:
```tsx
  useEffect(() => {
    if (storageKey && Object.keys(columnVisibility).length > 0) {
      localStorage.setItem(`col-vis-${storageKey}`, JSON.stringify(columnVisibility));
    }
  }, [columnVisibility, storageKey]);
```

Pass `storageKey={entityName}` from EntityListView when rendering EntityTable.

**Step 2: Commit**
```bash
git add ui/src/components/EntityTable.tsx ui/src/views/EntityListView.tsx
git commit -m "feat(ui): persist column visibility preferences to localStorage"
```

---

## Task 11: Encode Search/Filter State in URL

**Files:**
- Modify: `ui/src/views/EntityListView.tsx`

**Step 1: Sync search and stateFilter with URL query params**

In `ui/src/views/EntityListView.tsx`, add `useSearchParams`:
```tsx
import { useState, useEffect } from "react";
import { useNavigate, useParams, Link, useSearchParams } from "react-router-dom";
```

Initialize state from URL:
```tsx
  const [searchParams, setSearchParams] = useSearchParams();
  const [search, setSearch] = useState(searchParams.get("search") || "");
  const [stateFilter, setStateFilter] = useState(searchParams.get("status") || "");
  const [page, setPage] = useState(Number(searchParams.get("page") || "0"));
```

Add an effect to sync state to URL:
```tsx
  useEffect(() => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (stateFilter) params.set("status", stateFilter);
    if (page > 0) params.set("page", String(page));
    setSearchParams(params, { replace: true });
  }, [search, stateFilter, page, setSearchParams]);
```

This makes filtered views bookmarkable and shareable.

**Step 2: Commit**
```bash
git add ui/src/views/EntityListView.tsx
git commit -m "feat(ui): sync search and filter state with URL query params"
```

---

## Task 12: Add Favicon and Dynamic Page Titles

**Files:**
- Modify: `ui/index.html:6`
- Modify: `ui/src/views/EntityListView.tsx`
- Modify: `ui/src/views/EntityDetailView.tsx`
- Modify: `ui/src/views/EntityCreateView.tsx`

**Step 1: Add favicon**

In `ui/index.html`, add after `<meta name="viewport">`:
```html
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#x2B21;</text></svg>" />
```

Uses a hexagon SVG inline (no external file needed). Can be replaced with a proper Indemn logo later.

**Step 2: Add dynamic page titles**

In each view, add a `useEffect` to set `document.title`:

EntityListView (after the meta/loading check):
```tsx
  useEffect(() => { document.title = `${entityName} List - Indemn OS`; }, [entityName]);
```

EntityDetailView (after entity loads):
```tsx
  useEffect(() => {
    if (entity) {
      const name = String(entity.name || entity.title || entityId);
      document.title = `${name} - ${entityName} - Indemn OS`;
    }
  }, [entity, entityName, entityId]);
```

EntityCreateView:
```tsx
  useEffect(() => { document.title = `New ${entityName} - Indemn OS`; }, [entityName]);
```

**Step 3: Commit**
```bash
git add ui/index.html ui/src/views/EntityListView.tsx ui/src/views/EntityDetailView.tsx ui/src/views/EntityCreateView.tsx
git commit -m "feat(ui): add favicon and dynamic page titles per view"
```

---

## Task 13: Add Breadcrumb Navigation

**Files:**
- Create: `ui/src/components/Breadcrumb.tsx`
- Modify: `ui/src/views/EntityDetailView.tsx`
- Modify: `ui/src/views/EntityCreateView.tsx`

**Step 1: Create Breadcrumb component**

Create `ui/src/components/Breadcrumb.tsx`:
```tsx
import { Link } from "react-router-dom";

interface Crumb {
  label: string;
  to?: string;
}

export function Breadcrumb({ crumbs }: { crumbs: Crumb[] }) {
  return (
    <nav className="flex items-center gap-1 text-sm text-gray-500 mb-4">
      {crumbs.map((crumb, i) => (
        <span key={i} className="flex items-center gap-1">
          {i > 0 && <span>/</span>}
          {crumb.to ? (
            <Link to={crumb.to} className="text-blue-600 hover:underline">{crumb.label}</Link>
          ) : (
            <span className="text-gray-700 font-medium">{crumb.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
```

**Step 2: Replace back links with breadcrumbs**

In `EntityDetailView.tsx`, replace the back link (lines 35-41) with:
```tsx
<Breadcrumb crumbs={[
  { label: entityName, to: `/${entityType}` },
  { label: String(entity.name || entity.title || entityId || "") },
]} />
```

In `EntityCreateView.tsx`, replace the back link (lines 31-37) with:
```tsx
<Breadcrumb crumbs={[
  { label: entityName, to: `/${entityType}` },
  { label: "New" },
]} />
```

**Step 3: Commit**
```bash
git add ui/src/components/Breadcrumb.tsx ui/src/views/EntityDetailView.tsx ui/src/views/EntityCreateView.tsx
git commit -m "feat(ui): add breadcrumb navigation to detail and create views"
```

---

## Task 14: Show Assistant Context Badge

**Files:**
- Modify: `ui/src/assistant/AssistantPanel.tsx`

**Step 1: Show current context in assistant panel**

At the top of the assistant panel, show what context the assistant has. Read the current entity type/id from the URL and display a small badge:

```tsx
// Inside the panel header area:
const location = useLocation();
const parts = location.pathname.split("/").filter(Boolean);
const contextLabel = parts.length === 2
  ? `Viewing: ${parts[0]} detail`
  : parts.length === 1 && parts[0] !== "queue"
    ? `Viewing: ${parts[0]} list`
    : "Viewing: Queue";

// Render:
<div className="text-xs text-gray-400 px-3 py-1 border-b">{contextLabel}</div>
```

This helps users understand what the assistant "sees" about their current view.

**Step 2: Commit**
```bash
git add ui/src/assistant/AssistantPanel.tsx
git commit -m "feat(ui): show assistant context badge indicating current view"
```

---

## Task 15: Add Keyboard Shortcut Help

**Files:**
- Create: `ui/src/components/KeyboardHelp.tsx`
- Modify: `ui/src/layout/TopBar.tsx`

**Step 1: Create keyboard help modal**

Create `ui/src/components/KeyboardHelp.tsx`:
```tsx
import { useState, useEffect } from "react";

export function KeyboardHelp() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "?" && !e.ctrlKey && !e.metaKey && 
          !(e.target instanceof HTMLInputElement) && 
          !(e.target instanceof HTMLTextAreaElement)) {
        setOpen((v) => !v);
      }
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setOpen(false)}>
      <div className="bg-white rounded-lg shadow-xl p-6 w-80" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-sm font-semibold mb-3">Keyboard Shortcuts</h2>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-gray-600">Open assistant</span><kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-xs font-mono">/</kbd></div>
          <div className="flex justify-between"><span className="text-gray-600">Open assistant</span><kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-xs font-mono">Cmd+K</kbd></div>
          <div className="flex justify-between"><span className="text-gray-600">Close panel</span><kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-xs font-mono">Esc</kbd></div>
          <div className="flex justify-between"><span className="text-gray-600">This help</span><kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-xs font-mono">?</kbd></div>
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Add to Shell or TopBar**

Import and render `<KeyboardHelp />` in Shell.tsx alongside the children.

**Step 3: Commit**
```bash
git add ui/src/components/KeyboardHelp.tsx ui/src/layout/Shell.tsx
git commit -m "feat(ui): add keyboard shortcut help modal (press ? to toggle)"
```

---

## Summary

| Task | Category | What |
|------|----------|------|
| 1 | Critical | Fix horizontal scrolling |
| 2 | Critical | Fix changes timeline |
| 3 | Critical | Upgrade assistant model |
| 4 | Critical | Fix relationship display |
| 5 | Important | Toast notification system |
| 6 | Important | Pagination page indicator |
| 7 | Important | Form validation |
| 8 | Important | Create form defaults |
| 9 | Important | Empty states |
| 10 | Important | Persist column visibility |
| 11 | Important | URL-synced filters |
| 12 | Polish | Favicon + page titles |
| 13 | Polish | Breadcrumb navigation |
| 14 | Polish | Assistant context badge |
| 15 | Polish | Keyboard shortcut help |

**Total: 15 tasks.** Tasks 1-4 are independent and can be parallelized. Tasks 5-11 are independent of each other. Tasks 12-15 are independent polish items.
