import { useEffect, useMemo, useState } from "react";
import rough from "roughjs";
import type { Options } from "roughjs/bin/core";

/*
 * Hand-drawn diagrams, in the look of Excalidraw and eraser.io (the owner's choice, 21 November): rough.js
 * draws slightly wobbly outlines and arrows on plain, calm fills; labels use the normal text font (the
 * owner found handwriting and hatched fills tiring to read); code stays in the code font. Shapes come out as SVG paths with class names, and CSS colours them,
 * so they follow the light and dark themes. A fixed seed per shape keeps each drawing the same on every render.
 *
 * SketchSteps is a diagram that plays: a list of steps lights up one at a time (Play, Back, Next), a dot
 * travels down the arrow to the next box, and a line under the drawing says what is happening now.
 */

const gen = rough.generator();

type Tone = "plain" | "accent" | "now" | "done" | "dim";

function paths(drawable: ReturnType<typeof gen.rectangle>) {
  // Outline sets become strokes; hachure sets are the fill lines (also strokes, in the fill colour).
  return drawable.sets.map((set, i) => (
    <path key={i} d={gen.opsToPath(set)} className={set.type === "fillSketch" ? "sk-fill" : set.type === "fillPath" ? "sk-solid" : "sk-line"} />
  ));
}

const BASE: Options = { roughness: 1.1, bowing: 1.2, strokeWidth: 1.6, fillStyle: "solid" }; // plain fills: no lines behind the text (owner)

export function SketchBox({ x, y, w, h, label, tone = "plain", code, seed }: {
  x: number; y: number; w: number; h: number; label: string; tone?: Tone; code?: boolean; seed: number;
}) {
  const shape = useMemo(() => gen.rectangle(x, y, w, h, { ...BASE, seed, fill: "currentColor" }), [x, y, w, h, seed]);
  return (
    <g className={`sk-box sk-${tone}`}>
      {paths(shape)}
      <text className={code ? "sk-code" : "sk-hand"} x={x + w / 2} y={y + h / 2 + 5} textAnchor="middle">{label}</text>
    </g>
  );
}

export function SketchArrow({ x1, y1, x2, y2, seed, tone = "plain" }: { x1: number; y1: number; x2: number; y2: number; seed: number; tone?: Tone }) {
  const shape = useMemo(() => {
    const a = Math.atan2(y2 - y1, x2 - x1);
    const head = (d: number) => [x2 - 9 * Math.cos(a + d), y2 - 9 * Math.sin(a + d)] as const;
    const [hx1, hy1] = head(0.5);
    const [hx2, hy2] = head(-0.5);
    const o = { ...BASE, seed, roughness: 0.9 };
    return [gen.line(x1, y1, x2, y2, o), gen.line(x2, y2, hx1, hy1, o), gen.line(x2, y2, hx2, hy2, o)];
  }, [x1, y1, x2, y2, seed]);
  return <g className={`sk-arrow sk-${tone}`}>{shape.map((s, i) => <g key={i}>{paths(s)}</g>)}</g>;
}

const PLAY_MS = 1600; // one step every 1.6 seconds: time to read the line under the drawing

export interface PlayStep { label: string; says: string }

/** A header box, then the steps one under the other; Play lights them up in order. */
export function SketchSteps({ title, steps, label }: { title: string; steps: PlayStep[]; label: string }) {
  const [at, setAt] = useState(-1); // -1: nothing started yet
  const [playing, setPlaying] = useState(false);
  const last = steps.length - 1;
  useEffect(() => {
    if (!playing) return;
    if (at >= last) {
      setPlaying(false);
      return;
    }
    const t = setTimeout(() => setAt((a) => Math.min(last, a + 1)), at < 0 ? 300 : PLAY_MS);
    return () => clearTimeout(t);
  }, [playing, at, last]);

  const W = 440, BOX_H = 30, GAP = 18, TOP = 10, FIRST = TOP + 34 + GAP;
  const y = (i: number) => FIRST + i * (BOX_H + GAP);
  const height = y(steps.length) - GAP + 8;
  const done = at === last;
  const play = () => {
    if (playing) return setPlaying(false);
    if (done) setAt(-1);
    setPlaying(true);
  };
  const by = (fn: () => void) => () => { setPlaying(false); fn(); };
  const dotY = at < 0 ? TOP + 34 : y(at) + BOX_H / 2;

  return (
    <div className="sketch-play">
      <svg viewBox={`0 0 ${W} ${height}`} role="img" aria-label={label} className="sketch">
        <SketchBox x={10} y={TOP} w={W - 20} h={34} label={title} tone="accent" code seed={7} />
        {steps.map((s, i) => {
          const tone: Tone = i === at ? "now" : i < at ? "done" : at < 0 ? "plain" : "dim";
          const top = i === 0 ? TOP + 34 : y(i - 1) + BOX_H;
          return (
            <g key={s.label}>
              <SketchArrow x1={W / 2} y1={top + 2} x2={W / 2} y2={y(i) - 2} seed={20 + i} tone={i <= at ? "done" : "plain"} />
              <SketchBox x={30} y={y(i)} w={W - 60} h={BOX_H} label={s.label} tone={tone} seed={40 + i} />
            </g>
          );
        })}
        {/* The dot that travels down to the step being run (CSS moves it; still when motion is reduced). */}
        <circle className="sk-dot" cx={18} cy={0} r={6} style={{ transform: `translateY(${dotY}px)`, opacity: at < 0 ? 0 : 1 }} />
      </svg>
      <p className="sketch-says" aria-live="polite">
        {at < 0 ? "Press Play to watch the app start, one step at a time." : <><b>Step {at + 1} of {steps.length}.</b> {steps[at].says}</>}
      </p>
      <div className="trace-controls">
        <button className="trace-play" onClick={play} aria-pressed={playing}>{playing ? "⏸ Pause" : done ? "↻ Watch again" : "▶ Play"}</button>
        <span className="spacer" />
        <button className="btn btn-small btn-ghost" onClick={by(() => setAt(-1))} disabled={at < 0}>Restart</button>
        <button className="btn btn-small btn-ghost" onClick={by(() => setAt(Math.max(-1, at - 1)))} disabled={at < 0}>◀ Back</button>
        <button className="btn btn-small trace-next" onClick={by(() => setAt(Math.min(last, at + 1)))} disabled={done}>Next ▶</button>
      </div>
    </div>
  );
}
