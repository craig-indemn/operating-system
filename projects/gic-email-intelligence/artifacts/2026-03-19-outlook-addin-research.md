---
ask: "Research modern Outlook Add-in development — architecture, APIs, deployment, testing, constraints — to inform GIC Email Intelligence plugin design"
created: 2026-03-19
workstream: gic-email-intelligence
session: 2026-03-19-a
sources:
  - type: web
    description: "Microsoft Learn — Outlook add-ins overview"
    ref: "https://learn.microsoft.com/en-us/office/dev/add-ins/outlook/outlook-add-ins-overview"
  - type: web
    description: "Microsoft Learn — Unified manifest overview"
    ref: "https://learn.microsoft.com/en-us/office/dev/add-ins/develop/unified-manifest-overview"
  - type: web
    description: "Microsoft Learn — Sideload Outlook add-ins for testing"
    ref: "https://learn.microsoft.com/en-us/office/dev/add-ins/outlook/sideload-outlook-add-ins-for-testing"
  - type: web
    description: "Microsoft Learn — Deploy Office Add-ins in M365 admin center"
    ref: "https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-deployment-of-add-ins"
  - type: web
    description: "Microsoft Learn — Office.MessageRead API"
    ref: "https://learn.microsoft.com/en-us/javascript/api/outlook/office.messageread"
  - type: web
    description: "Microsoft Learn — Office.MessageCompose API"
    ref: "https://learn.microsoft.com/en-us/javascript/api/outlook/office.messagecompose"
  - type: web
    description: "Microsoft Learn — Office.Mailbox API"
    ref: "https://learn.microsoft.com/en-us/javascript/api/outlook/office.mailbox"
  - type: web
    description: "Microsoft Learn — Pinnable task pane"
    ref: "https://learn.microsoft.com/en-us/office/dev/add-ins/outlook/pinnable-taskpane"
  - type: web
    description: "Microsoft Learn — Migrate COM to web add-ins"
    ref: "https://learn.microsoft.com/en-us/microsoft-365-apps/outlook/get-started/migrate-com-to-web-addins"
  - type: web
    description: "Microsoft Learn — New Outlook on Windows add-in development"
    ref: "https://learn.microsoft.com/en-us/office/dev/add-ins/outlook/one-outlook"
  - type: web
    description: "Microsoft Learn — Requirements for running Office Add-ins"
    ref: "https://learn.microsoft.com/en-us/office/dev/add-ins/concepts/requirements-for-running-office-add-ins"
  - type: web
    description: "Microsoft Learn — Deploy and publish Office Add-ins"
    ref: "https://learn.microsoft.com/en-us/office/dev/add-ins/publish/publish"
---

# Outlook Add-in Development Research

Research into modern Outlook Add-in development to inform the GIC Email Intelligence plugin — how to surface submission intelligence, gap analysis, and draft replies directly inside Outlook.

---

## 1. Outlook Web Add-ins (Office.js) — The Modern Approach

### What They Are

Outlook Web Add-ins are web applications (HTML + JS + CSS) that run inside Outlook via a sandboxed browser/webview. They are declared via a **manifest file** (XML or JSON) that tells Outlook what UI surfaces to render and where the web content lives. No code is installed on the user's device — Outlook loads the add-in's web pages from a remote HTTPS server.

**Cross-platform by default**: the same add-in code runs on Outlook on the web, new Outlook on Windows, classic Outlook on Windows, Outlook on Mac, and Outlook mobile (iOS/Android). Feature availability varies by platform and API requirement set.

### UI Surfaces (Extension Points)

| Surface | Description | GIC Relevance |
|---------|-------------|---------------|
| **Task Pane** | Vertical panel on the right side of the reading pane or compose window. Can be **pinned** so it stays open as the user navigates between messages. | **Primary surface.** Show submission intelligence, gap analysis, draft suggestions alongside the email being read. |
| **Add-in Commands (Ribbon Buttons)** | Buttons on the Outlook ribbon/toolbar. Can either open a task pane or execute a function (no UI). | Button to open the GIC Intelligence panel. |
| **Contextual Add-ins** | Activate based on regex matches in message content (e.g., detecting a policy number pattern). Entity-based contextual add-ins are retired — regex-based still work. | Could auto-activate when emails match GIC's reference number patterns. |
| **Function Commands** | Run JavaScript without opening any UI. Triggered by ribbon button click. | "Mark as Done" or "Approve Draft" one-click actions. |
| **Event-Based Activation** | Add-in code runs automatically when events occur (new compose, message send, item change). No user click required. Requires admin deployment. | Could auto-populate draft replies when composing a response to a submission. |

### Pinnable Task Pane (Key for GIC)

The pinnable task pane is the most relevant surface for GIC's use case:

- Opens as a vertical panel to the right of the reading pane
- User can **pin** it so it stays open as they navigate between emails
- Listens for `ItemChanged` events to update its content based on the currently selected email
- Supported in: Outlook on the web, new Outlook on Windows, classic Outlook on Windows (Build 7668.2000+), Outlook on Mac
- Pinning is supported in both **Message Read** and **Message Compose** modes, but not across modes
- Requires API requirement set 1.5+
- Implementation: set `"pinnable": true` in the manifest action definition

### Modes of Operation

**Read Mode** — when the user is viewing a received email:
- Full access to: subject, normalizedSubject, from, sender, to, cc, body (HTML or text), attachments, internetMessageId, conversationId, dateTimeCreated, internetHeaders, categories
- Can open reply forms: `displayReplyForm()`, `displayReplyAllForm()`, `displayNewMessageForm()`
- Can get attachments content: `getAttachmentContentAsync()`
- Can get email as EML: `getAsFileAsync()`
- Reading Pane must be enabled for item access

**Compose Mode** — when the user is composing/replying:
- Can get/set: to, cc, bcc, subject, body (HTML or text)
- Can insert content: `body.setAsync()`, `body.prependAsync()`, `setSelectedDataAsync()`
- Can manage attachments: `addFileAttachmentAsync()`, `addFileAttachmentFromBase64Async()`
- Can save as draft: `saveAsync()`
- Can send: `sendAsync()` (requires appropriate permissions)
- Can close compose window: `closeAsync()`
- Can detect compose type: `getComposeTypeAsync()` (new/reply/forward)

### Key API Methods for GIC

**Reading the current email** (to identify the submission):
```javascript
// Get email metadata
const subject = Office.context.mailbox.item.subject;
const from = Office.context.mailbox.item.from; // { displayName, emailAddress }
const to = Office.context.mailbox.item.to; // Array of recipients
const conversationId = Office.context.mailbox.item.conversationId;
const internetMessageId = Office.context.mailbox.item.internetMessageId;

// Get email body
Office.context.mailbox.item.body.getAsync("html", (result) => {
  const htmlBody = result.value;
});

// Get internet headers (for threading)
Office.context.mailbox.item.getAllInternetHeadersAsync((result) => {
  const headers = result.value; // RFC 2183 format
});

// Get attachments
const attachments = Office.context.mailbox.item.attachments;
// Each has: name, size, attachmentType, isInline, id
```

**Opening a pre-filled reply** (for draft suggestions):
```javascript
// Open reply form with pre-filled content
Office.context.mailbox.item.displayReplyAllFormAsync({
  htmlBody: "<p>Thank you for your submission...</p>"
});

// Or open a new message form
Office.context.mailbox.displayNewMessageFormAsync({
  toRecipients: ["agent@example.com"],
  subject: "RE: Quote Request - GL Policy",
  htmlBody: "<p>Pre-filled draft content here</p>"
});
```

**Calling the GIC backend** (from the task pane):
```javascript
// Task pane is a web page — standard fetch() works
const response = await fetch("https://gic.indemn.ai/api/submissions/lookup", {
  method: "POST",
  headers: {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    internetMessageId: messageId,
    conversationId: conversationId,
    subject: subject
  })
});
const submission = await response.json();
```

### API Requirement Sets

The Outlook JS API is versioned via "requirement sets." Each set adds capabilities:

| Set | Key Features | Min Outlook Version |
|-----|-------------|---------------------|
| 1.1 | Basic read/compose, task panes | Outlook 2016 |
| 1.3 | Add-in commands (ribbon buttons) | Outlook 2016 (Build 7668) |
| 1.5 | Pinnable task panes | Outlook 2016 (Build 7668.2000) |
| 1.8 | Shared folder/delegate support | Outlook 2019 |
| 1.10 | Event-based activation (OnNewMessageCompose) | Outlook (M365 subscription) |
| 1.12 | Set signatures, appendOnSend | Outlook (M365 subscription) |
| 1.13 | Shared mailbox support, sensitivity labels, sendAsync | Outlook (M365 subscription) |
| 1.14 | inReplyTo, closeAsync, getComposeType | Latest M365 builds |

New Outlook on Windows supports up to requirement set **1.14**.

---

## 2. COM/VSTO Add-ins — The Legacy Approach

### What They Are

COM (Component Object Model) and VSTO (Visual Studio Tools for Office) add-ins are compiled .NET/C++ code that runs inside the Outlook process on Windows. They have deep access to the Outlook Object Model, can intercept virtually any Outlook event, and manipulate the UI at a low level.

### Current Status: Effectively Deprecated

**COM/VSTO add-ins are NOT supported in the new Outlook on Windows.** They only work in "classic" Outlook on Windows.

**Timeline:**
- **January 2025**: New Outlook became the default for small/medium business users (opt-out available)
- **April 2026**: Enterprise opt-out begins — new Outlook becomes default for enterprise users (can still switch back during this phase)
- **~2029+**: Classic Outlook supported through perpetual licensing until at least 2029

**Why Microsoft is phasing them out:**
- COM add-ins run inside the Outlook process and can cause crashes, instability, and unpredictable behavior
- Web add-ins run in a sandboxed browser environment with controlled resource access
- Microsoft wants one codebase across all Outlook clients (web, Windows, Mac, mobile)

### Deployment Story (Legacy)

COM/VSTO deployment requires:
- MSI installer or ClickOnce deployment
- Windows-only
- Registry entries to register the COM component
- IT admin must push via SCCM/Intune/GPO for enterprise deployment
- No support for web, Mac, or mobile

### Verdict for GIC

**Do not build a COM/VSTO add-in.** The new Outlook on Windows (which GIC will eventually use) does not support them. Web add-ins are the only forward-looking path and work everywhere.

---

## 3. Testing During Development

### Prerequisites

- **M365 account required**: You need a Microsoft 365 work/school account connected to Exchange Online. Free Microsoft 365 developer tenant available from the [Microsoft 365 Developer Program](https://developer.microsoft.com/en-us/microsoft-365/dev-program).
- **My Custom Apps role**: The mailbox must have the "My Custom Apps" user role in Exchange to install/sideload add-ins.

### Sideloading (Primary Dev Method)

Sideloading installs the add-in manifest into your mailbox for testing without going through admin deployment or the marketplace.

**Automatic sideloading** (recommended):
```bash
# Using Yeoman-generated project
npm start
# Opens browser, prompts for M365 login, registers manifest automatically
# Add-in available on desktop and web immediately
```

**Manual sideloading** (works everywhere):
1. Go to https://aka.ms/olksideload in a browser (opens Outlook on the web)
2. The "Add-Ins for Outlook" dialog appears
3. Select "My add-ins" > "Custom Addins" > "Add from File"
4. Upload the manifest XML file
5. The add-in is now available in Outlook on the web AND desktop clients

**Removing sideloaded add-ins:**
- If auto-sideloaded: `npm stop` removes it
- If manual: Go to Add-Ins for Outlook dialog > Custom Addins > ellipsis (...) > Remove

### Testing Across Clients

| Client | How to Test |
|--------|------------|
| **Outlook on the web** | Sideload manifest, open outlook.office.com, add-in appears immediately |
| **New Outlook on Windows** | Sideload in web, it syncs to the desktop client automatically |
| **Classic Outlook on Windows** | Same sideloading; may take up to 24 hours for manual sideloads due to caching |
| **Outlook on Mac** | Sideload via web; automatic sync to Mac client |
| **Mobile (iOS/Android)** | Sideload via web first, then follow mobile testing guidance |

### Debugging

**New Outlook on Windows:**
```bash
olk.exe --devtools
# Opens Outlook + Microsoft Edge DevTools for inspecting the task pane
```

**Outlook on the web:** Use browser DevTools (F12) directly.

**Classic Outlook on Windows:** Attach browser DevTools to the webview process.

### Local Development

- The add-in's web content (HTML/JS/CSS) is typically served from `https://localhost:3000` during development
- **HTTPS is required** even for localhost — the Yeoman generator auto-configures self-signed certificates
- The manifest points to your localhost URL during development, production URL when deployed
- `localhost` works for desktop clients but **not** for Outlook on the web or mobile (they cannot reach your machine's localhost)
- For testing on web/mobile during development: use a tunnel (ngrok, Cloudflare Tunnel) or deploy to a staging server

---

## 4. Deployment to a Customer (GIC)

### Option A: Microsoft 365 Admin Center — Centralized Deployment (Recommended for GIC)

This is how GIC's IT admin would deploy the add-in to their organization.

**Process:**
1. GIC admin signs into [Microsoft 365 admin center](https://admin.microsoft.com)
2. Navigate to Settings > Integrated Apps > Add-ins
3. Select "Deploy Add-in" > "Upload custom app"
4. Upload the manifest file (XML or JSON)
5. Choose deployment scope: Everyone, specific users/groups, or just the admin
6. Deploy

**What users experience:**
- The add-in appears automatically on their Outlook ribbon
- Available in: Outlook desktop (new and classic), Outlook on the web, and mobile
- Users can find it via Home > Get More Add-ins > Admin-managed
- Propagation: up to 24-72 hours for all users to see it

**Requirements:**
- GIC must have Microsoft 365 Business or Enterprise licenses (Basic, Standard, Premium, E1/E3/E5/F3)
- Active Exchange Online mailboxes
- Admin with Global Admin or Exchange Admin role

**Updates:**
- For LOB (line-of-business) add-ins: admin re-uploads the updated manifest
- Changes take effect next time users restart Office
- Permission changes require admin re-consent

### Option B: Exchange Admin Center (Alternative)

Outlook add-ins can also be deployed via Exchange PowerShell for organizations with more complex setups (on-premises Exchange, hybrid).

### Option C: Microsoft Marketplace (AppSource)

For public distribution. Requires Microsoft certification. Not needed for GIC's private deployment.

### Option D: User Self-Install (Sideloading)

Individual users can install add-ins themselves via the Add-Ins for Outlook dialog. No admin needed, but:
- Only affects that user's mailbox
- User needs the "My Custom Apps" role
- Not scalable for an organization

### Platform Support After Deployment

| Platform | Support |
|----------|---------|
| Outlook on the web | Full support |
| New Outlook on Windows | Full support |
| Classic Outlook on Windows | Full support |
| Outlook on Mac | Full support |
| Outlook on iOS | Supported (event-based + task pane with limitations) |
| Outlook on Android | Supported (event-based + task pane with limitations) |

---

## 5. Key Constraints and Requirements

### HTTPS Required

- All add-in resources (HTML, JS, CSS, images) must be served over HTTPS
- The manifest URL must be HTTPS
- Self-signed certificates OK for development, but production requires valid SSL
- This means the GIC backend must be deployed with SSL (e.g., `https://gic.indemn.ai`)

### Manifest Formats

**XML Manifest (add-in only)** — the established format:
- Widely supported on all platforms
- Can be deployed via all methods (admin center, Exchange, sideloading)
- More verbose, but well-documented
- Recommended for broadest compatibility

**JSON Unified Manifest** — the newer format:
- Based on Teams App manifest schema
- Production-ready for Outlook add-ins
- Preview-only for Excel, PowerPoint, Word
- Directly supported on: Outlook on the web, new Outlook on Windows (Build 16320+)
- NOT directly supported on: Mac, mobile, older Windows builds
- For unsupported platforms: must publish to Microsoft Marketplace first (auto-generates XML from JSON)
- LOB/custom add-ins with unified manifest deployed via admin center won't work on unsupported platforms

**Recommendation for GIC**: Use the **XML manifest** for maximum compatibility. GIC likely has users on classic Outlook, Mac, and mobile.

### Same-Origin Policy / CORS

- The task pane is a web page running in a sandboxed webview
- Standard browser same-origin policy applies
- The task pane can make `fetch()` calls to any server that allows CORS
- The GIC backend API must include appropriate CORS headers for the add-in's origin
- For event-based activation (JavaScript-only runtime), CORS requires adding the add-in to a well-known URI

### Supported Frameworks

The add-in's web content is just HTML/JS/CSS. Any framework works:
- **React** — most common choice, officially supported by Yeoman templates
- **Angular, Vue, Svelte** — all work fine
- **Vanilla JS** — perfectly viable for simpler add-ins
- **TypeScript** — fully supported and recommended

The GIC Email Intelligence frontend is already React + TypeScript + Vite + shadcn/ui — the task pane can reuse components from this existing codebase.

### Network Requirement

Add-ins require a network connection to run. They will not work offline (though the new Outlook on Windows has limited offline support — add-ins are disabled when offline).

### Mailbox Restrictions

Add-ins do NOT activate on:
- IRM-protected messages (on mobile)
- Delivery reports / NDR notifications
- Messages opened from .msg/.eml files
- Group mailboxes, public folders
- Messages created via Simple MAPI

Shared mailbox support was added in requirement set 1.13 — GIC's `quote@gicunderwriters.com` is likely a shared mailbox, so this is relevant. The add-in should target requirement set 1.13+.

### Size and Performance

- Task pane body content: 32KB limit in Outlook on the web for `displayNewMessageForm`
- SessionData: 50,000 character limit per add-in
- Attachment content retrieval: works for most types, but "Upload and share" attachments are not returned
- Recipient limits: 20 (mobile) to 500+ (desktop) recipients in to/cc arrays

### Event-Based Activation Constraints

- Requires **admin deployment** (sideloading for testing OK, but production requires admin)
- Runs in a JavaScript-only runtime (no DOM access, no task pane UI)
- Short-lived: runtime terminates after handler completes
- Limited to specific events: OnNewMessageCompose, OnMessageSend, OnAppointmentSend, ItemChanged, etc.

---

## 6. Architecture for GIC Email Intelligence Add-in

### Recommended Approach

```
[Outlook Client]
    |
    |--- Task Pane (React app served from https://gic.indemn.ai/addin/)
    |       |
    |       |-- Reads current email via Office.js (subject, from, body, messageId)
    |       |-- Sends email identifiers to GIC API
    |       |-- Receives: submission match, gap analysis, draft suggestions
    |       |-- Displays: reasoning chain, AI draft, action buttons
    |       |
    |       |-- "Insert Draft" button -> displayReplyAllFormAsync() with pre-filled content
    |       |-- "Mark as Done" button -> POST /api/submissions/{id}/resolve
    |       |
    |--- Ribbon Button (opens/pins the task pane)
    |
[GIC Backend API: https://gic.indemn.ai/api/]
    |-- GET /api/submissions/lookup?messageId=xxx
    |-- GET /api/submissions/{id}
    |-- GET /api/submissions/{id}/draft
    |-- POST /api/submissions/{id}/resolve
```

### Key Design Decisions

1. **Task pane is a thin client** — it reads the current email's identifiers via Office.js, sends them to the GIC API, and renders the response. All intelligence lives server-side.

2. **Pinnable task pane** — stays open as the user navigates between emails. Updates dynamically via `ItemChanged` event handler.

3. **Draft insertion uses native Outlook compose** — `displayReplyAllFormAsync()` opens a real Outlook reply window pre-filled with the AI-drafted content. User reviews, edits, and sends via normal Outlook flow. No need for `Mail.Send` permission.

4. **Shared mailbox support** — GIC's `quote@gicunderwriters.com` is likely a shared mailbox. Target requirement set 1.13+ for shared mailbox API support.

5. **Reuse existing React components** — the task pane can use the same shadcn/ui components and API client code from the existing GIC frontend.

### What You Do NOT Need

- **Mail.Send permission** — not needed if you use `displayReplyAllFormAsync()` (opens Outlook's own compose window)
- **Graph API from the add-in** — the backend already has Graph API access for syncing emails. The add-in only needs to identify the current email and call the GIC REST API.
- **Event-based activation** — nice for future enhancements but not needed for v1. A pinnable task pane covers the core use case.

---

## 7. Summary: What to Build

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Manifest | XML (add-in only format) | Declare ribbon button + pinnable task pane for message read mode |
| Task Pane Web App | React + TypeScript + Vite | Render submission intelligence, gap analysis, draft suggestions |
| Office.js Integration | `@microsoft/office-js` npm package | Read current email metadata, open reply forms with pre-filled drafts |
| Backend API | Existing GIC FastAPI (+ new endpoints) | Lookup submissions by email identifiers, serve drafts and analysis |
| Hosting | AWS (same as GIC backend) | Serve task pane HTML/JS from `https://gic.indemn.ai/addin/` |
| Deployment to GIC | M365 Admin Center centralized deployment | Admin uploads manifest, add-in appears for all GIC users |

### Development Steps

1. Scaffold Outlook add-in project (Yeoman generator or manual)
2. Build task pane as React app that calls GIC API
3. Add Office.js integration to read current email
4. Add `displayReplyAllFormAsync()` for draft insertion
5. Configure manifest with pinnable task pane for message read mode
6. Test via sideloading on Outlook on the web
7. Deploy task pane web app to `https://gic.indemn.ai/addin/`
8. GIC admin deploys manifest via M365 admin center
