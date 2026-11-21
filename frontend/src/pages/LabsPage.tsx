import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, type LabDetail, type LabSummary, type NextStep } from "../api";
import { chapterNumber } from "../components/StatusBar";
import { useAuth } from "../auth";
import DrillCard from "../components/DrillCard";
import LabCover from "../components/LabCover";
import StatsBadges from "../components/StatsBadges";
import Logo from "../components/Logo";
import { useToast } from "../components/Toasts";
import { useStats } from "../stats";
import ThemeButton from "../components/ThemeButton";

const TRACK_LABEL: Record<string, string> = {
  languages: "Languages",
  frameworks: "Frameworks",
  databases: "Databases",
  devops: "DevOps",
  "system-design": "System design",
  ai: "AI",
  interview: "Interview",
};

export default function LabsPage() {
  const { user, logout } = useAuth();
  const toast = useToast();
  const { stats } = useStats();
  const navigate = useNavigate();
  const [labs, setLabs] = useState<LabSummary[] | null>(null);
  const [next, setNext] = useState<NextStep | null>(null);

  useEffect(() => {
    api.labs().then(setLabs).catch((e) => toast(e.message));
    api.next().then(setNext).catch(() => {});
  }, [toast]);

  // Brand new learners start with the 60 second onboarding.
  useEffect(() => {
    if (stats?.needs_onboarding) navigate("/welcome", { replace: true });
  }, [stats, navigate]);

  return (
    <div className="labs-page">
      <header className="topbar">
        <Logo to="/" />
        <Link to="/skills" className="btn btn-small btn-ghost nav-skills">🗺 Skill maps</Link>
        <span className="spacer" />
        <ThemeButton />
        {user?.is_admin && <Link className="btn btn-small btn-ghost" to="/admin">Admin</Link>}
        <StatsBadges username={user?.username ?? ""} />
        <button className="btn btn-small" onClick={logout}>Log out</button>
      </header>
      {/* Wide screens: the next step sits in a sidebar on the left (owner: "ample of space"); narrow ones: on top. */}
      <div className={`labs-layout ${next ? "has-side" : ""}`}>
      {next && (
        <aside className="labs-side">
          <NextCard next={next} />
          <NextRail next={next} />
        </aside>
      )}
      <main className="labs-main">
        {stats && (
          <section className="progress-strip" aria-label="Your progress">
            <div>
              <div className="muted small-text">Level {stats.level}</div>
              <div className="progress level-progress" role="progressbar" aria-label="Progress to the next level"
                aria-valuenow={stats.xp_total - stats.level_xp} aria-valuemin={0} aria-valuemax={stats.next_level_xp - stats.level_xp}>
                <span className="progress-fill" style={{ width: `${(100 * (stats.xp_total - stats.level_xp)) / Math.max(1, stats.next_level_xp - stats.level_xp)}%` }} />
              </div>
              <div className="muted small-text">{stats.next_level_xp - stats.xp_total} XP to level {stats.level + 1}</div>
            </div>
            <div>
              <div className="big-number">🔥 {stats.streak_current}</div>
              <div className="muted small-text">day streak · best {stats.streak_best}</div>
            </div>
            <div>
              <div className="big-number">{Math.min(stats.today_xp, stats.streak_min_xp)}/{stats.streak_min_xp}</div>
              <div className="muted small-text">XP today for the streak</div>
            </div>
          </section>
        )}
        <DrillCard />
        <h2>Your labs</h2>
        {!labs && <p className="muted">Loading...</p>}
        {/* The same tile as the home page's lab grid, plus a quiet progress line. */}
        <div className="h-labs labs-tiles">
          {labs?.map((lab) => {
            const { passed_tasks: done, total_tasks: total } = lab.progress;
            const pct = total ? (100 * done) / total : 0;
            return (
              <Link key={lab.id} to={`/labs/${lab.id}`} className={`h-lab ${total && done === total ? "is-done" : ""}`}>
                <div className="h-lab-img">
                  {lab.cover_url ? <img src={lab.cover_url} alt="" loading="lazy" /> : (
                    <LabCover id={lab.id} title={lab.title} track={lab.track} tags={lab.tags} coverUrl={null} credit={null} />
                  )}
                </div>
                <div className="h-lab-text">
                  <strong>{lab.title}</strong>
                  <span>{TRACK_LABEL[lab.track] ?? lab.track}{lab.level ? ` · ${lab.level[0].toUpperCase()}${lab.level.slice(1)}` : ""}{lab.estimated_minutes ? ` · ${lab.estimated_minutes} min` : ""}</span>
                  <div className="h-lab-progress" title={`${done} of ${total} tasks`}>
                    <div className="h-lab-track"><div style={{ width: `${pct}%` }} /></div>
                    <span>{total && done === total ? "✓ Done" : done ? `${done} / ${total} tasks` : `${total} task${total === 1 ? "" : "s"} · ${lab.chapter_count} chapter${lab.chapter_count === 1 ? "" : "s"}`}</span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </main>
      </div>
    </div>
  );
}

/** The first thing on the dashboard: one clear next step. */
function NextCard({ next }: { next: NextStep }) {
  const cont = next.kind === "continue";
  const pct = Math.round((100 * (next.step - 1)) / Math.max(1, next.steps));
  return (
    <section className={`next-card ${cont ? "is-continue" : "is-start"}`} aria-label={cont ? "Continue where you left off" : "Start here"}>
      <div className="next-text">
        <div className="next-kicker">{cont ? "Continue where you left off" : "Start here"}</div>
        <h1 className="next-title">{next.lab_title}</h1>
        <div className="next-where">
          Chapter {next.chapter_number} of {next.chapters}: {next.chapter_title}
          {cont && <> · step {next.step} of {next.steps}</>}
        </div>
        {cont ? (
          <div className="progress next-progress" role="progressbar" aria-label="Progress in this chapter" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
            <span className="progress-fill" style={{ width: `${pct}%` }} />
          </div>
        ) : (
          next.reason && <p className="muted next-reason">{next.reason}</p>
        )}
      </div>
      <Link className="btn btn-primary next-go" to={`/labs/${next.lab_id}?chapter=${encodeURIComponent(next.chapter_id)}`}>
        {cont ? "Continue →" : "Start the first chapter →"}
      </Link>
    </section>
  );
}

/**
 * The sidebar's long vertical rail: every chapter of the lab you are in, as a timeline. Done chapters are
 * ticked, the current one glows, upcoming ones are faint; each one opens that chapter.
 */
function NextRail({ next }: { next: NextStep }) {
  const [lab, setLab] = useState<LabDetail | null>(null);
  useEffect(() => {
    api.lab(next.lab_id).then(setLab).catch(() => setLab(null));
  }, [next.lab_id]);
  if (!lab) return null;
  return (
    <nav className="next-rail" aria-label={`Chapters of ${lab.title}`}>
      <div className="next-rail-head">
        <span>Chapters</span>
        <span className="muted">{lab.progress.passed_tasks}/{lab.progress.total_tasks} tasks</span>
      </div>
      <ol>
        {lab.chapters.map((c, i) => {
          const done = c.tasks.length > 0 && c.tasks.every((t) => t.passed);
          const now = c.id === next.chapter_id;
          return (
            <li key={c.id} className={`rail-step ${done ? "is-done" : ""} ${now ? "is-now" : ""}`}>
              <Link to={`/labs/${lab.id}?chapter=${encodeURIComponent(c.id)}`} ref={now ? (el) => el?.scrollIntoView({ block: "nearest" }) : undefined}>
                <span className="rail-dot" aria-hidden="true">{done ? "✓" : chapterNumber(lab.chapters, i)}</span>
                <span className="rail-title">{c.title}</span>
              </Link>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
