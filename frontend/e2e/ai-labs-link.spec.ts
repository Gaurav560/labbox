import { expect, test } from "@playwright/test";

// Owner, 27 November: "AI labs" in the home page menu jumps to the home page's AI section. The AI labs list
// (/labs?category=ai) still asks a visitor to log in first and then lands there (owner, 25 November).
test("AI labs in the menu jumps to the AI section; the AI labs list asks to log in first", async ({ page, request }) => {
  const username = `ailink${Date.now() % 1e9}`;
  const signup = await request.post("/api/auth/signup", { data: { username, password: "secret123" } });
  const made = await signup.json();
  await request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${made.token}` } });

  await page.goto("/");
  await page.locator(".home-nav").getByRole("link", { name: "AI labs" }).click();
  await expect(page).toHaveURL(/\/#ai$/);
  await expect(page.locator("#ai .ai-spot h3")).toBeInViewport();
  await page.goto("/labs?category=ai");
  await expect(page).toHaveURL(/\/login\?next=%2Flabs%3Fcategory%3Dai$/);
  // Google and GitHub only (owner, 27 November): the buttons carry next= on; coming back signed in lands there.
  await expect(page.getByRole("link", { name: "Continue with Google" })).toHaveAttribute("href", /next=%2Flabs%3Fcategory%3Dai$/);
  await page.route("**/api/auth/oauth/exchange", (r) => r.fulfill({ json: { ...made, new: false } }));
  await page.goto("/login?oauth=one-time-code&next=%2Flabs%3Fcategory%3Dai");
  await expect(page).toHaveURL(/\/labs\?category=ai$/);
  await expect(page.locator("#category-ai .u-row").first()).toBeVisible({ timeout: 30_000 });
  await expect(page.locator(".u-group")).toHaveCount(1); // only the AI category is shown
  await expect(page.locator(".u-cat", { hasText: "AI" }).first()).toHaveAttribute("aria-pressed", "true");

  // A next= to another site is ignored.
  await page.evaluate(() => localStorage.removeItem("labbox.token"));
  await page.goto("/login?oauth=one-time-code&next=//evil.example.com");
  await expect(page).toHaveURL(/localhost:\d+\/labs$/);
});
