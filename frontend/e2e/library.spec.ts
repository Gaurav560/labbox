/* The Library (owner, 24 November): a public page of books, research papers and tech blogs. A visitor reads it
   without an account; a learner finds it from the dashboard and filters it; an admin adds an item, finds it, and
   removes it again. */
import { execFileSync } from "node:child_process";
import { expect, test, type Page } from "@playwright/test";

const ROOT = new URL("../..", import.meta.url).pathname;

async function signup(page: Page, prefix: string) {
  const username = `${prefix}${Date.now() % 1_000_000_000}`;
  const r = await page.request.post("/api/auth/signup", { data: { username, password: "secret123" } });
  const body = await r.json();
  await page.request.post("/api/onboarding/skip", { headers: { Authorization: `Bearer ${body.token}` } });
  await page.goto("/");
  await page.evaluate((t) => localStorage.setItem("labbox.token", t), body.token as string);
  return username;
}

test("learners read the library; an admin adds and removes an item", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));

  // A visitor, with no account: the page, a Start here pick, links to the labs that practise each idea, Start free.
  await page.goto("/library");
  await expect(page.getByRole("heading", { level: 1, name: "Premium reads." })).toBeVisible();
  await expect(page.getByRole("article", { name: "Featured: AI Engineering" })).toBeVisible();
  await expect(page.locator(".lib-featured")).not.toContainText("Start here"); // no kicker on the card (owner, 25 November)
  await expect(page.getByRole("link", { name: "Start free" }).first()).toBeVisible();
  await expect(page.locator(".lib-updated")).toHaveText(/^Last updated \d{1,2} [A-Z][a-z]{2} \d{4}$/);
  await expect(page.locator(".lib-tile-updated").first()).toContainText(/^.*Last updated \d{1,2} [A-Z][a-z]{2}/);
  await expect(page.getByRole("link", { name: /^Practise it hands-on/ }).first()).toHaveAttribute("href", "/login?signup=1");

  // A learner finds the Library from the dashboard: three sections, each with items and a note.
  await signup(page, "libreader");
  await page.goto("/labs");
  await page.getByRole("link", { name: "Premium Reads" }).click();
  await expect(page).toHaveURL(/\/library$/);
  await expect(page.getByRole("heading", { level: 1, name: "Premium reads." })).toBeVisible();
  await expect(page.getByRole("link", { name: /^Practise it hands-on/ }).first()).toHaveAttribute("href", /^\/courses\//);
  await expect(page.getByRole("link", { name: "Edit the library" })).toHaveCount(0);
  const tabs = page.getByRole("navigation", { name: "Library sections" });
  await expect(page.getByRole("list", { name: "Books" }).getByRole("listitem").first()).toBeVisible();
  await tabs.getByRole("button", { name: /Research papers/ }).click();
  await expect(page).toHaveURL(/tab=paper/);
  const papers = page.getByRole("list", { name: "Research papers" });
  // Attention Is All You Need is the first paper, the Start here card (owner); the whole card opens it, no read button.
  const start = page.getByRole("article", { name: "Featured: Attention Is All You Need" });
  await expect(start.getByRole("link", { name: "Attention Is All You Need" })).toHaveAttribute("href", "https://arxiv.org/abs/1706.03762");
  await expect(page.getByRole("link", { name: /^(Read the paper|See the book|Visit the blog)/ })).toHaveCount(0);
  // The whole card opens the paper; the lab chip on it still opens the lab. "Free to read" is not shown (owner).
  const card = papers.getByRole("listitem").first();
  const cardHref = await card.getByRole("heading").getByRole("link").getAttribute("href");
  const at = async (target: import("@playwright/test").Locator) => {
    await target.scrollIntoViewIfNeeded();
    const box = (await target.boundingBox())!;
    return page.evaluate(([x, y]) => (document.elementFromPoint(x, y)?.closest("a") as HTMLAnchorElement | null)?.getAttribute("href"),
      [box.x + box.width / 2, box.y + box.height / 2]);
  };
  expect(await at(start)).toBe("https://arxiv.org/abs/1706.03762");
  expect(await at(start.locator(".lib-chip"))).toMatch(/^\/courses\//);
  expect(await at(card)).toBe(cardHref);
  expect(await at(card.locator(".lib-chip"))).toMatch(/^\/courses\//);
  await expect(page.getByText("Free to read", { exact: true })).toHaveCount(0);
  await page.getByRole("group", { name: /Filter research papers by topic/ }).getByRole("button", { name: /^Databases/ }).click();
  await expect(page.getByRole("link", { name: "Attention Is All You Need" })).toHaveCount(0);
  await expect(papers.getByRole("listitem").first()).toBeVisible();
  await tabs.getByRole("button", { name: /Tech blogs/ }).click();
  await expect(page.getByRole("list", { name: "Tech blogs" }).getByRole("listitem").first()).toBeVisible();

  // An admin adds a blog, sees it on the Library page, then removes it.
  const boss = await signup(page, "libadmin");
  execFileSync(`${ROOT}scripts/labbox`, ["admin", "grant", boss], { cwd: ROOT });
  const title = `Test blog ${Date.now()}`;
  try {
    await page.goto("/admin?tab=library");
    const form = page.getByRole("form", { name: "Add a library item" });
    await form.getByRole("combobox", { name: "Section", exact: true }).selectOption("blog");
    await form.getByLabel("Title").fill(title);
    await form.getByLabel("Link").fill("https://example.org/");
    await form.getByLabel("Topic").fill("Testing");
    await form.getByLabel(/^Why read it/).fill("Added by the browser test.");
    // A picture, as an admin would upload a cover: a tiny PNG, stored by LabBox as WebP.
    const png = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "base64");
    await form.getByLabel(/^Picture/).setInputFiles({ name: "cover.png", mimeType: "image/png", buffer: png });
    await form.getByRole("button", { name: "Add to the library" }).click();
    await expect(page.getByRole("link", { name: title })).toBeVisible();

    await page.goto("/library?tab=blog");
    await expect(page.getByRole("link", { name: title })).toBeVisible();
    await expect(page.getByText("Added by the browser test.")).toHaveCount(0);  // blogs show no description
    await expect(page.getByRole("img", { name: `The ${title} home page` })).toHaveAttribute("src", /^\/api\/library\/images\/upload-/);

    await page.goto("/admin?tab=library");
    await page.getByRole("group", { name: "Section" }).getByRole("button", { name: "Tech blogs" }).click();
    page.once("dialog", (d) => d.accept());
    await page.getByRole("row", { name: new RegExp(title) }).getByRole("button", { name: "Remove" }).click();
    await expect(page.getByRole("link", { name: title })).toHaveCount(0);
  } finally {
    execFileSync(`${ROOT}scripts/labbox`, ["admin", "revoke", boss], { cwd: ROOT });
  }
  expect(errors).toEqual([]);
});
