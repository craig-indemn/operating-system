# Unisoft Communications: Software Guide

> Understanding Unisoft Communications as software — architecture, products, UI, capabilities.
> **Living document** — updated as we explore UAT environment and learn more.
> Last updated: 2026-03-31

---

## Company Profile

| Field | Detail |
|-------|--------|
| **Legal Name** | Unisoft Communications, Inc. |
| **Founded** | 1996 (sister company Unicorp Data Processing founded 1971) |
| **HQ** | 8900 SW 117th Ave, Suite C-105, Miami, FL 33186 |
| **Size** | 11-50 employees, family-run (Montiel family) |
| **Revenue** | ~$5-12M (estimates vary) |
| **Funding** | Bootstrapped, no external funding |
| **Focus** | Non-standard P&C insurance communication software |
| **Contact** | ProductsInfo@unisoftonline.com, 305-275-5537 |

### Key People

| Name | Role | Relevance to Us |
|------|------|-----------------|
| **Hugo P. Montiel** | President, Registered Agent | Primary business contact; JC cc'd Craig on email to Hugo for UAT/API access |
| **Hugo R. Montiel** | Officer | — |
| **Hector J. Montiel** | VP (Unicorp Data Processing) | — |
| **Derek Valdes-Diaz** | Senior Software Developer & Solutions Architect | Specializes in P&C Claims, Risk Analysis, Business Process Automation |
| **Robert Gonzalez** | Senior Software Engineer | Full-stack: ASP.NET Web API REST, SOAP/XML, cloud migration |
| **Sofia Cueto** | Office Manager | — |
| **Francisco Ansola** | MIS Specialist | — |

---

## Product Suite

Unisoft has **5 distinct products**. GIC primarily uses **UIMS** (the Insurance Management System).

### 1. UIMS — Unisoft Insurance Management System ★

**This is what GIC uses as their AMS.**

- Complete P&C insurance platform for carriers and MGAs
- Full lifecycle: client management, underwriting, claims, accounting, management reporting
- Personal and commercial lines
- New business processing, endorsements (with automatic re-rating), corrections
- Agent commission tracking with unearned commissions
- ACH money transfers between all parties
- Integrated with TruePremium (web-based Point of Sale)
- "Data transfer to carrier back-end systems eliminates double entry"

**GIC's instance:** `gicunderwriters.unisoftonline.com`

### 2. TruePremium — Agent Quoting Portal

- Web-based Point of Sale for agents
- Real-time quoting and binding with multiple carriers
- "Rating relevant questions first" for fast indications
- Insurance documents printed at POS
- Integrated premium financing
- Can be embedded within insurance company web applications

**Lines supported:** Personal Auto, Homeowners, Boats/Yachts, Umbrella, Commercial Auto, Commercial Crime, Commercial Property, GL, Workers Comp

**GIC's producer portal likely runs on this:** `gicunderwriters.com/Products`

### 3. UPFS — Premium Finance System

- Loan origination, payment processing, dunning, cancellation notices
- AS/400-based cloud backend
- Agent commission statements
- Third-party payment integration (ACH, credit card)
- Real-time electronic sales synchronization
- Agent portal with zero-install web access

**Customers:** Honor Capital, Boston Premium Finance, ABCO Premium Finance, Elite Premium Finance, Security Premium Finance, Standard Premium Finance, ETI Financial

### 4. ATARES — Tag Agency System

- Florida auto tag agency registration system
- DHSMV/FRVIS integration
- QuickBooks integration
- Multi-user Windows Terminal Services application

### 5. MVR — Motor Vehicle Records

- Authorized MVR provider
- Real-time driving record retrieval
- Portal: `mvr.unisoftonline.com`

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | ASP.NET MVC, ASP.NET Web API (REST), C# |
| **Database** | SQL Server (T-SQL, Entity Framework ORM) |
| **Frontend** | JavaScript, HTML, CSS, jQuery; React.js + Redux for newer apps |
| **Legacy** | AS/400 (IBM iSeries) — premium finance backend |
| **Web Server** | Microsoft IIS |
| **Monitoring** | New Relic (embedded in all customer portals) |
| **APM** | Stackify Retrace (adopted 2022) |
| **Infrastructure** | AT&T Internet hosting, Microsoft 365 |
| **Services** | SOAP/XML web services + REST APIs (internal) |
| **CSS Framework** | Bootstrap |
| **Accessibility** | Targets WCAG 2.1 Level AA |

**Key takeaway:** Modern enough tech stack (ASP.NET Web API, Entity Framework, C#) to support REST API exposure. The lack of public API is a business decision, not a technical limitation.

---

## Deployment Model

**Multi-tenant SaaS** with branded subdomains:

```
{customer}.unisoftonline.com
```

Each portal has:
- Agent Sign-In
- Customer Sign-In
- White-labeled with customer branding
- New Relic monitoring embedded

**Known customer portals:**

| Customer | URL | Type |
|----------|-----|------|
| GIC Underwriters | gicunderwriters.unisoftonline.com | MGA |
| SafePoint Insurance | safepoint.unisoftonline.com | Carrier |
| Federated National Insurance | fednat.unisoftonline.com | Carrier |
| US Insurance Brokers | usinsurancebrokers.unisoftonline.com | MGA |
| Honor Capital | honorcapitalcorp.unisoftonline.com | Premium Finance |
| Boston Premium Finance | bostonpremium.unisoftonline.com | Premium Finance |
| ABCO Premium Finance | abcopfc.unisoftonline.com | Premium Finance |
| Security Premium Finance | securitypremium.unisoftonline.com | Premium Finance |
| Elite Premium Finance | elitepremium.unisoftonline.com | Premium Finance |
| JAV Insurance & Tag | javinsurance.unisoftonline.com | Tag Agency |

**Alternative deployment:** Licensed in-house installation (particularly for AS/400-based systems).

---

## UI Structure (Detailed — From Video Frame Analysis)

> Source: Frame-by-frame analysis of JC's walkthrough video (March 27, 2026), 357 frames at 3-second intervals.
> Title bar reads: **"UNISOFT INSURANCE MANAGEMENT (GIC)"**

### Application Window

The application runs as a **browser-based web application** on Windows 11. It has:
- A **main menu bar** across the top
- A **toolbar** with icon buttons below the menu
- A **left sidebar** with blue background for module navigation
- A **main content area** that changes based on the selected module/screen

### Global Navigation

**Main Menu Bar** (top, persistent):
```
File | Edit | View | Policies | Quotes | Agents | Cash | Payables | Claims | Reports | Tasks | Contacts | Administration | Help
```

**Toolbar** (below menu): Icons for print, copy, paste, search, binoculars (find), back/forward arrows, list view

**Left Sidebar** (blue background, persistent):
```
Home
Policies
Claims
Quotes          ← highlighted yellow when active
Agents
Cash Posting
Payables
Reports
Tasks
Contacts
Administration
```

### Dashboard (Home Screen)

The dashboard shows:

**Pending Items** with filter tabs:
- Due Today (count) | Due Tomorrow (count) | Upcoming (count) | Pending (x/x) | Overdue (x/x)
- Filter by: Priority, Assignment
- Items include tasks like "Follow up on additional info requested", "Inspection Pending Review"
- Each item shows: description, quote/policy reference, agent name, due date, overdue days

**Announcements Panel** (right side):
- System notifications: "New Archived RAS", commission updates, submission alerts, policy tasks

**Sales Chart** (bottom):
- Bar chart: "Sales by Month" (Jan-Dec)
- Toggle: "Mine | All Policies"
- Y-axis: dollar values up to ~$6M

### Quote Entry Module

**Navigation path:** Left Sidebar → Quotes → Entry

**Action Button Bar** (blue, across top):
```
NEW QUOTE | NEW SUBMISSION | NEW ACTIVITY | NEW ATTACHMENT | NEW TASK | NEW AGENT CONNECT | REPORTS | ALERTS
```

**Quote Search/Filter** panel with fields:
- Search By: Quote # (dropdown + text field)
- Underwriter, Carrier, LOB, Sub LOB, Agent, Last Action, Task (all "Include all" dropdowns)
- Status, Business Type, Created, Last Activity Date, Task Due, Task Status (right column)
- Checkbox: "Unbudged quotes"
- Search Results area below

#### Step 1: New Quote — Initial Selection

Clicking **NEW QUOTE** opens a minimal form:

| Field | Type | Notes |
|-------|------|-------|
| **Business Type** | Dropdown | Defaults to "New" |
| **LOB** | Dropdown | "SELECT LOB" placeholder. 21 options (see full list below) |
| **Sub LOB** | Dropdown | Dependent on LOB. Loads dynamically ("Loading Sub LOBs...") |
| **Agent** | Dropdown | "SELECT AGENT or PROSPECT" — massive scrollable list with agency name + #number |

#### Complete LOB List (21 Lines of Business)

From video frame analysis of the LOB dropdown:

1. Boats & Yachts
2. Collector Vehicle
3. Commercial Auto
4. Commercial Property
5. Commercial Umbrella
6. Exotic Casualty
7. Flood
8. Garage
9. General Liability
10. Homeowners
11. Inland Marine (Commercial)
12. Inland Marine (Personal)
13. Management Liability
14. Motorcycle
15. Ocean Marine
16. Personal Liability
17. Personal Umbrella
18. Private Auto
19. Professional Liability
20. Transportation
21. Workers Compensation

#### General Liability Sub-LOBs (4 options)

1. Artisans/Contractors
2. Liquor Liability
3. Non-Artisans
4. Special Events

#### Agent Dropdown

Massive scrollable list of hundreds of agencies. Each entry format:
```
[Agency Name] | # [4-5 digit number]
```

Examples from video:
- FIR Insurance Services, Inc. | # 7312
- 24/7 Insurance LLC | # 8631
- 5 Star Insurance Agency LLC | # 7841
- GIC - Office Quoted | # 1111
- GIC Underwriters (Office Quoted) | # 1110
- Great Florida Insurance - Naples
- Univista Insurance (multiple entries with different suffixes)

The list is alphabetically sorted and includes hundreds of retail agencies.

#### Step 2: Applicant Tab (Full Quote Form)

After selecting LOB, Sub LOB, and Agent, the full **Applicant** form opens with tabs:

```
Applicant (active) | Activities | Submissions | Attachments | Tasks
```

**Header bar shows:**
- Agent: [selected] | Business Type: NEW | Quote Id: [auto-generated] | Status: OPEN

**Left Column — Applicant Details:**

| Field | Type | Example Value |
|-------|------|---------------|
| Agent | Dropdown | GIC - Office Quoted, 111 |
| LOB | Dropdown | General Liability |
| Sub LOB | Dropdown | Artisans/Contractors |
| Name | Text | "JC Test quote" |
| DBA | Text | |
| Address 1 | Text | "4875 SW 66th ave" |
| Address 2 | Text | |
| City | Text | "Miami" |
| State | Dropdown | Florida |
| Zip | Text | "33155" |
| Memo | Text area | |
| Term | Dropdown | 12 |
| Policy State | Dropdown | Florida |
| Effective | Date picker | 12/17/2026 |
| Expiration | Date picker | 12/17/2027 (auto-calculated from term) |

**Right Column — Contact & Business Info:**

| Field | Type | Example Value |
|-------|------|---------------|
| Email | Text + address book icon | |
| Phone #1, #2 | Phone format (area-number) | |
| Cell #, Fax # | Phone format | |
| Website | Text | |
| Form of Business | Dropdown | Corporation |
| FEIN/SRN | Text | |
| Business Descr | Text area | |
| Rates | Text | "2000 x 2000" (SIC code area) |
| Underwriter | Dropdown + refresh | Juan Carlos Diaz-Padron |
| Agent Contact | Dropdown + person icons | (see contact list below) |

**Bottom Left — PREVIOUS POLICY INFORMATION** (blue header):

| Field | Type |
|-------|------|
| Carrier | Dropdown (NONE default) |
| Policy Number | Text |
| Lapse/Exp Days | Text |
| Premium | Text |
| Canc. Date | Date picker |

**Bottom Right — POLICY INFORMATION** (blue header):

| Field | Type |
|-------|------|
| Carrier | Text |
| Policy Number | Text |
| Bound | Text |
| Confirmation # | Text |

**"Add New Agent Contact" dialog:**

| Field | Type |
|-------|------|
| Name | Text |
| Email | Text |
| Position | Dropdown |
| Phone #1, #2 | Phone format |
| Cell #, Fax # | Phone format |
| Buttons | SAVE, CLOSE |

#### GIC Staff / Agent Contacts (from dropdown)

From video frames of the Agent Contact dropdown:
- Juan C. Diaz-Padron
- JOSE RODRIGUEZ
- Nancy Negron
- Maylin Laguna
- Ileana Hernandez
- Hilena Abreola
- Dienly Sale/Solis
- Donna Capuccio/Guzman
- Adriana Falcon/Fulco
- Orlando Sanchez
- Amanda/Armanda Marquez
- Jennifer Aguilera
- Edy Lopez/Fugon
- Rosa Diaz
- STEPHANIE REGA
- Wivelka Jerez/Wesllan Javier
- (Test entries: BEYONCE, Michael Jackson, CSE Test)

#### Step 3: Submissions Tab

After saving the quote (confirmation: "Quote 144093 saved"), navigate to the **Submissions** tab.

**Header summary repeats:** Applicant name, address, LOB, Agent, phone, email, Quote ID, Status

**Content area:** Lists existing submissions for this quote. Initially empty.

**Buttons at bottom:** BROKER | CARRIER

**Creating a new submission:**

| Field | Type | Notes |
|-------|------|-------|
| Broker | Dropdown + refresh | Options include: NONE, Atlas General Insurance Services, AMWINS / David Intermediaries, BPS, Cornerstone Underwriting Parlour, FOXQUILT, **GIC Underwriters, Inc.**, International Grain, PARAGON SPECIALITY INS CO, RISK PLACEMENT SERVICES INC. |
| Carrier | Dropdown + refresh | Options include: NONE, Mutual Bones Part Insurance Co., **United States Liability Insurance Company (USLI)**, Mid Continent Casualty Company, Mid Continental/Excess & Surplus Insurance Company, Security National Insurance Company, PHOCOS INSURANCE COMPANY, Hallmark Specialty Insurance Company, LIG Specialty Insurance Company |
| Effective | Date (auto from quote) | |
| Expiration | Date (auto from quote) | |
| Contact Email | Text (auto from broker) | |
| Submission # | Auto-generated | e.g., 10780 |
| Description | Text | e.g., "Handyman" |

#### Submission Detail View

After saving a submission, the detail view shows:

**Inner tabs:** Submission | Activities | Documents | Financing

**QUOTE RECEIVED section** (blue header):
- Quote Amount (text input — entered when carrier responds)

**BINDER CONFIRMATION RECEIVED section** (blue header):
- Bind Date
- Confirmation #
- Policy #

#### Step 4: Activities

The **Add Activity** dialog has:

**Header:** Action description + submission context (Applicant, LOB, Broker, Carrier, Quote ID, Agent, Business Type, Submission #)

**Tabs within dialog:** Activity | Documents | Attachments | Email

**Activity Action Dropdown — COMPLETE LIST** (30+ activities from video):

| Category | Activity |
|----------|----------|
| **Internal** | (INTERNAL) Return Submission as Void Request |
| **Endorsements** | AKIS/TMAS Premium Endorsement to Quote |
| **Billing** | Hot Issue - 02/23/24 bill |
| **Renewal** | OPT Out - Renewal |
| **Pricing** | Price to Win (ACLI) |
| **Carrier Comms** | Receive RI Reclamation request from carrier |
| **Quoting** | Replacement Quotes |
| **Info Gathering** | Request additional form/information |
| **Loss Runs** | Request Loss Runs from Carrier |
| **Declination** | Send Declination to Agent |
| **Finance** | Send Finance Agreement to FIRST to agent |
| **Inspection** | Send Inspn Indication to agent |
| **Renewal** | Send New Renewal to Agent |
| **Quote Delivery** | Send offer Policy on to agent |
| **Quote Delivery** | Send offer to agent |
| **Certificates** | Send POC offer to Agent |
| **Finance** | Send TC Agreement to BT Finance |
| **Notices** | Send ROR/NoI to Agent |
| **Admin** | Submission Rollover |
| **Core** | **Submit application to carrier** |
| **Endorsements** | Submit endorsement to carrier |
| **Billing** | Submit Bill Carrier for Processing |
| **Approval** | Submit to OW Approval |
| **Binding** | Submit Binding Info To Carrier (for binder) |
| **Risk Mgmt** | Submit from to Risk Management 1/1 CARRIER |
| **Specialty** | Submit to Specialty / sub-producer |
| **Billing** | (ICS) Direct Bill Manual Payment from Reinsurer |

**"Submit application to carrier" sub-tabs:**

- **Activity tab**: Notes (12,000 char limit), Instructions section
- **Documents tab**: Document attachment area
- **Attachments tab**: Drag-and-drop file upload with columns: DESCRIPTION, AUTO FILLED & ATTACHED, AUTO ATTACHED, FILE TYPE. Buttons: Add New, Import
- **Email tab**: Built-in email composition with From, To, bcc, Subject (auto-populated: "Request for Quote: [Insured] - [Quote#]"), Message Body, Attachments. Checkbox: "Do not send notification email to the broker by email"

**ADD ATTACHMENTS dialog** (large overlay):
- Drag-and-drop zone: "Drop Files Here"
- Left sidebar tabs: Edit, General, Documents, Returns
- Columns: EDIT, DESCRIPTION, LOB, CATEGORY, SUBCATEGORY, STATUS, PAGES
- Bottom buttons: SUBMIT TO WDR, SEND TO ALL, MINUTES, MISSING, LINK, CLOSE

#### Step 5: Financing Tab

After entering a Quote Amount, the **Financing** tab shows automated calculations:

**FEES section:**

| Field | Type |
|-------|------|
| Billing Method | Dropdown (Net) |
| ADMIT RISK | Checkbox |
| Policy Fee | Amount |
| Carrier Fee | Amount |
| Inspection Fee | Amount |

**COMMISSION RATES section:**

| Role | Rate |
|------|------|
| Agent | 16.00% |
| MGA | 24.00% |

**SUMMARY section** (auto-calculated):

| Line Item | Example |
|-----------|---------|
| Carrier Amount | $360.00 |
| Policy Fee | $0.00 |
| Carrier Fee | $0.00 |
| Inspection Fee | $0.00 |
| **Subtotal** | **$360.00** |
| Surplus Lines Tax 1.60% | $5.76 |
| Surplus Lines Stamping Fee 0.16% | $0.58 |
| **Total** | **$366.34** |
| Agent Commission: 16.00% | ($57.60) |
| **Balance Due from Agent** | $308.74 |
| MGA Commission: 24.00% | ($86.40) |
| **Premium Owed To Carrier** | $222.34 |

### Outlook Integration (Observed)

JC demonstrated switching between Unisoft and Outlook during the walkthrough:
- **Calendar view** showing meetings (Day view, March 27, 2026)
- **Inbox** showing 174 items, 63 unread, with organized folder/Quick Steps categories
- **Email compose** with GIC 30th anniversary branding, full signature (JC's credentials: CPCU, RPLU, ARe, AU)
- **Contact autocomplete** showing both GIC internal contacts and external contacts

The workflow involves manually switching between Unisoft and Outlook — there is no embedded Outlook integration within Unisoft itself.

---

## UAT Environment

> JC arranged access through Hugo at Unisoft. **Windows-only.**

| Field | Detail |
|-------|--------|
| **Access** | UAT environment arranged by Hugo (Unisoft President) |
| **Platform** | Windows-only application (likely Windows Terminal Services or browser-based with IE/Edge requirement) |
| **Status** | Access pending / recently provided |
| **URL** | TBD — likely a UAT subdomain of unisoftonline.com |
| **Credentials** | TBD |

### UAT Exploration Plan

When we access the UAT environment:

1. **Screenshot every screen** — main menu, all tabs, all forms
2. **Map all navigation paths** — build complete sitemap
3. **Document all dropdowns** — LOB options, sublines, carrier lists, agency lists
4. **Test the quote entry flow** — create a test submission end-to-end
5. **Find all activities** — what actions can be taken on a submission
6. **Check search/lookup** — how to find existing submissions
7. **Test assignment/routing** — how submissions get routed to underwriters
8. **Look for API/export features** — any built-in data export or integration options
9. **Note field validations** — required fields, formats, constraints
10. **Check permissions/roles** — what different user types can do

---

## Competitive Context

Unisoft is **not** a general-purpose AMS. It occupies a specific niche:

| Dimension | Unisoft | Applied Epic / AMS360 | HawkSoft |
|-----------|---------|----------------------|----------|
| **Market** | Non-standard P&C, Florida-centric | National, all lines | Small-medium agencies |
| **Scale** | 11-50 employees | 2,000+ | 200+ |
| **API** | No public docs, internal REST/SOAP | Partner API program | Partner API program |
| **Vertical** | Carrier + MGA + PremFi + Tag | Agency-focused | Agency-focused |
| **Tech** | ASP.NET, SQL Server, AS/400 | Cloud-native | Cloud/hybrid |
| **Deployment** | Multi-tenant SaaS or on-prem | Cloud | Cloud/on-prem |

**Key differentiator:** Unisoft connects the **entire value chain** (carrier ↔ MGA ↔ agent ↔ premium finance ↔ tag agency) rather than just serving one participant. This is why GIC/Granada uses it — they need carrier-level functionality AND MGA-level brokerage tools.

---

## What We Still Need to Learn

### From UAT Exploration (partially answered by video)
- [x] All LOB options (21 LOBs confirmed from video)
- [x] GL sub-LOBs (4: Artisans/Contractors, Liquor Liability, Non-Artisans, Special Events)
- [x] All activity types (30+ confirmed from video)
- [ ] Sub-LOBs for ALL other LOBs (only GL confirmed)
- [ ] Complete navigation of Policies, Claims, Agents, Cash, Payables, Reports, Administration modules
- [ ] Search/lookup functionality (find existing quotes by name, ref number)
- [ ] Report capabilities and available report types
- [ ] User roles and permissions
- [ ] Data export options
- [ ] Integration/API settings (if visible in admin)
- [ ] How renewals are handled vs new business (Business Type dropdown has "New" — does it also have "Renewal"?)
- [ ] Claims workflow (if applicable to GIC)
- [ ] How the Announcement system works (right panel on dashboard)
- [ ] Task assignment/routing configuration

### From Hugo/Unisoft
- [ ] Technical architecture documentation
- [ ] Database schema (or at least entity model)
- [ ] API documentation (even internal/informal)
- [ ] Supported integration patterns
- [ ] Roadmap / planned features
- [ ] How TruePremium integrates with UIMS
- [ ] Custom development capabilities

### From JC
- [ ] Complete walkthrough of a USLI quote processing workflow
- [ ] Complete walkthrough of a new agent submission workflow
- [ ] How personal liability submissions are (or aren't) tracked
- [ ] What reports they regularly run
- [ ] What features they wish they had
- [ ] Pain points with Unisoft specifically

---

## Internal Architecture (Confirmed from Fiddler 2026-04-01)

The ClickOnce app is NOT a thick client talking directly to a database. It communicates with a multi-layer API:

```
ClickOnce Desktop App (WinForms .NET 4.8)
    │
    ├── REST API Gateway (Azure, JSON, JWT auth)
    │   └── ins-gic-api-gateway-uat-app.azurewebsites.net
    │
    ├── WCF SOAP Service (XML, WS-Security auth)
    │   └── services.uat.gicunderwriters.co/management/imsservice.svc
    │
    ├── File Service (SOAP, WS-Security auth)
    │   └── services.uat.gicunderwriters.co/attachments/insfileservice.svc
    │
    └── SignalR Hub (WebSocket, real-time)
        └── ins-gic-nothub-prod-app.azurewebsites.net
```

This is a modern service-oriented architecture. The REST gateway handles tasks, users, brokers, and documents. The SOAP service handles ALL insurance operations — quotes, submissions, policies, claims, agents, activities. 70 unique SOAP operations + 32 REST endpoints confirmed.

Full API documentation in `unisoft-api-reference.md`.

---

## Changelog

| Date | Update | Source |
|------|--------|--------|
| 2026-03-31 | Initial creation from web research + JC walkthrough | Web search (20+ queries), unisoftonline.com, meeting transcript |
| 2026-04-01 | Major update: complete UI documentation from video frame analysis | 357 video frames extracted, 360 hi-res cropped UI frames analyzed by 3 parallel agents |
| 2026-04-01 | Added internal architecture from Fiddler traffic interception | Confirmed SOA architecture, NOT thick client |
