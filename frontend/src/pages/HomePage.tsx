import { useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { api, type CatalogLab } from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import { Copyright, SiteLinks } from "../components/SiteFooter";
import { useTyped } from "../components/useTyped";
import ChoiceQuestion, { type ChoiceState } from "../lesson/ChoiceQuestion";
import { useTheme } from "../theme";

const TRACKS: { id: string; title: string; blurb: string }[] = [
  { id: "languages", title: "Programming languages", blurb: "Python, Java, Go, JavaScript, SQL" },
  { id: "frameworks", title: "Frameworks", blurb: "FastAPI, Spring Boot, Express" },
  { id: "databases", title: "Databases", blurb: "Postgres, Redis, real incidents" },
  { id: "devops", title: "DevOps", blurb: "Linux, Git, Docker, Kubernetes" },
  { id: "system-design", title: "System design", blurb: "Build it, then load test it" },
  { id: "ai", title: "AI engineering", blurb: "Tokens to RAG to agents" },
  { id: "interview", title: "Interview prep", blurb: "Traps, bugs and drills" },
];

const LIVE_SHOWN = 6; // lab titles listed under the tracks; the rest become "and N more"
const LABS_SHOWN = 6; // lab cards in the "pick a lab" grid

// Real technology logos (devicon, MIT: /logos/LICENSE-devicon) for the moving strip.
const STRIP = ["python", "java", "go", "javascript", "typescript", "postgresql", "redis", "docker", "kubernetes", "spring", "fastapi", "nodejs", "git", "linux"];

// The hero terminal: a real incident lab, start to finish.
const INCIDENT = [
  "! PAGER  checkout is slow: p99 4.2 s",
  "$ psql -c 'EXPLAIN SELECT * FROM orders WHERE customer_id = 42'",
  "Seq Scan on orders  (rows=1000000)",
  "$ psql -c 'CREATE INDEX ON orders (customer_id)'",
  "CREATE INDEX",
  "$ check",
  "✓ 1 of 1 passed   p99 38 ms   +325 XP",
];

// A small taste of a lesson. Demo content: answered in the browser, nothing is saved.
const DEMO = {
  question: 'What does this print?\n\n```python\nprint("chai" * 2)\n```',
  options: ["`chai2`", "`chaichai`", "An error"],
  answer: 1,
  explain: "Multiplying a string by a number repeats it. Every lab has a few small surprises like this.",
};

function TermLine({ text }: { text: string }) {
  if (text.startsWith("$ ")) return <div><span className="h-prompt">$</span> {text.slice(2)}</div>;
  if (text.startsWith("! ")) return <div className="h-alert">{text.slice(2)}</div>;
  return <div className={text.startsWith("✓") ? "h-ok" : "h-out"}>{text}</div>;
}

function IncidentTerminal() {
  const { shown, typing } = useTyped(INCIDENT, 5000);
  return (
    <div className="h-term" role="img" aria-label="A lab terminal: a slow checkout alert, the learner adds an index, and the check passes with 325 XP">
      <div className="h-term-bar" aria-hidden="true">
        <span className="h-dots"><i /><i /><i /></span>
        <span className="h-live">● INCIDENT</span>
        <span className="h-timer">14:52</span>
      </div>
      <div className="h-term-body" aria-hidden="true">
        {shown.map((l, i) => <TermLine key={i} text={l} />)}
        {typing && <TermLine text={typing} />}
        <span className="h-cursor" />
      </div>
    </div>
  );
}

function Panel({ n, title, text, className = "", children }: { n: string; title: string; text: string; className?: string; children: ReactNode }) {
  return (
    <article className={`h-panel ${className}`}>
      <header>
        <span className="h-num">{n}</span>
        <h3>{title}</h3>
        <p>{text}</p>
      </header>
      <div className="h-panel-body">{children}</div>
    </article>
  );
}

function CheckDemo() {
  return (
    <div className="h-mini" aria-label="A check result: 1 of 3 passed, with the expected and actual value side by side" role="img">
      <div className="h-mini-title"><span className="h-bad">1 of 3 passed</span></div>
      <div className="h-res h-res-bad">
        <strong><span className="h-bad">✗</span> greet.py: return a greeting</strong>
        <div className="h-eg">
          <div><span>Expected</span><code>'Hello, Asha!'</code></div>
          <div><span>Got</span><code>None</code></div>
        </div>
      </div>
      <div className="h-res"><strong><span className="h-good">✓</span> math_utils.py: add two numbers</strong></div>
    </div>
  );
}

function HintDemo() {
  return (
    <div className="h-mini" role="img" aria-label="Two hints revealed: a nudge and a direction, one hint left">
      <ol className="h-hints">
        <li><span>Nudge</span>An empty sentence must give 0. What do you return first?</li>
        <li><span>Direction</span>Split on spaces, then look at each word's length.</li>
      </ol>
      <span className="h-chip">💡 1 hint left</span>
    </div>
  );
}

function HabitDemo() {
  const days = [1, 1, 1, 0, 1, 1, 1];
  return (
    <div className="h-mini" role="img" aria-label="A 6 day streak, 330 XP and level 3">
      <div className="h-big-stats">
        <div><strong>🔥 6</strong><span>day streak</span></div>
        <div><strong>330</strong><span>XP</span></div>
        <div><strong>Lv 3</strong><span>next at 520</span></div>
      </div>
      <div className="h-week">
        {days.map((d, i) => <i key={i} className={d ? "on" : ""}>{"MTWTFSS"[i]}</i>)}
      </div>
    </div>
  );
}

function LabTile({ lab, to }: { lab: CatalogLab; to: string }) {
  return (
    <Link to={to} className="h-lab">
      <div className="h-lab-img">{lab.cover_url ? <img src={lab.cover_url} alt="" loading="lazy" /> : null}</div>
      <div className="h-lab-text">
        <strong>{lab.title}</strong>
        <span>{TRACKS.find((t) => t.id === lab.track)?.title ?? lab.track} · {lab.estimated_minutes} min</span>
      </div>
    </Link>
  );
}

export default function HomePage() {
  const { user } = useAuth();
  const { theme, toggle } = useTheme();
  const [catalog, setCatalog] = useState<CatalogLab[] | null>(null);
  const [demo, setDemo] = useState<ChoiceState>({ wrong: [], solved: false, answer: null, explain: null });

  useEffect(() => {
    document.title = "LabBox by Telusko: learn tech by doing";
    api.catalog().then(setCatalog).catch(() => setCatalog([]));
  }, []);

  function pickDemo(i: number) {
    setDemo((d) => (i === DEMO.answer ? { ...d, solved: true, answer: i, explain: DEMO.explain } : { ...d, wrong: [...d.wrong, i] }));
  }

  const cta = user ? (
    <Link className="h-btn h-btn-primary" to="/labs">Continue learning →</Link>
  ) : (
    <Link className="h-btn h-btn-primary" to="/login?signup=1">Start free →</Link>
  );
  const live = catalog ?? [];
  const labLink = (lab: CatalogLab) => (user ? `/labs/${lab.id}` : "/login?signup=1");

  return (
    <div className="home">
      <header className="home-header">
        <Logo to="/" />
        <nav aria-label="Main" className="home-nav">
          <a href="#how">How it works</a>
          <a href="#labs">Labs</a>
          <a href="#tracks">Tracks</a>
        </nav>
        <span className="spacer" />
        <button className="h-icon" onClick={toggle} aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}>
          {theme === "dark" ? "☀" : "☾"}
        </button>
        {user ? (
          <Link className="h-btn h-btn-primary h-btn-sm" to="/labs">Continue learning →</Link>
        ) : (
          <>
            <Link className="h-btn h-btn-ghost h-btn-sm" to="/login">Log in</Link>
            <Link className="h-btn h-btn-primary h-btn-sm" to="/login?signup=1">Start free</Link>
          </>
        )}
      </header>

      <main>
        <section className="hero" aria-labelledby="hero-title">
          <div className="h-hero-bg" aria-hidden="true" />
          <div className="hero-text">
            <p className="h-pill">
              <span className="h-pulse" aria-hidden="true" />
              {catalog === null ? "Labs are live" : `${live.length} lab${live.length === 1 ? "" : "s"} live now`}
            </p>
            <h1 id="hero-title">
              Learn tech by <span className="h-red-word">doing<svg viewBox="0 0 200 16" preserveAspectRatio="none" aria-hidden="true"><path d="M3 11 C 50 3, 120 3, 197 9" /></svg></span>, not <span className="h-strike">watching</span>.
            </h1>
            <p className="hero-sub">Real machines, real code, small steps, instant feedback. Every few minutes you read a little, guess, try, and win.</p>
            <div className="hero-cta">
              {cta}
              <a className="h-btn h-btn-ghost" href="#how">Try a question</a>
            </div>
          </div>
          <IncidentTerminal />
        </section>

        <section className="h-strip" aria-label="Technologies you practise on">
          <div className="h-strip-track">
            {[...STRIP, ...STRIP].map((n, i) => (
              <span key={i} className="h-strip-logo" aria-hidden={i >= STRIP.length || undefined}>
                <img src={`/logos/${n}.svg`} alt={i < STRIP.length ? n : ""} />
              </span>
            ))}
          </div>
        </section>

        <section className="h-stats" aria-label="LabBox in numbers">
          <div><strong>{catalog === null ? "…" : live.length}</strong><span>hands-on labs</span></div>
          <div><strong>~60 s</strong><span>to a real machine</span></div>
          <div><strong>0</strong><span>videos to sit through</span></div>
          <div><strong>7</strong><span>tracks</span></div>
        </section>

        <section id="how" className="h-section" aria-labelledby="how-title">
          <p className="h-kicker">How a lab works</p>
          <h2 id="how-title">Guess. Try. Break it. <span className="h-yellow">Fix it.</span></h2>
          <div className="h-bento">
            <Panel n="01" title="Predict first" text="Every lesson opens with a small surprise. Go on, try this one." className="h-panel-wide">
              <div className="try-card"><ChoiceQuestion question={DEMO.question} options={DEMO.options} state={demo} busy={false} onPick={pickDemo} /></div>
            </Panel>
            <Panel n="02" title="Checks that explain" text="Hidden tests on a clean machine show what they expected next to what you gave.">
              <CheckDemo />
            </Panel>
            <Panel n="03" title="Hints, not answers" text="A nudge, then a direction. You still write the code.">
              <HintDemo />
            </Panel>
            <Panel n="04" title="A habit that sticks" text="XP for every win and a streak that survives a busy day.">
              <HabitDemo />
            </Panel>
          </div>
        </section>

        {live.length > 0 && (
          <section id="labs" className="h-section" aria-labelledby="labs-title">
            <p className="h-kicker">Live now</p>
            <h2 id="labs-title">Pick a lab. <span className="h-soft">Start in a minute.</span></h2>
            <div className="h-labs">
              {live.slice(0, LABS_SHOWN).map((lab) => <LabTile key={lab.id} lab={lab} to={labLink(lab)} />)}
            </div>
          </section>
        )}

        <section className="home-tracks h-section" id="tracks" aria-labelledby="tracks-title">
          <p className="h-kicker">Seven tracks</p>
          <h2 id="tracks-title">Real tools in every one.</h2>
          <ul className="track-list">
            {TRACKS.map((t, i) => {
              const n = live.filter((l) => l.track === t.id).length;
              return (
                <li key={t.id} className={`track-chip ${n ? "is-live" : ""}`}>
                  <span className="t-num">{String(i + 1).padStart(2, "0")}</span>
                  <span className="t-name">{t.title}<small>{t.blurb}</small></span>
                  <span className="t-count">{catalog === null ? "" : n ? `${n} lab${n === 1 ? "" : "s"}` : "Soon"}</span>
                </li>
              );
            })}
          </ul>
          {live.length > 0 && (
            <p className="muted live-labs">
              Live now: {live.slice(0, LIVE_SHOWN).map((l) => l.title).join(" · ")}
              {live.length > LIVE_SHOWN && ` and ${live.length - LIVE_SHOWN} more`}
            </p>
          )}
        </section>

        <section className="home-final" aria-labelledby="final-title">
          <span className="h-sticker" aria-hidden="true">FREE</span>
          <h2 id="final-title">Your first win is about three minutes away.</h2>
          <p>Sign up, pick a goal, and you are writing code on a real machine within a minute.</p>
          {user ? (
            <Link className="h-btn h-btn-black" to="/labs">Continue learning →</Link>
          ) : (
            <Link className="h-btn h-btn-black" to="/login?signup=1">Start free →</Link>
          )}
        </section>
      </main>

      <footer className="home-footer">
        <div className="home-footer-brand">
          <Logo />
          <span className="muted small-text">Hands-on labs for programming, databases, DevOps, system design and AI.</span>
        </div>
        <SiteLinks />
        <Copyright />
      </footer>
    </div>
  );
}
