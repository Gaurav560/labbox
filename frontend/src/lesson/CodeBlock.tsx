import { useState } from "react";

interface Props {
  code: string;
  language: string;
  runnable: boolean;
  onRun?: (command: string) => void;
}

async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false; // insecure origin or permission denied
  }
}

export default function CodeBlock({ code, language, runnable, onRun }: Props) {
  const [copied, setCopied] = useState<"idle" | "ok" | "fail">("idle");

  async function copy() {
    setCopied((await copyText(code)) ? "ok" : "fail");
    window.setTimeout(() => setCopied("idle"), 1500);
  }

  return (
    <div className="code-card">
      <div className="code-head">
        <span className="code-lang">{language || "text"}</span>
        <span className="spacer" />
        {runnable && onRun && (
          <button className="code-btn" onClick={() => onRun(code)} title="Paste into the terminal (you press Enter)">
            ▶ Run in terminal
          </button>
        )}
        <button className="code-btn" onClick={copy} aria-live="polite">
          {copied === "ok" ? "Copied ✓" : copied === "fail" ? "Copy failed" : "Copy"}
        </button>
      </div>
      <pre>
        <code>{code}</code>
      </pre>
    </div>
  );
}
