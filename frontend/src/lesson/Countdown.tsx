import { useEffect, useState } from "react";

function secondsLeft(minutes: number, startedAt?: string | null): number {
  const start = startedAt ? Date.parse(startedAt) : NaN;
  const elapsed = Number.isNaN(start) ? 0 : Math.floor((Date.now() - start) / 1000);
  return Math.max(0, minutes * 60 - elapsed);
}

// Cosmetic incident timer: it never blocks anything. Fixing the incident before it runs out
// gives bonus XP. It counts from when the chapter was first opened (startedAt), so a reload
// does not reset it.
export default function Countdown({ minutes, startedAt }: { minutes: number; startedAt?: string | null }) {
  const [left, setLeft] = useState(() => secondsLeft(minutes, startedAt));
  useEffect(() => {
    setLeft(secondsLeft(minutes, startedAt));
    const id = window.setInterval(() => setLeft(secondsLeft(minutes, startedAt)), 1000);
    return () => window.clearInterval(id);
  }, [minutes, startedAt]);
  const mm = String(Math.floor(left / 60)).padStart(2, "0");
  const ss = String(left % 60).padStart(2, "0");
  return (
    <span className={`countdown ${left === 0 ? "countdown-done" : ""}`} role="timer" aria-label={`${Math.ceil(left / 60)} minutes left`}>
      ⏱ {left === 0 ? "time is up, fix it anyway" : `${mm}:${ss}`}
    </span>
  );
}
