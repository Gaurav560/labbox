import { expect, test } from "@playwright/test";

// Action mode can hide the whole lesson panel (owner, 25 November): the editor and terminal take the page, a slim
// rail keeps "Show the lesson" and Check, and the choice survives a reload.
test("action mode hides and shows the lesson panel", async ({ page, request }) => {
  const r = await request.post("/api/auth/signup", { data: { username: `panel${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  await request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${token}` } });
  await page.addInitScript((t) => { localStorage.setItem("labbox.token", t); localStorage.setItem("labbox.editor", JSON.stringify("classic")); }, token);
  await page.goto("/labs/javascript-basics");
  await expect(page.locator(".work-area")).toBeVisible({ timeout: 120_000 });
  const before = (await page.locator(".work-area").boundingBox())!.width;
  await page.getByRole("button", { name: "Hide the lesson" }).click();
  await expect(page.locator(".left-panel")).toBeHidden();
  await expect(page.getByRole("button", { name: "Check" })).toBeVisible(); // Check stays one click away
  expect((await page.locator(".work-area").boundingBox())!.width).toBeGreaterThan(before + 200);
  await page.reload();
  await expect(page.locator(".lesson-rail")).toBeVisible({ timeout: 120_000 });
  await page.getByRole("button", { name: "Show the lesson" }).click();
  await expect(page.locator(".left-panel")).toBeVisible();
  await expect(page.getByRole("button", { name: "Hide the lesson" })).toBeVisible();
});
