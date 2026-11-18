import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type LabSummary } from "../api";
import { useAuth } from "../auth";
import { useToast } from "../components/Toasts";

export default function LabsPage() {
  const { user, logout } = useAuth();
  const toast = useToast();
  const [labs, setLabs] = useState<LabSummary[] | null>(null);

  useEffect(() => {
    api.labs().then(setLabs).catch((e) => toast(e.message));
  }, [toast]);

  return (
    <div className="labs-page">
      <header className="topbar">
        <span className="brand">LabBox</span>
        <span className="spacer" />
        <span className="muted">{user?.username}</span>
        <button className="btn btn-small" onClick={logout}>Log out</button>
      </header>
      <main className="labs-main">
        <h2>Your labs</h2>
        {!labs && <p className="muted">Loading...</p>}
        <div className="lab-grid">
          {labs?.map((lab) => {
            const pct = lab.progress.total_tasks ? (100 * lab.progress.passed_tasks) / lab.progress.total_tasks : 0;
            return (
              <div key={lab.id} className="lab-card">
                <div className="row">
                  <h3>{lab.title}</h3>
                  <span className={`badge badge-${lab.language}`}>{lab.language}</span>
                </div>
                <p className="muted">{lab.description}</p>
                <div className="progress" title={`${lab.progress.passed_tasks} of ${lab.progress.total_tasks} tasks`}>
                  <div className="progress-fill" style={{ width: `${pct}%` }} />
                </div>
                <div className="row">
                  <span className="muted small">
                    {lab.progress.passed_tasks} / {lab.progress.total_tasks} tasks · {lab.chapter_count} chapter{lab.chapter_count === 1 ? "" : "s"}
                  </span>
                  <Link className="btn btn-primary" to={`/labs/${lab.id}`}>Open</Link>
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
