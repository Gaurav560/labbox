/* Phase G: a system design lab's design review step. Answers go to the grader (the local model in
 * dev), and the step shows a score and feedback per rubric point, or a clear "could not grade". */
import { expect, test } from "@playwright/test";

test("design review: answer, get feedback, see scores", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("labbox.editor", JSON.stringify("classic")));
  const r = await page.request.post("/api/auth/signup", { data: { username: `sd${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);
  await page.goto("/labs/rate-limiter");
  await page.locator("#chapter-select").selectOption("02-global-limit");
  await page.getByRole("button", { name: "Scene 5: Design review" }).click();
  await expect(page.locator(".step-kind")).toHaveText("Design review");
  await expect(page.locator(".design-q")).toHaveCount(3);
  const send = page.getByRole("button", { name: "Get feedback" });
  await expect(send).toBeDisabled(); // nothing written yet

  await page.getByLabel("Answer to question 1").fill("I would fail open: let requests through while Redis is down, so users are not blocked, with a short timeout.");
  await page.getByLabel("Answer to question 2").fill("Each server kept its own count in memory, so two servers allowed twice the limit.");
  await page.getByLabel("Answer to question 3").fill("Yes, 10 at the end of one second and 10 at the start of the next. A sliding window or token bucket fixes it.");
  await send.click();
  await expect(page.locator(".design-score, .design-error")).toBeVisible({ timeout: 120_000 });
  if (await page.locator(".design-score").isVisible()) {
    await expect(page.locator(".design-score")).toContainText("/ 10");
    await expect(page.locator(".design-pts")).toHaveCount(3);
    await expect(page.locator(".design-feedback li").first()).toBeVisible();
    // The last attempt comes back after a reload.
    await page.reload();
    await page.locator("#chapter-select").selectOption("02-global-limit");
    await page.getByRole("button", { name: "Scene 5: Design review" }).click();
    await expect(page.locator(".design-score")).toContainText("/ 10");
    await expect(page.getByLabel("Answer to question 2")).toHaveValue(/own count in memory/);
  }
});
