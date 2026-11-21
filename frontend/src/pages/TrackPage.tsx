import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type SkillMap } from "../api";
import { useAuth } from "../auth";
import { LogoMark } from "../components/Logo";
import MetroMap, { type MetroLine, type Station } from "../components/MetroMap";
import ProfileMenu from "../components/ProfileMenu";
import ThemeButton from "../components/ThemeButton";
import { useToast } from "../components/Toasts";

/*
 * A track's metro map: its topics in learning order (prerequisites first) as stations, in stages of a few topics
 * each (one line per stage). Choosing a station shows that topic's lab chapters below the map, each opening its lab.
 */

const STATE_LABEL = { done: "✓ Done", available: "Start", locked: "Locked", coming_soon: "Coming soon" } as const;
const PER_STAGE = 6;

export default function TrackPage() {
  const { track = "" } = useParams();
  const { user } = useAuth();
  const toast = useToast();
  const [map, setMap] = useState<SkillMap | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  useEffect(() => {
    setSelected(null);
    api.skills(track).then(setMap).catch((e) => toast(e.message));
  }, [track, toast]);

  const sorted = useMemo(() => {
    const nodes = map?.nodes ?? [];
    const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
    const depth: Record<string, number> = {};
    const req = (id: string) => byId[id].requires.filter((r) => byId[r]);
    const depthOf = (id: string): number => (depth[id] ??= req(id).length ? 1 + Math.max(...req(id).map(depthOf)) : 0);
    return nodes.map((n, i) => ({ n, d: depthOf(n.id), i })).sort((a, b) => a.d - b.d || a.i - b.i).map((x) => x.n);
  }, [map]);

  const lines: MetroLine[] = useMemo(() => {
    const firstOpen = sorted.findIndex((n) => n.state === "available");
    const stations: Station[] = sorted.map((n, i) => ({
      id: n.id,
      number: String(i + 1).padStart(2, "0"),
      title: n.title,
      topics: n.chapters.map((c) => ({ title: `${c.done ? "✓ " : ""}${c.title}`, href: `/labs/${c.lab_id}?chapter=${encodeURIComponent(c.chapter_id)}` })),
      meta: `${STATE_LABEL[n.state]} · ${n.chapters.length} chapter${n.chapters.length === 1 ? "" : "s"}`,
      state: n.state === "done" ? "done" : n.state === "coming_soon" ? "soon" : n.state === "locked" ? "locked" : i === firstOpen ? "now" : "open",
    }));
    const out: MetroLine[] = [];
    for (let k = 0; k < stations.length; k += PER_STAGE) out.push({ name: `Stage ${out.length + 1}`, stations: stations.slice(k, k + PER_STAGE) });
    return out;
  }, [sorted]);

  const current = lines.flatMap((l) => l.stations).find((s) => s.state === "now");
  const shown = sorted.find((n) => n.id === (selected ?? current?.id)) ?? sorted[0];
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
        <ProfileMenu username={user?.username ?? ""} />
      </header>
      {map && (
        <main className="map-main" aria-label="Skill map">
          <section className="map-hero">
            <div className="map-ring" style={{ ["--pct" as string]: `${total ? Math.round((100 * done) / total) : 0}` }}>
              <span>{done}/{total}</span>
            </div>
            <div className="map-hero-text">
              <div className="map-kicker">Track metro map</div>
              <h1>{map.title}</h1>
              <p className="muted">Choose a station to see the lab chapters that teach it.</p>
            </div>
          </section>
          <MetroMap lines={lines} selected={shown?.id} onSelect={setSelected} />
          {shown && (
            <section className="metro-panel" aria-label={shown.title}>
              <div className="map-kicker">{STATE_LABEL[shown.state]}</div>
              <h2>{shown.title}</h2>
              {shown.chapters.length === 0 ? (
                <p className="muted">This topic is coming soon.</p>
              ) : (
                <ul className="metro-chapters">
                  {shown.chapters.map((c) => (
                    <li key={`${c.lab_id}/${c.chapter_id}`} className={c.done ? "is-done" : ""}>
                      <Link to={`/labs/${c.lab_id}?chapter=${encodeURIComponent(c.chapter_id)}`} aria-label={`Open ${c.title}`}>
                        <span className="muted small-text">{c.lab_title}{c.number !== undefined ? ` · Ch ${c.number}` : ""}</span>
                        <span className="metro-ch-title">{c.done ? "✓ " : ""}{c.title}</span>
                        <span className="metro-open-link">Open →</span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          )}
          <ul className="sr-only" aria-label="Skills">
            {map.nodes.map((n) => <li key={n.id} className="skill-node">{n.title}: {STATE_LABEL[n.state]}</li>)}
          </ul>
        </main>
      )}
    </div>
  );
}
