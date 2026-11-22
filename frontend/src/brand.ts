// Each lab's main technology, from its cover credit ("Logos: redis,python"), and that brand's colour
// (the same colours as tools/logo_cover.py). Used for the faint logo behind the lesson.
const COLORS: Record<string, string> = {
  python: "#3776AB", java: "#f89820", "duke-waving": "#f89820", "duke-thumbsup": "#f89820",
  fastapi: "#009688", spring: "#6DB33F", "spring-ai": "#7eb050", postgresql: "#336791", sql: "#6366f1", go: "#00ADD8",
  javascript: "#F7DF1E", express: "#8a8a8a", redis: "#DC382D", nodejs: "#5FA04E",
  typescript: "#3178C6", linux: "#FCC624", git: "#F05033", docker: "#2496ED", kubernetes: "#326CE5",
  nginx: "#009639", mysql: "#00758F", mongodb: "#47A248",
};

export function labBrand(coverCredit: { by?: string } | null | undefined): { logo: string; color: string } | null {
  const m = /Logos:\s*([\w-]+)/.exec(coverCredit?.by ?? "");
  if (!m || !COLORS[m[1]]) return null;
  return { logo: `/logos/${m[1]}.svg`, color: COLORS[m[1]] };
}

// Each lab's colour on a dark surface: its cover's brand colour, but dark ones (navy Java, grey Linux)
// use their bright accent so they still show. The home page screenshot glow, the dashboard's tape deck
// and the course pages use it.
export const LAB_TONES: Record<string, string> = {
  "express-api": "#8b949e",
  "fastapi-first-api": "#009688",
  "git-without-fear": "#F05033",
  "go-basics": "#00ADD8",
  "java-basics": "#f89820",
  "java-collections": "#f89820",
  "javascript-basics": "#F7DF1E",
  "javascript-inside-out": "#F7DF1E",
  "linux-on-call": "#FCC624",
  "postgres-indexing-incident": "#4a8fd1",
  "postgres-transactions-and-locks": "#4a8fd1",
  "python-basics": "#4b8bbe",
  "python-collections": "#4b8bbe",
  "rate-limiter": "#00b347",
  "redis-in-practice": "#DC382D",
  "spring-ai": "#7eb050",
  "spring-boot-first-api": "#6DB33F",
  "sql-from-zero": "#6366f1",
};

/** The dashboard's Continue picture (owner, 22 November): a retro computer for labs where you write code
 *  (languages, frameworks, AI), the cassette for the rest (databases, DevOps, system design). */
export function labDeck(track: string | undefined): "computer" | "cassette" {
  return track === "languages" || track === "frameworks" || track === "ai" ? "computer" : "cassette";
}

/** A lab's colour: its own tone, else its cover's brand colour, else the LabBox red. */
export function labTone(labId: string, coverCredit?: { by?: string } | null): string {
  return LAB_TONES[labId] ?? labBrand(coverCredit)?.color ?? "#e50914";
}

/** Mix two #rrggbb colours: t = 0 gives a, 1 gives b. */
export function mix(a: string, b: string, t: number): string {
  const p = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const [x, y] = [p(a), p(b)];
  return `#${x.map((v, i) => Math.round(v + (y[i] - v) * t).toString(16).padStart(2, "0")).join("")}`;
}

/** Text that reads on a tone: dark on bright tones (yellow Linux, JavaScript), white on the rest. */
export function inkOn(tone: string): string {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(tone.slice(i, i + 2), 16) / 255).map((c) => (c <= 0.04 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.4 ? "#16130a" : "#fff";
}
