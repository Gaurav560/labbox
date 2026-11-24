/*
 * Five ways to tell visitors what happens when they start a lab (owner, 25 November: "we spin a container, Linux,
 * language, framework, database and whatever inside; you don't do the setup, you start learning by taking the
 * challenges"). One after another, for the owner to pick. The layers are each lab's real setup (its lab.yaml and
 * Dockerfile). Not linked from the app.
 */
import { useEffect, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import Logo from "../components/Logo";
import ThemeButton from "../components/ThemeButton";

type Layer = { kind: string; name: string; note: string };
type Lab = { id: string; label: string; title: string; challenge: string; layers: Layer[]; boot: string[]; manual: string[] };

const LINUX: Layer = { kind: "Machine", name: "Linux", note: "Ubuntu 24.04, your own, in a container" };
const TOOLS: Layer = { kind: "Tools", name: "VS Code and a terminal", note: "in your browser, with git" };

// What each lab's machine really has (labs/<id>/lab.yaml and Dockerfile, images/*).
const LABS: Lab[] = [
  {
    id: "fastapi-first-api", label: "FastAPI", title: "FastAPI: your first API", challenge: "GET /menu: list every item",
    layers: [LINUX, { kind: "Language", name: "Python 3.12", note: "with pip and a virtual env" },
      { kind: "Framework", name: "FastAPI and uvicorn", note: "the API answers in the Preview tab" }, TOOLS],
    boot: ["creating your machine (Ubuntu 24.04)", "Python 3.12 ready", "FastAPI 0.115 and uvicorn ready", "opening VS Code and a terminal"],
    manual: ["Install Python 3.12 (and fix the old one on your PATH)", "Create a virtual environment", "pip install fastapi uvicorn (and pick versions that work together)", "Set up an editor and a terminal", "Find out why port 8000 is taken"],
  },
  {
    id: "spring-boot-first-api", label: "Spring Boot", title: "Spring Boot", challenge: "Name the application",
    layers: [LINUX, { kind: "Language", name: "Java 21", note: "Eclipse Temurin JDK" },
      { kind: "Framework", name: "Spring Boot 3.4 and Maven", note: "every dependency already downloaded" }, TOOLS],
    boot: ["creating your machine (Ubuntu 24.04)", "Java 21 ready", "Maven and Spring Boot 3.4 ready (offline)", "opening VS Code and a terminal"],
    manual: ["Install a JDK and set JAVA_HOME", "Install Maven", "Wait while Maven downloads half the internet", "Configure an IDE for Spring", "Fix the build that works on your friend's laptop"],
  },
  {
    id: "redis-in-practice", label: "Redis", title: "Redis in practice", challenge: "Measure one round trip to Redis",
    layers: [LINUX, { kind: "Language", name: "Python 3.12", note: "with the redis client and redis-cli" },
      { kind: "Framework", name: "FastAPI", note: "a basket API to speed up" },
      { kind: "Database", name: "Redis 7.4, primary and replica", note: "two real servers on your own network" }, TOOLS],
    boot: ["creating your machine (Ubuntu 24.04)", "Python 3.12 and FastAPI ready", "starting Redis 7.4 (primary)", "starting Redis 7.4 (replica)", "opening VS Code and a terminal"],
    manual: ["Install Python and a Redis client", "Install Redis (or Docker, then Redis)", "Configure persistence and memory limits", "Set up a second Redis as a replica", "Wire it all together and hope"],
  },
  {
    id: "postgres-indexing-incident", label: "Postgres", title: "Postgres: the slow checkout", challenge: "Find the slow query",
    layers: [LINUX, { kind: "Language", name: "Python 3.12", note: "and psql" },
      { kind: "Database", name: "PostgreSQL 16", note: "loaded with a million orders" }, TOOLS],
    boot: ["creating your machine (Ubuntu 24.04)", "Python 3.12 and psql ready", "starting PostgreSQL 16", "loading a million orders", "opening VS Code and a terminal"],
    manual: ["Install PostgreSQL", "Create a user, a database and permissions", "Write a script to make a million realistic orders", "Tune memory so your laptop survives", "Install a client and connect"],
  },
  {
    id: "langchain", label: "LangChain", title: "LangChain", challenge: "A rule-based help desk",
    layers: [LINUX, { kind: "Language", name: "Python 3.12", note: "with LangChain 1.5 and every package the course uses" },
      { kind: "AI", name: "A model gateway", note: "real models, no API key, every token counted" }, TOOLS],
    boot: ["creating your machine (Ubuntu 24.04)", "Python 3.12 and LangChain 1.5 ready", "connecting the model gateway (no key needed)", "opening VS Code and a terminal"],
    manual: ["Install Python and resolve LangChain's dependencies", "Create an OpenAI account and add a card", "Keep your API key out of git", "Watch the bill", "Pin versions before the next release breaks it"],
  },
];

function LabPicker({ lab, onPick }: { lab: Lab; onPick: (l: Lab) => void }) {
  return (
    <div className="um-picker" role="tablist" aria-label="Pick a lab">
      {LABS.map((l) => (
        <button key={l.id} type="button" role="tab" aria-selected={l.id === lab.id} onClick={() => onPick(l)}>{l.label}</button>
      ))}
    </div>
  );
}

/** Replays an animation each time the key changes. */
function useReplay(dep: unknown) {
  const [n, setN] = useState(0);
  useEffect(() => setN((x) => x + 1), [dep]);
  return [n, () => setN((x) => x + 1)] as const;
}

/** 1. The machine builds itself: layers stack from the bottom, a timer runs, the first challenge appears. */
function BuildsItself() {
  const [lab, setLab] = useState(LABS[0]);
  const [run, replay] = useReplay(lab);
  const [secs, setSecs] = useState(0);
  useEffect(() => {
    setSecs(0);
    const t = setInterval(() => setSecs((s) => (s >= 58 ? 58 : s + 2)), 70);
    return () => clearInterval(t);
  }, [run]);
  return (
    <div className="um-1">
      <div className="um-1-text">
        <LabPicker lab={lab} onPick={setLab} />
        <h3>You press <em>Start</em>. We build the machine.</h3>
        <p>Linux, the language, the framework, the databases and your editor, the same versions as the course. No install, no setup, no "works on my laptop".</p>
        <button type="button" className="h-btn h-btn-primary" onClick={replay}>▶ Start {lab.label}</button>
      </div>
      <div className="um-1-stack" key={run} aria-live="polite">
        <div className="um-1-timer"><span>{secs} s</span>{secs >= 58 ? " ready" : " starting..."}</div>
        <ol>
          {[...lab.layers].reverse().map((l, i, all) => (
            <li key={l.name} style={{ "--d": `${(all.length - 1 - i) * 0.42}s` } as CSSProperties}>
              <small>{l.kind}</small><strong>{l.name}</strong><span>{l.note}</span>
            </li>
          ))}
        </ol>
        <div className="um-1-ready" style={{ "--d": `${lab.layers.length * 0.42 + 0.3}s` } as CSSProperties}>
          <small>Your first challenge</small><strong>{lab.challenge}</strong>
        </div>
      </div>
    </div>
  );
}

/** 2. The setup you skip: the manual steps crossed out one by one, beside a single Start. */
function SetupYouSkip() {
  const [lab, setLab] = useState(LABS[0]);
  const [run] = useReplay(lab);
  return (
    <div className="um-2" key={run}>
      <LabPicker lab={lab} onPick={setLab} />
      <div className="um-2-cols">
        <div className="um-2-own">
          <p className="u-kicker">On your own</p>
          <ol>{lab.manual.map((m, i) => <li key={m} style={{ "--d": `${0.5 + i * 0.45}s` } as CSSProperties}>{m}</li>)}</ol>
          <p className="um-2-time">An evening, if it goes well.</p>
        </div>
        <div className="um-2-vs" aria-hidden="true">or</div>
        <div className="um-2-box">
          <p className="u-kicker">On LabBox</p>
          <strong>Press Start.</strong>
          <p>{lab.layers.map((l) => l.name).join(" · ")}, ready in about a minute.</p>
          <p className="um-2-first">Then your first challenge: <b>{lab.challenge}</b></p>
          <Link className="h-btn h-btn-primary" to="/login?signup=1">Start free →</Link>
        </div>
      </div>
    </div>
  );
}

/** 3. The chest of drawers (tansu): each drawer is one layer of the machine; point at one and it slides open. */
function Tansu() {
  const [lab, setLab] = useState(LABS[2]);
  const [open, setOpen] = useState<string | null>(null);
  return (
    <div className="um-3">
      <div className="um-3-text">
        <LabPicker lab={lab} onPick={(l) => { setLab(l); setOpen(null); }} />
        <h3>Everything the lab needs, <em>already inside.</em></h3>
        <p>Every lab is a machine of its own, packed like a chest of drawers: one drawer per layer. Open any of them; nothing to install.</p>
      </div>
      <div className="um-3-chest" onMouseLeave={() => setOpen(null)}>
        <div className="um-3-top"><span>{lab.title}</span></div>
        {lab.layers.map((l) => (
          <button key={l.name} type="button" className={`um-3-drawer ${open === l.name ? "is-open" : ""}`}
            onMouseEnter={() => setOpen(l.name)} onFocus={() => setOpen(l.name)} onClick={() => setOpen(l.name)}>
            <span className="um-3-front"><small>{l.kind}</small><strong>{l.name}</strong><i aria-hidden="true" /></span>
            <span className="um-3-inside">{l.note}</span>
          </button>
        ))}
        <div className="um-3-feet" aria-hidden="true"><span /><span /></div>
      </div>
    </div>
  );
}

/** 4. The boot log: a terminal plays the machine starting, then the first challenge slides in. */
function BootLog() {
  const [lab, setLab] = useState(LABS[3]);
  const [run, replay] = useReplay(lab);
  const [shown, setShown] = useState(0);
  const lines = [`learner:~$ labbox start ${lab.id}`, ...lab.boot.map((b) => `✓ ${b}`), "✓ machine ready in 58 s"];
  useEffect(() => {
    setShown(0);
    const t = setInterval(() => setShown((n) => (n >= lines.length ? n : n + 1)), 520);
    return () => clearInterval(t);
  }, [run]); // eslint-disable-line react-hooks/exhaustive-deps
  return (
    <div className="um-4">
      <div className="um-4-text">
        <LabPicker lab={lab} onPick={setLab} />
        <h3>From Start to your first challenge <em>in about a minute.</em></h3>
        <p>This is what happens on our side when you open a lab. On yours, you just wait for the editor to appear.</p>
        <button type="button" className="uh-replay" onClick={replay}>↺ Play again</button>
      </div>
      <div className="um-4-term">
        <div className="um-4-bar" aria-hidden="true"><span /><span /><span /><em>{lab.title}</em></div>
        <pre aria-label="Machine start log">{lines.slice(0, shown).join("\n")}{shown < lines.length ? <span className="um-caret" /> : null}</pre>
        <div className={`um-4-card ${shown >= lines.length ? "is-in" : ""}`}>
          <small>Challenge 1</small><strong>{lab.challenge}</strong><span>Read a little, write the code, press Check.</span>
        </div>
      </div>
    </div>
  );
}

/** 5. Three moves, three prints, one line each. */
function ThreeMoves() {
  const moves = [
    { n: "1", title: "Pick a challenge", text: "A real task in a real course: make the API answer, fix the slow query, build the agent.", img: "/ukiyo/labs/go-basics.webp" },
    { n: "2", title: "We start your machine", text: "Linux, the language, the framework and the databases, already set up. About a minute.", img: "/ukiyo/labs/langchain4j.webp" },
    { n: "3", title: "You build, we check", text: "Write the code in VS Code; Check runs real tests and tells you what to fix.", img: "/ukiyo/labs/rust-basics.webp" },
  ];
  return (
    <ol className="um-5">
      {moves.map((m) => (
        <li key={m.n}>
          <div className="uh-frame"><img src={m.img} alt="" /></div>
          <span className="um-5-n">{m.n}</span>
          <h3>{m.title}</h3>
          <p>{m.text}</p>
        </li>
      ))}
    </ol>
  );
}

const OPTIONS = [
  { title: "The machine builds itself", note: "Press Start: the layers stack up from Linux to your code, a timer runs, the first challenge appears. Switch labs to see their real setup.", View: BuildsItself },
  { title: "The setup you skip", note: "What you would do on your own, crossed out one by one, beside a single Start button.", View: SetupYouSkip },
  { title: "The chest of drawers", note: "The machine as a Japanese tansu, one drawer per layer. Point at a drawer to open it.", View: Tansu },
  { title: "The boot log", note: "A terminal plays a real machine starting, then the first challenge slides in.", View: BootLog },
  { title: "Three moves", note: "Pick a challenge, we start your machine, you build and we check. The simplest.", View: ThreeMoves },
];

export default function UkiyoMachinePage() {
  useEffect(() => { document.title = "Start a lab: five options | LabBox by Telusko"; }, []);
  return (
    <div className="ul-page u-home home">
      <header className="ul-top">
        <Logo to="/" />
        <nav aria-label="Options">{OPTIONS.map((o, i) => <a key={o.title} href={`#machine-${i + 1}`}>{i + 1}. {o.title}</a>)}</nav>
        <ThemeButton />
      </header>
      <main className="ul-main">
        <h1>What happens when you start a lab</h1>
        <p className="uh-section-lead">Five ways to say it on the home page. The labs and their layers are real.</p>
        {OPTIONS.map(({ title, note, View }, i) => (
          <section key={title} id={`machine-${i + 1}`} className="ul-section" aria-labelledby={`machine-${i + 1}-t`}>
            <p className="u-kicker">Option {i + 1} of {OPTIONS.length}</p>
            <h2 id={`machine-${i + 1}-t`}>{i + 1}. {title}</h2>
            <p className="ul-note">{note}</p>
            <View />
          </section>
        ))}
      </main>
    </div>
  );
}
