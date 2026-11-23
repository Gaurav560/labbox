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
export function SketchSteps({ title, steps, label, intro = "Press Play to watch it happen, one step at a time." }: { title: string; steps: PlayStep[]; label: string; intro?: string }) {
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

  // A quiet vertical timeline (owner: "cool, minimal, soothing"): a thin rail with one small circle per
  // step and the text beside it. The rail fills as the steps run, a soft band slides to the step being
  // run, finished steps get a tick, and the ones still to come stay faint.
  const W = 440, ROW = 40, TOP = 50, NODE_X = 26, TEXT_X = 50;
  const y = (i: number) => TOP + i * ROW + ROW / 2;
  const height = TOP + steps.length * ROW + 6;
  const done = at === last;
  const play = () => {
    if (playing) return setPlaying(false);
    if (done) setAt(-1);
    setPlaying(true);
  };
  const by = (fn: () => void) => () => { setPlaying(false); fn(); };
  const railLen = y(last) - y(0);
  const filled = at <= 0 ? 0 : (y(at) - y(0)) / railLen;

  return (
    <div className="sketch-play">
      <svg viewBox={`0 0 ${W} ${height}`} role="img" aria-label={label} className="sketch tl">
        <text className="tl-title" x={NODE_X - 8} y={24}>{title}</text>
        <line className="tl-rule" x1={NODE_X - 8} y1={36} x2={W - 12} y2={36} />
        <rect className="tl-band" x={8} y={0} width={W - 16} height={ROW - 6} rx={9}
          style={{ transform: `translateY(${(at < 0 ? y(0) : y(at)) - (ROW - 6) / 2}px)`, opacity: at < 0 ? 0 : 1 }} />
        <rect className="tl-rail" x={NODE_X - 1} y={y(0)} width={2} height={railLen} rx={1} />
        <rect className="tl-rail tl-rail-done" x={NODE_X - 1} y={y(0)} width={2} height={railLen} rx={1}
          style={{ transform: `scaleY(${filled})` }} />
        {steps.map((s, i) => {
          const state = i === at ? "now" : i < at ? "done" : at < 0 ? "idle" : "next";
          return (
            <g key={s.label} className={`tl-step tl-${state}`}>
              <circle className="tl-node" cx={NODE_X} cy={y(i)} r={8} />
              {state === "done" && <path className="tl-tick" d={`M${NODE_X - 3.5} ${y(i)} l2.5 2.5 l4.5 -5`} />}
              <text className="tl-text" x={TEXT_X} y={y(i) + 5}>{s.label}</text>
            </g>
          );
        })}
      </svg>
      <p className="sketch-says" aria-live="polite">
        {at < 0 ? intro : <><b>Step {at + 1} of {steps.length}.</b> {steps[at].says}</>}
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

/** The Play, Pause, Back and Next state shared by playing diagrams: -1 means nothing has started yet. */
function usePlayer(count: number) {
  const [at, setAt] = useState(-1);
  const [playing, setPlaying] = useState(false);
  const last = count - 1;
  useEffect(() => {
    if (!playing) return;
    if (at >= last) {
      setPlaying(false);
      return;
    }
    const t = setTimeout(() => setAt((a) => Math.min(last, a + 1)), at < 0 ? 300 : PLAY_MS);
    return () => clearTimeout(t);
  }, [playing, at, last]);
  const done = at === last;
  const play = () => {
    if (playing) return setPlaying(false);
    if (done) setAt(-1);
    setPlaying(true);
  };
  const by = (fn: () => void) => () => { setPlaying(false); fn(); };
  return { at, playing, done, play, restart: by(() => setAt(-1)), back: by(() => setAt(Math.max(-1, at - 1))), next: by(() => setAt(Math.min(last, at + 1))) };
}

function PlayerControls({ p }: { p: ReturnType<typeof usePlayer> }) {
  return (
    <div className="trace-controls">
      <button className="trace-play" onClick={p.play} aria-pressed={p.playing}>{p.playing ? "⏸ Pause" : p.done ? "↻ Watch again" : "▶ Play"}</button>
      <span className="spacer" />
      <button className="btn btn-small btn-ghost" onClick={p.restart} disabled={p.at < 0}>Restart</button>
      <button className="btn btn-small btn-ghost" onClick={p.back} disabled={p.at < 0}>◀ Back</button>
      <button className="btn btn-small trace-next" onClick={p.next} disabled={p.done}>Next ▶</button>
    </div>
  );
}

/** One hand-drawn oval of a nested (Euler) diagram, with its label near its top edge. */
function NestedOval({ cx, cy, rx, ry, label, depth, state, seed, centreLabel }: {
  cx: number; cy: number; rx: number; ry: number; label: string; depth: number; state: string; seed: number; centreLabel: boolean;
}) {
  const shape = useMemo(() => gen.ellipse(cx, cy, rx * 2, ry * 2, { ...BASE, seed, fill: "currentColor" }), [cx, cy, rx, ry, seed]);
  return (
    <g className={`nest nest-c${depth % 4} nest-${state}`} style={{ transformOrigin: `${cx}px ${cy + ry}px` }}>
      {paths(shape)}
      <text className="nest-label" x={cx} y={centreLabel ? cy + 5 : cy - ry + 21} textAnchor="middle">{label}</text>
    </g>
  );
}

/**
 * A diagram of sets inside sets (an Euler diagram), drawn as hand-drawn ovals, each a little above the bottom
 * of the one around it and well below its top, so every label has room above the next oval. Play lights them up from the biggest to the smallest; the oval
 * being explained is outlined and its label bold, the ones not reached yet stay faint.
 * Each step's `label` is written on its oval (keep it short), `says` goes in the line under the drawing.
 */
export function SketchNested({ title, steps, label, intro = "Press Play to go from the biggest set to the smallest." }: {
  title: string; steps: PlayStep[]; label: string; intro?: string;
}) {
  const p = usePlayer(steps.length);
  const W = 460, TOP = 46, BOTTOM_PAD = 10;
  const n = steps.length;
  const outerRy = 30 + n * 30, outerRx = 214;
  const height = TOP + outerRy * 2 + BOTTOM_PAD;
  const bottom = TOP + outerRy * 2;
  return (
    <div className="sketch-play">
      <svg viewBox={`0 0 ${W} ${height}`} role="img" aria-label={label} className="sketch tl">
        <text className="tl-title" x={18} y={24}>{title}</text>
        <line className="tl-rule" x1={18} y1={36} x2={W - 12} y2={36} />
        {steps.map((s, i) => {
          // Each oval starts 30 below the one around it (room for that one's label) and ends 14 above its bottom.
          const top = TOP + i * 30, end = bottom - i * 14;
          const ry = (end - top) / 2;
          const rx = outerRx * (ry / outerRy) ** 0.8; // the small ovals get rounder, so their labels still fit
          const state = p.at < 0 ? "idle" : i === p.at ? "now" : i < p.at ? "lit" : "off";
          return (
            <NestedOval key={s.label} cx={W / 2} cy={top + ry} rx={rx} ry={ry} label={s.label} depth={i}
              state={state} seed={31 + i * 7} centreLabel={i === n - 1} />
          );
        })}
      </svg>
      <p className="sketch-says" aria-live="polite">
        {p.at < 0 ? intro : <><b>Step {p.at + 1} of {steps.length}.</b> {steps[p.at].says}</>}
      </p>
      <PlayerControls p={p} />
    </div>
  );
}
