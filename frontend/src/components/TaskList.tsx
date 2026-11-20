import type { Task } from "../api";

const STATE = (passed: boolean | null) => (passed ? "passed" : passed === false ? "failing" : "not checked yet");

interface Props {
  tasks: Task[];
  activeId?: string | null;
  onSelect?: (taskId: string) => void; // jump to the task's step
  ahead?: Record<string, number>; // tasks not reached yet: never shown as failing
}

/** The chapter's tasks as a quiet stepper: "Task 1 of 3", one dot per task, the current task's title. */
export default function TaskList({ tasks, activeId, onSelect, ahead = {} }: Props) {
  const failing = (t: Task) => t.passed === false && ahead[t.id] === undefined;
  const at = Math.max(0, tasks.findIndex((t) => t.id === activeId));
  const active = tasks[at];
  const done = tasks.filter((t) => t.passed).length;
  return (
    <div className="tasks">
      <div className="tasks-head">
        <span className="tasks-count">Task {at + 1} of {tasks.length}</span>
        <ol className="task-dots" aria-label="Tasks">
          {tasks.map((t) => (
            <li key={t.id}>
              <button
                className={`task-chip task-dot ${t.passed ? "is-pass" : failing(t) ? "is-fail" : ""} ${t === active ? "is-active" : ""}`}
                onClick={() => onSelect?.(t.id)}
                title={t.title}
                aria-current={t === active ? "step" : undefined}
              >
                <span className="sr-only">{t.title} ({t.id}), {failing(t) || t.passed ? STATE(t.passed) : STATE(null)}</span>
              </button>
            </li>
          ))}
        </ol>
        {done > 0 && <span className="tasks-done">{done === tasks.length ? "All done ✓" : `${done} done`}</span>}
      </div>
      {active && (
        <p className={`tasks-now ${active.passed ? "is-pass" : ""}`}>
          {active.passed && <span aria-hidden="true">✓ </span>}
          {active.title}
        </p>
      )}
    </div>
  );
}
