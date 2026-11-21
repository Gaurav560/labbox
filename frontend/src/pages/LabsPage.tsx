import { useEffect, useState, type CSSProperties } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, type LabDetail, type LabSummary, type NextStep } from "../api";
import { inkOn, labTone, mix } from "../brand";
import { chapterNumber } from "../components/StatusBar";
import { useAuth } from "../auth";
import DrillCard from "../components/DrillCard";
import LabCover from "../components/LabCover";
import ProfileMenu from "../components/ProfileMenu";
import Logo from "../components/Logo";
import { useToast } from "../components/Toasts";
import { useStats } from "../stats";
import ThemeButton from "../components/ThemeButton";

export const TRACK_LABEL: Record<string, string> = {
  languages: "Languages",
  frameworks: "Frameworks",
  databases: "Databases",
  devops: "DevOps",
  "system-design": "System design",
  ai: "AI",
  interview: "Interview",
};

export default function LabsPage() {
  const { user } = useAuth();
  const toast = useToast();
  const { stats } = useStats();
  const navigate = useNavigate();
  const [labs, setLabs] = useState<LabSummary[] | null>(null);
  const [next, setNext] = useState<NextStep | null>(null);
  const [nextLab, setNextLab] = useState<LabDetail | null>(null);   // the lab of the next step (deck keys, rail)

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

  return (
    <div className="labs-page">
      <header className="topbar">
        <Logo to="/" />
        <Link to="/skills" className="btn btn-small btn-ghost nav-skills">🗺 Skill maps</Link>
        <span className="spacer" />
        <ThemeButton />
        {user?.is_admin && <Link className="btn btn-small btn-ghost" to="/admin">Admin</Link>}
        <ProfileMenu username={user?.username ?? ""} />
      </header>
      {/* Wide screens: the next step sits in a sidebar on the left (owner: "ample of space"); narrow ones: on top. */}
      <div className={`labs-layout ${next ? "has-side" : ""}`}>
      {next && (
        <aside className="labs-side">
          <NextCard next={next} lab={nextLab} />
          {nextLab && <NextRail next={next} lab={nextLab} />}
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
              <Link key={lab.id} to={`/courses/${lab.id}`} className={`h-lab ${total && done === total ? "is-done" : ""}`}>
                <div className="h-lab-img">
                  {lab.cover_url ? <img src={lab.cover_url} alt="" loading="lazy" /> : (
                    <LabCover id={lab.id} title={lab.title} track={lab.track} tags={lab.tags} coverUrl={null} credit={null} />
                  )}
                </div>
                <div className="h-lab-text">
                  <strong>{lab.title}</strong>
                  <span>{TRACK_LABEL[lab.track] ?? lab.track}{lab.level ? ` · ${lab.level[0].toUpperCase()}${lab.level.slice(1)}` : ""}</span>
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

/*
 * The first thing on the dashboard: one clear next step, styled as a tape deck (owner, 21 November, after a
 * red-and-silver cassette design): a dark dotted panel, a bold title with a red initial, and a silver deck playing a
 * red cassette whose tape winds from the left reel to the right one as the chapter goes on. The keys work:
 * previous chapter, the lab's skill map, Continue (the red play key) and next chapter.
 */
function NextCard({ next, lab }: { next: NextStep; lab: LabDetail | null }) {
  const cont = next.kind === "continue";
  const pct = cont ? Math.round((100 * (next.step - 1)) / Math.max(1, next.steps)) : 0;
  const idx = lab?.chapters.findIndex((c) => c.id === next.chapter_id) ?? -1;
  const prev = idx > 0 ? lab!.chapters[idx - 1] : null;
  const after = lab && idx >= 0 && idx < lab.chapters.length - 1 ? lab.chapters[idx + 1] : null;
  const chapterUrl = (id: string) => `/labs/${next.lab_id}?chapter=${encodeURIComponent(id)}`;
  const title = next.lab_title;
  const tone = labTone(next.lab_id, lab?.cover_credit);
  return (
    <section className={`next-card deck-card ${cont ? "is-continue" : "is-start"}`} aria-label={cont ? "Continue where you left off" : "Start here"}
      style={deckVars(tone)}>
      <div className="next-text">
        <div className="next-kicker">{cont ? "Continue where you left off" : "Start here"}</div>
        <h1 className="next-title"><span className="deck-initial">{title.slice(0, 1)}</span>{title.slice(1)}</h1>
        <div className="next-where">
          Chapter {next.chapter_number} of {next.chapters}: {next.chapter_title}
          {cont && <> · step {next.step} of {next.steps}</>}
        </div>
        {!cont && next.reason && <p className="next-reason">{next.reason}</p>}
      </div>
      <div className="deck">
        <div className="deck-keys">
          {prev ? <Link className="deck-key" to={chapterUrl(prev.id)} aria-label={`Previous chapter: ${prev.title}`} title={prev.title}>◀◀</Link>
            : <span className="deck-key is-off" aria-hidden="true">◀◀</span>}
          <Link className="deck-key" to={`/skills/${next.lab_id}`} aria-label="Skill map" title="Skill map">■</Link>
          <Link className="deck-key deck-play next-go" to={chapterUrl(next.chapter_id)}>
            <span aria-hidden="true">▶ </span>{cont ? "Continue →" : "Start the first chapter →"}
          </Link>
          {after ? <Link className="deck-key" to={chapterUrl(after.id)} aria-label={`Next chapter: ${after.title}`} title={after.title}>▶▶</Link>
            : <span className="deck-key is-off" aria-hidden="true">▶▶</span>}
        </div>
        <div className="deck-body">
          <div className="deck-window">
            <Cassette progress={pct / 100} playing={cont} tone={tone} />
          </div>
          <div className="deck-label" role="progressbar" aria-label="Progress in this chapter" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
            <span className="deck-arrows" aria-hidden="true">⇄</span>
            <span>Chapter {String(next.chapter_number).padStart(2, "0")} / {String(next.chapters).padStart(2, "0")}</span>
            <span className={`deck-led ${cont ? "is-on" : ""}`} aria-hidden="true" />
          </div>
        </div>
      </div>
    </section>
  );
}

/** The deck's colours as CSS variables: the lab's tone, and text that reads on it. */
function deckVars(tone: string): CSSProperties {
  return { "--deck": tone, "--deck-ink": inkOn(tone), "--deck-hi": mix(tone, "#ffffff", 0.2), "--deck-lo": mix(tone, "#000000", 0.25) } as CSSProperties;
}

/** A cassette in the lab's colour: the tape winds from the left reel (to come) to the right one (done). */
function Cassette({ progress, playing, tone }: { progress: number; playing: boolean; tone: string }) {
  const shade = (t: number) => mix(tone, "#000000", t);
  const left = 9 + 13 * (1 - progress);
  const right = 9 + 13 * progress;
  const reel = (cx: number, r: number) => (
    <g>
      <circle cx={cx} cy={50} r={r} fill={shade(0.82)} />
      <circle cx={cx} cy={50} r={r} fill="none" stroke="#000" strokeOpacity=".35" />
      <g className={playing ? "deck-spin" : ""} style={{ transformOrigin: `${cx}px 50px` }}>
        <circle cx={cx} cy={50} r={8.5} fill="#e9e9ea" />
        <circle cx={cx} cy={50} r={8.5} fill="none" stroke="#9a9a9f" strokeWidth="1" />
        {[0, 60, 120, 180, 240, 300].map((a) => (
          <rect key={a} x={cx - 1.3} y={42.8} width={2.6} height={3.4} rx={0.6} fill="#8d8d93" transform={`rotate(${a} ${cx} 50)`} />
        ))}
        <circle cx={cx} cy={50} r={3} fill="#3a3a3f" />
      </g>
    </g>
  );
  return (
    <svg className="cassette" viewBox="0 0 220 112" aria-hidden="true">
      <defs>
        <linearGradient id="cas-body" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={mix(tone, "#ffffff", 0.12)} /><stop offset="1" stopColor={shade(0.3)} />
        </linearGradient>
        <linearGradient id="cas-glass" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#fff" stopOpacity=".16" /><stop offset=".45" stopColor="#fff" stopOpacity="0" />
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="216" height="108" rx="9" fill="url(#cas-body)" />
      <rect x="2" y="2" width="216" height="108" rx="9" fill="none" stroke={shade(0.62)} strokeWidth="2" />
      <rect x="14" y="12" width="192" height="66" rx="6" fill={shade(0.12)} stroke={shade(0.5)} />
      <rect x="44" y="30" width="132" height="40" rx="20" fill={shade(0.9)} />
      {reel(78, left)}
      {reel(142, right)}
      <rect x="98" y="38" width="24" height="24" rx="2" fill={shade(0.86)} stroke={shade(0.62)} />
      <path d="M 44 112 L 58 86 L 162 86 L 176 112 Z" fill={shade(0.4)} />
      {[78, 100, 120, 142].map((x) => <circle key={x} cx={x} cy={99} r={3.2} fill={shade(0.76)} />)}
      {[[10, 10], [210, 10], [10, 102], [210, 102]].map(([x, y]) => <circle key={`${x}${y}`} cx={x} cy={y} r={2.4} fill={shade(0.62)} />)}
      <rect x="2" y="2" width="216" height="108" rx="9" fill="url(#cas-glass)" />
    </svg>
  );
}

/**
 * The sidebar's long vertical rail: every chapter of the lab you are in, as a timeline. Done chapters are
 * ticked, the current one glows, upcoming ones are faint; each one opens that chapter.
 */
function NextRail({ next, lab }: { next: NextStep; lab: LabDetail }) {
  return (
    <nav className="next-rail" aria-label={`Chapters of ${lab.title}`} style={deckVars(labTone(lab.id, lab.cover_credit))}>
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
