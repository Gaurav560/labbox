import type { Step } from "../api";
import { DOT_LABEL } from "./LessonPanel";

/** Read mode: the chapter's steps by name, down the left (owner, 25 November); the × closes it. */
export default function StepOutline({ steps, current, visited, onGo, onClose }: { steps: Step[]; current: number; visited: number; onGo: (i: number) => void; onClose: () => void }) {
  return (
    <nav className="step-outline" aria-label="Steps in this chapter">
      <div className="step-outline-top">
        <p className="step-outline-head">Step {current + 1} of {steps.length}</p>
        <button className="step-outline-close" onClick={onClose} aria-label="Close the list of steps" title="Close the list of steps">×</button>
      </div>
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
