/**
 * Act 2 Phase 1 — Email Triage
 * 15s animation: 23 emails sort into 5 color-coded Kanban columns
 * Counter: "23 classified in 47 seconds"
 *
 * Access at: http://localhost:5180/?page=triage
 */
import { useEffect, useState } from "react";
import "./triage.css";

const avatarColors = [
  "#4752a3", "#a67cb7", "#3b82f6", "#22c55e", "#f59e0b",
  "#6366f1", "#ec4899", "#14b8a6", "#8b5cf6", "#ef4444",
  "#0ea5e9", "#f97316",
];

type Column = "green" | "blue" | "orange" | "purple" | "gray";

interface EmailCard {
  sender: string;
  subject: string;
  tag: string;
  column: Column;
}

const emailCards: EmailCard[] = [
  // New Submissions (green) — 8
  { sender: "Jessica Parker", subject: "Riverside Landscaping LLC", tag: "New — GL", column: "green" },
  { sender: "David Kim", subject: "Summit Electric LLC", tag: "New — GL", column: "green" },
  { sender: "Ryan O'Brien", subject: "Harbor View Restaurant Group", tag: "New — BOP", column: "green" },
  { sender: "James Wilson", subject: "Bright Horizons Daycare", tag: "New — GL", column: "green" },
  { sender: "Emily Grasso", subject: "Pinnacle Roofing & Solar", tag: "New — GL", column: "green" },
  { sender: "Jennifer Adams", subject: "Crossroads Trucking LLC", tag: "New — Auto", column: "green" },
  { sender: "Nicole Evans", subject: "Golden Gate Landscaping", tag: "New — GL", column: "green" },
  { sender: "Rachel Kim", subject: "Cascade Plumbing & HVAC", tag: "New — GL/WC", column: "green" },

  // Quote Ready (blue) — 4
  { sender: "Mark Chen", subject: "Apex Manufacturing — GL & WC", tag: "Quote Ready", column: "blue" },
  { sender: "Tom Bradley", subject: "Greenfield Construction — BR", tag: "Quote Ready", column: "blue" },
  { sender: "Daniel Ruiz", subject: "Mountain View Medical — PL", tag: "Quote Ready", column: "blue" },
  { sender: "Robert Tran", subject: "Valley Tech Solutions — Cyber", tag: "Quote Ready", column: "blue" },

  // Follow-Up Needed (orange) — 6
  { sender: "Sarah Wells", subject: "Pacific Dental — Loss Runs", tag: "Missing Info", column: "orange" },
  { sender: "Michelle Huang", subject: "Metro Plumbing — Sub Certs", tag: "Missing Info", column: "orange" },
  { sender: "Karen Mitchell", subject: "Westside Auto — Incomplete", tag: "Missing Info", column: "orange" },
  { sender: "Andrew Park", subject: "Cedar Creek — Loss Runs", tag: "Overdue", column: "orange" },
  { sender: "Samantha Cole", subject: "Bright Star — Prior Carrier", tag: "Missing Info", column: "orange" },
  { sender: "Michael Byrne", subject: "Atlas Logistics — Endorsement", tag: "Missing Info", column: "orange" },

  // Renewals (purple) — 3
  { sender: "Lisa Torres", subject: "AutoFleet Transport (4/15)", tag: "Renewal", column: "purple" },
  { sender: "Chris Nakamura", subject: "WC Policy #GR-4419 (4/22)", tag: "Renewal", column: "purple" },
  { sender: "Kevin Patel", subject: "GL Policy #PR-7802 (5/1)", tag: "Renewal", column: "purple" },

  // Not a Submission (gray) — 2
  { sender: "Amanda Foster", subject: "Out of Office — Back April 1", tag: "Auto-Reply", column: "gray" },
  { sender: "Brian Murphy", subject: "Weekly Insurance Market Digest", tag: "Newsletter", column: "gray" },
];

// Shuffle order so cards don't arrive in column-grouped order
const arrivalOrder = [
  0, 8, 12, 1, 18, 9, 2, 13, 20, 3, 10, 14, 19, 4, 21, 15, 5, 11, 16, 6, 17, 22, 7,
];

const columns: { key: Column; title: string; expected: number }[] = [
  { key: "green", title: "New Submission", expected: 8 },
  { key: "blue", title: "Quote Ready", expected: 4 },
  { key: "orange", title: "Follow-Up Needed", expected: 6 },
  { key: "purple", title: "Renewal", expected: 3 },
  { key: "gray", title: "Not a Submission", expected: 2 },
];

export default function EmailTriage() {
  const [arrivedSet, setArrivedSet] = useState<Set<number>>(new Set());
  const [sortedCount, setSortedCount] = useState(0);
  const [showCounts, setShowCounts] = useState(false);
  const [showCounter, setShowCounter] = useState(false);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];

    // Cards arrive with accelerating cadence
    // First 5: 700ms apart, next 8: 450ms, last 10: 300ms
    let t = 500;
    arrivalOrder.forEach((cardIdx, i) => {
      const delay = i < 5 ? 700 : i < 13 ? 450 : 300;
      t += delay;
      timers.push(
        setTimeout(() => {
          setArrivedSet((prev) => new Set(prev).add(cardIdx));
          setSortedCount(i + 1);
        }, t)
      );
    });

    // Show column counts after all cards
    timers.push(setTimeout(() => setShowCounts(true), t + 600));

    // Show bottom counter
    timers.push(setTimeout(() => setShowCounter(true), t + 1200));

    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="triage-page">
      <div className="triage-header">
        <img src="/brand/logo-iris.svg" alt="indemn" />
        <div className="triage-header-center">
          <span className="triage-progress-label">Sorted:</span>
          <span className="triage-progress-count">
            {sortedCount} / 23
          </span>
        </div>
        <span className="triage-header-badge">Inbox Associate</span>
      </div>

      <div className="triage-board">
        {columns.map((col) => {
          const colCards = emailCards
            .map((card, idx) => ({ ...card, idx }))
            .filter((c) => c.column === col.key);
          const visibleCount = colCards.filter((c) =>
            arrivedSet.has(c.idx)
          ).length;

          return (
            <div key={col.key} className={`triage-column ${col.key}`}>
              <div className="triage-column-header">
                <span className="triage-column-title">{col.title}</span>
                <span
                  className={`triage-column-count ${showCounts ? "visible" : ""}`}
                >
                  {visibleCount}
                </span>
              </div>
              <div className="triage-column-body">
                {colCards.map((card) => {
                  const initials = card.sender
                    .split(" ")
                    .map((n) => n[0])
                    .join("");
                  const colorIdx = card.idx % avatarColors.length;
                  return (
                    <div
                      key={card.idx}
                      className={`triage-card ${arrivedSet.has(card.idx) ? "visible" : ""}`}
                    >
                      <div
                        className="triage-card-avatar"
                        style={{ background: avatarColors[colorIdx] }}
                      >
                        {initials}
                      </div>
                      <div className="triage-card-content">
                        <div className="triage-card-subject">
                          {card.subject}
                        </div>
                        <div className="triage-card-sender">
                          {card.sender}
                        </div>
                      </div>
                      <span className={`triage-card-tag ${card.column}`}>
                        {card.tag}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div className={`triage-counter ${showCounter ? "visible" : ""}`}>
        <span className="triage-counter-text">
          <span className="triage-counter-highlight">23</span> emails.{" "}
          <span className="triage-counter-highlight">47</span> seconds.{" "}
          Zero human input.
        </span>
      </div>
    </div>
  );
}
