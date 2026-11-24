/*
 * Eight ways to show the lab categories on the home page, one after another, for the owner to pick one
 * (25 November: "I want to see all one by one"). Real catalog data, both themes. Not linked from the app.
 */
import { useEffect, useMemo, useState, type CSSProperties, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { api, type CatalogLab } from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import ThemeButton from "../components/ThemeButton";
import { TRACK_INK, TrackArt } from "../components/UkiyoArt";
import { byCategory, TRACK_LABEL } from "../components/UkiyoDirectory";

type Group = { id: string; labs: CatalogLab[] };
type Props = { groups: Group[]; to: string };

const ink = (id: string) => ({ "--ink": TRACK_INK[id] ?? "var(--text)" }) as CSSProperties;
const name = (id: string) => TRACK_LABEL[id] ?? id;
const count = (g: Group) => `${g.labs.length} lab${g.labs.length === 1 ? "" : "s"}`;
const titles = (g: Group, n = 3) => g.labs.slice(0, n).map((l) => l.title).join(" · ") + (g.labs.length > n ? " and more" : "");

/** 1. The card grid on the home page now. */
function CardGrid({ groups, to }: Props) {
  return (
    <ul className="uh-cats">
      {groups.map((g) => (
        <li key={g.id} style={ink(g.id)}>
          <Link to={to} className="uh-cat-card">
            <span className="uh-cat-art" aria-hidden="true"><TrackArt track={g.id} /></span>
            <span className="uh-cat-body">
              <span className="uh-cat-head"><strong>{name(g.id)}</strong><span className="uh-cat-count">{count(g)}</span></span>
              <span className="uh-cat-labs">{titles(g)}</span>
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

/** 2. A folding screen: six tall panels; the one under the pointer opens wider and lists its labs. */
function FoldingScreen({ groups, to }: Props) {
  return (
    <div className="ul-screen">
      {groups.map((g, i) => (
        <Link key={g.id} to={to} className="ul-panel" style={ink(g.id)}>
          <span className="ul-panel-art" aria-hidden="true"><TrackArt track={g.id} /></span>
          <span className="ul-panel-shade" aria-hidden="true" />
          <span className="ul-panel-n">{String(i + 1).padStart(2, "0")}</span>
          <span className="ul-panel-name">{name(g.id)}</span>
          <span className="ul-panel-open">
            <strong>{name(g.id)}</strong>
            <span className="ul-panel-count">{count(g)}</span>
            <ul>{g.labs.slice(0, 5).map((l) => <li key={l.id}>{l.title}</li>)}</ul>
          </span>
        </Link>
      ))}
    </div>
  );
}

/** 3. An editorial index: big numbered names in ruled rows; the print of the row under the pointer shows beside. */
function EditorialIndex({ groups, to }: Props) {
  const [on, setOn] = useState(groups[0]?.id ?? "");
  return (
    <div className="ul-index">
      <ol>
        {groups.map((g, i) => (
          <li key={g.id} style={ink(g.id)} className={on === g.id ? "is-on" : ""} onMouseEnter={() => setOn(g.id)} onFocus={() => setOn(g.id)}>
            <Link to={to}>
              <span className="ul-index-n">{String(i + 1).padStart(2, "0")}</span>
              <span className="ul-index-name">{name(g.id)}</span>
              <span className="ul-index-labs">{titles(g, 4)}</span>
              <span className="ul-index-count">{count(g)}</span>
            </Link>
          </li>
        ))}
      </ol>
      <figure className="ul-index-print" aria-hidden="true">
        <div className="uh-frame">{groups.map((g) => <div key={g.id} className={on === g.id ? "is-on" : ""}><TrackArt track={g.id} /></div>)}</div>
        <figcaption className="u-print-credit">{name(on)}</figcaption>
      </figure>
    </div>
  );
}

/** 4. A feature and a list: AI as one large print with all its labs; the other categories as compact rows. */
function FeatureList({ groups, to }: Props) {
  const [first, ...rest] = groups;
  if (!first) return null;
  return (
    <div className="ul-feature">
      <Link to={to} className="ul-feature-main" style={ink(first.id)}>
        <span className="ul-feature-art" aria-hidden="true"><TrackArt track={first.id} /></span>
        <span className="ul-feature-body">
          <span className="u-kicker">The headline track</span>
          <strong>{name(first.id)}</strong>
          <span className="ul-feature-labs">{first.labs.map((l) => l.title).join(" · ")}</span>
        </span>
      </Link>
      <ul className="ul-feature-list">
        {rest.map((g) => (
          <li key={g.id} style={ink(g.id)}>
            <Link to={to}>
              <span className="ul-thumb" aria-hidden="true"><TrackArt track={g.id} /></span>
              <span className="ul-feature-row">
                <strong>{name(g.id)}</strong>
                <span>{titles(g, 2)}</span>
              </span>
              <span className="ul-feature-count">{count(g)}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** 5. A gallery wall: framed prints in a row that scrolls sideways, with a caption under each. */
function GalleryWall({ groups, to }: Props) {
  return (
    <div className="ul-gallery">
      {groups.map((g) => (
        <Link key={g.id} to={to} className="ul-gallery-item" style={ink(g.id)}>
          <span className="uh-frame"><TrackArt track={g.id} /></span>
          <span className="ul-gallery-cap"><strong>{name(g.id)}</strong> <span>{count(g)}</span></span>
          <span className="ul-gallery-labs">{titles(g)}</span>
        </Link>
      ))}
    </div>
  );
}

/** 6. A hand scroll (emakimono): the six prints joined into one long picture, each named with a red seal. */
function HandScroll({ groups, to }: Props) {
  return (
    <div className="ul-scroll">
      <div className="ul-scroll-roll">
        {groups.map((g) => (
          <Link key={g.id} to={to} className="ul-scroll-scene">
            <span className="ul-scroll-art" aria-hidden="true"><TrackArt track={g.id} /></span>
            <span className="ul-scroll-label"><span className="ul-seal">{name(g.id)}</span><small>{count(g)}</small></span>
          </Link>
        ))}
      </div>
    </div>
  );
}

/** 7. Tabs: the category names as tabs; the chosen one shows its print large and every lab beside it. */
function Tabs({ groups, to }: Props) {
  const [on, setOn] = useState(groups[0]?.id ?? "");
  const g = groups.find((x) => x.id === on) ?? groups[0];
  if (!g) return null;
  return (
    <div className="ul-tabs">
      <div className="ul-tablist" role="tablist" aria-label="Categories">
        {groups.map((x) => (
          <button key={x.id} type="button" role="tab" aria-selected={x.id === on} style={ink(x.id)} onClick={() => setOn(x.id)}>
            {name(x.id)} <small>{x.labs.length}</small>
          </button>
        ))}
      </div>
      <div className="ul-tabpanel" role="tabpanel" style={ink(g.id)}>
        <div className="uh-frame"><TrackArt track={g.id} /></div>
        <div>
          <h3>{name(g.id)}</h3>
          <ol>{g.labs.map((l) => <li key={l.id}><Link to={to}>{l.title}</Link><span>{l.subtitle}</span></li>)}</ol>
        </div>
      </div>
    </div>
  );
}

/** 8. An uneven grid (bento): AI large, Languages wide, the rest smaller; names over the prints. */
function Bento({ groups, to }: Props) {
  return (
    <div className="ul-bento">
      {groups.map((g, i) => (
        <Link key={g.id} to={to} className={`ul-bento-tile ul-bento-${i}`} style={ink(g.id)}>
          <span className="ul-bento-art" aria-hidden="true"><TrackArt track={g.id} /></span>
          <span className="ul-bento-text">
            <strong>{name(g.id)}</strong>
            <span>{count(g)}{i < 2 ? ` · ${titles(g)}` : ""}</span>
          </span>
        </Link>
      ))}
    </div>
  );
}

const LAYOUTS: { title: string; note: string; View: (p: Props) => ReactNode }[] = [
  { title: "Card grid", note: "What the home page shows now: a picture on top, the name, the count and three titles below.", View: CardGrid },
  { title: "Folding screen", note: "Six tall panels like a Japanese byobu. Point at one: it opens wider and lists its labs.", View: FoldingScreen },
  { title: "Editorial index", note: "A numbered list of big serif names. The print of the row you point at shows beside it.", View: EditorialIndex },
  { title: "Feature and list", note: "AI as the headline, one large print with all its labs; the other categories as compact rows.", View: FeatureList },
  { title: "Gallery wall", note: "Framed prints in one row that scrolls sideways, each with a caption, like walking past a gallery wall.", View: GalleryWall },
  { title: "Hand scroll", note: "The six prints joined into one long picture (an emakimono); each category named with a red seal.", View: HandScroll },
  { title: "Tabs", note: "The category names as tabs. Pick one: its print shows large, with every lab beside it.", View: Tabs },
  { title: "Uneven grid", note: "A bento grid: AI large, Languages wide, the rest smaller, the names written over the prints.", View: Bento },
];

export default function UkiyoLayoutsPage() {
  const { user } = useAuth();
  const [catalog, setCatalog] = useState<CatalogLab[]>([]);
  useEffect(() => {
    document.title = "Category layouts | LabBox by Telusko";
    api.catalog().then(setCatalog).catch(() => setCatalog([]));
  }, []);
  const groups = useMemo(() => byCategory(catalog).filter((g) => g.labs.length), [catalog]);
  const to = user ? "/labs" : "/login?signup=1";
  return (
    <div className="ul-page">
      <header className="ul-top">
        <Logo to="/" />
        <nav aria-label="Layouts">
          {LAYOUTS.map((l, i) => <a key={l.title} href={`#layout-${i + 1}`}>{i + 1}. {l.title}</a>)}
        </nav>
        <ThemeButton />
      </header>
      <main className="ul-main">
        <h1>Eight ways to show the labs</h1>
        <p className="uh-section-lead">The same {catalog.length} labs in {groups.length} categories, laid out eight ways. Pick a number for the home page.</p>
        {LAYOUTS.map(({ title, note, View }, i) => (
          <section key={title} id={`layout-${i + 1}`} className="ul-section" aria-labelledby={`layout-${i + 1}-title`}>
            <p className="u-kicker">Layout {i + 1} of {LAYOUTS.length}</p>
            <h2 id={`layout-${i + 1}-title`}>{i + 1}. {title}</h2>
            <p className="ul-note">{note}</p>
            {groups.length ? <View groups={groups} to={to} /> : <p className="muted">Loading the labs...</p>}
          </section>
        ))}
      </main>
    </div>
  );
}
