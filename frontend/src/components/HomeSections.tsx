import { useState, type CSSProperties, type ReactNode } from "react";
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

/**
 * "Inside a lab": a real screenshot of a lab (a different one on each visit), then the tour of a lab's four moves
 * beside six features in a ruled grid (Ukiyo, 25 November: no icon bubbles).
 */
export function InsideLab({ tour }: { tour?: ReactNode }) {
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
      <div className="uh-inside-below">
        {tour}
        <ul className="uh-feats">
          {FEATURES.map((f, i) => (
            <li key={f.title}>
              <span className="uh-feat-n" aria-hidden="true">{String(i + 1).padStart(2, "0")}</span>
              <h3>{f.title}</h3>
              <p>{f.text}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

const FEATURES = [
  { title: "Real models", text: "A model gateway on your machine. No API key, every token counted." },
  { title: "Real VS Code", text: "The editor you use at work, with a terminal and live services beside it." },
  { title: "Checked under load", text: "Your code faces real traffic, races and latency targets, not a quiz." },
  { title: "Live incidents", text: "A real system breaks, the pager goes off, and you fix it." },
  { title: "A tutor that asks", text: "Stuck? It points at one thing and asks one question. No spoilers." },
  { title: "Design reviews", text: "Senior chapters end with your reasoning, graded against a rubric." },
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

/** The AI track as a ladder of four stages in fine ink lines, every planned lab listed. */
export function AiTrack() {
  return (
    <ol className="h-ai uh-ladder">
      {AI_STAGES.map((st, i) => (
        <li key={st.title} className="h-ai-stage">
          <span className="uh-stage">Stage {String(i + 1).padStart(2, "0")}</span>
          <h3>{st.title}</h3>
          <p>{st.blurb}</p>
          <ul className="uh-stage-labs" aria-label={`${st.title}: ${st.labs.length} labs`}>
            {st.labs.map((l) => <li key={l}>{l}</li>)}
          </ul>
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
