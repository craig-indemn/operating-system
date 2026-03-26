/**
 * Act 2 Phase 3 — Board Zoom Out
 * ~15s animation: pull back to show all 23 emails processed with outcomes
 * Shows what happened while we watched the deep dive on one email
 *
 * Access at: http://localhost:5180/?page=zoomout
 */
import { useEffect, useState } from "react";
import "./zoomout.css";

type Column = "green" | "blue" | "orange" | "purple" | "done";

interface MiniCard {
  text: string;
  status: string;
  statusClass: string;
  column: Column;
  stale?: boolean;
}

const cards: MiniCard[] = [
  // Fully processed / done (8)
  { text: "Riverside Landscaping — GL", status: "AMS updated", statusClass: "sent", column: "done" },
  { text: "Summit Electric — GL", status: "AMS updated", statusClass: "sent", column: "done" },
  { text: "Harbor View Restaurant — BOP", status: "AMS updated", statusClass: "sent", column: "done" },
  { text: "Bright Horizons Daycare — GL", status: "AMS updated", statusClass: "sent", column: "done" },
  { text: "Pinnacle Roofing — GL", status: "AMS updated", statusClass: "sent", column: "done" },
  { text: "Crossroads Trucking — Auto", status: "AMS updated", statusClass: "sent", column: "done" },
  { text: "Golden Gate Landscaping — GL", status: "AMS updated", statusClass: "sent", column: "done" },
  { text: "Cascade Plumbing — GL/WC", status: "AMS updated", statusClass: "sent", column: "done" },

  // Quote Ready — carrier quotes extracted (4)
  { text: "Apex Manufacturing — GL & WC", status: "Quote extracted", statusClass: "sent", column: "blue" },
  { text: "Greenfield Construction — BR", status: "Quote extracted", statusClass: "sent", column: "blue" },
  { text: "Mountain View Medical — PL", status: "Quote extracted", statusClass: "sent", column: "blue" },
  { text: "Valley Tech — Cyber", status: "Quote extracted", statusClass: "sent", column: "blue" },

  // Follow-Up — drafts ready (6)
  { text: "Pacific Dental — Loss Runs", status: "Draft ready", statusClass: "draft", column: "orange" },
  { text: "Metro Plumbing — Sub Certs", status: "Draft ready", statusClass: "draft", column: "orange" },
  { text: "Westside Auto — Incomplete", status: "Draft ready", statusClass: "draft", column: "orange" },
  { text: "Cedar Creek — Loss Runs", status: "Auto follow-up", statusClass: "draft", column: "orange", stale: true },
  { text: "Bright Star — Prior Carrier", status: "Draft ready", statusClass: "draft", column: "orange" },
  { text: "Atlas Logistics — Endorsement", status: "Auto follow-up", statusClass: "draft", column: "orange", stale: true },

  // Renewals — flagged (3)
  { text: "AutoFleet Transport (4/15)", status: "14 days", statusClass: "flagged", column: "purple" },
  { text: "WC Policy #GR-4419 (4/22)", status: "21 days", statusClass: "flagged", column: "purple" },
  { text: "GL Policy #PR-7802 (5/1)", status: "30 days", statusClass: "flagged", column: "purple" },
];

const columnDefs: { key: Column; title: string; count: number; color: string }[] = [
  { key: "done", title: "Fully Processed", count: 8, color: "#4752a3" },
  { key: "blue", title: "Quotes Extracted", count: 4, color: "#3b82f6" },
  { key: "orange", title: "Drafts Ready", count: 6, color: "#f59e0b" },
  { key: "purple", title: "Renewals Flagged", count: 3, color: "#a67cb7" },
];

export default function BoardZoomOut() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    // step 1-4: columns appear one by one
    // step 5: cards start appearing (staggered)
    // step 5+N: each card
    // final: summary bar
    const timers: ReturnType<typeof setTimeout>[] = [];
    timers.push(setTimeout(() => setStep(1), 500));
    timers.push(setTimeout(() => setStep(2), 900));
    timers.push(setTimeout(() => setStep(3), 1300));
    timers.push(setTimeout(() => setStep(4), 1700));

    // Cards appear starting at 2.2s, staggered 150ms
    const allCards = cards.length;
    for (let i = 0; i < allCards; i++) {
      timers.push(setTimeout(() => setStep(5 + i), 2200 + i * 150));
    }

    // Summary bar
    timers.push(setTimeout(() => setStep(5 + allCards), 2200 + allCards * 150 + 800));

    return () => timers.forEach(clearTimeout);
  }, []);

  const colOrder: Column[] = ["done", "blue", "orange", "purple"];

  return (
    <div className="zoomout-page">
      <div className="zoomout-header">
        <img src="/brand/logo-iris.svg" alt="indemn" />
        <span className="zoomout-header-badge">Inbox Associate</span>
      </div>

      <div className="zoomout-board">
        {colOrder.map((colKey, colIdx) => {
          const def = columnDefs.find((d) => d.key === colKey)!;
          const colCards = cards.filter((c) => c.column === colKey);

          return (
            <div
              key={colKey}
              className={`zoomout-column ${colKey} ${step >= colIdx + 1 ? "visible" : ""}`}
            >
              <div className="zoomout-col-header">
                <span className="zoomout-col-title">{def.title}</span>
                <span className="zoomout-col-count">{def.count}</span>
              </div>
              <div className="zoomout-col-body">
                {colCards.map((card, i) => {
                  const globalIdx = cards.indexOf(card);
                  return (
                    <div
                      key={i}
                      className={`zoomout-mini ${step >= 5 + globalIdx ? "visible" : ""}`}
                    >
                      <div
                        className="zoomout-mini-dot"
                        style={{ background: def.color }}
                      />
                      <span className="zoomout-mini-text">{card.text}</span>
                      {card.stale && (
                        <span className="zoomout-stale-badge">7d+</span>
                      )}
                      <span className={`zoomout-mini-status ${card.statusClass}`}>
                        {card.status}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div
        className={`zoomout-summary ${step >= 5 + cards.length ? "visible" : ""}`}
      >
        <span className="zoomout-summary-text">
          <span className="zoomout-summary-highlight">23</span> emails.{" "}
          <span className="zoomout-summary-highlight">3</span> minutes.{" "}
          <span className="zoomout-summary-highlight">8</span> fully resolved.{" "}
          <span className="zoomout-summary-highlight">15</span> drafts ready.
        </span>
      </div>
    </div>
  );
}
