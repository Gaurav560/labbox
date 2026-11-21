import { expect, test } from "@playwright/test";

// Owner, 22 November: level, streak and stars sit in a profile panel; an Exit button replaces "Log out".
test("the profile panel shows level, streak and stars, and Exit signs out", async ({ page, request }) => {
  const { token } = await (await request.post("/api/auth/signup", { data: { username: `prof${Date.now()}`, password: "secret123" } })).json();
  await request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${token}` } });
  await page.addInitScript((t: string) => { if (!sessionStorage.getItem("seeded")) { localStorage.setItem("labbox.token", t); sessionStorage.setItem("seeded", "1"); } }, token);

  await page.goto("/labs");
  const bar = page.locator(".topbar");
  await expect(bar.getByRole("button", { name: "Log out" })).toHaveCount(0);
  await expect(bar.getByLabel(/day streak/)).toHaveCount(0); // not in the bar itself any more
  await bar.getByRole("button", { name: /^Profile/ }).click();
  const panel = page.getByRole("dialog", { name: "Profile" });
  await expect(panel.getByLabel("Level 1")).toHaveText("Lv 1");
  await expect(panel.getByLabel(/day streak/)).toHaveText("🔥 0");
  await expect(panel.getByLabel(/XP$/)).toHaveText("⭐ 0");
  await expect(panel).toContainText("XP to level 2");
  await page.keyboard.press("Escape");
  await expect(panel).toBeHidden();

  await bar.getByRole("button", { name: /^Profile/ }).click();
  await panel.getByRole("button", { name: "Exit" }).click();
  await expect(page).toHaveURL(/\/$|\/login/);
  expect(await page.evaluate(() => localStorage.getItem("labbox.token"))).toBeNull();
});
