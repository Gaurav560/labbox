/*
 * Four ways to tell visitors what happens when they start a lab (owner, 25 November: "we spin a container, Linux,
 * language, framework, database and whatever inside; you don't do the setup, you start learning by taking the
 * challenges"; the first five options did not land, "show me all"). Not linked from the app.
 */
import { useEffect, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import Logo from "../components/Logo";
import ThemeButton from "../components/ThemeButton";

type Piece = { logo: string | null; name: string };
type Lab = { id: string; label: string; challenge: string; pieces: Piece[] };
const P = (logo: string | null, name: string): Piece => ({ logo, name });
const VSCODE = P(null, "VS Code");

// Each lab's real machine (labs/<id>/lab.yaml and Dockerfile).
const LABS: Lab[] = [
  { id: "fastapi-first-api", label: "FastAPI", challenge: "GET /menu: list every item",
    pieces: [P("linux", "Ubuntu 24.04"), P("python", "Python 3.12"), P("fastapi", "FastAPI"), VSCODE, P("git", "git")] },
  { id: "spring-boot-first-api", label: "Spring Boot", challenge: "Name the application",
    pieces: [P("linux", "Ubuntu 24.04"), P("java", "Java 21"), P("spring", "Spring Boot 3.4"), VSCODE, P("git", "git")] },
  { id: "redis-in-practice", label: "Redis", challenge: "Measure one round trip to Redis",
    pieces: [P("linux", "Ubuntu 24.04"), P("python", "Python 3.12"), P("fastapi", "FastAPI"), P("redis", "Redis 7.4"), P("redis", "Redis replica"), VSCODE] },
  { id: "postgres-indexing-incident", label: "Postgres", challenge: "Find the slow query",
    pieces: [P("linux", "Ubuntu 24.04"), P("python", "Python 3.12"), P("postgresql", "PostgreSQL 16"), P("sql", "1 million orders"), VSCODE] },
  { id: "rate-limiter", label: "System design", challenge: "10 requests a second per key, across both servers",
    pieces: [P("linux", "Ubuntu 24.04"), P("python", "Python 3.12"), P("nginx", "nginx load balancer"), P("redis", "Redis 7.4"), P("fastapi", "2 API servers"), VSCODE] },
  { id: "langchain", label: "LangChain", challenge: "A rule-based help desk",
    pieces: [P("linux", "Ubuntu 24.04"), P("python", "Python 3.12"), P("langchain", "LangChain 1.5"), P(null, "Model gateway, no key"), VSCODE] },
];

function Picker({ lab, onPick }: { lab: Lab; onPick: (l: Lab) => void }) {
  return (
    <div className="um-picker" role="tablist" aria-label="Pick a lab">
      {LABS.map((l) => <button key={l.id} type="button" role="tab" aria-selected={l.id === lab.id} onClick={() => onPick(l)}>{l.label}</button>)}
    </div>
  );
}

function Mark({ p }: { p: Piece }) {
  return p.logo ? <img src={`/logos/${p.logo}.svg`} alt="" /> : <span className="um-mono">{p.name === "VS Code" ? "</>" : "AI"}</span>;
}

/** A. Real logos fly into one container, it seals, and Start lights up. */
function LogosInABox() {
  const [lab, setLab] = useState(LABS[2]);
  const [run, setRun] = useState(0);
  useEffect(() => setRun((r) => r + 1), [lab]);
  const n = lab.pieces.length;
  return (
    <div className="ua">
      <div className="ua-text">
        <Picker lab={lab} onPick={setLab} />
        <h3>One click. <em>One machine with everything in it.</em></h3>
        <p>We pack the lab's whole stack into a container for you: the OS, the language, the framework, the databases and your editor. You open it and start the challenge.</p>
        <button type="button" className="uh-replay" onClick={() => setRun((r) => r + 1)}>↺ Pack it again</button>
      </div>
      <div className="ua-box" key={run}>
        <div className="ua-lid"><img src="/logos/docker.svg" alt="" /> your machine · {lab.label}</div>
        <ul className="ua-slots">
          {lab.pieces.map((p, i) => {
            const a = (i / n) * Math.PI * 2;
            return (
              <li key={p.name + i} style={{ "--d": `${0.15 + i * 0.28}s`, "--x": `${Math.cos(a) * 340}px`, "--y": `${Math.sin(a) * 260 - 60}px` } as CSSProperties}>
                <span className="ua-logo"><Mark p={p} /></span><span>{p.name}</span>
              </li>
            );
          })}
        </ul>
        <div className="ua-ready" style={{ "--d": `${0.4 + n * 0.28}s` } as CSSProperties}>
          <span><b>Ready</b> · first challenge: {lab.challenge}</span>
          <Link className="h-btn h-btn-primary" to="/login?signup=1">Start →</Link>
        </div>
      </div>
    </div>
  );
}

/** B. A real screen recording: the FastAPI course, Start, the machine opens with VS Code and the task. */
function Recording() {
  return (
    <div className="ub">
      <div className="ub-frame">
        <div className="ub-bar" aria-hidden="true"><span /><span /><span /><em>LabBox · FastAPI: your first API</em></div>
        <video src="/ukiyo/demo/start-a-lab.mp4" poster="/ukiyo/demo/start-a-lab-poster.webp" autoPlay muted loop playsInline
          aria-label="Screen recording: pressing Start on the FastAPI course opens the lab with VS Code, a terminal and the first task" />
      </div>
      <div className="ub-text">
        <h3>Press Start. <em>That's the whole setup.</em></h3>
        <p>Recorded on LabBox, not a mock-up: the FastAPI course, one click, and your own Linux machine opens with Python, FastAPI, VS Code, a terminal and the first task.</p>
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
        <img className="ud-after" src="/ukiyo/demo/fastapi-lab-ready.webp" alt="The FastAPI lab on LabBox: lesson, VS Code and terminal, ready" />
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
  { title: "Real logos in a box", note: "The lab's real stack, as real logos, flies into one container; it seals and Start lights up. Switch labs to see each stack.", View: LogosInABox },
  { title: "A real screen recording", note: "Recorded on this laptop just now: the FastAPI course, Start, and the lab opens with VS Code, the terminal and the task.", View: Recording },
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
