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

function Ledger({ label, heading, entries }: { label: string; heading: string; entries: [string, string][] }) {
  return <Svg label={label}>
    <path className="pc-card" d="M29 7 H290 V138 l-10 -4 -10 4 -10 -4 -10 4 -10 -4 -10 4 -10 -4 -10 4 -10 -4 -10 4 H29 Z" />
    <Hand x={48} y={31} kind="title">{heading}</Hand>
    <Ink d="M45 37 Q154 40 273 37" plain />
    {entries.map(([key, value], i) => <g key={key}>
      <Hand x={48} y={62 + i * 30}>{key}</Hand>
      <Hand x={268} y={62 + i * 30} anchor="end" kind={i === entries.length - 1 ? "label" : "hand"}>{value}</Hand>
    </g>)}
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

function Ruler({ label, ticks, notes, marked }: { label: string; ticks: string[]; notes: string[]; marked: number[] }) {
  return <Svg label={label}>
    <Ink d="M14 74 Q156 76 305 74" />
    {ticks.map((tick, i) => {
      const x = 38 + i * (243 / (ticks.length - 1));
      return <g key={tick}>
        <path className="pc-ink" d={`M${x} 67 v16`} />
        {marked.includes(i) && <circle className="pc-mark" cx={x} cy={74} r={10} />}
        <Hand x={x} y={53} anchor="middle" kind="title">{tick}</Hand>
        <Hand x={x} y={112} anchor="middle">{notes[i]}</Hand>
      </g>;
    })}
  </Svg>;
}

function Bars({ label, items }: { label: string; items: [string, number][] }) {
  const scale = 147 / Math.max(...items.map(([, value]) => value));
  return <Svg label={label}>
    {items.map(([name, value], i) => <g key={name}>
      <Hand x={9} y={41 + i * 36}>{name}</Hand>
      <rect className={i === items.length - 1 ? "pc-mark" : "pc-band"} x={94} y={24 + i * 36} height={21} width={Math.max(2, value * scale)} rx={3} />
      <Hand x={102 + value * scale} y={41 + i * 36}>{value}</Hand>
    </g>)}
  </Svg>;
}

export function GreetingCounter() {
  return (
    <Fork
      label="One greeting counter serves Riya and Kabir and hands each a personal greeting."
      input="one greeter"
      paths={[["Riya arrives", "Hello, Riya!"], ["Kabir arrives", "Hello, Kabir!"]]}
    />
  );
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

export function PostcardSlot() {
  return (
    <Svg label="A postcard has a blank for the city. A handwritten Pune fills it between Welcome to and the exclamation mark.">
      <Card x={25} y={12} w={270} h={126} />
      <rect className="pc-band" x={245} y={24} width={31} height={26} rx={2} />
      <Hand x={46} y={56}>Welcome to</Hand>
      <path className="pc-rule" strokeDasharray="4 3" d="M132 58 h77" />
      <Hand x={215} y={56}>!</Hand>
      <rect className="pc-mark" x={101} y={86} width={76} height={32} rx={4} />
      <Hand x={139} y={108} anchor="middle" kind="label">Pune</Hand>
      <Ink d="M177 98 Q201 92 184 63" />
    </Svg>
  );
}

export function TerminalHandoff() {
  return (
    <Route
      label="Node runs the file, the function hands a value back, and the caller prints it."
      stops={["file", "function", "caller"]}
      notes={["Node runs it", "returns text", "prints text"]}
    />
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

export function ClockQuarter() {
  return (
    <Svg
      label="A clock shows one complete turn of sixty minutes and an extra fifteen-minute quarter turn.">
      <circle className="pc-card" cx={88} cy={75} r={54} />
      <path className="pc-mark" d="M88 75 V23 A52 52 0 0 1 140 75 Z" />
      <Ink d="M88 37 V75 H128" plain /><circle cx={88} cy={75} r={4} className="pc-cell" />
      <Hand x={159} y={55}>one turn: 60 min</Hand><Hand x={159} y={87}>quarter: 15 min</Hand><Hand x={159} y={119} kind="label">75 minutes</Hand>
    </Svg>
  );
}

export function MinutesReceipt() {
  return (
    <Ledger
      label="A journey has one hour and ten extra minutes, recorded as sixty plus ten minutes."
      heading="Time receipt"
      entries={[["one hour", "60 min"], ["extra time", "10 min"], ["journey", "70 min"]]}
    />
  );
}

export function AverageNotebook() {
  return (
    <Route
      label="Three marks sum to 212. Their average is about 70.6667 and the displayed result is 70.7."
      stops={["three marks", "exact average", "rounded"]}
      notes={["sum: 212", "70.666…", "70.7"]}
    />
  );
}

export function TypeStamps() {
  return (
    <Board
      label="A form supplies a text two. Conversion turns it into a number two before two more are added."
      rows={[
        { left: "form", right: ["“2”", "text"] },
        { left: "converted", right: ["2", "number"], marked: [1] },
        { left: "plus two", right: ["4"], marked: [0] },
      ]}
    />
  );
}

export function NumberSorter() {
  return (
    <Fork
      label="Two strings enter a number converter. Digits produce twelve and letters produce NaN."
      input="text input"
      paths={[["digits: “12”", "number: 12"], ["letters: “abc”", "invalid number"]]}
    />
  );
}

export function PaisePockets() {
  return (
    <Svg label="Three pockets hold rupees, tens of paise and individual paise. A five-paise coin goes into the last pocket, giving ₹0.05.">
      {["rupees", "10 paise", "1 paisa"].map((label, i) => {
        const x = 18 + i * 97;
        return <g key={label}>
          <path className="pc-card" d={`M${x} 54 h86 v42 l-43 17 -43 -17 Z`} />
          <Hand x={x + 43} y={40} anchor="middle">{label}</Hand>
          <Hand x={x + 43} y={85} anchor="middle" kind="title">{i === 2 ? "5" : "0"}</Hand>
        </g>;
      })}
      <Hand x={160} y={139} anchor="middle" kind="label">price tag ₹0.05</Hand>
    </Svg>
  );
}

export function ShopTill() {
  return (
    <Ledger
      label="A till adds 75 and 50 paise and prints one rupee and twenty-five paise."
      heading="Till slip"
      entries={[["first price", "75 paise"], ["second price", "50 paise"], ["customer sees", "₹1.25"]]}
    />
  );
}

export function GradeBoundary() {
  return (
    <Ruler
      label="The grade boundary runs between 79 in band B and 80 in band A."
      ticks={["78", "79", "80", "81"]}
      notes={["B", "B", "A", "A"]}
      marked={[1, 2]}
    />
  );
}

export function EmptyLabels() {
  return (
    <Board
      label="Empty text is falsy, whereas text containing a single zero is truthy."
      rows={[
        { left: "blank tag", right: ["empty text", "falsy"] },
        { left: "printed tag", right: ["“0”", "truthy"], marked: [0] },
      ]}
    />
  );
}

export function MatchingBadges() {
  return (
    <Board
      label="Two number badges showing five match on both fields. A text badge showing five has a different type."
      rows={[
        { left: "badge A", right: ["number", "5"] },
        { left: "badge B", right: ["number", "5"], marked: [0, 1] },
        { left: "badge C", right: ["text", "“5”"] },
      ]}
    />
  );
}

export function AdultInterval() {
  return (
    <Ruler
      label="On the ticket scale, 17 is child, 18 and 59 are adult, and 60 is senior."
      ticks={["17", "18", "59", "60"]}
      notes={["child", "adult", "adult", "senior"]}
      marked={[1, 2]}
    />
  );
}

export function CenturyCalendar() {
  return (
    <Ledger
      label="A calendar compares 1900 with 28 February days and 2000 with 29."
      heading="February ledger"
      entries={[["1900", "28 days"], ["2000", "29 days"], ["2004", "29 days"]]}
    />
  );
}

export function PassingStamps() {
  return (
    <Board
      label="45, 20, 90 and 33 are inspected. 45, 90 and 33 receive pass stamps."
      rows={[
        { left: "marks", right: ["45", "20", "90", "33"] },
        { left: "stamped", right: ["yes", "no", "yes", "yes"], marked: [0, 2, 3] },
      ]}
    />
  );
}

export function TotalOdometer() {
  return (
    <Board
      label="Counters one to four correspond to cumulative totals one, three, six and ten."
      rows={[
        { left: "counter", right: ["1", "2", "3", "4"] },
        { left: "total", right: ["1", "3", "6", "10"], marked: [3] },
      ]}
    />
  );
}

export function StaircaseSum() {
  return (
    <Bars
      label="Stair one contributes one block, stair two adds two and stair three adds three."
      items={[["stair 1", 1], ["stair 2", 2], ["stair 3", 3]]}
    />
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

export function VowelBeads() {
  return (
    <Svg label="Five beads spell bread. The beads with e and a carry rings, giving two vowels.">
      <Ink d="M15 69 Q151 72 305 69" plain />
      {Array.from("bread", (letter, i) => {
        const x = 43 + i * 58;
        return <g key={letter}>
          <circle className="pc-card" cx={x} cy={69} r={18} />
          {(letter === "e" || letter === "a") && <circle className="pc-mark" cx={x} cy={69} r={25} />}
          <Hand x={x} y={76} anchor="middle" kind="title">{letter}</Hand>
        </g>;
      })}
      <Ink d="M159 104 q25 17 57 0" plain />
      <Hand x={187} y={139} anchor="middle" kind="label">two vowels</Hand>
    </Svg>
  );
}

export function LetterWalk() {
  return (
    <Route
      label="In the word tea, t leaves the count at zero, e increases it to one and a increases it to two."
      stops={["t", "e", "a"]}
      notes={["count 0", "count 1", "count 2"]}
    />
  );
}

export function TrimEdges() {
  return (
    <Board
      label="Dots mark spaces around and inside the words red and tea. Only the outer dots disappear."
      rows={[
        { left: "typed", right: ["··", "red", "··", "tea", "··"] },
        { left: "trimmed", right: ["red", "··", "tea"], marked: [1] },
      ]}
    />
  );
}

export function WordIslands() {
  return (
    <Board
      label="Two words with three space marks between them become two separate items."
      rows={[
        { left: "typed", right: ["red", "···", "tea"] },
        { left: "words", right: ["red", "tea"], marked: [0, 1] },
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

export function NameRegister() {
  return (
    <Ledger
      label="The words aNIL and raO are tidied separately into Anil and Rao and entered as Anil Rao."
      heading="Name register"
      entries={[["first word", "Anil"], ["second word", "Rao"], ["entry", "Anil Rao"]]}
    />
  );
}

export function UtfSlots() {
  return (
    <Svg
      label="One face icon sits above a bracket spanning two storage slots.">
      <circle className="pc-card" cx={160} cy={41} r={25} /><circle className="pc-cell" cx={152} cy={36} r={2} /><circle className="pc-cell" cx={168} cy={36} r={2} />
      <Ink d="M148 47 Q160 60 172 47 M102 85 V76 H219 V85" plain />
      <Strip left="UTF-16" right={["unit 1", "unit 2"]} y={97} />
    </Svg>
  );
}

export function UnchangedString() {
  return (
    <Board
      label="The original letters t, e, a stay lowercase and a second row holds the uppercase result."
      rows={[
        { left: "original", right: ["t", "e", "a"] },
        { left: "new text", right: ["T", "E", "A"], marked: [0, 1, 2] },
      ]}
    />
  );
}

export function CheapestTray() {
  return (
    <Board
      label="Original prices 40, 10 and 30 stay put. The sorted copy highlights its first two prices, 10 and 30."
      rows={[
        { left: "original", right: ["40", "10", "30"] },
        { left: "copy", right: ["10", "30", "40"], marked: [0, 1] },
      ]}
    />
  );
}

export function SortingLanes() {
  return (
    <Board
      label="Sorting 10, 9 and 100 as text yields 10, 100, 9. Numerically they become 9, 10, 100."
      rows={[
        { left: "as text", right: ["10", "100", "9"] },
        { left: "as numbers", right: ["9", "10", "100"] },
        { left: "original", right: ["10", "9", "100"] },
      ]}
    />
  );
}

export function PodiumSlots() {
  return (
    <Board
      label="The ranked scores 90, 72, 66 and 45 have their first two positions circled."
      rows={[
        { left: "ranked", right: ["90", "72", "66", "45"], marked: [0, 1] },
        { left: "result", right: ["90", "72"] },
      ]}
    />
  );
}

export function SearchSigns() {
  return (
    <Fork
      label="Coffee appears at slot one. One sign answers present and the other answers slot one."
      input="coffee"
      paths={[["is it there?", "yes"], ["where is it?", "slot 1"]]}
    />
  );
}

export function FirstFootprints() {
  return (
    <Board
      label="Tea, milk, tea and bun leave three first footprints in that order."
      rows={[
        { left: "visited", right: ["tea", "milk", "tea", "bun"], marked: [0, 1, 3] },
        { left: "kept", right: ["tea", "milk", "bun"] },
      ]}
    />
  );
}

export function MissingSlot() {
  return (
    <Ruler
      label="Slot minus one is the missing result, while actual array positions begin at zero."
      ticks={["−1", "0", "1", "2"]}
      notes={["missing", "tea", "milk", "bun"]}
      marked={[0]}
    />
  );
}

export function MissingField() {
  return (
    <Board
      label="A product card contains name and price. The absent colour field reads undefined."
      rows={[
        { left: "name", right: ["tea"] },
        { left: "price", right: ["20"] },
        { left: "colour", right: ["no value"], marked: [0] },
      ]}
    />
  );
}

export function CartShelves() {
  return (
    <Board
      label="Cart slot zero holds tea, 20 and two. Slot one holds bun, 15 and one."
      rows={[
        { left: "fields", right: ["name", "price", "qty"] },
        { left: "slot 0", right: ["tea", "20", "2"] },
        { left: "slot 1", right: ["bun", "15", "1"] },
      ]}
    />
  );
}

export function BasketCount() {
  return (
    <Svg label="Two cups of tea and one bun are three individual items even though they take only two cart lines.">
      {[32, 97].map(x => <g key={x}>
        <path className="pc-card" d={`M${x} 45 h44 l-5 36 q-17 10 -34 0 Z`} />
        <Ink d={`M${x + 43} 49 q28 -3 10 22 l-11 2`} plain />
      </g>)}
      <path className="pc-card" d="M203 79 Q206 34 243 41 Q277 41 284 79 Q241 91 203 79 Z" />
      <Ink d="M224 51 l8 11 M240 48 l8 10 M254 49 l8 10" plain />
      <Hand x={91} y={119} anchor="middle">2 teas</Hand>
      <Hand x={174} y={75} kind="title">+</Hand>
      <Hand x={243} y={119} anchor="middle">1 bun</Hand>
    </Svg>
  );
}

export function LineSubtotals() {
  return (
    <Ledger
      label="Two teas at 20 cost 40, one bun costs 15 and the bill is 55."
      heading="Cart bill"
      entries={[["two teas", "40"], ["one bun", "15"], ["total", "55"]]}
    />
  );
}

export function TwoPriceTags() {
  return (
    <Board
      label="Original and sale tags both say tea and quantity two. Only the sale price changes from 20 to 18."
      rows={[
        { left: "fields", right: ["name", "price", "qty"] },
        { left: "original", right: ["tea", "20", "2"] },
        { left: "sale copy", right: ["tea", "18", "2"], marked: [1] },
      ]}
    />
  );
}

export function OnePriceTag() {
  return (
    <Svg
      label="Two arrows labelled item and alias converge on one physical price tag marked 20.">
      <Hand x={25} y={46} kind="label">item</Hand><Hand x={25} y={119} kind="label">alias</Hand>
      <Ink d="M75 40 Q114 40 153 69" />
      <Ink d="M75 113 Q117 110 153 83" />
      <path className="pc-card" d="M158 72 l27 -30 h95 v67 h-95 Z" />
      <circle className="pc-cell" cx={177} cy={75} r={4} /><Hand x={198} y={82} kind="title">₹20</Hand>
    </Svg>
  );
}

export function CaseTallies() {
  return (
    <Board
      label="Tea, TEA and tea all use the lowercase key tea, which finishes with three marks."
      rows={[
        { left: "heard", right: ["Tea", "TEA", "tea"] },
        { left: "key", right: ["tea", "tea", "tea"] },
        { left: "count", right: ["1", "2", "3"], marked: [2] },
      ]}
    />
  );
}

export function SharedGroceries() {
  return (
    <Svg
      label="Two overlapping shopping lists share milk and tea. Coffee is only on the left and juice only on the right.">
      <ellipse className="pc-ink" cx={123} cy={79} rx={97} ry={52} /><ellipse className="pc-ink" cx={201} cy={79} rx={97} ry={52} />
      <Hand x={41} y={86}>coffee</Hand><Hand x={158} y={73} anchor="middle" kind="label">milk</Hand>
      <Hand x={158} y={99} anchor="middle" kind="label">tea</Hand><Hand x={242} y={86}>juice</Hand>
    </Svg>
  );
}

export function DoorTokens() {
  return (
    <Board
      label="When Riya, Arjun and Riya arrive, the guest count is one, then two, then still two."
      rows={[
        { left: "visitor", right: ["Riya", "Arjun", "Riya"] },
        { left: "set size", right: ["1", "2", "2"], marked: [2] },
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

export function CapitalStation() {
  return (
    <Board
      label="Riya, Arjun and Meera enter. Arjun and Meera pass the length test and finish in capitals."
      rows={[
        { left: "arrive", right: ["Riya", "Arjun", "Meera"] },
        { left: "keep", right: ["Arjun", "Meera"] },
        { left: "change", right: ["ARJUN", "MEERA"], marked: [0, 1] },
      ]}
    />
  );
}

export function DoublingMachine() {
  return (
    <Board
      label="Applying a doubling rule to 72, 30 and 90 gives 144, 60 and 180 in matching slots."
      rows={[
        { left: "input", right: ["72", "30", "90"] },
        { left: "doubled", right: ["144", "60", "180"] },
      ]}
    />
  );
}

export function TieBreak() {
  return (
    <Board
      label="Kiwi and date are both four letters long. Alphabetical order places date first."
      rows={[
        { left: "tied words", right: ["kiwi", "date"] },
        { left: "length", right: ["4", "4"] },
        { left: "tie broken", right: ["date", "kiwi"], marked: [0] },
      ]}
    />
  );
}

export function CallbackBell() {
  return (
    <Route
      label="A listener registers a function, a click arrives and the receiver calls the function."
      stops={["register", "click", "call"]}
      notes={["leave a rule", "event arrives", "run the rule"]}
    />
  );
}

export function SortedNotebook() {
  return (
    <Board
      label="An original word list has pear, fig and apple. A copy sorted by length has fig, pear and apple."
      rows={[
        { left: "original", right: ["pear", "fig", "apple"] },
        { left: "sorted copy", right: ["fig", "pear", "apple"] },
      ]}
    />
  );
}

export function QuantityCheckpoint() {
  return (
    <Fork
      label="At the quantity desk, text abc has the wrong type while zero is a whole number outside the allowed range."
      input="quantity"
      paths={[["abc", "wrong kind"], ["0", "out of range"]]}
    />
  );
}

export function CatchDetour() {
  return (
    <Route
      label="A path leads from a failed operation to the handler and on to the rest of the program."
      stops={["throw", "handle", "continue"]}
      notes={["leave block", "read reason", "next step"]}
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

export function SortingInputs() {
  return (
    <Board
      label="Given 10, x and 2.5, the good numbers total 12.5 and the rejected list contains x."
      rows={[
        { left: "input", right: ["10", "x", "2.5"] },
        { left: "total", right: ["12.5"] },
        { left: "bad list", right: ["x"], marked: [0] },
      ]}
    />
  );
}

export function HandlerDesk() {
  return (
    <Fork
      label="At an error desk, an expected input problem is handled locally and an unexpected fault is passed on."
      input="handler"
      paths={[["expected", "explain input"], ["unexpected", "pass it on"]]}
    />
  );
}

export function EmptyNumber() {
  return (
    <Board
      label="Empty text converts to zero and text abc converts to NaN, so the reader must inspect blank input too."
      rows={[
        { left: "blank text", right: ["0"] },
        { left: "abc", right: ["invalid"], marked: [0] },
      ]}
    />
  );
}

export function StepTurnstile() {
  return (
    <Svg label="A positive step passes through a turnstile and increases the stored total. A negative step is refused at the gate.">
      <circle className="pc-card" cx={153} cy={73} r={10} />
      <Ink d="M153 63 l-14 -40 M162 74 l43 14 M147 83 l-26 37" plain />
      <Hand x={12} y={45} kind="label">+3 steps</Hand>
      <Ink d="M68 43 Q105 43 125 52" />
      <Hand x={199} y={49}>add 3</Hand>
      <Hand x={12} y={108}>−2 steps</Hand>
      <Ink d="M88 105 Q110 102 106 125 Q104 134 80 133" />
      <Hand x={171} y={132} kind="label">refused: no change</Hand>
    </Svg>
  );
}

export function IndependentDials() {
  return (
    <Board
      label="Two new counters start at zero. The first receives two clicks and the second one click."
      rows={[
        { left: "counter", right: ["first", "second"] },
        { left: "start", right: ["0", "0"] },
        { left: "after clicks", right: ["2", "1"] },
      ]}
    />
  );
}

export function WithdrawSlip() {
  return (
    <Ledger
      label="An account with 50 receives a request for 80. The rejected request leaves 50."
      heading="Withdrawal slip"
      entries={[["before", "50"], ["request", "80"], ["after refusal", "50"]]}
    />
  );
}

export function AreaTiles() {
  return (
    <Svg
      label="A three by four rectangle reports twelve square units and a unit circle reports about 3.14 square units.">
      {Array.from({length:12}, (_,i) => <rect key={i} className="pc-cell" x={35 + (i%4)*21} y={31 + Math.floor(i/4)*21} width={20} height={20} />)}
      <circle className="pc-mark" cx={223} cy={62} r={32} /><Ink d="M223 62 l31 -1" plain />
      <Hand x={73} y={125} anchor="middle">12 units²</Hand><Hand x={226} y={125} anchor="middle">≈ 3.14 units²</Hand>
    </Svg>
  );
}

export function ShapeRequests() {
  return (
    <Fork
      label="A single request for area reaches a square that knows its side or a circle that knows its radius."
      input="area?"
      paths={[["square", "uses its side"], ["circle", "uses its radius"]]}
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

export function PriceTickets() {
  return (
    <Board
      label="Coffee and bun are requested. Bun finishes first, but the result still holds coffee price 30 followed by bun price 15."
      rows={[
        { left: "requested", right: ["coffee", "bun"] },
        { left: "finishes", right: ["bun", "coffee"] },
        { left: "result", right: ["30", "15"], marked: [0, 1] },
      ]}
    />
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

export function LastErrorSlip() {
  return (
    <Ledger
      label="Two attempts fail, first with timeout and then offline. Offline is the reason sent back."
      heading="Attempt log"
      entries={[["first", "timeout"], ["second", "offline"], ["returned reason", "offline"]]}
    />
  );
}

export function ReadyQueue() {
  return (
    <Route
      label="Slow work finishes, its callback joins a queue, and it runs when the call stack is clear."
      stops={["finished", "queued", "running"]}
      notes={["work ready", "await a turn", "stack clear"]}
    />
  );
}

export function RetryExits() {
  return (
    <Fork
      label="A retry loop can finish on success with a value or exhaust every try and throw the last error."
      input="attempts"
      paths={[["first success", "return value"], ["all failed", "throw last error"]]}
    />
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

export function MarginNumbers() {
  return (
    <Svg label="A file with a header, food, a blank line and rent. Rent is on line four at array index three.">
      <Card x={13} y={5} w={294} h={140} />
      <Hand x={38} y={31} kind="label">Line</Hand>
      <Hand x={95} y={31} kind="label">Index</Hand>
      <Hand x={160} y={31} kind="label">File contents</Hand>
      <path className="pc-rule" d="M23 39 H296 M82 17 V136 M145 17 V136" />
      {["header", "food", "", "rent"].map((line, i) => (
        <g key={i}>
          <Hand x={53} y={62 + i * 24} anchor="middle">{i + 1}</Hand>
          <Hand x={113} y={62 + i * 24} anchor="middle">{i}</Hand>
          <Hand x={160} y={62 + i * 24}>{line}</Hand>
        </g>
      ))}
    </Svg>
  );
}

export function CategoryBins() {
  return (
    <Bars
      label="In a five-row example, food occurs three times, rent once and an empty category once."
      items={[["food", 3], ["rent", 1], ["blank", 1]]}
    />
  );
}

export function CategoryBook() {
  return (
    <Ledger
      label="Two food rows worth 12.50 and 7.25 are recorded together for a food total of 19.75."
      heading="Food page"
      entries={[["first row", "12.50"], ["next row", "7.25"], ["food subtotal", "19.75"]]}
    />
  );
}

export function ReportInboxes() {
  return (
    <Fork
      label="A good data row goes to the totals and count. A bad data row sends its line number to a separate list."
      input="data row"
      paths={[["valid", "amount to totals"], ["invalid", "line to bad list"]]}
    />
  );
}

export function FoldNotepad() {
  return (
    <Board
      label="Starting at zero, folding 120, 80 and 45 produces running totals 120, 200 and 245."
      rows={[
        { left: "next row", right: ["120", "80", "45"] },
        { left: "total so far", right: ["120", "200", "245"], marked: [2] },
      ]}
    />
  );
}
