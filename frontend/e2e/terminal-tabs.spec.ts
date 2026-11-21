/* A second terminal (owner, 21 November: lessons run a server in one terminal and send it requests from
   another). Each tab is its own shell; + opens one, × closes it, Run in terminal types into the one shown. */
import { expect, test, type Page } from "@playwright/test";

const visibleTerm = (page: Page) => page.locator(".bottom-body:not([hidden]) .xterm-rows");

test("a second terminal tab is its own shell", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("labbox.editor", JSON.stringify("classic")));
  const r = await page.request.post("/api/auth/signup", { data: { username: `tt${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  const auth = { headers: { Authorization: `Bearer ${token}` } };
  await page.request.post("/api/onboarding/skip", auth);
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);
  try {
    await page.goto("/labs/python-basics");
    await expect(visibleTerm(page)).toContainText("learner@python-basics", { timeout: 90_000 });
    await expect(page.getByRole("tab", { name: "Terminal", exact: true })).toBeVisible();

    await page.getByRole("button", { name: "Open another terminal" }).click();
    await expect(page.getByRole("tab", { name: "Terminal 2" })).toHaveAttribute("aria-selected", "true");
    await expect(visibleTerm(page)).toContainText("learner@python-basics", { timeout: 30_000 });
    await page.locator(".bottom-body:not([hidden]) .xterm-helper-textarea").focus();
    await page.keyboard.type("echo only-in-two");
    await page.keyboard.press("Enter");
    await expect(visibleTerm(page)).toContainText("only-in-two");

    await page.getByRole("tab", { name: "Terminal 1" }).click();
    await expect(visibleTerm(page)).toContainText("learner@python-basics");
    await expect(visibleTerm(page)).not.toContainText("only-in-two");

    await page.getByRole("button", { name: "Close terminal 2" }).click();
    await expect(page.getByRole("tab", { name: "Terminal", exact: true })).toHaveAttribute("aria-selected", "true");
  } finally {
    await page.request.post("/api/labs/python-basics/workspace/stop", auth);
  }
});
