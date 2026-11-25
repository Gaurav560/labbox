/*
 * "Start a lab" on the home page (owner, 25 November: "one click and we spin up a container for you with everything
 * the lab needs"; picked from nine options). The lab's real stack (its lab.yaml and Dockerfile) packs itself into
 * one container, piece by piece with a line in the log each, then a green tick and Start, which opens that course.
 */
import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";

type Piece = { logo: string | null; icon?: "term" | "ai"; name: string; step: string };
type Lab = { id: string; label: string; challenge: string; pieces: Piece[] };
const P = (logo: string, name: string, step: string): Piece => ({ logo, name, step });
const LINUX = P("linux", "Ubuntu 24.04", "your own Linux machine, in a container");
// The editor is named for what it does, not the product (owner, 25 November: it may change if VS Code is too heavy).
const EDITOR: Piece = { logo: null, icon: "term", name: "Editor and terminal", step: "a code editor and a terminal, in your browser" };
const AI: Piece = { logo: null, icon: "ai", name: "AI code assistant", step: "explains, hints and reviews, never the answer" };

const GATEWAY: Piece = { logo: null, icon: "ai", name: "Model gateway", step: "real models, no API key, every token counted" };

// Each lab's real machine (labs/<id>/lab.yaml and Dockerfile). Owner, 25 November: three AI labs, then Spring Boot,
// Python, a database, Linux, FastAPI and Redis.
const LABS: Lab[] = [
  { id: "langchain", label: "LangChain", challenge: "A rule-based help desk",
    pieces: [LINUX, P("python", "Python 3.12", "the language"), P("langchain", "LangChain 1.5", "and every package the course uses"), GATEWAY, EDITOR, AI] },
  { id: "spring-ai", label: "Spring AI", challenge: "Connect /ask to the model",
    pieces: [LINUX, P("java", "Java 21", "the JDK the course uses"), P("spring", "Spring Boot 4.2", "with Maven and every dependency, offline"),
      P("spring-ai", "Spring AI 2.1", "chat, prompts, tools and RAG for Java"), GATEWAY, EDITOR, AI] },
  { id: "rag-vector-databases", label: "RAG", challenge: "Find sections by their words",
    pieces: [LINUX, P("python", "Python 3.12", "the language"), { logo: null, icon: "ai", name: "Embedding models", step: "two local models, already downloaded" },
      P("sql", "FAISS and Qdrant", "vector search, running locally"), GATEWAY, EDITOR, AI] },
  { id: "spring-boot-first-api", label: "Spring Boot", challenge: "Name the application",
    pieces: [LINUX, P("java", "Java 21", "the JDK the course uses"), P("spring", "Spring Boot 3.4", "with Maven and every dependency, offline"), EDITOR, AI] },
  { id: "python-basics", label: "Python", challenge: "hello.py: Pocket says hello",
    pieces: [LINUX, P("python", "Python 3.12", "the language, ready to run"), EDITOR, AI] },
  { id: "postgres-indexing-incident", label: "Postgres", challenge: "Find the slow query",
    pieces: [LINUX, P("python", "Python 3.12", "with psql"), P("postgresql", "PostgreSQL 16", "a real database server"),
      P("sql", "1 million orders", "loaded and waiting to be slow"), EDITOR, AI] },
  { id: "linux-on-call", label: "Linux", challenge: "Find the hidden welcome note",
    pieces: [P("linux", "Ubuntu 24.04", "a whole Linux server to explore"), { logo: null, icon: "term", name: "Bash and the classic tools", step: "grep, sed, lsof, htop, tar and the rest" }, EDITOR, AI] },
  { id: "fastapi-first-api", label: "FastAPI", challenge: "GET /menu: list every item",
    pieces: [LINUX, P("python", "Python 3.12", "the language, with pip"), P("fastapi", "FastAPI", "the framework, answering in the Preview tab"), EDITOR, AI] },
  { id: "redis-in-practice", label: "Redis", challenge: "Measure one round trip to Redis",
    pieces: [LINUX, P("python", "Python 3.12", "with the redis client and redis-cli"), P("fastapi", "FastAPI", "a basket API to make fast"),
      P("redis", "Redis 7.4", "the primary server"), P("redis", "Redis replica", "a second server, copying the first"), EDITOR, AI] },
];

function Picker({ lab, onPick }: { lab: Lab; onPick: (l: Lab) => void }) {
  return (
    <div className="um-picker" role="tablist" aria-label="Pick a lab">
      {LABS.map((l) => <button key={l.id} type="button" role="tab" aria-selected={l.id === lab.id} onClick={() => onPick(l)}>{l.label}</button>)}
    </div>
  );
}

function Mark({ p }: { p: Piece }) {
  if (p.logo) return <img src={`/logos/${p.logo}.svg`} alt="" />;
  if (p.icon === "term") return (
    <svg viewBox="0 0 48 48" aria-hidden="true"><rect x="4" y="8" width="40" height="32" rx="4" fill="#1b2533" />
      <path d="M12 19l6 5-6 5" fill="none" stroke="#e2583f" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M22 30h12" stroke="#e9e2d4" strokeWidth="3" strokeLinecap="round" /></svg>
  );
  return (
    <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 5l4.2 11.3L40 20l-11.8 3.9L24 35l-4.2-11.1L8 20l11.8-3.7z" fill="#c63f28" />
      <path d="M37 30l1.8 4.6 4.7 1.6-4.7 1.7L37 42.6l-1.8-4.7-4.7-1.7 4.7-1.6z" fill="#1f3a64" /></svg>
  );
}

type Pt = [number, number];
const L = (p: Pt, q: Pt, t: number): Pt => [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t];
const pts = (...ps: Pt[]) => ps.map((p) => p.join(",")).join(" ");
// The container in two-point perspective (viewBox 600 x 360): front face A B C D, end face B E F C, roof A H E B.
const A: Pt = [50, 118], B: Pt = [410, 132], C: Pt = [412, 292], D: Pt = [54, 278];
const E: Pt = [520, 104], F: Pt = [518, 262], H: Pt = [160, 90];
/** Where a point inside the end face sits: u across (B to E), v down (top to bottom). */
const END = (u: number, v: number): Pt => L(L(B, E, u), L(C, F, u), v);
/** The door opening's centre, where loaded pieces fly to (in viewBox units). */
export const DOOR: Pt = END(0.5, 0.55);
/** The inside: the far wall's bottom corner, and a point on the floor (t along the length, u from the front wall back). */
const Dd: Pt = [D[0] + (E[0] - B[0]), D[1] + (E[1] - B[1])];
const FLOOR = (t: number, u: number): Pt => L(L(D, C, t), L(Dd, F, t), u);
/** Where piece i of n stands inside: in stacks two high along the floor, the first stack at the far end. */
function slot(i: number, n: number): { at: Pt; row: number } {
  const cols = Math.ceil(n / 2), col = Math.floor(i / 2), level = i % 2;
  const t = 0.13 + (cols > 1 ? col * (0.55 / (cols - 1)) : 0.3); // clear of the door folded back at the end
  const [x, y] = FLOOR(t, 0.72);
  return { at: [x, y - level * 42], row: level };
}

/** A cardboard crate with the piece's logo on its front, standing on the floor at `at` (its front bottom centre). */
function Crate({ p, at, fresh }: { p: Piece; at: Pt; fresh: boolean }) {
  const [x, y] = at, w = 44, h = 40, kx = 14, ky = -5;
  const sx = DOOR[0] - x, sy = DOOR[1] - y;
  return (
    <g className={`ua-c-box ${fresh ? "is-new" : ""}`} style={{ "--sx": `${sx}px`, "--sy": `${sy}px` } as CSSProperties}>
      <polygon className="ua-c-box-top" points={pts([x - w / 2, y - h], [x + w / 2, y - h], [x + w / 2 + kx, y - h + ky], [x - w / 2 + kx, y - h + ky])} />
      <polygon className="ua-c-box-side" points={pts([x + w / 2, y - h], [x + w / 2 + kx, y - h + ky], [x + w / 2 + kx, y + ky], [x + w / 2, y])} />
      <rect className="ua-c-box-front" x={x - w / 2} y={y - h} width={w} height={h} rx="2" />
      <line className="ua-c-box-tape" x1={x + kx / 2 - 2} y1={y - h + ky / 2} x2={x + kx / 2 + 2} y2={y - h + ky / 2} />
      <rect className="ua-c-box-label" x={x - 15} y={y - h + 6} width="30" height="28" rx="3" />
      {p.logo ? <image href={`/logos/${p.logo}.svg`} x={x - 11} y={y - h + 9} width="22" height="22" />
        : <text className="ua-c-box-glyph" x={x} y={y - h + 26} textAnchor="middle">{p.icon === "term" ? ">_" : "✦"}</text>}
      <circle className="ua-c-box-led" cx={x - w / 2 + 6} cy={y - 6} r="2.6" />
    </g>
  );
}

/** The part of the drawing that is shown: tight around the container, so it fills the width (owner: "a little big"). */
const VB = [36, 76, 556, 258] as const;

function Casting({ at }: { at: Pt }) {
  return <g className="ua-c-cast"><rect x={at[0] - 7} y={at[1] - 6} width="14" height="12" rx="1.5" /><ellipse cx={at[0]} cy={at[1]} rx="3.4" ry="2.4" /></g>;
}

/**
 * A steel shipping container in the hand-drawn style of the Docker docs (owner, 25 November: "way more cool"):
 * corrugated walls, frame rails, corner posts and castings, stencilled numbers, the Docker whale, and doors at the
 * end with locking bars. phase "load": doors open, the wall turns to glass and each piece rides in as a crate; "close": the doors swing
 * shut and the bars lock; "start": the roof lamp blinks; "run": lamp and light strip glow green and it hums.
 */
function Container({ phase, loaded, pieces, bump }: { phase: "wait" | "load" | "close" | "start" | "run"; loaded: number; pieces: Piece[]; bump: number }) {
  const open = phase === "wait" || phase === "load";
  const strips = 26;
  const plate = phase === "run" ? "● RUNNING" : phase === "start" ? "◐ STARTING" : phase === "close" ? "◼ SEALING" : phase === "load" ? `▲ LOADING ${loaded}/${pieces.length}` : "▶ TAP TO START";
  const doorLeaf = (a: Pt, b: Pt, c: Pt, d: Pt, ribs: number) => (
    <>
      <polygon className="ua-c-leaf" points={pts(a, b, c, d)} />
      {Array.from({ length: ribs }, (_, i) => {
        const t = (i + 1) / (ribs + 1);
        const [x1, y1] = L(a, b, t), [x2, y2] = L(d, c, t);
        return <line key={i} className="ua-c-leafrib" x1={x1} y1={y1 + 5} x2={x2} y2={y2 - 5} />;
      })}
      <polygon className="ua-c-line" points={pts(a, b, c, d)} />
    </>
  );
  return (
    <svg className={`ua-container is-${phase}`} viewBox={VB.join(" ")} aria-hidden="true">
      <ellipse className="ua-c-shadow" cx="290" cy="318" rx="240" ry="15" />
      <ellipse className="ua-c-glow" cx="290" cy="306" rx="230" ry="10" />
      <g className="ua-c-hum">
        <g className="ua-c-bump" key={bump}>
          {/* roof, with its shallow corrugation */}
          <polygon className="ua-c-top" points={pts(A, H, E, B)} />
          {[0.25, 0.5, 0.75].map((t) => { const [x1, y1] = L(A, H, t), [x2, y2] = L(B, E, t); return <line key={t} className="ua-c-roofline" x1={x1} y1={y1} x2={x2} y2={y2} />; })}
          {/* the inside, seen through the wall while it loads: far wall, end wall, plank floor, a ceiling light */}
          <g className="ua-c-room">
            <polygon className="ua-c-far" points={pts(H, E, F, Dd)} />
            <polygon className="ua-c-endwall" points={pts(A, H, Dd, D)} />
            <polygon className="ua-c-deck" points={pts(D, C, F, Dd)} />
            {[0.25, 0.5, 0.75].map((u) => { const [x1, y1] = L(D, Dd, u), [x2, y2] = L(C, F, u); return <line key={u} className="ua-c-plank" x1={x1} y1={y1} x2={x2} y2={y2} />; })}
            <line className="ua-c-lightbar" x1={L(H, E, 0.08)[0]} y1={L(H, E, 0.08)[1] + 10} x2={L(H, E, 0.92)[0]} y2={L(H, E, 0.92)[1] + 10} />
            {pieces.slice(0, loaded).map((p, i) => ({ p, i, ...slot(i, pieces.length) }))
              .sort((a, b) => a.i - b.i)
              .map(({ p, i, at }) => <Crate key={p.name + i} p={p} at={at} fresh={i === loaded - 1 && phase === "load"} />)}
          </g>
          {/* front wall: corrugated strips, light and shade; it turns to glass while loading so the crates show */}
          <g className="ua-c-wall">
          {Array.from({ length: strips }, (_, i) => (
            <polygon key={i} className={i % 2 ? "ua-c-strip-b" : "ua-c-strip-a"}
              points={pts(L(A, B, i / strips), L(A, B, (i + 1) / strips), L(D, C, (i + 1) / strips), L(D, C, i / strips))} />
          ))}
          {Array.from({ length: strips }, (_, i) => { const [x1, y1] = L(A, B, i / strips), [x2, y2] = L(D, C, i / strips); return <line key={i} className="ua-c-ridge" x1={x1} y1={y1 + 12} x2={x2} y2={y2 - 12} />; })}
          </g>
          <polygon className="ua-c-glass" points={pts(A, B, C, D)} />
          {/* frame: top and bottom rails, corner posts */}
          <polygon className="ua-c-rail" points={pts(A, B, [B[0], B[1] + 12], [A[0], A[1] + 12])} />
          <polygon className="ua-c-rail is-low" points={pts([D[0], D[1] - 12], [C[0], C[1] - 12], C, D)} />
          <polygon className="ua-c-post" points={pts(A, [A[0] + 13, A[1] + 0.5], [D[0] + 13, D[1] + 0.5], D)} />
          <polygon className="ua-c-post" points={pts([B[0] - 13, B[1] - 0.5], B, C, [C[0] - 13, C[1] - 0.5])} />
          {/* stencils and the whale, following the wall's slope */}
          <g transform="skewY(2.2)">
            <g className="ua-c-print">
            <text className="ua-c-stencil" x="76" y="146">LABBOX</text>
            <text className="ua-c-stencil is-small" x="76" y="160">LBXU 240 017 3 · 22G1</text>
            <rect className="ua-c-spec" x="340" y="146" width="52" height="22" rx="2" />
            {[152, 157, 162].map((y) => <line key={y} className="ua-c-specline" x1="345" y1={y} x2="387" y2={y} />)}
            </g>
            {/* the whale stays the hero: printed on the glass, in front of the crates (owner, 25 November) */}
            <image className="ua-c-whale" href="/logos/docker.svg" x="146" y="104" width="214" height="186" />
            <g className="ua-c-plate"><rect x="66" y="259" width="122" height="17" rx="3" /><text x="75" y="271">{plate}</text></g>
          </g>
          {/* the end: open doors and what is inside, or closed and locked */}
          {open ? (
            <>
              <polygon className="ua-c-inside" points={pts(END(0.06, 0.05), END(0.94, 0.05), END(0.94, 0.95), END(0.06, 0.95))} />
              <polygon className="ua-c-floor" points={pts(END(0.06, 0.8), END(0.94, 0.8), END(0.94, 0.95), END(0.06, 0.95))} />
              <polygon className="ua-c-frame" points={pts(B, E, F, C)} />
            </>
          ) : (
            <g className="ua-c-doors">
              <polygon className="ua-c-end" points={pts(B, E, F, C)} />
              {Array.from({ length: 8 }, (_, i) => { const t = (i + 1) / 9; const [x1, y1] = L(B, E, t), [x2, y2] = L(C, F, t); return <line key={i} className="ua-c-endrib" x1={x1} y1={y1 + 8} x2={x2} y2={y2 - 8} />; })}
              <line className="ua-c-seam" x1={END(0.5, 0)[0]} y1={END(0.5, 0)[1]} x2={END(0.5, 1)[0]} y2={END(0.5, 1)[1]} />
              {[0.17, 0.36, 0.64, 0.83].map((u) => {
                const [x1, y1] = END(u, 0.05), [x2, y2] = END(u, 0.95), [hx, hy] = END(u, 0.56);
                return (
                  <g key={u}>
                    <line className="ua-c-bar" x1={x1} y1={y1} x2={x2} y2={y2} />
                    <line className="ua-c-handle" x1={hx} y1={hy} x2={hx + 11} y2={hy - 2} style={{ transformOrigin: `${hx}px ${hy}px` }} />
                  </g>
                );
              })}
            </g>
          )}
          {/* the door leaves, swung open: the left one folded back on the wall, the right one out towards you */}
          <g className={`ua-c-leaf-l ${open ? "" : "is-shut"}`}>{doorLeaf(L(B, A, 0.15), B, C, L(C, D, 0.15), 3)}</g>
          <g className={`ua-c-leaf-r ${open ? "" : "is-shut"}`}>{doorLeaf(E, [574, 120], [572, 284], F, 3)}</g>
          {[A, B, C, D, E, F, H].map((p, i) => <Casting key={i} at={p} />)}
          {/* outline */}
          <polygon className="ua-c-line is-thick" points={pts(A, H, E, F, C, D)} />
          <polyline className="ua-c-line" points={pts(A, B, E)} />
          <line className="ua-c-line" x1={B[0]} y1={B[1]} x2={C[0]} y2={C[1]} />
          {/* roof lamp and the light strip along the bottom rail */}
          <g className="ua-c-lamp"><rect x="466" y="96" width="12" height="6" rx="1" /><circle cx="472" cy="92" r="6" /></g>
          <polygon className="ua-c-strip-light" points={pts([D[0] + 16, D[1] - 6], [C[0] - 16, C[1] - 6], [C[0] - 16, C[1] - 3], [D[0] + 16, D[1] - 3])} />
        </g>
      </g>
    </svg>
  );
}

/**
 * The lab's stack waits on a dock above the container. After a click on Spin up each piece travels into the open
 * doors and stays stacked inside, with its line in the log; then the doors close and lock, docker start runs, the
 * container lights up and hums, and Start appears.
 */
export default function UkiyoMachine({ signedIn }: { signedIn: boolean }) {
  const [lab, setLab] = useState(LABS[0]); // LangChain: AI first
  // It plays when the visitor asks (owner, 25 November: "better if the user clicks and sees the animation"):
  // run 0 is the waiting box with the Spin up button; each click starts a new run.
  const [run, setRun] = useState(0);
  // step 1..n: piece step-1 travels from the dock into the doors; then n+1 close, n+2 start, n+3 running.
  const [step, setStep] = useState(0);
  const n = lab.pieces.length;
  const still = typeof window !== "undefined" && !!window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

  useEffect(() => {
    setStep(0);
    if (run === 0) return;
    if (still) { setStep(n + 3); return; }
    const timers: number[] = [];
    let at = 150;
    for (let k = 1; k <= n; k++) { timers.push(window.setTimeout(() => setStep(k), at)); at += 900; }
    timers.push(window.setTimeout(() => setStep(n + 1), at + 100));
    timers.push(window.setTimeout(() => setStep(n + 2), at + 1000));
    timers.push(window.setTimeout(() => setStep(n + 3), at + 2300));
    return () => timers.forEach(clearTimeout);
  }, [run, lab, n, still]);

  // The clock counts up smoothly from the click and reaches 58 s as the container starts running.
  const [secs, setSecs] = useState(0);
  useEffect(() => {
    setSecs(0);
    if (run === 0 || still) { if (still && run) setSecs(58); return; }
    const total = 150 + n * 900 + 2300, t0 = performance.now();
    const t = window.setInterval(() => {
      const s = Math.min(58, Math.round(((performance.now() - t0) / total) * 58));
      setSecs(s);
      if (s >= 58) clearInterval(t);
    }, 100);
    return () => clearInterval(t);
  }, [run, lab, n, still]);

  // The first run plays by itself when the section comes into view, on every visit (owner, 25 November);
  // after that a lab change waits for Run or a tap.
  const rootRef = useRef<HTMLDivElement>(null);
  const autoPlayed = useRef(false);
  useEffect(() => {
    const el = rootRef.current;
    if (!el || autoPlayed.current) return;
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting && !autoPlayed.current) { autoPlayed.current = true; setRun((r) => (r === 0 ? 1 : r)); io.disconnect(); }
    }, { threshold: 0.45 });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const waiting = run === 0;
  const slug = lab.label.toLowerCase().replace(/\s+/g, "-"); // short enough for a phone: "docker run system-design"
  const phase = waiting ? "wait" : step <= n ? "load" : step === n + 1 ? "close" : step === n + 2 ? "start" : "run";
  const loadedNow = Math.min(step, n);
  const running = phase === "run";
  const spin = () => setRun((r) => r + 1);

  // The piece on its way: measure its chip on the dock and the door opening, and fly the chip between them.
  const shipRef = useRef<HTMLDivElement>(null);
  const svgWrap = useRef<HTMLDivElement>(null);
  const chips = useRef<(HTMLLIElement | null)[]>([]);
  const [flight, setFlight] = useState<{ i: number; dx: number; dy: number } | null>(null);
  useLayoutEffect(() => {
    if (phase !== "load" || step < 1) { setFlight(null); return; }
    const chip = chips.current[step - 1], box = svgWrap.current?.querySelector("svg");
    if (!chip || !box) return;
    const c = chip.getBoundingClientRect(), b = box.getBoundingClientRect();
    const tx = b.left + ((DOOR[0] - VB[0]) / VB[2]) * b.width, ty = b.top + ((DOOR[1] - VB[1]) / VB[3]) * b.height;
    setFlight({ i: step - 1, dx: tx - (c.left + c.width / 2), dy: ty - (c.top + c.height / 2) });
  }, [step, phase]);

  const clock = phase === "wait" ? null : (
    <><b>{phase === "run" ? 58 : secs} s</b> · {phase === "load" ? `${loadedNow}/${n} loaded` : phase === "close" ? "sealing" : phase === "start" ? "starting" : "running"}</>
  );
  return (
    <div className="ua" ref={rootRef}>
      <div className="ua-text">
        <Picker lab={lab} onPick={(l) => { setLab(l); setRun(0); }} />
        <h2 id="machine-title">One click, and a container spins up for you <em>with everything the lab needs.</em></h2>
        <p>Linux, the language, the framework, the databases, an editor and terminal, and an AI code assistant: set up and running in about a minute. Nothing to install. You go straight to the first challenge.</p>
        {/* the call to action sits with the words, so the box shows only the machine (owner, 25 November) */}
        {/* the command that starts the machine (owner picked the terminal design); it types itself, and a green Run key
            and a pulsing ring make it plain that it is the thing to press, on phones too */}
        {waiting ? (
          <div className="ua-try">
            <p className="ua-try-label"><span aria-hidden="true">●</span> Try it: tap Run</p>
            <button type="button" className="ua-go" onClick={spin} aria-label={`Spin up the ${lab.label} machine`}
              style={{ "--len": `docker run ${slug}`.length } as CSSProperties} key={lab.id}>
              <span className="ua-go-prompt">$</span>
              <span className="ua-go-cmd">docker run {slug}</span>
              <span className="ua-go-run">Run ▶</span>
            </button>
          </div>
        ) : <button type="button" className="uh-replay" onClick={spin}>↺ Spin it up again</button>}
      </div>
      <div className={`ua-box ${running ? "is-sealed" : ""} ${waiting ? "is-waiting" : ""}`} key={`${lab.id}-${run}`}>
        <div className="ua-lid">
          <img src="/logos/docker.svg" alt="" />
          <span>your machine · {lab.label}</span>
          <span className={`ua-clock ${running ? "is-on" : ""}`} aria-hidden="true">{clock}</span>
          <span className="ua-bar" aria-hidden="true"><i style={{ width: `${(Math.min(step, n + 3) / (n + 3)) * 100}%` }} /></span>
        </div>
        <div className="ua-ship" ref={shipRef}>
          {/* each piece appears on its own when its turn comes, rises, and flies into the open doors (owner, 25 November:
              "this should not be present from the start; when I spin the container it should appear one by one") */}
          <ul className="ua-dock" aria-hidden="true">
            {phase === "load" && step >= 1 && (() => {
              const i = step - 1, p = lab.pieces[i];
              const ready = flight?.i === i;
              return (
                <li key={p.name + i} ref={(el) => { chips.current[i] = el; }} className={ready ? "is-flying" : "is-arriving"}
                  style={ready ? ({ "--dx": `${flight!.dx}px`, "--dy": `${flight!.dy}px` } as CSSProperties) : undefined}>
                  <span className="ua-logo"><Mark p={p} /></span><span className="ua-name">{p.name}</span>
                </li>
              );
            })()}
          </ul>
          <div ref={svgWrap} className={waiting ? "is-tappable" : ""} onClick={waiting ? spin : undefined}
            title={waiting ? "Tap to start" : undefined}><Container phase={phase} loaded={phase === "load" ? Math.max(0, step) : waiting ? 0 : n} pieces={lab.pieces} bump={loadedNow} /></div>
        </div>
        <div className="ua-logwrap">
          <ol className="ua-log" aria-live="polite">
            {waiting && <li className="ua-log-wait">learner:~$ <span className="ua-caret" aria-hidden="true" /></li>}
            {lab.pieces.slice(0, loadedNow).map((p, i) => (
              <li key={p.name + i} className="is-piece"><b>✓</b> <strong>{p.name}</strong> <span>{p.step}</span></li>
            ))}
            {step >= n + 2 && <li className="is-cmd"><b>▶</b> <strong>docker start</strong> <span>labbox-{lab.id}</span></li>}
            {running && <li className="is-run"><b>●</b> <strong>running</strong> <span>ready in 58 s, all yours</span></li>}
          </ol>
        </div>
        <span className="ua-stamp" role="img" aria-label="Ready">
          <svg viewBox="0 0 64 64" width="64" height="64"><circle cx="32" cy="32" r="29" /><path d="M19 33.5l9 9 17-19" /></svg>
        </span>
        <div className="ua-ready">
          <span><b>Ready</b> · first challenge: {lab.challenge}</span>
          <Link className="h-btn h-btn-primary" to={signedIn ? `/courses/${lab.id}` : `/login?next=${encodeURIComponent(`/courses/${lab.id}`)}`}>Start →</Link>
        </div>
      </div>
    </div>
  );
}
