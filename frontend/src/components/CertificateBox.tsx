/* The course page's certificate box (owner, 27 November): how far the learner is from the certificate (80% of the
   lab's tasks), the claim (the full name, typed once for the first certificate), or a link to the certificate.
   Same file on both designs. */
import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, type LabCertificateStatus } from "../api";
import { issuedOn } from "../certificate";

export default function CertificateBox({ labId }: { labId: string }) {
  const navigate = useNavigate();
  const [st, setSt] = useState<LabCertificateStatus | null>(null);
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let live = true;
    api.labCertificate(labId).then((s) => { if (live) { setSt(s); setName(s.saved_name ?? ""); } }).catch(() => undefined);
    return () => { live = false; };
  }, [labId]);

  if (!st || st.tasks_total === 0) return null;

  if (st.certificate) {
    const c = st.certificate;
    return (
      <section className="cert-box is-earned" aria-label="Your certificate">
        <span className="cert-box-kicker">Certificate</span>
        <p className="cert-box-line">
          Earned on {issuedOn(c.issued_at)}, in the name of <strong>{c.name}</strong>.
        </p>
        <Link className="cert-box-go" to={`/certificates/${c.id}`}>View and share</Link>
      </section>
    );
  }

  async function claim(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const c = await api.claimCertificate(labId, st?.saved_name ? undefined : name);
      navigate(`/certificates/${c.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setBusy(false);
    }
  }

  if (st.eligible) {
    return (
      <form className="cert-box is-ready" aria-label="Get your certificate" onSubmit={claim}>
        <span className="cert-box-kicker">Certificate</span>
        <p className="cert-box-line">You finished this lab. Your certificate is ready.</p>
        {st.saved_name ? (
          <p className="cert-box-small">It will be in the name of <strong>{st.saved_name}</strong>.</p>
        ) : (
          <label className="cert-box-name">
            <span>Your full name, as it should appear on your certificates</span>
            <input value={name} onChange={(e) => setName(e.target.value)} maxLength={60} autoComplete="name" placeholder="First and last name" />
          </label>
        )}
        {error && <p className="form-error" role="alert">{error}</p>}
        <button type="submit" className="cert-box-go" disabled={busy || (!st.saved_name && name.trim().length < 2)}>
          {busy ? "One moment…" : "Get my certificate"}
        </button>
      </form>
    );
  }

  const pct = Math.min(100, Math.round((st.tasks_passed / Math.max(1, st.tasks_needed)) * 100));
  return (
    <section className="cert-box" aria-label="Certificate">
      <span className="cert-box-kicker">Certificate</span>
      <p className="cert-box-line">
        Pass {st.tasks_needed} of the {st.tasks_total} tasks to earn this lab's certificate, with a link to share on LinkedIn and X.
      </p>
      <div className="cert-box-bar" role="progressbar" aria-valuemin={0} aria-valuemax={st.tasks_needed} aria-valuenow={st.tasks_passed}>
        <div style={{ width: `${pct}%` }} />
      </div>
      <p className="cert-box-small">{st.tasks_passed} of {st.tasks_needed} so far.</p>
    </section>
  );
}
