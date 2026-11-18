import type { Task } from "../api";

const RUNGS = ["Nudge", "Direction", "Almost there"];

interface Props {
  task: Task;
  hints: string[]; // revealed so far
  busy: boolean;
  onReveal: () => void;
}

export default function HintLadder({ task, hints, busy, onReveal }: Props) {
  if (task.hint_count === 0) return null;
  const left = task.hint_count - hints.length;
  return (
    <div className="hints">
      {hints.length > 0 && (
        <ol className="hint-list">
          {hints.map((h, i) => (
            <li key={i}>
              <span className="hint-rung">{RUNGS[i] ?? `Hint ${i + 1}`}</span>
              {h}
            </li>
          ))}
        </ol>
      )}
      {left > 0 && (
        <button className="btn btn-ghost btn-small" onClick={onReveal} disabled={busy}>
          💡 Hint ({left} left)
        </button>
      )}
    </div>
  );
}
