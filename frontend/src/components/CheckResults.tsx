import { useState } from "react";
import type { CheckResponse } from "../api";

interface Props {
  result: CheckResponse | null;
  running: boolean;
}

export default function CheckResults({ result, running }: Props) {
  const [open, setOpen] = useState(true);
  const [showOutput, setShowOutput] = useState(false);

  if (running) return <div className="results"><div className="results-bar"><span className="spinner" /> Running hidden tests on a clean machine...</div></div>;
  if (!result) return <div className="results"><div className="results-bar muted">Press Check to run the tests for this chapter.</div></div>;

  const allPass = result.passed_count === result.total_count;
  return (
    <div className="results">
      <div className="results-bar">
        <button className="link" onClick={() => setOpen(!open)}>{open ? "▾" : "▸"}</button>
        <strong className={allPass ? "pass" : "fail"}>
          Check results: {result.passed_count} of {result.total_count} pass
        </strong>
        <span className="muted">· {(result.duration_ms / 1000).toFixed(1)} s</span>
        <span className="spacer" />
        {result.output && (
          <button className="btn btn-small" onClick={() => setShowOutput(!showOutput)}>
            Output {showOutput ? "▴" : "▾"}
          </button>
        )}
      </div>
      {open && (
        <ul className="results-list">
          {result.results.map((r) => (
            <li key={r.task}>
              <span className={`task-icon ${r.passed ? "pass" : "fail"}`}>{r.passed ? "✓" : "✗"}</span>
              <strong>{r.title || r.task}</strong>
              {!r.passed && <span className="muted"> · {r.message}</span>}
            </li>
          ))}
        </ul>
      )}
      {showOutput && <pre className="output">{result.output}</pre>}
    </div>
  );
}
