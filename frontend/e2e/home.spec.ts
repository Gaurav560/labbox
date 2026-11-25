/* The public home page: works logged out, shows the live catalog, and leads into sign-up and onboarding. */
import { expect, test } from "@playwright/test";

test("home page for visitors leads to sign up and onboarding", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));

  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("The AI wave is here. Learn to build AI apps, or get left behind.");
  await expect(page).toHaveTitle(/LabBox by Telusko/);
  // The logo, as a link home and as the favicon.
  await expect(page.locator(".home-header").getByRole("link", { name: "LabBox by Telusko home" })).toBeVisible();
  expect((await page.request.get("/favicon.svg")).headers()["content-type"]).toContain("svg");
  // The hero shows a framed print with its credit (Ukiyo, owner 25 November).
  await expect(page.locator(".uh-hero-pic img")).toBeVisible();
  await expect(page.locator(".uh-term")).toContainText("labbox start");
  await expect(page.locator(".uh-hero-art figcaption")).toContainText("Hiroshige");
  // Start a lab: the lab's real stack packs itself into one container, line by line, then a tick and Start.
  const machine = page.locator("#machine");
  await expect(machine.getByRole("heading", { level: 2 })).toHaveText("One click, and a container spins up for you with everything the lab needs.");
  await machine.scrollIntoViewIfNeeded();
  // The first run starts by itself when the section comes into view (owner, 25 November).
  await expect(machine.locator(".ua-container")).toBeVisible(); // the Docker-style shipping container
  await expect(machine.locator(".ua-box.is-sealed")).toBeVisible({ timeout: 15_000 });
  await expect(machine.locator(".ua-log li.is-piece")).toHaveCount(6); // LangChain: Linux, Python, LangChain, gateway, editor, AI
  await expect(machine.locator(".ua-dock li")).toHaveCount(0); // all of them went in
  await expect(machine.locator(".ua-c-box")).toHaveCount(6); // each one stays inside as a crate, seen through the wall
  await expect(machine.locator(".ua-log li.is-cmd")).toContainText("docker start");
  await expect(machine.locator(".ua-c-plate")).toContainText("RUNNING");
  await expect(machine.getByRole("tab")).toHaveText(["LangChain", "Spring AI", "RAG", "Spring Boot", "Python", "Postgres", "Linux", "FastAPI", "Redis"]);
  await expect(machine.locator(".ua-log li").nth(2)).toContainText("LangChain 1.5");
  await expect(machine.locator(".ua-stamp")).toHaveAttribute("aria-label", "Ready");
  await expect(machine.locator(".ua-ready").getByRole("link", { name: "Start →" })).toHaveAttribute("href", "/login?next=%2Fcourses%2Flangchain");
  await machine.getByRole("tab", { name: "Redis" }).click();
  await expect(machine.locator(".ua-c-plate")).toContainText("TAP TO START"); // a lab change waits for Run or a tap
  await expect(machine.getByText("Try it: tap Run")).toBeVisible();
  await expect(machine.locator(".ua-log li.is-piece")).toHaveCount(0); // a new lab waits for its own click
  await machine.getByRole("button", { name: /Spin up the Redis machine/ }).click();
  await expect(machine.locator(".ua-box.is-sealed")).toBeVisible({ timeout: 15_000 });
  await expect(machine.locator(".ua-log li.is-piece")).toHaveCount(7);
  await expect(machine.locator(".ua-log")).toContainText("Redis replica");
  await expect(machine).not.toContainText("VS Code");
  // The catalog comes from the server: a folding screen, one panel per category, not every lab (owner, 25 November).
  const languages = page.locator("#labs .uh-panel", { hasText: "Languages" });
  await expect(languages).toContainText(/\d+ labs/);
  await expect(languages).toHaveAttribute("href", "/login?signup=1");
  await expect(page.locator("#labs .u-row")).toHaveCount(0);
  await expect(page.locator("#labs .uh-all a")).toHaveText(/^See all \d+ labs →$/);
  // The AI section (pagoda, "24 labs ... your own GPT") is off for now (owner, 25 November); "AI labs" opens the AI labs.
  await expect(page.locator("#ai")).toHaveCount(0);
  await expect(page.locator(".home-nav").getByRole("link", { name: "AI labs" })).toHaveAttribute("href", "/labs?category=ai");
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
