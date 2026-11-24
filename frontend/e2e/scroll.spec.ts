import { expect, test } from "@playwright/test";

// Owner, 25 November: a course page and Premium Reads must open at their top, not scrolled down to "You are here"
// or to wherever the previous page was scrolled.
test("Premium Reads opens at its top from the bottom of the home page", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.locator("footer").getByRole("link", { name: "Premium Reads" }).click();
  await expect(page).toHaveURL(/\/library$/);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await page.waitForTimeout(800);
  expect(await page.evaluate(() => window.scrollY)).toBe(0);
});

test("a course page opens at its top, not at You are here", async ({ page, request }) => {
  const signup = await request.post("/api/auth/signup", { data: { username: `scroll${Date.now()}`, password: "secret123" } });
  const { token } = await signup.json();
  const headers = { Authorization: `Bearer ${token}` };
  await request.post("/api/onboarding/skip", { headers });
  await request.put("/api/labs/go-basics/chapters/07-more-slices/progress", { headers, data: { current_step: 2 } });
  await page.addInitScript((t: string) => localStorage.setItem("labbox.token", t), token);
  await page.goto("/labs");
  const card = page.locator('a.h-lab[href="/courses/go-basics"], a.u-row-link[href="/courses/go-basics"]').first();
  await expect(card).toBeVisible({ timeout: 30_000 });
  await card.scrollIntoViewIfNeeded();
  expect(await page.evaluate(() => window.scrollY)).toBeGreaterThan(0);
  await card.click();
  await expect(page).toHaveURL(/\/courses\/go-basics$/);
  await expect(page.locator(".metro-now")).toContainText("You are here"); // still marked on the map
  await page.waitForTimeout(800);
  expect(await page.evaluate(() => window.scrollY)).toBe(0);
});
