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
  // The catalog comes from the server: both labs sit in the languages track, the rest are coming soon.
  await expect(page.locator(".track-chip", { hasText: "Programming languages" })).toContainText(/\d+ labs?/);
  // The AI track is the headline, honestly marked as launching, with its 24 planned labs.
  await expect(page.locator("#ai .h-launch")).toHaveText("Launching");
  await expect(page.locator("#ai .h-ai-stage")).toHaveCount(4);
  await expect(page.locator("#ai-title")).toContainText("24 labs");
  await expect(page.locator("#inside .h-shot img")).toBeVisible();
  await expect(page.locator(".track-chip", { hasText: "DevOps" })).toContainText(/\d+ labs?/);
  await expect(page.locator(".live-labs")).toContainText(/^Live now: .+/);  // first few titles, then "and N more"
  await expect(page.locator(".track-chip", { hasText: "Databases" })).toContainText(/\d+ labs?/);

  // The hero tour plays the four lesson moves; picking a step shows it and pauses.
  const tour = page.getByRole("region", { name: "A short tour of a LabBox lab" });
  await expect(tour.getByRole("tab", { name: /Read a little/ })).toHaveAttribute("aria-selected", "true");
  await tour.getByRole("tab", { name: /Get instant feedback/ }).click();
  await expect(tour.locator(".tour-pass")).toBeVisible();
  await expect(tour.locator(".tour-xp")).toContainText(/\+\d+ XP/);
  await expect(tour.getByRole("button", { name: "Play the tour" })).toBeVisible();
  await tour.getByRole("button", { name: "Turn sound on" }).click();
  await expect(tour.getByRole("button", { name: "Turn sound off" })).toHaveAttribute("aria-pressed", "true");

  // FAQs sit just above the footer, and the footer itself no longer links to them.
  await page.locator(".h-faq-item summary", { hasText: "Do I need an API key" }).click();
  await expect(page.locator(".h-faq-item[open]")).toContainText("lab requests");
  await expect(page.locator(".home-footer").getByRole("link", { name: "FAQs" })).toHaveCount(0);

  // Start free goes to sign up (Enter signs up), then onboarding.
  await page.locator(".hero").getByRole("link", { name: "Start free →" }).click();
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
  await expect(page.locator(".home-header").getByRole("link", { name: "Start free" })).toBeVisible();
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
  await page.locator(".auth-legal").getByRole("link", { name: "Terms of Service" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Terms of Service");
});
