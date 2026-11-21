/* Each lesson step opens the file it talks about (file= and line= in the lesson), and a task step opens
   its own task's file, so the lesson and the code on the right always match (owner, 21 November). */
import { expect, test } from "@playwright/test";

test("a lesson step opens its file and highlights its lines; a task step opens its task's file", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("labbox.editor", JSON.stringify("classic")));
  const r = await page.request.post("/api/auth/signup", { data: { username: `sf${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  await page.request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${token}` } });
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);
  try {
    await page.goto("/labs/spring-boot-first-api?chapter=04-app-startup");
    await expect(page.locator(".status-label", { hasText: "Running" })).toBeVisible({ timeout: 90_000 });

    // The step about SpringApplication.run opens the application class, with that line selected.
    await page.getByRole("button", { name: /^Step 3: What SpringApplication\.run does/ }).click();
    await expect(page.locator(".tab.active")).toContainText("ShopApiApplication.java");
    await expect(page.locator(".monaco-editor .view-lines")).toContainText("SpringApplication.run(ShopApiApplication.class, args);");
    await expect(page.locator(".monaco-editor .selected-text").first()).toBeVisible();

    // The @Value step opens the controller that uses it.
    await page.getByRole("button", { name: /^Step 10: Settings, read into your code: @Value/ }).click();
    await expect(page.locator(".tab.active")).toContainText("GreetingController.java");

    // A task step opens its own task's file (the settings file), not the chapter's first TODO.
    await page.getByRole("button", { name: /^Step 12: Your turn: set the greeting/ }).click();
    await expect(page.locator(".tab.active")).toContainText("application.properties");
  } finally {
    await page.request.post("/api/labs/spring-boot-first-api/workspace/stop", { headers: { Authorization: `Bearer ${token}` } });
  }
});
