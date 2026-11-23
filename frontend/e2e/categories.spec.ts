import { expect, test } from "@playwright/test";

// Owner, 23 November: the dashboard shows labs by category, AI first, then languages, frameworks, system design,
// databases, DevOps, and the categories still to come (cloud, AWS).
test("the dashboard groups labs by category, AI first", async ({ page, request }) => {
  const signup = await request.post("/api/auth/signup", { data: { username: `cats${Date.now()}`, password: "secret123" } });
  const { token } = await signup.json();
  await request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${token}` } });
  await page.addInitScript((t: string) => localStorage.setItem("labbox.token", t), token);

  await page.goto("/labs");
  const titles = page.locator(".lab-group-title");
  await expect(titles.first()).toContainText("AI", { timeout: 30_000 });
  const order = (await titles.allTextContents()).map((t) => t.replace(/\d+ labs?|coming soon/, "").trim());
  expect(order.slice(0, 8)).toEqual(["AI", "Languages", "Frameworks", "System design", "Databases", "DevOps", "Cloud", "AWS"]);

  // Each lab sits in its own category; upcoming categories say so and have no tiles.
  await expect(page.locator("#category-ai .h-lab", { hasText: "Spring AI" })).toBeVisible();
  await expect(page.locator("#category-languages .h-lab", { hasText: "Python from zero" })).toBeVisible();
  await expect(page.locator("#category-frameworks .h-lab", { hasText: "Spring Boot" })).toBeVisible();
  await expect(page.locator("#category-databases .h-lab", { hasText: "Redis in practice" })).toBeVisible();
  await expect(page.locator("#category-devops .h-lab", { hasText: "Linux on call" })).toBeVisible();
  await expect(page.locator("#category-cloud .h-lab")).toHaveCount(0);
  await expect(page.locator("#category-cloud")).toContainText("coming soon");

  // The chips jump to a category.
  await page.getByRole("navigation", { name: "Categories" }).getByRole("link", { name: /Databases/ }).click();
  await expect(page).toHaveURL(/#category-databases$/);
  await page.screenshot({ path: "test-results/categories.png", fullPage: true });
});
