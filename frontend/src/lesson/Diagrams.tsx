import type { ReactNode } from "react";

/*
 * Built-in pictures for ideas you cannot see (Content standard: "pictures for invisible ideas").
 * A chapter asks for one with :::diagram{name="shared-list"}, and the text inside becomes the caption.
 * Drawn as SVG with theme colours (CSS variables), so they work in light and dark themes and stay sharp
 * at any text size.
 */

function Box({ x, y, w, h, label, tone = "plain" }: { x: number; y: number; w: number; h: number; label: string; tone?: "plain" | "accent" }) {
  return (
    <g className={`dg-box dg-${tone}`}>
      <rect x={x} y={y} width={w} height={h} rx={8} />
      <text x={x + w / 2} y={y + h / 2 + 5} textAnchor="middle">{label}</text>
    </g>
  );
}

function Arrow({ x1, y1, x2, y2 }: { x1: number; y1: number; x2: number; y2: number }) {
  return <line className="dg-arrow" x1={x1} y1={y1} x2={x2} y2={y2} markerEnd="url(#dg-head)" />;
}

function Cells({ x, y, values, tone = "plain" }: { x: number; y: number; values: (string | number)[]; tone?: "plain" | "accent" }) {
  return (
    <g>
      {values.map((v, i) => (
        <Box key={i} x={x + i * 46} y={y} w={42} h={38} label={String(v)} tone={tone} />
      ))}
    </g>
  );
}

/** Two names, one list: b = a shares the list; a.copy() makes a second one. */
function SharedList() {
  return (
    <svg viewBox="0 0 440 200" role="img" aria-label="a and b point to the same list [3, 1, 2]; c points to a separate copy">
      <defs>
        <marker id="dg-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" className="dg-head" />
        </marker>
      </defs>
      <text className="dg-note" x={10} y={22}>b = a</text>
      <Box x={10} y={40} w={56} h={34} label="a" tone="accent" />
      <Box x={10} y={92} w={56} h={34} label="b" tone="accent" />
      <Arrow x1={68} y1={57} x2={196} y2={80} />
      <Arrow x1={68} y1={109} x2={196} y2={90} />
      <Cells x={200} y={66} values={[3, 1, 2]} />
      <text className="dg-note" x={200} y={56}>one list</text>
      <text className="dg-note" x={10} y={164}>c = a.copy()</text>
      <Box x={10} y={170} w={56} h={26} label="c" tone="accent" />
      <Arrow x1={68} y1={183} x2={196} y2={183} />
      <Cells x={200} y={164} values={[3, 1, 2]} />
      <text className="dg-note" x={344} y={188}>its own list</text>
    </svg>
  );
}

const DIAGRAMS: Record<string, () => JSX.Element> = {
  "shared-list": SharedList,
};

export default function Diagram({ name, caption }: { name: string; caption?: ReactNode }) {
  const Picture = DIAGRAMS[name];
  if (!Picture) return null;
  return (
    <figure className="diagram">
      <Picture />
      {caption && <figcaption>{caption}</figcaption>}
    </figure>
  );
}
