/* Certificates (owner, 27 November): a learner who passed 80% of a lab's tasks claims its certificate on the course
   page with their full name, lands on its public page with the share buttons, the share address carries the card
   tags LinkedIn and X read, a visitor sees it without logging in, hiding it takes it away, and My certificates
   lists it. Passing the tasks is done straight in the development database (checks would take minutes). */
import { execFileSync } from "node:child_process";
import { expect, test, type Page } from "@playwright/test";

const ROOT = new URL("../..", import.meta.url).pathname;
const LAB = "python-basics";

async function signup(page: Page) {
  const username = `cert${Date.now() % 1_000_000_000}`;
  const r = await page.request.post("/api/auth/signup", { data: { username, password: "secret123" } });
  const body = await r.json();
  await page.request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${body.token}` } });
  return { username, token: body.token as string, id: body.user.id as number };
}

function passFourFifths(userId: number, lab: string) {
  const code = `
import math, sys
from sqlmodel import Session
from app.config import get_settings
from app.db import engine
from app.labs import get_lab, init_labs
from app.models import TaskProgress, utcnow
init_labs(get_settings().LABS_DIR)
uid, lab = int(sys.argv[1]), get_lab(sys.argv[2])
tasks = [(c.id, t.id) for c in lab.chapters for t in c.tasks]
with Session(engine) as s:
    for ch, t in tasks[: math.ceil(0.8 * len(tasks))]:
        s.add(TaskProgress(user_id=uid, lab_id=lab.id, task_id=t, chapter_id=ch, passed=True, first_passed_at=utcnow()))
    s.commit()
`;
  execFileSync(`${ROOT}backend/.venv/bin/python`, ["-c", code, String(userId), lab], { cwd: `${ROOT}backend` });
}

test("finish a lab, claim its certificate, share it, hide it", async ({ page, browser }) => {
  const learner = await signup(page);
  passFourFifths(learner.id, LAB);
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), learner.token);

  // The course page: the certificate is ready; the first one asks for the full name.
  await page.goto(`/courses/${LAB}`);
  const box = page.getByRole("form", { name: "Get your certificate" });
  await expect(box).toContainText("Your certificate is ready");
  await box.getByRole("textbox").fill("Meera Iyer");
  await box.getByRole("button", { name: "Get my certificate" }).click();
  await expect(page).toHaveURL(/\/certificates\/[A-Z2-9]{8}$/);
  const id = page.url().split("/").pop()!;

  // Its page: the name, the lab, the share buttons (LinkedIn's form filled in with the certificate's id).
  await expect(page.locator(".cert-name")).toHaveText("Meera Iyer");
  await expect(page.locator(".cert-sheet")).toContainText(`Certificate ${id}`);
  const profile = page.getByRole("link", { name: "Add to LinkedIn profile" });
  await expect(profile).toHaveAttribute("href", new RegExp(`linkedin\\.com/profile/add.*certId=${id}`));
  await expect(page.getByRole("link", { name: "Post on X" })).toHaveAttribute("href", /x\.com\/intent\/post/);
  await expect(page.locator(".cert-share-url code")).toHaveText(new RegExp(`/c/${id}$`));

  // The share address: the card tags LinkedIn and X read, and the picture.
  const share = await page.request.get(`/c/${id}`);
  expect(share.ok()).toBeTruthy();
  const html = await share.text();
  expect(html).toContain('property="og:title" content="Meera Iyer completed');
  expect(html).toContain(`/api/certificates/${id}/image.jpg`);
  const image = await page.request.get(`/api/certificates/${id}/image.jpg`);
  expect(image.headers()["content-type"]).toBe("image/jpeg");

  // A visitor, not logged in, sees it; once hidden, they do not.
  const visitor = await browser.newPage();
  await visitor.goto(`/certificates/${id}`);
  await expect(visitor.locator(".cert-name")).toHaveText("Meera Iyer");
  await page.getByRole("button", { name: "Hide this certificate" }).click();
  await expect(page.locator(".cert-hidden-note")).toBeVisible();
  await visitor.reload();
  await expect(visitor.getByRole("heading", { name: "This certificate is not available" })).toBeVisible();
  await page.getByRole("button", { name: "Make it public again" }).click();
  await expect(page.locator(".cert-hidden-note")).toHaveCount(0);
  await visitor.close();

  // My certificates, and the course page now links to it.
  await page.goto("/certificates");
  await expect(page.getByRole("link", { name: /Python/ })).toHaveAttribute("href", `/certificates/${id}`);
  await page.goto(`/courses/${LAB}`);
  await expect(page.getByRole("region", { name: "Your certificate" })).toContainText("Meera Iyer");
});
