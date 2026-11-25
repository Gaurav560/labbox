import type { Step } from "../api";
import { DOT_LABEL } from "./LessonPanel";

/** A sidebar icon (a panel with its left column): the button that closes and reopens the list of steps. */
export function PanelIcon() {
  return (<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><rect x="3.5" y="4.5" width="17" height="15" rx="2.5" /><path d="M9.5 4.5v15" /><path d="M6 9h1M6 12h1" /></svg>);
}

/** Read mode: the chapter's steps by name, down the left (owner, 25 November); the panel button closes it. */
export default function StepOutline({ steps, current, visited, onGo, onClose }: { steps: Step[]; current: number; visited: number; onGo: (i: number) => void; onClose: () => void }) {
  return (
    <nav className="step-outline" aria-label="Scenes in this chapter">
      <div className="step-outline-top">
        <p className="step-outline-head">Scene {current + 1} of {steps.length}</p>
        <button className="panel-toggle" onClick={onClose} aria-label="Close the list of scenes" title="Close the list of scenes">
          <PanelIcon />
        </button>
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
