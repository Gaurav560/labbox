/* Sets inside sets as nested ovals (owner, 23 November: "wasn't this better as a Venn diagram animation?"):
   LangChain4j chapter 1's AI circles. Next lights the ovals from the biggest to the smallest; the ones not
   reached yet stay faint; Play runs to the end. Phone width, so no machine starts. */
import { expect, test } from "@playwright/test";

test("the AI circles play from the biggest to the smallest", async ({ page, request }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const signup = await request.post("/api/auth/signup", { data: { username: `nest${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await signup.json();
  await request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${token}` } });
  await page.addInitScript((t: string) => localStorage.setItem("labbox.token", t), token);
  await page.setViewportSize({ width: 390, height: 900 });

  await page.goto("/labs/langchain4j?chapter=ai-basics");
  await page.getByRole("button", { name: /^Scene 2:/ }).click();
  const fig = page.locator("figure.diagram").first();
  await expect(fig.getByRole("img")).toHaveAccessibleName(/artificial intelligence contains machine learning/);
  await expect(fig.locator(".nest")).toHaveCount(5);
  await expect(fig.locator(".nest-idle")).toHaveCount(5);

  await fig.getByRole("button", { name: "Next ▶" }).click();
  await expect(fig.locator(".sketch-says")).toContainText("Step 1 of 5.");
  await expect(fig.locator(".nest-now")).toContainText("Artificial intelligence");
  await expect(fig.locator(".nest-off")).toHaveCount(4);
  await fig.getByRole("button", { name: "Next ▶" }).click();
  await expect(fig.locator(".nest-now")).toContainText("Machine learning");
  await expect(fig.locator(".nest-lit")).toHaveCount(1);

  await fig.getByRole("button", { name: "▶ Play" }).click();
  await expect(fig.locator(".sketch-says")).toContainText("Step 5 of 5.", { timeout: 15_000 });
  await expect(fig.locator(".nest-now")).toContainText("LLM");
  await expect(fig.locator(".nest-lit")).toHaveCount(4);
  await expect(fig.getByRole("button", { name: "↻ Watch again" })).toBeVisible();
  expect(errors).toEqual([]);
});
