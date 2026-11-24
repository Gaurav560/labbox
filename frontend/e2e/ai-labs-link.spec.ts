import { expect, test } from "@playwright/test";

// Owner, 25 November: "AI labs" in the home page menu opens the AI labs when logged in; when not, it asks to log in
// first and then lands on the AI labs.
test("AI labs in the menu: log in first, then the AI labs", async ({ page, request }) => {
  const username = `ailink${Date.now() % 1e9}`;
  const signup = await request.post("/api/auth/signup", { data: { username, password: "secret123" } });
  const { token } = await signup.json();
  await request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${token}` } });

  await page.goto("/");
  await page.locator(".home-nav").getByRole("link", { name: "AI labs" }).click();
  await expect(page).toHaveURL(/\/login\?next=%2Flabs%3Fcategory%3Dai$/);
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill("secret123");
  await page.getByLabel("Password").press("Enter");
  await expect(page).toHaveURL(/\/labs\?category=ai$/);
  await expect(page.locator("#category-ai .u-row").first()).toBeVisible({ timeout: 30_000 });
  await expect(page.locator(".u-group")).toHaveCount(1); // only the AI category is shown
  await expect(page.locator(".u-cat", { hasText: "AI" }).first()).toHaveAttribute("aria-pressed", "true");

  // Logged in, the same link goes straight there; a next= to another site is ignored.
  await page.goto("/?home");
  await page.locator(".home-nav").getByRole("link", { name: "AI labs" }).click();
  await expect(page).toHaveURL(/\/labs\?category=ai$/);
  await page.evaluate(() => localStorage.removeItem("labbox.token"));
  await page.goto("/login?next=//evil.example.com");
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill("secret123");
  await page.getByLabel("Password").press("Enter");
  await expect(page).toHaveURL(/localhost:\d+\/labs$/);
});
