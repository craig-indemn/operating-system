/**
 * Act 3 — Dashboard Reveal
 * Shows what happened behind the scenes after the FNOL call.
 * Elements animate in sequentially when the page loads.
 *
 * Access at: http://localhost:5555/?page=dashboard
 */
import { useEffect, useState } from "react";
import "./dashboard.css";

export default function DashboardReveal() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const timers = [
      setTimeout(() => setStep(1), 500),
      setTimeout(() => setStep(2), 1500),
      setTimeout(() => setStep(3), 2500),
      setTimeout(() => setStep(4), 3200),
      setTimeout(() => setStep(5), 3900),
      setTimeout(() => setStep(6), 4600),
      setTimeout(() => setStep(7), 5300),
      setTimeout(() => setStep(8), 6000),
      setTimeout(() => setStep(9), 6700),
      setTimeout(() => setStep(10), 7400),
      setTimeout(() => setStep(11), 9000),
    ];
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="dashboard">
      <div className="brand-bar">
        <img src="/brand/logo-iris.svg" alt="indemn" className="brand-logo" />
      </div>

      <div className="dashboard-layout">
        {/* Left column: Claim + Adjuster */}
        <div className="dashboard-left">
          <div className={`card claim-card ${step >= 1 ? "visible" : ""}`}>
            <div className="card-header">
              <div className="card-header-left">
                <img src="/maya-avatar.png" alt="Maya" className="card-avatar" />
                <div>
                  <span className="card-title">Claim Created</span>
                  <span className="card-subtitle">Handled by Maya</span>
                </div>
              </div>
              <span className="claim-badge">CLM-2026-04281</span>
            </div>
            <div className="card-body">
              <div className="field-grid">
                <Field label="Status" value="Open — Pending Review" />
                <Field label="Policyholder" value="Mike Reynolds" />
                <Field label="Policy" value="ACM-2023-7841" />
                <Field label="Vehicle" value="2023 Honda Accord" />
                <Field label="Date of Loss" value="Mar 28, 2026 — 2:47 PM" />
                <Field label="Location" value="Kroger, 1450 Main St" />
                <Field label="Type" value="Auto Collision (Not at Fault)" />
                <Field label="Damage" value="Rear bumper, taillight" />
                <Field label="Other Party" value="Tom Davis — Progressive" />
              </div>
            </div>
          </div>

          <div className={`card adjuster-card ${step >= 2 ? "visible" : ""}`}>
            <div className="card-header">
              <span className="card-title">Adjuster Assigned</span>
              <span className="auto-badge">Auto-assigned</span>
            </div>
            <div className="card-body">
              <div className="adjuster-info">
                <div className="adjuster-avatar">SM</div>
                <div>
                  <div className="adjuster-name">Sarah Martinez</div>
                  <div className="adjuster-detail">Location + availability match</div>
                  <div className="adjuster-detail">Contact within 24 hours</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right column: Activity Timeline */}
        <div className="dashboard-right">
          <div className={`card timeline-card ${step >= 3 ? "visible" : ""}`}>
            <div className="card-header">
              <span className="card-title">Activity Timeline</span>
            </div>
            <div className="card-body">
              <div className="timeline">
                <TimelineItem step={3} currentStep={step} time="2:47 PM" text="Call received from Mike Reynolds" status="complete" />
                <TimelineItem step={4} currentStep={step} time="2:47 PM" text="Identity verified, policy ACM-2023-7841 matched" status="complete" />
                <TimelineItem step={5} currentStep={step} time="2:48 PM" text="FNOL intake completed — all required fields captured" status="complete" />
                <TimelineItem step={6} currentStep={step} time="2:49 PM" text="Claim CLM-2026-04281 created" status="complete" />
                <TimelineItem step={7} currentStep={step} time="2:49 PM" text="Adjuster Sarah Martinez auto-assigned" status="complete" />
                <TimelineItem step={8} currentStep={step} time="2:49 PM" text="Photo upload link sent via SMS to (555) 867-5309" status="complete" />
                <TimelineItem step={9} currentStep={step} time="2:49 PM" text="Manager notification sent — new claim flagged" status="complete" />
                <TimelineItem step={10} currentStep={step} time="2:49 PM" text="FNOL report filed to carrier system" status="complete" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats overlay */}
      <div className={`stats-overlay ${step >= 11 ? "visible" : ""}`}>
        <div className="stats-text">
          2 minutes. Zero hold time. Zero data entry. Claim resolved before he left the parking lot.
        </div>
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="field">
      <span className="field-label">{label}</span>
      <span className="field-value">{value}</span>
    </div>
  );
}

function TimelineItem({
  step,
  currentStep,
  time,
  text,
  status,
}: {
  step: number;
  currentStep: number;
  time: string;
  text: string;
  status: "complete" | "pending";
}) {
  return (
    <div className={`timeline-item ${currentStep >= step ? "visible" : ""}`}>
      <div className={`timeline-dot ${status}`}>
        {status === "complete" && (
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M2 6L5 9L10 3" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        )}
      </div>
      <div className="timeline-content">
        <span className="timeline-time">{time}</span>
        <span className="timeline-text">{text}</span>
      </div>
    </div>
  );
}
