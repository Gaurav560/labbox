/* The public home page: works logged out, shows the live catalog, and leads into sign-up and onboarding. */
import { expect, test } from "@playwright/test";

test("home page for visitors leads to sign up and onboarding", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));

  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Learn AI by building it, not watching.");
  await expect(page).toHaveTitle(/LabBox by Telusko/);
  // The logo, as a link home and as the favicon.
  await expect(page.locator(".home-header").getByRole("link", { name: "LabBox by Telusko home" })).toBeVisible();
  expect((await page.request.get("/favicon.svg")).headers()["content-type"]).toContain("svg");
  // The hero shows a framed print with its credit (Ukiyo, owner 25 November).
  await expect(page.locator(".uh-hero-bg")).toHaveCSS("background-image", /red-fuji/);
  await expect(page.locator(".uh-hero-credit")).toContainText("Hokusai");
  // The catalog comes from the server: a folding screen, one panel per category, not every lab (owner, 25 November).
  const languages = page.locator("#labs .uh-panel", { hasText: "Languages" });
  await expect(languages).toContainText(/\d+ labs/);
  await expect(languages).toHaveAttribute("href", "/login?signup=1");
  await expect(page.locator("#labs .u-row")).toHaveCount(0);
  await expect(page.locator("#labs .uh-all a")).toHaveText(/^See all \d+ labs →$/);
  // The AI section (pagoda, "24 labs ... your own GPT") is off for now (owner, 25 November); "AI labs" jumps to the labs.
  await expect(page.locator("#ai")).toHaveCount(0);
  await expect(page.locator(".home-nav").getByRole("link", { name: "AI labs" })).toHaveAttribute("href", "#labs");
  await expect(page.locator("#inside")).toHaveCount(0); // the Inside a lab section is gone (owner, 25 November)
  await expect(page.locator("#labs .uh-panel", { hasText: "DevOps" })).toContainText(/\d+ labs?/);
  // The closing panel has no "first win" line.
  await expect(page.locator(".uh-final")).not.toContainText("first win");

  // FAQs sit just above the footer, and the footer itself no longer links to them.
  await page.locator(".h-faq-item summary", { hasText: "Do I need an API key" }).click();
  await expect(page.locator(".h-faq-item[open]")).toContainText("lab requests");
  await expect(page.locator(".home-footer").getByRole("link", { name: "FAQs" })).toHaveCount(0);

  // Start free goes to sign up (Enter signs up), then onboarding.
  await page.locator(".uh-hero").getByRole("link", { name: "Start free →" }).click();
  await expect(page.getByRole("heading", { name: "Create your account" })).toBeVisible();
  await page.getByLabel("Username").fill(`home${Date.now() % 1_000_000_000}`);
  await page.getByLabel("Password").fill("secret123");
  await page.getByLabel("Password").press("Enter");
  await expect(page.getByRole("heading", { name: "What do you want to get better at?" })).toBeVisible();
  await page.getByRole("button", { name: "Skip" }).click();
  await expect(page.getByText("Your labs")).toBeVisible();

  // Logged in, / is the learner's dashboard (owner's UX review, step 2).
  await page.goto("/");
  await expect(page).toHaveURL(/\/labs$/);
  // The marketing page is still at /?home, and there it offers to continue instead of signing up.
  await page.goto("/?home");
  await expect(page.locator(".home-header").getByRole("link", { name: "Continue learning →" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Log in" })).toHaveCount(0);
  await page.locator(".home-header").getByRole("link", { name: "Continue learning →" }).click();
  await expect(page).toHaveURL(/\/labs$/);

  // An expired login does not lock visitors out of the home page.
  await page.evaluate(() => localStorage.setItem("labbox.token", "expired-or-garbage"));
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.locator(".home-header").getByRole("link", { name: "Log in" })).toBeVisible();
  await expect(page.locator(".home-header").getByRole("link", { name: "Start free" })).toHaveCount(0);
  expect(errors.filter((e) => !e.includes("401"))).toEqual([]);
});

test("FAQ, privacy policy and terms are public and linked from the home page", async ({ page }) => {
  await page.goto("/");
  await page.locator("#faq").getByRole("link", { name: "All questions →" }).click(); // from the FAQ section above the footer
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("FAQs");
  await page.getByText("Is it free?").click();
  await expect(page.getByText("every lab is free")).toBeVisible();
  await page.locator(".info-footer").getByRole("link", { name: "Privacy policy" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Privacy policy");
  await expect(page).toHaveTitle("Privacy policy · LabBox by Telusko");
  await page.goto("/login");
  // The login page has the light and dark switch too (owner, 25 November); it must not submit the form.
  const before = await page.evaluate(() => document.documentElement.dataset.theme);
  await page.locator(".auth-top").getByRole("button", { name: /^Switch to (light|dark) theme$/ }).click();
  await expect(page.locator("html")).not.toHaveAttribute("data-theme", before ?? "");
  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
  await page.locator(".auth-legal").getByRole("link", { name: "Terms of Service" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Terms of Service");
});
