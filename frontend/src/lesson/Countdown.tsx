import { useEffect, useState } from "react";

// Cosmetic incident timer: it never blocks anything, it only adds a little urgency.
export default function Countdown({ minutes }: { minutes: number }) {
  const [left, setLeft] = useState(minutes * 60);
  useEffect(() => {
    const id = window.setInterval(() => setLeft((s) => Math.max(0, s - 1)), 1000);
    return () => window.clearInterval(id);
  }, []);
  const mm = String(Math.floor(left / 60)).padStart(2, "0");
  const ss = String(left % 60).padStart(2, "0");
  return (
    <span className={`countdown ${left === 0 ? "countdown-done" : ""}`} role="timer" aria-label={`${Math.ceil(left / 60)} minutes left`}>
      ⏱ {mm}:{ss}
    </span>
  );
}
