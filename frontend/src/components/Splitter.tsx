import type { PointerEvent } from "react";

interface Props {
  direction: "vertical" | "horizontal"; // vertical = a bar you drag left/right
  onDrag: (delta: number) => void;
}

export default function Splitter({ direction, onDrag }: Props) {
  function onPointerDown(e: PointerEvent<HTMLDivElement>) {
    e.preventDefault();
    const el = e.currentTarget;
    el.setPointerCapture(e.pointerId);
    let last = direction === "vertical" ? e.clientX : e.clientY;
    const move = (ev: globalThis.PointerEvent) => {
      const pos = direction === "vertical" ? ev.clientX : ev.clientY;
      onDrag(pos - last);
      last = pos;
    };
    const up = () => {
      el.removeEventListener("pointermove", move);
      el.removeEventListener("pointerup", up);
      document.body.classList.remove("dragging");
    };
    el.addEventListener("pointermove", move);
    el.addEventListener("pointerup", up);
    document.body.classList.add("dragging");
  }
  return <div className={`splitter splitter-${direction}`} onPointerDown={onPointerDown} />;
}
