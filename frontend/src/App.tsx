import { lazy, Suspense, type ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import LabsPage from "./pages/LabsPage";
import LoginPage from "./pages/LoginPage";

// The lab page pulls in Monaco and xterm, so load it only when needed.
const LabPage = lazy(() => import("./pages/LabPage"));

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="center-screen">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/labs" element={<RequireAuth><LabsPage /></RequireAuth>} />
      <Route
        path="/labs/:labId"
        element={<RequireAuth><Suspense fallback={<div className="center-screen">Loading...</div>}><LabPage /></Suspense></RequireAuth>}
      />
      <Route path="*" element={<Navigate to="/labs" replace />} />
    </Routes>
  );
}
