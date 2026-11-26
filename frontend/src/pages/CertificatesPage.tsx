/* My certificates (owner, 27 November): every certificate the learner earned, newest first. Same file on both
   designs. */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Certificate } from "../api";
import { imageUrl, issuedOn } from "../certificate";
import Logo from "../components/Logo";
import ThemeButton from "../components/ThemeButton";

export default function CertificatesPage() {
  const [certs, setCerts] = useState<Certificate[] | null>(null);

  useEffect(() => {
    document.title = "My certificates | LabBox by Telusko";
    api.certificates().then(setCerts).catch(() => setCerts([]));
  }, []);

  return (
    <div className="cert-page">
      <header className="cert-top">
        <Logo to="/labs" />
        <span className="cert-top-links">
          <ThemeButton />
          <Link className="link small" to="/labs">Your labs</Link>
        </span>
      </header>
      <main className="cert-main">
        <h1 className="cert-list-title">My certificates</h1>
        {certs && certs.length === 0 && (
          <p className="muted">
            None yet. Pass 80% of a lab's tasks and its certificate is yours, with a link to share on LinkedIn and X.
          </p>
        )}
        <ul className="cert-list">
          {certs?.map((c) => (
            <li key={c.id}>
              <Link to={`/certificates/${c.id}`} className="cert-list-item">
                {c.hidden ? <span className="cert-list-ph">Hidden</span> : <img src={imageUrl(c.id)} alt="" width={240} height={125} loading="lazy" />}
                <span>
                  <strong>{c.lab_title}</strong>
                  <small>{issuedOn(c.issued_at)} · {c.id}{c.hidden ? " · hidden" : ""}</small>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}
