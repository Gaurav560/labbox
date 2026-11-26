import { useLayoutEffect, useMemo, useRef, useState, type MouseEvent, type ReactNode } from "react";
import { Link } from "react-router-dom";
import type { LabDetail } from "../api";
import { chapterNumber } from "./StatusBar";

/*
 * A skill map drawn as a metro map (owner, 21 November): every part of a course is its own coloured line, every
 * chapter a station with a card listing its subtopics. The route snakes down the page, a few roomy stations per
 * row, turning down at each end with rounded corners; where one part meets the next, the colour blends into the
 * next line's. A light 3D finish: tube-like tracks with a shadow, glossy stations, cards that tilt towards the mouse.
 * The route you have travelled is solid, the rest is faded; the station you are at pulses and says "You are here".
 * Narrow screens get the same lines as a vertical list.
 */

export type StationState = "done" | "now" | "open" | "locked" | "soon";
export interface Station {
  id: string;
  number: string;
  title: string;
  meta?: string;
  topics?: { title: string; href?: string }[];   // subtopics on the card, each opening its lesson step
  state: StationState;
  href?: string;            // a link station (a lab chapter)
}
export interface MetroLine { name: string; stations: Station[] }

const COLORS = ["#e5484d", "#0090ff", "#30a46c", "#f5a623", "#8e4ec6", "#12a594", "#d6409f"];
const CORNER = 34;      // radius of the turns at the row ends
const MARGIN = 18;      // the vertical connectors run this far from the edge, outside the cards
const CARD = 220;       // card width
const PAD = MARGIN + 18 + CARD / 2;   // the outermost stations, so their cards clear the connectors
const TOP = 96;         // room above the first row for the line name and "You are here"
const MIN_GAP = CARD + 26;   // stations are at least this far apart
const MAX_TOPICS = 4;
const NARROW = 700;

export const lineColor = (i: number) => COLORS[i % COLORS.length];

interface Placed extends Station { x: number; y: number; line: number; first: boolean; edge: "left" | "right"; index: number }

// Card height estimate (px) so rows never overlap: number, title, subtopics, meta, at about 26 characters a line.
const wrap = (text: string, per = 24) => Math.max(1, Math.ceil(text.length / per));
const cardHeight = (s: Station, open: boolean) => {
  const all = s.topics ?? [];
  const topics = open ? all : all.slice(0, MAX_TOPICS);
  const more = all.length > MAX_TOPICS ? 24 : 0;
  return 54 + 22 * wrap(s.title, 20) + topics.reduce((h, t) => h + 20 * wrap(t.title) + 3, topics.length ? 10 : 0) + more + (s.meta ? 24 : 0);
};

/**
 * A lab as metro lines: every course part a line, every chapter a station, each subtopic a link to its lesson step.
 * "You are here" is nowIdx when given (the chapter the learner was last in), else the first chapter not done.
 */
export function labLines(lab: LabDetail, nowIdx?: number): MetroLine[] {
  // A locked lab (app/slots.py): the map shows what the course covers, with no links into its lessons.
  const locked = lab.access === "locked";
  const done = (i: number) => lab.chapters[i].tasks.length > 0 && lab.chapters[i].tasks.every((t) => t.passed);
  const now = nowIdx ?? lab.chapters.findIndex((_, i) => !done(i));
  const out: MetroLine[] = [];
  lab.chapters.forEach((c, i) => {
    const passed = c.tasks.filter((t) => t.passed).length;
    const st: Station = {
      id: c.id,
      number: String(chapterNumber(lab.chapters, i)).padStart(2, "0"),
      title: c.title,
      topics: c.topics?.map((t) => ({ title: t.title, href: locked ? undefined : `/labs/${lab.id}?chapter=${encodeURIComponent(c.id)}&step=${t.step}` })),
      meta: `${passed} of ${c.tasks.length} task${c.tasks.length === 1 ? "" : "s"}${c.minutes ? ` · ${c.minutes} min` : ""}`,
      state: locked ? "locked" : i === now ? "now" : done(i) ? "done" : "open",
      href: locked ? undefined : `/labs/${lab.id}?chapter=${encodeURIComponent(c.id)}`,
    };
    // A chapter with a part starts that line; chapters without one stay on the current line.
    if (!out.length || (c.part && c.part !== out[out.length - 1].name)) out.push({ name: c.part || lab.title, stations: [] });
    out[out.length - 1].stations.push(st);
  });
  return out;
}

export default function MetroMap({ lines, selected, onSelect }: {
  lines: MetroLine[];
  selected?: string | null;
  onSelect?: (id: string) => void;   // for stations without a link (track topics)
}) {
  const box = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());   // cards showing all their subtopics
  const toggle = (id: string) => setExpanded((e) => { const n = new Set(e); if (n.has(id)) n.delete(id); else n.add(id); return n; });
  useLayoutEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setWidth(el.clientWidth));
    ro.observe(el);
    setWidth(el.clientWidth);
    return () => ro.disconnect();
  }, []);

  const all = lines.flatMap((l) => l.stations);
  const nowIdx = (() => {
    const i = all.findIndex((s) => s.state === "now");
    if (i >= 0) return i;
    return all.every((s) => s.state === "done") ? all.length : -1;
  })();

  const { placed, height, cardW } = useMemo(() => {
    if (!width || width < NARROW) return { placed: [] as Placed[], height: 0, cardW: 0 };
    const span = width - 2 * PAD;
    const perRow = Math.max(2, Math.floor(span / MIN_GAP) + 1);
    const out: Placed[] = [];
    let row = 0;
    let y = TOP;
    lines.forEach((l, li) => {
      // A long line is split into rows of equal size (10 stations on 4-wide rows become 4, 3, 3).
      const rows = Math.ceil(l.stations.length / perRow);
      for (let rr = 0, k = 0; rr < rows; rr++) {
        const size = Math.ceil((l.stations.length - k) / (rows - rr));
        const chunk = l.stations.slice(k, k + size);
        const ltr = row % 2 === 0;
        chunk.forEach((s, j) => {
          const t = chunk.length === 1 ? 0 : j / (chunk.length - 1);
          const x = ltr ? PAD + t * span : width - PAD - t * span;
          out.push({ ...s, x, y, line: li, first: k === 0 && j === 0, edge: ltr ? "right" : "left", index: out.length });
        });
        y += 36 + Math.max(...chunk.map((s) => cardHeight(s, expanded.has(s.id)))) + 96;
        row++;
        k += size;
      }
    });
    const gap = perRow > 1 ? span / (perRow - 1) : span;
    return { placed: out, height: y - 60, cardW: Math.min(CARD, gap - 24) };
  }, [lines, width, expanded]);

  // The page opens at its top; "You are here" marks the current chapter without scrolling to it (owner, 25 November).
  const nowRef = useRef<HTMLLIElement>(null);

  const narrow = width > 0 && width < NARROW;

  const trackPath = (a: Placed, b: Placed) => {
    if (a.y === b.y) return `M ${a.x} ${a.y} L ${b.x} ${b.y}`;
    const r = CORNER;
    if (a.edge === "right") {
      const xv = width - MARGIN;
      return `M ${a.x} ${a.y} L ${xv - r} ${a.y} A ${r} ${r} 0 0 1 ${xv} ${a.y + r} L ${xv} ${b.y - r} A ${r} ${r} 0 0 1 ${xv - r} ${b.y} L ${b.x} ${b.y}`;
    }
    const xv = MARGIN;
    return `M ${a.x} ${a.y} L ${xv + r} ${a.y} A ${r} ${r} 0 0 0 ${xv} ${a.y + r} L ${xv} ${b.y - r} A ${r} ${r} 0 0 0 ${xv + r} ${b.y} L ${b.x} ${b.y}`;
  };

  return (
    <div className="metro" ref={box}>
      {!narrow && placed.length > 0 && (
        <>
          <svg className="metro-svg" width={width} height={height} aria-hidden="true">
            <defs>
              <filter id="metro-shadow" x="-10%" y="-10%" width="120%" height="140%">
                <feGaussianBlur stdDeviation="4" />
              </filter>
              {placed.slice(1).map((b, i) => {
                const a = placed[i];
                return a.line !== b.line ? (
                  <linearGradient key={b.id} id={`mg-${b.index}`} gradientUnits="userSpaceOnUse" x1="0" y1={a.y} x2="0" y2={b.y}>
                    <stop offset="0" stopColor={lineColor(a.line)} />
                    <stop offset="1" stopColor={lineColor(b.line)} />
                  </linearGradient>
                ) : null;
              })}
            </defs>
            {/* the shadow under the whole route, then each segment as a tube: colour with a dark rim, then a centred highlight */}
            <g className="metro-shadow" filter="url(#metro-shadow)" transform="translate(0 9)">
              {placed.slice(1).map((b, i) => <path key={b.id} d={trackPath(placed[i], b)} />)}
            </g>
            {placed.slice(1).map((b, i) => {
              const a = placed[i];
              const travelled = b.index <= nowIdx;
              const stroke = a.line !== b.line ? `url(#mg-${b.index})` : lineColor(b.line);
              const d = trackPath(a, b);
              return (
                <g key={b.id} className={`metro-track ${travelled ? "is-travelled" : ""}`}>
                  <path d={d} stroke={stroke} className="metro-track-body" />
                  <path d={d} className="metro-track-shine" />
                </g>
              );
            })}
          </svg>
          <ol className="metro-stations" aria-label="Roadmap" style={{ height, ["--cw" as string]: `${cardW}px` }}>
            {placed.map((s) => (
              <li key={s.id} ref={s.state === "now" ? nowRef : undefined}
                className={`metro-station metro-${s.state} ${s.edge === "left" ? "starts-right" : ""} ${selected === s.id ? "is-selected" : ""}`}
                style={{ left: s.x, top: s.y, ["--c" as string]: lineColor(s.line) }}>
                {s.first && <span className="metro-line-name" style={{ background: lineColor(s.line) }}>{lines[s.line].name}</span>}
                {s.state === "now" && <span className="metro-here">You are here</span>}
                <StationBody s={s} onSelect={onSelect} open={expanded.has(s.id)} onToggle={() => toggle(s.id)} />
              </li>
            ))}
          </ol>
        </>
      )}
      {narrow && (
        <ol className="metro-list" aria-label="Roadmap">
          {lines.map((l, li) => [
            <li key={`line-${l.name}`} className="metro-line-head"><span className="metro-line-name" style={{ background: lineColor(li) }}>{l.name}</span></li>,
            ...l.stations.map((s) => {
              const gi = all.indexOf(s);
              return (
                <li key={s.id} ref={s.state === "now" ? nowRef : undefined}
                  className={`metro-station metro-${s.state} ${gi <= nowIdx ? "is-travelled" : ""} ${selected === s.id ? "is-selected" : ""}`}
                  style={{ ["--c" as string]: lineColor(li) }}>
                  <StationBody s={s} onSelect={onSelect} open={expanded.has(s.id)} onToggle={() => toggle(s.id)} here />
                </li>
              );
            }),
          ])}
        </ol>
      )}
    </div>
  );
}

/*
 * A station: its dot, and a card whose title opens the chapter (or, on a track map, selects the topic) and whose
 * subtopics each open their own lesson step. "+N more" shows the rest in place.
 */
function StationBody({ s, onSelect, open, onToggle, here }: {
  s: Station; onSelect?: (id: string) => void; open: boolean; onToggle: () => void; here?: boolean;
}) {
  const topics = s.topics ?? [];
  const shown = open ? topics : topics.slice(0, MAX_TOPICS);
  const dot = <span className="metro-dot">{s.state === "done" ? "✓" : ""}</span>;
  return (
    <div className="metro-hit" onMouseMove={tilt} onMouseLeave={untilt}>
      <StationLink s={s} onSelect={onSelect} className="metro-dot-link" hidden>{dot}</StationLink>
      <div className="metro-card">
        <StationLink s={s} onSelect={onSelect} className="metro-head">
          <span className="metro-num">{s.number}{here && s.state === "now" && <span className="metro-here">You are here</span>}</span>
          <span className="metro-title">{s.title}</span>
        </StationLink>
        {shown.length > 0 && (
          <ul className="metro-topics">
            {shown.map((t) => (
              <li key={t.title}>
                {t.href ? <Link className="metro-topic" to={t.href}>{t.title}</Link> : <span className="metro-topic">{t.title}</span>}
              </li>
            ))}
          </ul>
        )}
        {topics.length > MAX_TOPICS && (
          <button type="button" className="metro-more" onClick={onToggle} aria-expanded={open}>
            {open ? "Show less" : `+${topics.length - MAX_TOPICS} more`}
          </button>
        )}
        {s.meta && <span className="metro-meta">{s.meta}</span>}
      </div>
    </div>
  );
}

// The card tilts a little towards the mouse (a light 3D touch); reduced motion turns it off in CSS.
function tilt(e: MouseEvent<HTMLElement>) {
  const el = e.currentTarget;
  const r = el.getBoundingClientRect();
  el.style.setProperty("--ry", `${((e.clientX - r.left) / r.width - 0.5) * 10}deg`);
  el.style.setProperty("--rx", `${(0.5 - (e.clientY - r.top) / r.height) * 8}deg`);
}
function untilt(e: MouseEvent<HTMLElement>) {
  e.currentTarget.style.removeProperty("--rx");
  e.currentTarget.style.removeProperty("--ry");
}

// The dot repeats the title's link for the mouse only (hidden from screen readers and the tab order).
function StationLink({ s, onSelect, className, hidden, children }: {
  s: Station; onSelect?: (id: string) => void; className: string; hidden?: boolean; children: ReactNode;
}) {
  const a11y = hidden ? { "aria-hidden": true, tabIndex: -1 } : { "aria-label": `${s.number} ${s.title}` };
  if (s.href) return <Link className={className} to={s.href} {...a11y}>{children}</Link>;
  return <button type="button" className={className} onClick={() => onSelect?.(s.id)} {...a11y}>{children}</button>;
}
