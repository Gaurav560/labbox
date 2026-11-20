import { expect, test, type Locator } from "@playwright/test";

function contrast(first: string, second: string) {
  function luminance(rgb: string) {
    const [r, g, b] = rgb.match(/\d+/g)!.map(channel => {
      const v = Number(channel) / 255;
      return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }
  const a = luminance(first);
  const b = luminance(second);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

async function appearance(figure: Locator) {
  return figure.evaluate(async el => {
    await document.fonts.ready;
    const svg = el.querySelector("svg")!;
    const node = svg.querySelector("rect")!;
    const arrow = svg.querySelector("[marker-end]")!;
    const head = svg.querySelector("marker")!;
    const size = (e: Element) => [e.clientWidth, e.clientHeight];
    return {
      frame: getComputedStyle(el).backgroundColor,
      fill: getComputedStyle(node).fill,
      text: getComputedStyle(svg.querySelector(".dg-box text")!).fill,
      caption: getComputedStyle(el.querySelector("figcaption")!).color,
      line: getComputedStyle(arrow).stroke,
      head: getComputedStyle(head.firstElementChild!).fill,
      marker: getComputedStyle(arrow).markerEnd.includes(`#${head.id}"`),
      fits: svg.getBoundingClientRect().width <= el.clientWidth && el.scrollWidth === el.clientWidth && el.clientWidth <= window.innerWidth,
      layout: [el, svg, document.querySelector(".left-panel")!, document.querySelector(".work-area")!].map(size),
      labels: [...svg.querySelectorAll("text")].map(t => {
        const { x, y, width, height } = t.getBBox();
        return [t.textContent, x, y, width, height];
      }),
    };
  });
}

test("technical diagrams keep their geometry and readable arrows when the lesson theme changes", async ({ page, request }) => {
  const errors: string[] = [];

  const signup = await request.post("/api/auth/signup", {
    data: { username: `diagram${Date.now()}`, password: "secret123" },
  });
  expect(signup.ok()).toBeTruthy();
  const { token } = await signup.json();
  await page.addInitScript((token: string) => {
    localStorage.setItem("labbox.token", token);
    localStorage.setItem("labbox.editor", JSON.stringify("classic"));
  }, token);

  try {
    await page.goto("/labs/python-basics");
    await expect(page.locator(".status-label")).toHaveText("Running", { timeout: 60_000 });
    await page.getByLabel("Chapter", { exact: true }).selectOption("06-lists");
    await page.getByRole("button", { name: /Step 6: Sorting, and a list with two names/ }).click();
    const figure = page.locator("figure.diagram");
    await expect(figure.getByRole("img")).toHaveAccessibleName(/same list/);
    await expect(figure.getByText("its own list")).toHaveCSS("font-family", /Inter/);
    await expect(figure.getByText("c = a.copy()", { exact: true })).toHaveCSS("font-family", /JetBrains Mono/);

    await expect(page.locator(".monaco-editor .view-lines")).toContainText("def remove_duplicates");
    page.on("pageerror", e => errors.push(e.message));
    page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });

    // Also exercise a phone viewport narrower than the saved desktop lesson panel.
    for (const width of [1500, 390]) {
      await page.setViewportSize({ width, height: 800 });
      const before = await appearance(figure);
      const root = page.locator("html");
      const nextTheme = await root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      await page.getByRole("button", { name: `Switch to ${nextTheme} theme` }).click();
      await expect(root).toHaveAttribute("data-theme", nextTheme);
      const after = await appearance(figure);
      for (const sample of [before, after]) {
        expect(sample.fits).toBe(true);
        expect(sample.marker).toBe(true);
        expect(sample.head).toBe(sample.line);
        expect(contrast(sample.text, sample.fill)).toBeGreaterThanOrEqual(4.5);
        expect(contrast(sample.caption, sample.frame)).toBeGreaterThanOrEqual(4.5);
        expect(contrast(sample.line, sample.frame)).toBeGreaterThanOrEqual(3);
      }
      expect(after.layout).toEqual(before.layout);
      expect(after.labels).toEqual(before.labels);
      expect(after.fill).not.toBe(before.fill);
      expect(after.line).not.toBe(before.line);
      expect(after.frame).not.toBe(before.frame);
    }
    expect(errors).toEqual([]);
  } finally {
    await request.post("/api/labs/python-basics/workspace/stop", { headers: { Authorization: `Bearer ${token}` } });
  }
});
