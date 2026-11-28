/*
 * Phase D acceptance in the browser: the Preview tab shows a learner's FastAPI app (port 8000)
 * and Spring Boot app (port 8080), and the Postgres incident lab runs end to end (setup, timer,
 * a fix from the terminal, a live Check, the incident bonus).
 */
import { execFileSync } from "node:child_process";
import { expect, test, type Page } from "@playwright/test";
import { signIn } from "./signin";

test.describe.configure({ mode: "serial" });

const username = `d${Date.now() % 1_000_000_000}`;
let userId: number | null = null;
let auth: Record<string, string> = {};

test.afterAll(() => {
  if (userId === null) return;
  const ids = execFileSync("docker", ["ps", "-aq", "--filter", `label=labbox.user=${userId}`]).toString().split(/\s+/).filter(Boolean);
  if (ids.length) execFileSync("docker", ["rm", "-f", ...ids]);
  const nets = execFileSync("docker", ["network", "ls", "-q", "--filter", `name=labnet-u${userId}-`]).toString().split(/\s+/).filter(Boolean);
  for (const n of nets) execFileSync("docker", ["network", "rm", n]);
});

async function login(page: Page, first = false) {
  await signIn(page, username, { first });
  if (first) await page.getByRole("button", { name: "Skip" }).click();
  await expect(page.getByText("Your labs")).toBeVisible();
  const token = await page.evaluate(() => localStorage.getItem("labbox.token") ?? "");
  auth = { Authorization: `Bearer ${token}` };
  userId = (await (await page.request.get("/api/me", { headers: auth })).json()).id;
}

const term = (page: Page) => page.locator(".xterm-rows");

async function runInTerminal(page: Page, stepName: RegExp, expectPasted: string) {
  await page.getByRole("button", { name: stepName }).click();
  await page.getByRole("button", { name: /Run in terminal/ }).first().click();
  // The command is pasted (not run) and the terminal takes focus; then the learner presses Enter.
  await expect(term(page)).toContainText(expectPasted);
  await page.keyboard.press("Enter");
}

test("FastAPI app in the Preview tab", async ({ page }) => {
  await login(page, true);
  await page.goto("/labs/fastapi-first-api");
  await expect(page.locator(".status-label")).toHaveText("Running", { timeout: 60_000 });
  await expect(term(page)).toContainText("learner", { timeout: 20_000 });
  await runInTerminal(page, /Scene 4: Run it and look/, "fastapi dev main.py");
  await expect(term(page)).toContainText("Uvicorn running on http://0.0.0.0:8000", { timeout: 20_000 });

  await page.getByRole("tab", { name: "Preview" }).click();
  const frame = page.frameLocator("iframe.preview-frame");
  await expect(frame.locator("body")).toContainText("Lostdesk is open", { timeout: 20_000 });
  await page.getByLabel("Path").fill("/items");
  await page.getByRole("button", { name: "Go" }).click();
  await expect(frame.locator("body")).toContainText("Not Found"); // starter: no /items yet (FastAPI course, 28 November)
});

test("Spring Boot app in the Preview tab", async ({ page }) => {
  test.setTimeout(240_000);
  await login(page);
  // Use the finished controller so /hello answers (writing Java in the editor is not what is tested here).
  const controller = `package com.shop;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MerchantController {
    @GetMapping("/hello")
    public String hello() { return "Hello from the Shop API!"; }

    @GetMapping("/merchants")
    public List<String> merchants() { return List.of("Annapurna Mess", "Book Point", "Kirana King"); }
}
`;
  await page.goto("/labs/spring-boot-first-api?chapter=03-first-endpoints");
  await expect(page.locator(".status-label")).toHaveText("Running", { timeout: 60_000 });
  const r = await page.request.put("/api/labs/spring-boot-first-api/files/content", {
    headers: auth,
    data: { path: "03-first-endpoints/src/main/java/com/shop/MerchantController.java", content: controller },
  });
  expect(r.ok()).toBeTruthy();
  await expect(term(page)).toContainText("learner", { timeout: 20_000 });
  await runInTerminal(page, /Scene 7: Build and run/, "java -jar target/shop-api.jar");
  await expect(term(page)).toContainText("Started ShopApiApplication", { timeout: 180_000 });

  await page.getByRole("tab", { name: "Preview" }).click();
  await expect(page.getByLabel("Path")).toHaveValue("/hello");
  await expect(page.frameLocator("iframe.preview-frame").locator("body")).toHaveText("Hello from the Shop API!", { timeout: 20_000 });
});

test("Postgres incident: setup, timer, fix, live check", async ({ page }) => {
  test.setTimeout(180_000);
  await login(page);
  await page.goto("/labs/postgres-indexing-incident");
  await expect(page.locator(".status-label")).toHaveText("Running", { timeout: 90_000 });
  // The database service shows next to the machine status, and the chapter setup runs once.
  await expect(page.locator(".service-dot", { hasText: "db" })).toBeVisible({ timeout: 30_000 });
  await expect(page.locator(".setup-banner")).toBeHidden({ timeout: 90_000 });

  await page.getByRole("button", { name: /Scene 5: Pager/ }).click();
  await expect(page.locator(".incident [role=timer]")).toContainText(/1[0-5]:\d\d/);

  // Check before fixing: a live check, with the metric.
  await page.locator(".footer-actions").getByRole("button", { name: "Check" }).click();
  await expect(page.locator(".drawer-title")).toHaveText("0 of 1 passed", { timeout: 60_000 });
  await expect(page.locator(".res-message")).toContainText("Seq Scan");
  // The metric is a gauge against its target (5 ms): missed before the fix.
  const gauge = page.locator(".gauge", { hasText: "lookup" });
  await expect(gauge).toHaveClass(/metric-missed/);
  await expect(gauge).toContainText("target ≤ 5 ms");
  await page.getByRole("button", { name: "Close results" }).click();

  // Fix it from the terminal, like a learner would.
  await page.locator(".terminal-host").click();
  await page.keyboard.type("psql -c 'CREATE INDEX ON orders (customer_id, created_at DESC)'");
  await page.keyboard.press("Enter");
  // Postgres answers "CREATE INDEX" on a line of its own once the index is built.
  await expect.poll(async () => /^CREATE INDEX\s*$/m.test(await term(page).innerText()), { timeout: 60_000 }).toBe(true);

  await page.locator(".footer-actions").getByRole("button", { name: "Check" }).click();
  await expect(page.locator(".drawer-title")).toHaveText("1 of 1 passed 🎉", { timeout: 60_000 });
  await expect(page.locator(".gauge", { hasText: "lookup" })).toHaveClass(/metric-met/); // green once fixed
  await expect(page.locator(".toast-info").last()).toContainText("+325 XP");
  await expect(page.locator(".toast-info").last()).toContainText("Fixed inside the timer");
});
