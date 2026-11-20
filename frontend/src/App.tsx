import { lazy, Suspense, type ReactNode } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./auth";
import HomePage from "./pages/HomePage";
import { FaqPage, PrivacyPage, TermsPage } from "./pages/InfoPages";
import LabsPage from "./pages/LabsPage";
import LoginPage from "./pages/LoginPage";
import OnboardingPage from "./pages/OnboardingPage";

// A page's code is loaded when first needed. If that fails (Chrome drops downloads when the network
// changes, or a deploy replaced the files), try again, then reload the page once (at most every 30 s).
function lazyPage<T extends { default: React.ComponentType }>(load: () => Promise<T>) {
  return lazy(async () => {
    try {
      return await load();
    } catch {
      await new Promise((r) => setTimeout(r, 1000));
      try {
        return await load();
      } catch (e) {
        const KEY = "labbox.reloadedForCode";
        let last = 0;
        try { last = Number(sessionStorage.getItem(KEY) || 0); } catch { /* storage blocked */ }
        if (Date.now() - last > 30_000) {
          try { sessionStorage.setItem(KEY, String(Date.now())); } catch { /* storage blocked */ }
          window.location.reload();
          return new Promise<T>(() => {}); // the reload takes over
        }
        throw e;
      }
    }
  });
}

// The lab page pulls in Monaco and xterm, so load it only when needed.
const LabPage = lazyPage(() => import("./pages/LabPage"));
const TrackPage = lazyPage(() => import("./pages/TrackPage")); // React Flow is only needed here
const AdminPage = lazyPage(() => import("./pages/AdminPage")); // only admins ever load it

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="center-screen">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeOrDashboard />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/faq" element={<FaqPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route path="/labs" element={<RequireAuth><LabsPage /></RequireAuth>} />
      <Route
        path="/labs/:labId"
        element={<RequireAuth><Suspense fallback={<div className="center-screen">Loading...</div>}><LabPage /></Suspense></RequireAuth>}
      />
      <Route path="/welcome" element={<RequireAuth><OnboardingPage /></RequireAuth>} />
      <Route
        path="/tracks/:track"
        element={<RequireAuth><Suspense fallback={<div className="center-screen">Loading...</div>}><TrackPage /></Suspense></RequireAuth>}
      />
      <Route
        path="/admin"
        element={<RequireAuth><Suspense fallback={<div className="center-screen">Loading...</div>}><AdminPage /></Suspense></RequireAuth>}
      />
      <Route path="*" element={<Navigate to="/labs" replace />} />
    </Routes>
  );
}

/** Signed-in learners land on their dashboard; the marketing page stays at /?home for everyone. */
function HomeOrDashboard() {
  const { user, loading } = useAuth();
  const { search } = useLocation();
  if (loading) return null;
  if (user && !new URLSearchParams(search).has("home")) return <Navigate to="/labs" replace />;
  return <HomePage />;
}
