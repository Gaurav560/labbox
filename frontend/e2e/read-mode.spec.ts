import { expect, test } from "@playwright/test";

// Read mode (owner, 25 November): a first visit shows the lesson alone, starts no machine, and shows a step's code
// read-only; the task card and the Read / Action switch open the editor and terminal; the choice is remembered.
test.use({ storageState: { cookies: [], origins: [] } });

const LAB = "rag-vector-databases";
const CH = "why-rag";

test("read first, then action, and remembered", async ({ page, request }) => {
  const r = await request.post("/api/auth/signup", { data: { username: `read${Date.now() % 1_000_000_000}`, password: "secret123" } });
  const { token } = await r.json();
  const h = { Authorization: `Bearer ${token}` };
  await request.post("/api/onboarding/skip", { headers: h });
  await page.addInitScript((t) => localStorage.setItem("labbox.token", t), token);
  const steps: { type: string; file: string | null }[] = (await (await request.get(`/api/labs/${LAB}/chapters/${CH}`, { headers: h })).json()).steps;
  const fileStep = steps.findIndex((s) => s.type !== "task" && !!s.file);
  const taskStep = steps.findIndex((s) => s.type === "task");
  expect(fileStep).toBeGreaterThan(0);

  // Step 0 is far from a task: Read mode starts no machine at all.
  await page.goto(`/labs/${LAB}?chapter=${CH}&step=0`);
  await expect(page.getByRole("group", { name: "Mode" }).getByRole("button", { name: "Read" })).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".lesson")).toBeVisible();
  await expect(page.locator(".work-area")).toHaveCount(0);
  await page.waitForTimeout(3000);
  const ws = await (await request.get(`/api/labs/${LAB}/workspace/status`, { headers: h })).json();
  expect(ws.status).not.toBe("running");

  // The list of steps on the left, closed by default: every step by name, the current one marked; the panel button opens and closes it.
  const outline = page.getByRole("navigation", { name: "Scenes in this chapter" });
  await expect(outline).toHaveCount(0); // closed by default
  await page.getByRole("button", { name: "Show the list of scenes" }).click();
  await expect(outline.locator(".step-outline-item")).toHaveCount(steps.length);
  await expect(outline.locator("[aria-current=step]")).toHaveCount(1);
  await page.getByRole("button", { name: "Close the list of scenes" }).click();
  await expect(outline).toHaveCount(0);
  await page.getByRole("button", { name: "Show the list of scenes" }).click();
  await expect(outline).toBeVisible();

  // A step about a file shows those lines, read-only, with the step's own lines marked.
  await page.goto(`/labs/${LAB}?chapter=${CH}&step=${fileStep}`);
  await expect(page.locator(".read-code")).toBeVisible();
  await expect(page.locator(".read-code-path")).toHaveText(steps[fileStep].file!);
  await expect(page.locator(".read-code-line.is-marked").first()).toBeVisible();

  // A task step: the card opens Action mode, with the editor and terminal.
  await page.goto(`/labs/${LAB}?chapter=${CH}&step=${taskStep}`);
  await page.getByRole("button", { name: "Open Action mode" }).click();
  await expect(page.locator(".work-area")).toBeVisible({ timeout: 90_000 });
  await expect(page.getByRole("group", { name: "Mode" }).getByRole("button", { name: "Action" })).toHaveAttribute("aria-pressed", "true");

  // Remembered: a reload opens Action mode again; the switch goes back to Read.
  await page.reload();
  await expect(page.locator(".work-area")).toBeVisible({ timeout: 90_000 });
  await page.getByRole("group", { name: "Mode" }).getByRole("button", { name: "Read" }).click();
  await expect(page.locator(".work-area")).toHaveCount(0);
  await expect(page.locator(".read-task-card")).toBeVisible();
});
