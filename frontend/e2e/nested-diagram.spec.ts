/* Sets inside sets as nested circles: LangChain4j chapter 1's AI circles. Once an animation (owner, 23 November);
   since the lesson rewrite (26 November) a still picture with every circle, its meaning and an example at once.
   Phone width, so no machine starts. */
import { expect, test } from "@playwright/test";

test("the AI circles show every circle inside the one before", async ({ page, request }) => {
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
  // Since the LangChain4j rewrite (26 November) the circles are a still picture: every circle at once, no player.
  await expect(fig.getByRole("img")).toHaveAccessibleName(/^Artificial intelligence contains machine learning/);
  for (const name of ["Artificial intelligence", "Machine learning", "Deep learning", "Generative AI", "a large language model"]) {
    await expect(fig.getByRole("img")).toContainText(name);
  }
  await expect(fig.getByRole("button", { name: "▶ Play" })).toHaveCount(0);
  expect(errors).toEqual([]);
});
