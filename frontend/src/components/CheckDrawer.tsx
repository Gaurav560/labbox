import type { CheckResponse } from "../api";

interface Props {
  result: CheckResponse | null;
  running: boolean;
  open: boolean;
  onClose: () => void;
  onShowOutput: () => void;
}

export default function CheckDrawer({ result, running, open, onClose, onShowOutput }: Props) {
  if (!open || (!running && !result)) return null;
  const allPass = !!result && result.passed_count === result.total_count;
  return (
    <section className={`check-drawer ${allPass ? "drawer-pass" : ""}`} aria-label="Check results" aria-live="polite">
      <div className="drawer-head">
        {running || !result ? (
          <span className="drawer-title"><span className="spinner" /> Running hidden tests on a clean machine...</span>
        ) : (
          <>
            <span className={`drawer-title ${allPass ? "pass" : "fail"}`}>
              {result.passed_count} of {result.total_count} passed{allPass ? " 🎉" : ""}
            </span>
            <span className="muted">{(result.duration_ms / 1000).toFixed(1)} s</span>
          </>
        )}
        <span className="spacer" />
        {result?.output && !running && (
          <button className="btn btn-small btn-ghost" onClick={onShowOutput}>Show output</button>
        )}
        <button className="btn btn-small btn-ghost" onClick={onClose} aria-label="Close results">✕</button>
      </div>
      {result && !running && (
        <ul className="drawer-list">
          {result.results.map((r) => (
            <li key={r.task} className={r.passed ? "res-pass" : "res-fail"}>
              <div className="res-head">
                <span className={`task-icon ${r.passed ? "pass" : "fail"}`} aria-hidden="true">{r.passed ? "✓" : "✗"}</span>
                <strong>{r.title || r.task}</strong>
                <span className="sr-only">{r.passed ? "passed" : "failed"}</span>
                <span className="spacer" />
                {!r.passed && (
                  <button className="btn btn-small btn-ghost" disabled title="The AI tutor arrives in a later update">
                    Ask the tutor
                  </button>
                )}
              </div>
              {!r.passed && <p className="res-message">{r.message}</p>}
              {!r.passed && r.expected != null && (
                <div className="expected-got">
                  <div>
                    <div className="eg-label">Expected</div>
                    <code>{r.expected}</code>
                  </div>
                  <div>
                    <div className="eg-label">Got</div>
                    <code>{r.actual ?? ""}</code>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
