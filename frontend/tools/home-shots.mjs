// Captures real lab screenshots for the home page's "Inside a lab" window.
// Needs the backend, Vite and Docker running. Logs in as a demo learner (never a real account).
//   node tools/home-shots.mjs <out-dir> [lab-id ...]
// Writes <out-dir>/<lab>-<chapter>.png and <out-dir>/shots.json (file, caption, alt).
// tools/home-shots.py then turns them into public/images/labs/*.webp and src/homeShots.json.
import { chromium } from "@playwright/test";
import { writeFileSync, existsSync, readFileSync } from "node:fs";

const BASE = "http://localhost:5173";
const USER = { username: "riya", password: "labbox-demo-1" };

// [lab, chapter, step, file to open, terminal command, wait ms (default 6000)]. Each lab is reset first; Redis chapter 10
// fills Redis on purpose (the OOM incident), so it comes last.
export const SHOTS = [
  ["redis-in-practice", "01-what-redis-is", 2, "README.md", "redis-cli PING && redis-cli SET greeting \"hello, Brew Point\" && redis-cli GET greeting"],
  ["redis-in-practice", "04-sets-and-sorted-sets", 4, "README.md", "redis-cli ZADD leaderboard 120 asha 95 kabir 140 riya && redis-cli ZREVRANGE leaderboard 0 2 WITHSCORES"],
  ["redis-in-practice", "06-caching-for-real", 2, "app.py", "redis-cli PING && redis-cli HSET customer:42 name Riya visits 7 && redis-cli HGETALL customer:42"],
  ["redis-in-practice", "08-distributed-locks", 5, "app.py", "redis-cli SET lock:slot:5 c1 NX PX 5000 && redis-cli PTTL lock:slot:5"],
  ["redis-in-practice", "09-streams", 2, "app.py", "redis-cli XADD payments:stream '*' order 42 amount 180 && redis-cli XLEN payments:stream"],
  ["redis-in-practice", "13-production-capstone", 5, "app.py", "redis-cli SLOWLOG GET 2"],
  ["redis-in-practice", "10-memory-and-eviction", 5, "README.md", "redis-cli INFO memory | grep -E \"used_memory_human|maxmemory_human|maxmemory_policy\""],
  ["rate-limiter", "01-shared-limit", 4, "app.py", "bash run.sh && for i in 1 2 3 4; do curl -s -H \"X-API-Key: test\" http://lb:8080/quote; echo; done"],
  ["rate-limiter", "02-global-limit", 2, "app.py", "for i in $(seq 30); do curl -s -o /dev/null -w \"%{http_code}\\n\" -H \"X-API-Key: blast\" http://lb:8080/quote; done | sort | uniq -c"],
  ["postgres-indexing-incident", "01-slow-checkout", 5, "checkout.sql", "psql -c \"EXPLAIN ANALYZE $(cat checkout.sql)\""],
  ["postgres-transactions-and-locks", "01-all-or-nothing", 4, "transfer.sql", "psql -c \"SELECT * FROM wallets ORDER BY customer_id\""],
  ["postgres-transactions-and-locks", "02-checkout-frozen", 2, "transfer.sql", "psql -c \"SELECT pid, state, wait_event_type, left(query, 40) AS query FROM pg_stat_activity WHERE datname IS NOT NULL\""],
  ["sql-from-zero", "01-select-and-where", 5, "q1.sql", "psql -c \"SELECT * FROM orders ORDER BY id LIMIT 6\""],
  ["sql-from-zero", "02-group-by", 2, "q3.sql", "psql -c \"SELECT status, COUNT(*) FROM orders GROUP BY status\""],
  ["linux-on-call", "01-reading-logs", 5, "count_5xx.sh", "head -6 access.log"],
  ["linux-on-call", "02-disk-and-permissions", 4, "fix_perms.sh", "du -sh server/var/log/app/* && ls -l server/config"],
  ["go-basics", "13-goroutines", 4, "concurrent/concurrent.go", "cat > /tmp/c.go <<'GO'\npackage main\nimport (\"fmt\"; \"sync\"; \"time\")\nfunc main() {\n\tstart := time.Now()\n\tvar wg sync.WaitGroup\n\tfor i := range 5 {\n\t\twg.Add(1)\n\t\tgo func() { defer wg.Done(); time.Sleep(200 * time.Millisecond); fmt.Println(\"worker\", i, \"done\") }()\n\t}\n\twg.Wait()\n\tfmt.Println(\"5 x 200ms together:\", time.Since(start).Round(time.Millisecond))\n}\nGO\ngo run /tmp/c.go", 12000],
  ["java-collections", "01-lists-and-maps", 4, "Payments.java", "javac *.java && java Payments"],
  ["javascript-inside-out", "02-closures-and-promises", 2, "bot.js", "node -e \"const s=Date.now(); const w=()=>new Promise(r=>setTimeout(r,300)); (async()=>{await w(); await w(); await w(); console.log(Date.now()-s,'ms')})()\""],
  ["python-collections", "01-lists-and-dicts", 5, "orders.py", "python3 orders.py"],
  ["git-without-fear", "02-undo-without-fear", 4, "README.md", "cd /workspace/kitchen && git log --oneline --graph --all | head -12"],
  ["spring-boot-first-api", "01-first-endpoints", 4, "MerchantController.java", "mvn -q package -DskipTests && java -jar target/merchant-api.jar", 45000],
  ["express-api", "01-orders-api", 4, "server.js", "node server.js > /tmp/server.log 2>&1 & sleep 3; cat /tmp/server.log; curl -s localhost:3000/; echo; curl -s -i localhost:3000/orders/1 | head -1", 9000],
  ["fastapi-first-api", "01-menu-api", 4, "main.py", "uvicorn main:app --host 0.0.0.0 --port 8000 --reload", 8000],
  ["java-basics", "01-methods", 4, "Greeter.java", "java -version 2>&1 | head -1 && ls -l && javac Greeter.java && echo '$ java Greeter' && java Greeter", 8000],
  ["python-basics", "02-numbers-and-text", 4, "numbers_text.py", "python3 -c \"print(0.1 + 0.2); print(round(0.1 + 0.2, 2)); print(7 / 2, 7 // 2, 7 % 2)\""],
];

const out = process.argv[2];
const only = new Set(process.argv.slice(3));
const manifestPath = `${out}/shots.json`;
const manifest = existsSync(manifestPath) ? JSON.parse(readFileSync(manifestPath, "utf8")) : {};

const browser = await chromium.launch({ channel: "chrome" });
let page = await browser.newPage({ viewport: { width: 1600, height: 960 }, deviceScaleFactor: 2 });
let res = await page.request.post(`${BASE}/api/auth/login`, { data: USER });
if (!res.ok()) res = await page.request.post(`${BASE}/api/auth/signup`, { data: USER });
const { token } = await res.json();
const auth = { headers: { Authorization: `Bearer ${token}` } };
await page.request.post(`${BASE}/api/onboarding`, { ...auth, data: { goal: "backend-job", answers: [1, 1, 0] } });

const labs = [...new Set(SHOTS.map((s) => s[0]))].filter((l) => !only.size || only.has(l));
for (const lab of labs) {
  // A fresh browser profile per lab: VS Code would otherwise reopen the last lab's tabs.
  await page.context().close();
  page = await (await browser.newContext({ viewport: { width: 1600, height: 960 }, deviceScaleFactor: 2 })).newPage();
  await page.goto(`${BASE}/`);
  await page.evaluate((t) => { localStorage.setItem("labbox.token", t); localStorage.setItem("labbox.focus", "false"); }, token);
  const info = await (await page.request.get(`${BASE}/api/labs/${lab}`, auth)).json();
  await page.request.post(`${BASE}/api/labs/${lab}/workspace/reset`, { ...auth, timeout: 180000 });
  await page.goto(`${BASE}/labs/${lab}`);
  for (const [, chapter, step, file, cmd, wait = 6000] of SHOTS.filter((s) => s[0] === lab)) {
    const name = `${lab}-${chapter}`;
    try {
      await page.locator("#chapter-select").selectOption(chapter);
      await page.getByRole("button", { name: new RegExp(`^Step ${step}:`) }).click({ timeout: 30000 });
      const frame = page.frameLocator("iframe.ide-frame");
      await frame.locator(".monaco-workbench").waitFor({ timeout: 120000 });
      await page.waitForTimeout(1500);
      await page.getByText("Setting up this chapter").waitFor({ state: "hidden", timeout: 180000 });
      // Open the file with Quick Open, so nested files work too.
      await frame.locator(".monaco-workbench").click({ position: { x: 600, y: 300 } });
      // Type into the Quick Open box itself (never into the editor: the chapter may have opened a file).
      await page.keyboard.press("Control+p");
      const quick = frame.locator(".quick-input-widget input");
      await quick.waitFor({ state: "visible", timeout: 10000 });
      await quick.fill(file);
      await page.waitForTimeout(800);
      await quick.press("Enter");
      await page.waitForTimeout(1500);
      await page.locator(".terminal-host").click();
      await page.keyboard.type(`clear; ${cmd}\n`, { delay: 4 });
      await page.waitForTimeout(wait);
      await page.mouse.move(5, 5);
      await page.screenshot({ path: `${out}/${name}.png` });
      const ch = (await page.locator("#chapter-select option:checked").textContent()).replace(" · ", ", ");
      manifest[name] = {
        file: `${name}.png`,
        caption: `labbox · ${info.title} · ${ch}`,
        alt: `A LabBox lab, ${info.title} (${ch}): the lesson, VS Code and a live terminal`,
      };
      writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
      console.log("ok", name);
    } catch (e) {
      console.log("FAILED", name, String(e).split("\n")[0]);
    }
  }
  await page.request.post(`${BASE}/api/labs/${lab}/workspace/stop`, auth);
}
await browser.close();
