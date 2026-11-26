import { Link } from "react-router-dom";
import { useEffect, useRef, useState, type CSSProperties } from "react";
import { useAuth } from "../auth";
import { useStats } from "../stats";

/*
 * The top bars' profile button (owner, 22 November: level, streak and stars go in a profile section; an Exit
 * button instead of "Log out"). The button is the learner's initial in a ring that fills towards the next level;
 * it opens the profile: level and XP to the next, the streak and best streak, total stars, today's streak goal,
 * and Exit (signs out).
 */
export default function ProfileMenu({ username }: { username: string }) {
  const { stats } = useStats();
  const { logout } = useAuth();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const away = (e: MouseEvent) => { if (!ref.current?.contains(e.target as Node)) setOpen(false); };
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", away);
    document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("mousedown", away); document.removeEventListener("keydown", esc); };
  }, [open]);

  const span = stats ? Math.max(1, stats.next_level_xp - stats.level_xp) : 1;
  const pct = stats ? Math.min(100, Math.max(0, Math.round((100 * (stats.xp_total - stats.level_xp)) / span))) : 0;
  const todayDone = !!stats && stats.today_xp >= stats.streak_min_xp;
  const initial = (username.trim()[0] ?? "?").toUpperCase();

  return (
    <div className="ts-wrap profile-wrap" ref={ref}>
      <button className="profile-btn" onClick={() => setOpen((o) => !o)} aria-expanded={open} aria-haspopup="dialog"
        aria-label={`Profile: ${username}`} title="Profile" style={{ "--pct": pct } as CSSProperties}>
        <span className="profile-avatar">{initial}</span>
      </button>
      {open && (
        <div className="ts-pop profile-pop" role="dialog" aria-label="Profile">
          <div className="profile-head">
            <span className="profile-avatar profile-avatar-big">{initial}</span>
            <div>
              <strong>{username}</strong>
              {stats && <span className="level-badge" aria-label={`Level ${stats.level}`}>Level {stats.level}</span>}
            </div>
          </div>
          {stats && (
            <>
              <div className="profile-level">
                <div className="profile-bar"><div style={{ width: `${pct}%` }} /></div>
                <span>{stats.next_level_xp - stats.xp_total} XP to level {stats.level + 1}</span>
              </div>
              <div className="profile-stats">
                <div className={`profile-stat ${todayDone ? "is-lit" : ""}`}>
                  <span className="stat stat-streak" aria-label={`${stats.streak_current} day streak`}>{stats.streak_current}</span>
                  <small>day streak</small>
                  <small className="profile-best">best {stats.streak_best}</small>
                </div>
                <div className="profile-stat">
                  <span className="stat stat-xp" aria-label={`${stats.xp_total} XP`}>{stats.xp_total}</span>
                  <small>stars (XP)</small>
                </div>
              </div>
              <p className="profile-today">
                {todayDone
                  ? "Today counts for your streak already."
                  : `Earn ${stats.streak_min_xp - stats.today_xp} more XP today to keep your streak.`}
                {!todayDone && stats.freeze_available ? " One streak freeze left this week." : ""}
              </p>
            </>
          )}
          <Link className="profile-link" to="/certificates" onClick={() => setOpen(false)}>
            <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="9" r="6" /><path d="M8.5 14 7 22l5-3 5 3-1.5-8" />
            </svg>
            My certificates
          </Link>
          <button className="profile-exit" onClick={() => { setOpen(false); logout(); }}>
            <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><path d="M16 17l5-5-5-5" /><path d="M21 12H9" />
            </svg>
            Exit
          </button>
        </div>
      )}
    </div>
  );
}
