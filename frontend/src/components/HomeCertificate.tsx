/* The home page's certificate section (owner, 27 November: "add a certificate section on the home page, and that it
   is shareable on any platform, the link made by itself"). A sample certificate drawn by the same component as the
   real page, and what happens when a lab is finished. Same file on both designs; each styles it. */
import type { Certificate } from "../api";
import CertificateSheet from "./CertificateSheet";
import { ShareIcon } from "./ShareBar";

const SAMPLE: Certificate = {
  id: "7KQ2M9XA",
  lab_id: "langchain",
  lab_title: "LangChain",
  lab_subtitle: "Build Navin, the help desk of a farmers' cooperative, with LangChain and Python.",
  track: "ai",
  name: "Meera Iyer",
  tasks_passed: 44,
  tasks_total: 54,
  chapters_total: 27,
  skills: ["How language models work", "Calling a model", "Agents", "Knowledge and MCP", "Production"],
  issued_at: new Date().toISOString(),
  issuer: "LabBox by Telusko",
  hidden: false,
  name_corrected: false,
  mine: false,
};

// The rest of what a certificate is moved to the FAQ (owner, 27 November); LinkedIn and sharing stay here.
const POINTS = [
  { title: "One click to LinkedIn", text: "Adds it to Licenses and certifications, with the certificate's ID and link filled in." },
];

const PLATFORMS = [
  { key: "linkedin", label: "LinkedIn" },
  { key: "x", label: "X" },
  { key: "whatsapp", label: "WhatsApp" },
  { key: "facebook", label: "Facebook" },
];

export default function HomeCertificate() {
  return (
    <div className="hc">
      <div className="hc-sample">
        <CertificateSheet cert={SAMPLE} label="A sample certificate" sample />
        <p className="hc-link" aria-label="Its link">
          <span className="hc-link-dot" aria-hidden="true" />
          <span>{window.location.host}/c/<strong>7KQ2M9XA</strong></span>
        </p>
      </div>
      <div className="hc-text">
        <ul className="hc-points">
          {POINTS.map((p) => (
            <li key={p.title}><strong>{p.title}</strong><span>{p.text}</span></li>
          ))}
        </ul>
        <p className="hc-share-title">Share it anywhere a link goes</p>
        <ul className="hc-platforms" aria-label="Share on">
          {PLATFORMS.map((p) => (
            <li key={p.key}><ShareIcon name={p.key} /> {p.label}</li>
          ))}
          <li>Email</li>
          <li>Your CV</li>
          <li>Any page</li>
        </ul>
        <p className="hc-note">On LinkedIn, X and WhatsApp the link opens as a card with the certificate's picture.</p>
      </div>
    </div>
  );
}
