import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type CatalogLab } from "../api";
import { useAuth } from "../auth";
import ChoiceQuestion, { type ChoiceState } from "../lesson/ChoiceQuestion";
import { useTheme } from "../theme";

const TRACKS: { id: string; title: string; blurb: string }[] = [
  { id: "languages", title: "Programming languages", blurb: "Python, Java, JavaScript, Go, Rust and SQL, from first function to the traps." },
  { id: "frameworks", title: "Frameworks", blurb: "Spring Boot, FastAPI, Express and React, the way real teams use them." },
  { id: "databases", title: "Databases", blurb: "Postgres in depth, Redis in practice, and the incidents that wake people up." },
  { id: "devops", title: "DevOps", blurb: "Linux, Docker, Kubernetes, Nginx and CI/CD on machines you can break." },
  { id: "system-design", title: "System design", blurb: "Run a small distributed system and make it hit real targets under load." },
  { id: "ai", title: "AI engineering", blurb: "Tokenizers to transformers, then RAG, agents and evals, built for real." },
  { id: "interview", title: "Interview prep", blurb: "Bug hunts, language traps and design drills that feel like the real thing." },
];

const STEPS = [
  { n: 1, title: "Read a little", text: "One idea at a time, in a short card. Never a wall of text." },
  { n: 2, title: "Predict", text: "Guess what happens before you see it. Being wrong is where it sticks." },
  { n: 3, title: "Try it for real", text: "Your own Linux machine, an editor and a terminal, right in the browser." },
  { n: 4, title: "Check and win", text: "Hidden tests run on a clean machine and tell you exactly what is off." },
];

const WHY = [
  { title: "A real machine for every lab", text: "Not a simulation. Install things, run servers, break them and fix them." },
  { title: "A story to pull you forward", text: "Help Priya get Dabba Express through the lunch rush, one function at a time." },
  { title: "Hints, not answers", text: "A nudge, then a direction, then almost there. You still write the code." },
  { title: "A habit you can keep", text: "XP, streaks and a two minute daily drill for the busy days." },
];

// A small taste of a lesson. Demo content: answered in the browser, nothing is saved.
const DEMO = {
  question: 'What does this print?\n\n```python\nprint("chai" * 2)\n```',
  options: ["`chai2`", "`chaichai`", "An error"],
  answer: 1,
  explain: "Multiplying a string by a number repeats it. Python is full of small surprises like this, and every lab has a few.",
};

function LabPreview() {
  return (
    <div className="preview" role="img" aria-label="A LabBox lab: a lesson card on the left, code and a terminal on the right, and all checks passed">
      <div className="preview-chrome" aria-hidden="true">
        <span /><span /><span />
      </div>
      <div className="preview-body" aria-hidden="true">
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
      <div className="preview-pass" aria-hidden="true">3 of 3 passed 🎉</div>
    </div>
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

  return (
    <div className="home">
      <header className="home-header">
        <Link to="/" className="brand home-brand">LabBox</Link>
        <nav aria-label="Main" className="home-nav">
          <a href="#how">How it works</a>
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

        <section className="home-section split" id="try" aria-labelledby="try-title">
          <div className="split-intro">
            <p className="eyebrow">Try it</p>
            <h2 id="try-title">Guess first. Then see why.</h2>
            <p className="lede">Every lesson works like this. A small surprise, a quick guess, and the idea sticks.</p>
          </div>
          <div className="try-card">
            <ChoiceQuestion question={DEMO.question} options={DEMO.options} state={demo} busy={false} onPick={pickDemo} />
          </div>
        </section>

        <section className="home-section" id="how" aria-labelledby="how-title">
          <p className="eyebrow">How it works</p>
          <h2 id="how-title">Four steps, a few minutes each.</h2>
          <ol className="steps">
            {STEPS.map((s) => (
              <li key={s.n} className="step">
                <span className="step-n" aria-hidden="true">{String(s.n).padStart(2, "0")}</span>
                <h3>{s.title}</h3>
                <p>{s.text}</p>
              </li>
            ))}
          </ol>
        </section>

        <section className="home-section split" aria-labelledby="why-title">
          <div className="split-intro">
            <p className="eyebrow">Why it sticks</p>
            <h2 id="why-title">Built for doing, not watching.</h2>
          </div>
          <dl className="why-list">
            {WHY.map((w) => (
              <div key={w.title} className="why-item">
                <dt>{w.title}</dt>
                <dd>{w.text}</dd>
              </div>
            ))}
          </dl>
        </section>

        <section className="home-section" id="tracks" aria-labelledby="tracks-title">
          <p className="eyebrow">Tracks</p>
          <h2 id="tracks-title">Pick a direction.</h2>
          <p className="lede">New labs land in these tracks as they are built.</p>
          <ul className="track-rows">
            {TRACKS.map((t) => {
              const labs = catalog?.filter((l) => l.track === t.id) ?? [];
              return (
                <li key={t.id} className={`track-card ${labs.length ? "track-live" : ""}`}>
                  <div className="track-main-col">
                    <h3>{t.title}</h3>
                    <p>{t.blurb}</p>
                    {labs.length > 0 && (
                      <ul className="track-labs">
                        {labs.map((l) => (
                          <li key={l.id}>
                            <strong>{l.title}</strong>
                            <span>
                              {[l.level && l.level[0].toUpperCase() + l.level.slice(1), l.estimated_minutes && `${l.estimated_minutes} min`]
                                .filter(Boolean)
                                .join(" · ")}
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <span className={`track-status ${labs.length ? "is-live" : ""}`}>
                    {catalog === null ? "" : labs.length ? `${labs.length} lab${labs.length === 1 ? "" : "s"} live` : "Coming soon"}
                  </span>
                </li>
              );
            })}
          </ul>
        </section>

        <section className="home-final" aria-labelledby="final-title">
          <h2 id="final-title">Your first win is about three minutes away.</h2>
          <p className="lede">Sign up, pick a goal, and you are writing code on a real machine within a minute.</p>
          {cta}
        </section>
      </main>

      <footer className="home-footer">
        <span>LabBox</span>
        <span className="muted small-text">Hands-on labs for programming, databases, DevOps, system design and AI.</span>
      </footer>
    </div>
  );
}
