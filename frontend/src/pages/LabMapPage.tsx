import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type LabDetail } from "../api";
import { useAuth } from "../auth";
import Roadmap, { type RoadItem } from "../components/Roadmap";
import { chapterNumber } from "../components/StatusBar";
import StatsBadges from "../components/StatsBadges";
import ThemeButton from "../components/ThemeButton";
import { LogoMark } from "../components/Logo";

/** One lab's roadmap: every chapter a step; you are at the first chapter not done yet. */
export default function LabMapPage() {
  const { labId = "" } = useParams();
  const { user } = useAuth();
  const [lab, setLab] = useState<LabDetail | null>(null);
  useEffect(() => {
    api.lab(labId).then(setLab).catch(() => setLab(null));
  }, [labId]);

  const items: RoadItem[] = useMemo(() => {
    if (!lab) return [];
    const done = (i: number) => lab.chapters[i].tasks.length > 0 && lab.chapters[i].tasks.every((t) => t.passed);
    const now = lab.chapters.findIndex((_, i) => !done(i));
    return lab.chapters.map((c, i) => {
      const passed = c.tasks.filter((t) => t.passed).length;
      return {
        id: c.id,
        number: String(chapterNumber(lab.chapters, i)).padStart(2, "0"),
        title: c.title,
        meta: `${passed} of ${c.tasks.length} task${c.tasks.length === 1 ? "" : "s"}${c.minutes ? ` · ${c.minutes} min` : ""}`,
        state: done(i) ? "done" : i === now ? "now" : "open",
        href: `/labs/${lab.id}?chapter=${encodeURIComponent(c.id)}`,
      };
    });
  }, [lab]);
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
              <div className="map-kicker">Roadmap</div>
              <h1>{lab.title}</h1>
              <p className="muted">{doneCount} of {items.length} chapters done{current ? ` · next: ${current.title}` : ""}</p>
            </div>
            {current?.href && <Link className="btn btn-primary map-continue" to={current.href}>Continue →</Link>}
          </section>
          <Roadmap items={items} />
        </main>
      )}
    </div>
  );
}
