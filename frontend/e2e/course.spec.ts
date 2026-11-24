import { expect, test } from "@playwright/test";

// Owner, 22 November: the dashboard deck takes the colour of the lab it continues, and a lab card opens that
// lab's own page first; its buttons and chapters then open the lab (lesson, editor and terminal).
test("a lab card opens the lab's page; the feature wears the category's print", async ({ page, request }) => {
  const signup = await request.post("/api/auth/signup", { data: { username: `course${Date.now()}`, password: "secret123" } });
  const { token } = await signup.json();
  const headers = { Authorization: `Bearer ${token}` };
  await request.post("/api/onboarding/skip", { headers });
  await request.put("/api/labs/go-basics/chapters/02-numbers-and-text/progress", { headers, data: { current_step: 3 } });
  await page.addInitScript((t: string) => localStorage.setItem("labbox.token", t), token);

  await page.goto("/labs");
  const deck = page.getByRole("region", { name: "Continue where you left off" });
  await expect(deck).toContainText("Go from zero", { timeout: 30_000 }); // slow under a full parallel run
  // Ukiyo: the feature shows the category's woodblock print (Go is a language: the sun behind Fuji).
  await expect(deck.locator(".u-feature-art .u-print")).toBeVisible();
  await expect(deck).toContainText("Languages");
  await expect(deck.getByRole("link", { name: "Continue", exact: true })).toHaveAttribute("href", "/labs/go-basics?chapter=02-numbers-and-text");

  await page.locator(".u-row", { hasText: "Go from zero" }).click();
  await expect(page).toHaveURL(/\/courses\/go-basics$/);
  await expect(page.getByRole("heading", { level: 1, name: "Go from zero" })).toBeVisible();
  await expect(page.locator(".metro-now")).toContainText("Numbers and text"); // the chapters as a metro map
  await expect(page.locator(".metro-now")).toContainText("You are here");
  await expect(page.locator(".course-where")).toContainText("step 4 of");

  await page.getByRole("link", { name: /^Continue: Chapter \d+ →$/ }).click(); // count-free: courses grow
  await expect(page).toHaveURL(/\/labs\/go-basics\?chapter=02-numbers-and-text$/);
  await expect(page.locator(".step-count")).toHaveText(/^Step 4 of/);

  await request.put("/api/labs/sql-from-zero/chapters/01-select-and-where/progress", { headers, data: { current_step: 1 } });
  await page.goto("/labs");
  await expect(deck).toContainText("SQL", { timeout: 30_000 });
  await expect(deck).toContainText("Databases");  // and SQL gets the databases print

  await page.goto("/courses/go-basics");
  await expect(page.getByRole("heading", { name: "Skill map" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "What you will learn" })).toHaveCount(0);
  // Every lab has its own woodblock print, credited under it (Ukiyo).
  await expect(page.locator(".u-course-figure img.u-labprint")).toHaveAttribute("src", "/ukiyo/labs/go-basics.webp");
  await expect(page.locator(".u-print-credit")).toHaveText("Katsushika Hokusai, Hodogaya on the Tōkaidō, about 1831");
  await page.getByRole("link", { name: "01 Your first Go program" }).click();
  await expect(page).toHaveURL(/\/labs\/go-basics\?chapter=hello-go$/);

  // Every subtopic opens its own lesson step; course parts are the map's lines.
  await page.goto("/courses/spring-boot-first-api");
  await expect(page.locator(".metro-line-name", { hasText: "Production basics" })).toHaveCount(1); // the parts name their lines on the map
  const beans = page.locator(".metro-station", { hasText: "Beans and the application context" });
  await beans.getByRole("link", { name: "How a class becomes a bean" }).click();
  await expect(page).toHaveURL(/chapter=05-beans&step=4$/);
  await expect(page.locator(".step-count")).toHaveText(/^Step 5 of/);

  // The old Skill maps section is gone; its links land on the course page or the dashboard.
  await page.goto("/skills/go-basics");
  await expect(page).toHaveURL(/\/courses\/go-basics$/);
  await page.goto("/tracks/languages");
  await expect(page).toHaveURL(/\/labs$/);
  await expect(page.locator(".topbar").getByRole("link", { name: /Skill maps/ })).toHaveCount(0);
});
