/*
 * Renders one step's markdown, including the directives of the v2 chapter format:
 * :::character{name role}, :::mission, :::tip, :::warning, :::why, :::mistake,
 * :::deep-dive, :::incident{minutes}, and for history steps :::before, :::solved, :::timeline,
 * :::usedby and :::funfact; :::diagram{name} draws a built-in diagram (Diagrams.tsx), :::picture{name} a
 * small everyday picture (Pictures.tsx), and :::trace{title} turns its table into a step-through. A code fence
 * with the `run` attribute (```bash run) gets a Run in terminal button.
 */
import type { Element, ElementContent } from "hast";
import type { Root } from "mdast";
import type { ReactNode } from "react";
import Markdown, { type Components } from "react-markdown";
import remarkDirective from "remark-directive";
import { visit } from "unist-util-visit";
import CodeBlock from "./CodeBlock";
import Diagram from "./Diagrams";
import Picture from "./Pictures";
import Trace, { type TraceData } from "./Trace";
import Countdown from "./Countdown";

const CALLOUT_LABELS: Record<string, string> = {
  tip: "💡 Tip",
  warning: "⚠️ Warning",
  why: "Why this matters",
  mistake: "Common mistake",
};
const HISTORY_LABELS: Record<string, string> = {
  before: "Before it existed",
  solved: "The problem it solved",
  funfact: "Fun fact",
};
const BLOCKS = new Set([
  "character", "mission", "deep-dive", "incident", "question", "explain", "timeline", "usedby", "diagram", "picture", "trace",
  ...Object.keys(CALLOUT_LABELS), ...Object.keys(HISTORY_LABELS),
]);

/** Turn directives into <div data-directive=...> and keep code fence meta (```bash run). */
function remarkLessonBlocks() {
  return (tree: Root) => {
    visit(tree, (node, index, parent) => {
      if (node.type === "containerDirective" || node.type === "leafDirective") {
        const data = (node.data ??= {});
        data.hName = "div";
        const attrs: Record<string, string> = {};
        // hast properties use camelCase names (dataName renders as data-name).
        for (const [k, v] of Object.entries(node.attributes ?? {})) if (v != null) attrs[`data${k[0].toUpperCase()}${k.slice(1)}`] = v;
        if (node.type === "containerDirective" && node.name === "trace") {
          // The table becomes data for the step-through; anything else inside stays as text.
          // Without GFM tables the pipe rows arrive as one paragraph of text: read them line by line.
          const table = node.children.find((c) => c.type === "paragraph" && plain(c).trimStart().startsWith("|"));
          if (table) {
            const rows = plain(table)
              .split("\n")
              .map((ln) => ln.trim())
              .filter((ln) => ln.startsWith("|") && !/^\|[\s|:-]+\|$/.test(ln)) // drop the |---| separator
              .map((ln) => ln.replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
            attrs.dataTrace = JSON.stringify({ headers: rows[0] ?? [], rows: rows.slice(1) } satisfies TraceData);
            node.children = node.children.filter((c) => c !== table);
          }
        }
        data.hProperties = { ...attrs, dataDirective: BLOCKS.has(node.name) ? node.name : "unknown" };
      } else if (node.type === "textDirective" && parent && index !== undefined) {
        // Text like "ratio 3:a" is not meant as a directive: put the text back.
        parent.children.splice(index, 1, { type: "text", value: `:${node.name}` }, ...(node.children as never[]));
      } else if (node.type === "code" && node.meta) {
        (node.data ??= {}).hProperties = { dataMeta: node.meta };
      }
    });
  };
}

/** The plain text of an mdast node (a table cell, say), inline code included. */
function plain(node: unknown): string {
  const n = node as { value?: string; children?: unknown[] };
  if (typeof n.value === "string") return n.value;
  return (n.children ?? []).map(plain).join("");
}

function textOf(nodes: ElementContent[]): string {
  return nodes.map((n) => (n.type === "text" ? n.value : n.type === "element" ? textOf(n.children) : "")).join("");
}

function initials(name: string): string {
  return name
    .split(/\s+/)
    .map((w) => w[0] ?? "")
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

interface Props {
  markdown: string;
  onRun?: (command: string) => void;
  inline?: boolean; // render paragraphs as <span> (inside buttons)
}

export default function LessonMarkdown({ markdown, onRun, inline }: Props) {
  const components: Components = {
    ...(inline ? { p: ({ children }) => <span>{children}</span> } : {}),
    div({ node, children }) {
      const p = (node?.properties ?? {}) as Record<string, string | undefined>;
      return renderBlock(p.dataDirective, p, children);
    },
    pre({ node }) {
      const code = node?.children.find((c): c is Element => c.type === "element" && c.tagName === "code");
      if (!code) return null;
      const cls = (code.properties.className as string[] | undefined)?.find((c) => c.startsWith("language-"));
      const meta = String(code.properties.dataMeta ?? "");
      return (
        <CodeBlock
          code={textOf(code.children).replace(/\n$/, "")}
          language={cls?.slice("language-".length) ?? ""}
          runnable={/(^|\s)run(\s|$)/.test(meta)}
          onRun={onRun}
        />
      );
    },
    a({ href, children }) {
      return (
        <a href={href} target="_blank" rel="noreferrer noopener">
          {children}
        </a>
      );
    },
  };
  return (
    <Markdown remarkPlugins={[remarkDirective, remarkLessonBlocks]} components={components}>
      {markdown}
    </Markdown>
  );
}

function renderBlock(kind: string | undefined, p: Record<string, string | undefined>, children: ReactNode) {
  switch (kind) {
    case undefined:
      return <div>{children}</div>;
    case "character":
      return (
        <figure className="character">
          <div className="avatar" aria-hidden="true">{initials(p.dataName ?? "?")}</div>
          <div>
            <figcaption>
              <strong>{p.dataName}</strong>
              {p.dataRole && <span className="muted"> · {p.dataRole}</span>}
            </figcaption>
            <div className="character-says">{children}</div>
          </div>
        </figure>
      );
    case "mission":
      return (
        <div className="mission">
          <div className="mission-label">🎯 Mission</div>
          {children}
        </div>
      );
    case "deep-dive":
      return (
        <details className="deep-dive">
          <summary>Go deeper {p.dataMinutes ? `(${p.dataMinutes} min)` : ""}</summary>
          {children}
        </details>
      );
    case "incident":
      return (
        <div className="incident" role="alert">
          <div className="incident-head">
            <span>🚨 Incident</span>
            {p.dataMinutes && Number(p.dataMinutes) > 0 && <Countdown minutes={Number(p.dataMinutes)} />}
          </div>
          {children}
        </div>
      );
    case "before":
    case "solved":
    case "funfact":
      return (
        <aside className={`history-box history-${kind}`}>
          <div className="history-label">{p.dataTitle ?? HISTORY_LABELS[kind]}</div>
          {children}
        </aside>
      );
    case "timeline":
      // A plain markdown list ("- **1991**: first release") drawn as a timeline.
      return <div className="history-timeline">{children}</div>;
    case "usedby":
      return (
        <div className="history-usedby">
          <div className="history-label">{p.dataTitle ?? "Where it is used"}</div>
          {children}
        </div>
      );
    case "diagram":
      return <Diagram name={p.dataName ?? ""} caption={children} />;
    case "picture":
      return <Picture name={p.dataName ?? ""} code={p.dataCode} caption={children} />;
    case "trace": {
      let data: TraceData = { headers: [], rows: [] };
      try {
        data = JSON.parse(p.dataTrace ?? "");
      } catch {
        return <div>{children}</div>;
      }
      return (
        <>
          <Trace title={p.dataTitle} data={data} />
          {children}
        </>
      );
    }
    case "question":
    case "explain":
    case "unknown":
      return <div className={`directive-${kind}`}>{children}</div>;
    default:
      return (
        <aside className={`callout callout-${kind}`}>
          <div className="callout-label">{CALLOUT_LABELS[kind] ?? kind}</div>
          {children}
        </aside>
      );
  }
}
