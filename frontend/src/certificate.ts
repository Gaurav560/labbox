/* Certificates (owner, 27 November): the address to share and the share links for LinkedIn, X, WhatsApp and
   Facebook. The shared address is /c/<id>: the backend answers it with the card tags those sites read, then sends
   people on to /certificates/<id>. Same file on both designs. */
import type { Certificate } from "./api";

export const ISSUER = "LabBox by Telusko";

export function shareUrl(id: string): string {
  return `${window.location.origin}/c/${id}`;
}

export function imageUrl(id: string): string {
  return `/api/certificates/${encodeURIComponent(id)}/image.jpg`;
}

export function issuedOn(iso: string): string {
  return new Date(iso.endsWith("Z") ? iso : `${iso}Z`).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
}

function shareText(c: Certificate): string {
  return `I completed ${c.lab_title} on ${ISSUER}: ${c.tasks_passed} hands-on tasks passed on a real machine.`;
}

export interface ShareLink { key: string; label: string; href: string }

export function shareLinks(c: Certificate): ShareLink[] {
  const url = shareUrl(c.id);
  const issued = new Date(c.issued_at.endsWith("Z") ? c.issued_at : `${c.issued_at}Z`);
  const enc = encodeURIComponent;
  // LinkedIn's "Add to profile" form for Licenses and certifications, filled in.
  const addToProfile =
    "https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME" +
    `&name=${enc(c.lab_title)}&organizationName=${enc(ISSUER)}` +
    `&issueYear=${issued.getUTCFullYear()}&issueMonth=${issued.getUTCMonth() + 1}` +
    `&certUrl=${enc(url)}&certId=${enc(c.id)}`;
  return [
    { key: "linkedin-profile", label: "Add to LinkedIn profile", href: addToProfile },
    { key: "linkedin", label: "Post on LinkedIn", href: `https://www.linkedin.com/sharing/share-offsite/?url=${enc(url)}` },
    { key: "x", label: "Post on X", href: `https://x.com/intent/post?text=${enc(shareText(c))}&url=${enc(url)}` },
    { key: "whatsapp", label: "WhatsApp", href: `https://wa.me/?text=${enc(`${shareText(c)} ${url}`)}` },
    { key: "facebook", label: "Facebook", href: `https://www.facebook.com/sharer/sharer.php?u=${enc(url)}` },
  ];
}
