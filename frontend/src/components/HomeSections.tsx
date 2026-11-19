import { FAQS } from "../pages/InfoPages";

// Home page sections that show what a LabBox lab really is: real systems, real models, real
// incidents. Every artifact below is taken from an actual lab (Redis, rate limiter, the AI gateway).

/** "Inside a lab": six things no video course can do, each shown with a real artifact. */
export function InsideLab() {
  return (
    <div className="h-inside">
      <article className="h-in h-in-wide">
        <header><span className="h-num">01</span><h3>Build with real models</h3></header>
        <p>Your machine already has a model gateway. Call it like production code, then see every token it cost you.</p>
        <pre className="h-in-code">{`client.chat.completions.create(
    model="lab-chat",
    messages=[{"role": "user", "content": question}],
)`}</pre>
        <div className="h-in-term" aria-label="lab requests output">
          <div><span className="h-prompt">$</span> lab requests</div>
          <div className="h-in-row h-in-head"><span>model</span><span>in</span><span>out</span><span>ms</span><span>cost</span></div>
          <div className="h-in-row"><span>lab-chat</span><span>412</span><span>96</span><span>530</span><span>$0.00009</span></div>
          <div className="h-in-row"><span>lab-embed</span><span>1 204</span><span>0</span><span>88</span><span>$0.00002</span></div>
        </div>
        <div className="h-in-answer">
          <span>The answer, grounded in your own documents</span>
          <pre>{`{"answer": "Two bags, up to 15 kg each.",
 "sources": ["policy.md#luggage"],
 "confidence": 0.92}`}</pre>
        </div>
      </article>

      <article className="h-in">
        <header><span className="h-num">02</span><h3>Prove it under load</h3></header>
        <p>Checks fire real traffic at your code: load tests, races, 30 requests at once.</p>
        <div className="h-in-gauges">
          <InGauge label="p95 latency" value="38" unit="ms" target="≤ 50 ms" pct={58} ok />
          <InGauge label="calls to billing" value="1" unit="" target="≤ 2" pct={30} ok />
        </div>
      </article>

      <article className="h-in">
        <header><span className="h-num">03</span><h3>Fix live incidents</h3></header>
        <p>The pager goes off on a real, broken system. The clock is running.</p>
        <div className="h-in-pager" role="img" aria-label="An incident: Redis out of memory, 14:52 left">
          <div className="h-in-pager-head"><span>🚨 INCIDENT</span><span>14:52</span></div>
          <strong>Redis is refusing writes</strong>
          <code>OOM command not allowed when used memory &gt; 'maxmemory'</code>
        </div>
      </article>

      <article className="h-in">
        <header><span className="h-num">04</span><h3>A tutor that asks, not tells</h3></header>
        <p>Stuck? The AI tutor points at one thing and asks one question. It never hands you the answer.</p>
        <div className="h-in-chat">
          <div className="h-in-me">Why does the second call still take 1.5 s?</div>
          <div className="h-in-ai">✦ Look at what happens on a miss. After the slow lookup, where does the answer go?</div>
        </div>
      </article>

      <article className="h-in">
        <header><span className="h-num">05</span><h3>Defend your design</h3></header>
        <p>Every senior chapter ends with a design review, graded against a rubric.</p>
        <div className="h-in-review">
          <div className="h-in-score"><strong>9 / 10</strong><span>Design review</span></div>
          <div className="h-in-crit"><span className="ok">✓</span>Explains why two servers doubled the limit</div>
          <div className="h-in-crit"><span className="part">◐</span>Names a fix for bursts at window edges</div>
        </div>
      </article>

      <article className="h-in">
        <header><span className="h-num">06</span><h3>Your own machine</h3></header>
        <p>Real VS Code and a real terminal in the browser, next to the services your lab needs.</p>
        <ul className="h-in-services">
          {[["workspace", "VS Code, terminal, Python"], ["redis", "Redis 7.4"], ["replica", "a live replica"], ["lb", "nginx load balancer"]].map(([n, d]) => (
            <li key={n}><span className="h-in-dot" /><code>{n}</code><span>{d}</span></li>
          ))}
        </ul>
      </article>
    </div>
  );
}

function InGauge({ label, value, unit, target, pct, ok }: { label: string; value: string; unit: string; target: string; pct: number; ok: boolean }) {
  return (
    <div className={`h-in-gauge ${ok ? "ok" : ""}`}>
      <div><span>{label}</span><strong>{value}<small>{unit && ` ${unit}`}</small></strong></div>
      <div className="h-in-track"><i style={{ width: `${pct}%` }} /><b style={{ left: "75%" }} /></div>
      <small>target {target} · met ✓</small>
    </div>
  );
}

// The AI track, as planned: four stages from the first model call to your own GPT.
const AI_STAGES: { title: string; blurb: string; labs: string[] }[] = [
  { title: "Foundations", blurb: "What a model really does with your words.",
    labs: ["How LLMs work", "Prompts that hold up", "Structured output", "Tool calling", "Streaming responses", "Cost and latency budgets"] },
  { title: "Retrieval", blurb: "Answers grounded in your own data.",
    labs: ["Embeddings and similarity", "Vector search with pgvector", "RAG from zero", "Chunking and ranking", "Hybrid search and rerankers", "Evaluating RAG"] },
  { title: "Agents", blurb: "Models that act, safely.",
    labs: ["The agent loop", "Memory and state", "Planning multi-step work", "Prompt injection and guardrails", "Build an MCP server", "Multi-agent workflows"] },
  { title: "Production", blurb: "Ship it, measure it, own it.",
    labs: ["Evals and LLM judges", "Tracing and observability", "Caching and rate limits for LLMs", "Local models with Ollama", "Fine-tuning basics", "Build your own GPT"] },
];

export function AiTrack() {
  return (
    <div className="h-ai">
      {AI_STAGES.map((st, i) => (
        <article key={st.title} className="h-ai-stage">
          <header>
            <span className="h-ai-num">{String(i + 1).padStart(2, "0")}</span>
            <div><h3>{st.title}</h3><p>{st.blurb}</p></div>
          </header>
          <ol>
            {st.labs.map((l, j) => <li key={l}><span>{i * 6 + j + 1}</span>{l}</li>)}
          </ol>
        </article>
      ))}
    </div>
  );
}

const AI_FAQ = [
  {
    q: "What will I build in the AI labs?",
    a: <p>Real AI features end to end: a model call with structured output, a RAG search over your own documents, an agent that uses tools, evals that catch regressions. Every lab runs on your own machine, talking to real models through the LabBox gateway.</p>,
  },
  {
    q: "Do I need an API key or a paid AI account?",
    a: <p>No. Your lab machine comes with a model gateway and a daily allowance, and <code>lab requests</code> shows exactly what each call cost.</p>,
  },
];

/** FAQs right above the footer, as an accordion. */
export function HomeFaq() {
  const items = [...AI_FAQ, ...FAQS.filter((f) => !f.q.startsWith("What is"))].slice(0, 8);
  return (
    <div className="h-faq">
      {items.map((f) => (
        <details key={f.q} className="h-faq-item">
          <summary>{f.q}</summary>
          <div>{f.a}</div>
        </details>
      ))}
    </div>
  );
}
