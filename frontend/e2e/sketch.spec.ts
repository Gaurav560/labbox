/* A hand-drawn diagram that plays (the Excalidraw look, owner's sample, 21 November): Spring Boot's
   start-up in six steps. Next lights one step at a time; Play runs them all; nothing errors. */
import { expect, test } from "@playwright/test";

test("the start-up diagram plays step by step", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.addInitScript(() => localStorage.setItem("labbox.editor", JSON.stringify("classic")));
  const r = await page.request.post("/api/auth/signup", { data: { username: `sk${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  const auth = { headers: { Authorization: `Bearer ${token}` } };
  await page.request.post("/api/onboarding/skip", auth);
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);
  try {
    await page.goto("/labs/spring-boot-first-api?chapter=02-app-startup");
    await page.getByRole("button", { name: /^Step 2: What SpringApplication\.run does/ }).click();
    const fig = page.locator("figure.diagram").first();
    await expect(fig.getByRole("img")).toHaveAccessibleName(/SpringApplication\.run reads application\.properties/);
    await expect(fig.locator(".tl-step")).toHaveCount(6); // a timeline: one row per step
    await expect(fig.locator(".sketch-says")).toContainText("Press Play");

    await fig.getByRole("button", { name: "Next ▶" }).click();
    await expect(fig.locator(".sketch-says")).toContainText("Step 1 of 6.");
    await expect(fig.locator(".tl-step.tl-now")).toContainText("read application.properties");
    await fig.getByRole("button", { name: "Next ▶" }).click();
    await expect(fig.locator(".tl-step.tl-now")).toContainText("scan com.shop");
    await expect(fig.locator(".tl-step.tl-done")).toHaveCount(1);
    await fig.getByRole("button", { name: "◀ Back" }).click();
    await expect(fig.locator(".sketch-says")).toContainText("Step 1 of 6.");

    await fig.getByRole("button", { name: "▶ Play" }).click();
    await expect(fig.locator(".sketch-says")).toContainText("Step 6 of 6.", { timeout: 15_000 });
    await expect(fig.locator(".tl-step.tl-done")).toHaveCount(5);
    await expect(fig.getByRole("button", { name: "↻ Watch again" })).toBeVisible();
    expect(errors).toEqual([]);
  } finally {
    await page.request.post("/api/labs/spring-boot-first-api/workspace/stop", auth);
  }
});
