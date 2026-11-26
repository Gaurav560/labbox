/* The picture beside a certificate's text. Ukiyo: the lab's own woodblock print (public domain), the same one as
   on its course page and in the share image. (The current design's version shows a panel in the lab's colour.) */
import type { Certificate } from "../api";
import { LabPrint, printCredit } from "./UkiyoArt";

export default function CertArt({ cert }: { cert: Certificate }) {
  const credit = printCredit(cert.lab_id);
  return (
    <figure className="cert-art">
      <LabPrint lab={cert.lab_id} track={cert.track} />
      {credit && <figcaption className="u-print-credit">{credit}</figcaption>}
    </figure>
  );
}
