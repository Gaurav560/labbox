import type { CheckResponse, Metric } from "../api";

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
          <span className="drawer-title"><span className="spinner" /> Running the hidden checks...</span>
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
      {result && !running && !!result.metrics?.length && (
        <ul className="metrics" aria-label="Metrics">
          {result.metrics.map((m) => <Gauge key={m.name} metric={m} />)}
        </ul>
      )}
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


// Friendly names and units for the usual metric names; anything else is shown as it is.
function describe(name: string): { label: string; unit: string; scale: number } {
  const lat = /^p(\d+)_ms$/.exec(name);
  if (lat) return { label: `p${lat[1]} latency`, unit: "ms", scale: 1 };
  if (name === "error_rate") return { label: "errors", unit: "%", scale: 100 };
  if (name === "rps") return { label: "throughput", unit: "req/s", scale: 1 };
  const ms = /^(.*)_ms$/.exec(name);
  if (ms) return { label: ms[1].replace(/_/g, " "), unit: "ms", scale: 1 };
  return { label: name.replace(/_/g, " "), unit: "", scale: 1 };
}

const fmt = (v: number) => (Math.abs(v) >= 100 ? Math.round(v).toString() : Number(v.toFixed(2)).toString());

/** A metric against its target: a bar for the value and a tick for the target, green when met. */
function Gauge({ metric: m }: { metric: Metric }) {
  const { label, unit, scale } = describe(m.name);
  const value = m.value * scale;
  const target = m.target == null ? null : m.target * scale;
  const met = target == null || m.better == null ? null : m.better === "lower" ? value <= target : value >= target;
  // The bar's full width: room for the target and the value, so both are always visible.
  const max = Math.max(target == null ? value : target * 1.6, value * 1.08, 1e-9);
  const pct = (v: number) => `${Math.min(100, Math.max(0, (v / max) * 100))}%`;
  const state = met === null ? "" : met ? "metric-met" : "metric-missed";
  return (
    <li className={`gauge ${state}`} aria-label={`${label}: ${fmt(value)} ${unit}${target != null ? `, target ${m.better === "higher" ? "at least" : "at most"} ${fmt(target)}` : ""}`}>
      <div className="gauge-head">
        <span className="metric-name">{label}</span>
        <strong className="metric-value">{fmt(value)}<small>{unit && ` ${unit}`}</small></strong>
      </div>
      <div className="gauge-track" aria-hidden="true">
        <div className="gauge-fill" style={{ width: pct(value) }} />
        {target != null && <div className="gauge-target" style={{ left: pct(target) }} />}
      </div>
      {target != null && (
        <div className="gauge-foot muted small-text">
          target {m.better === "higher" ? "≥" : "≤"} {fmt(target)}{unit && ` ${unit}`} {met === null ? "" : met ? "· met ✓" : "· not yet"}
        </div>
      )}
    </li>
  );
}
