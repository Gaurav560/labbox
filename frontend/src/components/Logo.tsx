import { Link } from "react-router-dom";

// The LabBox mark: a rounded box with a shell prompt inside ("a box with a machine in it").
export function LogoMark({ size = 28 }: { size?: number }) {
  return (
    <svg className="logo-mark" width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <rect x="1" y="1" width="30" height="30" rx="8" fill="var(--accent)" />
      <rect x="1.5" y="1.5" width="29" height="29" rx="7.5" fill="none" stroke="var(--on-accent)" strokeOpacity="0.12" />
      <path d="M9 11.5 L14.5 16 L9 20.5" fill="none" stroke="var(--on-accent)" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M17 21 H23" stroke="var(--on-accent)" strokeWidth="2.8" strokeLinecap="round" />
    </svg>
  );
}

/** Mark plus wordmark. With `to`, it links there (usually home). */
export default function Logo({ to, size = 28 }: { to?: string; size?: number }) {
  const inner = (
    <>
      <LogoMark size={size} />
      <span className="logo-word">LabBox</span>
    </>
  );
  return to ? (
    <Link to={to} className="logo" aria-label="LabBox home">{inner}</Link>
  ) : (
    <span className="logo">{inner}</span>
  );
}
