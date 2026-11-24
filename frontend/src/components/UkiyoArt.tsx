/*
 * The Ukiyo artwork (owner, 24 November): original illustrations in the manner of Japanese woodblock prints,
 * one per category, drawn as SVG so they are sharp at every size, load with the page and cost nothing.
 * Flat colour blocks, an ink outline where it helps, and a faint paper grain, like a printed sheet.
 *   AI and Languages: pictures the owner chose (see TRACK_IMAGES below)
 *   Frameworks: bamboo                             Databases: a river through layered hills
 *   DevOps: geometric mountains and terraces       System design: a red arched bridge
 *   Cloud (coming soon): scrolling clouds
 * Also the small signature pieces: the seal, the brush-mark level, and the ink progress line.
 */
import { useId, type ReactNode } from "react";

const PAPER = "#efe5cf";
const INK = "#1b2533";

/** One print: paper, the picture, then a grain over everything. */
function Print({ children, label, bg = PAPER }: { children: (id: string) => ReactNode; label?: string; bg?: string }) {
  const id = useId().replace(/:/g, "");
  return (
    <svg className="u-print" viewBox="0 0 400 240" preserveAspectRatio="xMidYMid slice" role={label ? "img" : undefined}
      aria-label={label} aria-hidden={label ? undefined : true}>
      <defs>
        <filter id={`${id}-grain`} x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="3" />
          <feColorMatrix values="0 0 0 0 .2  0 0 0 0 .15  0 0 0 0 .1  0 0 0 .55 -.18" />
          <feComposite in2="SourceGraphic" operator="in" />
        </filter>
        <clipPath id={`${id}-frame`}><rect width="400" height="240" /></clipPath>
      </defs>
      <g clipPath={`url(#${id}-frame)`}>
        <rect width="400" height="240" fill={bg} />
        {children(id)}
        <rect width="400" height="240" fill="#000" filter={`url(#${id}-grain)`} />
      </g>
    </svg>
  );
}



function FrameworksPrint() {
  const stalks = [
    { x: 64, w: 15, c: "#4f6e3f" }, { x: 118, w: 11, c: "#6f8f58" }, { x: 214, w: 17, c: "#3f5c33" },
    { x: 276, w: 12, c: "#6f8f58" }, { x: 338, w: 15, c: "#4f6e3f" },
  ];
  const leaf = (x: number, y: number, a: number, s: number, c: string, k: number) => (
    <path key={k} d="M0 0 C 10 -6, 34 -6, 52 0 C 34 5, 10 5, 0 0 Z" fill={c} transform={`translate(${x} ${y}) rotate(${a}) scale(${s * 1.55})`} />
  );
  return (
    <Print bg="#e9e6d2">{() => (
      <>
        <rect width="400" height="240" fill="#e3e3cc" />
        <circle cx="300" cy="70" r="40" fill="#f4f0e2" />
        {/* mist bands */}
        <rect y="150" width="400" height="18" fill="#efecdc" opacity=".8" />
        {stalks.map((s, i) => (
          <g key={i}>
            <rect x={s.x} y="-10" width={s.w} height="260" rx={s.w / 2} fill={s.c} />
            {[30, 92, 156, 214].map((y) => (
              <rect key={y} x={s.x - 2} y={y + i * 7} width={s.w + 4} height="4" rx="2" fill={INK} opacity=".55" />
            ))}
          </g>
        ))}
        {[
          [80, 40, -24, 1, "#2f4a28"], [80, 46, 20, .8, "#3f5c33"], [124, 100, -150, .9, "#2f4a28"], [124, 108, 160, .7, "#4f6e3f"],
          [230, 60, -30, 1.1, "#2f4a28"], [230, 66, 14, .9, "#3f5c33"], [230, 120, -160, 1, "#2f4a28"], [282, 160, -20, .8, "#3f5c33"],
          [350, 90, -150, 1, "#2f4a28"], [350, 98, 170, .8, "#4f6e3f"], [70, 170, -18, .9, "#3f5c33"], [354, 190, 196, .9, "#2f4a28"],
        ].map(([x, y, a, s, c], i) => leaf(x as number, y as number, a as number, s as number, c as string, i))}
      </>
    )}</Print>
  );
}

function DatabasesPrint() {
  return (
    <Print bg="#e8e4d2">{() => (
      <>
        <rect width="400" height="240" fill="#e6e2cf" />
        {/* layered hills, far to near, like stacked data */}
        <path d="M-10 92 C 60 60, 120 78, 180 64 C 240 50, 300 70, 410 58 L 410 240 L -10 240 Z" fill="#c9cdbc" />
        <path d="M-10 122 C 50 102, 130 118, 200 104 C 270 90, 330 112, 410 100 L 410 240 L -10 240 Z" fill="#aab79c" />
        <path d="M-10 156 C 70 138, 140 154, 210 142 C 280 130, 340 150, 410 140 L 410 240 L -10 240 Z" fill="#8ea07f" />
        <path d="M-10 190 C 80 176, 150 192, 230 182 C 300 174, 350 186, 410 180 L 410 240 L -10 240 Z" fill="#c8c6a4" />
        {/* the river: one deep blue ribbon winding to the front */}
        <path d="M196 60 C 230 76, 170 96, 196 112 C 230 132, 120 146, 170 170 C 220 194, 330 190, 300 250 L 220 250
                 C 250 200, 150 196, 120 172 C 90 146, 196 132, 176 114 C 156 98, 206 80, 186 62 Z" fill="#1f4f8a" />
        {/* ripples */}
        {["M196 116 C 186 122, 176 124, 166 128", "M150 164 C 162 172, 178 176, 196 178", "M230 196 C 246 204, 262 214, 268 226",
          "M190 84 C 196 90, 196 96, 190 100", "M244 210 C 252 218, 256 226, 258 236"].map((d, i) => (
          <path key={i} d={d} fill="none" stroke="#a9c4e4" strokeWidth="2.2" strokeLinecap="round" />
        ))}
        {/* grasses at the bank */}
        {Array.from({ length: 30 }, (_, i) => 6 + i * 13.5).filter((x) => x < 196 || x > 318).map((x, i) => (
          <g key={x} stroke="#5d6b3c" strokeWidth="1.8" strokeLinecap="round" fill="none">
            <path d={`M${x} 240 L${x - 4 + (i % 3) * 2} ${214 + (i % 4) * 3}`} />
            <path d={`M${x + 3} 240 L${x + 7} ${220 + (i % 3) * 4}`} />
          </g>
        ))}
      </>
    )}</Print>
  );
}

function DevopsPrint() {
  return (
    <Print bg="#efe0b0">{() => (
      <>
        <rect width="400" height="240" fill="#f0dca2" />
        {/* geometric mountains in slate, teal and moss, with print hatching */}
        <path d="M-10 170 L70 60 L150 170 Z" fill="#46606e" />
        <path d="M90 170 L190 34 L290 170 Z" fill="#2f4a56" />
        <path d="M230 170 L320 70 L410 170 Z" fill="#5b7a72" />
        {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
          <path key={i} d={`M${150 + i * 10} ${86 + i * 11} L ${190 + i * 2} ${44 + i * 4}`} stroke="#7d98a2" strokeWidth="2" opacity=".55" />
        ))}
        <path d="M190 34 L176 54 L190 50 L204 56 Z" fill="#f6f1e6" />
        {/* terraces stepping down */}
        {[0, 1, 2, 3].map((i) => (
          <path key={i} d={`M-10 ${170 + i * 18} L ${150 - i * 20} ${170 + i * 18} L ${170 - i * 20} ${188 + i * 18} L 410 ${188 + i * 18} L 410 ${170 + i * 18} Z`}
            fill={["#8aa36a", "#6f8b52", "#b6b37a", "#7c9460"][i]} />
        ))}
        {/* small firs */}
        {[[40, 168], [58, 172], [300, 168], [322, 170], [342, 166]].map(([x, y], i) => (
          <path key={i} d={`M${x} ${y} L${x + 8} ${y - 26} L${x + 16} ${y} Z`} fill="#24382c" />
        ))}
        <circle cx="342" cy="44" r="16" fill="#d9472c" />
      </>
    )}</Print>
  );
}

function SystemDesignPrint() {
  // A red arched bridge over still water: parts joined into one structure (the pagoda moved to Languages).
  return (
    <Print bg="#e7dcc4">{() => (
      <>
        <rect width="400" height="240" fill="#e6dbc1" />
        {/* distant hills in two indigo washes */}
        <path d="M0 120 C 60 96, 110 92, 170 110 C 230 86, 300 84, 400 108 L 400 150 L 0 150 Z" fill="#9fb0c4" />
        <path d="M0 140 C 80 124, 150 126, 220 136 C 290 124, 350 126, 400 132 L 400 160 L 0 160 Z" fill="#7f93ad" />
        {/* water, with a few ink ripple lines */}
        <rect y="156" width="400" height="84" fill="#cdd8de" />
        {[172, 190, 208, 226].map((y, i) => (
          <path key={y} d={`M${20 + i * 14} ${y} q 30 -5 60 0 M${180 - i * 10} ${y + 4} q 40 -6 80 0 M${300 + i * 8} ${y} q 26 -4 52 0`}
            fill="none" stroke="#5f7894" strokeWidth="1.4" opacity=".7" />
        ))}
        {/* the reflection, broken by the water */}
        <path d="M70 176 C 140 214, 260 214, 330 176" fill="none" stroke="#c63f28" strokeWidth="6" opacity=".25" strokeDasharray="18 8" />
        {/* the bridge: an arched deck, posts and a rail */}
        <path d="M54 170 C 120 96, 280 96, 346 170 L 336 174 C 274 110, 126 110, 64 174 Z" fill="#c63f28" />
        <path d="M60 160 C 124 86, 276 86, 340 160" fill="none" stroke="#c63f28" strokeWidth="4" />
        {Array.from({ length: 11 }, (_, i) => {
          const t = i / 10, x = 60 + 280 * t, y = 160 - 222 * t * (1 - t);
          return <rect key={i} x={x - 2.5} y={y} width="5" height="12" fill="#a8321f" />;
        })}
        {[[86, 150], [130, 126], [270, 126], [314, 150]].map(([x, y], i) => (
          <rect key={i} x={x - 4} y={y} width="8" height={190 - y} fill="#3a2b25" />
        ))}
        <path d="M54 170 C 120 96, 280 96, 346 170" fill="none" stroke={INK} strokeWidth="1.6" opacity=".6" />
      </>
    )}</Print>
  );
}

function CloudPrint() {
  const cloud = (x: number, y: number, s: number, k: number) => (
    <g key={k} transform={`translate(${x} ${y}) scale(${s})`}>
      <path d="M0 30 C 0 12, 22 4, 36 14 C 44 -4, 76 -4, 84 14 C 100 4, 124 14, 122 30 Z" fill="#f6f1e6" stroke="#8c8476" strokeWidth="2" />
      <path d="M22 22 C 26 16, 34 16, 36 22 M70 20 C 74 14, 82 14, 84 20" fill="none" stroke="#8c8476" strokeWidth="2" />
    </g>
  );
  return (
    <Print bg="#dfe3e4">{() => (
      <>
        <rect width="400" height="240" fill="#d9dfe2" />
        {[0, 1, 2, 3].map((i) => <rect key={i} y={60 + i * 46} width="400" height="2" fill="#b9c2c6" />)}
        {cloud(30, 40, 1.1, 1)}{cloud(220, 90, 1.4, 2)}{cloud(90, 150, 1.2, 3)}{cloud(290, 20, .8, 4)}
      </>
    )}</Print>
  );
}

/**
 * Two categories use pictures the owner chose (25 November): AI the brushed red sun over an ink wave, Languages the
 * vermilion pagoda among snowy cedars. Files in public/ukiyo/tracks/ (cropped to the print shape, 1000 px).
 */
const TRACK_IMAGES: Record<string, string> = { ai: "/ukiyo/tracks/ai.webp", languages: "/ukiyo/tracks/languages.webp" };

const PRINTS: Record<string, () => JSX.Element> = {
  frameworks: FrameworksPrint, databases: DatabasesPrint,
  devops: DevopsPrint, "system-design": SystemDesignPrint, cloud: CloudPrint, aws: CloudPrint,
};

/** The print for a category (track). Unknown tracks get the cloud print. */
export function TrackArt({ track }: { track: string }) {
  if (TRACK_IMAGES[track]) return <img className="u-print u-labprint" src={TRACK_IMAGES[track]} alt="" />;
  const Art = PRINTS[track] ?? CloudPrint;
  return <Art />;
}

/**
 * One real woodblock print per lab (owner, 24 November: "classy unique images for each one of the lab").
 * Public domain (most are CC0 from the Metropolitan Museum of Art), stored in public/ukiyo/labs/.
 * Each is picked to echo the lab's running project: wind for Windwatch, a bridge for Setu, water for the water board.
 */
type LabPrintInfo = { artist: "Hokusai" | "Hiroshige"; title: string; year: string };
const HK = "Hokusai" as const, HG = "Hiroshige" as const;
export const LAB_PRINTS: Record<string, LabPrintInfo> = {
  "rust-basics": { artist: HK, title: "Ejiri in Suruga Province", year: "about 1831" },
  langchain4j: { artist: HK, title: "The Suspension Bridge between Hida and Etchū", year: "about 1834" },
  langchain: { artist: HK, title: "Fujimigahara in Owari Province", year: "about 1831" },
  langgraph: { artist: HK, title: "The Waterwheel at Onden", year: "about 1831" },
  "rag-vector-databases": { artist: HK, title: "Ushibori in Hitachi Province", year: "about 1831" },
  "spring-ai": { artist: HK, title: "Sazai Hall at the Temple of the Five Hundred Arhats", year: "about 1831" },
  "java-collections": { artist: HK, title: "Mitsui Shop at Surugachō in Edo", year: "about 1831" },
  "go-basics": { artist: HK, title: "Hodogaya on the Tōkaidō", year: "about 1831" },
  "python-collections": { artist: HG, title: "Driving Rain at Shōno", year: "about 1833" },
  "javascript-basics": { artist: HK, title: "Honganji at Asakusa in Edo", year: "about 1831" },
  "python-basics": { artist: HG, title: "Nihonbashi: Morning View", year: "about 1833" },
  "spring-boot-first-api": { artist: HK, title: "Fuji from Gotenyama at Shinagawa", year: "about 1831" },
  "redis-in-practice": { artist: HK, title: "Shower Below the Summit", year: "about 1831" },
  "postgres-indexing-incident": { artist: HG, title: "Night Snow at Kanbara", year: "about 1833" },
  "linux-on-call": { artist: HG, title: "Autumn Moon on the Tama River", year: "about 1838" },
  "rate-limiter": { artist: HK, title: "Fuji Seen from Kanaya on the Tōkaidō", year: "about 1831" },
  "javascript-inside-out": { artist: HK, title: "Kajikazawa in Kai Province", year: "about 1831" },
  "java-basics": { artist: HK, title: "The Tama River in Musashi Province", year: "about 1831" },
  "express-api": { artist: HG, title: "The Mie River at Yokkaichi", year: "about 1833" },
  "fastapi-first-api": { artist: HG, title: "The Lake at Hakone", year: "about 1833" },
  "sql-from-zero": { artist: HK, title: "Lake Suwa in Shinano Province", year: "about 1831" },
  "postgres-transactions-and-locks": { artist: HK, title: "Under the Mannen Bridge at Fukagawa", year: "about 1831" },
  "git-without-fear": { artist: HK, title: "Kintai Bridge in Suō Province", year: "about 1834" },
};

/** "Katsushika Hokusai, Ejiri in Suruga Province, about 1831" (for captions and alt text). */
export function printCredit(lab: string): string | null {
  const p = LAB_PRINTS[lab];
  if (!p) return null;
  return `${p.artist === "Hokusai" ? "Katsushika Hokusai" : "Utagawa Hiroshige"}, ${p.title}, ${p.year}`;
}

/** The lab's own print; a lab without one falls back to its category's print. */
export function LabPrint({ lab, track }: { lab: string; track: string }) {
  const credit = printCredit(lab);
  if (!credit) return <TrackArt track={track} />;
  return <img className="u-print u-labprint" src={`/ukiyo/labs/${lab}.webp`} alt={`Woodblock print: ${credit}`} loading="lazy" />;
}

/** Each category's ink as a plain colour (for code that mixes colours, like the metro map). */
export const TRACK_HEX: Record<string, string> = {
  ai: "#1f3a64", languages: "#c63f28", frameworks: "#5c7a4c", databases: "#2a5a86", devops: "#50606e",
  "system-design": "#84563a", cloud: "#8c8476", aws: "#8c8476",
};

/** Each category's ink colour and its motif, for small accents. */
export const TRACK_INK: Record<string, string> = {
  ai: "var(--indigo)", languages: "var(--vermilion)", frameworks: "var(--sage)", databases: "var(--river)",
  devops: "var(--slate)", "system-design": "var(--earth)", cloud: "var(--cloud)", aws: "var(--cloud)",
};
export const TRACK_MOTIF: Record<string, string> = {
  ai: "Sun and wave", languages: "Pagoda", frameworks: "Bamboo", databases: "River", devops: "Mountains",
  "system-design": "Bridge", cloud: "Clouds", aws: "Clouds",
};

/** A small vermilion hanko seal with up to two short lines (for milestones and picks). */
export function Seal({ lines, size = 44, title }: { lines: string[]; size?: number; title?: string }) {
  return (
    <svg className="u-seal" width={size} height={size} viewBox="0 0 44 44" role={title ? "img" : undefined} aria-label={title}
      aria-hidden={title ? undefined : true}>
      <rect x="2" y="2" width="40" height="40" rx="5" fill="var(--vermilion)" />
      <rect x="5.5" y="5.5" width="33" height="33" rx="2" fill="none" stroke="#fff" strokeWidth="1" opacity=".85" />
      <g fill="#fff" fontFamily="Fraunces, Georgia, serif" fontWeight="700" textAnchor="middle">
        {lines.length === 1
          ? <text x="22" y={lines[0].length > 2 ? 25.5 : 27} fontSize={[13, 13, 13, 10.5, 9, 7.6][Math.min(lines[0].length, 5)]}>{lines[0]}</text>
          : <><text x="22" y="20" fontSize="10.5">{lines[0]}</text><text x="22" y="32" fontSize="10.5">{lines[1]}</text></>}
      </g>
    </svg>
  );
}

/** Level as one to three brush marks (beginner, intermediate, advanced). */
export function BrushLevel({ level }: { level: string | null | undefined }) {
  if (!level) return null;
  const n = { beginner: 1, intermediate: 2, advanced: 3 }[level] ?? 0;
  const name = level[0].toUpperCase() + level.slice(1);
  return (
    <span className="u-level" title={name}>
      <svg width="30" height="12" viewBox="0 0 30 12" aria-hidden="true">
        {[0, 1, 2].map((i) => (
          <path key={i} d={`M${2 + i * 10} 10 C ${4 + i * 10} 6, ${6 + i * 10} 3, ${8 + i * 10} 2`} fill="none"
            stroke={i < n ? "currentColor" : "var(--border)"} strokeWidth="2.6" strokeLinecap="round" />
        ))}
      </svg>
      <span>{name}</span>
    </span>
  );
}

/** Progress as a fine ink line with a small seal where you are. */
export function InkProgress({ value, label }: { value: number; label: string }) {
  const pct = Math.max(0, Math.min(100, Math.round(value * 100)));
  return (
    <div className="u-ink" role="progressbar" aria-label={label} aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
      <span className="u-ink-line"><span style={{ width: `${pct}%` }} /></span>
      <span className="u-ink-mark" style={{ left: `${pct}%` }} />
    </div>
  );
}
