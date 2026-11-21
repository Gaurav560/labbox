import { Link } from "react-router-dom";
import type { Chapter, Progress, ServiceStatus } from "../api";
import { useTheme } from "../theme";
import { LogoMark } from "./Logo";
import StatsBadges from "./StatsBadges";
import MachineMenu from "./MachineMenu";
import TextSizeMenu from "./TextSizeMenu";

export type UiStatus = "starting" | "running" | "stopped" | "error";

interface Props {
  title: string;
  chapters: Chapter[];
  chapterId: string;
  onChapter: (id: string) => void;
  progress: Progress | null;
  status: UiStatus;
  services?: ServiceStatus[];
  username: string;
  focus: boolean;
  onFocus: () => void;
  onStart: () => void;
  onStop: () => void;
  onReset: () => void;
}

const LABEL: Record<UiStatus, string> = { starting: "Starting", running: "Running", stopped: "Stopped", error: "Error" };

export default function StatusBar(p: Props) {
  const { theme, toggle } = useTheme();
  const pct = p.progress && p.progress.total_tasks ? Math.round((100 * p.progress.passed_tasks) / p.progress.total_tasks) : 0;
  return (
    <header className="topbar">
      <Link to="/" className="logo" aria-label="LabBox by Telusko home"><LogoMark size={24} /></Link>
      <Link to="/labs" className="link">← Labs</Link>
      <span className="brand">{p.title}</span>
      <span className="muted" aria-hidden="true">›</span>
      <label className="sr-only" htmlFor="chapter-select">Chapter</label>
      <select id="chapter-select" className="chapter-select" value={p.chapterId} onChange={(e) => p.onChapter(e.target.value)}>
        {p.chapters.map((c, i) => (
          <option key={c.id} value={c.id}>Ch {chapterNumber(p.chapters, i)} · {c.title}</option>
        ))}
      </select>
      {p.progress && (
        <span className="lab-progress" title="Tasks passed in this lab">
          <span className="progress progress-inline" role="progressbar" aria-label="Lab progress" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
            <span className="progress-fill" style={{ width: `${pct}%` }} />
          </span>
          <span className="small-text">{p.progress.passed_tasks}/{p.progress.total_tasks}</span>
        </span>
      )}
      <span className="spacer" />
      <span className="machine">
        <span className={`status-dot status-${p.status}`} aria-hidden="true" />
        <span className="status-label">{LABEL[p.status]}</span>
        {!!p.services?.length && (
          <span className="service-dots" aria-label="Services">
            {p.services.map((s) => (
              <span key={s.name} className="service-dot" title={`${s.name}: ${s.status}`}>
                <span className={`status-dot status-${s.status === "running" ? "running" : s.status === "starting" ? "starting" : "stopped"}`} aria-hidden="true" />
                <span className="small-text">{s.name}</span>
                <span className="sr-only">{s.status}</span>
              </span>
            ))}
          </span>
        )}
      </span>
      {(p.status === "stopped" || p.status === "error") && (
        <button className="btn btn-small" onClick={p.onStart}>Start machine</button>
      )}
      <MachineMenu status={p.status} onStop={p.onStop} onReset={p.onReset} />
      <button className="btn btn-small btn-ghost" onClick={p.onFocus} aria-pressed={p.focus} title="Hide the file tree and widen the lesson and editor">
        {p.focus ? "Exit focus" : "Focus"}
      </button>
      <TextSizeMenu />
      <button className="btn btn-small btn-ghost" onClick={toggle} aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`} title="Theme">
        {theme === "dark" ? "☀" : "☾"}
      </button>
      <StatsBadges username={p.username} />
    </header>
  );
}

/** A course that opens with a chapter 0 (an introduction, id "00-...") numbers chapters by their ids, so the
 * menu matches the chapter folders; others count from 1. */
export function chapterNumber(chapters: { id: string }[], i: number): number {
  if (!chapters[0]?.id.startsWith("00-")) return i + 1;
  const n = /^(\d+)-/.exec(chapters[i]?.id ?? "");
  return n ? Number(n[1]) : i;  // the number in the id ("11-reading-the-request" is Ch 11), so the folders agree
}
