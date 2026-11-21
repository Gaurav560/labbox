import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type LabSummary, type TrackSummary } from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import StatsBadges from "../components/StatsBadges";
import ThemeButton from "../components/ThemeButton";

/*
 * The Skill maps section (owner, 21 November: "keep a skill map section entirely separate, for each lab"):
 * every lab has its own roadmap (each chapter a step), and every track has one too (each topic a step).
 */
export default function SkillsPage() {
  const { user, logout } = useAuth();
  const [labs, setLabs] = useState<LabSummary[] | null>(null);
  const [tracks, setTracks] = useState<TrackSummary[]>([]);
  useEffect(() => {
    api.labs().then(setLabs).catch(() => setLabs([]));
    api.tracks().then(setTracks).catch(() => setTracks([]));
  }, []);
  return (
    <div className="skills-page">
      <header className="topbar">
        <Logo to="/" />
        <Link to="/labs" className="link">Labs</Link>
        <span className="brand">Skill maps</span>
        <span className="spacer" />
        <ThemeButton />
        <StatsBadges username={user?.username ?? ""} />
        <button className="btn btn-small" onClick={logout}>Log out</button>
      </header>
      <main className="skills-main">
        <section className="skills-hero">
          <div className="skills-kicker">Skill maps</div>
          <h1>See the whole road, then take the next step.</h1>
          <p>Every lab is a roadmap, one step per chapter. Open one to see what you have done, where you are, and what comes next.</p>
        </section>
        <h2>Labs</h2>
        <div className="skills-grid">
          {labs?.map((l) => {
            const pct = l.progress.total_tasks ? Math.round((100 * l.progress.passed_tasks) / l.progress.total_tasks) : 0;
            return (
              <Link key={l.id} to={`/skills/${l.id}`} className="skill-card">
                <div className="skill-card-img">{l.cover_url ? <img src={l.cover_url} alt="" loading="lazy" /> : null}</div>
                <div className="skill-card-text">
                  <strong>{l.title}</strong>
                  <span>{l.chapter_count} {l.chapter_count === 1 ? "chapter" : "chapters"} · {pct}% done</span>
                  <div className="skill-card-bar"><div style={{ width: `${pct}%` }} /></div>
                </div>
              </Link>
            );
          })}
        </div>
        {tracks.length > 0 && <h2>Tracks</h2>}
        <div className="skills-grid">
          {tracks.map((t) => (
            <Link key={t.track} to={`/tracks/${t.track}`} className="skill-card skill-card-track">
              <div className="skill-card-text">
                <strong>{t.title}</strong>
                <span>{t.nodes} topics across labs · {t.done} done</span>
                <div className="skill-card-bar"><div style={{ width: `${t.nodes ? (100 * t.done) / t.nodes : 0}%` }} /></div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
