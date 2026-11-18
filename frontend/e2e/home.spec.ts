/* The public home page: works logged out, shows the live catalog, and leads into sign-up and onboarding. */
import { expect, test } from "@playwright/test";

test("home page for visitors leads to sign up and onboarding", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));

  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Learn tech by doing, not watching.");
  await expect(page).toHaveTitle(/LabBox/);
  // The logo, as a link home and as the favicon.
  await expect(page.locator(".home-header").getByRole("link", { name: "LabBox home" })).toBeVisible();
  expect((await page.request.get("/favicon.svg")).headers()["content-type"]).toContain("svg");
  // The catalog comes from the server: both labs sit in the languages track, the rest are coming soon.
  await expect(page.locator(".track-chip", { hasText: "Programming languages" })).toContainText("2 labs");
  await expect(page.locator(".track-chip", { hasText: "DevOps" })).toContainText("Soon");
  await expect(page.locator(".live-labs")).toContainText("Python Basics");
  await expect(page.locator(".track-chip", { hasText: "Databases" })).toContainText("1 lab");

  // The demo question works in the browser.
  const demo = page.locator(".try-card");
  await demo.locator(".predict-option", { hasText: "chai2" }).click();
  await expect(demo).toContainText("Not quite");
  await demo.locator(".predict-option", { hasText: "chaichai" }).click();
  await expect(demo.locator(".predict-explain")).toContainText("repeats it");

  // Start free goes to sign up (Enter signs up), then onboarding.
  await page.locator(".hero").getByRole("link", { name: "Start free →" }).click();
  await expect(page.getByRole("heading", { name: "Create your account" })).toBeVisible();
  await page.getByLabel("Username").fill(`home${Date.now() % 1_000_000_000}`);
  await page.getByLabel("Password").fill("secret123");
  await page.getByLabel("Password").press("Enter");
  await expect(page.getByRole("heading", { name: "What do you want to get better at?" })).toBeVisible();
  await page.getByRole("button", { name: "Skip" }).click();
  await expect(page.getByText("Your labs")).toBeVisible();

  // Logged in, the home page offers to continue instead of signing up.
  await page.goto("/");
  await expect(page.locator(".home-header").getByRole("link", { name: "Continue learning →" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Log in" })).toHaveCount(0);
  await page.locator(".home-header").getByRole("link", { name: "Continue learning →" }).click();
  await expect(page).toHaveURL(/\/labs$/);

  // An expired login does not lock visitors out of the home page.
  await page.evaluate(() => localStorage.setItem("labbox.token", "expired-or-garbage"));
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.locator(".home-header").getByRole("link", { name: "Start free" })).toBeVisible();
  expect(errors.filter((e) => !e.includes("401"))).toEqual([]);
});
