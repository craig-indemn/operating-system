/**
 * Act 2 Phase 2 — Email Deep Dive
 * ~40s animation: email opens → ACORD extraction → gap analysis → draft reply → auto-send
 *
 * Access at: http://localhost:5173/?page=deepdive
 */
import { useEffect, useState } from "react";
import "./deepdive.css";
import "./narration.css";

const extractionFields = [
  { label: "Business", value: "Riverside Landscaping LLC" },
  { label: "Revenue", value: "$1.2M" },
  { label: "Employees", value: "14" },
  { label: "Operations", value: "Commercial landscaping, tree removal" },
  { label: "Coverage", value: "GL $1M/$2M" },
];

const gapItems = [
  { label: "Business information", status: "complete" as const },
  { label: "Operations detail", status: "complete" as const },
  { label: "Loss runs (3 years)", status: "missing" as const },
  { label: "Subcontractor schedule", status: "missing" as const },
  { label: "Requested coverage", status: "complete" as const },
];

const draftLines = [
  {
    text: "Hi Jessica \u2014 thanks for sending over Riverside Landscaping. I\u2019ve reviewed the ACORD 125 and 126.",
    className: "greeting",
  },
  { text: "To move forward, I\u2019ll need:", className: "" },
  { text: "1. Three years of loss runs", className: "numbered" },
  {
    text: "2. Subcontractor schedule with certificates",
    className: "numbered",
  },
  {
    text: "Everything else looks good. Happy to prioritize this once those come in.",
    className: "closing",
  },
];

export default function EmailDeepDive() {
  const [step, setStep] = useState(0);
  const [narrationIdx, setNarrationIdx] = useState(-1);

  useEffect(() => {
    // Frame 1: Email card appears (0-5s)
    // step 1: email card visible
    // step 2: attachment 1
    // step 3: attachment 2
    //
    // Frame 2: Data extraction (5-15s)
    // step 4-8: extraction fields one by one
    // step 9: AMS callout
    //
    // Frame 3: Gap analysis (15-23s)
    // step 10: gap card visible
    // step 11-15: gap items one by one
    // step 16: completeness bar
    //
    // Frame 4: Draft reply (23-35s)
    // step 17: draft card visible
    // step 18-22: draft lines one by one
    // step 23: auto-send toggle
    // step 24: sent confirmation
    //
    // Frame 5: done (35-40s) — hold for recording

    const timings: [number, number][] = [
      // Frame 1 — Email (0-2.5s)
      [1, 400],
      [2, 1000],
      [3, 1500],
      // Frame 2 — Extraction (2.5-7s)
      [4, 2500],
      [5, 3100],
      [6, 3700],
      [7, 4300],
      [8, 4900],
      [9, 5800],
      // Frame 3 — Gap analysis (7-10.5s)
      [10, 7000],
      [11, 7500],
      [12, 7900],
      [13, 8300],
      [14, 8700],
      [15, 9100],
      [16, 9600],
      // Frame 4 — Draft reply (10.5-16s)
      [17, 10500],
      [18, 11200],
      [19, 11900],
      [20, 12600],
      [21, 13300],
      [22, 14000],
      [23, 15000],
      [24, 16000],
    ];

    const narrationTimings: [number, number][] = [
      [0, 400],     // "New submission from Worthington Insurance"
      [1, 2500],    // "Extracting data from ACORD 125 and 126"
      [2, 7000],    // "Running completeness check"
      [3, 10500],   // "Generating follow-up reply"
      [4, 16000],   // "Reply sent automatically"
    ];

    const timers = timings.map(([s, ms]) => setTimeout(() => setStep(s), ms));
    const nTimers = narrationTimings.map(([s, ms]) => setTimeout(() => setNarrationIdx(s), ms));
    timers.push(...nTimers);
    return () => timers.forEach(clearTimeout);
  }, []);

  const narrationTexts = [
    "New submission from Worthington Insurance",
    "Extracting data from ACORD 125 and 126",
    "Running completeness check",
    "Generating follow-up reply",
    "Reply sent automatically",
  ];
  const activeNarration = narrationIdx >= 0 ? narrationTexts[narrationIdx] : null;

  return (
    <div className="deepdive">
      <div className="dd-brand-bar">
        <img src="/brand/logo-iris.svg" alt="indemn" />
        <span className="dd-brand-badge">Inbox Associate</span>
      </div>

      <div className="dd-layout">
        {/* Left column: Email + Extraction */}
        <div className="dd-left">
          {/* Email card */}
          <div className={`dd-card ${step >= 1 ? "visible" : ""}`}>
            <div className="dd-card-header">
              <EmailIcon />
              Incoming Submission
            </div>
            <div className="dd-card-body">
              <div className="dd-email-from">
                From: <span>jessica.parker@worthington-insurance.com</span>
              </div>
              <div className="dd-email-subject">
                New Submission — Riverside Landscaping LLC
              </div>
              <div className="dd-attachments">
                <div
                  className={`dd-attachment ${step >= 2 ? "visible" : ""}`}
                >
                  <PdfIcon />
                  ACORD 125.pdf
                </div>
                <div
                  className={`dd-attachment ${step >= 3 ? "visible" : ""}`}
                >
                  <PdfIcon />
                  ACORD 126.pdf
                </div>
              </div>
            </div>
          </div>

          {/* Data extraction card */}
          <div className={`dd-card ${step >= 4 ? "visible" : ""}`}>
            <div className="dd-card-header">
              <ExtractIcon />
              ACORD Data Extraction
            </div>
            <div className="dd-card-body">
              {extractionFields.map((field, i) => (
                <div
                  key={field.label}
                  className={`dd-field-row ${step >= i + 4 ? "visible" : ""}`}
                >
                  <span className="dd-field-label">{field.label}</span>
                  <span className="dd-field-value">{field.value}</span>
                  <div
                    className={`dd-field-check ${step >= i + 4 ? "visible" : ""}`}
                  >
                    <CheckSmall />
                  </div>
                </div>
              ))}
              <div className={`dd-ams-callout ${step >= 9 ? "visible" : ""}`}>
                <AmsIcon />
                Direct AMS integration — no API required
              </div>
            </div>
          </div>
        </div>

        {/* Right column: Gap analysis + Draft */}
        <div className="dd-right">
          {/* Gap analysis */}
          <div className={`dd-card ${step >= 10 ? "visible" : ""}`}>
            <div className="dd-card-header">
              <GapIcon />
              Completeness Check
            </div>
            <div className="dd-card-body">
              {gapItems.map((item, i) => (
                <div
                  key={item.label}
                  className={`dd-gap-item ${step >= i + 11 ? "visible" : ""}`}
                >
                  <div className={`dd-gap-icon ${item.status}`}>
                    {item.status === "complete" ? (
                      <CheckSmall />
                    ) : (
                      <WarningSmall />
                    )}
                  </div>
                  <span className="dd-gap-label">{item.label}</span>
                  <span className={`dd-gap-status ${item.status}`}>
                    {item.status === "complete" ? "Complete" : "Missing"}
                  </span>
                </div>
              ))}
              <div
                className={`dd-completeness ${step >= 16 ? "visible" : ""}`}
              >
                <div className="dd-completeness-label">
                  <span>Completeness</span>
                  <span>6 / 8 fields</span>
                </div>
                <div className="dd-completeness-bar">
                  <div
                    className={`dd-completeness-fill ${step >= 16 ? "filled" : ""}`}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Draft reply */}
          <div className={`dd-card ${step >= 17 ? "visible" : ""}`}>
            <div className="dd-card-header">
              <DraftIcon />
              Auto-Generated Reply
            </div>
            <div className="dd-card-body">
              {draftLines.map((line, i) => (
                <div
                  key={i}
                  className={`dd-draft-line ${line.className} ${step >= i + 18 ? "visible" : ""}`}
                >
                  {line.text}
                </div>
              ))}
              <div className={`dd-autosend ${step >= 23 ? "visible" : ""}`}>
                <div className="dd-autosend-toggle">
                  <div className="dd-toggle-track">
                    <div className="dd-toggle-thumb" />
                  </div>
                  <span className="dd-autosend-label">Auto-send</span>
                </div>
                <div
                  className={`dd-autosend-status ${step >= 24 ? "visible" : ""}`}
                >
                  <CheckSmall />
                  Sent at 8:01 AM
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="narration-bar">
        {activeNarration && (
          <span className="narration-text visible" key={narrationIdx}>
            {activeNarration}
          </span>
        )}
      </div>
    </div>
  );
}

/* SVG Icons */

function EmailIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  );
}

function PdfIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}

function ExtractIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
      <line x1="3" y1="9" x2="21" y2="9" />
      <line x1="9" y1="21" x2="9" y2="9" />
    </svg>
  );
}

function GapIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 11l3 3L22 4" />
      <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
    </svg>
  );
}

function DraftIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  );
}

function AmsIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="16 16 12 12 8 16" />
      <line x1="12" y1="12" x2="12" y2="21" />
      <path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3" />
    </svg>
  );
}

function CheckSmall() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function WarningSmall() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}
