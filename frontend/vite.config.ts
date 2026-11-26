import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": { target: "http://localhost:8000", xfwd: true }, // xfwd: the backend sees the address used (sign-in redirects)
      "/ws": { target: "ws://localhost:8000", ws: true },
      "/preview": { target: "http://localhost:8000", ws: true },
      "/ide": { target: "http://localhost:8000", ws: true },
      "/ide-fonts": "http://localhost:8000",
      "/c/": { target: "http://localhost:8000", xfwd: true }, // certificate share pages (card tags for LinkedIn and X)
    },
  },
});
