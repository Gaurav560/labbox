import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type LabDetail, type NextStep } from "../api";
import { useAuth } from "../auth";
import { inkOn, labTone, mix } from "../brand";
import LabCover from "../components/LabCover";
import MetroMap, { labLines } from "../components/MetroMap";
import { LogoMark } from "../components/Logo";
import { chapterNumber } from "../components/StatusBar";
import ProfileMenu from "../components/ProfileMenu";
import ThemeButton from "../components/ThemeButton";
import { useToast } from "../components/Toasts";
import { TRACK_LABEL } from "./LabsPage";

/*
 * A lab's own page (owner, 22 November: a lab card opens a page for that lab first, then the lab itself). The
 * cover in the lab's colour, what the course is, how far you are, one button into the lab (the lesson, editor and
 * terminal page), and the chapters as a metro map (a line per course part, as on the skill maps); each chapter
 * and subtopic opens the lab there.
 */
export default function CoursePage() {
  const { labId = "" } = useParams();
  const { user } = useAuth();
  const toast = useToast();
  const [lab, setLab] = useState<LabDetail | null>(null);
  const [next, setNext] = useState<NextStep | null>(null);
  useEffect(() => {
    setLab(null);
    api.lab(labId).then(setLab).catch((e) => toast(e.message));
    api.next(labId).then(setNext).catch(() => setNext(null));
  }, [labId, toast]);

  const lines = useMemo(() => {
    if (!lab) return [];
    const at = next?.kind === "continue" && next.lab_id === lab.id ? lab.chapters.findIndex((c) => c.id === next.chapter_id) : -1;
    return labLines(lab, at >= 0 ? at : undefined);
  }, [lab, next]);

  if (!lab) return <div className="course-page"><Topbar title={labId} username={user?.username ?? ""} /></div>;

  const done = (c: LabDetail["chapters"][number]) => c.tasks.length > 0 && c.tasks.every((t) => t.passed);
  const doneCount = lab.chapters.filter(done).length;
  const here = next?.kind === "continue" && next.lab_id === lab.id;  // next is asked for this lab
  const nowIdx = here ? lab.chapters.findIndex((c) => c.id === next.chapter_id) : Math.max(0, lab.chapters.findIndex((c) => !done(c)));
  const now = lab.chapters[nowIdx] ?? lab.chapters[0];
  const started = here || lab.progress.passed_tasks > 0;
  const go = `/labs/${lab.id}?chapter=${encodeURIComponent(now.id)}`;
  const pct = lab.chapters.length ? Math.round((100 * doneCount) / lab.chapters.length) : 0;
  const tone = labTone(lab.id, lab.cover_credit);
  const vars = { "--tone": tone, "--tone-ink": inkOn(tone), "--tone-hi": mix(tone, "#ffffff", 0.18), "--tone-lo": mix(tone, "#000000", 0.22) } as CSSProperties;
  const level = lab.level ? `${lab.level[0].toUpperCase()}${lab.level.slice(1)}` : null;

  return (
    <div className="course-page" style={vars}>
      <Topbar title={lab.title} username={user?.username ?? ""} />
      <main className="course-main" aria-label={lab.title}>
        <section className="course-hero">
          <div className="course-cover">
            {lab.cover_url ? <img src={lab.cover_url} alt="" /> : (
              <LabCover id={lab.id} title={lab.title} track={lab.track} tags={lab.tags} coverUrl={null} credit={null} />
            )}
          </div>
          <div className="course-hero-text">
            <div className="course-kicker">{[TRACK_LABEL[lab.track] ?? lab.track, level].filter(Boolean).join(" · ")}</div>
            <h1>{lab.title}</h1>
            <p className="course-sub">{lab.subtitle}</p>
            <div className="course-progress" role="progressbar" aria-label="Chapters done" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
              <div className="course-bar"><div style={{ width: `${pct}%` }} /></div>
              <span>{doneCount} of {lab.chapters.length} chapters · {lab.progress.passed_tasks} of {lab.progress.total_tasks} tasks</span>
            </div>
            <div className="course-actions">
              <Link className="course-go" to={go}>
                <span aria-hidden="true" className="course-play">▶</span>{started ? "Continue" : "Start"}: Chapter {chapterNumber(lab.chapters, nowIdx)} →
              </Link>
            </div>
            <p className="course-where">
              {now.title}{here ? ` · step ${next.step} of ${next.steps}` : ""}
            </p>
          </div>
        </section>

        <section className="course-about" aria-label="About this lab">
          <p>{lab.description}</p>
          <ul className="course-facts">
            <li><strong>{lab.chapters.length}</strong><span>chapters</span></li>
            <li><strong>{lab.progress.total_tasks}</strong><span>hands-on tasks</span></li>
            {lines.length > 1 && <li><strong>{lines.length}</strong><span>parts</span></li>}
            <li><strong>Your own machine</strong><span>editor, terminal, instant checks</span></li>
          </ul>
        </section>

        {lab.before_you_start && (
          <section className="course-before" aria-labelledby="course-before-title">
            <h2 id="course-before-title">Before you start</h2>
            <p className="course-before-summary">{lab.before_you_start.summary}</p>
            {lab.before_you_start.needs.length > 0 && (
              <ul className="course-needs">
                {lab.before_you_start.needs.map((n, i) => (
                  <li key={i}>
                    <span className="course-need-check" aria-hidden="true">✓</span>
                    <div>
                      <strong>{n.know}</strong>
                      {n.why && <p>{n.why}</p>}
                      {n.lab && n.lab_title && (
                        <Link className="course-need-link" to={`/courses/${n.lab}`}>
                          Learn it in {n.lab_title}{n.where ? `, ${n.where}` : ""} →
                        </Link>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}

        <section className="course-syllabus" aria-label="Chapters">
          <h2>What you will learn</h2>
          <h3 className="course-map-title">Skill map</h3>
          <p className="muted">Every chapter on its line; each subtopic opens its lesson.</p>
          <MetroMap lines={lines} />
        </section>
      </main>
    </div>
  );
}

function Topbar({ title, username }: { title: string; username: string }) {
  return (
    <header className="topbar">
      <Link to="/" className="logo" aria-label="LabBox by Telusko home"><LogoMark size={24} /></Link>
      <Link to="/labs" className="link">← Dashboard</Link>
      <span className="brand">{title}</span>
      <span className="spacer" />
      <ThemeButton />
      <ProfileMenu username={username} />
    </header>
  );
}
