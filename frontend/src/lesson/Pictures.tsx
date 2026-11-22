import type { ReactNode } from "react";
import { Card, Hand, Ink, Svg } from "./PicturePrimitives";
import * as js from "./JavaScriptPictures";

/*
 * Small pictures for the everyday images a lesson uses to explain an idea (Content standard, section 3:
 * "picture it"). A chapter asks for one with :::picture{name="recipe-card"}; the text inside becomes the
 * caption. Both themes share the same printed labels and SVG layout. Most pictures hold no code, so one drawing
 * serves every language; a picture that shows code takes it from the chapter (code='phones["Riya"]'),
 * draws it in the code font (pc-code), and the validator checks that the same code is in a code block of
 * that step: learners never copy from a drawing. JavaScript chapters also name the teaching concept
 * on each picture, so the browser test can verify coverage across the related steps.
 */

interface P { code?: string }

/** A function or method is a recipe card: a name, what it needs, the steps, and what it gives back. */
function RecipeCard() {
  const rows: [number, string, string][] = [
    [36, "Lemon rice", "name"],
    [68, "needs: rice, lemon", "inputs"],
    [96, "1. boil 2. add 3. pour", "body"],
    [124, "gives: a plate of lemon rice", "return"],
  ];
  return (
    <Svg label="A recipe card mapped to the parts of a function: name, inputs, body and return value">
      <Card x={8} y={10} w={190} h={128} />
      <rect className="pc-band" x={10} y={12} width={186} height={34} rx={8} />
      {rows.map(([y, text, part], i) => (
        <g key={part}>
          <Hand x={22} y={y} kind={i === 0 ? "title" : "hand"}>{text}</Hand>
          <Ink d={`M204 ${y - 5} Q218 ${y - 9} 234 ${y - 5}`} />
          <Hand x={240} y={y} kind="label">{part}</Hand>
        </g>
      ))}
    </Svg>
  );
}

/** Variables are labelled jars: the label is the name, the contents the value, the jar's shape its type. */
function LabelledJars() {
  const jars: [number, string, string, string][] = [
    [20, "age", "17", "whole number"],
    [124, "price", "12.50", "decimal"],
    [228, "name", "Riya", "text"],
  ];
  return (
    <Svg label="Three labelled jars: age holds 17, price holds 12.50, name holds Riya; the age and price are numbers, the name is text">
      {jars.map(([x, name, value, type]) => (
        <g key={name}>
          <path className="pc-ink" d={`M${x + 8} 30 L${x + 64} 30 L${x + 70} 46 L${x + 70} 112 Q${x + 70} 120 ${x + 62} 120 L${x + 10} 120 Q${x + 2} 120 ${x + 2} 112 L${x + 2} 46 Z`} />
          <rect className="pc-band" x={x + 8} y={50} width={56} height={22} rx={4} />
          <Hand x={x + 36} y={66} kind="label" anchor="middle">{name}</Hand>
          <Hand x={x + 36} y={102} anchor="middle">{value}</Hand>
          <Hand x={x + 36} y={142} anchor="middle">{type}</Hand>
        </g>
      ))}
    </Svg>
  );
}

/** A decision is a fork in the road: one question, and the answer picks the path. */
function ForkInRoad() {
  return (
    <Svg label="A signpost asks: marks 80 or more? The yes path leads to A, the no path to the next question">
      <Ink d="M40 140 Q60 100 100 82" plain />
      <Ink d="M100 82 Q150 50 220 34" />
      <Ink d="M100 82 Q160 100 220 118" />
      <rect className="pc-band" x={14} y={34} width={134} height={28} rx={5} />
      <Hand x={22} y={54}>marks 80 or more?</Hand>
      <Hand x={228} y={38} kind="label">yes: "A"</Hand>
      <Hand x={228} y={122} kind="label">no: ask again</Hand>
    </Svg>
  );
}

/** A loop is laps around a track: the same steps again, with a counter, until the finish rule says stop. */
function RunningTrack() {
  return (
    <Svg label="A running track: each lap repeats the same steps and adds one to the lap counter, until the stop rule is met">
      <rect className="pc-card" x={20} y={24} width={180} height={100} rx={50} />
      <rect className="pc-ink" x={46} y={48} width={128} height={52} rx={26} />
      <Ink d="M110 24 Q150 22 168 30" />
      <Hand x={84} y={80} kind="label">lap 3</Hand>
      <Hand x={214} y={50}>same steps,</Hand>
      <Hand x={214} y={70}>every lap</Hand>
      <Hand x={214} y={104} kind="label">stop when</Hand>
      <Hand x={214} y={124} kind="label">laps = 5</Hand>
    </Svg>
  );
}

/** A string is beads on a thread: every character has a numbered position, starting at 0. */
function BeadsOnString() {
  const letters = ["r", "e", "d", " ", "c", "u", "p"];
  return (
    <Svg label="The text red cup as beads on a thread, positions 0 to 6; the space is a bead too">
      <Ink d="M8 70 L312 70" plain />
      {letters.map((ch, i) => (
        <g key={i}>
          <circle className={ch === " " ? "pc-cell" : "pc-bead"} cx={36 + i * 42} cy={70} r={17} />
          <Hand x={36 + i * 42} y={77} anchor="middle" kind="title">{ch === " " ? "_" : ch}</Hand>
          <Hand x={36 + i * 42} y={112} anchor="middle" kind="label">{i}</Hand>
        </g>
      ))}
      <Hand x={8} y={28}>positions start at 0;</Hand>
      <Hand x={160} y={28}>a space is a bead too</Hand>
      <Hand x={8} y={140}>7 beads, so the last is number 6</Hand>
    </Svg>
  );
}

/** A list or array is an egg box: numbered slots in a row, starting at 0. */
function EggBox() {
  const marks = [72, 45, 90, 66];
  return (
    <Svg label="An egg box with four slots numbered 0 to 3, holding 72, 45, 90 and 66">
      <Card x={14} y={34} w={240} h={66} />
      {marks.map((m, i) => (
        <g key={i}>
          <ellipse className="pc-cell" cx={46 + i * 58} cy={67} rx={24} ry={22} />
          <Hand x={46 + i * 58} y={74} anchor="middle" kind="title">{m}</Hand>
          <Hand x={46 + i * 58} y={124} anchor="middle" kind="label">{i}</Hand>
        </g>
      ))}
      <Hand x={14} y={22}>slots numbered from 0</Hand>
      <Hand x={262} y={74}>len 4</Hand>
      <Hand x={14} y={142}>last slot: length minus one</Hand>
    </Svg>
  );
}

/** An array is a form with a fixed number of boxes; an ArrayList is a notebook that takes another line. */
function NotebookVsForm({ code }: P) {
  return (
    <Svg label="Left: a form with exactly five boxes, all full. Right: a notebook where a new line can always be added">
      <Hand x={8} y={24} kind="label">fixed: 5 boxes</Hand>
      {[0, 1, 2, 3, 4].map((i) => (
        <rect key={i} className="pc-cell" x={10 + i * 27} y={36} width={22} height={22} rx={4} />
      ))}
      <Hand x={10} y={88}>a 6th one?</Hand>
      <Hand x={10} y={110}>no room</Hand>
      <Hand x={170} y={24} kind="label">grows</Hand>
      <Card x={168} y={34} w={144} h={108} />
      {[0, 1, 2, 3].map((i) => (
        <line key={i} className="pc-rule" x1={180} y1={60 + i * 24} x2={300} y2={60 + i * 24} />
      ))}
      <rect className="pc-mark" x={182} y={64} width={110} height={20} rx={4} />
      <Hand x={186} y={55}>72</Hand>
      {code ? <Hand x={186} y={79} kind="code">{code}</Hand> : <Hand x={186} y={80}>+ one more</Hand>}
    </Svg>
  );
}

/** A map or dictionary is a phone book: you look a key up to find its value. */
function PhoneBook({ code }: P) {
  const rows = [["Riya", "98201 11111"], ["Arjun", "99300 22222"], ["Meera", "90040 33333"]];
  return (
    <Svg label="A phone book with names as keys and numbers as values; looking up Riya finds her number">
      <Card x={142} y={10} w={172} h={130} />
      <Hand x={152} y={34} kind="label">key</Hand>
      <Hand x={210} y={34} kind="label">value</Hand>
      <Ink d="M202 16 L203 132" plain />
      <rect className="pc-mark" x={146} y={42} width={164} height={28} rx={6} />
      {rows.map(([k, v], i) => (
        <g key={k}>
          <Hand x={152} y={62 + i * 28}>{k}</Hand>
          <Hand x={210} y={62 + i * 28}>{v}</Hand>
        </g>
      ))}
      {code ? <Hand x={4} y={52} kind="code">{code}</Hand> : <Hand x={4} y={52} kind="label">look up "Riya"</Hand>}
      <Ink d="M60 62 Q100 76 144 58" />
    </Svg>
  );
}

/** A set is a guest list at the door: each name once, and order does not matter. */
function GuestList() {
  return (
    <Svg label="A guest list: Riya, Arjun and Meera are on it once each; a second Riya is turned away">
      <Card x={10} y={14} w={150} h={122} />
      <Hand x={24} y={38} kind="title">Guest list</Hand>
      {["Riya", "Arjun", "Meera"].map((n, i) => (
        <Hand key={n} x={28} y={68 + i * 24}>{`✓ ${n}`}</Hand>
      ))}
      <Hand x={184} y={60} kind="label">Riya again?</Hand>
      <Hand x={184} y={82}>already in:</Hand>
      <Hand x={184} y={102}>stays one Riya</Hand>
      <Ink d="M180 66 Q150 76 120 70" />
    </Svg>
  );
}

/** A class is a blueprint; objects are the houses built from it, each with its own contents. */
function BlueprintHouses() {
  const house = (x: number, label: string, detail: string) => (
    <g>
      <path className="pc-ink" d={`M${x} 92 L${x + 32} 66 L${x + 64} 92 L${x + 64} 132 L${x} 132 Z`} />
      <Hand x={x + 32} y={112} anchor="middle" kind="label">{label}</Hand>
      <Hand x={x + 32} y={143} anchor="middle">{detail}</Hand>
    </g>
  );
  return (
    <Svg label="One blueprint, the class, and two houses built from it, the objects, each with its own owner and balance">
      <rect className="pc-band" x={8} y={10} width={120} height={50} rx={6} />
      <Hand x={18} y={32} kind="title">blueprint</Hand>
      <Hand x={18} y={52}>owner, balance</Hand>
      <Ink d="M130 40 Q160 46 172 76" />
      <Ink d="M130 34 Q220 30 248 70" />
      {house(150, "Riya", "balance 500")}
      {house(240, "Arjun", "balance 80")}
      <Hand x={8} y={90}>one class,</Hand>
      <Hand x={8} y={110}>many objects</Hand>
    </Svg>
  );
}

/** An interface is a wall socket: anything with the right plug fits, whatever is behind it. */
function PlugSocket({ code }: P) {
  return (
    <Svg label="A wall socket labelled area; a rectangle plug and a circle plug both fit, because both have the area plug">
      <rect className="pc-card" x={10} y={34} width={90} height={82} rx={12} />
      <circle className="pc-cell" cx={42} cy={75} r={6} />
      <circle className="pc-cell" cx={68} cy={75} r={6} />
      <Hand x={55} y={136} anchor="middle" kind={code ? "code" : "label"}>{code ?? "area()"}</Hand>
      <Hand x={10} y={22}>the socket: one shape</Hand>
      <Ink d="M190 52 Q150 58 108 70" />
      <Ink d="M190 104 Q150 96 108 82" />
      <rect className="pc-ink" x={196} y={36} width={56} height={34} rx={4} />
      <Hand x={224} y={58} anchor="middle">Rect</Hand>
      <circle className="pc-ink" cx={224} cy={108} r={28} />
      <Hand x={224} y={114} anchor="middle">Circle</Hand>
      <Hand x={262} y={58}>fits</Hand>
      <Hand x={262} y={112}>fits</Hand>
    </Svg>
  );
}

/** An exception is a fire alarm: normal work stops until someone whose job it is handles it. */
function FireAlarm() {
  return (
    <Svg label="A fire alarm rings in one room; work stops there and the alarm travels to the handler, who deals with it, and then work carries on">
      <Card x={10} y={40} w={96} h={70} />
      <Hand x={58} y={66} anchor="middle" kind="label">bad input</Hand>
      <Hand x={58} y={92} anchor="middle">work stops</Hand>
      <path className="pc-ink" d="M50 14 Q58 4 66 14 L66 30 L50 30 Z" />
      <Hand x={70} y={24}>ring!</Hand>
      <Ink d="M108 74 Q160 56 204 70" />
      <Card x={206} y={40} w={104} h={70} />
      <Hand x={258} y={66} anchor="middle" kind="label">the handler</Hand>
      <Hand x={258} y={92} anchor="middle">deals with it</Hand>
      <Hand x={150} y={140} anchor="middle">then the program carries on</Hand>
    </Svg>
  );
}

/** Go's errors: a function hands back two things, the result and a note that says whether it worked. */
function ResultAndNote() {
  return (
    <Svg label="A function hands back two things: a parcel with the result and a slip saying whether anything went wrong">
      <Card x={10} y={46} w={92} h={60} />
      <Hand x={56} y={82} anchor="middle" kind="label">function</Hand>
      <Ink d="M104 66 Q150 40 196 44" />
      <Ink d="M104 88 Q150 112 196 108" />
      <rect className="pc-band" x={198} y={26} width={110} height={36} rx={6} />
      <Hand x={208} y={50}>the result</Hand>
      <rect className="pc-mark" x={198} y={92} width={110} height={34} rx={6} />
      <Hand x={208} y={114}>the error note</Hand>
      <Hand x={10} y={24}>two things come back:</Hand>
      <Hand x={10} y={140}>no note (nil) means it worked</Hand>
    </Svg>
  );
}

/** A reference or pointer is an address on an envelope: two envelopes, one house. */
function EnvelopeAddress() {
  return (
    <Svg label="Two envelopes carry the same address, so both lead to one house; changing the house is seen through either envelope">
      <rect className="pc-ink" x={10} y={8} width={110} height={42} rx={4} />
      <path className="pc-ink" d="M10 8 L65 33 L120 8" />
      <Hand x={18} y={68}>a: 12 MG Road</Hand>
      <rect className="pc-ink" x={10} y={78} width={110} height={42} rx={4} />
      <path className="pc-ink" d="M10 78 L65 103 L120 78" />
      <Hand x={18} y={140}>b: 12 MG Road</Hand>
      <Ink d="M124 30 Q190 40 226 76" />
      <Ink d="M124 100 Q190 104 226 92" />
      <path className="pc-ink" d="M232 70 L270 42 L308 70 L308 126 L232 126 Z" />
      <Hand x={270} y={104} anchor="middle" kind="label">one house</Hand>
    </Svg>
  );
}

/** A stream or pipeline is a conveyor belt: stations filter, change and sort; a box at the end collects. */
function ConveyorBelt() {
  return (
    <Svg label="A conveyor belt carries marks past a filter station, which keeps 40 or more, and a box at the end collects the result">
      <rect className="pc-card" x={8} y={86} width={304} height={22} rx={11} />
      {[30, 70, 110].map((x, i) => (
        <g key={x}>
          <rect className="pc-cell" x={x - 14} y={58} width={28} height={26} rx={4} />
          <Hand x={x} y={77} anchor="middle">{["72", "30", "90"][i]}</Hand>
        </g>
      ))}
      <rect className="pc-band" x={146} y={30} width={70} height={52} rx={6} />
      <Hand x={181} y={54} anchor="middle" kind="label">filter</Hand>
      <Hand x={181} y={74} anchor="middle">40 or more</Hand>
      <path className="pc-ink" d="M250 60 L300 60 L294 96 L256 96 Z" />
      <Hand x={275} y={50} anchor="middle" kind="label">toList</Hand>
      <Hand x={8} y={140}>stations keep, change or sort</Hand>
    </Svg>
  );
}

/** A file is a stack of lines; a CSV line is a row cut into fields at the commas. */
function FileLines() {
  return (
    <Svg label="A file shown as a page of lines; one line, 2026-03-02,food,120, is cut at the commas into three fields">
      <Card x={10} y={10} w={130} h={130} />
      {[0, 1, 2, 3, 4].map((i) => (
        <line key={i} className="pc-rule" x1={22} y1={38 + i * 20} x2={128} y2={38 + i * 20} />
      ))}
      <rect className="pc-mark" x={20} y={40} width={110} height={18} rx={3} />
      <Hand x={22} y={32} kind="label">expenses.csv</Hand>
      <Ink d="M134 50 Q160 44 180 50" />
      {["2026-03-02", "food", "120"].map((f, i) => (
        <g key={f}>
          <rect className="pc-cell" x={184} y={30 + i * 34} width={110} height={26} rx={4} />
          <Hand x={192} y={49 + i * 34}>{f}</Hand>
        </g>
      ))}
      <Hand x={184} y={140}>cut at the commas</Hand>
    </Svg>
  );
}

/** Goroutines: two cooks in one kitchen get dinner ready sooner than one cook doing every dish in turn. */
function TwoCooks() {
  return (
    <Svg label="One cook makes rice, then dal, then roti in turn; three cooks make all three at the same time and finish much sooner">
      <Hand x={8} y={22} kind="label">one cook, one dish after another</Hand>
      {["rice", "dal", "roti"].map((d, i) => (
        <g key={d}>
          <rect className="pc-cell" x={10 + i * 96} y={32} width={90} height={24} rx={5} />
          <Hand x={55 + i * 96} y={49} anchor="middle">{d}</Hand>
        </g>
      ))}
      <Hand x={8} y={84} kind="label">three cooks, all at once</Hand>
      {["rice", "dal", "roti"].map((d, i) => (
        <g key={d}>
          <rect className="pc-band" x={10} y={92 + i * 18} width={90} height={15} rx={4} />
          <Hand x={108} y={104 + i * 18}>{d}</Hand>
        </g>
      ))}
      <Hand x={168} y={112}>a third</Hand>
      <Hand x={168} y={132}>of the time</Hand>
    </Svg>
  );
}

/** Hash codes are shelf numbers: a set finds an item by going to its shelf first, then comparing there. */
function LibraryShelves() {
  return (
    <Svg label="Library shelves numbered 1 to 4; the hash code says which shelf, and equals compares only the books on that shelf">
      {[0, 1, 2, 3].map((i) => (
        <g key={i}>
          <rect className={i === 2 ? "pc-mark" : "pc-cell"} x={150} y={14 + i * 32} width={160} height={26} rx={4} />
          <Hand x={160} y={33 + i * 32} kind="label">{`shelf ${i + 1}`}</Hand>
        </g>
      ))}
      <Hand x={232} y={97}>book, book</Hand>
      <Hand x={8} y={40}>hashCode():</Hand>
      <Hand x={8} y={60}>which shelf?</Hand>
      <Hand x={8} y={100}>equals():</Hand>
      <Hand x={8} y={120}>which book?</Hand>
      <Ink d="M96 52 Q130 70 146 88" />
    </Svg>
  );
}

/* ---- Story scenes: one small picture at the start of a chapter ---- */

/* ---- Main ideas ---- */

/** + adds numbers but glues text. */
function GlueVsAdd() {
  return (
    <Svg label="Two number blocks 2 and 2 add up to 4; two text tiles 2 and 2 are glued into 22">
      <Hand x={10} y={24} kind="label">numbers: add</Hand>
      <rect className="pc-cell" x={10} y={34} width={30} height={30} rx={4} />
      <rect className="pc-cell" x={60} y={34} width={30} height={30} rx={4} />
      <Hand x={20} y={55}>2</Hand><Hand x={70} y={55}>2</Hand><Hand x={44} y={55}>+</Hand>
      <Ink d="M96 49 L120 49" />
      <rect className="pc-mark" x={126} y={34} width={30} height={30} rx={4} />
      <Hand x={136} y={55} kind="title">4</Hand>
      <Hand x={10} y={96} kind="label">text: glue</Hand>
      <rect className="pc-band" x={10} y={106} width={30} height={30} rx={4} />
      <rect className="pc-band" x={60} y={106} width={30} height={30} rx={4} />
      <Hand x={20} y={127}>2</Hand><Hand x={70} y={127}>2</Hand><Hand x={44} y={127}>+</Hand>
      <Ink d="M96 121 L120 121" />
      <rect className="pc-mark" x={126} y={106} width={52} height={30} rx={4} />
      <Hand x={136} y={127} kind="title">22</Hand>
      <Hand x={200} y={60}>same sign,</Hand>
      <Hand x={200} y={82}>different job</Hand>
    </Svg>
  );
}

/** Money as whole paise: count coins, show rupees only at the end. */
function CoinJar() {
  return (
    <Svg label="A jar of 1999 paise coins, shown as 19 rupees 99 only when printed">
      <Ink d="M30 40 L110 40 L118 56 L118 128 Q118 136 110 136 L30 136 Q22 136 22 128 L22 56 Z" plain />
      {[40, 64, 88, 52, 76, 100].map((x, i) => <circle key={i} className="pc-cell" cx={x} cy={i < 3 ? 120 : 100} r={10} />)}
      <Hand x={34} y={30} kind="label">1999 paise</Hand>
      <Ink d="M126 88 Q170 80 200 88" />
      <rect className="pc-mark" x={204} y={70} width={104} height={32} rx={6} />
      <Hand x={214} y={93} kind="title">{"₹19.99"}</Hand>
      <Hand x={142} y={130}>whole paise first</Hand>
    </Svg>
  );
}

/** 5 and "5" look alike but are different kinds of thing. */
function NumberVsText() {
  return (
    <Svg label="A number 5 on a round coin and a text 5 on a paper tag look alike but are different; === says false">
      <circle className="pc-cell" cx={60} cy={70} r={32} />
      <Hand x={52} y={80} kind="title">5</Hand>
      <Hand x={30} y={128} kind="label">a number</Hand>
      <path className="pc-card" d="M170 46 L240 46 L256 70 L240 94 L170 94 Z" />
      <Hand x={194} y={78} kind="title">"5"</Hand>
      <Hand x={176} y={128} kind="label">text</Hand>
      <Hand x={110} y={74}>look alike,</Hand>
      <Hand x={110} y={96}>not the same</Hand>
    </Svg>
  );
}

/** && and || as switches: in a row both must be on; side by side either will do. */
function TwoSwitches() {
  return (
    <Svg label="Two switches in a row light the bulb only when both are on (and); two side by side light it when either is on (or)">
      <Hand x={10} y={22} kind="label">and: both on</Hand>
      <Ink d="M10 50 Q31 49 50 50 M70 50 Q85 49 100 50 M120 50 Q130 49 140 50" plain />
      <Ink d="M50 50 L68 40 M100 50 L118 40" plain />
      <circle className="pc-mark" cx={152} cy={50} r={11} />
      <Hand x={10} y={92} kind="label">or: either one</Hand>
      <Ink d="M10 116 L40 116 L40 104 L60 104 M80 104 L100 104 L100 116 M40 116 L40 132 L60 132 M80 132 L100 132 L100 116 L130 116" plain />
      <Ink d="M60 104 L78 96 M60 132 L78 124" plain />
      <circle className="pc-mark" cx={142} cy={116} r={11} />
      <Hand x={184} y={56}>in series</Hand>
      <Hand x={184} y={122}>in parallel</Hand>
    </Svg>
  );
}

/** for...of is a postman visiting every house on the street, in order. */
function Postman() {
  return (
    <Svg label="A postman walks down a street and visits every house in order, one after another">
      {[0, 1, 2, 3].map((i) => (
        <g key={i}>
          <path className="pc-ink" d={`M${20 + i * 74} 76 L${46 + i * 74} 56 L${72 + i * 74} 76 L${72 + i * 74} 110 L${20 + i * 74} 110 Z`} />
          <Hand x={40 + i * 74} y={100} kind="label">{String(i + 1)}</Hand>
        </g>
      ))}
      <Ink d="M20 128 Q160 140 300 128" />
      <Hand x={20} y={30}>every house, in order:</Hand>
      <Hand x={190} y={30} kind="label">one visit each</Hand>
    </Svg>
  );
}

/** An object is a filled-in form: each field has a label and a value. */
function FormCard() {
  return (
    <Svg label="An object drawn as a form card with three labelled fields: name juice, price 20, qty 2">
      <Card x={30} y={14} w={200} h={122} />
      {[["name", "juice"], ["price", "20"], ["qty", "2"]].map(([k, v], i) => (
        <g key={k}>
          <Hand x={44} y={46 + i * 34} kind="label">{`${k}:`}</Hand>
          <rect className="pc-cell" x={110} y={30 + i * 34} width={108} height={24} rx={4} />
          <Hand x={118} y={48 + i * 34}>{v}</Hand>
        </g>
      ))}
      <Hand x={240} y={60}>a label,</Hand>
      <Hand x={240} y={82}>an answer</Hand>
    </Svg>
  );
}

/** Copy, then change: write on the photocopy and the original stays clean. */
function Photocopy() {
  return (
    <Svg label="The original price tag 20 stays untouched; a photocopy is made and the copy is changed to 18">
      <Card x={10} y={30} w={110} h={90} />
      <Hand x={22} y={56} kind="label">original</Hand>
      <Hand x={22} y={90}>price 20</Hand>
      <Ink d="M126 74 Q160 60 190 74" />
      <Hand x={136} y={52}>copy</Hand>
      <Card x={196} y={30} w={116} h={90} />
      <Hand x={208} y={56} kind="label">the copy</Hand>
      <Hand x={208} y={90}>price</Hand>
      <Ink d="M250 84 L272 84" plain />
      <rect className="pc-mark" x={274} y={72} width={30} height={24} rx={4} />
      <Hand x={278} y={90}>18</Hand>
      <Hand x={10} y={142}>the original keeps its price</Hand>
    </Svg>
  );
}

/** Sorting by a rule: line people up, the rule says who goes first. */
function LineUp() {
  return (
    <Svg label="Words line up shortest first: fig, date, kiwi, apple, banana; ties go alphabetical">
      {[["fig", 22], ["date", 30], ["kiwi", 30], ["apple", 38], ["banana", 46]].map(([w, h], i) => (
        <g key={String(w)}>
          <rect className={i === 1 || i === 2 ? "pc-mark" : "pc-cell"} x={14 + i * 60} y={110 - Number(h) * 1.6} width={44} height={Number(h) * 1.6} rx={5} />
          <Hand x={16 + i * 60} y={132}>{String(w)}</Hand>
        </g>
      ))}
      <Hand x={14} y={24}>shorter first</Hand>
      <Hand x={180} y={24} kind="label">ties: a to z</Hand>
    </Svg>
  );
}

/** try and catch are a safety net: if the risky step fails, the net catches it. */
function SafetyNet() {
  return (
    <Svg label="An acrobat on a high wire, the try block; below is a safety net, the catch block, so a fall is caught and the show goes on">
      <Ink d="M10 40 Q160 42 310 40" plain />
      <circle className="pc-ink" cx={150} cy={26} r={7} />
      <Ink d="M150 33 l1 7" plain />
      <Hand x={14} y={30} kind="label">high wire</Hand>
      <path className="pc-card" d="M30 108 Q160 140 290 108" />
      {[60, 100, 140, 180, 220, 260].map((x) => <line key={x} className="pc-rule" x1={x} y1={110} x2={x + 14} y2={128} />)}
      <Hand x={14} y={102} kind="label">net</Hand>
      <Ink d="M160 46 Q166 80 160 112" />
      <Hand x={180} y={84}>a fall is caught</Hand>
      <Hand x={170} y={142}>the show goes on</Hand>
    </Svg>
  );
}

/** A private field is money behind the counter: only the clerk (the methods) can touch it. */
function BankCounter() {
  return (
    <Svg label="A bank counter with a window; the cash box behind it can only be reached through the clerk, the deposit and withdraw methods">
      <Ink d="M10 120 L310 120" plain />
      <rect className="pc-card" x={110} y={20} width={180} height={100} rx={6} />
      <rect className="pc-mark" x={196} y={74} width={70} height={36} rx={4} />
      <Hand x={204} y={97}>balance</Hand>
      <rect className="pc-cell" x={110} y={56} width={30} height={34} rx={4} />
      <Hand x={14} y={60} kind="label">pay in</Hand>
      <Hand x={14} y={84} kind="label">take out</Hand>
      <Ink d="M96 72 Q104 72 112 72" />
      <Hand x={150} y={46}>behind the counter</Hand>
      <Hand x={14} y={142}>only through the window, with its checks</Hand>
    </Svg>
  );
}

/** A promise is a token receipt: you get it now, the food comes later. */
function TokenReceipt() {
  return (
    <Svg label="A token receipt number 42 says pending now; later the order is ready, or it failed">
      <path className="pc-card" d="M20 14 L120 14 L120 132 L110 126 L100 132 L90 126 L80 132 L70 126 L60 132 L50 126 L40 132 L30 126 L20 132 Z" />
      <Hand x={34} y={44} kind="title">Token 42</Hand>
      <rect className="pc-mark" x={30} y={60} width={80} height={24} rx={4} />
      <Hand x={40} y={78}>pending</Hand>
      <Ink d="M128 60 Q170 40 204 46" />
      <Ink d="M128 90 Q170 110 204 106" />
      <Hand x={210} y={50} kind="label">ready: a value</Hand>
      <Hand x={210} y={110} kind="label">failed: an error</Hand>
      <Hand x={137} y={140}>token now, food later</Hand>
    </Svg>
  );
}

/** reduce is a funnel: many values go in, one comes out. */
function Funnel() {
  return (
    <Svg label="Numbers 120, 80 and 45 pour into a funnel and come out as one total, 245">
      {[["120", 30], ["80", 90], ["45", 150]].map(([v, x]) => (
        <g key={String(v)}>
          <rect className="pc-cell" x={Number(x)} y={14} width={46} height={26} rx={4} />
          <Hand x={Number(x) + 8} y={33}>{String(v)}</Hand>
        </g>
      ))}
      <Ink d="M20 52 L210 52 L130 102 L130 122 L100 122 L100 102 Z" plain />
      <rect className="pc-mark" x={86} y={124} width={58} height={24} rx={4} />
      <Hand x={96} y={142} kind="title">245</Hand>
      <Hand x={222} y={84}>many in,</Hand>
      <Hand x={222} y={106}>one out</Hand>
    </Svg>
  );
}

const PICTURES: Record<string, (p: P) => JSX.Element> = {
  "recipe-card": RecipeCard,
  "labelled-jars": LabelledJars,
  "fork-in-road": ForkInRoad,
  "running-track": RunningTrack,
  "beads-on-string": BeadsOnString,
  "egg-box": EggBox,
  "notebook-vs-form": NotebookVsForm,
  "phone-book": PhoneBook,
  "guest-list": GuestList,
  "blueprint-houses": BlueprintHouses,
  "plug-socket": PlugSocket,
  "fire-alarm": FireAlarm,
  "result-and-note": ResultAndNote,
  "envelope-address": EnvelopeAddress,
  "conveyor-belt": ConveyorBelt,
  "file-lines": FileLines,
  "two-cooks": TwoCooks,
  "library-shelves": LibraryShelves,
  "glue-vs-add": GlueVsAdd,
  "coin-jar": CoinJar,
  "number-vs-text": NumberVsText,
  "two-switches": TwoSwitches,
  postman: Postman,
  "form-card": FormCard,
  photocopy: Photocopy,
  "line-up": LineUp,
  "safety-net": SafetyNet,
  "bank-counter": BankCounter,
  "token-receipt": TokenReceipt,
  funnel: Funnel,
  "square-tiles": js.SquareTiles,
  "remainder-bowls": js.RemainderBowls,
  "case-lenses": js.CaseLenses,
  "trim-edges": js.TrimEdges,
  "initial-and-tail": js.InitialAndTail,
  "search-signs": js.SearchSigns,
  "cart-shelves": js.CartShelves,
  "rule-gate": js.RuleGate,
  "spoiled-total": js.SpoiledTotal,
  "parallel-tickets": js.ParallelTickets,
  "retry-stamps": js.RetryStamps,
  "file-ribbon": js.FileRibbon,
};

export default function Picture({ name, code, caption }: { name: string; code?: string; caption?: ReactNode }) {
  const Drawing = PICTURES[name];
  if (!Drawing) return null;
  return (
    <figure className="picture">
      <Drawing code={code} />
      {caption && <figcaption>{caption}</figcaption>}
    </figure>
  );
}
