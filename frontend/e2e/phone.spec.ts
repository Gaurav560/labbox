import { execFileSync } from "node:child_process";
import { expect, test } from "@playwright/test";

// Step 4 of the owner's UX review: on a phone the lab page is a reading mode. It fits the screen, shows
// no editor or terminal, offers no Check or Run buttons, and never starts a machine.
test.use({ viewport: { width: 390, height: 844 } });

test("phones get a reading mode that fits and starts no machine", async ({ page, request }) => {
  const signup = await request.post("/api/auth/signup", { data: { username: `phone${Date.now()}`, password: "secret123" } });
  const { token, user } = await signup.json();
  await request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${token}` } });
  await page.addInitScript((t: string) => localStorage.setItem("labbox.token", t), token);

  await page.goto("/labs/javascript-basics");
  await expect(page.locator(".step-count")).toHaveText(/Step 1 of \d+/);
  await expect(page.locator(".work-area")).toHaveCount(0);
  await expect(page.locator("iframe")).toHaveCount(0);
  await expect(page.locator(".phone-note")).toContainText("laptop or tablet");
  await expect(page.getByRole("button", { name: "Check", exact: true })).toHaveCount(0);
  // Nothing runs off the right edge.
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  // The chapter picker and theme still work; a try step offers no Run button (there is no terminal).
  await page.getByLabel("Chapter", { exact: true }).selectOption("04-loops");
  await page.getByRole("button", { name: /^Step 6:/ }).click();
  await expect(page.locator(".step-kind")).toHaveText("Try it");
  await expect(page.locator(".code-btn", { hasText: /Run/ })).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);

  // No machine was started for this learner.
  await page.waitForTimeout(3000);
  const machines = execFileSync("docker", ["ps", "-aq", "--filter", `label=labbox.user=${user.id}`]).toString().trim();
  expect(machines).toBe("");
});
