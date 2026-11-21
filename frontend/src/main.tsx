import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./auth";
import { StatsProvider } from "./stats";
import { ToastProvider } from "./components/Toasts";
import { ThemeProvider } from "./theme";
// Fonts are bundled with the app (no font CDN at runtime).
import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/jetbrains-mono/400.css";
import "@fontsource/jetbrains-mono/700.css";
import "@fontsource/caveat/500.css"; // handwriting in the hand-drawn diagrams
import "@fontsource/caveat/700.css";
import "@xterm/xterm/css/xterm.css";
import "./styles.css";

// Monaco cancels its own pending timers when the editor switches files quickly (a lesson step opening
// its file) and rejects a promise nobody awaits, named "Canceled". It is harmless; drop that one only.
window.addEventListener("unhandledrejection", (e) => {
  const r = e.reason as { name?: string; message?: string } | undefined;
  if (r && r.name === "Canceled" && r.message === "Canceled") e.preventDefault();
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <ToastProvider>
          <AuthProvider>
            <StatsProvider>
              <App />
            </StatsProvider>
          </AuthProvider>
        </ToastProvider>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
);
