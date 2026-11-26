import { useEffect, useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import Logo from "../components/Logo";
import ThemeButton from "../components/ThemeButton";
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
  const { user, login, signup, adopt } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  // Sign-up may be closed (an invite-only site, ALLOW_SIGNUP=false): then the page is a login page and says so.
  const [signupOpen, setSignupOpen] = useState(true);
  const signupMode = signupOpen && params.get("signup") === "1"; // from "Start free" on the home page
  // Where to go after logging in: a path on this site (never another site), else the dashboard.
  const wanted = params.get("next") ?? "";
  const next = wanted.startsWith("/") && !wanted.startsWith("//") && !wanted.startsWith("/\\") ? wanted : "/labs";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [reveal, setReveal] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [providers, setProviders] = useState<string[]>([]);
  // Back from Google or GitHub: ?oauth=<one-time code> becomes a login; ?oauth_error says why it did not.
  const oauthCode = params.get("oauth");
  const [finishing, setFinishing] = useState(Boolean(oauthCode));
  useEffect(() => {
    api.authOptions().then((o) => { setSignupOpen(o.signup); setProviders(o.providers ?? []); }).catch(() => undefined);
  }, []);
  useEffect(() => {
    const failed = params.get("oauth_error");
    if (failed) setError(oauthError(failed, params.get("provider")));
    if (!oauthCode) return;
    api.oauthExchange(oauthCode)
      .then((res) => { adopt(res); navigate(res.new ? "/welcome" : next, { replace: true }); })
      .catch((e) => { setError(e instanceof Error ? e.message : "Sign-in failed. Try again."); setFinishing(false); });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (user) return <Navigate to={next} replace />;

  async function submit(action: "login" | "signup", e?: FormEvent) {
    e?.preventDefault();
    setBusy(true);
    setError("");
    try {
      await (action === "login" ? login : signup)(username.trim(), password);
      navigate(next);
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
            <span className="auth-top-links">
              <ThemeButton />
              <Link to="/" className="link small">← Home</Link>
            </span>
          </div>
          <h1>{signupMode ? "Create your account" : "Welcome back"}</h1>
          {!signupMode && <p className="muted auth-sub">Your machines are where you left them.</p>}

          {finishing && <p className="auth-finishing" role="status">Signing you in…</p>}
          {providers.length > 0 && !finishing && (
            <div className="auth-oauth">
              {providers.includes("google") && (
                <a className="auth-oauth-btn" href={`/api/auth/oauth/google/start?next=${encodeURIComponent(next)}`}>
                  <GoogleMark /> Continue with Google
                </a>
              )}
              {providers.includes("github") && (
                <a className="auth-oauth-btn" href={`/api/auth/oauth/github/start?next=${encodeURIComponent(next)}`}>
                  <GitHubMark /> Continue with GitHub
                </a>
              )}
              <p className="auth-or"><span>or with a username</span></p>
            </div>
          )}
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
          {signupOpen ? (
            <p className="auth-switch muted">
              {signupMode ? "Already have an account?" : "New to LabBox?"}{" "}
              <button type="button" className="auth-link" disabled={!ready} onClick={() => submit(other)}>
                {signupMode ? "Log in" : "Sign up"}
              </button>
            </p>
          ) : (
            <p className="auth-switch muted">Sign-up is by invitation for now. Got an invitation? Log in with the name and password you were given.</p>
          )}
          <p className="muted small auth-rules">Usernames: 3 to 32 letters, digits, dot, dash or underscore. Passwords: at least 6 characters.</p>
        </form>
        <p className="auth-legal small">
          By continuing you agree to our <Link to="/terms">Terms of Service</Link> and <Link to="/privacy">Privacy policy</Link>. Questions? Read the <Link to="/faq">FAQs</Link>.
        </p>
      </main>
    </div>
  );
}

function oauthError(reason: string, provider: string | null): string {
  const who = provider === "github" ? "GitHub" : "Google";
  if (reason === "closed") return `Sign-up is by invitation for now, and this ${who} account has no LabBox account yet.`;
  if (reason === "cancelled") return `Sign-in with ${who} was cancelled.`;
  if (reason === "expired") return "That sign-in took too long or was opened in another browser. Try again.";
  return `Could not sign you in with ${who}. Try again.`;
}

/** Google's "G" in its own four colours, as its sign-in branding asks. */
function GoogleMark() {
  return (
    <svg viewBox="0 0 48 48" width="18" height="18" aria-hidden="true">
      <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
      <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
      <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
      <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
    </svg>
  );
}

/** GitHub's mark (Simple Icons, CC0); it takes the text colour. */
function GitHubMark() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="currentColor">
      <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
    </svg>
  );
}
