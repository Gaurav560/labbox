// Hidden checks for javascript-inside-out. Prints one @@RESULT line per task; never prints the solution.
function report(task, passed, message, expected, actual) {
  const r = { task, passed, message };
  if (expected !== undefined) Object.assign(r, { expected: String(expected), actual: String(actual) });
  console.log("@@RESULT " + JSON.stringify(r));
}
const show = (v) => JSON.stringify(v) ?? String(v);

let bot;
try {
  bot = require("/check/workspace/bot.js");
} catch (e) {
  for (const t of ["parse_quantity", "same_items", "make_counter", "fetch_all"]) report(t, false, `bot.js could not be loaded: ${e.message}`);
  process.exit(0);
}

function cases(task, fn, list) {
  try {
    for (const [args, want] of list) {
      const got = bot[fn](...args);
      if (got !== want) return report(task, false, `${fn}(${args.map(show).join(", ")}) returned ${show(got)}`, show(want), show(got));
    }
    report(task, true, "ok");
  } catch (e) {
    report(task, false, `${fn} threw ${e.name}: ${e.message}`);
  }
}

cases("parse_quantity", "parseQuantity", [
  [["2"], 2], [[" 3 "], 3], [["20"], 20], [["two"], 0], [["2.5"], 0], [["0"], 0], [["21"], 0], [[""], 0], [["-1"], 0],
]);
cases("same_items", "sameItems", [
  [[["coffee", "bun"], ["coffee", "bun"]], true], [[["coffee"], ["bun"]], false], [[["coffee", "bun"], ["bun", "coffee"]], false],
  [[[], []], true], [[["coffee"], ["coffee", "coffee"]], false],
]);

try {
  const a = bot.makeTokenCounter("T");
  const b = bot.makeTokenCounter("Z");
  const got = [a(), a(), b(), a()];
  const want = ["T1", "T2", "Z1", "T3"];
  if (show(got) !== show(want)) report("make_counter", false, "Two counters must count on their own.", show(want), show(got));
  else report("make_counter", true, "ok");
} catch (e) {
  report("make_counter", false, `makeTokenCounter threw ${e.name}: ${e.message}`);
}

(async () => {
  try {
    let running = 0, most = 0;
    const fetchPrice = (item) => {
      running += 1;
      most = Math.max(most, running);
      return new Promise((ok) => setTimeout(() => { running -= 1; ok(item.length * 5); }, 150 - item.length * 10));
    };
    const started = Date.now();
    const got = await bot.fetchAllPrices(["coffee", "bun", "samosa", "poha"], fetchPrice);
    const want = [30, 15, 30, 20];
    if (show(got) !== show(want)) report("fetch_all", false, "The prices must come back in the order of items.", show(want), show(got));
    else if (most < 4) report("fetch_all", false, `The fetches ran one after another (${Date.now() - started} ms). Start them all at once.`, "4 at once", `${most} at once`);
    else report("fetch_all", true, "ok");
  } catch (e) {
    report("fetch_all", false, `fetchAllPrices failed: ${e.name}: ${e.message}`);
  }
})();
