import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, type LabDetail, type LabSummary, type NextStep } from "../api";
import { chapterNumber } from "../components/StatusBar";
import { InkProgress, LabPrint, Seal, TRACK_INK } from "../components/UkiyoArt";
import { byCategory, Directory, TRACK_LABEL } from "../components/UkiyoDirectory";
import { useAuth } from "../auth";
import DrillCard from "../components/DrillCard";
import ProfileMenu from "../components/ProfileMenu";
import Logo from "../components/Logo";
import { useToast } from "../components/Toasts";
import { useStats } from "../stats";
import ThemeButton from "../components/ThemeButton";

// The directory (category tiles and lab rows) is shared with the home page: components/UkiyoDirectory.tsx.
export { CATEGORY_ORDER, TRACK_LABEL } from "../components/UkiyoDirectory";

export default function LabsPage() {
  const { user } = useAuth();
  const toast = useToast();
  const { stats } = useStats();
  const navigate = useNavigate();
  const [labs, setLabs] = useState<LabSummary[] | null>(null);
  const [next, setNext] = useState<NextStep | null>(null);
  const [nextLab, setNextLab] = useState<LabDetail | null>(null);   // the lab of the next step (chapters, track)

  useEffect(() => {
    api.labs().then(setLabs).catch((e) => toast(e.message));
    api.next().then(setNext).catch(() => {});
  }, [toast]);

  useEffect(() => {
    if (next) api.lab(next.lab_id).then(setNextLab).catch(() => setNextLab(null));
  }, [next]);

  // Brand new learners start with the 60 second onboarding.
  useEffect(() => {
    if (stats?.needs_onboarding) navigate("/welcome", { replace: true });
  }, [stats, navigate]);

  const groups = useMemo(() => (labs ? byCategory(labs) : []), [labs]);
  const withLabs = groups.filter((g) => g.labs.length);

  return (
    <div className="labs-page u-dash-page">
      <header className="topbar">
        <Logo to="/" />
        <span className="spacer" />
        <ThemeButton />
        <Link className="btn btn-small btn-ghost" to="/library">Premium Reads</Link>
        {user?.is_admin && <Link className="btn btn-small btn-ghost" to="/admin">Admin</Link>}
        <ProfileMenu username={user?.username ?? ""} />
      </header>
      <main className="u-dash">
        <header className="u-dash-head">
          <span className="u-vertical" aria-hidden="true">The lab index</span>
          <div>
            <p className="u-kicker">{greeting()}</p>
            <h1 className="u-dash-title">{user?.username ? <>Welcome back, <em>{user.username}</em>.</> : "Your labs."}</h1>
            {labs && <p className="u-dash-sub">{labs.length} labs in {withLabs.length} categories. Every one runs in a real machine; you learn by building.</p>}
          </div>
        </header>

        {next && <Feature next={next} lab={nextLab} />}

        <DrillCard />

        <section className="u-section" aria-labelledby="your-labs">
          <div className="u-section-head">
            <h2 id="your-labs">Your labs</h2>
            <span className="u-rule-fill" aria-hidden="true" />
          </div>
          {!labs && <p className="muted">Loading...</p>}
          {labs && <Directory labs={labs} link={(lab) => `/courses/${lab.id}`} />}
        </section>
      </main>
    </div>
  );
}

function greeting(): string {
  const h = new Date().getHours();
  return h < 5 ? "Working late" : h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
}

/**
 * The first thing on the dashboard: one clear next step, as an editorial feature. The lab's own print on one side;
 * the lab, the chapter, the step, an ink progress line and the chapter ladder on the other. The red button continues.
 */
function Feature({ next, lab }: { next: NextStep; lab: LabDetail | null }) {
  const cont = next.kind === "continue";
  const pct = cont ? (next.step - 1) / Math.max(1, next.steps) : 0;
  const chapterUrl = (id: string) => `/labs/${next.lab_id}?chapter=${encodeURIComponent(id)}`;
  const track = lab?.track ?? next.track ?? "languages";
  return (
    <section className={`u-feature ${cont ? "is-continue" : "is-start"}`} aria-label={cont ? "Continue where you left off" : "Start here"}
      style={{ "--ink": TRACK_INK[track] ?? "var(--text)" } as CSSProperties}>
      <div className="u-feature-art">
        <LabPrint lab={next.lab_id} track={track} />
        <span className="u-feature-seal"><Seal lines={cont ? ["NEXT"] : ["START"]} size={58} /></span>
      </div>
      <div className="u-feature-text">
        <p className="u-kicker">{cont ? "Continue where you left off" : "Start here"} · {TRACK_LABEL[track] ?? track}</p>
        <h2 className="u-feature-title">{next.lab_title}</h2>
        <p className="u-feature-where">
          Chapter {next.chapter_number} of {next.chapters}: <strong>{next.chapter_title}</strong>
          {cont && <> · step {next.step} of {next.steps}</>}
        </p>
        {!cont && next.reason && <p className="u-feature-reason">{next.reason}</p>}
        {cont && <InkProgress value={pct} label="Progress in this chapter" />}
        <div className="u-feature-actions">
          <Link className="btn u-btn-seal u-feature-go" to={chapterUrl(next.chapter_id)}>{cont ? "Continue" : "Start the first chapter"}</Link>
          <Link className="btn btn-ghost" to={`/courses/${next.lab_id}`}>Course page</Link>
        </div>
        {lab && (
          <nav className="u-ladder" aria-label={`Chapters of ${lab.title}`}>
            {lab.chapters.map((c, i) => {
              const done = c.tasks.length > 0 && c.tasks.every((t) => t.passed);
              const now = c.id === next.chapter_id;
              return (
                <Link key={c.id} to={chapterUrl(c.id)} title={c.title}
                  className={`u-rung ${done ? "is-done" : ""} ${now ? "is-now" : ""}`} aria-current={now ? "step" : undefined}>
                  {chapterNumber(lab.chapters, i)}
                </Link>
              );
            })}
          </nav>
        )}
      </div>
    </section>
  );
}
