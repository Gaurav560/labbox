/*
 * Four ways to tell visitors what happens when they start a lab (owner, 25 November: "we spin a container, Linux,
 * language, framework, database and whatever inside; you don't do the setup, you start learning by taking the
 * challenges"; the first five options did not land, "show me all"). Not linked from the app.
 */
import { useEffect, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import Logo from "../components/Logo";
import ThemeButton from "../components/ThemeButton";
import { Seal } from "../components/UkiyoArt";

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

/** True once the element has been on screen (so the animation plays when the visitor reaches it). */
function useOnScreen() {
  const [el, setEl] = useState<HTMLElement | null>(null);
  const [seen, setSeen] = useState(false);
  useEffect(() => {
    if (!el) return;
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setSeen(true); io.disconnect(); } }, { threshold: 0.35 });
    io.observe(el);
    return () => io.disconnect();
  }, [el]);
  return [setEl, seen] as const;
}

/**
 * A. The lab's stack packs itself into one container, one piece at a time: an empty slot waits and pulses, the logo
 * flies in and settles, its line appears in the log, the progress bar and the clock move on. When the last piece is
 * in, the box seals and Start lights up.
 */
function LogosInABox() {
  const [lab, setLab] = useState(LABS[1]);
  const [run, setRun] = useState(0);
  const [step, setStep] = useState(0);
  const [ref, seen] = useOnScreen();
  const n = lab.pieces.length;
  const still = typeof window !== "undefined" && !!window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

  useEffect(() => {
    if (!seen) return;
    if (still) { setStep(n); return; }
    setStep(0);
    let k = 0;
    const t = setInterval(() => { k += 1; setStep(k); if (k >= n) clearInterval(t); }, 720);
    return () => clearInterval(t);
  }, [seen, run, lab, n, still]);

  const done = step >= n;
  const secs = Math.round((Math.min(step, n) / n) * 58);
  return (
    <div className="ua" ref={ref}>
      <div className="ua-text">
        <Picker lab={lab} onPick={(l) => { setLab(l); setRun((r) => r + 1); }} />
        <h3>One click, and we spin up a container for you <em>with everything the lab needs.</em></h3>
        <p>Linux, the language, the framework, the databases, an editor and terminal, and an AI code assistant: set up and running in about a minute. Nothing to install. You go straight to the first challenge.</p>
        <button type="button" className="uh-replay" onClick={() => setRun((r) => r + 1)}>↺ Pack it again</button>
      </div>
      <div className={`ua-box ${done ? "is-sealed" : ""}`} key={`${lab.id}-${run}`}>
        <div className="ua-lid">
          <img src="/logos/docker.svg" alt="" />
          <span>your machine · {lab.label}</span>
          <span className="ua-clock" aria-hidden="true">{done ? "ready" : `${secs} s`}</span>
          <span className="ua-bar" aria-hidden="true"><i style={{ width: `${(Math.min(step, n) / n) * 100}%` }} /></span>
        </div>
        <ul className="ua-slots" style={{ "--cols": n > 6 ? 4 : 3 } as CSSProperties}>
          {lab.pieces.map((p, i) => (
            <li key={p.name + i} className={i < step ? "is-in" : i === step ? "is-next" : ""}
              style={{ "--fx": `${(i % 2 ? 1 : -1) * (60 + (i * 37) % 80)}px`, "--fy": `${-110 - (i * 23) % 60}px` } as CSSProperties}>
              <span className="ua-tile">
                <span className="ua-logo"><Mark p={p} /></span>
                <span className="ua-name">{p.name}</span>
              </span>
            </li>
          ))}
        </ul>
        <ol className="ua-log" aria-live="polite" style={{ minHeight: `calc(${n} * 1.85em + 24px)` }}>
          {lab.pieces.slice(0, step).map((p, i) => (
            <li key={p.name + i}><b>✓</b> <strong>{p.name}</strong> <span>{p.step}</span></li>
          ))}
        </ol>
        <span className="ua-stamp" aria-hidden="true"><Seal lines={["READY"]} size={76} /></span>
        <div className="ua-ready">
          <span><b>Ready</b> · first challenge: {lab.challenge}</span>
          <Link className="h-btn h-btn-primary" to="/login?signup=1">Start →</Link>
        </div>
      </div>
    </div>
  );
}

/** B. A real screen recording: the FastAPI course, Start, the machine opens with the editor, terminal and task. */
function Recording() {
  return (
    <div className="ub">
      <div className="ub-frame">
        <div className="ub-bar" aria-hidden="true"><span /><span /><span /><em>LabBox · FastAPI: your first API</em></div>
        <video src="/ukiyo/demo/start-a-lab.mp4" poster="/ukiyo/demo/start-a-lab-poster.webp" autoPlay muted loop playsInline
          aria-label="Screen recording: pressing Start on the FastAPI course opens the lab with the editor, a terminal and the first task" />
      </div>
      <div className="ub-text">
        <h3>Press Start. <em>That's the whole setup.</em></h3>
        <p>Recorded on LabBox, not a mock-up: the FastAPI course, one click, and your own Linux machine opens with Python, FastAPI, an editor, a terminal and the first task.</p>
        <ol className="ub-steps"><li>Pick a lab</li><li>Press Start</li><li>Write code, press Check</li></ol>
      </div>
    </div>
  );
}

/** C. One big sentence and the real logos underneath. */
function BigSentence() {
  const logos = ["linux", "docker", "python", "java", "go", "rust", "javascript", "spring", "fastapi", "postgresql", "redis", "nginx", "langchain", "git"];
  return (
    <div className="uc">
      <h3 className="uc-line">No installs. No setup.<br /><em>Your machine is ready in about a minute.</em></h3>
      <p>Every lab comes with its own Linux machine, the language, the framework and the databases already running. You just take the challenge.</p>
      <ul className="uc-logos">{logos.map((l) => <li key={l}><img src={`/logos/${l}.svg`} alt={l} /></li>)}</ul>
    </div>
  );
}

/** D. Before and after: drag between a laptop full of install errors and the real LabBox lab. */
function BeforeAfter() {
  const [x, setX] = useState(50);
  return (
    <div className="ud">
      <div className="ud-head">
        <h3>Your laptop, <em>or your lab.</em></h3>
        <p>Drag the line.</p>
      </div>
      <div className="ud-stage" style={{ "--x": `${x}%` } as CSSProperties}>
        <img className="ud-after" src="/ukiyo/demo/fastapi-lab-ready.webp" alt="The FastAPI lab on LabBox: lesson, editor and terminal, ready" />
        <div className="ud-before" aria-label="A laptop terminal full of install errors">
          <pre>{`$ python3 -m pip install fastapi
error: externally-managed-environment
$ sudo pip install fastapi uvicorn
ERROR: Cannot install fastapi==0.115.6 and
  starlette==0.27.0: conflicting dependencies
$ python3 --version
Python 3.8.10      # the course needs 3.12
$ brew install postgresql@16
Error: No such keg: /usr/local/Cellar/postgresql@16
$ psql
psql: error: connection to server on socket
  "/tmp/.s.PGSQL.5432" failed: No such file
$ uvicorn main:app
ERROR: [Errno 98] Address already in use
$ # 2 hours later, still no code written`}</pre>
        </div>
        <span className="ud-label ud-label-l">Your laptop</span>
        <span className="ud-label ud-label-r">LabBox</span>
        <span className="ud-handle" aria-hidden="true"><i>⟷</i></span>
        <input type="range" min={0} max={100} value={x} onChange={(e) => setX(Number(e.target.value))} aria-label="Compare your laptop and LabBox" />
      </div>
    </div>
  );
}

const OPTIONS = [
  { title: "Real logos in a box", note: "The lab's real stack packs itself into one container, piece by piece, each with its line in the log; then it seals and Start lights up. Switch labs to see each stack.", View: LogosInABox },
  { title: "A real screen recording", note: "Recorded on this laptop just now: the FastAPI course, Start, and the lab opens with the editor, the terminal and the task.", View: Recording },
  { title: "One big sentence", note: "No diagram: one confident line and the real logos underneath.", View: BigSentence },
  { title: "Before and after", note: "A slider between a laptop full of install errors and the real LabBox lab, ready to go.", View: BeforeAfter },
];

export default function UkiyoMachinePage() {
  useEffect(() => { document.title = "Start a lab: four directions | LabBox by Telusko"; }, []);
  return (
    <div className="ul-page u-home home">
      <header className="ul-top">
        <Logo to="/" />
        <nav aria-label="Options">{OPTIONS.map((o, i) => <a key={o.title} href={`#machine-${i + 1}`}>{"ABCD"[i]}. {o.title}</a>)}</nav>
        <ThemeButton />
      </header>
      <main className="ul-main">
        <h1>What happens when you start a lab</h1>
        <p className="uh-section-lead">Four new directions. The stacks, the recording and the screenshot are real.</p>
        {OPTIONS.map(({ title, note, View }, i) => (
          <section key={title} id={`machine-${i + 1}`} className="ul-section" aria-labelledby={`machine-${i + 1}-t`}>
            <p className="u-kicker">Direction {"ABCD"[i]}</p>
            <h2 id={`machine-${i + 1}-t`}>{"ABCD"[i]}. {title}</h2>
            <p className="ul-note">{note}</p>
            <View />
          </section>
        ))}
      </main>
    </div>
  );
}
