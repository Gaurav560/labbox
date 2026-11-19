import { useEffect, useRef } from "react";
import type { Step } from "../api";

interface Props {
  steps: Step[];
  current: number;
  visited: number; // furthest step seen, for dot colours
  onGo: (index: number) => void;
  children: React.ReactNode; // the current step card
}

const DOT_LABEL: Record<Step["type"], string> = {
  story: "Story",
  concept: "Concept",
  example: "Example",
  predict: "Predict",
  try: "Try it",
  task: "Task",
  incident: "Incident",
  recap: "Recap",
  "deep-dive": "Go deeper",
  design: "Design review",
};

export default function LessonPanel({ steps, current, visited, onGo, children }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const count = steps.length;

  // Each step starts at its top.
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0 });
  }, [current]);

  return (
    <section className="lesson" aria-label="Lesson">
      {count > 1 && (
        <nav className="step-nav" aria-label="Steps">
          <ol className="step-dots">
            {steps.map((s, i) => (
              <li key={i}>
                <button
                  className={`dot ${i === current ? "dot-current" : i <= visited ? "dot-seen" : ""} dot-${s.type}`}
                  onClick={() => onGo(i)}
                  aria-label={`Step ${i + 1}: ${s.title ?? DOT_LABEL[s.type]}`}
                  aria-current={i === current ? "step" : undefined}
                />
              </li>
            ))}
          </ol>
          <span className="step-count">Step {current + 1} of {count}</span>
        </nav>
      )}
      <div className="lesson-scroll" ref={scrollRef}>
        <div className="step-anim" key={current}>
          {children}
        </div>
      </div>
      {count > 1 && (
        <div className="step-buttons">
          <button className="btn" onClick={() => onGo(current - 1)} disabled={current === 0}>
            ← Back
          </button>
          <span className="spacer" />
          <span className="muted kbd-hint" aria-hidden="true">← → keys</span>
          <button className="btn btn-primary" onClick={() => onGo(current + 1)} disabled={current >= count - 1}>
            Continue →
          </button>
        </div>
      )}
    </section>
  );
}
