---
name: agent-browser
description: Use when you need to interact with web pages — navigate, read content, fill forms, click buttons, verify UI, take screenshots, or test deployed services in a real browser.
---

# Agent Browser CLI

Browser automation via the `agent-browser` CLI. Use for verifying deployments, testing UI, filling forms, taking screenshots, and any task requiring a real browser.

## Status Check

```bash
agent-browser --version
```

## Core Workflow: Snapshot → Act → Verify

1. **Snapshot** to see the page: `agent-browser snapshot -i`
2. **Act** on elements using their refs: `agent-browser click @e2`
3. **Verify** by taking another snapshot: `agent-browser snapshot -i`

Always snapshot after actions to confirm the result.

## Quick Reference

### Navigation

```bash
agent-browser open --headed <url>  # Open URL (visible browser — required first command)
agent-browser open <url>           # Open URL (headless)
agent-browser back                 # Go back
agent-browser forward              # Go forward
agent-browser reload               # Reload page
agent-browser close                # Close browser
```

**Always pass `--headed` on the first `open` command** so the browser is visible for monitoring. Subsequent commands reuse the same session.

### Reading the Page

```bash
agent-browser snapshot -i          # Interactive elements with refs (PREFERRED)
agent-browser snapshot -i -C       # Include cursor-interactive elements (divs with onclick)
agent-browser snapshot -c          # Compact mode (remove empty structure)
agent-browser snapshot -d 3        # Limit depth to 3 levels
agent-browser snapshot -s "#main"  # Scope to a CSS selector
agent-browser get text @e1         # Get text content of element
agent-browser get value @e3        # Get input value
agent-browser get title            # Page title
agent-browser get url              # Current URL
```

Snapshot output shows elements with refs:
```
- heading "Dashboard" [ref=e1] [level=1]
- textbox "Search" [ref=e2]
- button "Submit" [ref=e3]
```

### Interacting

```bash
agent-browser click @e2            # Click element
agent-browser dblclick @e2         # Double-click
agent-browser fill @e3 "text"     # Clear field and type
agent-browser type @e3 "text"     # Type without clearing
agent-browser press Enter          # Press key (Enter, Tab, Escape, Control+a)
agent-browser hover @e2            # Hover
agent-browser select @e5 "value"  # Select dropdown option
agent-browser check @e6            # Check checkbox
agent-browser uncheck @e6          # Uncheck checkbox
agent-browser scroll down 500      # Scroll down 500px
```

### Selectors (beyond refs)

```bash
agent-browser click "#submit-button"           # CSS ID
agent-browser click "button.primary"           # CSS class
agent-browser click "//button[@type='submit']" # XPath
agent-browser find role button click --name "Submit"  # Semantic: role
agent-browser find text "Sign In" click               # Semantic: text
agent-browser find label "Email" fill "test@test.com" # Semantic: label
```

### Waiting

```bash
agent-browser wait @e3                # Wait for element
agent-browser wait 2000               # Wait 2 seconds
agent-browser wait --text "Success"   # Wait for text
agent-browser wait --url "**/dashboard" # Wait for URL pattern
agent-browser wait --load networkidle # Wait for network idle
```

### Screenshots

```bash
agent-browser screenshot                     # To stdout
agent-browser screenshot path/to/file.png   # Save to file
agent-browser screenshot --full page.png    # Full page
```

### Tabs

```bash
agent-browser tab                   # List tabs
agent-browser tab new <url>         # Open new tab
agent-browser tab 2                 # Switch to tab 2
agent-browser tab close             # Close current tab
```

### State & Sessions

```bash
agent-browser --session my-session open <url>  # Isolated session
agent-browser state save auth.json             # Save cookies/state
agent-browser state load auth.json             # Restore state
```

### JavaScript Eval

```bash
agent-browser eval "document.title"
agent-browser eval "document.querySelectorAll('link[href*=\"style-\"]').length"
```

**CRITICAL: Always truncate eval output** — append `.substring(0, 3000)` to expressions returning HTML/text. Unbounded output can overflow the context window.

### State Checking

```bash
agent-browser is visible @e3       # Element visible?
agent-browser is enabled @e3       # Element enabled?
agent-browser is checked @e6       # Checkbox checked?
```

### Dialogs

```bash
agent-browser dialog accept        # Accept alert/confirm
agent-browser dialog dismiss       # Dismiss dialog
```

## Common Verification Patterns

**Check no CSS leaks into document head:**
```bash
agent-browser open --headed http://localhost:4500
agent-browser wait --load networkidle
agent-browser eval "document.querySelectorAll('link[href*=\"style-\"]').length"
# Should return 0
```

**Verify element renders inside shadow DOM:**
```bash
agent-browser eval "document.querySelector('#container')?.shadowRoot ? 'has shadow root' : 'no shadow root'"
```

**Take a before/after screenshot:**
```bash
agent-browser screenshot before.png
# ... make changes ...
agent-browser screenshot after.png
```
