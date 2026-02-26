---
ask: "How are PDFs generated in the Observatory — both frontend and CLI?"
created: 2026-02-26
workstream: gic-observatory
session: 2026-02-26-a
sources:
  - type: codebase
    description: "Report components, generateReport.tsx, styles.ts, CLI scripts, report-library skill, report-generate skill"
  - type: codebase
    ref: "/Users/home/Repositories/indemn-observability/frontend/src/components/report/"
    name: "Report component directory"
  - type: codebase
    ref: "/Users/home/Repositories/indemn-observability/scripts/"
    name: "CLI extraction and generation scripts"
---

# PDF Generation Patterns

## Two Generation Paths

### Path 1: Frontend (Production — Browser Download)

Used when a user clicks "Customer Analytics (PDF)" in the Observatory UI.

**Flow:**
1. `ReportButton.tsx` triggers data fetch
2. `useCustomerReportData()` hook calls API endpoints
3. `generateReport()` in `lib/generateReport.tsx` creates PDF via `@react-pdf/renderer`
4. Browser downloads the file

**Library:** `@react-pdf/renderer v4.3.2` — renders React components to PDF in the browser.

**Key utility:**
```typescript
// lib/generateReport.tsx
import { pdf } from '@react-pdf/renderer';

export async function generateReport(document: React.ReactElement, filename: string) {
  const blob = await pdf(document).toBlob();
  // Trigger browser download
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
}
```

### Path 2: CLI (Ad-hoc / Custom Reports)

Used for one-off reports or custom data views. Two-file pattern:

**Extraction (Python):**
```bash
python scripts/extract-{name}.py --org gic --date-from 2026-02-01 --date-to 2026-02-28
# Outputs: data/{name}-{date}.json
```

**Rendering (Node.js JSX):**
```bash
NODE_PATH=frontend/node_modules node scripts/generate-{name}.jsx data/{name}.json
# Outputs: reports/{name}.pdf
```

**Important:** CLI renderers use `React.createElement` (h) syntax, NOT JSX compilation. Barlow fonts must be registered inline (cannot import from Vite). See existing scripts for the pattern.

## Report Component Structure

### Wrapper (CustomerReportDocument.tsx)
```tsx
<Document>
  <ReportCover {...coverData} />
  <ReportHandoffPage {...handoffData} />
  <ReportCSRBreakdownPage {...csrData} />
  <ReportToolAnalysisPage {...toolData} />
  {/* NEW: ReportCSRTimeOfDayPage would go here */}
</Document>
```

### Page Pattern
Every page follows:
```tsx
<Page size="A4" style={pageStyles}>
  {/* Header: title + page number */}
  <View style={headerStyles}>
    <Text>{pageTitle}</Text>
    <Text>Page {n}</Text>
  </View>

  {/* Content cards */}
  <View style={cardStyles}>
    {/* Metric cards, charts, tables */}
  </View>

  {/* Footer */}
  <PageFooter label={reportTitle} />
</Page>
```

## Component Cookbook

### MetricCard
Highlight number with label. Used on cover and section pages.
```tsx
<View style={{background: '#f4f3f8', borderRadius: 6, padding: 16}}>
  <Text style={{fontSize: 24, fontWeight: 700, color: '#4752a3'}}>{value}</Text>
  <Text style={{fontSize: 10, color: '#6b7280'}}>{label}</Text>
</View>
```

### HorizontalBar
Proportional bar chart (e.g., outcome distribution).

### PieChart
SVG-based pie chart rendered inline in PDF.

### Table (Header + Rows)
Striped table with alternating row backgrounds.
```tsx
<View style={tableHeaderStyle}>
  <Text style={colStyle}>{header}</Text>
  ...
</View>
{rows.map((row, i) => (
  <View style={{...rowStyle, background: i % 2 ? '#f9fafb' : 'white'}}>
    <Text>{row.value}</Text>
  </View>
))}
```

### Badge
Colored tag for status/category indicators.

### PageFooter
Absolute-positioned at bottom with top border, report label, and page number.

## Brand System (styles.ts)

```typescript
// Colors
const IRIS = '#4752a3';      // Primary
const LILAC = '#a67cb7';     // Secondary
const EGGPLANT = '#1e2553';  // Dark
const LIME = '#e0da67';      // Accent
const OLIVE = '#2a2b1a';     // Text dark

// Semantic
const SUCCESS = '#4752a3';
const HANDOFF = '#a67cb7';
const ABANDONED = '#1e2553';
const NEUTRAL = '#9ca3af';

// Layout
const PAGE_PADDING = 40;  // points
const CARD_BG = '#f4f3f8';
const CARD_RADIUS = 6;
const CARD_PADDING = 16;

// Typography — Barlow
// Registered at app startup in styles.ts
Font.register({
  family: 'Barlow',
  fonts: [
    { src: '/fonts/Barlow-Regular.ttf', fontWeight: 400 },
    { src: '/fonts/Barlow-Medium.ttf', fontWeight: 500 },
    { src: '/fonts/Barlow-SemiBold.ttf', fontWeight: 600 },
    { src: '/fonts/Barlow-Bold.ttf', fontWeight: 700 },
  ]
});
```

## Skills for Report Generation

### `/report-generate` — End-to-end workflow
Four phases: Understand → Design → Build → Execute.
- Phase 1: Clarify subject, org, date range, audience, key questions
- Phase 2: Design page-by-page outline with data sources
- Phase 3: Write extraction + renderer scripts
- Phase 4: Run the pipeline

### `/report-library` — Reference material
- Brand system details
- Component cookbook with code examples
- Data source reference (collections + API endpoints)
- CLI script templates
- Existing report type inventory

## Adding a New Page to Customer Analytics

To add the time-of-day distribution:

1. **Create component**: `frontend/src/components/report/ReportCSRTimeOfDayPage.tsx`
2. **Add data to hook**: Extend `useCustomerReportData()` to fetch time-of-day data
3. **Add API endpoint** (if needed): New endpoint or extend `/csr-metrics` response
4. **Add to wrapper**: Include in `CustomerReportDocument.tsx` page sequence
5. **For CLI**: Create extraction script for the new data, extend renderer

## Visualization Options for Time-of-Day

**In @react-pdf/renderer, you cannot use Recharts.** Charts must be built with SVG primitives or pre-rendered.

Options:
- **Heatmap grid**: 24 rows (hours) × 3 columns (20-min buckets), color intensity = activity level
- **Stacked bar chart**: 72 bars (one per 20-min slot), segments per CSR, built with SVG `<Rect>`
- **Table with sparklines**: Per-CSR rows with mini bar charts showing activity distribution
- **Simple table**: Time bucket rows with CSR columns showing message counts (least visual, most data-dense)

Note: The existing `ReportVolumePage.tsx` already has a 24-hour timeline visualization for conversation volume — can be adapted for the CSR time-of-day view with finer granularity.
