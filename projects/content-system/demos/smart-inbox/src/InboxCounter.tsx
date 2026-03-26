/**
 * Act 1 — Inbox Counter
 * 5s animation: inbox filling up, badge ticking 0 → 8 → 14 → 23
 * Text overlay: "Monday. 8:00 AM. 23 submissions arrived overnight."
 *
 * Access at: http://localhost:5180/?page=inbox
 */
import { useEffect, useState } from "react";
import "./inbox.css";

const avatarColors = [
  "#4752a3", "#a67cb7", "#3b82f6", "#22c55e", "#f59e0b",
  "#6366f1", "#ec4899", "#14b8a6", "#8b5cf6", "#ef4444",
  "#0ea5e9", "#f97316",
];

const emails = [
  // Batch 1 (0→8)
  { sender: "Jessica Parker", email: "jessica.parker@worthington-insurance.com", subject: "New Submission — Riverside Landscaping LLC", time: "7:58 AM", hasAttachment: true },
  { sender: "Mark Chen", email: "mark.chen@brokerfirst.com", subject: "Quote Ready: Apex Manufacturing — GL & WC", time: "7:52 AM", hasAttachment: true },
  { sender: "Sarah Wells", email: "sarah.wells@insurepoint.com", subject: "Follow-Up: Missing Loss Runs — Pacific Dental", time: "7:45 AM", hasAttachment: false },
  { sender: "David Kim", email: "david.kim@peakrisk.com", subject: "New Submission — Summit Electric LLC", time: "7:38 AM", hasAttachment: true },
  { sender: "Lisa Torres", email: "lisa.torres@bridgeins.com", subject: "Renewal Notice — AutoFleet Transport (exp. 4/15)", time: "7:31 AM", hasAttachment: false },
  { sender: "Ryan O'Brien", email: "ryan.obrien@coastalbrokers.com", subject: "New Submission — Harbor View Restaurant Group", time: "7:24 AM", hasAttachment: true },
  { sender: "Amanda Foster", email: "amanda.foster@noreply.com", subject: "Re: Out of Office — Back April 1", time: "7:18 AM", hasAttachment: false },
  { sender: "Tom Bradley", email: "tom.bradley@meridiangroup.com", subject: "Quote Ready: Greenfield Construction — Builders Risk", time: "7:12 AM", hasAttachment: true },
  // Batch 2 (8→14)
  { sender: "Michelle Huang", email: "michelle.huang@allstarins.com", subject: "Follow-Up: Subcontractor Certificates — Metro Plumbing", time: "6:55 AM", hasAttachment: false },
  { sender: "James Wilson", email: "james.wilson@keystoneuw.com", subject: "New Submission — Bright Horizons Daycare", time: "6:48 AM", hasAttachment: true },
  { sender: "Karen Mitchell", email: "karen.mitchell@tridentbrokers.com", subject: "Follow-Up: Application Incomplete — Westside Auto", time: "6:41 AM", hasAttachment: false },
  { sender: "Daniel Ruiz", email: "daniel.ruiz@premiumbind.com", subject: "Quote Ready: Mountain View Medical — Professional Liability", time: "6:33 AM", hasAttachment: true },
  { sender: "Chris Nakamura", email: "chris.nakamura@relianceuw.com", subject: "Renewal Notice — WC Policy #GR-4419 (exp. 4/22)", time: "6:26 AM", hasAttachment: false },
  { sender: "Emily Grasso", email: "emily.grasso@concordins.com", subject: "New Submission — Pinnacle Roofing & Solar", time: "6:19 AM", hasAttachment: true },
  // Batch 3 (14→23)
  { sender: "Andrew Park", email: "andrew.park@vanguardbrokers.com", subject: "Follow-Up: Loss Runs Still Outstanding — Cedar Creek", time: "5:58 AM", hasAttachment: false },
  { sender: "Jennifer Adams", email: "jennifer.adams@shielduw.com", subject: "New Submission — Crossroads Trucking LLC", time: "5:49 AM", hasAttachment: true },
  { sender: "Robert Tran", email: "robert.tran@apexbrokers.com", subject: "Quote Ready: Valley Tech Solutions — Cyber Liability", time: "5:41 AM", hasAttachment: true },
  { sender: "Samantha Cole", email: "samantha.cole@trustins.com", subject: "Follow-Up: Prior Carrier Info — Bright Star Electric", time: "5:32 AM", hasAttachment: false },
  { sender: "Brian Murphy", email: "brian.murphy@noreply.com", subject: "Newsletter: Weekly Insurance Market Digest", time: "5:24 AM", hasAttachment: false },
  { sender: "Nicole Evans", email: "nicole.evans@primebind.com", subject: "New Submission — Golden Gate Landscaping", time: "5:15 AM", hasAttachment: true },
  { sender: "Kevin Patel", email: "kevin.patel@solidrockuw.com", subject: "Renewal Notice — GL Policy #PR-7802 (exp. 5/1)", time: "5:08 AM", hasAttachment: false },
  { sender: "Rachel Kim", email: "rachel.kim@clearviewins.com", subject: "New Submission — Cascade Plumbing & HVAC", time: "4:55 AM", hasAttachment: true },
  { sender: "Michael Byrne", email: "michael.byrne@sterlingsur.com", subject: "Follow-Up: Additional Insured Endorsement — Atlas Logistics", time: "4:42 AM", hasAttachment: false },
];

export default function InboxCounter() {
  const [visibleCount, setVisibleCount] = useState(0);
  const [showOverlay, setShowOverlay] = useState(false);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];

    // Batch 1: emails 1-8 (staggered over 0.3s-1.3s)
    for (let i = 0; i < 8; i++) {
      timers.push(setTimeout(() => setVisibleCount(i + 1), 300 + i * 120));
    }

    // Batch 2: emails 9-14 (staggered over 1.5s-2.5s)
    for (let i = 8; i < 14; i++) {
      timers.push(setTimeout(() => setVisibleCount(i + 1), 1500 + (i - 8) * 100));
    }

    // Batch 3: emails 15-23 (staggered over 2.8s-3.8s — faster, overwhelming)
    for (let i = 14; i < 23; i++) {
      timers.push(setTimeout(() => setVisibleCount(i + 1), 2800 + (i - 14) * 80));
    }

    // Overlay text
    timers.push(setTimeout(() => setShowOverlay(true), 3800));

    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="inbox-page">
      <div className="inbox-sidebar">
        <div className="inbox-sidebar-logo">
          <img src="/brand/logo-iris.svg" alt="indemn" />
        </div>

        <div className="inbox-folder active">
          <InboxIcon />
          Inbox
          {visibleCount > 0 && (
            <span className="inbox-badge" key={visibleCount}>
              {visibleCount}
            </span>
          )}
        </div>
        <div className="inbox-folder">
          <SendIcon />
          Sent
        </div>
        <div className="inbox-folder">
          <DraftIcon />
          Drafts
        </div>
        <div className="inbox-folder">
          <ArchiveIcon />
          Archive
        </div>
        <div className="inbox-folder">
          <StarIcon />
          Starred
        </div>
      </div>

      <div className="inbox-main">
        <div className="inbox-toolbar">
          <span className="inbox-toolbar-title">Inbox</span>
          <span className="inbox-toolbar-subtitle">
            {visibleCount > 0 ? `${visibleCount} unread` : "No new messages"}
          </span>
        </div>
        <div className="inbox-list">
          {emails.map((email, i) => {
            const colorIdx = i % avatarColors.length;
            const initials = email.sender
              .split(" ")
              .map((n) => n[0])
              .join("");
            return (
              <div
                key={i}
                className={`inbox-row unread ${i < visibleCount ? "visible" : ""}`}
              >
                <div className="inbox-row-dot" />
                <div
                  className="inbox-row-avatar"
                  style={{ background: avatarColors[colorIdx] }}
                >
                  {initials}
                </div>
                <div className="inbox-row-content">
                  <div className="inbox-row-sender">{email.email}</div>
                  <div className="inbox-row-subject">{email.subject}</div>
                </div>
                <div className="inbox-row-meta">
                  {email.hasAttachment && (
                    <span className="inbox-row-attachment">
                      <AttachmentIcon />
                    </span>
                  )}
                  <span className="inbox-row-time">{email.time}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className={`inbox-overlay ${showOverlay ? "visible" : ""}`}>
        <span className="inbox-overlay-text">
          Monday. 8:00 AM. 23 submissions arrived overnight.
        </span>
      </div>
    </div>
  );
}

/* Icons */

function InboxIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 16 12 14 15 10 15 8 12 2 12" />
      <path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z" />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}

function DraftIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  );
}

function ArchiveIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="21 8 21 21 3 21 3 8" />
      <rect x="1" y="3" width="22" height="5" />
      <line x1="10" y1="12" x2="14" y2="12" />
    </svg>
  );
}

function StarIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </svg>
  );
}

function AttachmentIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
    </svg>
  );
}
