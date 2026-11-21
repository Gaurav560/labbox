import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, type Onboarding, type OnboardingResult } from "../api";
import Logo from "../components/Logo";
import { useToast } from "../components/Toasts";
import LessonMarkdown from "../lesson/LessonMarkdown";
import { useStats } from "../stats";
import ThemeButton from "../components/ThemeButton";

// First 60 seconds: pick a goal, answer 3 quick questions, land in the first lab.
export default function OnboardingPage() {
  const navigate = useNavigate();
  const toast = useToast();
  const { refresh } = useStats();
  const [data, setData] = useState<Onboarding | null>(null);
  const [goal, setGoal] = useState<string | null>(null);
  const [answers, setAnswers] = useState<(number | null)[]>([]);
  const [result, setResult] = useState<OnboardingResult | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api
      .onboarding()
      .then((d) => {
        setData(d);
        setAnswers(d.placement.map(() => null));
      })
      .catch((e) => toast(e.message));
  }, [toast]);

  async function finish() {
    if (!goal || answers.some((a) => a === null)) return;
    setBusy(true);
    try {
      setResult(await api.finishOnboarding(goal, answers as number[]));
      await refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function skip() {
    await api.skipOnboarding().catch(() => {});
    await refresh();
    navigate("/labs", { replace: true });
  }

  const step = result ? 3 : goal ? 2 : 1;

  return (
    <div className="onboarding">
      <header className="topbar">
        <Logo to="/" />
        <span className="spacer" />
        <ThemeButton />
        <span className="muted small-text">Step {step} of 3</span>
        {!result && <button className="btn btn-small btn-ghost" onClick={skip}>Skip</button>}
      </header>
      <main className="onboarding-main">
        {!data && <p className="muted">Loading...</p>}

        {data && step === 1 && (
          <section aria-labelledby="ob-goal">
            <h1 id="ob-goal">What do you want to get better at?</h1>
            <p className="muted">You will be writing real code in about a minute.</p>
            <div className="goal-grid">
              {data.goals.map((g) => (
                <button key={g.id} className="goal-card" onClick={() => setGoal(g.id)}>
                  <strong>{g.title}</strong>
                  <span className="muted">{g.blurb}</span>
                </button>
              ))}
            </div>
          </section>
        )}

        {data && step === 2 && (
          <section aria-labelledby="ob-level">
            <h1 id="ob-level">How much do you know?</h1>
            <p className="muted">Three quick questions. Guessing is fine: this only decides where you start.</p>
            {data.placement.map((q, qi) => (
              <div key={qi} className="placement-q">
                <div className="predict-question" id={`pq-${qi}`}>
                  <LessonMarkdown markdown={q.question} />
                </div>
                <div className="predict-options" role="radiogroup" aria-labelledby={`pq-${qi}`}>
                  {q.options.map((o, oi) => (
                    <button
                      key={oi}
                      role="radio"
                      aria-checked={answers[qi] === oi}
                      className={`predict-option ${answers[qi] === oi ? "is-picked" : ""}`}
                      onClick={() => setAnswers((a) => a.map((x, i) => (i === qi ? oi : x)))}
                    >
                      <span className="predict-mark" aria-hidden="true">{String.fromCharCode(65 + oi)}</span>
                      <LessonMarkdown markdown={o} inline />
                    </button>
                  ))}
                </div>
              </div>
            ))}
            <div className="row">
              <button className="btn" onClick={() => setGoal(null)}>← Back</button>
              <button className="btn btn-primary" onClick={finish} disabled={busy || answers.some((a) => a === null)}>
                {busy ? "..." : "See my path →"}
              </button>
            </div>
          </section>
        )}

        {data && result && (
          <section aria-labelledby="ob-path">
            <h1 id="ob-path">Your path</h1>
            <p>
              You got <strong>{result.score} of {result.results.length}</strong>. Starting level: <strong>{result.level}</strong>.
            </p>
            {result.note && <p className="callout callout-tip">{result.note}</p>}
            <div className="start-card">
              <div>
                <div className="muted small-text">First lab</div>
                <strong className="start-title">{result.start.title}</strong>
              </div>
              <button className="btn btn-primary" onClick={() => navigate(`/labs/${result.start.lab_id}`)} autoFocus>
                Start coding →
              </button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
