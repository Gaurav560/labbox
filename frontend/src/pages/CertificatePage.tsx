/* A certificate's public page (owner, 27 November), /certificates/<id>: anyone with the link may open it, no login.
   Its learner also sees the switch to hide it and the one name correction. The address people share is /c/<id>
   (see certificate.ts). Same file on both designs; only CertArt (the picture beside the text) differs. */
import { useEffect, useState, type CSSProperties, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError, type Certificate } from "../api";
import { useAuth } from "../auth";
import { labTone } from "../brand";
import { issuedOn } from "../certificate";
import CertArt from "../components/CertArt";
import Logo from "../components/Logo";
import ShareBar from "../components/ShareBar";
import ThemeButton from "../components/ThemeButton";

export default function CertificatePage() {
  const { id = "" } = useParams();
  const { user } = useAuth();
  const [cert, setCert] = useState<Certificate | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    let live = true;
    api.certificate(id)
      .then((c) => { if (live) setCert(c); })
      .catch((e) => { if (live && e instanceof ApiError) setMissing(true); });
    return () => { live = false; };
  }, [id, user?.id]);

  useEffect(() => {
    if (cert) document.title = `${cert.name}: ${cert.lab_title} | LabBox by Telusko`;
  }, [cert]);

  return (
    <div className="cert-page">
      <header className="cert-top">
        <Logo to="/" />
        <span className="cert-top-links">
          <ThemeButton />
          {user ? <Link className="link small" to="/certificates">My certificates</Link> : <Link className="link small" to="/">About LabBox</Link>}
        </span>
      </header>
      <main className="cert-main">
        {missing && (
          <section className="cert-missing">
            <h1>This certificate is not available</h1>
            <p className="muted">The link may be mistyped, or its owner has hidden it.</p>
            <Link className="link" to="/">Go to LabBox</Link>
          </section>
        )}
        {cert && <Sheet cert={cert} />}
        {cert && !cert.hidden && <ShareBar cert={cert} />}
        {cert?.mine && <OwnerControls cert={cert} onChange={setCert} />}
        {cert && !cert.mine && (
          <p className="cert-verify muted small">
            Issued by LabBox by Telusko on {issuedOn(cert.issued_at)}. The address of this page is the proof: certificate {cert.id}.
          </p>
        )}
      </main>
    </div>
  );
}

function Sheet({ cert }: { cert: Certificate }) {
  return (
    <article className="cert-sheet" style={{ "--tone": labTone(cert.lab_id) } as CSSProperties} aria-label={`Certificate ${cert.id}`}>
      <CertArt cert={cert} />
      <div className="cert-body">
        <p className="cert-kicker">Certificate of completion</p>
        <p className="cert-small">This certifies that</p>
        <h1 className="cert-name">{cert.name}</h1>
        <p className="cert-small">completed the hands-on lab</p>
        <h2 className="cert-lab">{cert.lab_title}</h2>
        {cert.lab_subtitle && <p className="cert-sub">{cert.lab_subtitle}</p>}
        <p className="cert-facts">
          {cert.tasks_passed} of {cert.tasks_total} tasks passed on a real machine · {cert.chapters_total} chapters
        </p>
        {cert.skills.length > 0 && (
          <ul className="cert-skills" aria-label="Skills">
            {cert.skills.map((s) => <li key={s}>{s}</li>)}
          </ul>
        )}
        <footer className="cert-foot">
          <div>
            <strong>{issuedOn(cert.issued_at)}</strong>
            <span>Certificate {cert.id}</span>
            <span className="cert-issuer">{cert.issuer}</span>
          </div>
          <span className="cert-seal" aria-hidden="true">Lab<br />Box</span>
        </footer>
        {cert.hidden && <p className="cert-hidden-note">Hidden: only you can see this page.</p>}
      </div>
    </article>
  );
}

function OwnerControls({ cert, onChange }: { cert: Certificate; onChange: (c: Certificate) => void }) {
  const [fixing, setFixing] = useState(false);
  const [name, setName] = useState(cert.name);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function save(body: { name?: string; hidden?: boolean }) {
    setBusy(true);
    setError("");
    try {
      onChange(await api.changeCertificate(cert.id, body));
      setFixing(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    void save({ name });
  }

  return (
    <section className="cert-owner" aria-label="Your certificate">
      <p className="cert-owner-state">
        {cert.hidden ? "Hidden: its link shows \"not available\" to everyone but you." : "Public: anyone with the link can see it."}{" "}
        <button type="button" className="link small" disabled={busy} onClick={() => void save({ hidden: !cert.hidden })}>
          {cert.hidden ? "Make it public again" : "Hide this certificate"}
        </button>
      </p>
      {!cert.name_corrected && !fixing && (
        <button type="button" className="link small" onClick={() => setFixing(true)}>Fix a mistake in the name (once)</button>
      )}
      {fixing && (
        <form className="cert-owner-fix" onSubmit={submit}>
          <input value={name} onChange={(e) => setName(e.target.value)} maxLength={60} aria-label="Name on the certificate" />
          <button type="submit" className="cert-box-go" disabled={busy || name.trim() === cert.name}>Save the name</button>
          <button type="button" className="link small" onClick={() => { setFixing(false); setName(cert.name); }}>Cancel</button>
          <p className="muted small">You can correct it once; after that it is final. Later certificates use it too.</p>
        </form>
      )}
      {error && <p className="form-error" role="alert">{error}</p>}
    </section>
  );
}
