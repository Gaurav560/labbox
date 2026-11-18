import { useId, type ReactNode } from "react";

// Cover art for a lab card. A lab can ship its own image (`cover:` in lab.yaml, served at cover_url);
// otherwise one is drawn here: the track sets the colours and the illustration, and a pattern seeded
// from the lab id makes every lab look a little different. Works for any number of labs.

interface Props {
  id: string;
  title: string;
  track: string;
  tags: string[];
  coverUrl?: string | null;
  credit?: { by: string; url: string; source: string } | null;
}

// Three colour pairs per track; each lab picks one, so labs in the same track still differ.
const PALETTES: Record<string, [string, string][]> = {
  languages: [["#4338ca", "#7c3aed"], ["#3730a3", "#2563eb"], ["#5b21b6", "#c026d3"]],
  frameworks: [["#0f766e", "#0891b2"], ["#047857", "#0d9488"], ["#155e75", "#2563eb"]],
  databases: [["#b45309", "#e11d48"], ["#9a3412", "#d97706"], ["#be123c", "#c2410c"]],
  devops: [["#0369a1", "#4f46e5"], ["#1e40af", "#0891b2"], ["#075985", "#0f766e"]],
  "system-design": [["#334155", "#4338ca"], ["#1e293b", "#0369a1"], ["#3f3f46", "#7c3aed"]],
  ai: [["#a21caf", "#e11d48"], ["#7e22ce", "#db2777"], ["#be185d", "#ea580c"]],
  interview: [["#047857", "#0e7490"], ["#166534", "#0f766e"], ["#0f766e", "#4d7c0f"]],
};

/** FNV-1a: a stable number from a string. */
function hash(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

/** Small seeded random generator (mulberry32), so the same lab always gets the same art. */
function rng(seed: number): () => number {
  let a = seed;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const S = { stroke: "#fff", strokeWidth: 2.5, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
const FILL = "rgba(255,255,255,0.1)";

// Each motif is drawn in a 140 x 110 box.
function motif(track: string, r: () => number): ReactNode {
  switch (track) {
    case "frameworks":
      return [0, 1, 2].map((i) => {
        const y = 70 - i * 26;
        return <path key={i} d={`M10 ${y} L70 ${y - 22} L130 ${y} L70 ${y + 22} Z`} fill={FILL} {...S} opacity={1 - i * 0.18} />;
      });
    case "databases":
      return (
        <>
          {[0, 1].map((i) => {
            const y = 18 + i * 42;
            return (
              <g key={i} opacity={i ? 0.8 : 1}>
                <path d={`M25 ${y} v34 a45 12 0 0 0 90 0 v-34`} fill={FILL} {...S} />
                <ellipse cx="70" cy={y} rx="45" ry="12" fill={FILL} {...S} />
              </g>
            );
          })}
          <path d="M120 20 l12 -12 M126 8 h6 v6" {...S} fill="none" />
        </>
      );
    case "devops":
      return (
        <>
          {[
            [10, 52],
            [52, 52],
            [94, 52],
            [31, 14],
            [73, 14],
          ].map(([x, y], i) => (
            <g key={i}>
              <rect x={x} y={y} width="36" height="32" rx="4" fill={FILL} {...S} />
              <path d={`M${x + 9} ${y + 6} v20 M${x + 18} ${y + 6} v20 M${x + 27} ${y + 6} v20`} {...S} strokeWidth={1.5} opacity={0.7} />
            </g>
          ))}
          <path d="M6 98 Q70 110 134 98" {...S} fill="none" />
        </>
      );
    case "system-design": {
      const pts = [
        [20, 55],
        [70, 15 + r() * 10],
        [70, 95 - r() * 10],
        [120, 35 + r() * 10],
        [120, 80 + r() * 10],
      ];
      const edges = [[0, 1], [0, 2], [1, 3], [1, 4], [2, 4], [2, 3]];
      return (
        <>
          {edges.map(([a, b], i) => (
            <line key={i} x1={pts[a][0]} y1={pts[a][1]} x2={pts[b][0]} y2={pts[b][1]} {...S} opacity={0.6} />
          ))}
          {pts.map(([x, y], i) => (
            <circle key={i} cx={x} cy={y} r={i === 0 ? 13 : 10} fill={FILL} {...S} />
          ))}
        </>
      );
    }
    case "ai": {
      const layers = [3, 4, 2].map((n, li) => Array.from({ length: n }, (_, i) => [15 + li * 55, 55 + (i - (n - 1) / 2) * 26]));
      return (
        <>
          {layers.slice(0, -1).flatMap((layer, li) =>
            layer.flatMap(([x1, y1], i) =>
              layers[li + 1].map(([x2, y2], j) => (
                <line key={`${li}-${i}-${j}`} x1={x1} y1={y1} x2={x2} y2={y2} {...S} strokeWidth={1.4} opacity={0.35 + r() * 0.4} />
              )),
            ),
          )}
          {layers.flat().map(([x, y], i) => (
            <circle key={i} cx={x} cy={y} r="8" fill={FILL} {...S} />
          ))}
        </>
      );
    }
    case "interview":
      return (
        <>
          {[44, 30, 16].map((rad, i) => (
            <circle key={i} cx="62" cy="56" r={rad} fill={i === 0 ? FILL : "none"} {...S} opacity={1 - i * 0.15} />
          ))}
          <path d="M98 30 l-36 26" {...S} />
          <path d="M104 62 l10 10 l20 -26" {...S} fill="none" strokeWidth={3.5} />
        </>
      );
    default: {
      // languages: a code window with a few lines of "code".
      const widths = Array.from({ length: 4 }, () => 30 + r() * 60);
      return (
        <>
          <rect x="5" y="5" width="130" height="100" rx="10" fill={FILL} {...S} />
          <line x1="5" y1="25" x2="135" y2="25" {...S} opacity={0.6} />
          {[16, 26, 36].map((x) => (
            <circle key={x} cx={x} cy="15" r="2.5" fill="#fff" opacity={0.8} />
          ))}
          {widths.map((w, i) => (
            <line key={i} x1={i % 2 ? 30 : 18} y1={42 + i * 15} x2={(i % 2 ? 30 : 18) + w} y2={42 + i * 15} {...S} opacity={0.85 - i * 0.12} />
          ))}
          <rect x={18 + widths[3] * 0.3} y="95" width="8" height="3" fill="#fff" opacity={0.9} />
        </>
      );
    }
  }
}

export default function LabCover({ id, title, track, tags, coverUrl, credit }: Props) {
  const uid = useId().replace(/:/g, "");
  if (coverUrl) {
    return (
      <div className="lab-cover-photo">
        <img className="lab-cover" src={coverUrl} alt="" loading="lazy" decoding="async" />
        {credit?.url && (
          <a className="cover-credit" href={credit.url} target="_blank" rel="noreferrer noopener">
            Photo: {credit.by} / {credit.source}
          </a>
        )}
      </div>
    );
  }
  const r = rng(hash(id));
  const options = PALETTES[track] ?? PALETTES.languages;
  const [c1, c2] = options[Math.floor(r() * options.length)];
  const angle = Math.round(r() * 60);
  const dots = Array.from({ length: 16 }, () => ({ x: r() * 400, y: r() * 200, rad: 2 + r() * 10, ring: r() > 0.6, o: 0.06 + r() * 0.12 }));
  const glowX = 260 + r() * 120;
  const labels = tags.slice(0, 2);

  return (
    <svg className="lab-cover" viewBox="0 0 400 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true" data-title={title}>
      <defs>
        <linearGradient id={`g${uid}`} gradientTransform={`rotate(${angle} 0.5 0.5)`}>
          <stop offset="0" stopColor={c1} />
          <stop offset="1" stopColor={c2} />
        </linearGradient>
        <radialGradient id={`l${uid}`}>
          <stop offset="0" stopColor="#fff" stopOpacity="0.28" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect width="400" height="200" fill={`url(#g${uid})`} />
      <circle cx={glowX} cy="30" r="150" fill={`url(#l${uid})`} />
      {dots.map((d, i) =>
        d.ring ? (
          <circle key={i} cx={d.x} cy={d.y} r={d.rad} fill="none" stroke="#fff" strokeWidth="1.5" opacity={d.o} />
        ) : (
          <circle key={i} cx={d.x} cy={d.y} r={d.rad / 2} fill="#fff" opacity={d.o} />
        ),
      )}
      <g transform="translate(236 44)">{motif(track, r)}</g>
      {labels.map((t, i) => {
        const w = 14 + t.length * 8.2;
        const x = 20 + labels.slice(0, i).reduce((n, p) => n + 22 + p.length * 8.2, 0);
        return (
          <g key={t} transform={`translate(${x} 150)`}>
            <rect width={w} height="28" rx="14" fill="rgba(0,0,0,0.28)" />
            <text x={w / 2} y="19" textAnchor="middle" fill="#fff" fontFamily='"JetBrains Mono", monospace' fontSize="13" fontWeight="700">
              {t}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
