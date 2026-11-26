/* Sign in with Google and GitHub (owner, 27 November). The providers cannot run in a test, so the server's answers
   are faked in the browser: the buttons appear when the server lists providers and point at its start addresses; a
   return with ?oauth=<code> signs the learner in (the code swapped for a real login made here); a refused sign-in
   says why. The server side of the flow is tested in backend/tests/test_oauth.py. */
import { expect, test } from "@playwright/test";

test("Google and GitHub buttons, and coming back signed in", async ({ page }) => {
  // A real account whose login the faked exchange hands back.
  const username = `oauth${Date.now() % 1_000_000_000}`;
  const made = await (await page.request.post("/api/auth/signup", { data: { username, password: "secret123" } })).json();
  await page.request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${made.token}` } });

  await page.route("**/api/auth/options", (r) => r.fulfill({ json: { signup: true, providers: ["google", "github"] } }));
  await page.route("**/api/auth/oauth/exchange", (r) => r.fulfill({ json: { ...made, new: false } }));

  await page.goto("/login?next=/certificates");
  const google = page.getByRole("link", { name: "Continue with Google" });
  const github = page.getByRole("link", { name: "Continue with GitHub" });
  await expect(google).toHaveAttribute("href", "/api/auth/oauth/google/start?next=%2Fcertificates");
  await expect(github).toHaveAttribute("href", "/api/auth/oauth/github/start?next=%2Fcertificates");
  // Google and GitHub only (owner, 27 November): no username or password form.
  await expect(page.getByLabel("Username")).toHaveCount(0);
  await expect(page.getByLabel("Password")).toHaveCount(0);

  // Back from the provider: the one-time code becomes a login, and the page goes where the learner was heading.
  await page.goto("/login?oauth=one-time-code&next=/certificates");
  await expect(page).toHaveURL(/\/certificates$/);
  await expect(page.getByRole("heading", { name: "My certificates" })).toBeVisible();
  expect(await page.evaluate(() => localStorage.getItem("labbox.token"))).toBe(made.token);
});

test("a refused sign-in says why, and no buttons without keys", async ({ page }) => {
  await page.route("**/api/auth/options", (r) => r.fulfill({ json: { signup: false, providers: [] } }));
  await page.goto("/login?oauth_error=closed&provider=github");
  await expect(page.getByRole("alert")).toContainText("this GitHub account has no LabBox account yet");
  await expect(page.getByRole("link", { name: "Continue with Google" })).toHaveCount(0);
});
