import { useState } from "react";
import { api, ApiError, type Task, type TutorReply } from "../api";

// The AI tutor under a task: "Ask the tutor" once a check has failed, "Review my code" once it passes.
// Both use the learner's daily AI budget; the tutor nudges and asks, it never hands over the solution.
export default function TutorBox({ labId, chapterId, task }: { labId: string; chapterId: string; task: Task }) {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [answer, setAnswer] = useState<TutorReply | null>(null);
  const [error, setError] = useState<string | null>(null);
  const review = task.passed === true;
  if (task.passed === null) return null; // nothing to talk about before the first check

  const run = async () => {
    setBusy(true);
    setError(null);
    try {
      setAnswer(review ? await api.review(labId, chapterId, task.id) : await api.tutor(labId, chapterId, task.id, question));
      setQuestion("");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "The tutor is not available right now.");
    } finally {
      setBusy(false);
    }
  };

  if (!open) {
    return (
      <button className="btn btn-small btn-ghost tutor-open" onClick={() => { setOpen(true); if (review) void run(); }}>
        {review ? "✦ Review my code" : "✦ Ask the tutor"}
      </button>
    );
  }
  return (
    <div className="tutor" aria-live="polite">
      <div className="tutor-head">
        <strong>{review ? "Code review" : "Tutor"}</strong>
        <span className="muted small-text">{review ? "Like a senior engineer's PR review. No XP either way." : "Nudges and questions, never the answer."}</span>
        <span className="spacer" />
        <button className="btn btn-small btn-ghost" onClick={() => setOpen(false)} aria-label="Close the tutor">✕</button>
      </div>
      {answer && (
        <div className={`tutor-reply ${answer.blocked ? "tutor-blocked" : ""}`}>
          {answer.reply}
          <div className="muted small-text tutor-meta">AI tokens used today: {answer.tokens_used_today.toLocaleString()}</div>
        </div>
      )}
      {busy && !answer && <div className="tutor-reply muted"><span className="spinner" /> Thinking...</div>}
      {error && <div className="tutor-error" role="alert">{error}</div>}
      {!review && (
        <form className="tutor-ask" onSubmit={(e) => { e.preventDefault(); void run(); }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            maxLength={500}
            placeholder={answer ? "Ask a follow-up (optional)" : "What are you stuck on? (optional)"}
            aria-label="Your question for the tutor"
          />
          <button className="btn btn-small btn-primary" disabled={busy}>{busy ? "..." : "Ask"}</button>
        </form>
      )}
    </div>
  );
}
