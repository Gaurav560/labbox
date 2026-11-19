import { useState } from "react";
import { api, ApiError, type DesignAttempt, type DesignQuestion, type DesignResult } from "../api";
import LessonMarkdown from "./LessonMarkdown";

// A design review: a few short written answers, graded by the tutor model against the lab's rubric.
// It gives feedback and XP, and never blocks finishing the chapter. Answers can be improved and resent.
export default function DesignStep(p: {
  labId: string;
  chapterId: string;
  stepIndex: number;
  questions: DesignQuestion[];
  attempt: DesignAttempt | undefined;
  onGraded: (attempt: DesignAttempt) => void;
}) {
  const [answers, setAnswers] = useState<Record<string, string>>(() => p.attempt?.answers ?? {});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const result: DesignResult | undefined = p.attempt?.result;
  const byId = Object.fromEntries((result?.questions ?? []).map((q) => [q.id, q]));
  const written = p.questions.filter((q) => (answers[q.id] ?? "").trim().length >= 20).length;

  const submit = async () => {
    setBusy(true);
    setError(null);
    try {
      const r = await api.gradeDesign(p.labId, p.chapterId, p.stepIndex, answers);
      p.onGraded({ answers, result: r });
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not grade right now. Try again in a minute.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="design">
      {result && (
        <div className={`design-score ${result.score * 2 >= result.max ? "good" : ""}`}>
          <strong>{result.score} / {result.max}</strong>
          <span>{result.score * 2 >= result.max ? "Solid reasoning. Improve any answer and send it again if you like." : "A start. Read the feedback, improve your answers and send them again."}</span>
        </div>
      )}
      {p.questions.map((q, i) => {
        const r = byId[q.id];
        return (
          <section key={q.id} className="design-q">
            <div className="design-q-head">
              <span className="design-num">{i + 1}</span>
              <LessonMarkdown markdown={q.text} />
              {r && <span className={`design-pts ${r.score === r.max ? "full" : r.score === 0 ? "none" : ""}`}>{r.score}/{r.max}</span>}
            </div>
            <textarea
              value={answers[q.id] ?? ""}
              onChange={(e) => setAnswers((a) => ({ ...a, [q.id]: e.target.value }))}
              placeholder="A few sentences, in your own words."
              maxLength={2000}
              rows={4}
              aria-label={`Answer to question ${i + 1}`}
            />
            {r && (
              <ul className="design-feedback">
                {r.criteria.map((c) => (
                  <li key={c.id} className={c.score === c.max ? "full" : c.score === 0 ? "none" : "part"}>
                    <span className="design-mark" aria-hidden="true">{c.score === c.max ? "✓" : c.score === 0 ? "○" : "◐"}</span>
                    <span>{c.feedback || (c.score === c.max ? "Covered." : "Not covered yet.")}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        );
      })}
      {error && <p className="design-error" role="alert">{error}</p>}
      <div className="design-actions">
        <button className="btn btn-primary" onClick={submit} disabled={busy || written === 0}>
          {busy ? <><span className="spinner" /> Reading your answers...</> : result ? "Send again" : "Get feedback"}
        </button>
        <span className="muted small-text">Graded by the AI tutor against a rubric. Gives XP, never blocks the chapter.</span>
      </div>
    </div>
  );
}
