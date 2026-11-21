import { useState, type CSSProperties } from "react";
import { FAQS } from "../pages/InfoPages";
import SHOTS from "../homeShots.json";
import { LAB_TONES } from "../brand";

// Home page sections: a real lab screenshot, the AI track and the FAQs.

// The glow around the screenshot takes the lab's own colour (LAB_TONES in brand.ts).

/** The lab a screenshot belongs to, from its file name (/images/labs/<lab>-<nn>-<chapter>.webp). */
export function shotTone(src: string): string | undefined {
  const name = src.split("/").pop() ?? "";
  const lab = Object.keys(LAB_TONES).find((id) => name.startsWith(`${id}-`));
  return lab ? LAB_TONES[lab] : undefined;
}

/** "Inside a lab": a real screenshot of a lab (a different one on each visit), then six features. */
export function InsideLab() {
  const [shot] = useState(() => SHOTS[Math.floor(Math.random() * SHOTS.length)]);
  return (
    <div className="h-inside">
      <figure className="h-shot" style={{ "--shot-tone": shotTone(shot.src) } as CSSProperties}>
        <div className="h-shot-bar" aria-hidden="true">
          <span /><span /><span />
          <em>{shot.caption}</em>
        </div>
        <img
          key={shot.src}
          src={shot.src}
          width={1920}
          height={1152}
          loading="lazy"
          alt={shot.alt}
        />
      </figure>
      <ul className="h-feats">
        {FEATURES.map((f) => (
          <li key={f.title}>
            <span className="h-feat-icon" aria-hidden="true">{f.icon}</span>
            <h3>{f.title}</h3>
            <p>{f.text}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

const svg = (d: string) => (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);

const FEATURES = [
  { title: "Real models", text: "A model gateway on your machine. No API key, every token counted.",
    icon: svg("M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8zM18 15l.9 2.1L21 18l-2.1.9L18 21l-.9-2.1L15 18l2.1-.9z") },
  { title: "Real VS Code", text: "The editor you use at work, with a terminal and live services beside it.",
    icon: svg("M8 7l-5 5 5 5M16 7l5 5-5 5M13.5 4l-3 16") },
  { title: "Checked under load", text: "Your code faces real traffic, races and latency targets, not a quiz.",
    icon: svg("M3 12h4l3-8 4 16 3-8h4") },
  { title: "Live incidents", text: "A real system breaks, the pager goes off, and you fix it.",
    icon: svg("M12 3a6 6 0 016 6v4l2 3H4l2-3V9a6 6 0 016-6zM10 19a2 2 0 004 0") },
  { title: "A tutor that asks", text: "Stuck? It points at one thing and asks one question. No spoilers.",
    icon: svg("M4 5h16v11H9l-5 4zM9 10h.01M12 10h.01M15 10h.01") },
  { title: "Design reviews", text: "Senior chapters end with your reasoning, graded against a rubric.",
    icon: svg("M9 4h6l1 2h3v15H5V6h3zM9 13l2 2 4-4") },
];

// The AI track, as planned: four stages from the first model call to your own GPT.
const AI_STAGES: { title: string; blurb: string; labs: string[] }[] = [
  { title: "Foundations", blurb: "What a model really does with your words, and how to make it dependable.",
    labs: ["How LLMs work", "Prompts that hold up", "Structured output", "Tool calling", "Streaming responses", "Cost and latency budgets"] },
  { title: "Retrieval", blurb: "Answers grounded in your own data, and proof that they are right.",
    labs: ["Embeddings and similarity", "Vector search with pgvector", "RAG from zero", "Chunking and ranking", "Hybrid search and rerankers", "Evaluating RAG"] },
  { title: "Agents", blurb: "Models that plan, use tools and act, without being talked into harm.",
    labs: ["The agent loop", "Memory and state", "Planning multi-step work", "Prompt injection and guardrails", "Build an MCP server", "Multi-agent workflows"] },
  { title: "Production", blurb: "Ship it, measure it, own it, then build your own GPT.",
    labs: ["Evals and LLM judges", "Tracing and observability", "Caching and rate limits for LLMs", "Local models with Ollama", "Fine-tuning basics", "Build your own GPT"] },
];

export function AiTrack() {
  return (
    <ol className="h-ai">
      {AI_STAGES.map((st, i) => (
        <li key={st.title} className="h-ai-stage">
          <span className="h-ai-num" aria-hidden="true">{String(i + 1).padStart(2, "0")}</span>
          <span className="h-ai-dot" aria-hidden="true" />
          <h3>{st.title}</h3>
          <p>{st.blurb}</p>
          <div className="h-ai-labs" title={st.labs.join(", ")}>
            <strong>{st.labs.length} labs</strong>
            <ul>
              {st.labs.slice(0, 3).map((l) => <li key={l}>{l}</li>)}
              <li className="h-ai-more">+ {st.labs.length - 3} more</li>
            </ul>
          </div>
        </li>
      ))}
    </ol>
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

/** FAQs right above the footer: one numbered list, one answer open at a time, opening smoothly. */
export function HomeFaq() {
  const items = [...AI_FAQ, ...FAQS.filter((f) => !f.q.startsWith("What is"))].slice(0, 8);
  return (
    <div className="h-faq">
      {items.map((f, i) => (
        <details key={f.q} className="h-faq-item" name="home-faq">
          <summary>
            <span className="h-faq-n" aria-hidden="true">{String(i + 1).padStart(2, "0")}</span>
            <span className="h-faq-q">{f.q}</span>
            <span className="h-faq-icon" aria-hidden="true" />
          </summary>
          <div className="h-faq-a">{f.a}</div>
        </details>
      ))}
    </div>
  );
}
