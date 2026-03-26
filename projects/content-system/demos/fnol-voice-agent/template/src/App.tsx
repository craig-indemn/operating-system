import { useEffect, useState, useRef, useCallback } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useRoomContext,
  useConnectionState,
} from "@livekit/components-react";
import {
  RoomEvent,
  ConnectionState,
  type TranscriptionSegment,
  type Participant,
} from "livekit-client";
import EgressHelper from "@livekit/egress-sdk";
import "./styles.css";

interface TranscriptEntry {
  id: string;
  speaker: "agent" | "caller";
  text: string;
  timestamp: number;
  final: boolean;
}

function getConnectionParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    url: params.get("url") || EgressHelper.getLiveKitURL(),
    token: params.get("token") || EgressHelper.getAccessToken(),
    layout: params.get("layout") || "default",
  };
}

export default function App() {
  const { url, token } = getConnectionParams();
  const [started, setStarted] = useState(false);

  if (!url || !token) {
    return (
      <div className="app loading">
        <p>Waiting for connection parameters...</p>
      </div>
    );
  }

  // Show the full branded layout with a start button overlay
  // This lets you set up screen recording first, then click to begin
  if (!started) {
    return (
      <div className="app">
        <div className="brand-bar">
          <img src="/brand/logo-iris.svg" alt="indemn" className="brand-logo" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
        </div>

        <div className="main-layout">
          <div className="phone-panel">
            <div className="phone-frame">
              <div className="carrier-name">Acme Insurance</div>
              <div className="carrier-subtitle">Claims Line</div>
              <div className="agent-avatar">
                <img src="/maya-avatar.png" alt="Maya" className="avatar-image" />
              </div>
              <div className="agent-name">Maya</div>
              <div className="agent-role">Claims Associate</div>
              <div className="call-status">
                <span className="status-ready">Ready</span>
              </div>
              <div className="call-timer">00:00</div>
              <div className="waveform">
                <canvas width={280} height={60} />
              </div>
            </div>
          </div>

          <div className="transcript-panel">
            <div className="transcript-header">
              <span className="transcript-title">Live Transcript</span>
            </div>
            <div className="transcript-body">
              <div className="start-overlay">
                <button className="start-button" onClick={() => setStarted(true)}>
                  Start Call
                </button>
                <p className="start-hint">Set up screen recording first, then click to begin</p>
              </div>
            </div>
          </div>
        </div>

        <div className="caption-bar">
          <div className="caption-label">CC</div>
          <div className="caption-content idle">
            <span className="caption-text-idle">Live captions</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <LiveKitRoom
      serverUrl={url}
      token={token}
      connect={true}
      audio={true}
      options={{ audioCaptureDefaults: { autoGainControl: true, noiseSuppression: true } }}
    >
      <RoomAudioRenderer />
      <RecordingTemplate />
    </LiveKitRoom>
  );
}

function RecordingTemplate() {
  const room = useRoomContext();
  const connectionState = useConnectionState();
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [currentCaption, setCurrentCaption] = useState<{
    speaker: string;
    text: string;
  } | null>(null);
  const [callStartTime, setCallStartTime] = useState<number | null>(null);
  const [elapsed, setElapsed] = useState("00:00");
  const [isActive, setIsActive] = useState(false);
  const transcriptRef = useRef<HTMLDivElement>(null);
  const captionTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  // Register with egress helper
  useEffect(() => {
    if (room) {
      EgressHelper.setRoom(room);
    }
  }, [room]);

  // Start recording when connected
  useEffect(() => {
    if (connectionState === ConnectionState.Connected) {
      EgressHelper.startRecording();
    }
  }, [connectionState]);

  // Call timer
  useEffect(() => {
    if (!callStartTime) return;
    const interval = setInterval(() => {
      const diff = Math.floor((Date.now() - callStartTime) / 1000);
      const mins = String(Math.floor(diff / 60)).padStart(2, "0");
      const secs = String(diff % 60).padStart(2, "0");
      setElapsed(`${mins}:${secs}`);
    }, 200);
    return () => clearInterval(interval);
  }, [callStartTime]);

  // Handle transcription events
  const handleTranscription = useCallback(
    (
      segments: TranscriptionSegment[],
      participant?: Participant
    ) => {
      if (!callStartTime) {
        setCallStartTime(Date.now());
        setIsActive(true);
      }

      const isAgent = participant?.identity?.startsWith("agent") ?? false;
      const speaker = isAgent ? "agent" : "caller";
      const speakerName = isAgent ? "Maya" : "Mike";

      for (const segment of segments) {
        // Update caption bar
        setCurrentCaption({ speaker: speakerName, text: segment.text });
        if (captionTimeoutRef.current) {
          clearTimeout(captionTimeoutRef.current);
        }
        captionTimeoutRef.current = setTimeout(
          () => setCurrentCaption(null),
          3000
        );

        // Update transcript
        setTranscript((prev) => {
          const existing = prev.findIndex((e) => e.id === segment.id);
          if (existing >= 0) {
            const updated = [...prev];
            updated[existing] = {
              ...updated[existing],
              text: segment.text,
              final: segment.final,
            };
            return updated;
          }
          return [
            ...prev,
            {
              id: segment.id,
              speaker,
              text: segment.text,
              timestamp: Date.now(),
              final: segment.final,
            },
          ];
        });
      }
    },
    [callStartTime]
  );

  useEffect(() => {
    if (!room) return;
    room.on(RoomEvent.TranscriptionReceived, handleTranscription);
    return () => {
      room.off(RoomEvent.TranscriptionReceived, handleTranscription);
    };
  }, [room, handleTranscription]);

  // Auto-scroll transcript
  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight;
    }
  }, [transcript]);

  return (
    <div className="app">
      <div className="brand-bar">
        <img src="/brand/logo-iris.svg" alt="indemn" className="brand-logo" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
      </div>

      <div className="main-layout">
        {/* Left: Phone UI — shows Maya (the agent you're talking to) */}
        <div className="phone-panel">
          <div className="phone-frame">
            <div className="carrier-name">Acme Insurance</div>
            <div className="carrier-subtitle">Claims Line</div>

            <div className="agent-avatar">
              <img
                src="/maya-avatar.png"
                alt="Maya"
                className="avatar-image"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                  (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
                }}
              />
              <div className="avatar-fallback hidden">M</div>
            </div>
            <div className="agent-name">Maya</div>
            <div className="agent-role">Claims Associate</div>
            <div className="call-status">
              {isActive ? (
                <span className="status-active">
                  <span className="pulse-dot" />
                  Active Call
                </span>
              ) : (
                <span className="status-connecting">Connecting...</span>
              )}
            </div>

            <div className="call-timer">{elapsed}</div>

            <AudioVisualizer isActive={isActive} />
          </div>
        </div>

        {/* Right: Transcript */}
        <div className="transcript-panel">
          <div className="transcript-header">
            <span className="transcript-title">Live Transcript</span>
            <span className="transcript-dot" />
          </div>
          <div className="transcript-body" ref={transcriptRef}>
            {transcript.length === 0 && (
              <div className="transcript-empty">
                Waiting for conversation...
              </div>
            )}
            {transcript
              .filter((e) => e.final || e.text.length > 3)
              .map((entry) => (
                <div
                  key={entry.id}
                  className={`transcript-entry ${entry.speaker} ${entry.final ? "final" : "interim"}`}
                >
                  <span className="speaker-label">
                    {entry.speaker === "agent" ? "Maya" : "Mike"}
                  </span>
                  <span className="entry-text">{entry.text}</span>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* Bottom: Caption bar — always visible */}
      <div className="caption-bar">
        <div className="caption-label">CC</div>
        {currentCaption ? (
          <div className="caption-content active">
            <span className="caption-speaker">{currentCaption.speaker}:</span>
            <span className="caption-text">{currentCaption.text}</span>
          </div>
        ) : (
          <div className="caption-content idle">
            <span className="caption-text-idle">Live captions</span>
          </div>
        )}
      </div>
    </div>
  );
}

function AudioVisualizer({
  isActive,
}: {
  isActive: boolean;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animFrameRef = useRef<number>();

  useEffect(() => {
    if (!isActive || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d")!;
    const barCount = 24;
    const bars = new Array(barCount).fill(0);

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < barCount; i++) {
        const target = Math.random() * 0.6 + 0.1;
        bars[i] += (target - bars[i]) * 0.15;

        const barWidth = (canvas.width / barCount) * 0.7;
        const gap = (canvas.width / barCount) * 0.3;
        const x = i * (barWidth + gap);
        const barHeight = bars[i] * canvas.height * 0.8;
        const y = (canvas.height - barHeight) / 2;

        ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, barHeight, 2);
        ctx.fill();
      }

      animFrameRef.current = requestAnimationFrame(draw);
    }

    draw();
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [isActive]);

  return (
    <div className="waveform">
      <canvas ref={canvasRef} width={280} height={60} />
    </div>
  );
}
