import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import { api, type CatalogLab } from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import { Copyright, SiteLinks } from "../components/SiteFooter";
import HomeAiLabs from "../components/HomeAiLabs";
import { HomeFaq } from "../components/HomeSections";
import HomeCertificate from "../components/HomeCertificate";
import UkiyoMachine from "../components/UkiyoMachine";
import { byCategory, TRACK_LABEL } from "../components/UkiyoDirectory";
import { TRACK_INK, TrackArt } from "../components/UkiyoArt";
import { SITE } from "../site";
import { useTheme } from "../theme";

/*
 * The public home page in the Ukiyo design (owner, 25 November: "redesign the home page; the inside looks cool").
 * One language with the inside: a framed woodblock print in the hero, fine rules instead of cards, serif headings,
 * one red button per screen, and the dashboard's own directory of labs.
 */

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
          <a href="#ai">AI labs</a>{/* jumps to the AI section (owner, 27 November) */}
          <Link to="/library">Premium Reads</Link>
          <Link to="/pricing">Pricing</Link>
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
        {/* The hero (owner, 27 November): "The AI wave is here. Learn to ride it." beside the picture that says it, an
            engineer riding a wave of light toward the city (made for LabBox in woodblock style); no terminal over it. */}
        <section className="uh-hero is-print" aria-labelledby="hero-title">
          <div className="uh-hero-text">
            {/* Owner, 27 November: "fix this way of writing"; picked "ride the wave" (an invitation, not a threat; it matches
                the Forward Deployed Engineer picture of an engineer riding a wave). Ink and indigo, no red but the button. */}
            <h1 id="hero-title"><span className="uh-line">The AI wave is here.</span> <em className="uh-line">Learn to ride it.</em></h1>
            <p className="uh-lead">Build real AI apps in your browser. A lab machine with an editor, a terminal and real models is ready in about a minute.</p>
            <p className="uh-promise"><span>No videos to sit through.</span> <em>You learn by building.</em></p>
            <div className="uh-cta">{cta}</div>
          </div>
          {/* Half text, half picture (owner, 28 November: "use this image in the hero, flip the wave and boy, the
              photo fills the right side and melts into the page"): the engineer riding the wave of light, made for
              LabBox in woodblock style, mirrored so he stands on the right and looks toward the headline. */}
          <div className="uh-hero-print is-rider" aria-hidden="true">
            <img src="/ukiyo/heroes/wave-rider.webp" width={1200} height={800} alt="" />
          </div>
        </section>

        {/* AI labs first, with the Forward Deployed Engineer course in the spotlight (owner, 27 November) */}
        <div className="uh-ai">
          <HomeAiLabs
            labs={live}
            signedIn={!!user}
            thumb={(lab) => <img src={`/home/ai/${lab.id}.webp`} alt="" loading="lazy" />}
            spotArt={<>
              <img src="/home/fde-spotlight.webp" width={1800} height={872} alt="Woodblock print: Utagawa Hiroshige, View toward Kasumigaseki in Edo, about 1830. A wide street of white-walled mansions climbs toward red-lit trees, crowds and processions in the foreground." />
            </>}
            title={<>Build with real models. <em>Start with the job itself.</em></>}
            lead="Each AI lab is a real build on a lab machine in your browser: model calls, RAG search, agents and evals, through the LabBox gateway."
          />
        </div>

        <section id="machine" className="uh-section uh-machine" aria-labelledby="machine-title">
          <UkiyoMachine signedIn={!!user} />
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

        <section id="certificates" className="uh-section uh-certs" aria-labelledby="cert-title">
          <header className="uh-head">
            <p className="u-kicker">Certificates</p>
            <h2 id="cert-title">Finish a lab. <em>Share the proof.</em></h2>
            <p className="uh-section-lead">Every lab you finish gives you a certificate with its own link, made automatically. Post it on LinkedIn, X, WhatsApp or anywhere else.</p>
          </header>
          <HomeCertificate />
        </section>

        <section className="uh-final" aria-labelledby="final-title">
          <figure className="uh-final-print">
            <div className="uh-frame"><img src="/ukiyo/hira-evening-snow.webp" width={1200} height={607} alt="Woodblock print: Utagawa Hiroshige, Evening Snow on Mount Hira, about 1834" /></div>
            <figcaption className="u-print-credit">Utagawa Hiroshige, Evening Snow on Mount Hira, Eight Views of Omi, about 1834</figcaption>
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
