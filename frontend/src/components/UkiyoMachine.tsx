/*
 * "Start a lab" on the home page (owner, 25 November: "one click and we spin up a container for you with everything
 * the lab needs"; picked from nine options). The lab's real stack (its lab.yaml and Dockerfile) packs itself into
 * one container, piece by piece with a line in the log each, then a green tick and Start, which opens that course.
 */
import { useEffect, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";

type Piece = { logo: string | null; icon?: "term" | "ai"; name: string; step: string };
type Lab = { id: string; label: string; challenge: string; pieces: Piece[] };
const P = (logo: string, name: string, step: string): Piece => ({ logo, name, step });
const LINUX = P("linux", "Ubuntu 24.04", "your own Linux machine, in a container");
// The editor is named for what it does, not the product (owner, 25 November: it may change if VS Code is too heavy).
const EDITOR: Piece = { logo: null, icon: "term", name: "Editor and terminal", step: "a code editor and a terminal, in your browser" };
const AI: Piece = { logo: null, icon: "ai", name: "AI code assistant", step: "explains, hints and reviews, never the answer" };

// Each lab's real machine (labs/<id>/lab.yaml and Dockerfile).
const LABS: Lab[] = [
  { id: "fastapi-first-api", label: "FastAPI", challenge: "GET /menu: list every item",
    pieces: [LINUX, P("python", "Python 3.12", "the language, with pip"), P("fastapi", "FastAPI", "the framework, answering in the Preview tab"), EDITOR, AI] },
  { id: "spring-boot-first-api", label: "Spring Boot", challenge: "Name the application",
    pieces: [LINUX, P("java", "Java 21", "the JDK the course uses"), P("spring", "Spring Boot 3.4", "with Maven and every dependency, offline"), EDITOR, AI] },
  { id: "redis-in-practice", label: "Redis", challenge: "Measure one round trip to Redis",
    pieces: [LINUX, P("python", "Python 3.12", "with the redis client and redis-cli"), P("fastapi", "FastAPI", "a basket API to make fast"),
      P("redis", "Redis 7.4", "the primary server"), P("redis", "Redis replica", "a second server, copying the first"), EDITOR, AI] },
  { id: "postgres-indexing-incident", label: "Postgres", challenge: "Find the slow query",
    pieces: [LINUX, P("python", "Python 3.12", "with psql"), P("postgresql", "PostgreSQL 16", "a real database server"),
      P("sql", "1 million orders", "loaded and waiting to be slow"), EDITOR, AI] },
  { id: "rate-limiter", label: "System design", challenge: "10 requests a second per key, across both servers",
    pieces: [LINUX, P("python", "Python 3.12", "the language"), P("fastapi", "2 API servers", "the same app, twice"),
      P("nginx", "nginx", "a load balancer in front of them"), P("redis", "Redis 7.4", "the shared counter"), EDITOR, AI] },
  { id: "langchain", label: "LangChain", challenge: "A rule-based help desk",
    pieces: [LINUX, P("python", "Python 3.12", "the language"), P("langchain", "LangChain 1.5", "and every package the course uses"),
      { logo: null, icon: "ai", name: "Model gateway", step: "real models, no API key, every token counted" }, EDITOR, AI] },
];

function Picker({ lab, onPick }: { lab: Lab; onPick: (l: Lab) => void }) {
  return (
    <div className="um-picker" role="tablist" aria-label="Pick a lab">
      {LABS.map((l) => <button key={l.id} type="button" role="tab" aria-selected={l.id === lab.id} onClick={() => onPick(l)}>{l.label}</button>)}
    </div>
  );
}

function Mark({ p }: { p: Piece }) {
  if (p.logo) return <img src={`/logos/${p.logo}.svg`} alt="" />;
  if (p.icon === "term") return (
    <svg viewBox="0 0 48 48" aria-hidden="true"><rect x="4" y="8" width="40" height="32" rx="4" fill="#1b2533" />
      <path d="M12 19l6 5-6 5" fill="none" stroke="#e2583f" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M22 30h12" stroke="#e9e2d4" strokeWidth="3" strokeLinecap="round" /></svg>
  );
  return (
    <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 5l4.2 11.3L40 20l-11.8 3.9L24 35l-4.2-11.1L8 20l11.8-3.7z" fill="#c63f28" />
      <path d="M37 30l1.8 4.6 4.7 1.6-4.7 1.7L37 42.6l-1.8-4.7-4.7-1.7 4.7-1.6z" fill="#1f3a64" /></svg>
  );
}

/**
 * The lab's stack packs itself into one container, one piece at a time: an empty slot waits and pulses, the logo
 * flies in and settles, its line appears in the log, the progress bar and the clock move on. When the last piece is
 * in, the box seals and Start lights up. It waits for a click on Spin up.
 */
export default function UkiyoMachine({ signedIn }: { signedIn: boolean }) {
  const [lab, setLab] = useState(LABS[1]);
  // It plays when the visitor asks (owner, 25 November: "better if the user clicks and sees the animation"):
  // run 0 is the waiting box with the Spin up button; each click starts a new run.
  const [run, setRun] = useState(0);
  const [step, setStep] = useState(0);
  const n = lab.pieces.length;
  const still = typeof window !== "undefined" && !!window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

  useEffect(() => {
    setStep(0);
    if (run === 0) return;
    if (still) { setStep(n); return; }
    let k = 0;
    const t = setInterval(() => { k += 1; setStep(k); if (k >= n) clearInterval(t); }, 720);
    return () => clearInterval(t);
  }, [run, lab, n, still]);

  const waiting = run === 0;
  const spin = () => setRun((r) => r + 1);
  const done = step >= n;
  const secs = Math.round((Math.min(step, n) / n) * 58);
  return (
    <div className="ua">
      <div className="ua-text">
        <Picker lab={lab} onPick={(l) => { setLab(l); setRun(0); }} />
        <h2 id="machine-title">One click, and we spin up a container for you <em>with everything the lab needs.</em></h2>
        <p>Linux, the language, the framework, the databases, an editor and terminal, and an AI code assistant: set up and running in about a minute. Nothing to install. You go straight to the first challenge.</p>
        {!waiting && <button type="button" className="uh-replay" onClick={spin}>↺ Spin it up again</button>}
      </div>
      <div className={`ua-box ${done ? "is-sealed" : ""} ${waiting ? "is-waiting" : ""}`} key={`${lab.id}-${run}`}>
        <div className="ua-lid">
          <img src="/logos/docker.svg" alt="" />
          <span>your machine · {lab.label}</span>
          <span className="ua-clock" aria-hidden="true">{waiting ? "" : done ? "ready" : `${secs} s`}</span>
          <span className="ua-bar" aria-hidden="true"><i style={{ width: `${(Math.min(step, n) / n) * 100}%` }} /></span>
        </div>
        <ul className="ua-slots" style={{ "--cols": n > 6 ? 4 : 3 } as CSSProperties}>
          {lab.pieces.map((p, i) => (
            <li key={p.name + i} className={i < step ? "is-in" : i === step && !waiting ? "is-next" : ""}
              style={{ "--fx": `${(i % 2 ? 1 : -1) * (60 + (i * 37) % 80)}px`, "--fy": `${-110 - (i * 23) % 60}px` } as CSSProperties}>
              <span className="ua-tile">
                <span className="ua-logo"><Mark p={p} /></span>
                <span className="ua-name">{p.name}</span>
              </span>
            </li>
          ))}
        </ul>
        {waiting && (
          <button type="button" className="ua-go" onClick={spin}>
            <span className="ua-go-play" aria-hidden="true">▶</span>
            <span>Spin up the {lab.label} machine</span>
            <small>{n} pieces · about a minute on a real lab</small>
          </button>
        )}
        <ol className="ua-log" aria-live="polite" style={{ minHeight: `calc(${n} * 1.85em + 24px)` }}>
          {waiting && <li className="ua-log-wait">learner:~$ <span className="ua-caret" aria-hidden="true" /></li>}
          {lab.pieces.slice(0, step).map((p, i) => (
            <li key={p.name + i}><b>✓</b> <strong>{p.name}</strong> <span>{p.step}</span></li>
          ))}
        </ol>
        <span className="ua-stamp" role="img" aria-label="Ready">
          <svg viewBox="0 0 64 64" width="64" height="64"><circle cx="32" cy="32" r="29" /><path d="M19 33.5l9 9 17-19" /></svg>
        </span>
        <div className="ua-ready">
          <span><b>Ready</b> · first challenge: {lab.challenge}</span>
          <Link className="h-btn h-btn-primary" to={signedIn ? `/courses/${lab.id}` : `/login?next=${encodeURIComponent(`/courses/${lab.id}`)}`}>Start →</Link>
        </div>
      </div>
    </div>
  );
}
