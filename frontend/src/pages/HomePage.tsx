import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type CatalogLab } from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import { Copyright, SiteLinks } from "../components/SiteFooter";
import HeroTour from "../components/HeroTour";
import { AiTrack, HomeFaq, InsideLab } from "../components/HomeSections";
import { SITE } from "../site";
import { useTheme } from "../theme";

const TRACKS: { id: string; title: string; blurb: string }[] = [
  { id: "languages", title: "Programming languages", blurb: "Python, Java, Go, JavaScript, SQL" },
  { id: "frameworks", title: "Frameworks", blurb: "FastAPI, Spring Boot, Express" },
  { id: "databases", title: "Databases", blurb: "Postgres, Redis, real incidents" },
  { id: "devops", title: "DevOps", blurb: "Linux, Git, Docker, Kubernetes" },
  { id: "system-design", title: "System design", blurb: "Build it, then load test it" },
  { id: "interview", title: "Interview prep", blurb: "Traps, bugs and drills" },
];

const LIVE_SHOWN = 6; // lab titles listed under the tracks; the rest become "and N more"
// The "pick a lab" grid: these labs, in this order (any that are not live are skipped), then the
// coming-soon cards, which are not links.
const FEATURED = [
  "express-api", "fastapi-first-api", "go-basics",
  "java-basics", "spring-boot-first-api", "javascript-inside-out",
  "python-basics", "sql-from-zero", "postgres-indexing-incident",
  "redis-in-practice", "linux-on-call", "git-without-fear",
  "postgres-transactions-and-locks",
];
const COMING_SOON = [
  { id: "redis-in-practice", title: "Redis in practice", track: "Databases", cover: "/covers/redis-in-practice.svg" },
  { id: "git-without-fear", title: "Git without fear", track: "DevOps", cover: "/covers/git-without-fear.svg" },
  { id: "docker-start-to-ship", title: "Docker: start to ship", track: "DevOps", cover: "/covers/docker-start-to-ship.svg" },
  { id: "kubernetes-from-zero", title: "Kubernetes from zero", track: "DevOps", cover: "/covers/kubernetes-from-zero.svg" },
  { id: "linux-on-call", title: "Linux on call", track: "DevOps", cover: "/covers/linux-on-call.svg" },
];

// Real technology logos (devicon, MIT: /logos/LICENSE-devicon) for the moving strip.
const STRIP = ["python", "java", "go", "javascript", "typescript", "postgresql", "redis", "docker", "kubernetes", "spring", "fastapi", "nodejs", "git", "linux"];

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
        <span>{TRACKS.find((t) => t.id === lab.track)?.title ?? lab.track}</span>
      </div>
    </Link>
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

  const cta = user ? (
    <Link className="h-btn h-btn-primary" to="/labs">Continue learning →</Link>
  ) : (
    <Link className="h-btn h-btn-primary" to="/login?signup=1">Start free →</Link>
  );
  const live = catalog ?? [];
  const labLink = (lab: CatalogLab) => (user ? `/courses/${lab.id}` : "/login?signup=1");

  return (
    <div className="home">
      <header className="home-header">
        <Logo to="/" />
        <nav aria-label="Main" className="home-nav">
          <a href="#inside">Inside a lab</a>
          <a href="#ai">AI labs</a>
          <a href="#labs">Labs</a>
          <Link to="/library">Library</Link>
          <a href="#faq">FAQs</a>
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
              {catalog === null ? "Labs are live" : `AI track launching · ${live.length} lab${live.length === 1 ? "" : "s"} live now`}
            </p>
            <h1 id="hero-title">
              Learn AI by <span className="h-red-word">building<svg viewBox="0 0 200 16" preserveAspectRatio="none" aria-hidden="true"><path d="M3 11 C 50 3, 120 3, 197 9" /></svg></span> it, not <span className="h-strike">watching</span>.
            </h1>
            <p className="hero-sub">Hands-on AI labs on your own machine in the browser: call real models, build RAG search and agents, write evals, with a guide checking every step. And the engineering around them: system design, languages, databases and DevOps.</p>
            <div className="hero-cta">
              {cta}
              <a className="h-btn h-btn-ghost" href="#inside">See inside a lab</a>
            </div>
          </div>
          <HeroTour />
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
          <div><strong>24</strong><span>AI labs on the way</span></div>
        </section>

        <section id="inside" className="h-section" aria-labelledby="inside-title">
          <p className="h-kicker">Inside a lab</p>
          <h2 id="inside-title">Not exercises. <span className="h-yellow">Real systems.</span></h2>
          <InsideLab />
        </section>

        <section id="ai" className="h-section h-ai-section" aria-labelledby="ai-title">
          <p className="h-kicker">AI labs <span className="h-launch">Launching</span></p>
          <h2 id="ai-title">24 labs, from your first model call to <span className="h-yellow">your own GPT.</span></h2>
          <p className="h-section-lead">Four stages, each lab a real build on your own machine with real models. The AI track is being crafted now; these are the labs it launches with.</p>
          <AiTrack />
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
          <p className="h-kicker">Also on LabBox</p>
          <h2 id="tracks-title">The engineering around AI. <span className="h-soft">Real tools in every track.</span></h2>
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
        <section id="faq" className="h-section" aria-labelledby="faq-title">
          <div className="h-faq-wrap">
            <div className="h-faq-intro">
              <p className="h-kicker">FAQs</p>
              <h2 id="faq-title">Questions, answered.</h2>
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
