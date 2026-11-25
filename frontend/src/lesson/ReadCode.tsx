import { useEffect, useState } from "react";
import { api, type StepCode } from "../api";

/** Read mode has no editor: under a step about a file, the lines it talks about, read-only, from the learner's own
 * files (or the starter), with the step's own lines marked. */
export default function ReadCode({ labId, chapterId, step }: { labId: string; chapterId: string; step: number }) {
  const [code, setCode] = useState<StepCode | null>(null);
  useEffect(() => {
    let live = true;
    setCode(null);
    api.stepCode(labId, chapterId, step).then((c) => live && setCode(c)).catch(() => live && setCode(null));
    return () => { live = false; };
  }, [labId, chapterId, step]);
  if (!code?.path || !code.lines.length) return null;
  const [from, to] = code.highlight.length === 2 ? code.highlight : [0, -1];
  const width = String(code.first_line + code.lines.length - 1).length;
  return (
    <figure className="read-code" aria-label={`${code.path}, lines ${code.first_line} to ${code.first_line + code.lines.length - 1}`}>
      <figcaption className="read-code-head">
        <span className="read-code-path">{code.path}</span>
        <span className="read-code-note">read only · open Action mode to edit</span>
      </figcaption>
      <pre>
        {code.lines.map((text, i) => {
          const n = code.first_line + i;
          return (
            <span key={n} className={`read-code-line${n >= from && n <= to ? " is-marked" : ""}`}>
              <span className="read-code-no" aria-hidden="true">{String(n).padStart(width)}</span>
              <code>{text || " "}</code>
            </span>
          );
        })}
      </pre>
    </figure>
  );
}
