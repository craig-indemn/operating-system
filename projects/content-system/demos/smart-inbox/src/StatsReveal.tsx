/**
 * Act 3 — Stats Reveal
 * ~15s animation: clean stats view with animated counters
 * "Your inbox used to be a bottleneck. Now it's a pipeline."
 *
 * Access at: http://localhost:5180/?page=stats
 */
import { useEffect, useState } from "react";
import "./stats.css";

const stats = [
  { number: "23", label: "Emails processed\nin 3 minutes" },
  { number: "8", label: "Fully resolved\nzero human touch" },
  { number: "15", label: "Drafts ready\nfor review" },
];

export default function StatsReveal() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const timers = [
      setTimeout(() => setStep(1), 800),    // first stat card
      setTimeout(() => setStep(2), 1600),   // second stat card
      setTimeout(() => setStep(3), 2400),   // third stat card
      setTimeout(() => setStep(4), 3800),   // detail items
      setTimeout(() => setStep(5), 4400),   // detail item 2
      setTimeout(() => setStep(6), 5000),   // detail item 3
      setTimeout(() => setStep(7), 6500),   // tagline
    ];
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="stats-page">
      <div className="stats-brand">
        <img src="/brand/logo-iris.svg" alt="indemn" />
      </div>

      <div className="stats-content">
        <div className="stats-row">
          {stats.map((stat, i) => (
            <div
              key={i}
              className={`stat-card ${step >= i + 1 ? "visible" : ""}`}
            >
              <div className="stat-number">{stat.number}</div>
              <div className="stat-label">
                {stat.label.split("\n").map((line, j) => (
                  <span key={j}>
                    {line}
                    {j === 0 && <br />}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="stats-details">
          <div className={`stats-detail-item ${step >= 4 ? "visible" : ""}`}>
            <div className="stats-detail-icon check">
              <CheckIcon />
            </div>
            <span className="stats-detail-text">
              Zero submissions lost. Zero duplicates.
            </span>
          </div>
          <div className={`stats-detail-item ${step >= 5 ? "visible" : ""}`}>
            <div className="stats-detail-icon shield">
              <ShieldIcon />
            </div>
            <span className="stats-detail-text">
              AMS updated automatically — no API required
            </span>
          </div>
          <div className={`stats-detail-item ${step >= 6 ? "visible" : ""}`}>
            <div className="stats-detail-icon check">
              <ClockIcon />
            </div>
            <span className="stats-detail-text">
              Stale submissions auto-followed up
            </span>
          </div>
        </div>

        <div className={`stats-tagline ${step >= 7 ? "visible" : ""}`}>
          Your inbox used to be a bottleneck. Now it's a pipeline.
        </div>
      </div>
    </div>
  );
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}

function ClockIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}
