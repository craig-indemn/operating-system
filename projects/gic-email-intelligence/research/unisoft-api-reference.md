# Unisoft API Reference & Integration Options

> Complete API surface for the Unisoft Insurance Management System (UIMS) used by GIC Underwriters.
> **Living document** — updated as API access is granted and capabilities discovered.
> Last updated: 2026-04-01

---

## Architecture (from Fiddler Traffic Analysis)

The Unisoft Insurance Management System (GIC) uses a multi-layer API architecture:

### 1. REST API Gateway
- **Host:** `ins-gic-api-gateway-uat-app.azurewebsites.net`
- Modern JSON REST API
- JWT Bearer token auth
- Handles: users, tasks, brokers, documents, search preferences

### 2. WCF SOAP Service
- **Host:** `services.uat.gicunderwriters.co/management/imsservice.svc`
- WS-Security with UsernameToken auth (username: `UniClient`, password: `J5j!}7=r/z`)
- Then GetToken with ClientId: `GIC_UAT`, CompanyInitials: `GIC_UAT`
- Handles: ALL insurance operations — quotes, submissions, agents, carriers, LOBs, policies, activities, cash
- DTO namespace: `Unisoft.Insurance.Services.DTO.*`

### 3. File/Attachment Service
- **Host:** `services.uat.gicunderwriters.co/attachments/insfileservice.svc`
- Same WS-Security auth
- Handles: attachment upload/download, categories, supported types

### 4. SignalR Notification Hub
- **Host:** `ins-gic-nothub-prod-app.azurewebsites.net`
- Hub name: `UnisoftMessageHub`
- Protocol: SignalR 2.1 with WebSockets transport
- Provides real-time notifications

---

## Authentication

### REST API (JWT)

- **Endpoint:** `POST /api/authentication/login`
- **Request:**
```json
{
  "UserName": "ccerto",
  "Password": "GIC2026$$!",
  "UseTwoFactorAuth": false
}
```
- **Response:**
```json
{
  "isAuthSuccessful": true,
  "accessToken": "eyJ...",
  "refreshToken": "...",
  "isTwoFactorAuthRequired": false
}
```
- **JWT claims:** name=ccerto, role=Underwriter, iss=Unisoft.Insurance.UserManagement.WebApi, aud=https://ins-gic-users-api-uat-app.azurewebsites.net
- **Usage:** `Authorization: Bearer <accessToken>`

### SOAP Service (WS-Security + Token)

**Step 1: WS-Security UsernameToken**
- Username: `UniClient`
- Password: `J5j!}7=r/z`
- Action: RequestSecurityToken (SCT)
- This establishes a SecurityContextToken

**Step 2: GetToken operation**
- ClientId: `GIC_UAT`
- CompanyInitials: `GIC_UAT`
- Returns: AccessToken (GUID like `f08564a2-1ec3-4561-99d6-233faf9ced22`)
- This token is included in all subsequent SOAP requests

---

## REST API Endpoints (32 unique endpoints captured)

### Authentication

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/authentication/login` | Login, returns JWT + refresh token |

### Users

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/api/users/{userName}` | User profile | `{firstName, lastName, userName, email, roles, id, isActive, ...}` |
| GET | `/api/users?forLookup=true` | All users (lookup) | Array of users with roles |
| GET | `/api/roles/{roleName}/users` | Users by role | Array of users |

Users discovered in UAT: arivera (Underwriter), aritest (Underwriter), ariadna (Developer at Unisoft), bbriz (Accounting), carlosdp (Marketing Rep), carlos (Developer at Unisoft), carmendp (Accounting/Executive), carmeng (Marketing Rep/Customer Service), ccerto (Underwriter), and many more.

### Tasks

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/api/tasks/dashboard?userName={user}&groupId=0&sectionId=0&actionId=0&statusId=0&isPrivate=False&userGroupFilteringOption=ALL&dueDateFilteringOption=Pending` | Dashboard task summary | `{dueTodayTasksCount, dueTomorrowTasksCount, upcomingTasksCount, pendingTasksCount, overdueTasksCount, completedTasksCount, tasksForLookup:[]}` |
| POST | `/api/tasks` | Create new task | Full task object with taskId |
| GET | `/api/tasks?responseType=ForLookup&paging=False&quoteId={id}` | Tasks for quote | Array of task objects |
| GET | `/api/tasks?responseType=ForLookup&paging=True&pageNumber=1&pageSize=20&orderBy=...&many filters` | Search tasks | Paginated task results |
| GET | `/api/taskStatus` | Task statuses | `[{statusId:1,description:"In Progress"},{2:"Completed"},{3:"Not Started"},{4:"Deferred"},{5:"Waiting"}]` |
| GET | `/api/taskPriorities` | Task priorities | `[{priorityId:1,description:"NONE"},{2:"Low"},{3:"Medium"},{4:"High"}]` |
| GET | `/api/taskActions?responseType=ForLookup&paging=False` | All task actions | Array of `{actionId, description, sectionId, assignedWorkDays, isActive}` |
| GET | `/api/taskActions?sectionId={id}` | Actions by section | Filtered array |
| GET | `/api/taskGroups` | All task groups | Array of groups |
| GET | `/api/taskGroups?userName={user}` | User's task groups | Array |

**Task CREATE payload (POST /api/tasks):**
```json
{
  "taskId": 0,
  "actionId": 27,
  "subject": null,
  "startDate": null,
  "dueDate": null,
  "enteredDate": "2026-04-01T14:41:43.206Z",
  "enteredByUser": "ccerto",
  "sectionId": 5,
  "priorityId": 1,
  "groupId": 0,
  "departmentId": 0,
  "statusId": 1,
  "assignedToUser": "ccerto",
  "isPrivate": false,
  "taskAssociation": {
    "taskId": 0,
    "policyNo": null,
    "quoteId": 17129,
    "agentNo": 777,
    "carrierNo": 0,
    "submissionNo": 0,
    "activityId": 0
  }
}
```

**Task sections:** sectionId 1=General, 2=New Business, 3=Policy, 4=Claims(?), 5=Quotes, 6=E&O

### Brokers

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/api/1.0/brokers?forLookup=true` | All brokers | Array of `{brokerId, name}` — 16 brokers |
| GET | `/api/1.0/brokers/{id}` | Broker details | `{brokerId, name, address1, city, stateCode, zipCode, phone, email, ...}` |
| GET | `/api/1.0/brokers/bylob?carrierNumber={n}&lob={lob}&subLob={sub}` | Brokers for LOB/carrier | Filtered broker array |
| GET | `/api/1.0/brokers?carrierNumber={n}` | Brokers for carrier | Filtered array |

**Confirmed brokers:** GIC Underwriters Inc. (id:1), Atlas General (13), Cornerstone Underwriting (14), International Excess (4), BTIS (23), CFC Underwriting (22), Concept Special Risks (16), GRIDIRON (21), National Insurance Underwriters (6), Professional Program Insurance Brokerage (17), Specialty Insurance (18), (SkiSafe) Sullivan & Strauss (19), Tokio Marine (20), Yachtinsure (15), Flood (24), International Excess Program Managers (3)

### Documents

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/documentTemplates?sectionId={id}` | Document templates by section |
| GET | `/api/documentTemplates?responseType=Full&paging=True&pageNumber=1&pageSize=20&orderBy=Name&sectionId=0&name=` | Search templates |
| GET | `/api/documentActions` | Document actions |
| GET | `/api/documentActions?actionId={id}` | Actions for document |
| GET | `/api/documentGroups` | Document groups |
| GET | `/api/documentStages` | Document stages |

### Search Preferences

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/userSearchPreferences?userName={user}&systemSearchId={id}` | Saved search filters |

**systemSearchId values:** 1=Quotes, 2=Policies(?), 3=Agents(?), 7=Tasks, 9=unknown

---

## SOAP Operations (70 unique operations captured)

### Write Operations (Critical for Automation)

| Operation | Purpose | DTO Namespace | Key Fields |
|-----------|---------|---------------|------------|
| SetQuote | Create/update quote | `Unisoft.Insurance.Services.DTO.Quotes` | Action (Insert/Update), Address, AgentNumber, LOB, SubLOB, Name, EffectiveDate, ExpirationDate, FormOfBusiness, Email, AssignedTo, BrokerId, CarrierNumber, and many more (see full model below) |
| SetSubmission | Create/update submission | `Unisoft.Insurance.Services.DTO.Quotes.Submissions` | Links to quoteId, brokerId, carrierNumber, description, effective/expiration dates |
| SetActivity | Log activity on submission | `Unisoft.Insurance.Services.DTO.Activities` | Links to quoteId, submissionId, actionId, notes, email fields |
| SetCashDetail | Create cash entry | `Unisoft.Insurance.Services.DTO.Cash` | Payment details |
| EndorsePolicy | Create endorsement | `Unisoft.Insurance.Services.DTO.PolicyInquiry` | Endorsement details |

### SetQuote Data Model (from captured payload)

Key fields in the Quote DTO:

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| Action | string | `"Insert"` or `"Update"` | Insert for new, Update for edits |
| Address | string | `"123 Main St"` | |
| Address2 | string | | |
| City | string | `"Alexandria"` | |
| State | string | `"VA"` | 2-char state code |
| Zip | string | `"22301"` | |
| CountryCode | string | | |
| AgentNumber | int | `777` | |
| AgentName | string | | |
| AgentContactID | int | | |
| LOB | string | `"CG"` | 2-char LOB code (see LOB Codes section) |
| SubLOB | string | `"AC"` | 2-char sub-LOB code |
| Name | string | | Insured name |
| Name2 | string | | |
| DBA | string | | Doing business as |
| EffectiveDate | datetime | ISO format | |
| ExpirationDate | datetime | ISO format | |
| FormOfBusiness | char | `"C"` | C=Corporation, I=Individual, P=Partnership, etc. |
| Email | string | | |
| Phone1 | string | | |
| Phone2 | string | | |
| CellNumber | string | | |
| FaxNumber | string | | |
| FEIN | string | | Federal EIN |
| BusinessDescription | string | | |
| AssignedTo | string | `"ccerto"` | Username |
| AssignedToFullName | string | | |
| BrokerId | int | | |
| CarrierNumber | int | | |
| CarrierName | string | | |
| Memo | string | | |
| PolicyState | string | `"FL"` | |
| Term | int | | Months |
| PreviousCarrierNumber | int | | |
| PreviousPolicyNumber | string | | |
| PreviousPremium | decimal | | |
| ConfirmationNumber | string | | |
| Bound | datetime | | Bound date |
| QuoteId | int | | Returned on create, auto-assigned |
| Status | string | `"OPEN"` | |
| IsProspect | bool | | |
| IsNewSystem | bool | `true` | True for new quotes |
| CreatedBy | string | | Username |
| CreatedDate | datetime | ISO format | |

**SetQuote Response:** Returns `ReplyStatus: "Success"`, `RowsAffected: 1`, and the full Quote object with server-assigned QuoteId and populated fields.

### File Operations

| Operation | Purpose |
|-----------|---------|
| FILE:AddQuoteAttachment | Upload attachment to quote |
| FILE:GetQuoteAttachments | Get attachments for quote |
| FILE:GetPolicyAttachments | Get attachments for policy |
| FILE:GetActionAttachments | Get attachments for activity |
| FILE:GetAttachmentCategories | Attachment category list |
| FILE:GetSupportedAttachmentTypes | Supported file types |

### Read Operations — Reference Data

| Operation | Purpose | Response Data |
|-----------|---------|---------------|
| GetInsuranceLOBs | All lines of business | Array of `{LOB (code), Description}` — e.g., `{LOB:"CG", Description:"General Liability"}` |
| GetInsuranceLOB | Single LOB details | `{LOB, Description, SubLines}` |
| GetInsuranceSubLOBs | Sub-LOBs for a LOB | Array of `{LOB, SubLOB (code), Description}` — e.g., CG has AC=Artisans/Contractors, LL=Liquor Liability, HM=Non-Artisans, SE=Special Events |
| GetInsuranceSubLOB | Single sub-LOB | `{LOB, SubLOB, Description}` |
| GetInsuranceCarriers | All carriers | Array of carrier objects |
| GetCarrier | Single carrier | Full carrier with address, NAIC, email, etc. — e.g., CarrierNumber:2, Name:"United States Liability Ins Co", NAICNumber:25895, City:Wayne, State:PA, ContactEmail:joanneh@usli.com |
| GetCarriersForLookup | Carriers dropdown | Simplified carrier list |
| GetAgentsAndProspectsForLookup | Agent dropdown | Massive list with AgentNumber and Name |
| GetAgent | Full agent details | Rich object: Address, City, State, Zip, County, Email, Phone, Fax, FederalID, AgentOfRecord, AppointmentDate, ErrorOmmissionsDate/Limit, BillType, ContractType (Voluntary), AgencyAppointedStates, and nested: AgentContacts, AgentCarriers, AgentCommissions, AgentLOBs, AgentLicenses, AgentDiaries, AgentStatementRecords |
| GetAccountManagers | Account manager list | Array of managers |
| GetMarketingReps | Marketing reps | Array of reps |

### Read Operations — Quotes & Submissions

| Operation | Purpose |
|-----------|---------|
| GetQuote | Get quote by ID |
| GetSubmissions | Get submissions for quote |
| GetQuoteActions | All quote activity definitions (161K response!) — includes ActionId, Description, EmailFrom, EmailRecipient, EmailTemplate, TaskActionId, etc. |
| GetQuoteActivityCarriers | Carriers available for quote activities — includes ContactEmail per carrier: USLI=joanneh@usli.com, Mid-Continent=GAMail@mcg-ins.com, etc. |
| GetActivitiesByQuoteId | Activity history for quote |
| GetActivitiesBySubmissionId | Activity history for submission |
| GetRecurringQuoteActivitiesByQuote | Recurring activities |
| GetUnderwriterAssignedToQuote | Assigned underwriter |

### Read Operations — Policies

| Operation | Purpose |
|-----------|---------|
| GetPolicyEntry | Full policy data |
| GetPolicyEntryClasses | ISO classes for policy |
| GetPolicyEntryFees | Fee structure |
| GetPolicyEntryLimitsByLocation | Coverage limits |
| GetPolicyEntryLocations | Insured locations |
| GetPolicyEntryAdditionalInsuredsNew | Additional insureds |
| GetPolicyEntryAdditionalInterests | Additional interests |
| GetPolicyEntryCertificates | Certificates |
| GetPolicyEntryPayment | Payment details |
| GetActivitiesByPolicyNo | Policy activity history |
| EndorsePolicy | Create endorsement |
| GetEndorsementsEntryBySearchCriteria | Search endorsements |

### Read Operations — Agents & Contacts

| Operation | Purpose |
|-----------|---------|
| GetAgent | Full agent record |
| GetContacts | Contacts for agent/carrier/etc. — includes Name, Email, Phone, AssociationType |
| GetContact | Single contact |
| GetAgentCommissionByCriteria | Agent commissions |
| GetAgentStatementRecords | Agent statements |
| GetISOClasses | ISO classification codes |

### Read Operations — Financial

| Operation | Purpose |
|-----------|---------|
| GetCashHeaders | Cash receipt headers |
| GetCashDetails | Cash receipt line items |
| GetCashTotals | Cash totals/summary |
| GetPFCs | Premium finance companies |
| GetSurplusLineCoverages | Surplus lines data |
| GetCarrierPolicyFees | Fee schedules by carrier |
| GetEnabledInsuranceCodes | Enabled insurance codes |

### Read Operations — System

| Operation | Purpose |
|-----------|---------|
| GetCompanyRules | Company configuration |
| GetSections | UI sections (sectionIds map to areas of the app) |
| GetUserAppFeaturesAccessControl | User permissions |
| GetAppClient | App client configuration |
| GetActionsBySectionId | Actions available per section |
| GetActionNotifications | Notification templates |
| GetActionOptionLists | Action option configurations |
| GetActionOptions | Specific action options |
| GetActivityDefaultNoteContentByActionId | Default note text for actions |
| GetBuildInEventPayloads | System event payloads |
| GetDepartments | Department list |
| GetAdditionalInsuredForms | AI form types |
| GetAdditionalInterestTypes | Interest types |
| GetCountries | Country list |
| GetAlertsByAssociation | Alerts for a record |
| GetLOBs / GetLOB / GetSubLOBs / GetSubLOB | LOB hierarchy |
| KeepMeAlive | Session keepalive |
| GetDashboardReport | Monthly sales data — JSON with Year, Month, TotalPolicies, Premium, AveragePremium, AgentCommission, NetMGACommission, GrossMGACommission, NewBusinessPremium, NewBusinessCount, RenewalsPremium, RenewalsCount per month |
| GetAnnouncements | System announcements (created by jcdp) |

---

## LOB Codes (from SOAP responses)

| Code | Description | Known Sub-LOBs |
|------|-------------|----------------|
| CG | General Liability | AC=Artisans/Contractors, LL=Liquor Liability, HM=Non-Artisans, SE=Special Events |
| (others TBD — need to call GetInsuranceLOBs) | | |

---

## Carrier Data (from SOAP responses)

| Number | Name | NAIC | Contact Email | City/State |
|--------|------|------|---------------|------------|
| 1 | Mount Vernon Fire Insurance Co. | — | joanneh@usli.com | — |
| 2 | United States Liability Ins Co (USLI) | 25895 | joanneh@usli.com | Wayne, PA |
| 21 | Mid-Continent Casualty Company | — | GAMail@mcg-ins.com | — (inactive) |
| 28 | Mid-Continent Excess & Surplus | — | GAMail@mcg-ins.com | — |
| (others visible in GetQuoteActivityCarriers response) | | | | |

---

## GIC Users (from REST /api/users and /api/roles responses)

Key users with roles:

| Username | Role(s) | Name | Email |
|----------|---------|------|-------|
| arivera | Underwriter | — | quote@gicunderwriters.com |
| bbriz | Accounting | Beatriz Briz | bbriz@gicunderwriters.com |
| carlosdp | Marketing Rep | Carlos Diaz-Padron | carlosdp@gicunderwriters.com |
| carmendp | Accounting, Executive | Carmen Diaz-Padron | cdp@gicunderwriters.com |
| carmeng | Marketing Rep, Customer Service | Carmen Guerrero | cguerrero@gicunderwriters.com |
| ccerto | Underwriter | Craig Certo | craig@indemn.ai |
| ariadna | Developer | Ariadna Marill | ariadna@unisoftonline.com (Unisoft staff) |
| carlos | Developer | Carlos Oporto | carlos@unisoftonline.com (Unisoft staff) |

---

## Integration Strategy (Updated After Recon)

### The Game-Changer

We do NOT need UI automation. The ClickOnce app communicates via SOAP and REST APIs that we can call directly from Python. The SOAP service has the full CRUD operations we need: SetQuote, SetSubmission, SetActivity.

### Priority 1: Prototype (Python to SOAP to SetQuote)

1. Authenticate via WS-Security to get SecurityContextToken
2. Call GetToken to get AccessToken
3. Call SetQuote with Action="Insert" and the quote data
4. Call SetSubmission to add carrier/broker
5. Verify via GetQuote/GetSubmissions

Python libraries: zeep (SOAP client) or raw requests with XML templates.

### Priority 2: Read Reference Data

1. GetInsuranceLOBs — all LOB codes
2. GetInsuranceSubLOBs — sub-LOB codes per LOB
3. GetInsuranceCarriers — full carrier list with numbers
4. GetAgentsAndProspectsForLookup — agent directory

This gives us the lookup data to map our email pipeline's extracted fields to Unisoft's codes.

### Priority 3: Full Automation Pipeline

Our email intelligence pipeline extracts: insured name, LOB, agent, carrier, reference numbers, etc.
Map these to SetQuote fields and call the API to create entries automatically.

### The WCF Challenge

The SOAP service uses WS-Security with SecurityContextToken (SCT), WS-ReliableMessaging, and HMAC-SHA1 signatures. This is non-trivial to implement in Python. Options:

1. **zeep** — Python SOAP library, supports WS-Security but SCT support may need custom handling
2. **Replay approach** — capture a valid session's security tokens and replay, refreshing as needed
3. **Ask Unisoft** — Robert Gonzalez may be able to provide a simpler REST endpoint (they clearly have the infrastructure for it given the REST API gateway exists)

The REST API gateway is much simpler to call but currently only covers tasks, users, brokers, and documents — not quotes/submissions. If Unisoft exposes SetQuote via REST, that would be ideal.

---

## UAT Environment Details

| Item | Value |
|------|-------|
| ClickOnce URL | `https://ins-gic-client-uat-app.azurewebsites.net/publish.htm` |
| App Version | 3.0.0.11 |
| UAT Username | `ccerto` |
| UAT Password | `GIC2026$$!` |
| SOAP Service | `https://services.uat.gicunderwriters.co/management/imsservice.svc` |
| File Service | `https://services.uat.gicunderwriters.co/attachments/insfileservice.svc` |
| REST Gateway | `https://ins-gic-api-gateway-uat-app.azurewebsites.net` |
| SignalR Hub | `https://ins-gic-nothub-prod-app.azurewebsites.net` |
| SOAP Auth | `UniClient` / `J5j!}7=r/z` then GetToken with `GIC_UAT` |
| REST Auth | POST `/api/authentication/login` with `ccerto` / `GIC2026$$!` |
| Windows EC2 | `i-0dc2563c9bc92aa0e` (indemn-windows-server, t3.xlarge) |
| EC2 RDP | SSM port forwarding, Administrator / `Welcome1!` |

---

## API Access Status

| API | Status | Notes |
|-----|--------|-------|
| SOAP Service (UAT) | WORKING — confirmed via Fiddler | Full CRUD operations available |
| REST Gateway (UAT) | WORKING — confirmed via Fiddler | Tasks, users, brokers, documents |
| Swagger Docs | PENDING — JC emailed Robert Gonzalez 2026-03-30 | Would give us the complete API spec |
| WSDL | NOT YET FETCHED — should be at imsservice.svc?wsdl | Would document all SOAP operations |
| Production API | UNKNOWN — production endpoints not yet identified | Likely similar URLs without "uat" |

---

## Questions (Updated)

1. Can we get the WSDL from `services.uat.gicunderwriters.co/management/imsservice.svc?wsdl`? This would document every operation and its parameters.
2. Is there a REST equivalent for SetQuote/SetSubmission on the API gateway? (The gateway already handles tasks, brokers, etc.)
3. What are all the LOB codes? (Need to call GetInsuranceLOBs)
4. What are the FormOfBusiness codes? (C=Corporation confirmed, others unknown)
5. What is the production API endpoint? (vs UAT)
6. Can we get a simpler auth mechanism than WCF WS-Security? (Token-based would be ideal)

---

## Changelog

| Date | Update | Source |
|------|--------|--------|
| 2026-03-31 | Initial creation from web research + JC walkthrough | Web search, meeting transcript |
| 2026-04-01 | MAJOR UPDATE: Complete API surface from Fiddler traffic interception | 2 Fiddler captures (export1.saz: 648 sessions, export2.saz: 1629 sessions), ClickOnce app on Windows EC2 |
