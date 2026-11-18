import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, type LabSummary, type TrackSummary } from "../api";
import { useAuth } from "../auth";
import DrillCard from "../components/DrillCard";
import LabCover from "../components/LabCover";
import StatsBadges from "../components/StatsBadges";
import Logo from "../components/Logo";
import { useToast } from "../components/Toasts";
import { useStats } from "../stats";

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
  const [tracks, setTracks] = useState<TrackSummary[]>([]);

  useEffect(() => {
    api.labs().then(setLabs).catch((e) => toast(e.message));
    api.tracks().then(setTracks).catch(() => {});
  }, [toast]);

  // Brand new learners start with the 60 second onboarding.
  useEffect(() => {
    if (stats?.needs_onboarding) navigate("/welcome", { replace: true });
  }, [stats, navigate]);

  return (
    <div className="labs-page">
      <header className="topbar">
        <Logo to="/" />
        <span className="spacer" />
        <StatsBadges username={user?.username ?? ""} />
        <button className="btn btn-small" onClick={logout}>Log out</button>
      </header>
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
            {tracks.map((t) => (
              <Link key={t.track} to={`/tracks/${t.track}`} className="track-link">
                <span className="big-number">{t.done}/{t.nodes}</span>
                <span className="muted small-text">{t.title} skill map →</span>
              </Link>
            ))}
          </section>
        )}
        <DrillCard />
        <h2>Your labs</h2>
        {!labs && <p className="muted">Loading...</p>}
        <div className="lab-grid">
          {labs?.map((lab) => {
            const pct = lab.progress.total_tasks ? (100 * lab.progress.passed_tasks) / lab.progress.total_tasks : 0;
            return (
              <div key={lab.id} className="lab-card">
                <LabCover id={lab.id} title={lab.title} track={lab.track} tags={lab.tags} coverUrl={lab.cover_url} />
                <div className="lab-card-body">
                  <h3>{lab.title}</h3>
                  <p className="muted">{lab.subtitle || lab.description}</p>
                  <div className="lab-meta">
                    <span className="meta-chip">{TRACK_LABEL[lab.track] ?? lab.track}</span>
                    {lab.level && <span className="meta-chip meta-chip-cap">{lab.level}</span>}
                    {lab.estimated_minutes && <span className="meta-chip">{lab.estimated_minutes} min</span>}
                  </div>
                  <div className="progress" title={`${lab.progress.passed_tasks} of ${lab.progress.total_tasks} tasks`}>
                    <div className="progress-fill" style={{ width: `${pct}%` }} />
                  </div>
                  <div className="row">
                    <span className="muted small">
                      {lab.progress.passed_tasks} / {lab.progress.total_tasks} tasks · {lab.chapter_count} chapter{lab.chapter_count === 1 ? "" : "s"}
                    </span>
                    <Link className="btn btn-primary" to={`/labs/${lab.id}`}>Open</Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
