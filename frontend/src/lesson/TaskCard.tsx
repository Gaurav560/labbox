import type { TaskExample } from "../api";

/*
 * The task card: what the learner is building, drawn the same way for every task. Each example is
 * a call and what it should give back, from the task's `examples` in lab.yaml.
 */
export default function TaskCard({ examples }: { examples: TaskExample[] }) {
  if (!examples.length) return null;
  return (
    <figure className="task-card" aria-label="What your code should do">
      <div className="task-card-label">What your code should do</div>
      <ul>
        {examples.map((e, i) => (
          <li key={i}>
            <code className="tc-call">{e.call}</code>
            <span className="tc-arrow" aria-label="gives">→</span>
            <code className="tc-gives">{e.gives}</code>
            {e.note && <span className="tc-note">{e.note}</span>}
          </li>
        ))}
      </ul>
    </figure>
  );
}
