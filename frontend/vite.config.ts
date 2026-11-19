import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
      "/ws": { target: "ws://localhost:8000", ws: true },
      "/preview": { target: "http://localhost:8000", ws: true },
      "/ide": { target: "http://localhost:8000", ws: true },
      "/ide-fonts": "http://localhost:8000",
    },
  },
});
