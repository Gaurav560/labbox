import { useCallback, useEffect, useRef, useState } from "react";

// The hero product tour: a small copy of a lab playing the four moves of every lesson (read, guess,
// code, check). Each loop shows a different real lab, in a shuffled order per visitor.
// Sound is off until the visitor turns it on; the sounds are made in the browser, no audio files.

interface Tour {
  lab: string;
  step: string;
  title: string;
  read: string;
  q: string;
  options: string[];
  answer: number;
  file: string;
  code: string;
  run: string;
  out: string[];
  result: string;
  xp: number;
}

const TOURS: Tour[] = [
  {
    lab: "python-basics", step: "Step 2 of 6", title: "Functions give values back",
    read: "A function can hand a value back with return. Then you can print it, store it, or pass it on.",
    q: "add(2, 3) returns a + b. What comes back?", options: ["5", "23", "None"], answer: 0,
    file: "math_utils.py", code: "def add(a, b):\n    return a + b",
    run: "python3 -c 'from math_utils import add; print(add(2, 3))'", out: ["5"],
    result: "3 of 3 checks passed", xp: 60,
  },
  {
    lab: "java-basics", step: "Step 3 of 7", title: "Strings join with +",
    read: "In Java, + glues strings together. Duke uses it to greet every new learner by name.",
    q: 'What is "coffee" + "cup"?', options: ['"coffeecup"', '"coffee cup"', "A compile error"], answer: 0,
    file: "Greet.java", code: 'public class Greet {\n    public static void main(String[] a) {\n        System.out.println("Hello, " + a[0]);\n    }\n}',
    run: "javac Greet.java && java Greet Asha", out: ["Hello, Asha"],
    result: "2 of 2 checks passed", xp: 40,
  },
  {
    lab: "go-basics", step: "Step 4 of 6", title: "Loop over a slice",
    read: "range walks a slice one item at a time. Add each price to a running total and return it.",
    q: "s := []int{1, 2}; s = append(s, 3). What is len(s)?", options: ["2", "3", "It panics"], answer: 1,
    file: "total.go", code: "func Total(prices []int) int {\n    sum := 0\n    for _, p := range prices {\n        sum += p\n    }\n    return sum\n}",
    run: "go test ./...", out: ["ok   labbox/orders   0.41s"],
    result: "4 of 4 checks passed", xp: 80,
  },
  {
    lab: "javascript-inside-out", step: "Step 2 of 5", title: "map makes a new array",
    read: "map calls your function on every item and collects the answers in a brand new array.",
    q: "What is [1, 2, 3].map(n => n * 2)?", options: ["[2, 4, 6]", "6", "[1, 2, 3]"], answer: 0,
    file: "double.js", code: "export const double = (xs) =>\n  xs.map((n) => n * 2);",
    run: "node demo.js", out: ["[ 2, 4, 6 ]"],
    result: "3 of 3 checks passed", xp: 60,
  },
  {
    lab: "sql-from-zero", step: "Step 3 of 8", title: "WHERE picks the rows",
    read: "WHERE keeps only the rows that match. ORDER BY then sorts what is left.",
    q: "Which rows does WHERE price > 20 keep?", options: ["Prices above 20", "Prices of 20 and up", "Every row"], answer: 0,
    file: "query.sql", code: "SELECT item, price\nFROM menu\nWHERE price > 20\nORDER BY price;",
    run: "psql -f query.sql", out: [" vada pav    |    25", " cold coffee |    40", "(2 rows)"],
    result: "1 of 1 check passed", xp: 50,
  },
  {
    lab: "postgres-indexing-incident", step: "Incident", title: "Checkout is slow",
    read: "The pager says p99 is 4.2 s. EXPLAIN shows a Seq Scan: Postgres reads every one of a million rows.",
    q: "A million orders and a Seq Scan. What fixes it?", options: ["An index on customer_id", "More RAM", "A longer timeout"], answer: 0,
    file: "fix.sql", code: "CREATE INDEX idx_orders_customer\n    ON orders (customer_id);",
    run: "psql -f fix.sql", out: ["CREATE INDEX"],
    result: "p99 4.2 s → 38 ms", xp: 325,
  },
  {
    lab: "fastapi-first-api", step: "Step 3 of 6", title: "Path parameters",
    read: "Put {item} in the path and FastAPI hands that part of the URL to your function.",
    q: "GET /menu/vada%20pav. What is item?", options: ['"vada pav"', '"vada%20pav"', '"/menu"'], answer: 0,
    file: "main.py", code: '@app.get("/menu/{item}")\ndef price(item: str):\n    return {"item": item, "price": MENU[item]}',
    run: "curl localhost:8000/menu/vada%20pav", out: ['{"item":"vada pav","price":25}'],
    result: "2 of 2 checks passed", xp: 40,
  },
  {
    lab: "spring-boot-first-api", step: "Step 2 of 6", title: "Map a URL to a method",
    read: "A controller method answers a URL. Spring turns what it returns into JSON for you.",
    q: "Which annotation answers GET /orders?", options: ['@GetMapping("/orders")', '@PostMapping("/orders")', "@Bean"], answer: 0,
    file: "OrderController.java", code: '@GetMapping("/orders")\nList<Order> all() {\n    return repo.findAll();\n}',
    run: "curl localhost:8080/orders", out: ['[{"id":1,"item":"filter coffee"}]'],
    result: "3 of 3 checks passed", xp: 60,
  },
  {
    lab: "express-api", step: "Step 2 of 5", title: "Send JSON back",
    read: "res.json() turns an object into JSON and sets the right headers in one call.",
    q: "What does res.json() set for you?", options: ["Content-Type: application/json", "A cookie", "Status 404"], answer: 0,
    file: "server.js", code: 'app.get("/health", (req, res) => {\n  res.json({ ok: true });\n});',
    run: "curl localhost:3000/health", out: ['{"ok":true}'],
    result: "2 of 2 checks passed", xp: 40,
  },
  {
    lab: "python-collections", step: "Step 3 of 6", title: "Count with a dict",
    read: "A dict maps keys to values. get() with a default makes counting things a one liner.",
    q: 'counts is empty. What is counts.get("latte", 0)?', options: ["0", "None", "KeyError"], answer: 0,
    file: "orders.py", code: "counts = {}\nfor item in orders:\n    counts[item] = counts.get(item, 0) + 1\nprint(counts)",
    run: "python3 orders.py", out: ["{'coffee': 3, 'latte': 1}"],
    result: "3 of 3 checks passed", xp: 60,
  },
  {
    lab: "java-collections", step: "Step 2 of 6", title: "A map holds one value per key",
    read: "put() on a key that is already there replaces the old value. merge() can add to it instead.",
    q: 'put("coffee", 1), then put("coffee", 5). What is get("coffee")?', options: ["5", "1", "6"], answer: 0,
    file: "Stock.java", code: 'Map<String, Integer> stock = new HashMap<>();\nstock.merge("coffee", 1, Integer::sum);\nSystem.out.println(stock);',
    run: "java Stock.java", out: ["{coffee=1}"],
    result: "2 of 2 checks passed", xp: 40,
  },
  {
    lab: "redis-in-practice", step: "Step 3 of 6", title: "Cache-aside",
    read: "Look in Redis first. On a miss, do the slow work once and keep the answer for 60 seconds.",
    q: 'Redis holds price:samosa = 20. What does r.get("price:samosa") return?', options: ['"20", a string', "20, a number", "None"], answer: 0,
    file: "app.py", code: 'cached = r.get(f"price:{item}")\nif cached is not None:\n    return {"item": item, "price": int(cached)}',
    run: "time curl -s localhost:8000/price/samosa", out: ['{"item":"samosa","price":20}', "real  0m0.012s"],
    result: "2 of 2 checks passed", xp: 80,
  },
  {
    lab: "linux-on-call", step: "Step 2 of 6", title: "Count and rank",
    read: "awk picks a field, sort and uniq -c count repeats. Pipes chain small tools into answers.",
    q: "A file has the lines b, a, b. What does uniq -c print?", options: ["1 b, 1 a, 1 b", "2 b and 1 a", "1 a and 2 b"], answer: 0,
    file: "top_ips.sh", code: "awk '{print $2}' \"$1\" | sort | uniq -c \\\n  | sort -rn | head -3 | awk '{print $2}'",
    run: "bash top_ips.sh access.log", out: ["10.0.0.12", "10.0.0.31", "10.0.1.7"],
    result: "3 of 3 checks passed", xp: 70,
  },
  {
    lab: "git-without-fear", step: "Step 3 of 7", title: "Undo a pushed mistake",
    read: "Never rewrite history other people have. git revert adds a new commit that undoes the bad one.",
    q: "The bad commit is already pushed. What is safe?", options: ["git revert", "git reset --hard", "git commit --amend"], answer: 0,
    file: "terminal", code: "git log --oneline\ngit revert --no-edit 6af4e0e",
    run: "grep coffee menu.txt", out: ["filter coffee 30", "cold coffee 40"],
    result: "2 of 2 checks passed", xp: 80,
  },
  {
    lab: "postgres-transactions-and-locks", step: "Incident", title: "Checkout is frozen",
    read: "A forgotten transaction holds a lock on order 42, so every payment for it waits forever.",
    q: "When is a row lock released?", options: ["When its transaction ends", "After the UPDATE", "After a few seconds"], answer: 0,
    file: "find.sql", code: "SELECT pid, state, application_name\nFROM pg_stat_activity\nWHERE state = 'idle in transaction';",
    run: "psql -c 'SELECT pg_terminate_backend(4711)'", out: [" pg_terminate_backend", " t"],
    result: "Checkout goes through again", xp: 80,
  },
];

// Short labels on the tabs; the longer phrase is the tooltip and the accessible name.
const SCENES = [["Read", "Read a little"], ["Guess", "Guess what happens"], ["Code", "Write real code"], ["Check", "Get instant feedback"]];

function shuffled(n: number): number[] {
  const order = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  return order;
}

/** Where each scene ends: scene 2 types the code, then shows the command and its output lines. */
function sceneEnd(scene: number, t: Tour): number {
  return [0, 1, t.code.length + 1 + t.out.length, 2][scene];
}

/** Tiny sounds made with Web Audio: a soft key tick, a pick, and a chime when the checks pass. */
function useSound() {
  const ctx = useRef<AudioContext | null>(null);
  const [on, setOn] = useState(false);
  const toggle = useCallback(() => {
    setOn((v) => {
      if (!v && !ctx.current) {
        try { ctx.current = new AudioContext(); } catch { return false; }
      }
      if (!v) ctx.current?.resume().catch(() => {});
      return !v;
    });
  }, []);
  const tone = useCallback((freq: number, at: number, len: number, gain: number, type: OscillatorType = "sine") => {
    const ac = ctx.current;
    if (!ac) return;
    const o = ac.createOscillator();
    const g = ac.createGain();
    o.type = type;
    o.frequency.value = freq;
    const t0 = ac.currentTime + at;
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(gain, t0 + 0.005);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + len);
    o.connect(g).connect(ac.destination);
    o.start(t0);
    o.stop(t0 + len + 0.02);
  }, []);
  const play = useCallback((kind: "key" | "pick" | "pass") => {
    if (!on) return;
    if (kind === "key") tone(1500 + Math.random() * 500, 0, 0.025, 0.02, "triangle");
    if (kind === "pick") tone(660, 0, 0.12, 0.05);
    if (kind === "pass") { tone(784, 0, 0.35, 0.06); tone(1175, 0.12, 0.5, 0.06); }
  }, [on, tone]);
  return { on, toggle, play };
}

export default function HeroTour() {
  const reduce = typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  const [order] = useState(() => shuffled(TOURS.length));
  const [at, setAt] = useState(0);
  const tour = TOURS[order[at]];
  const [scene, setScene] = useState(reduce ? 2 : 0);
  const [n, setN] = useState(() => (reduce ? sceneEnd(2, tour) : 0));
  const [paused, setPaused] = useState(false);
  const { on: soundOn, toggle: toggleSound, play } = useSound();

  const go = useCallback((s: number, step = 0) => { setScene(s); setN(step); }, []);

  useEffect(() => {
    if (paused || reduce) return;
    let delay: number;
    let next: () => void;
    const typed = tour.code.length;
    if (scene === 0) { delay = 3400; next = () => go(1); }
    else if (scene === 1 && n === 0) { delay = 1600; next = () => { setN(1); play("pick"); }; }
    else if (scene === 1) { delay = 2200; next = () => go(2); }
    else if (scene === 2 && n < typed) {
      delay = n === 0 ? 400 : 22 + Math.random() * 38;
      next = () => { setN(n + 1); if (tour.code[n].trim()) play("key"); };
    }
    else if (scene === 2 && n < sceneEnd(2, tour)) { delay = n === typed ? 500 : 450; next = () => setN(n + 1); }
    else if (scene === 2) { delay = 1200; next = () => go(3); }
    else if (n === 0) { delay = 700; next = () => setN(1); }
    else if (n === 1) { delay = 550; next = () => { setN(2); play("pass"); }; }
    else { delay = 3000; next = () => { setAt((i) => (i + 1) % order.length); go(0); }; }
    const t = window.setTimeout(next, delay);
    return () => window.clearTimeout(t);
  }, [scene, n, paused, reduce, tour, order.length, go, play]);

  // Picking a scene shows it finished and pauses, so it can be read.
  const pick = (s: number) => { setPaused(true); go(s, sceneEnd(s, tour)); };

  const typed = scene === 2 ? Math.min(n, tour.code.length) : tour.code.length;
  const shownOut = scene === 2 ? Math.max(0, n - tour.code.length - 1) : tour.out.length;
  const ranCmd = scene === 3 || (scene === 2 && n > tour.code.length);

  return (
    <section className="h-term tour" aria-label="A short tour of a LabBox lab">
      <div className="h-term-bar">
        <span className="h-dots" aria-hidden="true"><i /><i /><i /></span>
        <span className="h-lab-name">● {tour.lab}</span>
        <span className="tour-tools">
          <button className="tour-tool" onClick={toggleSound} aria-pressed={soundOn} aria-label={soundOn ? "Turn sound off" : "Turn sound on"} title={soundOn ? "Sound on" : "Sound off"}>
            {soundOn ? "🔊" : "🔇"}
          </button>
          {!reduce && (
            <button className="tour-tool" onClick={() => setPaused((p) => !p)} aria-label={paused ? "Play the tour" : "Pause the tour"} title={paused ? "Play" : "Pause"}>
              {paused ? "▶" : "❚❚"}
            </button>
          )}
        </span>
      </div>

      <div className="tour-steps" role="tablist" aria-label="Tour steps">
        {SCENES.map(([label, long], i) => (
          <button
            key={label} role="tab" aria-selected={scene === i} aria-label={`${i + 1}. ${long}`} title={long}
            className={`tour-step ${scene === i ? "is-on" : ""} ${scene > i ? "is-done" : ""}`}
            onClick={() => pick(i)}
          >
            <b>{i + 1}</b><span>{label}</span>
          </button>
        ))}
      </div>

      <div className="tour-body" key={`${at}-${scene}`} aria-live="off">
        {scene === 0 && (
          <div className="tour-read">
            <p className="tour-kicker">{tour.step}</p>
            <h3>{tour.title}</h3>
            <p>{tour.read}</p>
          </div>
        )}

        {scene === 1 && (
          <div className="tour-guess">
            <p className="tour-kicker">Predict</p>
            <p className="tour-q">{tour.q}</p>
            <div className="tour-options">
              {tour.options.map((o, i) => (
                <div key={o} className={`tour-option ${n > 0 && i === tour.answer ? "is-right" : ""}`}>
                  <span className="tour-radio" aria-hidden="true" />{o}
                </div>
              ))}
            </div>
            {n > 0 && <p className="tour-right">Right! Now try it for real.</p>}
          </div>
        )}

        {(scene === 2 || scene === 3) && (
          <div className="tour-code">
            <div className="tour-editor">
              <div className="tour-tab">{tour.file}</div>
              <pre>{tour.code.slice(0, typed)}{scene === 2 && n <= tour.code.length && <span className="h-cursor" />}</pre>
            </div>
            <div className="tour-terminal">
              {ranCmd && <div><span className="h-prompt">$</span> {tour.run}</div>}
              {tour.out.slice(0, shownOut).map((l, i) => <div key={i} className="h-out">{l}</div>)}
            </div>
            {scene === 3 && (
              <div className="tour-check">
                <span className={`tour-check-btn ${n >= 1 ? "is-pressed" : ""}`}>Check</span>
                {n >= 2 && (
                  <>
                    <span className="tour-pass">✓ {tour.result}</span>
                    <span className="tour-xp">+{tour.xp} XP</span>
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
