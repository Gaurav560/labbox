/* The skill map as a 3D roadmap (owner, 21 November): a WebGL board, every topic in the side panel, and every
   topic's chapters opening their lab at that chapter. */
import { expect, test } from "@playwright/test";

test("the 3D roadmap: choose a topic, open its chapter in the lab", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const r = await page.request.post("/api/auth/signup", { data: { username: `rm${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  await page.request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${token}` } });
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);

  await page.goto("/tracks/frameworks");
  await expect(page.locator(".roadmap3d canvas")).toBeVisible();          // the 3D board
  await expect(page.locator(".skill-node", { hasText: "Spring Boot, HTTP and Maven" })).toContainText("Start");

  // Choose a topic in the list: the panel shows its chapters, each with an Open link into the lab.
  await page.locator(".topic-list button", { hasText: "Relationships, paging and N+1" }).click();
  const panel = page.locator(".topic-details");
  await expect(panel).toContainText("Spring Boot · Ch 21");
  await expect(panel).toContainText("Best after");
  await panel.getByRole("link", { name: "Open Relationships and the N+1 problem" }).click();
  await expect(page).toHaveURL(/\/labs\/spring-boot-first-api\?chapter=21-relationships$/);
  await expect(page.locator(".step-count")).toBeVisible();
  expect(errors).toEqual([]);
  await page.request.post("/api/labs/spring-boot-first-api/workspace/stop", { headers: { Authorization: `Bearer ${token}` } });
});
