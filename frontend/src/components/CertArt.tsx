/* The picture beside a certificate's text. Current design: a panel in the lab's own colour with the LabBox mark.
   (Ukiyo's version of this file shows the lab's woodblock print instead.) */
import type { Certificate } from "../api";
import { LogoMark } from "./Logo";

export default function CertArt({ cert }: { cert: Certificate }) {
  return (
    <div className="cert-art" aria-hidden="true">
      <LogoMark />
      <span>{cert.lab_title}</span>
    </div>
  );
}
