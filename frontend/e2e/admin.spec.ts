/* Phase J: the admin area. An admin (granted with the CLI) sees the funnel, a lab's report, a learner's
   running machine (and stops it); a learner is sent back to the labs page. */
import { execFileSync } from "node:child_process";
import { expect, test, type Page } from "@playwright/test";

const ROOT = new URL("../..", import.meta.url).pathname;

async function signup(page: Page, prefix: string) {
  const username = `${prefix}${Date.now() % 1_000_000_000}`;
  const r = await page.request.post("/api/auth/signup", { data: { username, password: "secret123" } });
  const body = await r.json();
  // New accounts start with onboarding (covered in engagement.spec.ts); skip it here.
  await page.request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${body.token}` } });
  return { username, token: body.token as string, id: body.user.id as number };
}

async function loginAs(page: Page, token: string) {
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);
}

test("admin: funnel, a lab's report, machines with stop; learners are kept out", async ({ page }) => {
  const learner = await signup(page, "admlearner");
  const boss = await signup(page, "admboss");
  execFileSync(`${ROOT}scripts/labbox`, ["admin", "grant", boss.username], { cwd: ROOT });
  // Never leave a test account with admin rights behind (its password is known).
  try {
    await adminTour(page, learner, boss);
  } finally {
    execFileSync(`${ROOT}scripts/labbox`, ["admin", "revoke", boss.username], { cwd: ROOT });
  }
});

async function adminTour(page: Page, learner: { username: string; token: string; id: number }, boss: { token: string }) {
  const auth = { headers: { Authorization: `Bearer ${learner.token}` } };
  expect((await page.request.post("/api/labs/python-basics/workspace/start", auth)).ok()).toBeTruthy();

  // A learner who tries /admin lands on the labs page, with no Admin link.
  await loginAs(page, learner.token);
  await page.goto("/admin");
  await expect(page).toHaveURL(/\/labs$/);
  await expect(page.getByRole("link", { name: "Admin" })).toHaveCount(0);

  await loginAs(page, boss.token);
  await page.goto("/labs");
  await page.getByRole("link", { name: "Admin" }).click();
  await expect(page.getByRole("heading", { name: "Funnel" })).toBeVisible();
  await expect(page.locator(".adm-funnel li").first()).toContainText("Signed up");
  await page.getByRole("group", { name: "Window" }).getByRole("button", { name: "7d" }).click();
  await expect(page.locator(".adm-funnel li")).toHaveCount(5);

  await page.getByRole("navigation", { name: "Admin sections" }).getByRole("button", { name: "Labs" }).click();
  await page.getByRole("button", { name: "Python Basics" }).click();
  await expect(page.getByRole("columnheader", { name: "Confusion" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Your first functions" })).toBeVisible();

  await page.getByRole("navigation", { name: "Admin sections" }).getByRole("button", { name: "Machines" }).click();
  const row = page.locator("tr", { hasText: learner.username });
  await expect(row).toContainText("Python Basics");
  page.once("dialog", (d) => d.accept());
  await row.getByRole("button", { name: "Stop" }).click();
  await expect(page.getByRole("status")).toContainText(`Stopped lab-u${learner.id}-python-basics`);
  await expect(page.locator("tr", { hasText: learner.username })).toHaveCount(0);

  const status = await (await page.request.get("/api/labs/python-basics/workspace/status", auth)).json();
  expect(status.status).toBe("stopped");
  expect(status.stopped_reason).toContain("by an admin");

  await page.getByRole("navigation", { name: "Admin sections" }).getByRole("button", { name: "Learners" }).click();
  await page.getByLabel("Search username").fill(learner.username);
  await expect(page.locator(".adm-table tbody tr")).toHaveCount(1);
}
