import type { Task } from "../api";

function icon(passed: boolean | null) {
  if (passed === true) return <span className="task-icon pass">✓</span>;
  if (passed === false) return <span className="task-icon fail">✗</span>;
  return <span className="task-icon none">○</span>;
}

const STATE = (passed: boolean | null) => (passed ? "passed" : passed === false ? "failing" : "not checked yet");

interface Props {
  tasks: Task[];
  activeId?: string | null;
  onSelect?: (taskId: string) => void; // jump to the task's step
}

export default function TaskList({ tasks, activeId, onSelect }: Props) {
  return (
    <div className="tasks">
      <h3 className="tasks-title">Tasks</h3>
      <ul>
        {tasks.map((t) => (
          <li key={t.id}>
            <button
              className={`task-chip ${t.id === activeId ? "task-chip-active" : ""}`}
              onClick={() => onSelect?.(t.id)}
              title={t.title}
              aria-label={`${t.id}: ${t.title}, ${STATE(t.passed)}`}
            >
              {t.id === activeId && !t.passed ? <span className="task-icon accent">▶</span> : icon(t.passed)}
              <span>{t.id}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
