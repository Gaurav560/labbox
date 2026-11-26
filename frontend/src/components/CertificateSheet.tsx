/* A certificate as people see it (owner, 27 November): on its public page, and as the sample on the home page.
   Same file on both designs; CertArt (the picture beside the text) differs. */
import type { CSSProperties } from "react";
import type { Certificate } from "../api";
import { labTone } from "../brand";
import { issuedOn, qrUrl } from "../certificate";
import CertArt from "./CertArt";

/** `sample`: shown inside another page (the home page), so the name and lab are not that page's headings. */
export default function CertificateSheet({ cert, label, sample = false }: { cert: Certificate; label?: string; sample?: boolean }) {
  const Name = sample ? "p" : "h1";
  const Lab = sample ? "p" : "h2";
  return (
    <article className="cert-sheet" style={{ "--tone": labTone(cert.lab_id) } as CSSProperties} aria-label={label ?? `Certificate ${cert.id}`}>
      <CertArt cert={cert} />
      <div className="cert-body">
        <p className="cert-kicker">Certificate of completion</p>
        <p className="cert-small">This certifies that</p>
        <Name className="cert-name">{cert.name}</Name>
        <p className="cert-small">completed the hands-on lab</p>
        <Lab className="cert-lab">{cert.lab_title}</Lab>
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
          <span className="cert-marks">
            <a className="cert-qr" href={`/verify/${cert.id}`} title="Scan or open to verify this certificate">
              <span>Scan to verify</span>
              <img src={qrUrl(cert.id)} width={84} height={84} alt={`QR code: verify certificate ${cert.id}`} />
            </a>
            <span className="cert-seal" aria-hidden="true">Lab<br />Box</span>
          </span>
        </footer>
        {cert.hidden && <p className="cert-hidden-note">Hidden: only you can see this page.</p>}
      </div>
    </article>
  );
}
