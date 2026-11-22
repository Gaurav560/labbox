import { expect, test } from "@playwright/test";

// Step 2 of the owner's UX review: one clear next step, a dashboard landing, and checks that never call
// a task the learner has not reached yet a failure.
test("a confident start: start here, continue where you left off, coming-up tasks", async ({ page, request }) => {
  const signup = await request.post("/api/auth/signup", { data: { username: `next${Date.now()}`, password: "secret123" } });
  const { token } = await signup.json();
  const headers = { Authorization: `Bearer ${token}` };
  await request.post("/api/onboarding/skip", { headers });
  await page.addInitScript((t: string) => {
    localStorage.setItem("labbox.token", t);
    localStorage.setItem("labbox.editor", JSON.stringify("classic"));
  }, token);
  try {
    // Signed in, / is the dashboard, and a new learner gets one "Start here" card.
    await page.goto("/");
    await expect(page).toHaveURL(/\/labs$/);
    const card = page.getByRole("region", { name: "Start here" });
    await expect(card).toContainText("Python from zero");
    // The marketing page is still there for anyone who asks for it.
    await page.goto("/?home");
    await expect(page.getByRole("link", { name: /Continue learning/ }).first()).toBeVisible();

    // A check before reaching any task: nothing is shown as failing.
    await page.goto("/labs/javascript-basics");
    await expect(page.locator(".status-label", { hasText: "Running" })).toBeVisible({ timeout: 90_000 });
    await page.getByRole("button", { name: "Check" }).last().click();
    await expect(page.locator(".check-drawer .drawer-title")).toHaveText("Your tasks are coming up", { timeout: 60_000 });
    await expect(page.locator(".check-drawer .res-fail")).toHaveCount(0);
    await expect(page.locator(".check-drawer .res-upcoming")).toHaveCount(2);
    await expect(page.locator(".task-dot.is-fail")).toHaveCount(0);

    // After moving on: the dashboard continues exactly there.
    await request.put("/api/labs/javascript-basics/chapters/04-loops/progress", { headers, data: { current_step: 5 } });
    await page.goto("/labs");
    const cont = page.getByRole("region", { name: "Continue where you left off" });
    await expect(cont).toContainText("Chapter 5 of 15: Loops");
    await cont.getByRole("link", { name: "Continue", exact: true }).click();
    await expect(page).toHaveURL(/\/labs\/javascript-basics\?chapter=04-loops$/);
    await expect(page.locator(".step-count")).toHaveText("Step 6 of 14");
  } finally {
    await request.post("/api/labs/javascript-basics/workspace/stop", { headers });
  }
});
