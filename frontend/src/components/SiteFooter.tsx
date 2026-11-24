import { Link } from "react-router-dom";
import { SITE } from "../site";

/** Links to the FAQ and the legal pages, shown at the bottom of public pages. */
export function SiteLinks({ className = "", faq = true }: { className?: string; faq?: boolean }) {
  return (
    <nav aria-label="About" className={`site-links ${className}`}>
      <Link to="/library">Premium Reads</Link>
      {faq && <Link to="/faq">FAQs</Link>}
      <Link to="/privacy">Privacy policy</Link>
      <Link to="/terms">Terms of Service</Link>
    </nav>
  );
}

export function Copyright() {
  return <span className="muted small-text">© {new Date().getFullYear()} {SITE.company}. {SITE.product} is a product of {SITE.company}.</span>;
}
