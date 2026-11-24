import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import { api, type CatalogLab } from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import { Copyright, SiteLinks } from "../components/SiteFooter";
import { HomeFaq } from "../components/HomeSections";
import { byCategory, TRACK_LABEL } from "../components/UkiyoDirectory";
import { TRACK_INK, TrackArt } from "../components/UkiyoArt";
import { SITE } from "../site";
import { useTheme } from "../theme";

/*
 * The public home page in the Ukiyo design (owner, 25 November: "redesign the home page; the inside looks cool").
 * One language with the inside: a framed woodblock print in the hero, fine rules instead of cards, serif headings,
 * one red button per screen, and the dashboard's own directory of labs.
 */

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
  const groups = useMemo(() => byCategory(live).filter((g) => g.labs.length), [live]);
  const cta = user ? (
    <Link className="h-btn h-btn-primary" to="/labs">Continue learning →</Link>
  ) : (
    <Link className="h-btn h-btn-primary" to="/login?signup=1">Start free →</Link>
  );
  const allLabs = user ? "/labs" : "/login?signup=1";

  return (
    <div className="home u-home">
      <header className="home-header">
        <Logo to="/" />
        <nav aria-label="Main" className="home-nav">
          <a href="#labs">AI labs</a>
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
            </div>
          </div>
          {/* Red Fuji as the hero's background, fading into the paper behind the words (owner, 25 November) */}
          <div className="uh-hero-bg" role="img" aria-label="Woodblock print: Katsushika Hokusai, Fine Wind, Clear Morning (Red Fuji), about 1831" />
          <p className="u-print-credit uh-hero-credit">Katsushika Hokusai, Fine Wind, Clear Morning, about 1831</p>
        </section>



        {live.length > 0 && (
          <section id="labs" className="uh-section uh-labs" aria-labelledby="labs-title">
            <header className="uh-head">
              <p className="u-kicker">Labs</p>
              <h2 id="labs-title">Pick a lab. <em>Start in a minute.</em></h2>
              <p className="uh-section-lead">{live.length} labs in {groups.length} categories, from your first line of Python to a system under load. Every one runs in a real machine.</p>
            </header>
            {/* A folding screen: one tall panel per category; the one under the pointer opens wider and lists its labs
                (owner, 25 November, picked from eight layouts) */}
            <div className="uh-screen">
              {groups.map((g) => {
                const label = TRACK_LABEL[g.id] ?? g.id;
                const n = `${g.labs.length} lab${g.labs.length === 1 ? "" : "s"}`;
                return (
                  <Link key={g.id} to={allLabs} className="uh-panel" aria-label={`${label}: ${n}`}
                    style={{ "--ink": TRACK_INK[g.id] ?? "var(--text)" } as CSSProperties}>
                    <span className="uh-panel-art" aria-hidden="true"><TrackArt track={g.id} /></span>
                    <span className="uh-panel-shade" aria-hidden="true" />
                    <span className="uh-panel-name" aria-hidden="true">{label}</span>
                    <span className="uh-panel-open" aria-hidden="true">
                      <strong>{label}</strong>
                      <span className="uh-panel-count">{n}</span>
                      <ul>{g.labs.slice(0, 5).map((l) => <li key={l.id}>{l.title}</li>)}</ul>
                    </span>
                  </Link>
                );
              })}
            </div>
            <p className="uh-all"><Link to={allLabs}>See all {live.length} labs →</Link></p>
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
