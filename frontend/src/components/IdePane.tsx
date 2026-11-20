import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "../api";
import { useTextSizes } from "../textSize";

// Real VS Code (openvscode-server) running inside the learner's own machine, shown through the
// signed-in /ide proxy. If the server has no VS Code, or it does not start, the lab falls back to the
// classic editor.
export default function IdePane({ labId, onUnavailable }: { labId: string; onUnavailable: (why: string) => void }) {
  const [url, setUrl] = useState<string | null>(null);
  const [state, setState] = useState<"starting" | "ready" | "slow">("starting");
  const [attempt, setAttempt] = useState(0);
  // VS Code reads font sizes only when it starts, so a new size reloads the frame (files and tabs stay).
  const { editor, terminal } = useTextSizes();
  const [sized, setSized] = useState({ editor, terminal });
  useEffect(() => {
    const t = setTimeout(() => setSized({ editor, terminal }), 600); // wait until the slider stops
    return () => clearTimeout(t);
  }, [editor, terminal]);

  useEffect(() => {
    let cancelled = false;
    setState("starting");
    api.openIde(labId).then((info) => {
      if (cancelled) return;
      if (!info.available) return onUnavailable("VS Code is not set up on this server.");
      setUrl(info.url);
      setState(info.ready ? "ready" : "slow");
    }).catch((e) => {
      if (!cancelled) onUnavailable(e instanceof ApiError ? e.message : "VS Code could not start.");
    });
    return () => { cancelled = true; };
  }, [labId, attempt, onUnavailable]);

  if (state === "starting" || !url) {
    return <div className="ide-wait"><span className="spinner" /> Starting your IDE...</div>;
  }
  if (state === "slow") {
    return (
      <div className="ide-wait">
        <p>The IDE is taking longer than usual to start.</p>
        <button className="btn btn-primary" onClick={() => setAttempt((a) => a + 1)}>Try again</button>
      </div>
    );
  }
  const src = `${url}${url.includes("?") ? "&" : "?"}lb_fs=${sized.editor}&lb_ts=${sized.terminal}`;
  return <IdeFrame key={src} src={src} />;
}

/** VS Code paints a white, empty window for a moment on its first start, before our dark theme and the
 * chapter's file load. Keep it behind the waiting screen until the workbench is drawn in its theme. */
function IdeFrame({ src }: { src: string }) {
  const ref = useRef<HTMLIFrameElement>(null);
  const [shown, setShown] = useState(false);
  useEffect(() => {
    const started = Date.now();
    const timer = setInterval(() => {
      let ready = false;
      try {
        // Same address as the app, so the page can look inside; a separate origin throws here.
        const bench = ref.current?.contentDocument?.querySelector(".monaco-workbench");
        // LabBox Dark is a dark theme; the white flash is VS Code's light default, before ours loads.
        ready = !!bench && bench.classList.contains("vs-dark") && !!bench.querySelector(".part.editor");
      } catch {
        ready = Date.now() - started > 1500; // cannot look inside: show it shortly after it loads
      }
      if (ready || Date.now() - started > 15000) {
        setShown(true);
        clearInterval(timer);
      }
    }, 150);
    return () => clearInterval(timer);
  }, []);
  return (
    <div className="ide-holder">
      <iframe ref={ref} className={`ide-frame ${shown ? "" : "ide-hidden"}`} src={src} title="VS Code" allow="clipboard-read; clipboard-write" />
      {!shown && <div className="ide-wait ide-over"><span className="spinner" /> Opening VS Code...</div>}
    </div>
  );
}
