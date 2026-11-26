/*
 * Phase C acceptance: onboarding lands a new user in a lab with the editor open, the daily drill
 * counts for the streak, and the course page's skill map lights up after a chapter is completed.
 */
import { execFileSync } from "node:child_process";
import { expect, test, type Page } from "@playwright/test";
import { signIn } from "./signin";

const PY_SOLVED: Record<string, string> = {
  // Python from zero, chapter 1 (its own folder since the 22 November rewrite).
  "01-first-program/hello.py": 'print("Hello! I am Pocket.")\nprint("I will help you track your money.")\n',
  "01-first-program/fix_me.py": 'print("Pocket is starting...")\nprint("Ready to count your rupees.")\nprint("Today\'s budget is", 500, "rupees.")\n',
};

let userId: number | null = null;

test.afterAll(() => {
  if (userId === null) return;
  const ids = execFileSync("docker", ["ps", "-aq", "--filter", `label=labbox.user=${userId}`]).toString().split(/\s+/).filter(Boolean);
  if (ids.length) execFileSync("docker", ["rm", "-f", ...ids]);
});

// Level, streak and stars live in the profile panel behind the top bar's profile button.
const openProfile = async (page: Page) => {
  const panel = page.getByRole("dialog", { name: "Profile" });
  if (!(await panel.isVisible())) await page.locator(".topbar").getByRole("button", { name: /^Profile/ }).click();
};
const badge = (page: Page, label: RegExp) => page.getByRole("dialog", { name: "Profile" }).getByLabel(label);

test("onboarding, daily drill, streak, XP and skill map", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("labbox.editor", JSON.stringify("classic"))); // these tests drive the classic editor
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));

  // 1. Sign up: onboarding starts by itself.
  const started = Date.now();
  await signIn(page, `ob${Date.now() % 1_000_000_000}`, { first: true });
  await expect(page.getByRole("heading", { name: "What do you want to get better at?" })).toBeVisible();

  // 2. Goal, then 3 placement questions, then the path.
  await page.getByRole("button", { name: /Learn a new language/ }).click();
  await expect(page.getByRole("heading", { name: "How much do you know?" })).toBeVisible();
  for (let i = 0; i < 3; i++) await page.locator(".placement-q").nth(i).getByRole("radio").nth(1).click();
  await page.getByRole("button", { name: "See my path →" }).click();
  await expect(page.getByText("You got 3 of 3")).toBeVisible();
  await expect(page.locator(".start-card")).toContainText("Python from zero");

  // 3. Into the lab: the editor is open on the first starter file, well within 60 seconds.
  await page.getByRole("button", { name: "Start coding →" }).click();
  await expect(page.locator(".tab.active")).toContainText("hello.py", { timeout: 60_000 });
  await expect(page.locator(".monaco-editor .view-lines")).toContainText("task hello_pocket");
  expect(Date.now() - started).toBeLessThan(60_000);
  const token = await page.evaluate(() => localStorage.getItem("labbox.token") ?? "");
  const auth = { Authorization: `Bearer ${token}` };
  userId = (await (await page.request.get("/api/me", { headers: auth })).json()).id;
  await openProfile(page);
  await expect(badge(page, /day streak/)).toHaveText("0");
  await expect(badge(page, /Level/)).toHaveText("Level 1");
  await page.keyboard.press("Escape");

  // 4. The daily drill on the labs page counts for the streak (answers are checked on the server).
  await page.goto("/labs");
  // Ukiyo: the labs are rows in a directory, each with its logo or initial and its title.
  await expect(page.locator(".u-row").first()).toBeVisible();
  await expect(page.locator(".u-row .u-row-title")).toHaveCount(await page.locator(".u-row").count());
  const drill = page.locator(".drill-card");
  await expect(drill).toBeVisible();
  const options = drill.locator(".predict-option");
  for (let i = 0; i < (await options.count()); i++) {
    if (await drill.locator(".predict-explain").isVisible()) break;
    if (await options.nth(i).isEnabled()) {
      await options.nth(i).click();
      await expect(options.nth(i)).toHaveAttribute("aria-pressed", "true");
    }
  }
  await expect(drill.locator(".predict-explain")).toBeVisible();
  await expect(drill.locator(".xp-chip")).toHaveText("Done ✓");
  await expect(page.locator(".toast-info")).toContainText("+20 XP");
  await openProfile(page);
  await expect(badge(page, /day streak/)).toHaveText("1");
  await expect(badge(page, /XP$/)).toHaveText("20");

  // 5. The skill map on the lab's course page, before: chapter 1 is where you are, not done.
  await page.goto("/courses/python-basics");
  const pyNode = page.locator(".metro-station", { hasText: "Your first program" });
  await expect(pyNode).toHaveClass(/metro-now/);

  // 6. Complete the chapter with a real Check: XP, recap, then the node lights up.
  await page.goto("/labs/python-basics");
  await expect(page.locator(".status-label")).toHaveText("Running", { timeout: 60_000 });
  for (const [path, content] of Object.entries(PY_SOLVED)) {
    expect((await page.request.put("/api/labs/python-basics/files/content", { headers: auth, data: { path, content } })).ok()).toBeTruthy();
  }
  await page.locator(".footer-actions").getByRole("button", { name: "Check" }).click();
  await expect(page.locator(".drawer-title")).toHaveText("2 of 2 passed 🎉", { timeout: 60_000 });
  // Chapter 1 of the course: two tasks (20 each) and the chapter (50), no whole-lab bonus yet.
  await expect(page.locator(".toast-info").last()).toContainText("+90 XP");
  await expect(page.locator(".recap-stats")).toContainText("⭐ 90");
  await openProfile(page);
  await expect(badge(page, /XP$/)).toHaveText("110");
  await expect(badge(page, /Level/)).toHaveText("Level 2");

  await page.goto("/courses/python-basics");
  await expect(pyNode).toHaveClass(/metro-done/);  // the station lights up
  await expect(page.locator(".metro-now")).toContainText("You are here");  // and you move on to chapter 2
  await expect(page.locator(".course-progress")).toContainText("1 of");

  // Returning: no onboarding again.
  await page.goto("/labs");
  await expect(page.getByText("Your labs")).toBeVisible();
  expect(errors).toEqual([]);
});
