import { useState } from "react";

/*
 * "Watch it run": a chapter writes a small table inside :::trace{title="..."}; each row is one moment
 * of the program, each column a variable, and an optional "note" column says in words what happened.
 * The learner steps through it; rows appear one at a time, and the values that just changed are
 * highlighted, so they can see a variable change instead of only reading about it.
 */

export interface TraceData { headers: string[]; rows: string[][] }

export default function Trace({ title, data }: { title?: string; data: TraceData }) {
  const [at, setAt] = useState(0); // index of the row being shown
  const noteCol = data.headers.findIndex((h) => h.trim().toLowerCase() === "note");
  const cols = data.headers.map((h, i) => ({ h, i })).filter((c) => c.i !== noteCol);
  const last = data.rows.length - 1;
  if (last < 0) return null;
  const note = noteCol >= 0 ? data.rows[at][noteCol] : "";

  return (
    <figure className="trace" aria-label={title ? `Watch it run: ${title}` : "Watch it run"}>
      <div className="trace-head">
        <span className="trace-label">▶ Watch it run</span>
        {title && <span className="trace-title">{title}</span>}
        <span className="spacer" />
        <span className="muted small-text">step {at + 1} of {last + 1}</span>
      </div>
      <table className="trace-table">
        <thead>
          <tr>{cols.map((c) => <th key={c.i} scope="col">{c.h}</th>)}</tr>
        </thead>
        <tbody>
          {data.rows.slice(0, at + 1).map((row, r) => (
            <tr key={r} className={r === at ? "trace-now" : ""}>
              {cols.map((c) => {
                const changed = r > 0 && row[c.i] !== data.rows[r - 1][c.i];
                return <td key={c.i} className={r === at && changed ? "trace-changed" : ""}>{row[c.i]}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
      {note && <p className="trace-note" aria-live="polite">{note}</p>}
      <div className="trace-controls">
        <button className="btn btn-small btn-ghost" onClick={() => setAt(0)} disabled={at === 0}>Restart</button>
        <button className="btn btn-small btn-ghost" onClick={() => setAt(Math.max(0, at - 1))} disabled={at === 0}>◀ Back</button>
        <button className="btn btn-small trace-next" onClick={() => setAt(Math.min(last, at + 1))} disabled={at === last}>
          {at === last ? "Done" : "Next ▶"}
        </button>
      </div>
    </figure>
  );
}
