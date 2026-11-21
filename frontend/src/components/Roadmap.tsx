import { useEffect, useRef, type ReactNode } from "react";
import { Link } from "react-router-dom";

/*
 * A plain, clean roadmap (owner, 21 November: "a plain cool roadmap, simple"): one vertical line with a numbered
 * dot per step, and a card beside each, alternating left and right on wide screens (one column on narrow ones).
 * Done steps are green with a tick and the line behind them turns green; the current step pulses gently and says
 * "You are here"; upcoming steps are outlined. Every card links to its chapter.
 */

export type RoadState = "done" | "now" | "open" | "locked" | "soon";
export interface RoadItem {
  id: string;
  number: string;
  title: string;
  meta?: string;          // a short line under the title ("2 tasks · 35 min")
  state: RoadState;
  href?: string;          // the whole card opens this
  children?: ReactNode;   // extra content (a track topic's chapters)
}

const STATE_TEXT: Record<RoadState, string> = { done: "Done", now: "You are here", open: "", locked: "Locked", soon: "Coming soon" };

export default function Roadmap({ items }: { items: RoadItem[] }) {
  const nowRef = useRef<HTMLLIElement>(null);
  useEffect(() => {
    nowRef.current?.scrollIntoView({ block: "center", behavior: "smooth" });
  }, [items]);
  const lastDone = items.reduce((k, it, i) => (it.state === "done" ? i : k), -1);
  return (
    <ol className="road" aria-label="Roadmap">
      {items.map((it, i) => {
        const card = (
          <>
            <div className="road-card-top">
              <span className="road-num">{it.number}</span>
              {STATE_TEXT[it.state] && <span className={`road-badge road-badge-${it.state}`}>{STATE_TEXT[it.state]}</span>}
            </div>
            <div className="road-title">{it.title}</div>
            {it.meta && <div className="road-meta">{it.meta}</div>}
          </>
        );
        return (
          <li key={it.id} ref={it.state === "now" ? nowRef : undefined}
            className={`road-step road-${it.state} ${i % 2 ? "road-right" : "road-left"} ${i <= lastDone ? "road-passed" : ""}`}>
            <span className="road-dot" aria-hidden="true">{it.state === "done" ? "✓" : Number(it.number)}</span>
            <div className="road-card">
              {it.href ? <Link className="road-link" to={it.href} aria-label={`${it.number} ${it.title}`}>{card}</Link> : <div className="road-link">{card}</div>}
              {it.children}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
