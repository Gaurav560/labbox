import { useCallback, useEffect, useState, type FormEvent, type ReactNode } from "react";
import { Link, Navigate, useSearchParams } from "react-router-dom";
import {
  admin, api, ApiError, library, libraryImage, type CatalogLab, type LibraryItem, type LibraryItemIn, type LibraryKind, type LibraryLevel,
  type AdminError, type AdminLabReport, type AdminLabRow, type AdminLearner, type AdminMachine, type AdminSpend, type AdminWindow, type FunnelStep,
} from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import ThemeButton from "../components/ThemeButton";
import { LIBRARY_TABS } from "./LibraryPage";

// The admin area (Phase J): what to improve, and what is running. Only for accounts with is_admin;
// the backend refuses everyone else, this page only hides itself.

const TABS = [
  ["funnel", "Funnel"],
  ["labs", "Labs"],
  ["learners", "Learners"],
  ["machines", "Machines"],
  ["ai", "AI spend"],
  ["errors", "Errors"],
  ["library", "Library"],
] as const;
type Tab = (typeof TABS)[number][0];

const pct = (v: number | null | undefined) => (v == null ? "n/a" : `${Math.round(v * 100)}%`);
const when = (iso: string | null) => (iso ? new Date(iso.endsWith("Z") || iso.includes("+") ? iso : `${iso}Z`).toLocaleString() : "never");
const secs = (s: number | null) => (s == null ? "" : s < 90 ? `${Math.round(s)} s` : `${(s / 60).toFixed(1)} min`);

function useLoad<T>(load: () => Promise<T>, deps: unknown[]): [T | null, string | null, () => void] {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [n, setN] = useState(0);
  useEffect(() => {
    let live = true;
    setError(null);
    load().then((d) => live && setData(d)).catch((e) => live && setError(e instanceof ApiError ? e.message : String(e)));
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, n]);
  return [data, error, () => setN((x) => x + 1)];
}

function Panel({ title, note, children, actions }: { title: string; note?: string; children: ReactNode; actions?: ReactNode }) {
  return (
    <section className="adm-panel">
      <div className="adm-panel-head">
        <div>
          <h2>{title}</h2>
          {note && <p className="muted small-text">{note}</p>}
        </div>
        {actions}
      </div>
      {children}
    </section>
  );
}

function Bar({ value, max, tone = "brand" }: { value: number; max: number; tone?: "brand" | "warn" }) {
  return (
    <span className={`adm-bar adm-bar-${tone}`} aria-hidden="true">
      <span style={{ width: `${max && value > 0 ? Math.max(2, (100 * value) / max) : 0}%` }} />
    </span>
  );
}

function Loading({ error }: { error: string | null }) {
  return error ? <p className="adm-error" role="alert">{error}</p> : <p className="muted">Loading...</p>;
}

// ---------- tabs ----------

function FunnelTab() {
  const [win, setWin] = useState<AdminWindow>("30d");
  const [steps, error] = useLoad<FunnelStep[]>(() => admin.funnel(win), [win]);
  return (
    <Panel
      title="Funnel"
      note="Learners who signed up in this window, and how far they got. Paywall and payments join after Phase I."
      actions={
        <div className="adm-seg" role="group" aria-label="Window">
          {(["7d", "30d", "90d", "all"] as AdminWindow[]).map((w) => (
            <button key={w} aria-pressed={w === win} onClick={() => setWin(w)}>{w === "all" ? "All" : w}</button>
          ))}
        </div>
      }
    >
      {!steps ? <Loading error={error} /> : steps.length === 0 ? <p className="muted">No sign-ups in this window.</p> : (
        <ol className="adm-funnel">
          {steps.map((s) => (
            <li key={s.key}>
              <span className="adm-funnel-label">{s.label}</span>
              <Bar value={s.count} max={steps[0].count} />
              <span className="adm-num">{s.count}</span>
              <span className="muted small-text adm-funnel-drop">{s.of_previous == null ? "" : `${pct(s.of_previous)} of the step before`}</span>
            </li>
          ))}
        </ol>
      )}
    </Panel>
  );
}

function LabDetail({ id, onBack }: { id: string; onBack: () => void }) {
  const [r, error] = useLoad<AdminLabReport>(() => admin.lab(id), [id]);
  if (!r) return <Loading error={error} />;
  return (
    <>
      <button className="btn btn-small btn-ghost" onClick={onBack}>← All labs</button>
      <Panel title={r.title} note={`${r.learners} learners opened it. Tasks are ranked so the most confusing come first: low pass rate, failed checks and hints per learner.`}>
        <table className="adm-table">
          <thead><tr><th>Task</th><th>Tried</th><th>Pass rate</th><th>Failed checks / learner</th><th>Hints / learner</th><th>Confusion</th></tr></thead>
          <tbody>
            {r.tasks.map((t) => (
              <tr key={t.id}>
                <td>{t.title}<div className="muted small-text">{t.chapter_id}</div></td>
                <td className="adm-num">{t.attempted}</td>
                <td className="adm-num">{pct(t.pass_rate)}</td>
                <td className="adm-num">{t.failed_checks_per_learner}</td>
                <td className="adm-num">{t.hints_per_learner} <span className="muted small-text">of {t.hint_count}</span></td>
                <td><Bar value={t.confusion} max={Math.max(...r.tasks.map((x) => x.confusion), 0.01)} tone="warn" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
      {r.chapters.map((c) => {
        const most = Math.max(...c.steps.map((s) => s.stopped_here), 1);
        return (
          <Panel key={c.id} title={c.title} note={`${c.started} started, ${c.completed} finished. "Stopped here": unfinished chapters left on that step for 2+ days.`}>
            <table className="adm-table">
              <thead><tr><th>Step</th><th>Stopped here</th><th>Avg time</th><th>Views</th></tr></thead>
              <tbody>
                {c.steps.map((s) => (
                  <tr key={s.index}>
                    <td><span className="muted small-text">{s.index + 1}. {s.type}</span> {s.title}</td>
                    <td><span className="adm-inline"><Bar value={s.stopped_here} max={most} tone="warn" /><span className="adm-num">{s.stopped_here}</span></span></td>
                    <td className="adm-num">{secs(s.avg_seconds)}</td>
                    <td className="adm-num">{s.views}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>
        );
      })}
    </>
  );
}

function LabsTab() {
  const [params, setParams] = useSearchParams();
  const open = params.get("lab");
  const [rows, error] = useLoad<AdminLabRow[]>(() => admin.labs(), []);
  if (open) return <LabDetail id={open} onBack={() => setParams({ tab: "labs" })} />;
  return (
    <Panel title="Labs" note="Open a lab to see where learners stop and which tasks confuse them.">
      {!rows ? <Loading error={error} /> : (
        <table className="adm-table">
          <thead><tr><th>Lab</th><th>Learners</th><th>Chapters finished</th><th>Task pass rate</th><th>Most confusing task</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td><button className="adm-link" onClick={() => setParams({ tab: "labs", lab: r.id })}>{r.title}</button></td>
                <td className="adm-num">{r.learners}</td>
                <td className="adm-num">{r.chapters_completed}</td>
                <td className="adm-num">{pct(r.pass_rate)}</td>
                <td className="muted">{r.most_confusing_task ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Panel>
  );
}

function LearnersTab() {
  const [query, setQuery] = useState("");
  const [typed, setTyped] = useState("");
  useEffect(() => {
    const t = setTimeout(() => setQuery(typed.trim()), 300);
    return () => clearTimeout(t);
  }, [typed]);
  const [rows, error] = useLoad<AdminLearner[]>(() => admin.learners(query), [query]);
  return (
    <Panel
      title="Learners"
      note={query ? `Usernames containing "${query}".` : "The 50 newest accounts."}
      actions={<input className="adm-search" type="search" placeholder="Search username" aria-label="Search username" value={typed} onChange={(e) => setTyped(e.target.value)} />}
    >
      {!rows ? <Loading error={error} /> : rows.length === 0 ? <p className="muted">No one matches.</p> : (
        <table className="adm-table">
          <thead><tr><th>Learner</th><th>Joined</th><th>Labs</th><th>XP</th><th>Checks</th><th>Last active</th></tr></thead>
          <tbody>
            {rows.map((u) => (
              <tr key={u.id}>
                <td>{u.username} {u.is_admin && <span className="adm-tag">admin</span>}<div className="muted small-text">id {u.id}</div></td>
                <td>{when(u.joined)}</td>
                <td className="adm-num">{u.labs}</td>
                <td className="adm-num">{u.xp}</td>
                <td className="adm-num">{u.checks}</td>
                <td>{when(u.last_active)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Panel>
  );
}

function MachinesTab() {
  const [rows, error, reload] = useLoad<AdminMachine[]>(() => admin.machines(), []);
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const act = useCallback(async (m: AdminMachine, action: "stop" | "kill") => {
    const what = action === "stop"
      ? `Stop ${m.username}'s ${m.lab_title} machine? Their files are kept, and their lab page says an admin stopped it.`
      : `Kill ${m.username}'s ${m.lab_title} machine? It is removed; their files stay and the next start builds a fresh machine.`;
    if (!window.confirm(what)) return;
    setBusy(m.container);
    try {
      await admin.machineAction(m.container, action);
      setMessage(`${action === "stop" ? "Stopped" : "Killed"} ${m.container}`);
      reload();
    } catch (e) {
      setMessage(e instanceof ApiError ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  }, [reload]);
  return (
    <Panel title="Machines" note="Lab machines running now, oldest first." actions={<button className="btn btn-small" onClick={reload}>Refresh</button>}>
      {message && <p className="adm-note" role="status">{message}</p>}
      {!rows ? <Loading error={error} /> : rows.length === 0 ? <p className="muted">No machine is running.</p> : (
        <table className="adm-table">
          <thead><tr><th>Learner</th><th>Lab</th><th>Running since</th><th>Learner's files</th><th /></tr></thead>
          <tbody>
            {rows.map((m) => (
              <tr key={m.container}>
                <td>{m.username}<div className="muted small-text">{m.container}</div></td>
                <td>{m.lab_title}</td>
                <td>{when(m.started_at)}</td>
                <td className="adm-num">{m.files_mb} MB</td>
                <td className="adm-actions">
                  <button className="btn btn-small" disabled={busy === m.container} onClick={() => act(m, "stop")}>Stop</button>
                  <button className="btn btn-small btn-danger" disabled={busy === m.container} onClick={() => act(m, "kill")}>Kill</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Panel>
  );
}

function SpendTab() {
  const [days, setDays] = useState(30);
  const [s, error] = useLoad<AdminSpend>(() => admin.spend(days), [days]);
  const most = s ? Math.max(...s.days.map((d) => d.tokens), 1) : 1;
  const usd = (v: number) => (v === 0 ? "$0" : `$${v.toFixed(v < 1 ? 4 : 2)}`);
  return (
    <Panel
      title="AI spend"
      note="Every call through the LabBox gateway: labs, the tutor and code completion. Local Ollama models cost nothing."
      actions={
        <div className="adm-seg" role="group" aria-label="Days">
          {[7, 30, 90].map((d) => <button key={d} aria-pressed={d === days} onClick={() => setDays(d)}>{d} days</button>)}
        </div>
      }
    >
      {!s ? <Loading error={error} /> : s.days.length === 0 ? <p className="muted">No AI requests in this window.</p> : (
        <div className="adm-grid">
          <table className="adm-table">
            <thead><tr><th>Day</th><th>Tokens</th><th>Requests</th><th>Cost</th></tr></thead>
            <tbody>
              {[...s.days].reverse().map((d) => (
                <tr key={d.day}>
                  <td>{d.day}</td>
                  <td><span className="adm-inline"><Bar value={d.tokens} max={most} /><span className="adm-num">{d.tokens.toLocaleString()}</span></span></td>
                  <td className="adm-num">{d.requests}</td>
                  <td className="adm-num">{usd(d.cost_usd)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div>
            <h3>By model</h3>
            <table className="adm-table">
              <tbody>{s.by_model.map((m) => <tr key={m.name}><td>{m.name}</td><td className="adm-num">{m.tokens.toLocaleString()}</td><td className="adm-num">{usd(m.cost_usd)}</td></tr>)}</tbody>
            </table>
            <h3>Top learners</h3>
            <table className="adm-table">
              <tbody>{s.top_learners.map((m) => <tr key={m.name}><td>{m.name}</td><td className="adm-num">{m.tokens.toLocaleString()}</td><td className="adm-num">{usd(m.cost_usd)}</td></tr>)}</tbody>
            </table>
          </div>
        </div>
      )}
    </Panel>
  );
}

function ErrorsTab() {
  const [rows, error, reload] = useLoad<AdminError[]>(() => admin.errors(), []);
  return (
    <Panel title="Errors" note="The latest server errors (5xx). Search the logs for the request id to see the whole story."
      actions={<button className="btn btn-small" onClick={reload}>Refresh</button>}>
      {!rows ? <Loading error={error} /> : rows.length === 0 ? <p className="muted">No server errors recorded. Good.</p> : (
        <table className="adm-table">
          <thead><tr><th>When</th><th>Request</th><th>Status</th><th>Error</th><th>Request id</th></tr></thead>
          <tbody>
            {rows.map((e, i) => (
              <tr key={`${e.request_id}-${i}`}>
                <td>{when(e.at)}</td>
                <td><code>{e.method} {e.route}</code><div className="muted small-text">{e.ms} ms</div></td>
                <td className="adm-num">{e.status}</td>
                <td className="adm-err-text">{e.error || <span className="muted">(no message)</span>}</td>
                <td><code>{e.request_id}</code></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Panel>
  );
}

const EMPTY: LibraryItemIn = { kind: "book", title: "", authors: "", year: null, url: "", note: "", topic: "", lab: "", practice: "", level: "", free: false, featured: false };

const readFile = (file: File) => new Promise<string>((resolve, reject) => {
  const reader = new FileReader();
  reader.onload = () => resolve(String(reader.result));
  reader.onerror = () => reject(new Error("The file could not be read"));
  reader.readAsDataURL(file);
});

function LibraryForm({ start, labs, image, onSave, onCancel, onRemoveImage }: {
  start: LibraryItemIn; labs: CatalogLab[]; image?: string;
  onSave: (item: LibraryItemIn, picture: string | null) => Promise<void>; onCancel?: () => void; onRemoveImage?: () => Promise<void>;
}) {
  const [item, setItem] = useState<LibraryItemIn>(start);
  const [picture, setPicture] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const set = <K extends keyof LibraryItemIn>(key: K, value: LibraryItemIn[K]) => setItem((i) => ({ ...i, [key]: value }));
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onSave(item, picture);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };
  return (
    <form className="lib-form" onSubmit={submit} aria-label={onCancel ? "Edit library item" : "Add a library item"}>
      <label>Section
        <select value={item.kind} onChange={(e) => set("kind", e.target.value as LibraryKind)}>
          {LIBRARY_TABS.map(([k, label]) => <option key={k} value={k}>{label}</option>)}
        </select>
      </label>
      <label>Title<input required maxLength={200} value={item.title} onChange={(e) => set("title", e.target.value)} /></label>
      <label>Authors<input maxLength={200} value={item.authors} onChange={(e) => set("authors", e.target.value)} /></label>
      <label>Year<input type="number" min={1000} max={2100} value={item.year ?? ""} onChange={(e) => set("year", e.target.value ? Number(e.target.value) : null)} /></label>
      <label>Link<input type="url" maxLength={500} placeholder="https://" value={item.url} onChange={(e) => set("url", e.target.value)} /></label>
      <label>Topic<input maxLength={40} placeholder="AI, Databases, Systems..." value={item.topic} onChange={(e) => set("topic", e.target.value)} /></label>
      <label>Level
        <select value={item.level} onChange={(e) => set("level", e.target.value as LibraryLevel)}>
          <option value="">(not shown)</option><option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option><option value="advanced">Advanced</option>
        </select>
      </label>
      <label>Practise it in (lab)
        <select value={item.lab} onChange={(e) => set("lab", e.target.value)}>
          <option value="">(no lab)</option>
          {labs.map((l) => <option key={l.id} value={l.id}>{l.title}</option>)}
        </select>
      </label>
      <label>Where in the lab<input maxLength={80} placeholder="chapter 6, the HNSW index" value={item.practice} onChange={(e) => set("practice", e.target.value)} /></label>
      <label className="lib-check"><input type="checkbox" checked={item.free} onChange={(e) => set("free", e.target.checked)} />Free to read online</label>
      <label className="lib-check"><input type="checkbox" checked={item.featured} onChange={(e) => set("featured", e.target.checked)} />Start here (the big card of its section)</label>
      <div className="lib-form-wide lib-form-picture">
        {(picture || image) && <img src={picture ?? libraryImage(image!)} alt="The picture shown on the Library page" />}
        <label>Picture (a book cover, a paper's first page, a view of the blog: JPEG, PNG or WebP, up to 6 MB)
          <input type="file" accept="image/jpeg,image/png,image/webp" onChange={async (e) => {
            const file = e.target.files?.[0];
            setPicture(file ? await readFile(file) : null);
          }} />
        </label>
        {image && !picture && onRemoveImage && <button className="btn btn-small" type="button" onClick={onRemoveImage}>Remove the picture</button>}
      </div>
      <label className="lib-form-wide">Why read it
        <textarea maxLength={1000} rows={3} value={item.note} onChange={(e) => set("note", e.target.value)} />
      </label>
      {error && <p className="adm-error lib-form-wide" role="alert">{error}</p>}
      <div className="lib-form-wide lib-form-actions">
        <button className="btn btn-small btn-primary" type="submit" disabled={busy}>{onCancel ? "Save changes" : "Add to the library"}</button>
        {onCancel && <button className="btn btn-small" type="button" onClick={onCancel}>Cancel</button>}
      </div>
    </form>
  );
}

function LibraryTab() {
  const [kind, setKind] = useState<LibraryKind>("book");
  const [items, error, reload] = useLoad<LibraryItem[]>(() => library.list(), []);
  const [editing, setEditing] = useState<LibraryItem | null>(null);
  const [added, setAdded] = useState(0);
  const [labs] = useLoad<CatalogLab[]>(() => api.catalog(), []);
  const rows = (items ?? []).filter((i) => i.kind === kind);
  const fields = (i: LibraryItem): LibraryItemIn => ({
    kind: i.kind, title: i.title, authors: i.authors, year: i.year, url: i.url, note: i.note, topic: i.topic,
    lab: i.lab, practice: i.practice, level: i.level, free: i.free, featured: i.featured,
  });
  const remove = async (i: LibraryItem) => {
    if (!window.confirm(`Remove "${i.title}" from the library? This cannot be undone.`)) return;
    await library.remove(i.id);
    reload();
  };
  return (
    <>
      <Panel title="Library" note="Books, research papers and tech blogs every learner sees on the Library page. Changes show at once."
        actions={
          <div className="adm-seg" role="group" aria-label="Section">
            {LIBRARY_TABS.map(([k, label]) => (
              <button key={k} aria-pressed={k === kind} onClick={() => { setKind(k); setEditing(null); }}>{label}</button>
            ))}
          </div>
        }>
        {!items ? <Loading error={error} /> : rows.length === 0 ? <p className="muted">Nothing in this section yet.</p> : (
          <table className="adm-table">
            <thead><tr><th>Order</th><th>Title</th><th>Topic</th><th>Year</th><th /></tr></thead>
            <tbody>
              {rows.map((i, n) => (
                <tr key={i.id}>
                  <td className="lib-order">
                    <button className="btn btn-small btn-ghost" aria-label={`Move ${i.title} up`} disabled={n === 0}
                      onClick={() => library.move(i.id, "up").then(reload)}>↑</button>
                    <button className="btn btn-small btn-ghost" aria-label={`Move ${i.title} down`} disabled={n === rows.length - 1}
                      onClick={() => library.move(i.id, "down").then(reload)}>↓</button>
                  </td>
                  <td>
                    {i.url ? <a href={i.url} target="_blank" rel="noopener noreferrer">{i.title}</a> : i.title}
                    <div className="muted small-text">{i.authors}{i.featured ? " · Start here" : ""}</div>
                  </td>
                  <td>{i.topic}</td>
                  <td className="adm-num">{i.year ?? ""}</td>
                  <td className="lib-row-actions">
                    <button className="btn btn-small" onClick={() => setEditing(i)}>Edit</button>
                    <button className="btn btn-small" onClick={() => remove(i)}>Remove</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>
      {editing ? (
        <Panel title={`Edit: ${editing.title}`}>
          <LibraryForm key={editing.id} labs={labs ?? []} start={fields(editing)} image={editing.image} onCancel={() => setEditing(null)}
            onRemoveImage={async () => { setEditing(await library.removeImage(editing.id)); reload(); }}
            onSave={async (item, picture) => {
              await library.change(editing.id, item);
              if (picture) await library.setImage(editing.id, picture);
              setEditing(null);
              reload();
            }} />
        </Panel>
      ) : (
        <Panel title="Add an item" note="It goes to the end of its section; move it up from the list.">
          <LibraryForm key={`${added}-${kind}`} labs={labs ?? []} start={{ ...EMPTY, kind }}
            onSave={async (item, picture) => {
              const made = await library.add(item);
              if (picture) await library.setImage(made.id, picture);
              setKind(item.kind);
              setAdded((x) => x + 1);
              reload();
            }} />
        </Panel>
      )}
    </>
  );
}

export default function AdminPage() {
  const { user } = useAuth();
  const [params, setParams] = useSearchParams();
  const tab = (TABS.find(([id]) => id === params.get("tab"))?.[0] ?? "funnel") as Tab;
  if (user && !user.is_admin) return <Navigate to="/labs" replace />;
  return (
    <div className="labs-page adm-page">
      <header className="topbar">
        <Logo to="/" />
        <span className="adm-title">Admin</span>
        <span className="spacer" />
        <ThemeButton />
        <Link className="btn btn-small btn-ghost" to="/labs">Back to labs</Link>
      </header>
      <main className="adm-main">
        <nav className="adm-tabs" aria-label="Admin sections">
          {TABS.map(([id, label]) => (
            <button key={id} aria-current={id === tab ? "page" : undefined} onClick={() => setParams({ tab: id })}>{label}</button>
          ))}
        </nav>
        {tab === "funnel" && <FunnelTab />}
        {tab === "labs" && <LabsTab />}
        {tab === "learners" && <LearnersTab />}
        {tab === "machines" && <MachinesTab />}
        {tab === "ai" && <SpendTab />}
        {tab === "errors" && <ErrorsTab />}
        {tab === "library" && <LibraryTab />}
      </main>
    </div>
  );
}
