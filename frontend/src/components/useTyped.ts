import { useEffect, useState } from "react";

/**
 * Types a little terminal session on a loop: lines starting with "$ " are typed a key at a time,
 * the rest appear at once. With reduced motion everything shows at once and nothing moves.
 */
export function useTyped(lines: string[], pauseMs = 4000): { shown: string[]; typing: string } {
  const reduce = typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  const [line, setLine] = useState(reduce ? lines.length : 0);
  const [chars, setChars] = useState(0);

  useEffect(() => {
    if (reduce) return;
    let t: number;
    if (line >= lines.length) {
      t = window.setTimeout(() => { setLine(0); setChars(0); }, pauseMs); // pause, then play again
    } else if (!lines[line].startsWith("$ ")) {
      t = window.setTimeout(() => { setLine(line + 1); setChars(0); }, 450);
    } else if (chars < lines[line].length) {
      t = window.setTimeout(() => setChars(chars + 1), chars < 2 ? 0 : 38 + Math.random() * 40);
    } else {
      t = window.setTimeout(() => { setLine(line + 1); setChars(0); }, 380);
    }
    return () => window.clearTimeout(t);
  }, [line, chars, lines, reduce, pauseMs]);

  return { shown: lines.slice(0, line), typing: line < lines.length ? lines[line].slice(0, chars) : "" };
}
