import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, type LabDetail, type LabSummary, type NextStep } from "../api";
import { labBrand } from "../brand";
import { chapterNumber } from "../components/StatusBar";
import { BrushLevel, InkProgress, Seal, TRACK_INK, TRACK_MOTIF, TrackArt } from "../components/UkiyoArt";
import { useAuth } from "../auth";
import DrillCard from "../components/DrillCard";
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
  cloud: "Cloud",
  aws: "AWS",
  interview: "Interview",
};

// The dashboard shows labs by category, in this order (owner, 23 November). Categories without labs yet
// show a quiet "coming soon" line; a track missing here still shows, after these.
export const CATEGORY_ORDER = ["ai", "languages", "frameworks", "system-design", "databases", "devops", "cloud", "aws", "interview"];
const UPCOMING = new Set(["cloud", "aws"]);
const LEVEL_ORDER: Record<string, number> = { beginner: 0, intermediate: 1, advanced: 2 };

function byCategory(labs: LabSummary[]): { id: string; labs: LabSummary[] }[] {
  const ids = [...CATEGORY_ORDER, ...labs.map((l) => l.track).filter((t) => !CATEGORY_ORDER.includes(t))];
  return [...new Set(ids)]
    .map((id) => ({
      id,
      labs: labs
        .filter((l) => l.track === id)
        // Full courses first, then the short labs; beginners before advanced; then A to Z.
        .sort((a, b) => b.chapter_count - a.chapter_count
          || (LEVEL_ORDER[a.level ?? ""] ?? 9) - (LEVEL_ORDER[b.level ?? ""] ?? 9) || a.title.localeCompare(b.title)),
    }))
    .filter((g) => g.labs.length > 0 || UPCOMING.has(g.id));
}

export default function LabsPage() {
  const { user } = useAuth();
  const toast = useToast();
  const { stats } = useStats();
  const navigate = useNavigate();
  const [labs, setLabs] = useState<LabSummary[] | null>(null);
  const [next, setNext] = useState<NextStep | null>(null);
  const [nextLab, setNextLab] = useState<LabDetail | null>(null);   // the lab of the next step (chapters, track)
  const [shown, setShown] = useState<string>("all");                  // the category the directory shows

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
          {labs && <Categories groups={groups} shown={shown} onShow={setShown} />}
          {labs && groups.filter((g) => shown === "all" || g.id === shown).map((g) => (
            <section key={g.id} id={`category-${g.id}`} className="u-group" aria-label={TRACK_LABEL[g.id] ?? g.id}
              style={{ "--ink": TRACK_INK[g.id] ?? "var(--text)" } as CSSProperties}>
              <h3 className="u-group-title">
                <span className="u-group-art" aria-hidden="true"><TrackArt track={g.id} /></span>
                <span className="u-group-name">{TRACK_LABEL[g.id] ?? g.id}</span>
                <span className="u-group-count">{g.labs.length ? `${g.labs.length} lab${g.labs.length === 1 ? "" : "s"}` : "coming soon"}</span>
              </h3>
              {g.labs.length ? (
                <ol className="u-rows">
                  {g.labs.map((lab) => <LabRow key={lab.id} lab={lab} />)}
                </ol>
              ) : (
                <p className="u-soon">{TRACK_LABEL[g.id] ?? g.id} labs are being written. They will appear here.</p>
              )}
            </section>
          ))}
        </section>
      </main>
    </div>
  );
}

function greeting(): string {
  const h = new Date().getHours();
  return h < 5 ? "Working late" : h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
}

/** The categories as compact tiles: a print, the name, how many labs. Picking one narrows the directory. */
function Categories({ groups, shown, onShow }: { groups: { id: string; labs: LabSummary[] }[]; shown: string; onShow: (id: string) => void }) {
  return (
    <nav className="u-cats" aria-label="Categories" style={{ "--n": groups.length + 1 } as CSSProperties}>
      <button type="button" className="u-cat is-all" aria-pressed={shown === "all"} onClick={() => onShow("all")}>
        <span className="u-cat-name">All labs</span>
        <span className="u-cat-count">{groups.reduce((n, g) => n + g.labs.length, 0)}</span>
      </button>
      {groups.map((g) => (
        <button type="button" key={g.id} className={`u-cat ${g.labs.length ? "" : "is-soon"}`} aria-pressed={shown === g.id}
          onClick={() => onShow(shown === g.id ? "all" : g.id)} style={{ "--ink": TRACK_INK[g.id] ?? "var(--text)" } as CSSProperties}>
          <span className="u-cat-art" aria-hidden="true"><TrackArt track={g.id} /></span>
          <span className="u-cat-name">{TRACK_LABEL[g.id] ?? g.id}</span>
          <span className="u-cat-count">{g.labs.length || "soon"}</span>
          <span className="u-cat-motif">{TRACK_MOTIF[g.id] ?? ""}</span>
        </button>
      ))}
    </nav>
  );
}

/** One lab in the directory: its logo, title and line, level, size and progress. The whole row opens the course. */
function LabRow({ lab }: { lab: LabSummary }) {
  const { passed_tasks: done, total_tasks: total } = lab.progress;
  const finished = total > 0 && done === total;
  const brand = labBrand(lab.cover_credit);
  return (
    <li className={`u-row ${finished ? "is-done" : ""}`}>
      <Link to={`/courses/${lab.id}`} className="u-row-link">
        <span className="u-row-logo" aria-hidden="true">
          {brand ? <img src={brand.logo} alt="" /> : <span className="u-row-mono">{lab.title.slice(0, 1)}</span>}
        </span>
        <span className="u-row-main">
          <strong className="u-row-title">{lab.title}</strong>
          <span className="u-row-line">{lab.subtitle || lab.description}</span>
        </span>
        <span className="u-row-level"><BrushLevel level={lab.level} /></span>
        <span className="u-row-size">{lab.chapter_count} chapter{lab.chapter_count === 1 ? "" : "s"}<br />{total} task{total === 1 ? "" : "s"}</span>
        <span className="u-row-progress">
          {finished ? <Seal lines={["✓"]} size={30} title="Finished" />
            : done ? <><InkProgress value={done / total} label={`${lab.title}: ${done} of ${total} tasks`} /><small>{done} / {total}</small></>
            : <small className="muted">Not started</small>}
        </span>
        <span className="u-row-go" aria-hidden="true">→</span>
      </Link>
    </li>
  );
}

/**
 * The first thing on the dashboard: one clear next step, as an editorial feature. The category's print on one side;
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
        <TrackArt track={track} />
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
