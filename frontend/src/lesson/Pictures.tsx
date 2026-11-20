import type { ReactNode } from "react";

/*
 * Small pictures for the everyday images a lesson uses to explain an idea (Content standard, section 3:
 * "picture it"). A chapter asks for one with :::picture{name="recipe-card"}; the text inside becomes the
 * caption. They are deliberately small line drawings in one style (theme colours, one accent), so they
 * support the text instead of competing with it. Diagrams.tsx holds the larger technical diagrams.
 */

function Line({ x1, y1, x2, y2, dashed }: { x1: number; y1: number; x2: number; y2: number; dashed?: boolean }) {
  return <line className="pc-line" x1={x1} y1={y1} x2={x2} y2={y2} strokeDasharray={dashed ? "3 4" : undefined} />;
}

function Head() {
  return (
    <defs>
      <marker id="pc-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" className="pc-head" />
      </marker>
    </defs>
  );
}

function Pointer({ x1, y1, x2, y2 }: { x1: number; y1: number; x2: number; y2: number }) {
  return <line className="pc-pointer" x1={x1} y1={y1} x2={x2} y2={y2} markerEnd="url(#pc-head)" />;
}

/** A method is a recipe card: a name, what it needs, the steps, and what it gives back. */
function RecipeCard() {
  const rows: [number, string, string][] = [
    [34, "Masala chai", "name"],
    [62, "needs: milk, tea", "inputs"],
    [88, "1. boil  2. add  3. pour", "body"],
    [114, "gives: one cup of chai", "return"],
  ];
  return (
    <svg viewBox="0 0 300 140" role="img" aria-label="A recipe card mapped to the parts of a method: name, inputs, body and return value">
      <Head />
      <rect className="pc-card" x={8} y={10} width={176} height={120} rx={10} />
      <rect className="pc-band" x={8} y={10} width={176} height={36} rx={10} />
      {rows.map(([y, text, part], i) => (
        <g key={part}>
          <text className={i === 0 ? "pc-title" : "pc-text"} x={20} y={y}>{text}</text>
          <Pointer x1={190} y1={y - 4} x2={220} y2={y - 4} />
          <text className="pc-label" x={226} y={y}>{part}</text>
        </g>
      ))}
    </svg>
  );
}

/** An array is a form with a fixed number of boxes; an ArrayList is a notebook that takes another line. */
function NotebookVsForm() {
  return (
    <svg viewBox="0 0 300 140" role="img" aria-label="Left: a form with exactly five boxes, all full. Right: a notebook where a new line can always be added">
      <text className="pc-label" x={10} y={18}>array: 5 boxes, fixed</text>
      {[0, 1, 2, 3, 4].map((i) => (
        <rect key={i} className="pc-cell" x={10 + i * 25} y={30} width={21} height={21} rx={4} />
      ))}
      <text className="pc-text" x={10} y={76}>a 6th item?</text>
      <text className="pc-text" x={10} y={94}>no room</text>
      <text className="pc-label" x={160} y={18}>ArrayList: grows</text>
      <rect className="pc-card" x={160} y={28} width={130} height={104} rx={8} />
      {[0, 1, 2, 3].map((i) => (
        <g key={i}>
          <Line x1={172} y1={48 + i * 20} x2={278} y2={48 + i * 20} />
          {i < 3 && <text className="pc-text" x={176} y={44 + i * 20}>{["72", "45", "90"][i]}</text>}
        </g>
      ))}
      <text className="pc-accent" x={176} y={104}>+ add(66)</text>
      <Line x1={172} y1={108} x2={278} y2={108} dashed />
    </svg>
  );
}

/** A HashMap is a phone book: you look a key up to find its value. */
function PhoneBook() {
  const rows = [["Riya", "98201 11111"], ["Arjun", "99300 22222"], ["Meera", "90040 33333"]];
  return (
    <svg viewBox="0 0 300 140" role="img" aria-label="A phone book with names as keys and numbers as values; get Arjun finds Arjun's number">
      <Head />
      <rect className="pc-card" x={100} y={10} width={192} height={120} rx={10} />
      <text className="pc-label" x={114} y={30}>key</text>
      <text className="pc-label" x={194} y={30}>value</text>
      <Line x1={186} y1={18} x2={186} y2={122} />
      {rows.map(([k, v], i) => (
        <g key={k}>
          {i === 1 && <rect className="pc-hit" x={104} y={60} width={184} height={26} rx={6} />}
          <text className="pc-text" x={114} y={54 + i * 28}>{k}</text>
          <text className="pc-text" x={194} y={54 + i * 28}>{v}</text>
        </g>
      ))}
      <text className="pc-accent" x={4} y={70}>get("Arjun")</text>
      <Pointer x1={60} y1={78} x2={100} y2={76} />
    </svg>
  );
}

const PICTURES: Record<string, () => JSX.Element> = {
  "recipe-card": RecipeCard,
  "notebook-vs-form": NotebookVsForm,
  "phone-book": PhoneBook,
};

export default function Picture({ name, caption }: { name: string; caption?: ReactNode }) {
  const Drawing = PICTURES[name];
  if (!Drawing) return null;
  return (
    <figure className="picture">
      <Drawing />
      {caption && <figcaption>{caption}</figcaption>}
    </figure>
  );
}
