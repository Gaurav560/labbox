import { useMemo, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import type { LabInfo, Progress } from "../api";
import { labBrand } from "../brand";
import { BrushLevel, InkProgress, Seal, TRACK_INK, TRACK_MOTIF, TrackArt } from "./UkiyoArt";

/*
 * The lab directory of the Ukiyo design: category tiles (a print, the name, how many labs) that narrow a list of lab
 * rows grouped by category. The dashboard shows it with each learner's progress; the home page shows the same
 * directory to visitors (owner, 25 November: the home page should look like the inside).
 */

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

// Labs show by category, in this order (owner, 23 November). Categories without labs yet show a quiet
// "coming soon" line; a track missing here still shows, after these.
export const CATEGORY_ORDER = ["ai", "languages", "frameworks", "system-design", "databases", "devops", "cloud", "aws", "interview"];
const UPCOMING = new Set(["cloud", "aws"]);
const LEVEL_ORDER: Record<string, number> = { beginner: 0, intermediate: 1, advanced: 2 };

/** What a row needs: the public catalog has all of it; the dashboard's labs add progress. */
export type DirectoryLab = LabInfo & { id: string; title: string; chapter_count: number; description?: string; progress?: Progress };
type Group<L> = { id: string; labs: L[] };

export function byCategory<L extends DirectoryLab>(labs: L[]): Group<L>[] {
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

/** The categories as compact tiles: a print, the name, how many labs. Picking one narrows the directory. */
export function Categories<L>({ groups, shown, onShow }: { groups: Group<L>[]; shown: string; onShow: (id: string) => void }) {
  return (
    <nav className="u-cats" aria-label="Categories" style={{ "--n": groups.length + 1 } as CSSProperties}>
      <button type="button" className="u-cat is-all" aria-pressed={shown === "all"} onClick={() => onShow("all")}>
        <span className="u-cat-art" aria-hidden="true"><img className="u-print u-labprint" src="/ukiyo/great-wave.webp" alt="" /></span>
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

/** "45 min" or "about 9 h", for visitors (who have no progress to show). */
function duration(minutes: number): string {
  return minutes < 90 ? `${minutes} min` : `about ${Math.round(minutes / 60)} h`;
}

/** One lab: its logo, title and line, level, size and (signed in) progress. The whole row is the link. */
export function LabRow({ lab, to }: { lab: DirectoryLab; to: string }) {
  const done = lab.progress?.passed_tasks ?? 0;
  const total = lab.progress?.total_tasks ?? 0;
  const finished = total > 0 && done === total;
  const brand = labBrand(lab.cover_credit);
  return (
    <li className={`u-row ${finished ? "is-done" : ""}`}>
      <Link to={to} className="u-row-link">
        <span className="u-row-logo" aria-hidden="true">
          {brand ? <img src={brand.logo} alt="" /> : <span className="u-row-mono">{lab.title.slice(0, 1)}</span>}
        </span>
        <span className="u-row-main">
          <strong className="u-row-title">{lab.title}</strong>
          <span className="u-row-line">{lab.subtitle || lab.description}</span>
        </span>
        <span className="u-row-level"><BrushLevel level={lab.level} /></span>
        <span className="u-row-size">
          {lab.chapter_count} chapter{lab.chapter_count === 1 ? "" : "s"}
          {lab.progress && <><br />{total} task{total === 1 ? "" : "s"}</>}
        </span>
        <span className="u-row-progress">
          {!lab.progress ? (lab.estimated_minutes ? <small className="muted">{duration(lab.estimated_minutes)}</small> : null)
            : finished ? <Seal lines={["✓"]} size={30} title="Finished" />
            : done ? <><InkProgress value={done / total} label={`${lab.title}: ${done} of ${total} tasks`} /><small>{done} / {total}</small></>
            : <small className="muted">Not started</small>}
        </span>
        <span className="u-row-go" aria-hidden="true">→</span>
      </Link>
    </li>
  );
}

/** Category tiles, then one ruled group of rows per category. `link` gives each row's target. */
export function Directory<L extends DirectoryLab>({ labs, link }: { labs: L[]; link: (lab: L) => string }) {
  const [shown, setShown] = useState<string>("all");
  const groups = useMemo(() => byCategory(labs), [labs]);
  return (
    <>
      <Categories groups={groups} shown={shown} onShow={setShown} />
      {groups.filter((g) => shown === "all" || g.id === shown).map((g) => (
        <section key={g.id} id={`category-${g.id}`} className="u-group" aria-label={TRACK_LABEL[g.id] ?? g.id}
          style={{ "--ink": TRACK_INK[g.id] ?? "var(--text)" } as CSSProperties}>
          <h3 className="u-group-title">
            <span className="u-group-art" aria-hidden="true"><TrackArt track={g.id} /></span>
            <span className="u-group-name">{TRACK_LABEL[g.id] ?? g.id}</span>
            <span className="u-group-count">{g.labs.length ? `${g.labs.length} lab${g.labs.length === 1 ? "" : "s"}` : "coming soon"}</span>
          </h3>
          {g.labs.length ? (
            <ol className="u-rows">
              {g.labs.map((lab) => <LabRow key={lab.id} lab={lab} to={link(lab)} />)}
            </ol>
          ) : (
            <p className="u-soon">{TRACK_LABEL[g.id] ?? g.id} labs are being written. They will appear here.</p>
          )}
        </section>
      ))}
    </>
  );
}
