import { lazy, Suspense, type ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import HomePage from "./pages/HomePage";
import { FaqPage, PrivacyPage, TermsPage } from "./pages/InfoPages";
import LabsPage from "./pages/LabsPage";
import LoginPage from "./pages/LoginPage";
import OnboardingPage from "./pages/OnboardingPage";

// The lab page pulls in Monaco and xterm, so load it only when needed.
const LabPage = lazy(() => import("./pages/LabPage"));
const TrackPage = lazy(() => import("./pages/TrackPage")); // React Flow is only needed here

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="center-screen">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
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
      <Route path="*" element={<Navigate to="/labs" replace />} />
    </Routes>
  );
}
