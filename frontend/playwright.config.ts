import { defineConfig } from "@playwright/test";

// Browser tests against a running dev setup (backend on :8000, Vite on :5173, Docker with lab images).
// Uses the Chrome installed on this machine, so no browser download is needed.
export default defineConfig({
  testDir: "e2e",
  globalSetup: "./e2e/global-setup.ts",
  globalTeardown: "./e2e/global-teardown.ts",
  timeout: 180_000,
  expect: { timeout: 15_000 },
  workers: 1,
  reporter: "list",
  use: {
    baseURL: process.env.LABBOX_URL ?? "http://localhost:5173",
    channel: "chrome",
    headless: true,
    viewport: { width: 1500, height: 900 },
    permissions: ["clipboard-read", "clipboard-write"],
    trace: "retain-on-failure",
  },
});
