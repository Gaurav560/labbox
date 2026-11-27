/* The public home page: works logged out, shows the live catalog, and leads into sign-up and onboarding. */
import { expect, test } from "@playwright/test";
import { signIn } from "./signin";

test("home page for visitors leads to sign up and onboarding", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));

  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("The AI wave is here. Learn to ride it.");
  await expect(page).toHaveTitle(/LabBox by Telusko/);
  // Certificates (owner, 27 November): a sample certificate and how it is shared.
  const certs = page.locator("#certificates");
  await expect(certs.getByRole("heading", { level: 2 })).toHaveText("Finish a lab. Share the proof.");
  await expect(certs.getByRole("article", { name: "A sample certificate" })).toContainText("Meera Iyer");
  await expect(certs.getByRole("list", { name: "Share on" })).toContainText("LinkedIn");
  // The logo, as a link home and as the favicon.
  await expect(page.locator(".home-header").getByRole("link", { name: "LabBox by Telusko home" })).toBeVisible();
  expect((await page.request.get("/favicon.svg")).headers()["content-type"]).toContain("svg");
  // The hero shows a framed print with its credit (Ukiyo, owner 25 November).
  await expect(page.locator(".uh-hero-print img")).toBeVisible();
  await expect(page.locator(".uh-promise")).toHaveText("No videos to sit through. You learn by building.");
  // Half text, half print: Hiroshige's A Great Wave by the Coast fading into the page (owner, 27 November)
  await expect(page.locator(".uh-hero-print img")).toHaveAttribute("src", "/ukiyo/heroes/hiroshige-coast.webp");
  expect(await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)).toBe(0); // no sideways scroll
  await expect(page.locator(".uh-term")).toHaveCount(0);
  // Start a lab: the lab's real stack packs itself into one container, line by line, then a tick and Start.
  const machine = page.locator("#machine");
  await expect(machine.getByRole("heading", { level: 2 })).toHaveText("One click. Your lab is ready.");
  await machine.scrollIntoViewIfNeeded();
  // The first run starts by itself when the section comes into view (owner, 25 November).
  await expect(machine.locator(".ua-container")).toBeVisible(); // the Docker-style shipping container
  await expect(machine.locator(".ua-box.is-sealed")).toBeVisible({ timeout: 30_000 });
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
  await expect(machine.locator(".ua-box.is-sealed")).toBeVisible({ timeout: 30_000 });
  await expect(machine.locator(".ua-log li.is-piece")).toHaveCount(7);
  await expect(machine.locator(".ua-log")).toContainText("Redis replica");
  await expect(machine).not.toContainText("VS Code");
  // The catalog comes from the server: a folding screen, one panel per category, not every lab (owner, 25 November).
  const languages = page.locator("#labs .uh-panel", { hasText: "Languages" });
  await expect(languages).toContainText(/\d+ labs/);
  await expect(languages).toHaveAttribute("href", "/login?signup=1");
  await expect(page.locator("#labs .u-row")).toHaveCount(0);
  await expect(page.locator("#labs .uh-all a")).toHaveText(/^See all \d+ labs →$/);
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
  await expect(ai.locator(".ai-spot-tag")).toHaveText(/^New ?The hottest job in AI\.$/);
  expect(await page.evaluate(() => {
    const hero = document.querySelector("main")!.firstElementChild!;
    return !!hero.nextElementSibling?.matches("#ai, :has(> #ai)");
  })).toBe(true);
  // "AI labs" in the menu jumps to the AI section (owner, 27 November).
  await expect(page.locator(".home-nav").getByRole("link", { name: "AI labs" })).toHaveAttribute("href", "#ai");
  await expect(page.locator("#inside")).toHaveCount(0); // the Inside a lab section is gone (owner, 25 November)
  await expect(page.locator("#labs .uh-panel", { hasText: "DevOps" })).toContainText(/\d+ labs?/);
  // The closing panel has no "first win" line.
  await expect(page.locator(".uh-final")).not.toContainText("first win");

  // FAQs sit just above the footer, and the footer itself no longer links to them.
  await page.locator(".h-faq-item summary", { hasText: "Do I need an API key" }).click();
  await expect(page.locator(".h-faq-item[open]")).toContainText("lab requests");
  await expect(page.locator(".home-footer").getByRole("link", { name: "FAQs" })).toHaveCount(0);

  // Start free goes to sign up: Google and GitHub only (owner, 27 November); a new account then starts onboarding.
  await page.locator(".uh-hero").getByRole("link", { name: "Start free →" }).click();
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
