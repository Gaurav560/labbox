import { Suspense, lazy, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type LabDetail } from "../api";
import { useAuth } from "../auth";
import { chapterNumber } from "../components/StatusBar";
import StatsBadges from "../components/StatsBadges";
import ThemeButton from "../components/ThemeButton";
import { LogoMark } from "../components/Logo";
import type { Stop } from "../components/NeonWorld";
import { useTheme } from "../theme";
import { usePhone } from "../usePhone";

// three.js and the world are large: loaded only on map pages.
const NeonWorld = lazy(() => import("../components/NeonWorld"));

/** One lab's road: each chapter a stop; you start at the first chapter not done yet. */
export default function LabMapPage() {
  const { labId = "" } = useParams();
  const { user } = useAuth();
  const { theme } = useTheme();
  const phone = usePhone();
  const [lab, setLab] = useState<LabDetail | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [reset, setReset] = useState(0);
  const [noWebGl, setNoWebGl] = useState(false);
  useEffect(() => {
    setSelected(null);
    api.lab(labId).then(setLab).catch(() => setLab(null));
  }, [labId]);

  const stops: Stop[] = useMemo(() => {
    if (!lab) return [];
    const done = (i: number) => lab.chapters[i].tasks.length > 0 && lab.chapters[i].tasks.every((t) => t.passed);
    const next = lab.chapters.findIndex((_, i) => !done(i));
    return lab.chapters.map((c, i) => ({
      id: c.id,
      number: String(chapterNumber(lab.chapters, i)).padStart(2, "0"),
      title: c.title,
      state: done(i) ? "done" : i === next ? "next" : "open",
    }));
  }, [lab]);
  const stop = stops.find((s) => s.id === selected) ?? stops.find((s) => s.state === "next") ?? null;
  const chapter = lab?.chapters.find((c) => c.id === stop?.id);
  const show3d = !phone && !noWebGl;

  return (
    <div className="track-page">
      <header className="topbar">
        <Link to="/" className="logo" aria-label="LabBox by Telusko home"><LogoMark size={24} /></Link>
        <Link to="/skills" className="link">← Skill maps</Link>
        <span className="brand">{lab?.title ?? labId}</span>
        {lab && <span className="muted small-text">{stops.filter((s) => s.state === "done").length} of {stops.length} chapters</span>}
        <span className="spacer" />
        <ThemeButton />
        <StatsBadges username={user?.username ?? ""} />
      </header>
      <main className={`track-main ${show3d ? "has-3d" : ""}`} aria-label="Skill map">
        {lab && show3d && (
          <div className="roadmap-stage">
            <Suspense fallback={<div className="roadmap3d muted small-text roadmap-loading">Building your road...</div>}>
              <NeonWorld stops={stops} selected={selected} onSelect={setSelected} resetSignal={reset} theme={theme} onFail={() => setNoWebGl(true)} />
            </Suspense>
            <div className="roadmap-help small-text" aria-hidden="true">Drag to look around · scroll to zoom · click a sign to ride there</div>
            <button className="btn btn-small roadmap-reset" onClick={() => setReset((r) => r + 1)}>Behind the rider</button>
          </div>
        )}
        {lab && (
          <aside className="roadmap-panel" aria-label="Chapters">
            {stop && chapter && (
              <div className="stop-card">
                <div className={`topic-state stop-${stop.state}`}>{stop.state === "done" ? "✓ Done" : stop.state === "next" ? "You are here" : "Chapter"}</div>
                <h2 className="roadmap-panel-title">Ch {Number(stop.number)} · {chapter.title}</h2>
                <p className="muted small-text">{chapter.tasks.filter((t) => t.passed).length} of {chapter.tasks.length} tasks{chapter.minutes ? ` · about ${chapter.minutes} min` : ""}</p>
                <Link className="btn btn-primary stop-enter" to={`/labs/${lab.id}?chapter=${encodeURIComponent(chapter.id)}`}>Enter chapter →</Link>
              </div>
            )}
            <ol className="topic-list stop-list">
              {stops.map((s) => (
                <li key={s.id} className={`skill-node stop-${s.state} ${s.id === stop?.id ? "is-current" : ""}`}>
                  <button onClick={() => setSelected(s.id)} aria-label={`Chapter ${Number(s.number)}: ${s.title}`}>
                    <span className="stop-num">{s.number}</span>
                    <span className="skill-title">{s.title}</span>
                    <span className="skill-state">{s.state === "done" ? "✓" : s.state === "next" ? "▶" : ""}</span>
                  </button>
                </li>
              ))}
            </ol>
          </aside>
        )}
      </main>
    </div>
  );
}
