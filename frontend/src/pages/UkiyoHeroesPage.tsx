/*
 * Eight home page heroes to compare, one after another (owner, 25 November: "this image and this text look off ...
 * how many ways, new design, new images, new text, I want to see it"). Each has its own layout, picture and words.
 * All pictures are public domain woodblock prints. Not linked from the app.
 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import Logo from "../components/Logo";
import ThemeButton from "../components/ThemeButton";
import { TrackArt } from "../components/UkiyoArt";

const CTA = () => <Link className="h-btn h-btn-primary" to="/login?signup=1">Start free →</Link>;
const Credit = ({ children }: { children: string }) => <p className="u-print-credit">{children}</p>;

/** 1. Type only: a very large serif line on paper, a vermilion seal, and a strip of six prints beneath. */
function Hero1({ labs }: { labs: number }) {
  return (
    <div className="hx hx-1">
      <span className="hx1-seal" aria-hidden="true">学</span>
      <h1>Learn AI<br />by <em>building</em> it.</h1>
      <p className="hx-lead">{labs} hands-on labs on a real machine in your browser. No videos. A guide checks every step.</p>
      <CTA />
      <div className="hx1-strip" aria-hidden="true">
        {["langchain4j", "rust-basics", "langgraph", "linux-on-call", "python-basics", "rag-vector-databases"].map((l) => (
          <img key={l} src={`/ukiyo/labs/${l}.webp`} alt="" />
        ))}
      </div>
    </div>
  );
}

/** 2. Split with a tall print: words on the left, Hiroshige's Moon Pine framed on the right. */
function Hero2() {
  return (
    <div className="hx hx-2">
      <div>
        <p className="u-kicker">Real machines · Real models · Real code</p>
        <h1>Don't watch AI.<br /><em>Build it.</em></h1>
        <p className="hx-lead">Call real models, build RAG search and agents, and ship them, in labs that run on your own machine in the browser.</p>
        <CTA />
      </div>
      <figure>
        <div className="uh-frame"><img src="/ukiyo/heroes/moonpine.webp" alt="Woodblock print: Utagawa Hiroshige, Moon Pine at Ueno, 1857" /></div>
        <Credit>Utagawa Hiroshige, Moon Pine at Ueno, 1857</Credit>
      </figure>
    </div>
  );
}

/** 3. Full bleed: the Great Wave across the whole width, dark wash, the words in white at the bottom left. */
function Hero3() {
  return (
    <div className="hx hx-3">
      <div className="hx3-bg" aria-hidden="true" />
      <div className="hx3-text">
        <p className="u-kicker">LabBox</p>
        <h1>The wave is here.<br /><em>Learn to build on it.</em></h1>
        <p className="hx-lead">Hands-on AI labs: models, RAG, agents and evals, on a real machine, checked step by step.</p>
        <CTA />
      </div>
      <Credit>Katsushika Hokusai, The Great Wave off Kanagawa, about 1831</Credit>
    </div>
  );
}

/** 4. A triptych: three tall prints side by side, like a three-sheet print, with the words beneath. */
function Hero4() {
  return (
    <div className="hx hx-4">
      <div className="hx4-tri" aria-hidden="true">
        <img src="/ukiyo/heroes/kinryuzan.webp" alt="" />
        <img src="/ukiyo/heroes/shower.webp" alt="" />
        <img src="/ukiyo/plum-garden.webp" alt="" />
      </div>
      <div className="hx4-text">
        <h1>Read a little. Try it. <em>Get it checked.</em></h1>
        <p className="hx-lead">Every LabBox lesson is three moves on a real machine, until AI stops being magic and becomes something you build.</p>
        <CTA />
      </div>
      <Credit>Utagawa Hiroshige, One Hundred Famous Views of Edo, 1856 to 1858</Credit>
    </div>
  );
}

/** 5. The seal: a large vermilion hanko stamped beside the words on plain paper. No picture at all. */
function Hero5({ labs }: { labs: number }) {
  return (
    <div className="hx hx-5">
      <div>
        <p className="u-kicker">{labs} labs live</p>
        <h1>A lab for every idea <em>in AI.</em></h1>
        <p className="hx-lead">From your first model call to agents in production. Each idea gets a real machine, a task, and a check that tells you it works.</p>
        <CTA />
      </div>
      <div className="hx5-seal" aria-hidden="true"><span>Lab</span><span>Box</span></div>
    </div>
  );
}

/** 6. Words over a working terminal: the rain of Sudden Shower behind a lab session. */
function Hero6() {
  return (
    <div className="hx hx-6">
      <div>
        <h1>Stop watching tutorials. <em>Start shipping AI.</em></h1>
        <p className="hx-lead">Open a lab and a Linux machine starts for you in about a minute, with VS Code, a terminal and a model gateway.</p>
        <CTA />
      </div>
      <div className="hx6-art">
        <img src="/ukiyo/heroes/shower.webp" alt="" aria-hidden="true" />
        <pre className="hx6-term" aria-label="A lab terminal">{`learner:~$ labbox start langchain
✓ machine ready in 58 s
learner:~$ python agent.py
> Which train leaves first?
  The 7:40 to Ooty, platform 2.
✓ task passed  +20 XP`}</pre>
      </div>
    </div>
  );
}

/** 7. A magazine cover: one print as the cover, a big masthead and cover lines. */
function Hero7() {
  return (
    <div className="hx hx-7">
      <div className="hx7-cover">
        <img src="/ukiyo/heroes/kinryuzan.webp" alt="Woodblock print: Utagawa Hiroshige, Kinryuzan Temple at Asakusa, 1856" />
        <span className="hx7-mast">LabBox</span>
        <span className="hx7-issue">Issue 01 · AI</span>
      </div>
      <div className="hx7-lines">
        <p className="u-kicker">In this issue</p>
        <h1>Learn AI the way engineers do: <em>by building it.</em></h1>
        <ul>
          <li><b>RAG</b> Search your own documents, with sources</li>
          <li><b>Agents</b> Tools, memory and a human in the loop</li>
          <li><b>Evals</b> Prove it works before you ship</li>
        </ul>
        <CTA />
      </div>
    </div>
  );
}

/** 8. A mosaic: six category prints in a grid on the right, the words on the left. */
function Hero8({ labs }: { labs: number }) {
  return (
    <div className="hx hx-8">
      <div>
        <h1>{labs} labs. <em>One way to learn:</em> build.</h1>
        <p className="hx-lead">AI first, and the engineering around it: languages, frameworks, databases, system design and DevOps.</p>
        <CTA />
      </div>
      <div className="hx8-grid" aria-hidden="true">
        {["ai", "languages", "frameworks", "system-design", "databases", "devops"].map((t) => <span key={t}><TrackArt track={t} /></span>)}
      </div>
    </div>
  );
}

const HEROES = [
  { title: "Type only", note: "No big picture: a very large serif line, a red seal, six small lab prints underneath.", Hero: Hero1 },
  { title: "Tall print", note: "Words on the left, Hiroshige's Moon Pine framed on the right. New line: \"Don't watch AI. Build it.\"", Hero: Hero2 },
  { title: "Full-bleed wave", note: "The Great Wave across the whole width behind a dark wash, white words at the bottom.", Hero: Hero3 },
  { title: "Triptych", note: "Three tall Hiroshige prints side by side, the words beneath: the three moves of a lesson.", Hero: Hero4 },
  { title: "The seal", note: "Plain paper and a large red hanko stamp. Calm, no picture.", Hero: Hero5 },
  { title: "Terminal over rain", note: "A real lab session over Hiroshige's Sudden Shower. Says what you actually get.", Hero: Hero6 },
  { title: "Magazine cover", note: "A print as the cover, a masthead, and cover lines for RAG, agents and evals.", Hero: Hero7 },
  { title: "Mosaic", note: "The six category prints in a grid beside the words.", Hero: Hero8 },
];

export default function UkiyoHeroesPage() {
  const [labs, setLabs] = useState(23);
  useEffect(() => {
    document.title = "Hero options | LabBox by Telusko";
    api.catalog().then((c) => setLabs(c.length)).catch(() => {});
  }, []);
  return (
    <div className="ul-page u-home home">
      <header className="ul-top">
        <Logo to="/" />
        <nav aria-label="Heroes">{HEROES.map((h, i) => <a key={h.title} href={`#hero-${i + 1}`}>{i + 1}. {h.title}</a>)}</nav>
        <ThemeButton />
      </header>
      <main>
        {HEROES.map(({ title, note, Hero }, i) => (
          <section key={title} id={`hero-${i + 1}`} className="hx-section" aria-labelledby={`hero-${i + 1}-t`}>
            <div className="hx-label"><span className="u-kicker">Hero {i + 1} of {HEROES.length}</span> <strong id={`hero-${i + 1}-t`}>{title}</strong> <span>{note}</span></div>
            <Hero labs={labs} />
          </section>
        ))}
      </main>
    </div>
  );
}
