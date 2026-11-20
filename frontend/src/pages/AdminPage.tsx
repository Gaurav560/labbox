import { useCallback, useEffect, useState, type ReactNode } from "react";
import { Link, Navigate, useSearchParams } from "react-router-dom";
import {
  admin, ApiError,
  type AdminError, type AdminLabReport, type AdminLabRow, type AdminLearner, type AdminMachine, type AdminSpend, type AdminWindow, type FunnelStep,
} from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";

// The admin area (Phase J): what to improve, and what is running. Only for accounts with is_admin;
// the backend refuses everyone else, this page only hides itself.

const TABS = [
  ["funnel", "Funnel"],
  ["labs", "Labs"],
  ["learners", "Learners"],
  ["machines", "Machines"],
  ["ai", "AI spend"],
  ["errors", "Errors"],
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
      </main>
    </div>
  );
}
