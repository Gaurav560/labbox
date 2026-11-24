import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, ApiError, library, libraryImage, type CatalogLab, type LibraryItem, type LibraryKind } from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import ProfileMenu from "../components/ProfileMenu";
import { Copyright, SiteLinks } from "../components/SiteFooter";
import ThemeButton from "../components/ThemeButton";
import { labTone } from "../brand";

// The Library (owner, 24 November): books, research papers and tech blogs worth reading next to the labs. Public, so
// it can be shared and found by search engines; every pick says why it matters and which lab lets you practise it.
// Admins keep the list current from Admin > Library.

export const LIBRARY_TABS: [LibraryKind, string, string][] = [
  ["book", "Books", "The books our courses are built on: from first principles to how real systems work."],
  ["paper", "Research papers", "The papers behind the ideas you build in the labs, most of them free to read."],
  ["blog", "Tech blogs", "Engineers and companies who explain how real systems are built, updated every week."],
];

/** The three sections as big tiles: a colour, an icon, a line that says what is inside. */
const SECTION: Record<LibraryKind, { tone: string; line: string }> = {
  book: { tone: "#e8a33d", line: "From first principles to real systems" },
  paper: { tone: "#8b7cff", line: "The ideas behind every lab, at the source" },
  blog: { tone: "#2bb3a0", line: "How real teams build, every week" },
};

function SectionIcon({ kind }: { kind: LibraryKind }) {
  const common = { width: 22, height: 22, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8,
    strokeLinecap: "round" as const, strokeLinejoin: "round" as const, "aria-hidden": true };
  if (kind === "book") return (
    <svg {...common}><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z" /><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5" /><path d="M8 7h8M8 11h6" /></svg>
  );
  if (kind === "paper") return (
    <svg {...common}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6" /><path d="M8 13h8M8 17h8M8 9h2" /></svg>
  );
  return (
    <svg {...common}><path d="M4 11a9 9 0 0 1 9 9" /><path d="M4 4a16 16 0 0 1 16 16" /><circle cx="5" cy="19" r="1.4" /></svg>
  );
}

/** The newest change to any item of a section, as "24 Nov 2026" (the backend stores UTC without a zone). Moving or removing
    an item does not count. */
function lastUpdated(items: LibraryItem[], fullYear = false): string {
  const newest = Math.max(0, ...items.map((i) => Date.parse(/[zZ]|[+-]\d\d:?\d\d$/.test(i.updated_at) ? i.updated_at : `${i.updated_at}Z`) || 0));
  if (!newest) return "";
  const date = new Date(newest);
  const year = !fullYear && date.getFullYear() === new Date().getFullYear() ? undefined : "numeric";  // "24 Nov", or "24 Nov 2025" for an older year
  return date.toLocaleDateString("en-GB", { day: "numeric", month: "short", year });
}

function SectionTile({ kind, label, items, active, onPick }: {
  kind: LibraryKind; label: string; items: LibraryItem[]; active: boolean; onPick: () => void;
}) {
  const { tone: t, line } = SECTION[kind];
  const shots = items.filter((i) => i.image).slice(0, 10);
  const updated = lastUpdated(items);
  return (
    <button className={`lib-tile is-${kind}`} aria-current={active ? "page" : undefined} onClick={onPick}
      style={{ "--t": t } as CSSProperties}>
      <span className="lib-tile-wall" aria-hidden="true">
        {shots.map((i) => <img key={i.id} src={libraryImage(i.image)} alt="" loading="eager" />)}
      </span>
      <span className="lib-tile-head">
        <span className="lib-tile-icon"><SectionIcon kind={kind} /></span>
        <span className="lib-tile-kicker">{items.length} hand-picked</span>
      </span>
      <span className="lib-tile-text">
        <span className="lib-tile-name">{label}</span>
        <span className="lib-tile-line">{line}</span>
      </span>
      <span className="lib-tile-foot">
        {updated && <span className="lib-tile-updated"><span aria-hidden="true">↻</span> Last updated {updated}</span>}
      </span>
    </button>
  );
}

const SINGULAR: Record<LibraryKind, string> = { book: "book", paper: "paper", blog: "blog" };

/** One colour per topic, shared by covers, monograms and badges. */
const TOPIC_TONES: Record<string, string> = {
  "AI": "#6d5dfc",
  "RAG and search": "#139e8a",
  "Databases": "#2f74d0",
  "Systems": "#d9822b",
  "Programming": "#3f9b4f",
  "DevOps": "#d4537e",
};
function tone(topic: string): string {
  if (TOPIC_TONES[topic]) return TOPIC_TONES[topic];
  let h = 0;
  for (const ch of topic) h = (h * 31 + ch.charCodeAt(0)) % 360;
  return `hsl(${h} 45% 45%)`;
}

const levelLabel = (l: string) => (l ? `${l[0].toUpperCase()}${l.slice(1)}` : "");

function Badges({ item, topic = false }: { item: LibraryItem; topic?: boolean }) {
  if (!item.level && !(topic && item.topic)) return null;
  return (
    <div className="lib-badges">
      {item.level && <span className="lib-badge">{levelLabel(item.level)}</span>}
      {topic && item.topic && <span className="lib-badge lib-badge-topic" style={{ "--t": tone(item.topic) } as CSSProperties}>{item.topic}</span>}
    </div>
  );
}

/** On a card: one small chip in the lab's colour. The chapter shows on hover (owner, 24 November: on every card, Start here too). */
function PracticeChip({ item, labs, signedIn }: { item: LibraryItem; labs: Map<string, CatalogLab>; signedIn: boolean }) {
  const lab = item.lab ? labs.get(item.lab) : undefined;
  if (!lab) return null;
  const where = `Practise it hands-on in ${lab.title}${item.practice ? `, ${item.practice}` : ""}`;
  return (
    <Link className="lib-chip" to={signedIn ? `/courses/${lab.id}` : "/login?signup=1"} title={where} aria-label={where}
      style={{ "--lt": labTone(lab.id) } as CSSProperties}>
      <span className="lib-chip-play" aria-hidden="true">▶</span>
      <span className="lib-chip-name">{lab.title}</span>
    </Link>
  );
}

/** The item's real picture (a book's cover, a paper's first page, a view of a blog), stored with LabBox. */
function Picture({ item, className }: { item: LibraryItem; className: string }) {
  const alt = item.kind === "book" ? `Cover of ${item.title}` : item.kind === "paper" ? `First page of ${item.title}` : `The ${item.title} home page`;
  return <img className={className} src={libraryImage(item.image)} alt={alt} loading="eager" decoding="async" />;
}

/** A book cover drawn from the data, for items that have no picture yet. */
function Cover({ item, big = false }: { item: LibraryItem; big?: boolean }) {
  if (item.image) return <Picture item={item} className={`lib-cover-img ${big ? "is-big" : ""}`} />;
  return (
    <div className={`lib-cover ${big ? "is-big" : ""}`} style={{ "--t": tone(item.topic) } as CSSProperties} aria-hidden="true">
      <span className="lib-cover-kicker">{item.topic || "Book"}</span>
      <span className="lib-cover-title">{item.title}</span>
      <span className="lib-cover-author">{item.authors}</span>
    </div>
  );
}

function Monogram({ item }: { item: LibraryItem }) {
  const letters = item.title.replace(/[^A-Za-z0-9 ]/g, "").split(" ").filter(Boolean).slice(0, 2).map((w) => w[0]).join("").toUpperCase();
  return <div className="lib-mono" style={{ "--t": tone(item.topic) } as CSSProperties} aria-hidden="true">{letters}</div>;
}

function Featured({ item, labs, signedIn }: { item: LibraryItem; labs: Map<string, CatalogLab>; signedIn: boolean }) {
  return (
    <article className="lib-featured" aria-label={`Start here: ${item.title}`}>
      <div className={`lib-featured-art is-${item.kind}`}>
        {item.kind === "book" ? <Cover item={item} big /> : item.image ? <Picture item={item} className={`lib-shot is-${item.kind}`} /> :
          item.kind === "blog" ? <Monogram item={item} /> : (
          <div className="lib-paper-art" style={{ "--t": tone(item.topic) } as CSSProperties} aria-hidden="true">
            <span>{item.year}</span>
          </div>
        )}
      </div>
      <div className="lib-featured-text">
        <span className="lib-start">Start here</span>
        <h2>{item.url ? <a className="lib-stretch" href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a> : item.title}</h2>
        <p className="lib-by">{[item.authors, item.year].filter(Boolean).join(" · ")}</p>
        {item.kind === "paper" && item.note && <p className="lib-why">{item.note}</p>}
        <Badges item={item} topic />
        <div className="lib-actions">
          <PracticeChip item={item} labs={labs} signedIn={signedIn} />
        </div>
      </div>
    </article>
  );
}

function BookCard({ item, labs, signedIn }: { item: LibraryItem; labs: Map<string, CatalogLab>; signedIn: boolean }) {
  return (
    <li className="lib-book" aria-label={item.title}>
      {/* The cover already shows the title and the authors (owner, 24 November), so the card does not repeat them. */}
      {item.url ? (
        <a className="lib-cover-link" href={item.url} target="_blank" rel="noopener noreferrer" aria-label={`${item.title}, by ${item.authors}`}>
          <Cover item={item} />
        </a>
      ) : <Cover item={item} />}
      <div className="lib-card-body">
        <Badges item={item} />
        <PracticeChip item={item} labs={labs} signedIn={signedIn} />
      </div>
    </li>
  );
}

function PaperRow({ item, labs, signedIn }: { item: LibraryItem; labs: Map<string, CatalogLab>; signedIn: boolean }) {
  return (
    <li className="lib-paper" style={{ "--t": tone(item.topic) } as CSSProperties}>
      {item.image && <Picture item={item} className="lib-shot is-paper" />}
      <div className="lib-card-body">
        <p className="lib-year">{item.year ?? ""}</p>
        <h3>{item.url ? <a className="lib-stretch" href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a> : item.title}</h3>
        <p className="lib-by">{item.authors}</p>
        <p className="lib-why">{item.note}</p>
        <Badges item={item} />
        <div className="lib-actions">
          <PracticeChip item={item} labs={labs} signedIn={signedIn} />
        </div>
      </div>
    </li>
  );
}

function BlogCard({ item, labs, signedIn }: { item: LibraryItem; labs: Map<string, CatalogLab>; signedIn: boolean }) {
  return (
    <li className="lib-blog">
      {item.image && <Picture item={item} className="lib-shot is-blog" />}
      <div className="lib-blog-head">
        {!item.image && <Monogram item={item} />}
        <div>
          <h3>{item.url ? <a className="lib-stretch" href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a> : item.title}</h3>
          <p className="lib-by">{item.authors}</p>
        </div>
      </div>
      <Badges item={item} />
      <div className="lib-actions">
        <PracticeChip item={item} labs={labs} signedIn={signedIn} />
      </div>
    </li>
  );
}

export default function LibraryPage() {
  const { user } = useAuth();
  const signedIn = !!user;
  const [params, setParams] = useSearchParams();
  const kind = (LIBRARY_TABS.find(([k]) => k === params.get("tab"))?.[0] ?? "book") as LibraryKind;
  const [items, setItems] = useState<LibraryItem[] | null>(null);
  const [labs, setLabs] = useState<Map<string, CatalogLab>>(new Map());
  const [error, setError] = useState<string | null>(null);
  const [topic, setTopic] = useState("");

  useEffect(() => {
    library.list().then(setItems).catch((e) => setError(e instanceof ApiError ? e.message : String(e)));
    api.catalog().then((all) => setLabs(new Map(all.map((l) => [l.id, l])))).catch(() => setLabs(new Map()));
  }, []);
  useEffect(() => { document.title = "Premium reads: books, papers and blogs | LabBox by Telusko"; }, []);

  const ofKind = useMemo(() => (items ?? []).filter((i) => i.kind === kind), [items, kind]);
  const topics = useMemo(() => [...new Set(ofKind.map((i) => i.topic).filter(Boolean))], [ofKind]);
  const filtered = topic && topics.includes(topic) ? ofKind.filter((i) => i.topic === topic) : ofKind;
  const featured = topic ? undefined : ofKind.find((i) => i.featured);
  const rest = filtered.filter((i) => i !== featured);
  const [, title, intro] = LIBRARY_TABS.find(([k]) => k === kind)!;

  return (
    <div className="lib-page">
      <header className="topbar">
        <Logo to="/" />
        <span className="spacer" />
        <ThemeButton />
        {signedIn ? (
          <>
            <Link className="btn btn-small btn-ghost" to="/labs">Labs</Link>
            {user?.is_admin && <Link className="btn btn-small btn-ghost" to="/admin?tab=library">Edit the library</Link>}
            <ProfileMenu username={user?.username ?? ""} />
          </>
        ) : (
          <>
            <Link className="btn btn-small btn-ghost" to="/login">Log in</Link>
            <Link className="lib-btn lib-btn-primary lib-btn-sm" to="/login?signup=1">Start free</Link>
          </>
        )}
      </header>

      <main className="lib-main">
        <section className="lib-hero" aria-labelledby="lib-title">
          <div className="lib-hero-text">
          <span className="lib-kicker">Hand-picked by the LabBox team</span>
          <h1 id="lib-title">Premium reads.</h1>
          <p className="lib-sub">
            The books, research papers and engineering blogs behind every LabBox course, hand-picked, with the lab
            that lets you build each idea yourself.
          </p>
          </div>
          {items && items.length > 0 && <p className="lib-updated">Last updated {lastUpdated(items, true)}</p>}
        </section>

        <nav className="lib-tiles" aria-label="Library sections">
          {LIBRARY_TABS.map(([k, label]) => (
            <SectionTile key={k} kind={k} label={label} items={(items ?? []).filter((i) => i.kind === k)} active={k === kind}
              onPick={() => { setTopic(""); setParams({ tab: k }); }} />
          ))}
        </nav>
        <p className="lib-intro">{intro}</p>

        {error && <p className="adm-error" role="alert">{error}</p>}
        {!items && !error && <p className="muted">Loading...</p>}

        {featured && <Featured item={featured} labs={labs} signedIn={signedIn} />}

        {topics.length > 1 && (
          <div className="lib-topics" role="group" aria-label={`Filter ${title.toLowerCase()} by topic`}>
            <button aria-pressed={!topic} onClick={() => setTopic("")}>All {title.toLowerCase()}<span>{ofKind.length}</span></button>
            {topics.map((t) => (
              <button key={t} aria-pressed={topic === t} onClick={() => setTopic(t)} style={{ "--t": tone(t) } as CSSProperties}>
                <i aria-hidden="true" />{t}<span>{ofKind.filter((i) => i.topic === t).length}</span>
              </button>
            ))}
          </div>
        )}

        {items && filtered.length === 0 && <p className="muted">No {SINGULAR[kind]}s here yet.</p>}
        {kind === "book" && (
          <ul className="lib-books" aria-label={title}>{rest.map((i) => <BookCard key={i.id} item={i} labs={labs} signedIn={signedIn} />)}</ul>
        )}
        {kind === "paper" && (
          <ul className="lib-papers" aria-label={title}>{rest.map((i) => <PaperRow key={i.id} item={i} labs={labs} signedIn={signedIn} />)}</ul>
        )}
        {kind === "blog" && (
          <ul className="lib-blogs" aria-label={title}>{rest.map((i) => <BlogCard key={i.id} item={i} labs={labs} signedIn={signedIn} />)}</ul>
        )}

        <section className="lib-cta" aria-label="Learn by building">
          <h2>Reading is half of it.</h2>
          <p>In LabBox you build these ideas yourself, on a real machine in your browser, with a check that tells you when it works.</p>
          {signedIn
            ? <Link className="lib-btn lib-btn-primary" to="/labs">Continue learning →</Link>
            : <Link className="lib-btn lib-btn-primary" to="/login?signup=1">Start free →</Link>}
        </section>
      </main>
      <footer className="lib-footer">
        <SiteLinks />
        <Copyright />
      </footer>
    </div>
  );
}
