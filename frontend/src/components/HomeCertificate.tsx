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

// Only the sharing logos stay here (owner, 27 November: the LinkedIn point removed; the rest is in the FAQ).

// Real logos in their own colours, no boxes (owner, 27 November: "logos").
const PLATFORMS = [
  { key: "linkedin", label: "LinkedIn" },
  { key: "x", label: "X" },
  { key: "whatsapp", label: "WhatsApp" },
  { key: "facebook", label: "Facebook" },
  { key: "email", label: "Email" },
  { key: "link", label: "Any page" },
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
        <p className="hc-share-title">Share it anywhere a link goes</p>
        <ul className="hc-platforms" aria-label="Share on">
          {PLATFORMS.map((p) => (
            <li key={p.key} className={`hc-logo is-${p.key}`}><span className="hc-logo-mark"><ShareIcon name={p.key} /></span>{p.label}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
