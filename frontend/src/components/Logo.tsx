import { Link } from "react-router-dom";
import { SITE } from "../site";

// The LabBox mark in the Ukiyo design: a vermilion hanko (a carved seal), square with a carved border, holding the
// shell prompt that has always been LabBox's sign ("a box with a machine in it"). A faint stamp texture keeps it
// from looking like a flat icon.
export function LogoMark({ size = 28 }: { size?: number }) {
  return (
    <svg className="logo-mark" width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <defs>
        <filter id="lb-stamp" x="-5%" y="-5%" width="110%" height="110%">
          <feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="7" result="n" />
          <feColorMatrix in="n" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -3 2.45" result="holes" />
          <feComposite in="SourceGraphic" in2="holes" operator="in" />
        </filter>
      </defs>
      <g filter="url(#lb-stamp)">
        <rect x="1.5" y="1.5" width="29" height="29" rx="3.5" fill="var(--brand-red)" />
        <rect x="4" y="4" width="24" height="24" rx="1.5" fill="none" stroke="#fff" strokeWidth="1.1" strokeOpacity=".9" />
        <path d="M9.5 11.5 L14.5 16 L9.5 20.5" fill="none" stroke="#fff" strokeWidth="2.6" strokeLinecap="square" strokeLinejoin="miter" />
        <path d="M16.8 21 H22.5" stroke="#fff" strokeWidth="2.6" strokeLinecap="square" />
      </g>
    </svg>
  );
}

/** Mark plus wordmark. With `to`, it links there (usually home). */
export default function Logo({ to, size = 28 }: { to?: string; size?: number }) {
  const inner = (
    <>
      <LogoMark size={size} />
      <span className="logo-text">
        <span className="logo-word">{SITE.product}</span>
        <span className="logo-by"><span className="logo-by-word">by</span> {SITE.company}</span>
      </span>
    </>
  );
  return to ? (
    <Link to={to} className="logo" aria-label={`${SITE.full} home`}>{inner}</Link>
  ) : (
    <span className="logo">{inner}</span>
  );
}
