import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../auth";
import Logo from "../components/Logo";

export default function LoginPage() {
  const { user, login, signup } = useAuth();
  const navigate = useNavigate();
  const signupMode = useSearchParams()[0].get("signup") === "1"; // from "Start free" on the home page
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
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

  return (
    <div className="center-screen">
      <form className="login-card" onSubmit={(e) => submit(signupMode ? "signup" : "login", e)}>
        <Link to="/" className="link small">← Home</Link>
        <Logo />
        <h1>{signupMode ? "Create your account" : "Welcome back"}</h1>
        <p className="muted">Hands-on coding labs in your browser</p>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus autoComplete="username" />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={signupMode ? "new-password" : "current-password"}
          />
        </label>
        {error && <div className="form-error">{error}</div>}
        <div className="row">
          {signupMode ? (
            <>
              <button type="submit" className="btn btn-primary" disabled={busy || !username || !password}>Sign up</button>
              <button type="button" className="btn" disabled={busy || !username || !password} onClick={() => submit("login")}>Log in</button>
            </>
          ) : (
            <>
              <button type="submit" className="btn btn-primary" disabled={busy || !username || !password}>Log in</button>
              <button type="button" className="btn" disabled={busy || !username || !password} onClick={() => submit("signup")}>Sign up</button>
            </>
          )}
        </div>
        <p className="muted small">Usernames: 3 to 32 letters, digits, dot, dash or underscore. Passwords: at least 6 characters.</p>
      </form>
    </div>
  );
}
