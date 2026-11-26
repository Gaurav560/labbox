/* Signing a test account in (owner, 27 November: the login page has only Google and GitHub, which cannot run in a
   test). Accounts are made through the API (PASSWORD_LOGIN is on for development only), and the login token goes where
   the app keeps it. A new account then lands where a real new learner would: onboarding. */
import type { Page } from "@playwright/test";

export async function signIn(page: Page, username: string, opts: { first?: boolean } = {}): Promise<string> {
  const path = opts.first ? "/api/auth/signup" : "/api/auth/login";
  const r = await page.request.post(path, { data: { username, password: "secret123" } });
  if (!r.ok()) throw new Error(`${path} failed: ${r.status()} ${await r.text()}`);
  const { token } = (await r.json()) as { token: string };
  await page.goto("/login");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);
  await page.goto("/labs");
  return token;
}
