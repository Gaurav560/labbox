import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type LabDetail } from "../api";
import { useAuth } from "../auth";
import MetroMap, { lineColor, type MetroLine, type Station } from "../components/MetroMap";
import { chapterNumber } from "../components/StatusBar";
import StatsBadges from "../components/StatsBadges";
import ThemeButton from "../components/ThemeButton";
import { LogoMark } from "../components/Logo";

/** One lab's metro map: every course part a line, every chapter a station; you are at the first chapter not done. */
export default function LabMapPage() {
  const { labId = "" } = useParams();
  const { user } = useAuth();
  const [lab, setLab] = useState<LabDetail | null>(null);
  useEffect(() => {
    api.lab(labId).then(setLab).catch(() => setLab(null));
  }, [labId]);

  const lines: MetroLine[] = useMemo(() => {
    if (!lab) return [];
    const done = (i: number) => lab.chapters[i].tasks.length > 0 && lab.chapters[i].tasks.every((t) => t.passed);
    const now = lab.chapters.findIndex((_, i) => !done(i));
    const out: MetroLine[] = [];
    lab.chapters.forEach((c, i) => {
      const passed = c.tasks.filter((t) => t.passed).length;
      const st: Station = {
        id: c.id,
        number: String(chapterNumber(lab.chapters, i)).padStart(2, "0"),
        title: c.title,
        topics: c.topics?.map((t) => ({ title: t.title, href: `/labs/${lab.id}?chapter=${encodeURIComponent(c.id)}&step=${t.step}` })),
        meta: `${passed} of ${c.tasks.length} task${c.tasks.length === 1 ? "" : "s"}${c.minutes ? ` · ${c.minutes} min` : ""}`,
        state: done(i) ? "done" : i === now ? "now" : "open",
        href: `/labs/${lab.id}?chapter=${encodeURIComponent(c.id)}`,
      };
      // A chapter with a part starts that line; chapters without one stay on the current line.
      if (!out.length || (c.part && c.part !== out[out.length - 1].name)) out.push({ name: c.part || lab.title, stations: [] });
      out[out.length - 1].stations.push(st);
    });
    return out;
  }, [lab]);
  const items = lines.flatMap((l) => l.stations);
  const doneCount = items.filter((i) => i.state === "done").length;
  const pct = items.length ? Math.round((100 * doneCount) / items.length) : 0;
  const current = items.find((i) => i.state === "now");

  return (
    <div className="map-page">
      <header className="topbar">
        <Link to="/" className="logo" aria-label="LabBox by Telusko home"><LogoMark size={24} /></Link>
        <Link to="/skills" className="link">← Skill maps</Link>
        <span className="brand">{lab?.title ?? labId}</span>
        <span className="spacer" />
        <ThemeButton />
        <StatsBadges username={user?.username ?? ""} />
      </header>
      {lab && (
        <main className="map-main">
          <section className="map-hero">
            <div className="map-ring" style={{ ["--pct" as string]: `${pct}` }} aria-label={`${pct}% done`}>
              <span>{pct}%</span>
            </div>
            <div className="map-hero-text">
              <div className="map-kicker">Metro map</div>
              <h1>{lab.title}</h1>
              <p className="muted">{doneCount} of {items.length} chapters done{current ? ` · next: ${current.title}` : ""}</p>
            </div>
            {current?.href && <Link className="btn btn-primary map-continue" to={current.href}>Continue →</Link>}
          </section>
          {lines.length > 1 && (
            <ul className="metro-legend" aria-label="Lines">
              {lines.map((l, i) => (
                <li key={l.name} style={{ ["--c" as string]: lineColor(i) }}>
                  <span className="metro-legend-bar" />{l.name}
                  <span className="muted">{l.stations.filter((s) => s.state === "done").length}/{l.stations.length}</span>
                </li>
              ))}
            </ul>
          )}
          <MetroMap lines={lines} />
        </main>
      )}
    </div>
  );
}
