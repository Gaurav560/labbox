/* At most a few labs at a time (owner, 26 November). An admin gives one learner a limit of 2 (never the site's
   setting: other tests run at the same time). The learner sees the slot strip and locked tiles; a locked lab's
   lesson link lands on its course page, which unlocks it; with both slots used, a third lab cannot be unlocked;
   the admin's Lab access tab lists the learner as an exception, and the Learners tab shows the same limit. */
import { execFileSync } from "node:child_process";
import { expect, test, type Page } from "@playwright/test";

const ROOT = new URL("../..", import.meta.url).pathname;
const FIRST = "python-collections";
const SECOND = "fastapi-first-api";
const THIRD = "java-collections";

async function signup(page: Page, prefix: string) {
  const username = `${prefix}${Date.now() % 1_000_000_000}`;
  const r = await page.request.post("/api/auth/signup", { data: { username, password: "secret123" } });
  const body = await r.json();
  await page.request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${body.token}` } });
  return { username, token: body.token as string, id: body.user.id as number };
}

async function loginAs(page: Page, token: string) {
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), token);
}

test("a learner with two slots: locked labs, unlock, full", async ({ page }) => {
  const learner = await signup(page, "slotlearner");
  const boss = await signup(page, "slotboss");
  execFileSync(`${ROOT}scripts/labbox`, ["admin", "grant", boss.username], { cwd: ROOT });
  try {
    const set = await page.request.put(`/api/admin/learners/${learner.id}/lab-limit`, {
      headers: { Authorization: `Bearer ${boss.token}` }, data: { lab_limit: 2 } });
    expect(set.ok()).toBeTruthy();

    // The Lab access tab: the rule in one sentence, and this learner among the exceptions; the Learners tab shows
    // the same limit on the learner's row. The site's setting is never changed here (other tests run meanwhile).
    await loginAs(page, boss.token);
    await page.goto("/admin?tab=access");
    await expect(page.getByRole("heading", { name: "Lab access" })).toBeVisible();
    await expect(page.locator(".acc-sentence")).toContainText(/every lab|at a time/);
    await expect(page.getByRole("combobox", { name: `Lab limit for ${learner.username}` })).toHaveValue("2");
    await page.goto("/admin?tab=learners");
    await page.getByRole("searchbox", { name: "Search username" }).fill(learner.username);
    await expect(page.getByRole("combobox", { name: `Lab limit for ${learner.username}` })).toHaveValue("2");
  } finally {
    execFileSync(`${ROOT}scripts/labbox`, ["admin", "revoke", boss.username], { cwd: ROOT });
  }

  await loginAs(page, learner.token);
  await page.goto("/labs");
  await expect(page.getByRole("region", { name: "Your lab slots" })).toContainText("0 of 2 in use");
  await expect(page.locator(".u-row.is-locked").first()).toBeVisible();

  // A lesson link of a locked lab lands on its course page: no lesson, no links into it, one Unlock button.
  await page.goto(`/labs/${FIRST}`);
  await expect(page).toHaveURL(new RegExp(`/courses/${FIRST}$`));
  await expect(page.getByText("This lab is locked")).toBeVisible();
  await expect(page.locator(".course-syllabus a")).toHaveCount(0);
  await page.getByRole("button", { name: "Unlock this lab" }).click();
  await expect(page.locator(".course-go")).toContainText("Start");
  await expect(page.locator(".course-slot-note")).toContainText("uses one of your 2 slots");
  await expect(page.locator(".course-syllabus a").first()).toBeVisible();

  // The second slot, then a third lab: its button is off and the page says how a slot frees itself.
  expect((await page.request.post(`/api/labs/${SECOND}/unlock`, { headers: { Authorization: `Bearer ${learner.token}` } })).ok()).toBeTruthy();
  await page.goto(`/courses/${THIRD}`);
  await expect(page.getByRole("button", { name: "Unlock this lab" })).toBeDisabled();
  await expect(page.locator(".course-lock")).toContainText("All 2 are in use");
  await expect(page.locator(".course-lock")).toContainText("80% of its tasks");

  // The unlocked lab opens as usual.
  await page.goto(`/labs/${FIRST}`);
  await expect(page).toHaveURL(new RegExp(`/labs/${FIRST}`));
  await expect(page.locator(".lesson")).toBeVisible();
  await page.goto("/labs");
  await expect(page.getByRole("region", { name: "Your lab slots" })).toContainText("2 of 2 in use");
});
