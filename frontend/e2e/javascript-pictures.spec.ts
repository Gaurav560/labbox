import { expect, test, type Locator } from "@playwright/test";
import type { ChapterContent, LabDetail } from "../src/api";

async function checkLettering(drawing: Locator, name: string, theme: string, code?: string) {
  await expect(drawing.locator(".pc-hand, .pc-label, .pc-title").first())
    .toHaveCSS("font-family", /Inter/);
  if (code) {
    const snippet = drawing.locator(".pc-code");
    await expect(snippet).toHaveText(code);
    await expect(snippet).toHaveCSS("font-family", /JetBrains Mono/);
  }
  const clipped = await drawing.evaluate(async svg => {
    await document.fonts.ready;
    const view = (svg as SVGSVGElement).viewBox.baseVal;
    return Array.from(svg.querySelectorAll("text")).filter(label => {
      const box = label.getBBox();
      return box.x < 0 || box.y < 0 || box.x + box.width > view.width || box.y + box.height > view.height;
    }).map(label => label.textContent);
  });
  expect(clipped, `${name} in ${theme}`).toEqual([]);
}

test("JavaScript teaches each concept with one distinct picture, where it is taught, in both themes", async ({ page, request }) => {
  const lab = "/api/labs/javascript-basics";
  const signup = await request.post("/api/auth/signup", {
    data: { username: `jspics${Date.now()}`, password: "secret123" },
  });
  expect(signup.ok()).toBeTruthy();
  const { token } = await signup.json();
  const headers = { Authorization: `Bearer ${token}` };
  await page.addInitScript((token: string) => {
    localStorage.setItem("labbox.token", token);
    localStorage.setItem("labbox.editor", JSON.stringify("classic"));
  }, token);

  const detail: LabDetail = await (await request.get(lab, { headers })).json();
  const seen = new Set<string>();
  try {
    await page.goto("/labs/javascript-basics");
    for (const chapter of detail.chapters) {
      const content: ChapterContent = await (await request.get(`${lab}/chapters/${chapter.id}`, { headers })).json();
      const concepts = new Map(content.steps.filter(s => s.type === "concept").map(s => [s.title, 0]));
      await page.getByLabel("Chapter", { exact: true }).selectOption(chapter.id);
      for (const [index, step] of content.steps.entries()) {
        const pictures = [...step.markdown.matchAll(/^:::picture\{name="([^"]+)"[^\n]*? concept="([^"]+)"\}\n([^\n]+)/gm)];
        expect(pictures.length).toBe((step.markdown.match(/^:::picture\{/gm) ?? []).length);
        expect(pictures.length).toBeLessThanOrEqual(1);
        if (!pictures.length) continue;
        const [directive, name, concept, caption] = pictures[0];
        const code = /\bcode=(["'])(.*?)\1/.exec(directive)?.[2];
        expect(concepts.has(concept), `${chapter.title}: ${concept}`).toBeTruthy();
        expect(["concept", "example"], `${chapter.title}: a picture on a ${step.type} step`).toContain(step.type);
        if (step.type === "concept") {
          expect(concept, `${chapter.title}: the picture belongs to the concept it sits on`).toBe(step.title);
          concepts.set(concept, concepts.get(concept)! + 1);
        }
        expect(seen.has(name), name).toBeFalsy();
        seen.add(name);

        await page.getByRole("button", { name: `Step ${index + 1}: ${step.title}`, exact: true }).click();
        if (step.type === "deep-dive") await page.locator(".deep-dive summary").click();
        const figure = page.locator(".step-card figure.picture");
        await expect(figure.locator("figcaption")).toHaveText(caption);
        const drawing = figure.getByRole("img");
        await expect(drawing).toHaveAccessibleName(/\S/);
        // Switch through the UI on each drawing so both palettes are exercised on the lesson itself.
        const theme = await page.locator("html").getAttribute("data-theme");
        expect(["light", "dark"]).toContain(theme);
        const nextTheme = theme === "dark" ? "light" : "dark";
        await checkLettering(drawing, name, theme!, code);
        await expect(drawing).toBeVisible();
        const canvas = () => figure.evaluate(el => getComputedStyle(el).backgroundColor);
        const firstCanvas = await canvas();
        await page.getByRole("button", { name: `Switch to ${nextTheme} theme` }).click();
        await expect(page.locator("html")).toHaveAttribute("data-theme", nextTheme);
        expect(await canvas()).not.toBe(firstCanvas);
        await checkLettering(drawing, name, nextTheme, code);
      }
      // Since the curiosity-first rewrite (22 November) some concept steps teach with a photo, a diagram or a run
      // instead: at most one picture each, never repeated.
      for (const [concept, count] of concepts) expect(count, concept ?? chapter.title).toBeLessThanOrEqual(1);
    }
    expect(seen.size).toBeGreaterThanOrEqual(30); // one distinct picture per idea, wherever an idea is taught with one
  } finally {
    await request.post(`${lab}/workspace/stop`, { headers });
  }
});
