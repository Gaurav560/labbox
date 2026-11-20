import { useEffect, useState } from "react";

/*
 * "Watch it run": a chapter writes a small table inside :::trace{title="..."}; each row is one moment
 * of the program, each column a variable, and an optional "note" column says in words what happened.
 * Rows appear one at a time and the values that just changed are highlighted, so a learner can see a
 * variable change instead of only reading about it. Every control does something (owner's review):
 * ▶ Watch it run plays the rows by itself (⏸ pauses), Back and Restart step back, Next steps on, and at
 * the end "Watch again" starts over.
 */

export interface TraceData { headers: string[]; rows: string[][] }

const PLAY_MS = 1500; // one row every 1.5 seconds: time to read the note

export default function Trace({ title, data }: { title?: string; data: TraceData }) {
  const [at, setAt] = useState(0); // index of the row being shown
  const [playing, setPlaying] = useState(false);
  const noteCol = data.headers.findIndex((h) => h.trim().toLowerCase() === "note");
  const cols = data.headers.map((h, i) => ({ h, i })).filter((c) => c.i !== noteCol);
  const last = data.rows.length - 1;

  useEffect(() => {
    if (!playing) return;
    if (at >= last) {
      setPlaying(false);
      return;
    }
    const t = setTimeout(() => setAt((a) => Math.min(last, a + 1)), PLAY_MS);
    return () => clearTimeout(t);
  }, [playing, at, last]);

  if (last < 0) return null;
  const note = noteCol >= 0 ? data.rows[at][noteCol] : "";
  const done = at === last;
  const play = () => {
    if (playing) return setPlaying(false);
    if (done) setAt(0); // played to the end before: play it again from the start
    setPlaying(true);
  };
  const by = (fn: () => void) => () => { setPlaying(false); fn(); }; // stepping by hand pauses the player

  return (
    <figure className="trace" aria-label={title ? `Watch it run: ${title}` : "Watch it run"}>
      <div className="trace-head">
        <button className="trace-play" onClick={play} aria-pressed={playing} title={playing ? "Pause" : "Play the steps one by one"}>
          {playing ? "⏸ Pause" : "▶ Watch it run"}
        </button>
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
        <button className="btn btn-small btn-ghost" onClick={by(() => setAt(0))} disabled={at === 0}>Restart</button>
        <button className="btn btn-small btn-ghost" onClick={by(() => setAt(Math.max(0, at - 1)))} disabled={at === 0}>◀ Back</button>
        {done ? (
          <button className="btn btn-small trace-next" onClick={() => { setAt(0); setPlaying(true); }}>↻ Watch again</button>
        ) : (
          <button className="btn btn-small trace-next" onClick={by(() => setAt(Math.min(last, at + 1)))}>Next ▶</button>
        )}
      </div>
    </figure>
  );
}
