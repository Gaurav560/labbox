import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import { useTyped } from "../components/useTyped";

// A lab run, typed out in the showcase terminal. "$ " lines are typed, the rest appear at once.
const SCRIPT = [
  "$ labbox start redis-in-practice",
  "✓ machine ready in 2.1 s",
  "$ redis-cli SET cookie:orders 42",
  "OK",
  "$ check",
  "✓ 3 of 3 passed  +60 XP  🔥 5 day streak",
];

function TermLine({ text }: { text: string }) {
  if (text.startsWith("$ ")) {
    return <div><span className="auth-prompt">learner:~$</span> {text.slice(2)}</div>;
  }
  return <div className={text.startsWith("✓") ? "auth-ok" : "auth-out"}>{text}</div>;
}

function Showcase() {
  const { shown, typing } = useTyped(SCRIPT);
  return (
    <aside className="auth-show" aria-hidden="true">
      <div className="auth-glow auth-glow-a" />
      <div className="auth-glow auth-glow-b" />
      <div className="auth-grid" />
      <div className="auth-pitch">
        <p className="auth-eyebrow">Real machines. Real code.</p>
        <h2>Break it. Fix it.<br />Actually learn it.</h2>
        <div className="auth-term">
          <div className="auth-term-bar"><span /><span /><span /></div>
          <div className="auth-term-body">
            {shown.map((l, i) => <TermLine key={i} text={l} />)}
            {typing && <TermLine text={typing} />}
            <span className="auth-cursor" />
          </div>
        </div>
      </div>
    </aside>
  );
}

export default function LoginPage() {
  const { user, login, signup } = useAuth();
  const navigate = useNavigate();
  const signupMode = useSearchParams()[0].get("signup") === "1"; // from "Start free" on the home page
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [reveal, setReveal] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/labs" replace />;

  async function submit(action: "login" | "signup", e?: FormEvent) {
    e?.preventDefault();
    setBusy(true);
    setError("");
    try {
      await (action === "login" ? login : signup)(username.trim(), password);
      navigate("/labs");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  const ready = !busy && !!username && !!password;
  const primary = signupMode ? "signup" : "login";
  const other = signupMode ? "login" : "signup";

  return (
    <div className="auth">
      <Showcase />
      <main className="auth-main">
        <form className="auth-card" onSubmit={(e) => submit(primary, e)}>
          <div className="auth-top">
            <Logo to="/" />
            <Link to="/" className="link small">← Home</Link>
          </div>
          <h1>{signupMode ? "Create your account" : "Welcome back"}</h1>
          <p className="muted auth-sub">
            {signupMode ? "Your first win is about three minutes away." : "Your machines are where you left them."}
          </p>

          <label className="auth-field">
            <span>Username</span>
            <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus autoComplete="username" placeholder="asha" spellCheck={false} />
          </label>
          <label className="auth-field">
            <span>Password</span>
            <div className="auth-pass">
              <input
                type={reveal ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={signupMode ? "new-password" : "current-password"}
                placeholder="At least 6 characters"
              />
              <button type="button" className="auth-reveal" onClick={() => setReveal(!reveal)} aria-pressed={reveal} title={reveal ? "Hide" : "Show"}>
                {reveal ? "Hide" : "Show"}
              </button>
            </div>
          </label>

          {error && <div className="form-error" role="alert">{error}</div>}

          <button type="submit" className="btn btn-primary auth-go" disabled={!ready}>
            {busy ? "One moment…" : signupMode ? "Sign up" : "Log in"}
          </button>
          <p className="auth-switch muted">
            {signupMode ? "Already have an account?" : "New to LabBox?"}{" "}
            <button type="button" className="auth-link" disabled={!ready} onClick={() => submit(other)}>
              {signupMode ? "Log in" : "Sign up"}
            </button>
          </p>
          <p className="muted small auth-rules">Usernames: 3 to 32 letters, digits, dot, dash or underscore. Passwords: at least 6 characters.</p>
        </form>
        <p className="auth-legal small">
          By continuing you agree to our <Link to="/terms">Terms of Service</Link> and <Link to="/privacy">Privacy policy</Link>. Questions? Read the <Link to="/faq">FAQs</Link>.
        </p>
      </main>
    </div>
  );
}
