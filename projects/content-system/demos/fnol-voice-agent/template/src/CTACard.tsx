/**
 * Act 4 — CTA End Card
 * "Making insurance a conversation" with channel icons and indemn.ai
 *
 * Access at: http://localhost:5555/?page=cta
 */
import { useEffect, useState } from "react";
import "./cta.css";

const channels = [
  { label: "Phone", icon: PhoneIcon },
  { label: "Web Voice", icon: MicIcon },
  { label: "Web Chat", icon: ChatIcon },
  { label: "Email", icon: EmailIcon },
  { label: "SMS", icon: SmsIcon },
];

export default function CTACard() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const timers = [
      setTimeout(() => setStep(1), 400),
      setTimeout(() => setStep(2), 800),
      setTimeout(() => setStep(3), 1000),
      setTimeout(() => setStep(4), 1200),
      setTimeout(() => setStep(5), 1400),
      setTimeout(() => setStep(6), 1600),
      setTimeout(() => setStep(7), 2200),
      setTimeout(() => setStep(8), 3000),
    ];
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="cta-page">
      <div className={`cta-logo ${step >= 1 ? "visible" : ""}`}>
        <img src="/brand/logo-white.svg" alt="indemn" />
      </div>

      <div className="cta-channels">
        {channels.map((ch, i) => (
          <div
            key={ch.label}
            className={`cta-channel ${step >= i + 2 ? "visible" : ""}`}
          >
            <div className="cta-channel-icon">
              <ch.icon />
            </div>
            <span className="cta-channel-label">{ch.label}</span>
          </div>
        ))}
      </div>

      <div className={`cta-tagline ${step >= 7 ? "visible" : ""}`}>
        Making insurance a conversation.
      </div>

      <div className={`cta-url ${step >= 8 ? "visible" : ""}`}>
        indemn.ai
      </div>
    </div>
  );
}

function PhoneIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/>
    </svg>
  );
}

function MicIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/>
      <path d="M19 10v2a7 7 0 01-14 0v-2"/>
      <line x1="12" y1="19" x2="12" y2="23"/>
      <line x1="8" y1="23" x2="16" y2="23"/>
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
    </svg>
  );
}

function EmailIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
      <polyline points="22,6 12,13 2,6"/>
    </svg>
  );
}

function SmsIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="5" y="2" width="14" height="20" rx="2" ry="2"/>
      <line x1="12" y1="18" x2="12.01" y2="18"/>
    </svg>
  );
}
