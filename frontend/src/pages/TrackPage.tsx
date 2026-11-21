import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type SkillMap } from "../api";
import { useAuth } from "../auth";
import { LogoMark } from "../components/Logo";
import Roadmap, { type RoadItem } from "../components/Roadmap";
import StatsBadges from "../components/StatsBadges";
import ThemeButton from "../components/ThemeButton";
import { useToast } from "../components/Toasts";

/*
 * A track's roadmap: its topics in learning order (prerequisites first), each card listing the lab chapters that
 * teach it, each chapter opening its lab.
 */

const STATE_LABEL = { done: "✓ Done", available: "Start", locked: "Locked", coming_soon: "Coming soon" } as const;

export default function TrackPage() {
  const { track = "" } = useParams();
  const { user } = useAuth();
  const toast = useToast();
  const [map, setMap] = useState<SkillMap | null>(null);
  useEffect(() => {
    api.skills(track).then(setMap).catch((e) => toast(e.message));
  }, [track, toast]);

  const items: RoadItem[] = useMemo(() => {
    const nodes = map?.nodes ?? [];
    const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
    const depth: Record<string, number> = {};
    const req = (id: string) => byId[id].requires.filter((r) => byId[r]);
    const depthOf = (id: string): number => (depth[id] ??= req(id).length ? 1 + Math.max(...req(id).map(depthOf)) : 0);
    const sorted = nodes.map((n, i) => ({ n, d: depthOf(n.id), i })).sort((a, b) => a.d - b.d || a.i - b.i).map((x) => x.n);
    const firstOpen = sorted.findIndex((n) => n.state === "available");
    return sorted.map((n, i): RoadItem => ({
      id: n.id,
      number: String(i + 1).padStart(2, "0"),
      title: n.title,
      meta: `${n.chapters.length} chapter${n.chapters.length === 1 ? "" : "s"}`,
      state: n.state === "done" ? "done" : n.state === "coming_soon" ? "soon" : n.state === "locked" ? "locked" : i === firstOpen ? "now" : "open",
      children: n.chapters.length ? (
        <ul className="road-chapters">
          {n.chapters.map((c) => (
            <li key={`${c.lab_id}/${c.chapter_id}`} className={c.done ? "is-done" : ""}>
              <Link to={`/labs/${c.lab_id}?chapter=${encodeURIComponent(c.chapter_id)}`} aria-label={`Open ${c.title}`}>
                <span className="road-ch-where">{c.lab_title}{c.number !== undefined ? ` · Ch ${c.number}` : ""}</span>
                <span className="road-ch-title">{c.done ? "✓ " : ""}{c.title}</span>
              </Link>
            </li>
          ))}
        </ul>
      ) : undefined,
    }));
  }, [map]);
  const done = map?.nodes.filter((n) => n.state === "done").length ?? 0;
  const total = map?.nodes.length ?? 0;

  return (
    <div className="map-page">
      <header className="topbar">
        <Link to="/" className="logo" aria-label="LabBox by Telusko home"><LogoMark size={24} /></Link>
        <Link to="/skills" className="link">← Skill maps</Link>
        <span className="brand">{map?.title ?? track}</span>
        {map && <span className="muted small-text">{done} of {total} skills</span>}
        <span className="spacer" />
        <ThemeButton />
        <StatsBadges username={user?.username ?? ""} />
      </header>
      {map && (
        <main className="map-main" aria-label="Skill map">
          <section className="map-hero">
            <div className="map-ring" style={{ ["--pct" as string]: `${total ? Math.round((100 * done) / total) : 0}` }}>
              <span>{done}/{total}</span>
            </div>
            <div className="map-hero-text">
              <div className="map-kicker">Track roadmap</div>
              <h1>{map.title}</h1>
              <p className="muted">Each topic lists the lab chapters that teach it.</p>
            </div>
          </section>
          <Roadmap items={items} />
          <ul className="sr-only" aria-label="Skills">
            {map.nodes.map((n) => <li key={n.id} className="skill-node">{n.title}: {STATE_LABEL[n.state]}</li>)}
          </ul>
        </main>
      )}
    </div>
  );
}
