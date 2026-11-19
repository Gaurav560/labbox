import { useCallback, useEffect, useState, type ReactNode } from "react";
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
// The "pick a lab" grid: these labs, in this order (any that are not live are skipped), then the
// coming-soon cards, which are not links.
const FEATURED = [
  "express-api", "fastapi-first-api", "go-basics",
  "java-basics", "spring-boot-first-api", "javascript-inside-out",
  "python-basics", "sql-from-zero", "postgres-indexing-incident",
];
const COMING_SOON = [
  { id: "redis-in-practice", title: "Redis in practice", track: "Databases", cover: "/covers/redis-in-practice.svg" },
  { id: "git-without-fear", title: "Git without fear", track: "DevOps", cover: "/covers/git-without-fear.svg" },
  { id: "docker-start-to-ship", title: "Docker: start to ship", track: "DevOps", cover: "/covers/docker-start-to-ship.svg" },
  { id: "kubernetes-from-zero", title: "Kubernetes from zero", track: "DevOps", cover: "/covers/kubernetes-from-zero.svg" },
  { id: "linux-on-call", title: "Linux on call", track: "DevOps", cover: "/covers/linux-on-call.svg" },
  { id: "nginx-and-networking", title: "Nginx and networking", track: "DevOps", cover: "/covers/nginx-and-networking.svg" },
];

// Real technology logos (devicon, MIT: /logos/LICENSE-devicon) for the moving strip.
const STRIP = ["python", "java", "go", "javascript", "typescript", "postgresql", "redis", "docker", "kubernetes", "spring", "fastapi", "nodejs", "git", "linux"];

// The hero terminal: short sessions from the real labs. Each visitor starts on a random one, then
// they play one after another in a shuffled order. "$ " lines are typed, "! " is a pager alert.
interface Session { lab: string; incident?: boolean; lines: string[] }
const SESSIONS: Session[] = [
  {
    lab: "postgres-indexing-incident", incident: true,
    lines: [
      "! PAGER  checkout is slow: p99 4.2 s",
      "$ psql -c 'EXPLAIN SELECT * FROM orders WHERE customer_id = 42'",
      "Seq Scan on orders  (rows=1000000)",
      "$ psql -c 'CREATE INDEX ON orders (customer_id)'",
      "CREATE INDEX",
      "$ check",
      "✓ 1 of 1 passed   p99 38 ms   +325 XP",
    ],
  },
  {
    lab: "python-basics",
    lines: ["$ python3 greet.py", "Hello, Asha!", "$ python3 -c 'from math_utils import add; print(add(2, 3))'", "5", "$ check", "✓ 3 of 3 passed   +60 XP"],
  },
  {
    lab: "fastapi-first-api",
    lines: [
      "$ uvicorn main:app --host 0.0.0.0",
      "Uvicorn running on http://0.0.0.0:8000",
      "$ curl localhost:8000/menu/vada%20pav",
      '{"item":"vada pav","price":25}',
      "$ check",
      "✓ 2 of 2 passed   +40 XP",
    ],
  },
  {
    lab: "spring-boot-first-api",
    lines: [
      "$ mvn -q package && java -jar target/merchant-api.jar",
      "Started MerchantApiApplication in 2.4 seconds",
      "$ curl localhost:8080/merchants",
      '["Annapurna Mess","Brew Point","Kirana King"]',
      "$ check",
      "✓ 2 of 2 passed   +40 XP",
    ],
  },
  {
    lab: "javascript-inside-out",
    lines: ["$ node -e 'console.log(\"2\" + 2, \"2\" - 2)'", "22 0", "$ node -e 'console.log(0.1 + 0.2 === 0.3)'", "false", "$ check", "✓ 4 of 4 passed   +80 XP"],
  },
  {
    lab: "go-basics",
    lines: ["$ go run ./cmd", "3500", "1250 <nil>", "map[coffee:3 vada pav:1] coffee", "$ check", "✓ 4 of 4 passed   +80 XP"],
  },
  {
    lab: "sql-from-zero",
    lines: [
      "$ psql -f q3.sql",
      " name           | revenue_paise",
      " Koramangala    |       1849200",
      " Andheri        |       1512650",
      "$ check",
      "✓ q3.sql matches the expected rows   +20 XP",
    ],
  },
  {
    lab: "express-api",
    lines: [
      "$ node server.js",
      "Dabba Express API on http://0.0.0.0:3000",
      "$ curl -s -X POST localhost:3000/orders",
      '{"error":"Send items (a list of dishes) and area"}',
      "$ check",
      "✓ 2 of 2 passed   +40 XP",
    ],
  },
  {
    lab: "java-basics",
    lines: ["$ java Greeter.java", "Hello, Asha!", "$ check", "✗ 1 of 2 passed: longestWord(\"\") should be 0", "$ check", "✓ 2 of 2 passed   +40 XP"],
  },
  {
    lab: "java-collections",
    lines: [
      "$ java Payments.java",
      "20000",
      "{Brew Point=5000, Kirana King=15000}",
      "[Brew Point, Kirana King]",
      "[Kirana King]",
      "$ check",
      "✓ 4 of 4 passed   +80 XP",
    ],
  },
  {
    lab: "python-collections",
    lines: [
      "$ python3 orders.py",
      "330",
      "['dal rice']",
      "['Aundh', 'Baner']",
      "$ check",
      "✓ 4 of 4 passed   +80 XP   🔥 5 day streak",
    ],
  },
];

/** A shuffled order of all sessions, different for every visitor. */
function shuffled(n: number): number[] {
  const order = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  return order;
}

// A small taste of a lesson. Demo content: answered in the browser, nothing is saved.
const DEMO = {
  question: 'What does this print?\n\n```python\nprint("coffee" * 2)\n```',
  options: ["`coffee2`", "`coffeecoffee`", "An error"],
  answer: 1,
  explain: "Multiplying a string by a number repeats it. Every lab has a few small surprises like this.",
};

function TermLine({ text }: { text: string }) {
  if (text.startsWith("$ ")) return <div><span className="h-prompt">$</span> {text.slice(2)}</div>;
  if (text.startsWith("! ")) return <div className="h-alert">{text.slice(2)}</div>;
  if (text.startsWith("✗")) return <div className="h-bad-line">{text}</div>;
  return <div className={text.startsWith("✓") ? "h-ok" : "h-out"}>{text}</div>;
}

function LabTerminal() {
  const [order] = useState(() => shuffled(SESSIONS.length));
  const [at, setAt] = useState(0);
  const session = SESSIONS[order[at]];
  const next = useCallback(() => setAt((i) => (i + 1) % order.length), [order.length]);
  const { shown, typing } = useTyped(session.lines, 3500, next);
  return (
    <div className="h-term" role="img" aria-label="A lab terminal: a learner runs real commands in a lab and the check passes">
      <div className="h-term-bar" aria-hidden="true">
        <span className="h-dots"><i /><i /><i /></span>
        {session.incident ? <span className="h-live">● INCIDENT</span> : <span className="h-lab-name">● {session.lab}</span>}
        {session.incident && <span className="h-timer">14:52</span>}
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

function SoonTile({ title, track, cover }: { title: string; track: string; cover: string }) {
  return (
    <div className="h-lab h-lab-soon" aria-label={`${title}: coming soon`}>
      <div className="h-lab-img"><img src={cover} alt="" loading="lazy" /><span className="h-soon-chip">Coming soon</span></div>
      <div className="h-lab-text">
        <strong>{title}</strong>
        <span>{track} · coming soon</span>
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
            <p className="hero-sub">LabBox is hands-on coding labs in your browser. Each lab gives you a real Linux machine with a code editor and a terminal, then guides you step by step through Python, Java, SQL, DevOps and more, checking your code as you go. Nothing to install.</p>
            <div className="hero-cta">
              {cta}
              <a className="h-btn h-btn-ghost" href="#how">Try a question</a>
            </div>
          </div>
          <LabTerminal />
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
            <p className="h-kicker">Labs</p>
            <h2 id="labs-title">Pick a lab. <span className="h-soft">Start in a minute.</span></h2>
            <div className="h-labs">
              {FEATURED.map((id) => live.find((l) => l.id === id)).filter((l): l is CatalogLab => !!l).map((lab) => (
                <LabTile key={lab.id} lab={lab} to={labLink(lab)} />
              ))}
              {COMING_SOON.filter((c) => !live.some((l) => l.id === c.id)).map((c) => <SoonTile key={c.id} {...c} />)}
            </div>
            <div className="h-labs-more">
              <Link className="h-btn h-btn-ghost" to={user ? "/labs" : "/login?signup=1"}>See all labs →</Link>
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
          <h2 id="final-title">Your first win is about three minutes away.</h2>
          <p>Sign up, pick a goal, and you are writing code on a real machine within a minute.</p>
          {user ? (
            <Link className="h-btn h-btn-black" to="/labs">Continue learning →</Link>
          ) : (
            <Link className="h-btn h-btn-black" to="/login?signup=1">Start your first lab →</Link>
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
