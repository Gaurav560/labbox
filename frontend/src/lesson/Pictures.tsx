import type { ReactNode } from "react";
import CODE from "./pictures.json";

/*
 * Small pictures for the everyday images a lesson uses to explain an idea (Content standard, section 3:
 * "picture it"). A chapter asks for one with :::picture{name="recipe-card"}; the text inside becomes the
 * caption. One hand-drawn look, two moods: a sketch in the dark theme and notebook paper in the light
 * theme (styles.css). Everyday words are handwritten (pc-hand); anything that is real code stays in the
 * code font (pc-code) and is listed in pictures.json, so the validator can check that the same code is in
 * a code block of the step: learners never copy from a drawing.
 */

const code = (name: keyof typeof CODE, i = 0) => (CODE[name] as string[])[i];

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

/** A curved, hand-drawn arrow. */
function Arrow({ d }: { d: string }) {
  return <path className="pc-ink" d={d} markerEnd="url(#pc-head)" />;
}

/** A method is a recipe card: a name, what it needs, the steps, and what it gives back. */
function RecipeCard() {
  const rows: [number, string, string][] = [
    [36, "Masala chai", "name"],
    [68, "needs: milk, tea", "inputs"],
    [96, "1. boil 2. add 3. pour", "body"],
    [124, "gives: one cup of chai", "return"],
  ];
  return (
    <svg viewBox="0 0 320 150" role="img" aria-label="A recipe card mapped to the parts of a method: name, inputs, body and return value">
      <Defs />
      <rect className="pc-card" x={8} y={10} width={190} height={128} rx={10} />
      <rect className="pc-band" x={10} y={12} width={186} height={34} rx={8} />
      {rows.map(([y, text, part], i) => (
        <g key={part}>
          <text className={i === 0 ? "pc-title" : "pc-hand"} x={22} y={y}>{text}</text>
          <Arrow d={`M204 ${y - 5} Q218 ${y - 9} 234 ${y - 5}`} />
          <text className="pc-label" x={240} y={y}>{part}</text>
        </g>
      ))}
    </svg>
  );
}

/** An array is a form with a fixed number of boxes; an ArrayList is a notebook that takes another line. */
function NotebookVsForm() {
  return (
    <svg viewBox="0 0 320 150" role="img" aria-label="Left: a form with exactly five boxes, all full. Right: a notebook where a new line can always be added">
      <Defs />
      <text className="pc-label" x={8} y={24}>array: 5 boxes, fixed</text>
      {[0, 1, 2, 3, 4].map((i) => (
        <rect key={i} className="pc-cell" x={10 + i * 27} y={36} width={22} height={22} rx={4} />
      ))}
      <text className="pc-hand" x={10} y={88}>a 6th one?</text>
      <text className="pc-hand" x={10} y={110}>no room</text>
      <text className="pc-label" x={170} y={24}>ArrayList: grows</text>
      <rect className="pc-card" x={168} y={34} width={144} height={108} rx={8} />
      {[0, 1, 2, 3].map((i) => (
        <line key={i} className="pc-rule" x1={180} y1={60 + i * 24} x2={300} y2={60 + i * 24} />
      ))}
      <rect className="pc-mark" x={182} y={64} width={92} height={20} rx={4} />
      <text className="pc-hand" x={186} y={55}>72</text>
      <text className="pc-code" x={186} y={79}>+ {code("notebook-vs-form")}</text>
    </svg>
  );
}

/** A HashMap is a phone book: you look a key up to find its value. */
function PhoneBook() {
  const rows = [["Riya", "98201 11111"], ["Arjun", "99300 22222"], ["Meera", "90040 33333"]];
  return (
    <svg viewBox="0 0 320 150" role="img" aria-label="A phone book with names as keys and numbers as values; get Riya finds Riya's number">
      <Defs />
      <rect className="pc-card" x={112} y={10} width={200} height={130} rx={10} />
      <text className="pc-label" x={126} y={34}>key</text>
      <text className="pc-label" x={208} y={34}>value</text>
      <path className="pc-ink" d="M198 16 L199 132" />
      <rect className="pc-mark" x={118} y={42} width={188} height={28} rx={6} />
      {rows.map(([k, v], i) => (
        <g key={k}>
          <text className="pc-hand" x={126} y={62 + i * 28}>{k}</text>
          <text className="pc-hand" x={208} y={62 + i * 28}>{v}</text>
        </g>
      ))}
      <text className="pc-code" x={6} y={52}>{code("phone-book")}</text>
      <Arrow d="M50 62 Q80 74 114 58" />
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
