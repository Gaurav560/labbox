import { useId, type CSSProperties, type ReactNode } from "react";

export function Ink({ d, plain }: { d: string; plain?: boolean }) {
  return <path className="pc-ink" d={d} markerEnd={plain ? undefined : "var(--figure-arrowhead)"} />;
}

export function Card({ x, y, w, h }: { x: number; y: number; w: number; h: number }) {
  return <rect className="pc-card" x={x} y={y} width={w} height={h} rx={10} />;
}

export function Hand({ x, y, children, kind = "hand", anchor }: { x: number; y: number; children: ReactNode; kind?: "hand" | "title" | "label" | "code"; anchor?: "middle" | "end" }) {
  return <text className={`pc-${kind}`} x={x} y={y} textAnchor={anchor}>{children}</text>;
}

export function Svg({ label, viewBox = "0 0 320 150", children }: { label: string; viewBox?: string; children: ReactNode }) {
  const head = useId();
  const style = { "--figure-arrowhead": `url("#${head}")` } as CSSProperties;
  return (
    <svg viewBox={viewBox} role="img" aria-label={label} style={style}>
      <defs>
        <marker id={head} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M1 1 L9 5 L1 9 Z" className="figure-arrowhead" />
        </marker>
      </defs>
      {children}
    </svg>
  );
}
