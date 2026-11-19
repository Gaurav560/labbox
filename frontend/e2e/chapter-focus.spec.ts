/* Switching chapters opens that chapter's code (Lite editor; VS Code gets the same through its extension). */
import { expect, test } from "@playwright/test";

test("a chapter opens its own code, at its section", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("labbox.editor", JSON.stringify("classic")));
  const r = await page.request.post("/api/auth/signup", { data: { username: `cf${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);
  await page.goto("/labs/redis-in-practice");
  await expect(page.locator(".tab.active")).toContainText("README.md", { timeout: 90_000 }); // chapter 1 is redis-cli only
  await page.locator("#chapter-select").selectOption("06-caching-for-real");
  await expect(page.locator(".tab.active")).toContainText("app.py");
  await expect(page.locator(".monaco-editor .view-lines")).toContainText("chapter 6: caching for real");
  // The task area: a stepper with the task's real title, not its id.
  await expect(page.locator(".tasks-count")).toHaveText("Task 1 of 3");
  await expect(page.locator(".tasks-now")).not.toBeEmpty();
  await expect(page.locator(".footer-actions").getByRole("button", { name: /^Hint \(\d left\)$/ })).toBeVisible();
});
