---
ask: "Shake out the endorsement path by manually walking through Steps 1-5 with agent-browser against the Fergerson activity"
created: 2026-02-19
workstream: web-operator
session: 2026-02-19-b
sources:
  - type: web
    description: "Manual walkthrough of path_v1.md Steps 1-5 against Applied Epic demo (johns87.appliedepic.com) using agent-browser CLI"
---

# Endorsement Path Shakeout — Steps 1-5

## Summary

Walked through Steps 1-5 of `paths/ecm_cap_endorsement/path_v1.md` against the Fergerson activity (#1 BAUT — "Remove the 1978 Ford F150"). Steps 1-4 work well with minor fixes needed. Step 5 hit a blocker: the 2024-2025 BAUT policy period is not visible in Applied Epic's Policies sidebar under any filter.

## Results by Step

### Step 1: Login — WORKS (workaround needed)

The multi-step login flow works: agency code JOHNS87 → Continue → Login button → popup tab → credentials → "already logged in" dialog → Yes → dashboard.

**Issue**: `agent-browser fill` and `agent-browser type` both escape `!` to `\!` in the password (`D@t@Guru!2#`). This causes "Invalid Usercode or Password" on every attempt using the path's documented approach.

**Workaround**: Use the native input value setter via eval to bypass agent-browser's escaping:
```javascript
(function(){
  let input = document.querySelector('input[type=password]');
  let nativeSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 'value'
  ).set;
  nativeSetter.call(input, 'D@t@Guru!2#');
  input.dispatchEvent(new Event('input', {bubbles: true}));
  input.dispatchEvent(new Event('change', {bubbles: true}));
  return input.value;
})()
```

**Path refinement**: Step 1.7 must use the eval-based password entry. The `fill` command works fine for the Usercode field (no special chars).

### Step 2: Collect BAUT Activities — WORKS PERFECTLY

The eval on `.virtual-list-table` finds all 4 BAUT CHG3 activities immediately. No issues. Output matches the inventory exactly.

### Step 3: Open Activity & Read Notes — WORKS PERFECTLY

- Double-click on tagged virtual list row opens the activity correctly
- All fields readable: Code CHG3, Description, Association (Policy - BAUT - CAP500961), Issuing Company (EVECA1 — Everett Cash Mutual), Premium Payable (CA — EVECA1)
- "View All Notes" click via eval works
- Both notes captured:
  - **4/8/2025 BGILBERT**: "Tammy emailed and asked to remove the 1978 Ford F150 Vin #F15HKCJ1062. I submitted the change today."
  - **4/14/2025 AUTOMATION**: "endorsement decs attached"
- Change type correctly identified: vehicle removal, VIN #F15HKCJ1062

### Step 4: Download and Read PDF — WORKS PERFECTLY

**4a (Navigate to Attachments)**: Access menu via real mouse events → dropdown → "Attachments" click works. Verification check ("Attachments - Filtered" vs "Attachments - Last") correctly identifies the right page.

**4b (Find and Download)**: PDF row found by `Automation + .pdf + Policy Documents` filter. Tag-and-dblclick pattern works. Download dialog appears with Install/Download/Cancel buttons. `agent-browser download @ref path` successfully saves the file.

**4c (Read PDF)**: PDF is 3 pages. Key extracted data:
- **REVISED DECLARATION** header confirmed
- Change: "Removed the 1978 Ford F150 Vin #F15HKCJ1062"
- Effective date: 04/07/2025
- Pro-rata premium change: -$68
- Total Premium: $2,155
- Total Endorsement Premiums: $146
- Policy: CAP500961, Period: 05/19/2024 to 05/19/2025

### Step 5: Verify Change in Epic — BLOCKED

**Critical issue**: The 2024-2025 BAUT policy period does NOT appear in the Policies sidebar under ANY filter:

| Filter | Result |
|--------|--------|
| Current/Renewed (default) | "No items found" |
| All Except Marketed | Only 2021-2022 (Historical) and 2022-2023 (Renewed) |
| Expired/History | Same two old periods |

The 2023-2024 and 2024-2025 renewal periods are completely missing from the Policies list for the Fergerson account.

**What was tried**:
1. Sidebar Policies → Current/Renewed: empty
2. Changed filter to All Except Marketed: 9 rows total, only 2 BAUT rows (both old)
3. Changed filter to Expired/History: same result
4. Double-clicked BAUT Renewal (2022-2023): opens policy viewer at wrong period
5. Opened Servicing/Billing > Policy tab: shows 2022-2023 data
6. Tried Association link on activity: not clickable (just text)
7. Right-clicked Association: no context menu
8. Tried Locate menu: shows account list, not policy search
9. Checked Service Summary section below policy list: "No items found"

**Hypothesis**: The demo environment (a copy from spring 2025) may not have the 2024-2025 renewal period imported for the Fergerson account, even though the endorsement activity and automation-generated PDF reference that period.

## Technical Findings

### Eval Quoting for Bash

All complex eval expressions must use heredoc syntax when run through bash to avoid quote mangling:
```bash
agent-browser --session name eval "$(cat <<'JSEOF'
(function(){
  // JavaScript with any quotes — single, double, backtick
  let menubar = document.querySelector('ul.menubar');
  return menubar ? 'found' : 'not found';
})()
JSEOF
)"
```

Without heredoc, smart quotes and special characters cause `SyntaxError: Invalid or unexpected token`.

### Agent-Browser `!` Escaping Bug

Both `fill` and `type` commands escape `!` to `\!`. This is an agent-browser issue, not a bash issue (confirmed by testing with `set +H` and various quoting). The only workaround is setting the value via `eval` with the native input setter + event dispatch for Angular compatibility.

### Applied Epic Navigation Patterns Confirmed

- Virtual list eval for reading activity rows: works reliably
- Tag-and-dblclick pattern for opening rows: works reliably
- Real mouse events for Angular dropdown menus (Access, File): works reliably
- File → Exit for navigation: works reliably
- Progress bar polling: works (loader class `.progress-box`)
- "Attachments - Filtered" vs "Attachments - Last" verification: correctly distinguishes the two pages

## Path Refinements Needed

1. **Step 1 (Login)**: Replace `fill` for password with eval-based native setter approach
2. **Step 5 (Policy Navigation)**: Needs alternative approach when policy period not in default sidebar view. Options to investigate:
   - Navigate from activity association (if Epic supports it via different interaction)
   - Use Locate > Policy search functionality
   - Try opening policy directly via URL pattern if known
   - Check if Rudra's code has a different navigation approach
3. **General**: Add heredoc eval pattern guidance for agent-browser commands (relevant for harness execution if it shells out via bash)

## Next Steps

1. **Investigate the missing policy period** — may need Rudra's input or to try a different test activity (Thanh Tran #0 was updated 2/18/2026 by Rudra and may have the policy visible)
2. **Check Rudra's code** for how the renewal path navigates to the BAUT policy — the renewal flow must solve this same problem
3. **Apply Step 1-4 fixes** to path_v1.md
4. **Resolve Step 5** before running through the harness with Haiku 4.5
