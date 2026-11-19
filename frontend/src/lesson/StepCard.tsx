import type { DesignAttempt, PredictState, Step, Task } from "../api";
import { useStats } from "../stats";
import ChoiceQuestion from "./ChoiceQuestion";
import Countdown from "./Countdown";
import HintLadder from "./HintLadder";
import LessonMarkdown from "./LessonMarkdown";
import TutorBox from "./TutorBox";
import DesignStep from "./DesignStep";

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
  design: "Design review",
};

interface Props {
  labId: string;
  chapterId: string;
  stepIndex: number;
  design: DesignAttempt | undefined;
  onDesignGraded: (attempt: DesignAttempt) => void;
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
  chapterXp: number;
  startedAt: string | null; // when the chapter was first opened; incident timers count from here
  checkMode: "fresh" | "live";
  onPredict: (option: number) => void;
  onHint: (taskId: string) => void;
  onRun: (command: string) => void;
  onCheck: () => void;
  onNextChapter: () => void;
}

export default function StepCard(p: Props) {
  const { step } = p;
  const { stats } = useStats();
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
          <div className="incident-head">
            <span>🚨 Incident</span>
            {step.minutes ? <Countdown minutes={step.minutes} startedAt={p.startedAt} /> : null}
          </div>
          {body}
          {step.minutes ? <p className="muted small-text">Fix it before the timer runs out for +25 bonus XP.</p> : null}
        </div>
      ) : (
        body
      )}

      {step.predict && (
        <ChoiceQuestion
          question={step.predict.question}
          options={step.predict.options.map((o) => o.text)}
          state={p.predict}
          busy={p.predictBusy}
          onPick={p.onPredict}
          onRun={p.onRun}
        />
      )}

      {step.type === "design" && step.questions && (
        <DesignStep
          key={`${p.chapterId}/${p.stepIndex}`}
          labId={p.labId}
          chapterId={p.chapterId}
          stepIndex={p.stepIndex}
          questions={step.questions}
          attempt={p.design}
          onGraded={p.onDesignGraded}
        />
      )}

      {(step.type === "task" || step.type === "incident") && p.task && (
        <TaskBox labId={p.labId} chapterId={p.chapterId} task={p.task} hints={p.hints} hintBusy={p.hintBusy} checking={p.checking} live={p.checkMode === "live"} onHint={p.onHint} onCheck={p.onCheck} />
      )}

      {step.type === "recap" && (
        <div className="recap-status">
          <div className="recap-stats">
            <div><span className="big-number">⭐ {p.chapterXp}</span><span className="muted small-text">XP from this chapter</span></div>
            {stats && <div><span className="big-number">🔥 {stats.streak_current}</span><span className="muted small-text">day streak</span></div>}
            {stats && <div><span className="big-number">Lv {stats.level}</span><span className="muted small-text">{stats.next_level_xp - stats.xp_total} XP to the next level</span></div>}
          </div>
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

function TaskBox(p: { labId: string; chapterId: string; task: Task; hints: string[]; hintBusy: boolean; checking: boolean; live: boolean; onHint: (id: string) => void; onCheck: () => void }) {
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
        {task.passed
          ? "Passed. Nice work."
          : p.live
            ? "Fix the running system, then press Check: a checker inspects it live."
            : "Edit your files, then press Check to run the hidden tests on a clean machine."}
      </p>
      <HintLadder task={task} hints={p.hints} busy={p.hintBusy} onReveal={() => p.onHint(task.id)} />
      {!task.passed && (
        <button className="btn btn-primary" onClick={p.onCheck} disabled={p.checking}>
          {p.checking ? <><span className="spinner" /> Checking...</> : "Check"}
        </button>
      )}
      <TutorBox key={`${p.labId}/${task.id}/${task.passed}`} labId={p.labId} chapterId={p.chapterId} task={task} />
    </div>
  );
}
