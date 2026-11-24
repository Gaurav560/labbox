/* Lesson photos always load (owner, 24 November: "sometimes it fetches on my machine, sometimes it does not").
   Photos are files inside LabBox; a chapter fetches all of its photos as soon as it opens, and a photo whose load
   fails is tried again by itself. Reading mode (phone width) starts no machine, so this test needs none. */
import { expect, test } from "@playwright/test";

test.use({ viewport: { width: 390, height: 844 } });

test("a lesson photo whose first load fails still appears", async ({ page, request }) => {
  const signup = await request.post("/api/auth/signup", { data: { username: `photo${Date.now()}`, password: "secret123" } });
  const { token } = await signup.json();
  await request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${token}` } });
  await page.addInitScript((t: string) => localStorage.setItem("labbox.token", t), token);

  // Every request for the tiger photo fails twice, as on a connection that drops for a moment.
  let tries = 0;
  await page.route(/\/lesson-images\/rag\/tiger\.webp/, (route) => (++tries <= 2 ? route.abort() : route.continue()));
  // The chapter's photos are requested as soon as it opens, before their steps are shown.
  const notes = page.waitForRequest(/\/lesson-images\/rag\/rag-01-notes\.webp/);

  await page.goto("/labs/rag-vector-databases?chapter=why-rag");
  await expect(page.locator(".step-count")).toHaveText(/Step 1 of \d+/);
  await notes;  // the recap's notes page, 13 steps ahead, is already on its way

  const photo = page.locator("figure.lesson-photo img").first();
  await expect(photo).toBeVisible();
  await expect.poll(() => photo.evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth > 0), { timeout: 15_000 }).toBe(true);
  expect(tries).toBeGreaterThanOrEqual(3);
});
