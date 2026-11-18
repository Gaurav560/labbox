import { useEffect, useRef, useState, type FormEvent } from "react";
import { api, type PreviewPort } from "../api";

interface Props {
  labId: string;
  ports: PreviewPort[];
  visible: boolean;
}

// The learner's own app, through the backend's preview proxy. The proxy only lets this browser
// reach this learner's machine (HttpOnly cookie set by previewTicket) and only the listed ports.
export default function PreviewPane({ labId, ports, visible }: Props) {
  const [ready, setReady] = useState(false);
  const [error, setError] = useState("");
  const [port, setPort] = useState(ports[0]?.port ?? 0);
  const [path, setPath] = useState(ports[0]?.path ?? "/");
  const [draft, setDraft] = useState(path);
  const [reloads, setReloads] = useState(0);
  const asked = useRef(false);

  // Ask for the preview cookie the first time the tab is shown.
  useEffect(() => {
    if (!visible || asked.current) return;
    asked.current = true;
    api.previewTicket(labId).then(() => setReady(true)).catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, [visible, labId]);

  const clean = (p: string) => "/" + p.replace(/^\/+/, "");
  const src = `/preview/${encodeURIComponent(labId)}/${port}${clean(path)}`;

  function go(e: FormEvent) {
    e.preventDefault();
    setPath(clean(draft));
    setReloads((n) => n + 1);
  }

  function pickPort(p: number) {
    const info = ports.find((x) => x.port === p);
    setPort(p);
    setPath(info?.path ?? "/");
    setDraft(info?.path ?? "/");
  }

  return (
    <div className="preview-pane">
      <form className="preview-bar" onSubmit={go}>
        {ports.length > 1 && (
          <>
            <label className="sr-only" htmlFor="preview-port">App</label>
            <select id="preview-port" value={port} onChange={(e) => pickPort(Number(e.target.value))}>
              {ports.map((p) => (
                <option key={p.port} value={p.port}>{p.name} ({p.port})</option>
              ))}
            </select>
          </>
        )}
        <span className="preview-origin muted small-text" aria-hidden="true">:{port}</span>
        <label className="sr-only" htmlFor="preview-path">Path</label>
        <input id="preview-path" className="preview-path" value={draft} onChange={(e) => setDraft(e.target.value)} spellCheck={false} />
        <button className="btn btn-small" type="submit">Go</button>
        <button className="btn btn-small btn-ghost" type="button" onClick={() => setReloads((n) => n + 1)} aria-label="Reload preview">⟳</button>
        <a className="btn btn-small btn-ghost" href={src} target="_blank" rel="noreferrer">Open in new tab ↗</a>
      </form>
      {error ? (
        <div className="center-fill muted pad">{error}</div>
      ) : ready ? (
        <iframe key={`${src}#${reloads}`} className="preview-frame" src={src} title={`Preview of your app on port ${port}`} />
      ) : (
        <div className="center-fill muted"><span className="spinner" /> Opening preview...</div>
      )}
    </div>
  );
}
