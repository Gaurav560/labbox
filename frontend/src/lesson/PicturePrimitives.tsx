import type { ReactNode } from "react";

/** Filters and markers for the hand-drawn look; every picture carries its own copy. */
function Defs() {
  return (
    <defs>
      <filter id="pc-wobble">
        <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="3" />
        <feDisplacementMap in="SourceGraphic" scale="3" />
      </filter>
      <pattern id="pc-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
        <line className="pc-hatch-line" x1="0" y1="0" x2="0" y2="6" />
      </pattern>
      <marker id="pc-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M 0 1 L 9 5 L 0 9" className="pc-head" />
      </marker>
    </defs>
  );
}

/** A hand-drawn line or curve; with an arrow head unless plain. */
export function Ink({ d, plain }: { d: string; plain?: boolean }) {
  return <path className="pc-ink" d={d} markerEnd={plain ? undefined : "url(#pc-head)"} />;
}

export function Card({ x, y, w, h }: { x: number; y: number; w: number; h: number }) {
  return <rect className="pc-card" x={x} y={y} width={w} height={h} rx={10} />;
}

export function Hand({ x, y, children, kind = "hand", anchor }: { x: number; y: number; children: ReactNode; kind?: "hand" | "title" | "label" | "code"; anchor?: "middle" | "end" }) {
  return <text className={`pc-${kind}`} x={x} y={y} textAnchor={anchor}>{children}</text>;
}

export function Svg({ label, children }: { label: string; children: ReactNode }) {
  return (
    <svg viewBox="0 0 320 150" role="img" aria-label={label}>
      <Defs />
      {children}
    </svg>
  );
}
