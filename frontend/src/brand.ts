// Each lab's main technology, from its cover credit ("Logos: redis,python"), and that brand's colour
// (the same colours as tools/logo_cover.py). Used for the faint logo behind the lesson.
const COLORS: Record<string, string> = {
  python: "#3776AB", java: "#f89820", "duke-waving": "#f89820", "duke-thumbsup": "#f89820",
  fastapi: "#009688", spring: "#6DB33F", postgresql: "#336791", sql: "#6366f1", go: "#00ADD8",
  javascript: "#F7DF1E", express: "#8a8a8a", redis: "#DC382D", nodejs: "#5FA04E",
  typescript: "#3178C6", linux: "#FCC624", git: "#F05033", docker: "#2496ED", kubernetes: "#326CE5",
  nginx: "#009639", mysql: "#00758F", mongodb: "#47A248",
};

export function labBrand(coverCredit: { by?: string } | null | undefined): { logo: string; color: string } | null {
  const m = /Logos:\s*([\w-]+)/.exec(coverCredit?.by ?? "");
  if (!m || !COLORS[m[1]]) return null;
  return { logo: `/logos/${m[1]}.svg`, color: COLORS[m[1]] };
}
