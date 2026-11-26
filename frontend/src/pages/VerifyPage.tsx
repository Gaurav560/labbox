/* Verify a certificate (owner, 27 November: "a verifiable QR code that verifies the authenticity of the certificate
   from the backend server"). A certificate's QR code opens /verify/<id>; this page asks the server what it has on
   record for that id and shows exactly that, so a picture that was edited shows up as a mismatch. Anyone can also
   type an id. Public, no login. Same file on both designs. */
import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, type Verification } from "../api";
import { issuedOn } from "../certificate";
import Logo from "../components/Logo";
import ThemeButton from "../components/ThemeButton";

export default function VerifyPage() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const [typed, setTyped] = useState(id);
  const [result, setResult] = useState<Verification | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    document.title = "Verify a certificate | LabBox by Telusko";
    setResult(null);
    setFailed(false);
    setTyped(id);
    if (!id) return;
    let live = true;
    api.verifyCertificate(id).then((v) => { if (live) setResult(v); }).catch(() => { if (live) setFailed(true); });
    return () => { live = false; };
  }, [id]);

  function check(e: FormEvent) {
    e.preventDefault();
    const clean = typed.replace(/[^A-Za-z0-9]/g, "").toUpperCase();
    if (clean) navigate(`/verify/${clean}`);
  }

  return (
    <div className="cert-page">
      <header className="cert-top">
        <Logo to="/" />
        <span className="cert-top-links">
          <ThemeButton />
          <Link className="link small" to="/">About LabBox</Link>
        </span>
      </header>
      <main className="cert-main verify-main">
        <h1 className="verify-title">Verify a certificate</h1>
        <p className="muted verify-lead">
          Every LabBox certificate has an 8-character ID and a QR code. This page shows what our server has on record for an
          ID, straight from the database, not from any picture.
        </p>
        <form className="verify-form" onSubmit={check} aria-label="Check a certificate ID">
          <input value={typed} onChange={(e) => setTyped(e.target.value)} placeholder="Certificate ID, e.g. 7KQ2M9XA"
            maxLength={16} autoComplete="off" spellCheck={false} aria-label="Certificate ID" />
          <button type="submit" className="cert-box-go" disabled={!typed.trim()}>Check</button>
        </form>
        {failed && <p className="form-error" role="alert">Could not reach the server. Try again in a moment.</p>}
        {result && <Result v={result} />}
      </main>
    </div>
  );
}

function Result({ v }: { v: Verification }) {
  if (v.status === "verified") {
    return (
      <section className="verify-card is-ok" aria-label="Verified">
        <p className="verify-badge"><span aria-hidden="true">✓</span> Verified by {v.issuer}</p>
        <dl className="verify-facts">
          <div><dt>Name</dt><dd>{v.name}</dd></div>
          <div><dt>Lab</dt><dd>{v.lab_title}</dd></div>
          <div><dt>Issued</dt><dd>{v.issued_at ? issuedOn(v.issued_at) : ""}</dd></div>
          <div><dt>Tasks passed</dt><dd>{v.tasks_passed} of {v.tasks_total}, on a real machine</dd></div>
          <div><dt>Certificate</dt><dd><code>{v.id}</code></dd></div>
        </dl>
        <p className="verify-warn">
          If the certificate you were shown says anything different (another name, lab or date), it was altered and is not genuine.
        </p>
        <Link className="link small" to={`/certificates/${v.id}`}>See the certificate</Link>
        <p className="muted small verify-checked">Checked with our server just now.</p>
      </section>
    );
  }
  if (v.status === "private") {
    return (
      <section className="verify-card is-private" aria-label="Genuine, private">
        <p className="verify-badge"><span aria-hidden="true">✓</span> Genuine, and kept private</p>
        <p>
          Certificate <code>{v.id}</code> was issued by {v.issuer}, but its owner has chosen to hide it, so its details are
          not shown. Ask them to make it public if you need to see them.
        </p>
      </section>
    );
  }
  if (v.status === "sample") {
    return (
      <section className="verify-card is-sample" aria-label="Sample">
        <p className="verify-badge">This is the sample certificate</p>
        <p>
          <code>{v.id}</code> is the example on our home page; it was never issued to anyone. Real certificates are made when a
          learner passes 80% of a lab's tasks.
        </p>
      </section>
    );
  }
  return (
    <section className="verify-card is-bad" aria-label="Not found">
      <p className="verify-badge"><span aria-hidden="true">✗</span> No certificate with this ID</p>
      <p>
        {v.id ? <>We have never issued a certificate <code>{v.id}</code>.</> : "That is not a certificate ID."} Check the ID for a
        typing mistake (IDs never contain 0, 1, I, L, O or U); if it is right, the certificate is not genuine.
      </p>
    </section>
  );
}
