// The learner's XP, level and streak, shared by every page. Also sends the browser's timezone once.
import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type Stats, type XpAward } from "./api";
import { useAuth } from "./auth";
import { useToast } from "./components/Toasts";

interface StatsState {
  stats: Stats | null;
  refresh: () => Promise<Stats | null>;
  /** Show "+20 XP" for awards that just happened, then refresh the numbers. */
  celebrate: (awards: XpAward[] | undefined) => void;
}

const StatsContext = createContext<StatsState>({ stats: null, refresh: async () => null, celebrate: () => {} });

function browserTimezone(): string | null {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || null;
  } catch {
    return null;
  }
}

export function StatsProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const toast = useToast();
  const [stats, setStats] = useState<Stats | null>(null);

  const refresh = useCallback(async () => {
    try {
      const s = await api.stats();
      setStats(s);
      return s;
    } catch {
      return null; // the badges just stay as they were
    }
  }, []);

  useEffect(() => {
    if (!user) {
      setStats(null);
      return;
    }
    refresh().then((s) => {
      const tz = browserTimezone();
      // Days for streaks are counted in the learner's timezone; set it the first time we see them.
      if (s && !s.timezone && tz) api.saveProfile({ timezone: tz }).then(refresh).catch(() => {});
    });
  }, [user, refresh]);

  const celebrate = useCallback(
    (awards: XpAward[] | undefined) => {
      if (!awards?.length) return;
      const total = awards.reduce((n, a) => n + a.amount, 0);
      const what = awards.map((a) => a.label).filter(Boolean).join(" · ");
      toast(`+${total} XP${what ? `  ${what}` : ""}`, "info");
      refresh();
    },
    [toast, refresh],
  );

  return <StatsContext.Provider value={{ stats, refresh, celebrate }}>{children}</StatsContext.Provider>;
}

export const useStats = () => useContext(StatsContext);
