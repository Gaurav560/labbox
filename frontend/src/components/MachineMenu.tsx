import { useEffect, useRef, useState } from "react";

/*
 * The machine's rarely used actions in one small menu (the owner's UX review): stopping the machine,
 * and resetting the lab, which throws away the learner's files. A red Reset button next to Stop in the
 * header was one slip away from losing work; here it sits behind a click, and still asks to confirm.
 */
export default function MachineMenu({ status, onStop, onReset }: { status: string; onStop: () => void; onReset: () => void }) {
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
  const act = (fn: () => void) => () => { setOpen(false); fn(); };
  return (
    <div className="ts-wrap mm-wrap" ref={ref}>
      <button className="btn btn-small btn-ghost" onClick={() => setOpen((o) => !o)} aria-expanded={open} aria-haspopup="menu" title="Machine">
        Machine ▾
      </button>
      {open && (
        <div className="ts-pop mm-pop" role="menu" aria-label="Machine">
          <button role="menuitem" className="mm-item" onClick={act(onStop)} disabled={status !== "running"}>
            <strong>Stop machine</strong>
            <span>Pause it; your files stay. It starts again when you come back.</span>
          </button>
          <button role="menuitem" className="mm-item mm-danger" onClick={act(onReset)} disabled={status === "starting"}>
            <strong>Reset lab…</strong>
            <span>Delete your files for this lab and start again from the starter files.</span>
          </button>
        </div>
      )}
    </div>
  );
}
