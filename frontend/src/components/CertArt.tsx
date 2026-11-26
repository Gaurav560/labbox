/* The picture beside a certificate's text. Ukiyo: a woodblock print (public domain). A lab may have its own
   certificate print in public/ukiyo/certs/ (owner, 27 November: LangChain's is Hiroshige's Lake Biwa by moonlight,
   in place of the cooper in its course print); otherwise the lab's own print, as on its course page. The backend's
   share image (app/certificates.py) looks for the same files. (The current design's version shows a panel in the
   lab's colour.) */
import type { Certificate } from "../api";
import { LabPrint, printCredit } from "./UkiyoArt";

/** Certificate-only prints, stored in public/ukiyo/certs/<lab>.webp. */
export const CERT_PRINTS: Record<string, { credit: string; source: string }> = {
  langchain: {
    credit: "Utagawa Hiroshige, Lake Biwa and Ishiyama Temple, Ōmi Province, 1853",
    source: "San Diego Museum of Art, 1957.295, public domain (Wikimedia Commons)",
  },
};

export default function CertArt({ cert }: { cert: Certificate }) {
  const own = CERT_PRINTS[cert.lab_id];
  const credit = own?.credit ?? printCredit(cert.lab_id);
  return (
    <figure className="cert-art">
      {own
        ? <img className="u-print u-labprint" src={`/ukiyo/certs/${cert.lab_id}.webp`} alt={`Woodblock print: ${own.credit}`} />
        : <LabPrint lab={cert.lab_id} track={cert.track} />}
      {credit && <figcaption className="u-print-credit">{credit}</figcaption>}
    </figure>
  );
}
