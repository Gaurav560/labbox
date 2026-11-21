/*
 * Phase A acceptance: open a lab, step through every step with the keyboard, answer a predict,
 * reveal a hint, run a command from the lesson, pass Check, see the recap, and keep step,
 * panel size and theme across a reload. Also checks the terminal shows one prompt after a restart.
 */
import { execFileSync } from "node:child_process";
import { expect, test, type Page } from "@playwright/test";

// Python from zero, chapter 2 (id 01-functions, folder 02-functions since the 22 November rewrite).
const PY_SOLVED: Record<string, string> = {
  "02-functions/greet.py": 'def greet(name):\n    return f"Hello, {name}!"\n',
  "02-functions/math_utils.py": "def add(a, b):\n    return a + b\n\n\ndef is_even(n):\n    return n % 2 == 0\n",
};

const username = `e2e${Date.now() % 1_000_000_000}`;
let userId: number | null = null;
const errors: string[] = [];

const termText = (page: Page) => page.locator(".xterm-rows").innerText();
const stepCount = (page: Page) => page.locator(".step-count");

async function token(page: Page): Promise<string> {
  return page.evaluate(() => localStorage.getItem("labbox.token") ?? "");
}

test.afterAll(() => {
  // Remove only the containers this test created.
  if (userId === null) return;
  const ids = execFileSync("docker", ["ps", "-aq", "--filter", `label=labbox.user=${userId}`]).toString().split(/\s+/).filter(Boolean);
  if (ids.length) execFileSync("docker", ["rm", "-f", ...ids]);
});

test("lesson flow: steps, predict, hint, run, check, recap, persistence", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("labbox.editor", JSON.stringify("classic"))); // these tests drive the classic editor
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));

  // Sign up and open the lab.
  await page.goto("/login");
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill("secret123");
  await page.getByRole("button", { name: "Sign up" }).click();
  // New accounts start with onboarding (covered in engagement.spec.ts); skip it here.
  await page.getByRole("button", { name: "Skip" }).click();
  await expect(page.getByText("Your labs")).toBeVisible();
  const auth = { Authorization: `Bearer ${await token(page)}` };
  userId = (await (await page.request.get("/api/me", { headers: auth })).json()).id;

  // The lab opens on chapter 1, "Your first program": its story, mission and the history card.
  await page.goto("/labs/python-basics");
  await expect(page.locator(".status-label")).toHaveText("Running", { timeout: 60_000 });
  await expect(stepCount(page)).toHaveText("Step 1 of 17");
  await expect(page.locator(".step-kind")).toHaveText("Story");
  await expect(page.locator(".mission")).toContainText("Make Pocket say its first two sentences");
  await page.keyboard.press("ArrowRight");
  await expect(stepCount(page)).toHaveText("Step 2 of 17");
  await expect(page.locator(".step-kind")).toHaveText("History");
  await expect(page.locator(".history-timeline li")).toHaveCount(5);
  await expect(page.locator(".history-before")).toContainText("Guido van Rossum");
  // A real photo, loaded and credited (owner, 22 November).
  const guido = page.locator(".lesson-photo img[alt*='Guido van Rossum']");
  await expect(guido).toBeVisible();
  await expect.poll(() => guido.evaluate((img: HTMLImageElement) => img.naturalWidth)).toBeGreaterThan(0);
  await expect(page.locator(".lesson-photo-credit").first()).toContainText("CC BY-SA 4.0");

  // Chapter 2, functions, by link: the rest of the flow happens there.
  const chapterResponse = page.waitForResponse((r) => r.url().endsWith("/api/labs/python-basics/chapters/01-functions"));
  await page.goto("/labs/python-basics?chapter=01-functions");
  // The predict answer is checked on the server: it is not in what the page received.
  const chapterJson = await (await chapterResponse).text();
  expect(chapterJson).not.toContain("[x]");
  expect(chapterJson).not.toContain('"answer"');
  expect(chapterJson).not.toContain("Python's special value");
  await expect(stepCount(page)).toHaveText("Step 1 of 16", { timeout: 60_000 });
  await expect(page.locator(".mission")).toContainText("which builds a greeting for any name");

  // Keyboard: right arrow through the concept and the worked example to the predict step.
  await page.keyboard.press("ArrowRight"); // concept
  await page.keyboard.press("ArrowRight"); // worked example
  await expect(page.locator(".step-kind")).toHaveText("Example");
  await page.keyboard.press("ArrowRight");
  await expect(page.locator(".step-kind")).toHaveText("Predict");

  // Predict: a wrong guess first, then the right one reveals the explanation.
  expect(await page.content()).not.toContain("Python's special value");
  await page.locator(".predict-option", { hasText: "An error" }).click();
  await expect(page.getByText("Not quite. Have another go.")).toBeVisible();
  await page.locator(".predict-option", { hasText: "None" }).click();
  await expect(page.locator(".predict-explain")).toContainText("A function that ends without a");

  // Try step: Run in terminal pastes the command but does not press Enter.
  await page.keyboard.press("ArrowRight");
  await expect(page.locator(".step-kind")).toHaveText("Try it");
  await expect.poll(() => termText(page), { timeout: 15_000 }).toMatch(/learner@python-basics/);
  await page.getByRole("button", { name: /Run in terminal/ }).click();
  await expect.poll(() => termText(page)).toContain("from greet import greet"); // the long command wraps in the terminal
  await page.waitForTimeout(800);
  expect((await termText(page)).match(/^None$/m)).toBeNull(); // not run yet
  await page.keyboard.press("Enter"); // the terminal has focus now
  await expect.poll(() => termText(page)).toMatch(/^None\s*$/m);

  // Step through everything else to the recap with the keyboard (focus back on the page first).
  await page.locator(".step-card").click();
  for (let i = 6; i <= 16; i++) {
    await page.keyboard.press("ArrowRight");
    await expect(stepCount(page)).toHaveText(`Step ${i} of 16`);
  }
  await expect(page.locator(".step-kind")).toHaveText("Recap");
  await expect(page.locator(".recap-status")).toContainText("3 tasks still need to pass");
  await page.keyboard.press("ArrowLeft");
  await expect(stepCount(page)).toHaveText("Step 15 of 16");

  // Hint ladder on the greet task (task chip jumps to its step).
  await page.locator(".task-chip", { hasText: "greet" }).click();
  await expect(page.locator(".step-card h2")).toHaveText("Your turn: greet someone");
  await expect(page.locator(".xp-chip")).toHaveText("20 XP");
  await page.locator(".task-box").getByRole("button", { name: "💡 Hint (3 left)" }).click();
  await expect(page.locator(".hint-list li")).toHaveCount(1);
  await expect(page.locator(".hint-list li").first()).toContainText("Nudge");
  await expect(page.locator(".task-box").getByRole("button", { name: "💡 Hint (2 left)" })).toBeVisible();
  await expect(page.locator(".xp-chip")).toHaveText("16 XP");

  // Check the starter code: the drawer shows failures with Expected vs Got.
  await page.locator(".footer-actions").getByRole("button", { name: "Check" }).click();
  await expect(page.locator(".drawer-title")).toHaveText("0 of 3 passed", { timeout: 60_000 });
  await expect(page.locator(".expected-got").first()).toContainText("'Hello, Asha!'");
  await expect(page.locator(".expected-got").first()).toContainText("None");

  // The tutor appears once a check has failed. It uses whatever model the server maps (local Ollama in
  // dev), so only check that a reply, or a clear error if no model is running, comes back.
  await page.getByRole("button", { name: "Close results" }).click();
  await page.locator(".task-box").getByRole("button", { name: "✦ Ask the tutor" }).click();
  await page.getByLabel("Your question for the tutor").fill("Why does greet fail?");
  await page.locator(".tutor-ask").getByRole("button", { name: "Ask" }).click();
  await expect(page.locator(".tutor-meta, .tutor-error")).toBeVisible({ timeout: 90_000 });

  // Solve it (through the files API, like saving from the editor) and Check again.
  for (const [path, content] of Object.entries(PY_SOLVED)) {
    const r = await page.request.put("/api/labs/python-basics/files/content", { headers: auth, data: { path, content } });
    expect(r.ok()).toBeTruthy();
  }
  await page.locator(".footer-actions").getByRole("button", { name: "Check" }).click();
  await expect(page.locator(".drawer-title")).toHaveText("3 of 3 passed 🎉", { timeout: 60_000 });
  // A fully passed chapter jumps to the recap.
  await expect(stepCount(page)).toHaveText("Step 16 of 16");
  await expect(page.locator(".recap-status")).toContainText("Chapter complete");
  await page.getByRole("button", { name: "Close results" }).click();

  // Theme and panel size, then reload: everything is remembered.
  await page.getByRole("button", { name: "Switch to light theme" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  const panel = page.locator(".left-panel");
  const before = (await panel.boundingBox())!.width;
  const bar = (await page.getByRole("separator", { name: "Resize lesson panel" }).boundingBox())!;
  await page.mouse.move(bar.x + 2, bar.y + 200);
  await page.mouse.down();
  await page.mouse.move(bar.x + 82, bar.y + 200, { steps: 5 });
  await page.mouse.up();
  const after = (await panel.boundingBox())!.width;
  expect(Math.round(after - before)).toBe(80);
  await page.waitForTimeout(600); // the step position is saved shortly after the last move

  await page.reload();
  // The page reloads on chapter 2 (the URL names it), still on its recap.
  await expect(page.locator("#chapter-select")).toHaveValue("01-functions");
  await expect(stepCount(page)).toHaveText("Step 16 of 16");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  expect(Math.round((await panel.boundingBox())!.width)).toBe(Math.round(after));
  // The answered predict is still answered (it comes from the server).
  await page.getByRole("button", { name: "Step 4: Guess first" }).click();
  await expect(page.locator(".predict-explain")).toContainText("special value");
  await expect(page.locator(".predict-option.is-wrong")).toContainText("An error");

  // Double prompt bug: after Stop and Start the terminal shows exactly one prompt.
  await page.getByRole("button", { name: /^Machine/ }).click(); // Stop and Reset live in the Machine menu
  await page.getByRole("menuitem", { name: /Stop machine/ }).click();
  await expect(page.locator(".status-label")).toHaveText("Stopped", { timeout: 30_000 });
  await page.getByRole("button", { name: "Start machine" }).click();
  await expect(page.locator(".status-label")).toHaveText("Running", { timeout: 30_000 });
  await expect.poll(() => termText(page)).toMatch(/learner@python-basics/);
  await page.waitForTimeout(1000);
  expect((await termText(page)).match(/learner@python-basics/g)).toHaveLength(1);

  expect(errors).toEqual([]);
});

test("java lab renders its v2 steps", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("labbox.editor", JSON.stringify("classic"))); // these tests drive the classic editor
  await page.goto("/login");
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill("secret123");
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page.getByText("Your labs")).toBeVisible();
  await page.goto("/labs/java-basics");
  await expect(stepCount(page)).toHaveText("Step 1 of 16", { timeout: 60_000 });
  await expect(page.getByText("Welcome to Java")).toBeVisible();
  await page.locator(".dot").nth(6).click(); // dots jump straight to a step
  await expect(page.locator(".step-kind")).toHaveText("Predict");
  await page.locator(".predict-option", { hasText: "null" }).click();
  await expect(page.getByText("Right first time!")).toBeVisible();
});

test("lessons show pictures, a step-through trace and task cards", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("labbox.editor", JSON.stringify("classic")));
  await page.goto("/login");
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill("secret123");
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page.getByText("Your labs")).toBeVisible();
  await page.goto("/labs/java-basics");
  await expect(stepCount(page)).toHaveText("Step 1 of 16", { timeout: 60_000 });
  await page.locator(".dot").nth(2).click(); // Why methods exist: the recipe card
  await expect(page.locator(".picture svg")).toBeVisible();
  await page.locator(".dot").nth(10).click(); // Worked example: the shortest word
  const trace = page.locator(".trace");
  await expect(trace).toContainText("step 1 of 5");
  await trace.getByRole("button", { name: "Next ▶" }).click();
  await expect(trace).toContainText("best becomes 3");
  await expect(trace.locator(".trace-changed")).toHaveCount(3); // w, w.length() and best all changed
  // Every control does something: ▶ plays the rest by itself, and at the end "Watch again" plays it again.
  await trace.getByRole("button", { name: "▶ Watch it run" }).click();
  await expect(trace.getByRole("button", { name: "⏸ Pause" })).toBeVisible();
  await expect(trace).toContainText("step 5 of 5", { timeout: 10_000 });
  await expect(trace.getByRole("button", { name: "▶ Watch it run" })).toBeVisible(); // stopped at the end
  await trace.getByRole("button", { name: "↻ Watch again" }).click();
  await expect(trace).toContainText("step 1 of 5");
  await expect(trace.getByRole("button", { name: "⏸ Pause" })).toBeVisible();
  await page.locator(".dot").nth(8).click(); // the greet task
  await expect(page.locator(".task-card")).toContainText('greet("Asha")');
  await expect(page.locator(".task-card")).toContainText('"Hello, Asha!"');
});
