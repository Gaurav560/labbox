import type { Step } from "../api";
import { DOT_LABEL } from "./LessonPanel";

/** Read mode on a wide screen: the chapter's steps by name, down the left (the step squares, with words). */
export default function StepOutline({ steps, current, visited, onGo }: { steps: Step[]; current: number; visited: number; onGo: (i: number) => void }) {
  return (
    <nav className="step-outline" aria-label="Steps in this chapter">
      <p className="step-outline-head">Step {current + 1} of {steps.length}</p>
      <ol>
        {steps.map((s, i) => (
          <li key={i}>
            <button
              className={`step-outline-item${i === current ? " is-current" : i <= visited ? " is-seen" : ""}`}
              onClick={() => onGo(i)}
              aria-current={i === current ? "step" : undefined}
            >
              <span className={`step-outline-mark dot-${s.type}`} aria-hidden="true" />
              <span className="step-outline-text">
                {(s.type === "task" || s.type === "incident" || s.type === "predict") && <span className="step-outline-kind">{DOT_LABEL[s.type]}</span>}
                {s.title ?? DOT_LABEL[s.type]}
              </span>
            </button>
          </li>
        ))}
      </ol>
    </nav>
  );
}
