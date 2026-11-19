/* Offline completion in the editor: keywords, library calls the labs use, and snippets. No AI. */
import { expect, test } from "@playwright/test";

test("the editor suggests Python names and snippets", async ({ page }) => {
  const r = await page.request.post("/api/auth/signup", { data: { username: `ed${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);
  await page.goto("/labs/redis-in-practice");
  await page.locator(".tree-row", { hasText: "app.py" }).click({ timeout: 60_000 });
  await expect(page.locator(".tab.active")).toContainText("app.py");
  const editor = page.locator(".monaco-editor").first();
  await expect(editor).toBeVisible();

  await editor.click();
  await page.keyboard.press("Control+End");
  await page.keyboard.press("Enter");
  await page.keyboard.type("r.hge", { delay: 30 });
  const suggest = page.locator(".suggest-widget");
  await expect(suggest).toBeVisible();
  await expect(suggest).toContainText("hgetall");

  await page.keyboard.press("Escape");
  await page.keyboard.press("Control+a");
  await page.keyboard.type("ifma", { delay: 30 });
  await expect(suggest).toContainText("ifmain");
  await page.keyboard.press("Enter");
  await expect(page.locator(".view-lines")).toContainText('if __name__ == "__main__":');
  // Leave the learner's file as it was: undo everything typed here.
  for (let i = 0; i < 10; i++) await page.keyboard.press("Control+z");
});

test("AI completion can be switched off and stays off", async ({ page }) => {
  const r = await page.request.post("/api/auth/signup", { data: { username: `ai${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);
  await page.goto("/labs/python-basics");
  await page.locator(".tree-row", { hasText: "greet.py" }).click({ timeout: 60_000 });
  const toggle = page.getByRole("button", { name: /✦ AI (on|off)/ });
  await expect(toggle).toHaveText("✦ AI on");
  await toggle.click();
  await expect(toggle).toHaveText("✦ AI off");
  await page.reload();
  await page.locator(".tree-row", { hasText: "greet.py" }).click({ timeout: 60_000 });
  await expect(page.getByRole("button", { name: /✦ AI (on|off)/ })).toHaveText("✦ AI off");
});
