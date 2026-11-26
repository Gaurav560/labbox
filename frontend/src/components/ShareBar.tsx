/* Share a certificate (owner, 27 November): LinkedIn (add to profile, or a post), X, WhatsApp, Facebook, the link
   itself, and the picture. Same file on both designs. */
import { useState } from "react";
import type { Certificate } from "../api";
import { imageUrl, shareLinks, shareUrl } from "../certificate";

const ICONS: Record<string, string> = {
  "linkedin-profile": "M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1V21h-4v-5.6c0-1.34-.03-3.06-1.86-3.06-1.87 0-2.15 1.46-2.15 2.96V21H9z",
  linkedin: "M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1V21h-4v-5.6c0-1.34-.03-3.06-1.86-3.06-1.87 0-2.15 1.46-2.15 2.96V21H9z",
  x: "M17.75 3h3.07l-6.7 7.66L22 21h-6.17l-4.83-6.32L5.47 21H2.4l7.17-8.2L2 3h6.33l4.37 5.78zm-1.08 16.2h1.7L7.4 4.7H5.57z",
  whatsapp: "M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.15l-.3-.18-3 .78.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.25-.13-1.47-.73-1.7-.81-.23-.08-.4-.12-.56.13-.17.25-.64.8-.79.97-.14.17-.29.19-.54.06a6.7 6.7 0 0 1-3.3-2.9c-.25-.43.25-.4.71-1.33.08-.16.04-.3-.02-.43l-.76-1.83c-.2-.48-.4-.41-.56-.42h-.48a.92.92 0 0 0-.67.31 2.8 2.8 0 0 0-.87 2.08 4.9 4.9 0 0 0 1.02 2.6 11.2 11.2 0 0 0 4.3 3.8c1.6.69 2.23.75 3.03.63.49-.07 1.47-.6 1.68-1.18.21-.58.21-1.08.15-1.18-.06-.1-.23-.17-.48-.29z",
  facebook: "M13.5 22v-8.2h2.75l.41-3.2H13.5V8.56c0-.93.26-1.56 1.59-1.56h1.7V4.14A22.8 22.8 0 0 0 14.31 4c-2.46 0-4.14 1.5-4.14 4.25v2.35H7.4v3.2h2.77V22z",
};

export function ShareIcon({ name }: { name: string }) {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="currentColor">
      <path d={ICONS[name]} />
    </svg>
  );
}

export default function ShareBar({ cert }: { cert: Certificate }) {
  const [copied, setCopied] = useState(false);
  const links = shareLinks(cert);
  const [profile, ...rest] = links;

  async function copy() {
    try {
      await navigator.clipboard.writeText(shareUrl(cert.id));
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      window.prompt("Copy this link", shareUrl(cert.id));
    }
  }

  return (
    <section className="cert-share" aria-label="Share this certificate">
      <a className="cert-share-main" href={profile.href} target="_blank" rel="noopener noreferrer">
        <ShareIcon name={profile.key} />
        {profile.label}
      </a>
      <div className="cert-share-row">
        {rest.map((l) => (
          <a key={l.key} className="cert-share-btn" href={l.href} target="_blank" rel="noopener noreferrer">
            <ShareIcon name={l.key} />
            {l.label}
          </a>
        ))}
        <button type="button" className="cert-share-btn" onClick={copy} aria-live="polite">
          {copied ? "Link copied" : "Copy link"}
        </button>
        <a className="cert-share-btn" href={imageUrl(cert.id)} download={`labbox-certificate-${cert.id}.jpg`}>
          Download image
        </a>
      </div>
      <p className="cert-share-url">
        <span>Link</span> <code>{shareUrl(cert.id)}</code>
      </p>
    </section>
  );
}
