import type { PredictState, Step, Task } from "../api";
import HintLadder from "./HintLadder";
import LessonMarkdown from "./LessonMarkdown";

export const NO_PREDICT: PredictState = { wrong: [], solved: false, answer: null, explain: null };

const TYPE_LABEL: Record<Step["type"], string> = {
  story: "Story",
  concept: "Concept",
  example: "Example",
  predict: "Predict",
  try: "Try it",
  task: "Your task",
  incident: "Incident",
  recap: "Recap",
  "deep-dive": "Go deeper",
};

interface Props {
  step: Step;
  task: Task | undefined;
  hints: string[];
  hintBusy: boolean;
  predict: PredictState;
  predictBusy: boolean;
  checking: boolean;
  chapterDone: boolean;
  tasksLeft: number;
  hasNextChapter: boolean;
  onPredict: (option: number) => void;
  onHint: (taskId: string) => void;
  onRun: (command: string) => void;
  onCheck: () => void;
  onNextChapter: () => void;
}

export default function StepCard(p: Props) {
  const { step } = p;
  const body = <LessonMarkdown markdown={step.markdown} onRun={p.onRun} />;
  const title = step.title ?? (step.type === "recap" ? "Chapter recap" : null);

  return (
    <article className={`step-card step-${step.type}`} aria-labelledby="step-title">
      <div className="step-kind">{TYPE_LABEL[step.type]}</div>
      {title && <h2 id="step-title">{title}</h2>}

      {step.type === "deep-dive" ? (
        <details className="deep-dive">
          <summary>Go deeper {step.minutes ? `(${step.minutes} min)` : ""}</summary>
          {body}
        </details>
      ) : step.type === "incident" ? (
        <div className="incident" role="alert">
          <div className="incident-head">🚨 Incident</div>
          {body}
        </div>
      ) : (
        body
      )}

      {step.predict && <PredictBox step={step} state={p.predict} busy={p.predictBusy} onPick={p.onPredict} onRun={p.onRun} />}

      {(step.type === "task" || step.type === "incident") && p.task && (
        <TaskBox task={p.task} hints={p.hints} hintBusy={p.hintBusy} checking={p.checking} onHint={p.onHint} onCheck={p.onCheck} />
      )}

      {step.type === "recap" && (
        <div className="recap-status">
          {p.chapterDone ? (
            <p className="pass"><strong>Chapter complete. Every task passes. 🎉</strong></p>
          ) : (
            <p className="muted">{p.tasksLeft === 1 ? "1 task still needs" : `${p.tasksLeft} tasks still need`} to pass before this chapter is complete.</p>
          )}
          {p.hasNextChapter && (
            <button className="btn btn-primary" onClick={p.onNextChapter}>Next chapter →</button>
          )}
        </div>
      )}
    </article>
  );
}

interface PredictBoxProps {
  step: Step;
  state: PredictState;
  busy: boolean;
  onPick: (i: number) => void;
  onRun: (c: string) => void;
}

function PredictBox({ step, state, busy, onPick, onRun }: PredictBoxProps) {
  const pr = step.predict!;
  const done = state.solved;
  return (
    <div className="predict">
      <div className="predict-question" id="predict-q">
        <LessonMarkdown markdown={pr.question} onRun={onRun} />
      </div>
      <div className="predict-options" role="group" aria-labelledby="predict-q">
        {pr.options.map((o, i) => {
          const wrong = state.wrong.includes(i);
          const right = done && i === state.answer;
          return (
            <button
              key={i}
              className={`predict-option ${wrong ? "is-wrong" : ""} ${right ? "is-right" : ""}`}
              onClick={() => onPick(i)}
              disabled={done || wrong || busy}
              aria-pressed={wrong || right}
            >
              <span className="predict-mark" aria-hidden="true">{right ? "✓" : wrong ? "✗" : String.fromCharCode(65 + i)}</span>
              <LessonMarkdown markdown={o.text} inline />
            </button>
          );
        })}
      </div>
      <div aria-live="polite">
        {!done && state.wrong.length > 0 && <p className="fail">Not quite. Have another go.</p>}
        {done && (
          <div className="predict-explain">
            <p className="pass"><strong>{state.wrong.length === 0 ? "Right first time!" : "That's it."}</strong></p>
            {state.explain && <LessonMarkdown markdown={state.explain} onRun={onRun} />}
          </div>
        )}
      </div>
    </div>
  );
}

function TaskBox(p: { task: Task; hints: string[]; hintBusy: boolean; checking: boolean; onHint: (id: string) => void; onCheck: () => void }) {
  const { task } = p;
  return (
    <div className={`task-box ${task.passed ? "task-done" : ""}`}>
      <div className="task-box-head">
        <span className={`task-icon ${task.passed ? "pass" : task.passed === false ? "fail" : "none"}`} aria-hidden="true">
          {task.passed ? "✓" : task.passed === false ? "✗" : "○"}
        </span>
        <strong>{task.title}</strong>
        <span className="spacer" />
        <span className="xp-chip" title="Each hint you reveal lowers the XP for this task">{task.xp} XP</span>
      </div>
      <p className="muted small-text">
        {task.passed ? "Passed. Nice work." : "Edit your files, then press Check to run the hidden tests on a clean machine."}
      </p>
      <HintLadder task={task} hints={p.hints} busy={p.hintBusy} onReveal={() => p.onHint(task.id)} />
      {!task.passed && (
        <button className="btn btn-primary" onClick={p.onCheck} disabled={p.checking}>
          {p.checking ? <><span className="spinner" /> Checking...</> : "Check"}
        </button>
      )}
    </div>
  );
}
