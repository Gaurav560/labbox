/* The Skill maps section (owner, 21 November): a landing page with every lab and track, and every lab a metro
   map, one line per course part and one station per chapter, where every station opens its chapter. */
import { expect, test } from "@playwright/test";

test("skill maps: from the landing page to a lab's road, into a chapter", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const r = await page.request.post("/api/auth/signup", { data: { username: `sm${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  const auth = { headers: { Authorization: `Bearer ${token}` } };
  await page.request.post("/api/onboarding/skip", auth);
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);

  await page.goto("/labs");
  await page.getByRole("link", { name: /Skill maps/ }).click();
  await expect(page).toHaveURL(/\/skills$/);
  await page.locator(".skill-card", { hasText: "Spring Boot" }).click();
  await expect(page).toHaveURL(/\/skills\/spring-boot-first-api$/);
  const road = page.getByRole("list", { name: "Roadmap" });
  await expect(road.locator(".metro-station")).toHaveCount(31);
  // One line per course part.
  await expect(page.getByRole("list", { name: "Lines" })).toContainText("Foundations");
  await expect(page.getByRole("list", { name: "Lines" })).toContainText("Production basics");

  // You start at the first chapter not done; every step opens its chapter.
  await expect(road.locator(".metro-now")).toContainText("You are here");
  await expect(page.locator(".map-ring")).toContainText("0%");
  await road.getByRole("link", { name: "06 Dependency injection in depth" }).click();
  await expect(page).toHaveURL(/\/labs\/spring-boot-first-api\?chapter=06-dependency-injection$/);
  expect(errors).toEqual([]);
  await page.request.post("/api/labs/spring-boot-first-api/workspace/stop", auth);
});
