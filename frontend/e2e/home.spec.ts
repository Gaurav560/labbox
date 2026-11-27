/* The public home page: works logged out, shows the live catalog, and leads into sign-up and onboarding. */
import { expect, test } from "@playwright/test";
import { signIn } from "./signin";

test("home page for visitors leads to sign up and onboarding", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));

  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Learn AI by building it, not watching.");
  await expect(page).toHaveTitle(/LabBox by Telusko/);
  // Certificates (owner, 27 November): a sample certificate and how it is shared.
  const certs = page.locator("#certificates");
  await expect(certs.getByRole("heading", { level: 2 })).toHaveText("Finish a lab. Share the proof.");
  await expect(certs.getByRole("article", { name: "A sample certificate" })).toContainText("Meera Iyer");
  await expect(certs.getByRole("list", { name: "Share on" })).toContainText("LinkedIn");
  // The logo, as a link home and as the favicon.
  await expect(page.locator(".home-header").getByRole("link", { name: "LabBox by Telusko home" })).toBeVisible();
  expect((await page.request.get("/favicon.svg")).headers()["content-type"]).toContain("svg");
  // The catalog comes from the server: both labs sit in the languages track, the rest are coming soon.
  await expect(page.locator(".track-chip", { hasText: "Programming languages" })).toContainText(/\d+ labs?/);
  // The AI labs come first, right under the hero, with the Forward Deployed Engineer course in the spotlight
  // (owner, 27 November).
  const ai = page.locator("#ai");
  await expect(ai.locator(".ai-spot h3")).toHaveText("Forward Deployed Engineer");
  await expect(ai.locator(".ai-spot-go")).toHaveAttribute("href", "/courses/forward-deployed-engineer"); // not straight to sign-up
  await expect(ai.locator(".ai-rows li")).toHaveCount(5);
  await expect(ai.locator(".ai-rows img")).toHaveCount(5); // small logos, like the dashboard's list
  await expect(ai.locator(".ai-rows a").first()).toHaveAttribute("href", /^\/courses\//);
  await expect(ai.locator(".ai-spot-art img")).toBeVisible(); // its big picture (the email demo is off for now)
  await expect(ai.locator(".ai-demo")).toHaveCount(0);
  await expect(ai.locator(".ai-spot-tag")).toContainText("Learn the hottest job in the tech market");
  expect(await page.evaluate(() => {
    const hero = document.querySelector("main")!.firstElementChild!;
    return !!hero.nextElementSibling?.matches("#ai, :has(> #ai)");
  })).toBe(true);
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

  // Start free goes to sign up: Google and GitHub only (owner, 27 November); a new account then starts onboarding.
  await page.locator(".hero").getByRole("link", { name: "Start free →" }).click();
  await expect(page.getByRole("heading", { name: "Create your account" })).toBeVisible();
  await expect(page.getByLabel("Username")).toHaveCount(0);
  await signIn(page, `home${Date.now() % 1_000_000_000}`, { first: true });
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

test("the AI courses' intro pages open for visitors; other courses ask them to log in", async ({ page }) => {
  // Owner, 27 November: the home page's AI rows open "the actual intro page where the skill map is", AI courses only.
  await page.goto("/courses/langchain");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("LangChain");
  await expect(page.getByRole("heading", { name: "Skill map" })).toBeVisible();
  await expect(page.locator(".course-syllabus")).toContainText("Sign up free to open its lessons");
  await expect(page.locator(".course-go")).toHaveAttribute("href", "/login?signup=1&next=%2Fcourses%2Flangchain");
  await expect(page.locator(".course-syllabus a[href^='/labs/']")).toHaveCount(0); // no way into the lessons
  await expect(page.locator(".course-progress")).toHaveCount(0);
  await page.goto("/courses/python-basics");
  await expect(page).toHaveURL(/\/login\?next=%2Fcourses%2Fpython-basics/);
});

test("pricing: plans without prices, linked from the home menu and the footer", async ({ page }) => {
  // Owner, 27 November: a pricing page, UI only, "plans, no prices yet".
  await page.goto("/");
  await page.locator(".home-nav").getByRole("link", { name: "Pricing" }).click();
  await expect(page).toHaveURL(/\/pricing$/);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Pricing");
  await expect(page.locator(".plan")).toHaveCount(3);
  await expect(page.locator(".plan.is-now")).toContainText("₹0");
  await expect(page.locator(".plan.is-soon .plan-price")).toHaveText(["Coming soon", "Coming soon"]);
  await expect(page.locator(".plan.is-now a")).toHaveAttribute("href", "/login?signup=1");
  await expect(page.locator(".info-footer").getByRole("link", { name: "Pricing" })).toHaveAttribute("href", "/pricing");
});
