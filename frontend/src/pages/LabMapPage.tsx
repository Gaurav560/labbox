import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type LabDetail } from "../api";
import { useAuth } from "../auth";
import MetroMap, { labLines, MetroLegend, type MetroLine } from "../components/MetroMap";
import ProfileMenu from "../components/ProfileMenu";
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

  const lines: MetroLine[] = useMemo(() => (lab ? labLines(lab) : []), [lab]);
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
        <ProfileMenu username={user?.username ?? ""} />
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
          <MetroLegend lines={lines} />
          <MetroMap lines={lines} />
        </main>
      )}
    </div>
  );
}
