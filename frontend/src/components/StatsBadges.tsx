import { useStats } from "../stats";

// 🔥 streak, ⭐ XP and the level badge, for the top bars.
export default function StatsBadges({ username }: { username: string }) {
  const { stats } = useStats();
  return (
    <span className="stats-badges">
      {stats && (
        <>
          <span
            className={`stat stat-streak ${stats.today_xp >= stats.streak_min_xp ? "stat-today-done" : ""}`}
            title={
              stats.today_xp >= stats.streak_min_xp
                ? `Streak: ${stats.streak_current} days. Today counts already.`
                : `Streak: ${stats.streak_current} days. Earn ${stats.streak_min_xp - stats.today_xp} more XP today to keep it.` +
                  (stats.freeze_available ? " One streak freeze left this week." : "")
            }
            aria-label={`${stats.streak_current} day streak`}
          >
            🔥 {stats.streak_current}
          </span>
          <span className="stat stat-xp" title={`${stats.xp_total} XP in total`} aria-label={`${stats.xp_total} XP`}>
            ⭐ {stats.xp_total}
          </span>
        </>
      )}
      <span className="user-chip">
        {stats && (
          <span
            className="level-badge"
            title={`Level ${stats.level}: ${stats.next_level_xp - stats.xp_total} XP to level ${stats.level + 1}`}
            aria-label={`Level ${stats.level}`}
          >
            Lv {stats.level}
          </span>
        )}
        <span className="muted small-text">{username}</span>
      </span>
    </span>
  );
}
