/* The Aa menu: text size per area (lesson, tasks, editor, terminal), saved on this device. */
import { expect, test } from "@playwright/test";

test("text size: presets, a slider per area, kept after a reload, reset", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("labbox.editor", JSON.stringify("classic")));
  const r = await page.request.post("/api/auth/signup", { data: { username: `ts${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);
  await page.goto("/labs/python-basics");
  await expect(page.locator(".tab.active")).toContainText("hello.py", { timeout: 60_000 }); // chapter 1 opens its first task's file
  const zoom = (sel: string) => page.locator(sel).first().evaluate((e) => getComputedStyle(e).zoom);
  const editorFont = () => page.locator(".monaco-editor .view-lines").first().evaluate((e) => getComputedStyle(e).fontSize);
  await expect.poll(editorFont).toBe("15px");

  await page.getByRole("button", { name: "Text size" }).click();
  const menu = page.getByRole("dialog", { name: "Text size" });
  await menu.getByRole("button", { name: "L", exact: true }).click();
  await expect(menu.getByRole("button", { name: "L", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(menu.locator("output").first()).toHaveText("115%");
  expect(await zoom(".left-panel .lesson-scroll")).toBe("1.15");
  expect(await zoom(".left-panel .left-footer")).toBe("1.15");
  await expect.poll(editorFont).toBe("17px");

  // One area on its own: the preset is no longer "L".
  await menu.getByLabel("Terminal text size").fill("150");
  await expect(menu.locator(".ts-row", { hasText: "Terminal" }).locator("output")).toHaveText("150%");
  await expect(menu.getByRole("button", { name: "L", exact: true })).toHaveAttribute("aria-pressed", "false");
  await page.keyboard.press("Escape");
  await expect(menu).toBeHidden();

  await page.reload();
  await page.getByRole("button", { name: "Text size" }).click();
  await expect(menu.locator(".ts-row", { hasText: "Terminal" }).locator("output")).toHaveText("150%");
  expect(await zoom(".left-panel .lesson-scroll")).toBe("1.15");
  expect(JSON.parse((await page.evaluate(() => localStorage.getItem("labbox.textSize")))!)).toEqual({ lesson: 115, tasks: 115, editor: 115, terminal: 150 });

  await menu.getByRole("button", { name: "Reset" }).click();
  await expect(menu.getByRole("button", { name: "M", exact: true })).toHaveAttribute("aria-pressed", "true");
  expect(await zoom(".left-panel .lesson-scroll")).toBe("1");
});
