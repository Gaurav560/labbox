/*
 * The Ukiyo artwork (owner, 24 November): original illustrations in the manner of Japanese woodblock prints,
 * one per category, drawn as SVG so they are sharp at every size, load with the page and cost nothing.
 * Flat colour blocks, an ink outline where it helps, and a faint paper grain, like a printed sheet.
 *   AI: waves (the great wave and seigaiha)       Languages: the sun behind Fuji
 *   Frameworks: bamboo                             Databases: a river through layered hills
 *   DevOps: geometric mountains and terraces       System design: a pagoda
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

/** Seigaiha: rows of overlapping wave arcs, for the bottom of the AI print. */
function SeigaihaRows({ y, rows, color, fill }: { y: number; rows: number; color: string; fill: string }) {
  const out: ReactNode[] = [];
  for (let r = 0; r < rows; r++) {
    for (let c = -1; c < 12; c++) {
      const cx = c * 36 + (r % 2 ? 18 : 0);
      const cy = y + r * 12;
      out.push(
        <g key={`${r}-${c}`}>
          <circle cx={cx} cy={cy + 18} r="18" fill={fill} stroke={color} strokeWidth="1.6" />
          <circle cx={cx} cy={cy + 18} r="12.5" fill="none" stroke={color} strokeWidth="1.4" />
          <circle cx={cx} cy={cy + 18} r="7" fill="none" stroke={color} strokeWidth="1.3" />
        </g>,
      );
    }
  }
  return <g>{out}</g>;
}

function AiPrint() {
  return (
    <Print bg="#efe3c8">{() => (
      <>
        {/* a pale sky and a small, distant Fuji */}
        <rect width="400" height="240" fill="#e9dcc0" />
        <path d="M262 150 L292 116 L322 150 Z" fill="#7f93ad" />
        <path d="M284 125 L292 116 L300 125 L296 128 L292 124 L288 128 Z" fill="#f6f1e6" />
        {/* the great curl, rising from the left */}
        <path d="M-10 240 L-10 150 C 30 92, 110 54, 186 70 C 232 80, 252 116, 230 140 C 214 157, 186 150, 190 132
                 C 194 118, 214 120, 210 104 C 200 82, 150 86, 120 112 C 92 136, 84 190, 120 240 Z" fill="#1f3a64" />
        <path d="M10 240 C 20 184, 56 134, 110 110 C 80 140, 70 190, 96 240 Z" fill="#2f5487" />
        <path d="M36 240 C 44 200, 64 170, 92 150 C 80 180, 80 214, 92 240 Z" fill="#a9bdd6" />
        {/* the white claw of foam along the crest */}
        <path d="M120 112 C 150 86, 200 82, 210 104 C 214 120, 194 118, 190 132 C 186 150, 214 157, 230 140
                 C 222 152, 196 160, 182 146 C 172 134, 186 118, 200 112 C 186 94, 148 98, 120 112 Z" fill="#f6f1e6" />
        {[[134, 104], [150, 96], [168, 92], [186, 93], [200, 99], [214, 132], [224, 142], [204, 148]].map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r={2.6 + (i % 3)} fill="#f6f1e6" />
        ))}
        {/* the ocean pattern beneath */}
        <SeigaihaRows y={168} rows={6} color="#1f3a64" fill="#e9dcc0" />
        <path d="M-10 240 L-10 150 C 30 92, 110 54, 186 70" fill="none" stroke={INK} strokeWidth="2" opacity=".55" />
      </>
    )}</Print>
  );
}

function LanguagesPrint() {
  const rays = Array.from({ length: 18 }, (_, i) => i);
  return (
    <Print bg="#f0c46a">{() => (
      <>
        {/* sun rays fanning out from behind the mountain */}
        <g transform="translate(232 128)">
          {rays.map((i) => (
            <path key={i} d="M0 0 L-14 -260 L14 -260 Z" fill={i % 2 ? "#f6d58f" : "#eab352"} transform={`rotate(${-90 + i * 10.6})`} />
          ))}
        </g>
        <circle cx="232" cy="118" r="54" fill="#d9472c" />
        <circle cx="232" cy="118" r="54" fill="none" stroke="#b9361f" strokeWidth="3" />
        {/* Fuji: indigo slopes, a snow cap with long fingers */}
        <path d="M70 240 L196 112 C 214 100, 252 100, 268 112 L 410 240 Z" fill="#2a4a78" />
        <path d="M196 112 C 214 100, 252 100, 268 112 L 300 148 L 288 142 L 280 162 L 266 140 L 256 170 L 246 138 L 234 166
                 L 224 136 L 212 158 L 204 134 L 188 150 L 170 142 Z" fill="#f6f1e6" />
        <path d="M70 240 L196 112 C 214 100, 252 100, 268 112 L 410 240" fill="none" stroke={INK} strokeWidth="2.2" />
        {/* ridge lines down the slopes */}
        {[[150, 170, 120, 240], [176, 150, 160, 240], [300, 160, 330, 240], [320, 180, 352, 240]].map(([x1, y1, x2, y2], i) => (
          <path key={i} d={`M${x1} ${y1} L${x2} ${y2}`} stroke="#1f3a64" strokeWidth="5" opacity=".6" />
        ))}
        {/* a band of cloud at the foot */}
        <path d="M-10 214 C 30 200, 60 220, 96 206 C 130 194, 160 214, 196 204 C 230 194, 262 214, 300 204 C 336 194, 370 210, 410 202 L 410 240 L -10 240 Z"
          fill="#f6f1e6" />
        <path d="M-10 214 C 30 200, 60 220, 96 206 C 130 194, 160 214, 196 204 C 230 194, 262 214, 300 204 C 336 194, 370 210, 410 202"
          fill="none" stroke="#c9a15a" strokeWidth="2" />
      </>
    )}</Print>
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
  const roof = (y: number, w: number, k: number) => (
    <g key={k}>
      <path d={`M${200 - w} ${y} C ${200 - w + 10} ${y - 4}, ${200 - w * 0.4} ${y - 16}, 200 ${y - 22} C ${200 + w * 0.4} ${y - 16}, ${200 + w - 10} ${y - 4}, ${200 + w} ${y}
               L ${200 + w - 8} ${y + 4} L ${200 - w + 8} ${y + 4} Z`} fill="#2b2622" />
      <path d={`M${200 - w + 6} ${y + 4} L ${200 + w - 6} ${y + 4}`} stroke="#c9a15a" strokeWidth="1.6" />
    </g>
  );
  return (
    <Print bg="#e7dcc4">{() => (
      <>
        <rect width="400" height="240" fill="#e4d8bd" />
        {/* pines either side, in grey-green blocks */}
        {[[30, 40], [70, 70], [330, 50], [366, 80]].map(([x, y], i) => (
          <g key={i}>
            <rect x={x + 10} y={y + 40} width="6" height="160" fill="#4a4036" />
            <path d={`M${x - 20} ${y + 70} L${x + 13} ${y} L${x + 46} ${y + 70} Z`} fill="#5d6f5a" opacity=".85" />
            <path d={`M${x - 14} ${y + 110} L${x + 13} ${y + 50} L${x + 40} ${y + 110} Z`} fill="#4d5e4a" opacity=".85" />
          </g>
        ))}
        {/* the pagoda: three tiers of vermilion posts under dark curved roofs */}
        <rect x="184" y="18" width="32" height="6" fill="#c9a15a" />
        <rect x="197" y="2" width="6" height="22" fill="#c9a15a" />
        {[[176, 44, 30], [168, 92, 40], [158, 142, 52]].map(([x, y, w], i) => (
          <g key={i}>
            <rect x={x} y={y} width={(200 - x) * 2} height={w} fill="#c63f28" />
            {[0.2, 0.5, 0.8].map((f) => <rect key={f} x={x + (200 - x) * 2 * f - 2} y={y} width="4" height={w} fill="#8e2a1a" />)}
            <rect x={x} y={y + w - 8} width={(200 - x) * 2} height="8" fill="#e9dcc0" opacity=".8" />
          </g>
        ))}
        {roof(48, 50, 1)}{roof(96, 62, 2)}{roof(146, 76, 3)}
        {/* stone base and steps */}
        <rect x="132" y="194" width="136" height="18" fill="#8d877c" />
        <path d="M132 194 L268 194" stroke={INK} strokeWidth="1.5" />
        {[0, 1, 2].map((i) => <rect key={i} x={182 - i * 6} y={212 + i * 9} width={36 + i * 12} height="9" fill={["#a39d90", "#958f83", "#88827a"][i]} />)}
        <rect y="232" width="400" height="8" fill="#9a9384" />
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

const PRINTS: Record<string, () => JSX.Element> = {
  ai: AiPrint, languages: LanguagesPrint, frameworks: FrameworksPrint, databases: DatabasesPrint,
  devops: DevopsPrint, "system-design": SystemDesignPrint, cloud: CloudPrint, aws: CloudPrint,
};

/** The print for a category (track). Unknown tracks get the cloud print. */
export function TrackArt({ track }: { track: string }) {
  const Art = PRINTS[track] ?? CloudPrint;
  return <Art />;
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
  ai: "Waves", languages: "Rising sun", frameworks: "Bamboo", databases: "River", devops: "Mountains",
  "system-design": "Pagoda", cloud: "Clouds", aws: "Clouds",
};

/** A small vermilion hanko seal with up to two short lines (for milestones and picks). */
export function Seal({ lines, size = 44, title }: { lines: string[]; size?: number; title?: string }) {
  return (
    <svg className="u-seal" width={size} height={size} viewBox="0 0 44 44" role={title ? "img" : undefined} aria-label={title}
      aria-hidden={title ? undefined : true}>
      <rect x="2" y="2" width="40" height="40" rx="5" fill="var(--vermilion)" transform="rotate(-4 22 22)" />
      <rect x="5.5" y="5.5" width="33" height="33" rx="2" fill="none" stroke="#fff" strokeWidth="1" transform="rotate(-4 22 22)" opacity=".85" />
      <g transform="rotate(-4 22 22)" fill="#fff" fontFamily="Fraunces, Georgia, serif" fontWeight="700" textAnchor="middle">
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
