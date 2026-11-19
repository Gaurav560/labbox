import { useEffect, useState } from "react";
import { api, ApiError } from "../api";

// Real VS Code (openvscode-server) running inside the learner's own machine, shown through the
// signed-in /ide proxy. If the server has no VS Code, or it does not start, the lab falls back to the
// classic editor.
export default function IdePane({ labId, onUnavailable }: { labId: string; onUnavailable: (why: string) => void }) {
  const [url, setUrl] = useState<string | null>(null);
  const [state, setState] = useState<"starting" | "ready" | "slow">("starting");
  const [attempt, setAttempt] = useState(0);

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
  return <iframe key={url} className="ide-frame" src={url} title="VS Code" allow="clipboard-read; clipboard-write" />;
}
