import { useEffect, useRef, useState, type CSSProperties } from "react";
import { DEFAULT_SIZES, MAX_SIZE, MIN_SIZE, PRESETS, setTextSizes, useTextSizes, type TextArea } from "../textSize";

const AREAS: [TextArea, string][] = [["lesson", "Lesson"], ["tasks", "Tasks"], ["editor", "Code editor"], ["terminal", "Terminal"]];

/** The "Aa" button in the lab's top bar: one preset for everything, or a slider per area. */
export default function TextSizeMenu() {
  const sizes = useTextSizes();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const away = (e: MouseEvent) => { if (!ref.current?.contains(e.target as Node)) setOpen(false); };
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", away);
    document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("mousedown", away); document.removeEventListener("keydown", esc); };
  }, [open]);

  const values = Object.values(sizes);
  const preset = Object.entries(PRESETS).find(([, v]) => values.every((s) => s === v))?.[0];

  return (
    <div className="ts-wrap" ref={ref}>
      <button className="btn btn-small btn-ghost ts-btn" onClick={() => setOpen((o) => !o)} aria-expanded={open} aria-haspopup="dialog" aria-label="Text size" title="Text size">
        A<small>A</small>
      </button>
      {open && (
        <div className="ts-pop" role="dialog" aria-label="Text size">
          <div className="ts-head">
            <strong>Text size</strong>
            <button className="ts-reset" onClick={() => setTextSizes(DEFAULT_SIZES)}>Reset</button>
          </div>
          <div className="ts-presets" role="group" aria-label="Presets">
            {Object.entries(PRESETS).map(([name, v]) => (
              <button key={name} aria-pressed={preset === name} onClick={() => setTextSizes({ lesson: v, tasks: v, editor: v, terminal: v })}>
                {name}
              </button>
            ))}
          </div>
          {AREAS.map(([area, label]) => (
            <label key={area} className="ts-row">
              <span>{label}</span>
              <input
                type="range"
                min={MIN_SIZE}
                max={MAX_SIZE}
                step={5}
                value={sizes[area]}
                onChange={(e) => setTextSizes({ [area]: Number(e.target.value) })}
                style={{ "--ts-fill": `${((sizes[area] - MIN_SIZE) / (MAX_SIZE - MIN_SIZE)) * 100}%` } as CSSProperties}
                aria-label={`${label} text size`}
              />
              <output>{sizes[area]}%</output>
            </label>
          ))}
          <p className="ts-foot">Saved on this device · default 100%</p>
        </div>
      )}
    </div>
  );
}
