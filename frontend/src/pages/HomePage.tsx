import { useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { api, type CatalogLab } from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import ChoiceQuestion, { type ChoiceState } from "../lesson/ChoiceQuestion";
import { useTheme } from "../theme";

const TRACKS: { id: string; title: string }[] = [
  { id: "languages", title: "Programming languages" },
  { id: "frameworks", title: "Frameworks" },
  { id: "databases", title: "Databases" },
  { id: "devops", title: "DevOps" },
  { id: "system-design", title: "System design" },
  { id: "ai", title: "AI engineering" },
  { id: "interview", title: "Interview prep" },
];

// A small taste of a lesson. Demo content: answered in the browser, nothing is saved.
const DEMO = {
  question: 'What does this print?\n\n```python\nprint("chai" * 2)\n```',
  options: ["`chai2`", "`chaichai`", "An error"],
  answer: 1,
  explain: "Multiplying a string by a number repeats it. Every lab has a few small surprises like this.",
};

/** The window frame used by the hero preview and every showcase below it. */
function Frame({ label, children, className = "" }: { label?: string; children: ReactNode; className?: string }) {
  return (
    <div className={`preview frame ${className}`} role={label ? "img" : undefined} aria-label={label}>
      <div className="preview-chrome" aria-hidden="true">
        <span /><span /><span />
      </div>
      <div aria-hidden={label ? true : undefined}>{children}</div>
    </div>
  );
}

function LabPreview() {
  return (
    <Frame label="A LabBox lab: a lesson card on the left, code and a terminal on the right, and all checks passed">
      <div className="preview-body">
        <div className="preview-lesson">
          <span className="step-kind">Story</span>
          <div className="preview-title">Lunch orders at Dabba Express</div>
          <div className="preview-line w90" />
          <div className="preview-line w75" />
          <div className="preview-mission">🎯 Mission: greet every customer</div>
        </div>
        <div className="preview-work">
          <pre className="preview-code">
            <span className="tk-kw">def</span> <span className="tk-fn">greet</span>(name):{"\n"}
            {"    "}<span className="tk-kw">return</span> <span className="tk-str">f"Hello, {"{name}"}!"</span>
          </pre>
          <pre className="preview-term">
            <span className="tk-prompt">learner</span>:/workspace$ python3 greet.py{"\n"}Hello, Asha!
          </pre>
        </div>
      </div>
      <div className="preview-pass">3 of 3 passed 🎉</div>
    </Frame>
  );
}

function CheckShowcase() {
  return (
    <Frame label="A check result: 1 of 3 passed, with the expected and actual value side by side">
      <div className="sc-pad">
        <div className="sc-check-title fail">1 of 3 passed</div>
        <div className="sc-result sc-fail">
          <div className="sc-result-head"><span className="fail">✗</span> <strong>greet.py: return a greeting</strong></div>
          <p>greet('Asha') returned None</p>
          <div className="sc-eg">
            <div><span>Expected</span><code>'Hello, Asha!'</code></div>
            <div><span>Got</span><code>None</code></div>
          </div>
        </div>
        <div className="sc-result"><span className="pass">✓</span> <strong>math_utils.py: add two numbers</strong></div>
      </div>
    </Frame>
  );
}

function HintShowcase() {
  return (
    <Frame label="A task with two hints revealed: a nudge and a direction, and one hint left">
      <div className="sc-pad">
        <div className="sc-task-head">
          <strong>Longest word in a shop name</strong>
          <span className="xp-chip">12 XP</span>
        </div>
        <ol className="hint-list">
          <li><span className="hint-rung">Nudge</span>An empty sentence must give 0. What do you return before looking at any word?</li>
          <li><span className="hint-rung">Direction</span>Split the sentence on spaces, then look at each word's length.</li>
        </ol>
        <span className="sc-btn">💡 Hint (1 left)</span>
      </div>
    </Frame>
  );
}

function HabitShowcase() {
  const nodes = [
    { t: "Python functions", s: "done" },
    { t: "Lists and dicts", s: "available" },
    { t: "Python traps", s: "soon" },
  ];
  return (
    <Frame label="Progress: a 4 day streak, 330 XP, level 3, and a skill map with one skill done">
      <div className="sc-pad">
        <div className="sc-stats">
          <div><strong>🔥 4</strong><span>day streak</span></div>
          <div><strong>⭐ 330</strong><span>XP</span></div>
          <div><strong>Lv 3</strong><span>520 at level 4</span></div>
        </div>
        <div className="sc-map">
          {nodes.map((n, i) => (
            <div key={n.t} className="sc-map-step">
              {i > 0 && <span className={`sc-edge ${nodes[i - 1].s === "done" ? "on" : ""}`} />}
              <div className={`sc-node sc-${n.s}`}>
                <strong>{n.t}</strong>
                <span>{n.s === "done" ? "✓ Done" : n.s === "available" ? "Start" : "Soon"}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Frame>
  );
}

function Showcase({ eyebrow, title, text, flip, children }: { eyebrow: string; title: string; text: string; flip?: boolean; children: ReactNode }) {
  return (
    <section className={`showcase ${flip ? "flip" : ""}`}>
      <div className="showcase-text">
        <p className="eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
        <p className="lede">{text}</p>
      </div>
      <div className="showcase-visual">{children}</div>
    </section>
  );
}

export default function HomePage() {
  const { user } = useAuth();
  const { theme, toggle } = useTheme();
  const [catalog, setCatalog] = useState<CatalogLab[] | null>(null);
  const [demo, setDemo] = useState<ChoiceState>({ wrong: [], solved: false, answer: null, explain: null });

  useEffect(() => {
    document.title = "LabBox: learn tech by doing";
    api.catalog().then(setCatalog).catch(() => setCatalog([]));
  }, []);

  function pickDemo(i: number) {
    setDemo((d) => (i === DEMO.answer ? { ...d, solved: true, answer: i, explain: DEMO.explain } : { ...d, wrong: [...d.wrong, i] }));
  }

  const cta = user ? (
    <Link className="btn btn-primary btn-big" to="/labs">Continue learning →</Link>
  ) : (
    <Link className="btn btn-primary btn-big" to="/login?signup=1">Start free →</Link>
  );
  const live = catalog ?? [];

  return (
    <div className="home">
      <header className="home-header">
        <Logo to="/" />
        <nav aria-label="Main" className="home-nav">
          <a href="#try">How it works</a>
          <a href="#tracks">Tracks</a>
        </nav>
        <span className="spacer" />
        <button className="btn btn-small btn-ghost" onClick={toggle} aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}>
          {theme === "dark" ? "☀" : "☾"}
        </button>
        {user ? (
          <Link className="btn btn-small btn-primary" to="/labs">Continue learning →</Link>
        ) : (
          <>
            <Link className="btn btn-small btn-ghost" to="/login">Log in</Link>
            <Link className="btn btn-small btn-primary" to="/login?signup=1">Start free</Link>
          </>
        )}
      </header>

      <main>
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-text">
            <h1 id="hero-title">Learn tech by doing, not watching.</h1>
            <p className="hero-sub">Real machines, real code, small steps, instant feedback. Every few minutes you read a little, guess, try, and win.</p>
            <div className="hero-cta">
              {cta}
              <a className="btn btn-big btn-ghost" href="#try">Try a question</a>
            </div>
          </div>
          <LabPreview />
        </section>

        <div id="try" className="showcases">
          <Showcase eyebrow="Predict" title="Guess first. Then see why." text="Every lesson starts with a small surprise. Being wrong for a second is how it sticks. Go on, try this one.">
            <Frame className="try-card">
              <div className="sc-pad">
                <ChoiceQuestion question={DEMO.question} options={DEMO.options} state={demo} busy={false} onPick={pickDemo} />
              </div>
            </Frame>
          </Showcase>

          <Showcase flip eyebrow="Check" title="Fails that tell you why." text="Hidden tests run on a clean machine and show what they expected next to what you gave them.">
            <CheckShowcase />
          </Showcase>

          <Showcase eyebrow="Hints" title="Hints, not answers." text="A nudge, then a direction, then almost there. You still write the code, so you still own it.">
            <HintShowcase />
          </Showcase>

          <Showcase flip eyebrow="Habit" title="Five minutes a day adds up." text="XP for every win, a streak that survives a busy day, and a skill map that lights up as you go.">
            <HabitShowcase />
          </Showcase>
        </div>

        <section className="home-tracks" id="tracks" aria-labelledby="tracks-title">
          <h2 id="tracks-title">Seven tracks. Real tools in every one.</h2>
          <ul className="track-chips">
            {TRACKS.map((t) => {
              const n = live.filter((l) => l.track === t.id).length;
              return (
                <li key={t.id} className={`track-chip ${n ? "is-live" : ""}`}>
                  {t.title}
                  <span>{catalog === null ? "" : n ? `${n} lab${n === 1 ? "" : "s"}` : "Soon"}</span>
                </li>
              );
            })}
          </ul>
          {live.length > 0 && (
            <p className="muted live-labs">
              Live now: {live.map((l) => l.title).join(" · ")}
            </p>
          )}
        </section>

        <section className="home-final" aria-labelledby="final-title">
          <h2 id="final-title">Your first win is about three minutes away.</h2>
          <p className="lede">Sign up, pick a goal, and you are writing code on a real machine within a minute.</p>
          {cta}
        </section>
      </main>

      <footer className="home-footer">
        <Logo />
        <span className="muted small-text">Hands-on labs for programming, databases, DevOps, system design and AI.</span>
      </footer>
    </div>
  );
}
