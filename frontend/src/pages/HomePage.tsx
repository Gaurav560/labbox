import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, type CatalogLab } from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import { Copyright, SiteLinks } from "../components/SiteFooter";
import HeroTour from "../components/HeroTour";
import { AiTrack, HomeFaq, InsideLab } from "../components/HomeSections";
import { byCategory, Directory } from "../components/UkiyoDirectory";
import { SITE } from "../site";
import { useTheme } from "../theme";

/*
 * The public home page in the Ukiyo design (owner, 25 November: "redesign the home page; the inside looks cool").
 * One language with the inside: a framed woodblock print in the hero, fine rules instead of cards, serif headings,
 * one red button per screen, and the dashboard's own directory of labs.
 */

// Real technology logos (devicon, MIT: /logos/LICENSE-devicon) for the moving strip.
const STRIP = ["python", "java", "go", "javascript", "typescript", "postgresql", "redis", "docker", "kubernetes", "spring", "fastapi", "nodejs", "git", "linux"];

/** A vermilion brush stroke under a word, drawn once when the page opens. */
function Brush({ children }: { children: string }) {
  return (
    <span className="uh-brush">{children}<svg viewBox="0 0 200 16" preserveAspectRatio="none" aria-hidden="true"><path d="M3 11 C 50 3, 120 3, 197 9" /></svg></span>
  );
}

export default function HomePage() {
  const { user } = useAuth();
  const { theme, toggle } = useTheme();
  const [catalog, setCatalog] = useState<CatalogLab[] | null>(null);

  useEffect(() => {
    document.title = "LabBox by Telusko: AI labs and hands-on tech labs";
    api.catalog().then(setCatalog).catch(() => setCatalog([]));
  }, []);

  const live = useMemo(() => catalog ?? [], [catalog]);
  const categories = useMemo(() => byCategory(live).filter((g) => g.labs.length).length, [live]);
  const cta = user ? (
    <Link className="h-btn h-btn-primary" to="/labs">Continue learning →</Link>
  ) : (
    <Link className="h-btn h-btn-primary" to="/login?signup=1">Start free →</Link>
  );
  const labLink = (lab: CatalogLab) => (user ? `/courses/${lab.id}` : "/login?signup=1");

  return (
    <div className="home u-home">
      <header className="home-header">
        <Logo to="/" />
        <nav aria-label="Main" className="home-nav">
          <a href="#ai">AI labs</a>
          <Link to="/library">Premium Reads</Link>
          <a href="#faq">FAQs</a>
        </nav>
        <span className="spacer" />
        <button className="h-icon" onClick={toggle} aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}>
          {theme === "dark" ? "☀" : "☾"}
        </button>
        {user ? (
          <Link className="h-btn h-btn-primary h-btn-sm" to="/labs">Continue learning →</Link>
        ) : (
          <Link className="h-btn h-btn-ghost h-btn-sm" to="/login">Log in</Link>
        )}
      </header>

      <main>
        <section className="uh-hero" aria-labelledby="hero-title">
          <div className="uh-hero-text">
            <p className="u-kicker">
              {catalog === null ? "Hands-on labs" : `${live.length} labs live`} <span className="uh-dot" aria-hidden="true" /> AI track launching
            </p>
            <h1 id="hero-title">Learn AI by <Brush>building</Brush> it, not <span className="uh-strike">watching</span>.</h1>
            <p className="uh-lead">Hands-on AI labs on your own machine in the browser: call real models, build RAG search and agents, write evals, with a guide checking every step. And the engineering around them: system design, languages, databases and DevOps.</p>
            <div className="uh-cta">
              {cta}
              <a className="uh-link" href="#inside">See inside a lab →</a>
            </div>
          </div>
          <figure className="uh-hero-print">
            <div className="uh-frame">
              <img src="/ukiyo/red-fuji.webp" width={1280} height={854} alt="Woodblock print: Katsushika Hokusai, Fine Wind, Clear Morning (Red Fuji), about 1831" />
            </div>
            <figcaption className="u-print-credit">Katsushika Hokusai, Fine Wind, Clear Morning, about 1831</figcaption>
          </figure>
        </section>

        <section className="h-strip uh-strip" aria-label="Technologies you practise on">
          <div className="h-strip-track">
            {[...STRIP, ...STRIP].map((n, i) => (
              <span key={i} className="h-strip-logo" aria-hidden={i >= STRIP.length || undefined}>
                <img src={`/logos/${n}.svg`} alt={i < STRIP.length ? n : ""} />
              </span>
            ))}
          </div>
        </section>

        <section className="uh-stats" aria-label="LabBox in numbers">
          <div><strong>{catalog === null ? "…" : live.length}</strong><span>hands-on labs</span></div>
          <div><strong>~60 s</strong><span>to a real machine</span></div>
          <div><strong>0</strong><span>videos to sit through</span></div>
          <div><strong>24</strong><span>AI labs on the way</span></div>
        </section>

        <section id="inside" className="uh-section" aria-labelledby="inside-title">
          <header className="uh-head">
            <p className="u-kicker">Inside a lab</p>
            <h2 id="inside-title">Not exercises. <em>Real systems.</em></h2>
          </header>
          <InsideLab tour={<HeroTour />} />
        </section>

        <section id="ai" className="uh-section uh-ai" aria-labelledby="ai-title">
          <div className="uh-ai-head">
            <figure className="uh-ai-print">
              <div className="uh-frame"><img src="/ukiyo/tracks/ai-pagoda.webp" alt="" /></div>
            </figure>
            <header className="uh-head">
              <p className="u-kicker">AI labs <span className="h-launch">Launching</span></p>
              <h2 id="ai-title">24 labs, from your first model call to <em>your own GPT.</em></h2>
              <p className="uh-section-lead">Four stages, each lab a real build on your own machine with real models. The AI track is being crafted now; these are the labs it launches with.</p>
            </header>
          </div>
          <AiTrack />
        </section>

        {live.length > 0 && (
          <section id="labs" className="uh-section uh-labs" aria-labelledby="labs-title">
            <header className="uh-head">
              <p className="u-kicker">Labs</p>
              <h2 id="labs-title">Pick a lab. <em>Start in a minute.</em></h2>
              <p className="uh-section-lead">{live.length} labs in {categories} categories, from your first line of Python to a system under load. Every one runs in a real machine.</p>
            </header>
            <Directory labs={live} link={labLink} />
          </section>
        )}

        <section className="uh-final" aria-labelledby="final-title">
          <figure className="uh-final-print">
            <div className="uh-frame"><img src="/ukiyo/labs/python-basics.webp" alt="" /></div>
            <figcaption className="u-print-credit">Utagawa Hiroshige, Nihonbashi: Morning View, about 1833. Every journey on the Tōkaidō road began here.</figcaption>
          </figure>
          <div className="uh-final-text">
            <p className="u-kicker">Begin</p>
            <h2 id="final-title">Your machine is ready <em>when you are.</em></h2>
            <p>Sign up, pick a goal, and you are writing code on a real machine within a minute.</p>
            {user ? (
              <Link className="h-btn h-btn-primary" to="/labs">Continue learning →</Link>
            ) : (
              <Link className="h-btn h-btn-primary" to="/login?signup=1">Start your first lab →</Link>
            )}
          </div>
        </section>

        <section id="faq" className="uh-section" aria-labelledby="faq-title">
          <div className="h-faq-wrap">
            <div className="h-faq-intro">
              <p className="u-kicker">FAQs</p>
              <h2 id="faq-title">Questions, <em>answered.</em></h2>
              <p className="h-faq-lead">Everything about how a lab works, what it costs and what happens to your code. Still curious? Write to <a href={`mailto:${SITE.contactEmail}`}>{SITE.contactEmail}</a>.</p>
              <p className="h-faq-more"><Link to="/faq">All questions →</Link></p>
            </div>
            <HomeFaq />
          </div>
        </section>
      </main>

      <footer className="home-footer">
        <div className="home-footer-brand">
          <Logo />
          <span className="muted small-text">Hands-on AI labs, plus system design, languages, databases and DevOps.</span>
        </div>
        <SiteLinks faq={false} />
        <Copyright />
      </footer>
    </div>
  );
}
