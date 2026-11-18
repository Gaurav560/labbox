import { Link } from "react-router-dom";
import type { Chapter } from "../api";

export type UiStatus = "starting" | "running" | "stopped" | "error";

interface Props {
  title: string;
  chapters: Chapter[];
  chapterId: string;
  onChapter: (id: string) => void;
  status: UiStatus;
  username: string;
  onStart: () => void;
  onStop: () => void;
  onReset: () => void;
}

const LABEL: Record<UiStatus, string> = { starting: "Starting", running: "Running", stopped: "Stopped", error: "Error" };

export default function StatusBar(p: Props) {
  const index = p.chapters.findIndex((c) => c.id === p.chapterId);
  return (
    <header className="topbar">
      <Link to="/labs" className="link">← Labs</Link>
      <span className="brand">{p.title}{index >= 0 && ` · Chapter ${index + 1}`}</span>
      <select value={p.chapterId} onChange={(e) => p.onChapter(e.target.value)}>
        {p.chapters.map((c, i) => (
          <option key={c.id} value={c.id}>{i + 1}. {c.title}</option>
        ))}
      </select>
      <span className="spacer" />
      <span className={`status-dot status-${p.status}`} />
      <span className="status-label">{LABEL[p.status]}</span>
      {p.status === "stopped" || p.status === "error" ? (
        <button className="btn btn-small" onClick={p.onStart}>Start machine</button>
      ) : (
        <button className="btn btn-small" onClick={p.onStop} disabled={p.status !== "running"}>Stop machine</button>
      )}
      <button className="btn btn-small btn-danger" onClick={p.onReset} disabled={p.status === "starting"}>Reset lab</button>
      <span className="muted">{p.username}</span>
    </header>
  );
}
