import type { ReactNode } from "react";
import { Card, Hand, Ink, Svg } from "./PicturePrimitives";

// Repeated visual conventions make examples comparable across the course.
// A strip preserves order, a receipt groups amounts, and a fork separates outcomes.
interface StripProps {
  left: string;
  right: string[];
  y: number;
  marked?: number[];
}

function Strip({ left, right, y, marked = [] }: StripProps) {
  const width = Math.min(88, 208 / right.length);
  return <g>
    <Hand x={10} y={y + 21} kind="label">{left}</Hand>
    {right.map((value, index) => {
      const x = 109 + index * width;
      const selected = marked.includes(index);
      return <g key={index}>
        <rect x={x} y={y} width={width - 4} height={30} rx={5} className={selected ? "pc-mark" : "pc-cell"} />
        <Hand x={x + (width - 4) / 2} y={y + 21} anchor="middle">{value}</Hand>
        {selected && <Ink d={`M${x + 5} ${y + 34} q${width / 3} 3 ${width - 15} 0`} plain />}
      </g>;
    })}
  </g>;
}

function Board({ label, rows }: { label: string; rows: Omit<StripProps, "y">[] }) {
  return <Svg label={label}>
    {rows.map((row, i) => <Strip key={row.left} {...row} y={rows.length === 2 ? 32 + i * 58 : 12 + i * 47} />)}
  </Svg>;
}

function Fork({ label, input, paths }: { label: string; input: string; paths: [[string, string], [string, string]] }) {
  return <Svg label={label}>
    <Card x={6} y={55} w={95} h={40} /><Hand x={53} y={81} anchor="middle">{input}</Hand>
    {paths.map(([when, result], i) => {
      const y = i === 0 ? 42 : 112;
      return <g key={when}>
        <Ink d={`M102 75 Q132 75 162 ${y}`} />
        <rect className={i === 0 ? "pc-cell" : "pc-bead"} x={164} y={y - 29} width={151} height={54} rx={8} />
        <Hand x={175} y={y - 7} kind="label">{when}</Hand>
        <Hand x={175} y={y + 14}>{result}</Hand>
      </g>;
    })}
  </Svg>;
}

function Route({ label, stops, notes }: { label: string; stops: [string, string, string]; notes: [ReactNode, ReactNode, ReactNode] }) {
  return <Svg label={label}>
    <Ink d="M36 72 Q158 64 281 72" />
    {stops.map((stop, i) => <g key={i}>
      <circle className={i === 2 ? "pc-mark" : "pc-card"} cx={48 + i * 111} cy={71} r={9} />
      <Hand x={48 + i * 111} y={47} anchor="middle" kind="label">{stop}</Hand>
      <Hand x={48 + i * 111} y={107} anchor="middle">{notes[i]}</Hand>
    </g>)}
  </Svg>;
}

export function SquareTiles() {
  return (
    <Svg
      label="A square with four tiles on each side contains sixteen tiles.">
      {Array.from({ length: 16 }, (_, i) => <rect key={i} className="pc-cell" x={49 + (i % 4) * 23} y={21 + Math.floor(i / 4) * 23} width={22} height={22} />)}
      <Hand x={85} y={138}>4 across</Hand><Hand x={156} y={55}>4 rows</Hand>
      <Ink d="M157 78 Q176 87 202 87" /><Hand x={212} y={94} kind="label">16 tiles</Hand>
    </Svg>
  );
}

export function RemainderBowls() {
  return (
    <Svg
      label="Two bowls hold three counters each. A seventh counter sits outside both bowls.">
      {[18, 122].map(x => <g key={x}>
        <path className="pc-card" d={`M${x} 72 q40 100 82 0 Z`} />
        {[18,40,62].map(dx => <circle key={dx} className="pc-bead" cx={x+dx} cy={62} r={10} />)}
      </g>)}<circle className="pc-mark" cx={268} cy={61} r={13} />
      <Hand x={268} y={106} anchor="middle" kind="label">1 left</Hand>
    </Svg>
  );
}

export function CaseLenses() {
  return (
    <Board
      label="A capital A, lowercase a and capital T become a, a and t before the vowel test."
      rows={[
        { left: "letters", right: ["A", "a", "T"] },
        { left: "lowercase", right: ["a", "a", "t"] },
        { left: "vowels", right: ["yes", "yes", "no"], marked: [0, 1] },
      ]}
    />
  );
}

export function TrimEdges() {
  return (
    <Board
      label="Dots mark spaces around and inside the words red and cup. Only the outer dots disappear."
      rows={[
        { left: "typed", right: ["··", "red", "··", "cup", "··"] },
        { left: "trimmed", right: ["red", "··", "cup"], marked: [1] },
      ]}
    />
  );
}

export function InitialAndTail() {
  return (
    <Board
      label="The s and HARMA in sHARMA become S and harma, then join into Sharma."
      rows={[
        { left: "cut", right: ["s", "HARMA"] },
        { left: "change", right: ["S", "harma"], marked: [0] },
        { left: "join", right: ["Sharma"] },
      ]}
    />
  );
}

export function SearchSigns() {
  return (
    <Fork
      label="Cookie appears at slot one. One sign answers present and the other answers slot one."
      input="cookie"
      paths={[["is it there?", "yes"], ["where is it?", "slot 1"]]}
    />
  );
}

export function CartShelves() {
  return (
    <Board
      label="Cart slot zero holds jelly, 20 and two. Slot one holds bun, 15 and one."
      rows={[
        { left: "fields", right: ["name", "price", "qty"] },
        { left: "slot 0", right: ["jelly", "20", "2"] },
        { left: "slot 1", right: ["bun", "15", "1"] },
      ]}
    />
  );
}

export function RuleGate() {
  return (
    <Fork
      label="A gate labelled mark sends 45 to yes and 30 to no under a pass threshold of 40."
      input="mark"
      paths={[["45 arrives", "yes, passes"], ["30 arrives", "no, below 40"]]}
    />
  );
}

export function SpoiledTotal({ code }: { code?: string }) {
  return (
    <Route
      label="The text x converts to NaN. Adding five still gives NaN."
      stops={["text", "convert", "add five"]}
      notes={["x", "invalid", code ? <tspan className="pc-code">{code}</tspan> : "still invalid"]}
    />
  );
}

export function ParallelTickets() {
  return (
    <Svg
      label="Two lanes share a timeline. The waiting function pauses between asking and resuming while another lane continues working.">
      <Hand x={7} y={48}>function</Hand><Ink d="M86 42 q19 -2 38 0 M211 42 q42 -2 84 0" /><path className="pc-rule" strokeDasharray="4 4" d="M127 42 H208" />
      <Hand x={167} y={30} anchor="middle" kind="label">waiting</Hand>
      <Hand x={7} y={106}>other work</Hand><Ink d="M87 98 Q191 103 295 98" />
      <Hand x={94} y={139}>time runs left to right</Hand>
    </Svg>
  );
}

export function RetryStamps() {
  return (
    <Svg label="Three dated attempt stamps show failure, failure, then success. The successful result ends the attempts.">
      {["failed", "failed", "success"].map((result, i) => {
        const x = 57 + i * 102;
        return <g key={i}>
          <circle className={i === 2 ? "pc-mark" : "pc-card"} cx={x} cy={65} r={34} />
          <Ink d={i === 2 ? `M${x - 15} 64 l11 12 21 -25` : `M${x - 11} 53 l22 23 m0 -23 l-22 23`} plain />
          <Hand x={x} y={21} anchor="middle">try {i + 1}</Hand>
          <Hand x={x} y={128} anchor="middle" kind="label">{result}</Hand>
        </g>;
      })}
    </Svg>
  );
}

export function FileRibbon() {
  return (
    <Svg label="A text file unrolls as one long ribbon. Cutting at the line breaks separates the header and the data rows.">
      <path className="pc-card" d="M12 30 q14 -19 30 0 h262 v35 H42 Q12 69 12 49 Z" />
      <Ink d="M42 30 q-12 11 -8 28" plain />
      <Hand x={51} y={54}>header</Hand><Hand x={140} y={54}>food row</Hand><Hand x={224} y={54}>rent row</Hand>
      {[122, 211].map(x => <path key={x} className="pc-rule" strokeDasharray="4 3" d={`M${x} 25 v46`} />)}
      <Ink d="M126 108 Q125 92 122 72 M204 108 Q208 87 211 72" />
      <Hand x={164} y={136} anchor="middle" kind="label">cut at the line breaks</Hand>
    </Svg>
  );
}

