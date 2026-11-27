/* A certificate as people see it (owner, 27 November): on its public page, and as the sample on the home page.
   Same file on both designs; CertArt (the picture beside the text) differs. */
import { useId, type CSSProperties } from "react";
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
          <CertStamp year={new Date(cert.issued_at).getFullYear()} />
          <span className="cert-marks">
            <a className="cert-qr" href={`/verify/${cert.id}`} title="Scan or open to verify this certificate">
              <span>Scan to verify</span>
              <img src={qrUrl(cert.id)} width={84} height={84} alt={`QR code: verify certificate ${cert.id}`} />
            </a>
          </span>
        </footer>
        {cert.hidden && <p className="cert-hidden-note">Hidden: only you can see this page.</p>}
      </div>
    </article>
  );
}

/*
 * The LabBox stamp (owner, 27 November: "place it in the certificate as a stamp", "this style": a round rubber stamp):
 * two rings, the issuer around the edge, COMPLETED across the middle, the year under it, in slightly worn ink.
 * Drawn upright, never rotated (owner's rule), and in currentColor so each design picks its ink.
 */
function CertStamp({ year }: { year: number }) {
  const id = useId().replace(/:/g, "");
  return (
    <svg className="cert-stamp" viewBox="0 0 120 120" width="96" height="96" aria-hidden="true">
      <defs>
        <path id={`${id}-top`} d="M 17,60 A 43,43 0 0,1 103,60" />
        <path id={`${id}-bottom`} d="M 11,60 A 49,49 0 0,0 109,60" />
        <filter id={`${id}-ink`} x="-5%" y="-5%" width="110%" height="110%">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="7" result="noise" />
          <feColorMatrix in="noise" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.2 2.3" result="wear" />
          <feComposite in="SourceGraphic" in2="wear" operator="in" result="worn" />
          <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="1" seed="3" result="warp" />
          <feDisplacementMap in="worn" in2="warp" scale="1.6" />
        </filter>
      </defs>
      <g filter={`url(#${id}-ink)`} fill="currentColor" stroke="currentColor">
        <circle cx="60" cy="60" r="56" fill="none" strokeWidth="3.6" />
        <circle cx="60" cy="60" r="51.5" fill="none" strokeWidth="1" />
        <circle cx="60" cy="60" r="33" fill="none" strokeWidth="1" />
        <text fontSize="9.5" fontWeight="800" letterSpacing="1.4" stroke="none" fontFamily="var(--font-text, system-ui), sans-serif">
          <textPath href={`#${id}-top`} startOffset="50%" textAnchor="middle">LABBOX BY TELUSKO</textPath>
        </text>
        <text fontSize="9" fontWeight="800" letterSpacing="1.6" stroke="none" fontFamily="var(--font-text, system-ui), sans-serif">
          <textPath href={`#${id}-bottom`} startOffset="50%" textAnchor="middle">HANDS-ON LAB</textPath>
        </text>
        <text x="13" y="63.5" textAnchor="middle" fontSize="8" stroke="none">★</text>
        <text x="107" y="63.5" textAnchor="middle" fontSize="8" stroke="none">★</text>
        <line x1="22" y1="50" x2="98" y2="50" strokeWidth="1.3" />
        <line x1="22" y1="70" x2="98" y2="70" strokeWidth="1.3" />
        <text x="60" y="65" textAnchor="middle" fontSize="14" fontWeight="900" textLength="72" lengthAdjust="spacingAndGlyphs" stroke="none"
          fontFamily="var(--font-text, system-ui), sans-serif">COMPLETED</text>
        <text x="60" y="86" textAnchor="middle" fontSize="9" fontWeight="800" letterSpacing="1.5" stroke="none"
          fontFamily="var(--font-text, system-ui), sans-serif">{year}</text>
      </g>
    </svg>
  );
}
