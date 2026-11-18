import type { Task } from "../api";

function icon(passed: boolean | null) {
  if (passed === true) return <span className="task-icon pass">✓</span>;
  if (passed === false) return <span className="task-icon fail">✗</span>;
  return <span className="task-icon none">○</span>;
}

export default function TaskList({ tasks }: { tasks: Task[] }) {
  return (
    <div className="tasks">
      <h4>Your tasks</h4>
      <ul>
        {tasks.map((t) => (
          <li key={t.id}>
            {icon(t.passed)}
            <span>{t.title}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
