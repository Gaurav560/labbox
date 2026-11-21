/* A track's skill map as a plain roadmap (owner, 21 November): every topic a step in learning order, and every
   topic's chapters opening their lab at that chapter. */
import { expect, test } from "@playwright/test";

test("the track roadmap: find a topic, open its chapter in the lab", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const r = await page.request.post("/api/auth/signup", { data: { username: `rm${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  await page.request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${token}` } });
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);

  await page.goto("/tracks/frameworks");
  await expect(page.getByRole("list", { name: "Roadmap" })).toBeVisible();
  await expect(page.locator(".skill-node", { hasText: "Spring Boot, HTTP and Maven" })).toContainText("Start");

  // Every topic's card lists its chapters, each an Open link into the lab.
  const panel = page.locator(".road-step", { hasText: "Relationships, paging and N+1" });
  await expect(panel).toContainText("Spring Boot · Ch 21");
  await panel.getByRole("link", { name: "Open Relationships and the N+1 problem" }).click();
  await expect(page).toHaveURL(/\/labs\/spring-boot-first-api\?chapter=21-relationships$/);
  await expect(page.locator(".step-count")).toBeVisible();
  expect(errors).toEqual([]);
  await page.request.post("/api/labs/spring-boot-first-api/workspace/stop", { headers: { Authorization: `Bearer ${token}` } });
});
