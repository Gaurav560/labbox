// Hidden checks for JavaScript from zero. One @@RESULT line per task; never prints the solution.
// Each chapter loads only its own file, so a mistake in one chapter never breaks another chapter's
// check. LABBOX_CHAPTER (set by LabBox) limits the run to the chapter being checked.
const path = require("node:path");
const fs = require("node:fs");
const os = require("node:os");

const W = process.env.LABBOX_WORKSPACE || "/check/workspace";
const show = (v) => (v === undefined ? "undefined" : typeof v === "number" && Number.isNaN(v) ? "NaN" : JSON.stringify(v) ?? String(v));
const same = (a, b) => show(a) === show(b);

function report(task, passed, message, expected, actual) {
  const r = { task, passed, message };
  if (expected !== undefined) Object.assign(r, { expected: String(expected), actual: String(actual) });
  console.log("@@RESULT " + JSON.stringify(r));
}

// What each task teaches when it passes (Content standard: passes teach too).
const PASS = {
  greet: "Your first function: it takes a name and gives back new text. A template literal (`Hello, ${name}!`) built it.",
  total_minutes: "Arithmetic in a function: hours * 60 + minutes. JavaScript does * before +, just like school maths.",
  percent: "A guarded division: you checked for 0 first, then rounded to one decimal. That guard prevents a classic Infinity bug.",
  format_rupees: "toFixed(2) always shows two decimals, which is exactly what money needs.",
  grade: "Impossible values first, then the ranges from the top down: the first true condition wins.",
  leap_year: "Three rules in one line with && and ||, and the remainder operator % doing the dividing test.",
  sum_to: "A running total: start at 0 and add inside the loop. The same pattern adds up prices, marks and minutes.",
  count_vowels: "A loop over characters with a counter. Lower-casing first meant one check covered both cases.",
  count_words: "trim and split on runs of spaces: the empty-text case is the one most people miss, and you did not.",
  clean_name: "Split, change each piece, join: the three moves behind almost every text clean-up.",
  top_n: "You sorted a copy, so the caller's array is untouched. Changing data you were only lent is a common bug.",
  unique: "Each item once, in the order it first appeared: you kept the order a Set alone would also keep, by hand.",
  cart_total: "A loop over objects, reading each one's fields: the shape of almost every shopping cart and invoice.",
  with_discount: "You made a new object with { ...item } instead of changing the one you were given.",
  word_counts: "Counting with an object: (counts[key] ?? 0) + 1. The most used pattern in data work.",
  common_items: "A Set answers \"is it in there?\" instantly, and removed the duplicates for free.",
  passing: "filter with an arrow function: the whole loop in one readable line.",
  sort_by_length: "A compare function with a tie-break, on a copy: sort changes the array it is called on.",
  parse_age: "Clear errors for bad input: the right type of error, and a message that names the value.",
  safe_sum: "Robust: good values added, bad ones reported, nothing crashes.",
  bank_account: "The private #balance can only change through your two methods, so it can never go wrong.",
  total_area: "Different classes, one method name: totalArea never needs to know which shape it has.",
  fetch_all: "All the fetches ran at once and Promise.all kept the order: the core of fast JavaScript.",
  retry: "await inside try/catch in a loop: a pattern used for every flaky network call.",
  read_totals: "You read a real, messy file and skipped what you could not use, without crashing.",
  monthly_report: "A complete report from messy data, with the right line numbers. You have finished JavaScript from zero: well done.",
};
const pass = (task) => report(task, true, PASS[task] ?? "ok");
const fail = (task, msg, expected, actual) => report(task, false, "Not yet: " + msg, expected, actual);

function load(file) {
  const full = path.join(W, file);
  delete require.cache[require.resolve(full)];
  return require(full);
}

/** Calls fn(...args) for each case; returns true when every case matches, or reports the first miss. */
function cases(task, mod, fn, list, advice = () => "") {
  if (typeof mod[fn] !== "function") {
    fail(task, `${fn} is not exported. Keep it in module.exports at the bottom of the file.`);
    return false;
  }
  for (const [args, want] of list) {
    let got;
    try {
      got = mod[fn](...args.map((a) => structuredClone(a)));
    } catch (e) {
      fail(task, `${fn}(${args.map(show).join(", ")}) threw ${e.name}: ${e.message}`);
      return false;
    }
    if (!same(got, want)) {
      const tip = advice(args, got, want);
      fail(task, `${fn}(${args.map(show).join(", ")}) gave ${show(got)}, but it should be ${show(want)}.${tip ? " " + tip : ""}`, show(want), show(got));
      return false;
    }
  }
  return true;
}

const CHAPTERS = {
  "01-first-program": ["hello/hello.js", (m) => {
    if (cases("greet", m, "greet", [[["Asha"], "Hello, Asha!"], [["Kabir"], "Hello, Kabir!"]], (a, got) =>
      got === undefined ? "The function has no return: add return before the text." : "Mind the comma, the space and the !")) pass("greet");
    if (cases("total_minutes", m, "totalMinutes", [[[2, 15], 135], [[0, 45], 45], [[1, 0], 60]], (a, got) =>
      typeof got === "string" ? "That is text: + joined the values. Make sure both are numbers." : "")) pass("total_minutes");
  }],
  "02-values-and-types": ["types/numbers.js", (m) => {
    if (cases("percent", m, "percent", [[[45, 50], 90], [[1, 3], 33.3], [[2, 3], 66.7], [[7, 0], 0]], (a, got) =>
      a[1] === 0 ? "Check for a total of 0 before dividing." : "Round to one decimal: Math.round(x * 10) / 10.")) pass("percent");
    if (cases("format_rupees", m, "formatRupees", [[[1250], "₹12.50"], [[5], "₹0.05"], [[0], "₹0.00"], [[120000], "₹1200.00"]], () =>
      "Divide by 100 for rupees, then toFixed(2) for exactly two decimals.")) pass("format_rupees");
  }],
  "03-decisions": ["decisions/decisions.js", (m) => {
    if (cases("grade", m, "grade", [[[80], "A"], [[79], "B"], [[60], "B"], [[40], "C"], [[39], "F"], [[0], "F"], [[100], "A"], [[101], "Invalid"], [[-1], "Invalid"]], (a) =>
      a[0] > 100 || a[0] < 0 ? "Check for impossible marks first." : "Look at the boundary: 80, 60 and 40 themselves count (>=).")) pass("grade");
    if (cases("leap_year", m, "isLeapYear", [[[2024], true], [[2023], false], [[1900], false], [[2000], true], [[2100], false]], (a) =>
      a[0] % 100 === 0 ? "Years divisible by 100 are not leap years, unless divisible by 400." : "")) pass("leap_year");
  }],
  "04-loops": ["loops/loops.js", (m) => {
    if (cases("sum_to", m, "sumTo", [[[5], 15], [[1], 1], [[0], 0], [[100], 5050]], (a, got) =>
      got === 10 && a[0] === 5 ? "The loop stops one too early: let it run while i <= n." : "")) pass("sum_to");
    if (cases("count_vowels", m, "countVowels", [[["Hello World"], 3], [["AEIOU"], 5], [["rhythm"], 0], [[""], 0]], (a) =>
      a[0] === "AEIOU" ? "Capital vowels count too: lower-case the text first." : "")) pass("count_vowels");
  }],
  "05-strings": ["words/words.js", (m) => {
    if (cases("count_words", m, "countWords", [[["JavaScript is fun"], 3], [["  lots   of   spaces  "], 3], [[""], 0], [["   "], 0]], (a, got) =>
      a[0].trim() === "" ? "Empty text has no words: trim first, and check for nothing left." : "Split on runs of spaces: split(/\\s+/) after trim().")) pass("count_words");
    if (cases("clean_name", m, "cleanName", [[["  riya   SHARMA "], "Riya Sharma"], [["ARJUN"], "Arjun"], [["   "], ""]], () =>
      "Split into words, make the first letter upper case and the rest lower case, then join with one space.")) pass("clean_name");
  }],
  "06-arrays": ["arrays/arrays.js", (m) => {
    const nums = [72, 45, 90, 66];
    let ok = cases("top_n", m, "topN", [[[[72, 45, 90, 66], 2], [90, 72]], [[[5, 1], 5], [5, 1]], [[[3, 1, 2], 0], []], [[[10, 9, 100], 2], [100, 10]]], (a, got) =>
      "Biggest first needs a compare function, (a, b) => b - a: sort() on its own compares numbers as text, so 100 comes before 9.");
    if (ok) {
      m.topN(nums, 2);
      if (!same(nums, [72, 45, 90, 66])) { fail("top_n", `topN changed the array it was given: it is now ${show(nums)}. Sort a copy: [...numbers].`, show([72, 45, 90, 66]), show(nums)); ok = false; }
    }
    if (ok) pass("top_n");
    if (cases("unique", m, "unique", [[[["juice", "coffee", "juice", "milk"]], ["juice", "coffee", "milk"]], [[[3, 1, 3, 2, 1]], [3, 1, 2]], [[[]], []]])) pass("unique");
  }],
  "07-objects": ["objects/cart.js", (m) => {
    const cart = [{ name: "juice", price: 20, qty: 2 }, { name: "bun", price: 15, qty: 1 }];
    if (cases("cart_total", m, "cartTotal", [[[cart], 55], [[[]], 0], [[[{ name: "pen", price: 12.5, qty: 4 }]], 50]], (a, got) =>
      got === 35 ? "Multiply each price by its qty before adding." : "")) pass("cart_total");
    let ok = cases("with_discount", m, "withDiscount", [[[{ name: "juice", price: 20 }, 10], { name: "juice", price: 18 }], [[{ name: "bag", price: 999, stock: 3 }, 50], { name: "bag", price: 499.5, stock: 3 }]], (a, got) =>
      got && got.name === undefined ? "Keep every other field: start the new object with ...item." : "");
    if (ok) {
      const item = { name: "juice", price: 20 };
      m.withDiscount(item, 10);
      if (item.price !== 20) { fail("with_discount", "withDiscount changed the item it was given. Build a new object: { ...item, price: ... }.", "20", show(item.price)); ok = false; }
    }
    if (ok) pass("with_discount");
  }],
  "08-objects-and-sets": ["counting/counting.js", (m) => {
    if (cases("word_counts", m, "wordCounts", [[[["juice", "Coffee", "JUICE", "juice"]], { juice: 3, coffee: 1 }], [[[]], {}]], (a, got) =>
      got && got.JUICE ? "Lower-case each word before counting." : "")) pass("word_counts");
    if (cases("common_items", m, "commonItems", [[[["toast", "coffee", "milk"], ["milk", "toast", "juice"]], ["milk", "toast"]], [[["b", "a", "b"], ["b", "b", "a"]], ["a", "b"]], [[[], ["juice"]], []]], (a, got) =>
      Array.isArray(got) && new Set(got).size !== got.length ? "Each item once: a Set removes the repeats." : "Sort the result so the order is always the same.")) pass("common_items");
  }],
  "09-array-methods": ["arraymethods/marks.js", (m) => {
    if (cases("passing", m, "passing", [[[[72, 30, 90, 40, 39]], [72, 90, 40]], [[[]], []]], (a, got) =>
      Array.isArray(got) && !got.includes(40) ? "40 itself passes: use >= 40." : "")) pass("passing");
    const words = ["banana", "fig", "apple", "kiwi", "date"];
    let ok = cases("sort_by_length", m, "sortByLength", [[[words], ["fig", "date", "kiwi", "apple", "banana"]]], (a, got) =>
      same(got, ["fig", "kiwi", "date", "apple", "banana"]) ? "Ties need an order: when lengths are equal, compare the words (a.localeCompare(b))." : "");
    if (ok) {
      const w = [...words];
      m.sortByLength(w);
      if (!same(w, words)) { fail("sort_by_length", "sortByLength changed the array it was given. sort works in place, so sort a copy: [...words].", show(words), show(w)); ok = false; }
    }
    if (ok) pass("sort_by_length");
  }],
  "10-errors": ["errors/ages.js", (m) => {
    let ok = cases("parse_age", m, "parseAge", [[["17"], 17], [[" 42 "], 42], [["0"], 0], [["150"], 150]]);
    for (const [bad, kind] of ok ? [["abc", TypeError], ["12.5", TypeError], ["", TypeError], ["-1", TypeError], ["151", RangeError]] : []) {
      try {
        const got = m.parseAge(bad);
        fail("parse_age", `parseAge(${show(bad)}) returned ${show(got)}; it should throw a ${kind.name}.`); ok = false; break;
      } catch (e) {
        if (!(e instanceof kind)) { fail("parse_age", `parseAge(${show(bad)}) threw a ${e.name}; it should be a ${kind.name}.`, kind.name, e.name); ok = false; break; }
        if (!String(e.message).includes(bad.trim() || "\"\"") && bad !== "") { fail("parse_age", `The message for ${show(bad)} should name the value, so people know which one was wrong.`); ok = false; break; }
      }
    }
    if (ok) pass("parse_age");
    if (cases("safe_sum", m, "safeSum", [[[["10", "x", "2.5", ""]], { total: 12.5, bad: ["x", ""] }], [[["1", "2"]], { total: 3, bad: [] }], [[[]], { total: 0, bad: [] }]], (a, got) =>
      got && got.total === 12.5 && got.bad && got.bad.length === 1 ? "An empty string is not a number either, even though Number(\"\") gives 0." : "")) pass("safe_sum");
  }],
  "11-classes": ["classes/bank.js", (m) => {
    try {
      const a = new m.BankAccount("Riya");
      a.deposit(500);
      a.withdraw(200);
      if (a.balance !== 300) throw new Error(`after deposit(500) and withdraw(200) the balance is ${a.balance}, but it should be 300`);
      for (const [label, act] of [["deposit(0)", () => a.deposit(0)], ["deposit(-5)", () => a.deposit(-5)], ["withdraw(1000)", () => a.withdraw(1000)], ["withdraw(-1)", () => a.withdraw(-1)]]) {
        let threw = null;
        try { act(); } catch (e) { threw = e; }
        if (!(threw instanceof RangeError)) throw new Error(`${label} should throw a RangeError${threw ? `, not a ${threw.name}` : ""}`);
        if (a.balance !== 300) throw new Error(`${label} changed the balance to ${a.balance}; a refused amount must leave it at 300`);
      }
      pass("bank_account");
    } catch (e) {
      fail("bank_account", e.message + ".");
    }
    try {
      const c = new m.Circle(2);
      if (typeof c.area !== "function") throw new Error("Circle has no area() method yet");
      const got = m.totalArea([new m.Rect(3, 4), new m.Circle(1)]);
      if (got !== 15.14) throw new Error(`totalArea([Rect(3, 4), Circle(1)]) gave ${show(got)}, but it should be 15.14 (12 + 3.14...)`);
      if (m.totalArea([]) !== 0) throw new Error("totalArea([]) should be 0");
      pass("total_area");
    } catch (e) {
      fail("total_area", e.message + ".");
    }
  }],
  "12-async": ["async/prices.js", async (m) => {
    try {
      let running = 0, most = 0;
      const fetchPrice = (item) => {
        running++; most = Math.max(most, running);
        return new Promise((ok) => setTimeout(() => { running--; ok(item.length * 5); }, 150 - item.length * 10));
      };
      const started = Date.now();
      const got = await m.fetchAll(["coffee", "bun", "samosa", "poha"], fetchPrice);
      if (!same(got, [30, 15, 30, 20])) fail("fetch_all", "The prices must come back in the order of the items. Promise.all keeps that order for you.", show([30, 15, 30, 20]), show(got));
      else if (most < 4) fail("fetch_all", `The fetches ran one after another (${Date.now() - started} ms). Start them all, then await them together.`, "4 at once", `${most} at once`);
      else pass("fetch_all");
    } catch (e) {
      fail("fetch_all", `fetchAll threw ${e.name}: ${e.message}`);
    }
    try {
      let calls = 0;
      const flaky = async () => { calls++; if (calls < 3) throw new Error(`try ${calls} failed`); return "ok"; };
      const got = await m.retry(flaky, 5);
      if (got !== "ok" || calls !== 3) throw new Error(`retry(flaky, 5) gave ${show(got)} after ${calls} tries; it should give "ok" on the third try`);
      let tries = 0, err = null;
      try { await m.retry(async () => { tries++; throw new Error(`fail ${tries}`); }, 2); } catch (e) { err = e; }
      if (!err) throw new Error("when every try fails, retry should throw");
      if (tries !== 2) throw new Error(`retry(task, 2) tried ${tries} times; it should try exactly 2`);
      if (err.message !== "fail 2") throw new Error(`it threw "${err.message}"; throw the last error ("fail 2")`);
      pass("retry");
    } catch (e) {
      fail("retry", e.message + ".");
    }
  }],
  "13-capstone": ["capstone/report.js", (m) => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "lb-"));
    process.chdir(dir); // the files below are named as a learner would name them
    const csv = "march.csv";
    fs.writeFileSync(csv, "date,category,amount\n2026-03-02,food,120\n2026-03-02,travel,40.50\n\n2026-03-03,food,80\n2026-03-04,food,abc\n2026-03-04,travel,\n2026-03-05,,30\n");
    if (cases("read_totals", m, "readTotals", [[[csv], { food: 200, travel: 40.5 }]], (a, got) =>
      got && "" in got ? "A row with no category cannot be counted: skip it." : "Skip the header, blank lines and amounts that are not numbers.")) pass("read_totals");
    const five = "five.csv";
    fs.writeFileSync(five, "date,category,amount\n2026-03-02,food,120\n2026-03-03,,45\n2026-03-03,travel,abc\n2026-03-04,rent,18000\n");
    const blank = "blank.csv";
    fs.writeFileSync(blank, "date,category,amount\n\n2026-03-02,food,10\n2026-03-02,food,x\n");
    const empty = "empty.csv";
    fs.writeFileSync(empty, "date,category,amount\n");
    if (cases("monthly_report", m, "monthlyReport", [
      [[five], { total: 18120, count: 2, average: 9060, perCategory: { food: 120, rent: 18000 }, badLines: [3, 4] }],
      [[blank], { total: 10, count: 1, average: 10, perCategory: { food: 10 }, badLines: [4] }],
      [[empty], { total: 0, count: 0, average: 0, perCategory: {}, badLines: [] }],
    ], (a, got) => a[0] === blank && got && same(got.badLines, [3]) ? "Line numbers count the blank line too: use the line's place in the file (index + 1)." : a[0] === empty ? "No rows: the average is 0, not NaN." : "")) pass("monthly_report");
  }],
};

const TASKS = {
  "01-first-program": ["greet", "total_minutes"], "02-values-and-types": ["percent", "format_rupees"],
  "03-decisions": ["grade", "leap_year"], "04-loops": ["sum_to", "count_vowels"], "05-strings": ["count_words", "clean_name"],
  "06-arrays": ["top_n", "unique"], "07-objects": ["cart_total", "with_discount"], "08-objects-and-sets": ["word_counts", "common_items"],
  "09-array-methods": ["passing", "sort_by_length"], "10-errors": ["parse_age", "safe_sum"], "11-classes": ["bank_account", "total_area"],
  "12-async": ["fetch_all", "retry"], "13-capstone": ["read_totals", "monthly_report"],
};

(async () => {
  const only = process.env.LABBOX_CHAPTER;
  for (const [chapter, [file, run]] of Object.entries(CHAPTERS)) {
    if (only && only !== chapter) continue;
    let mod;
    try {
      mod = load(file);
    } catch (e) {
      const why = e.code === "MODULE_NOT_FOUND" ? `${file} is missing from your workspace.` : `${file} could not be loaded: ${e.name}: ${e.message.split("\n")[0]}. Run node ${file} in the terminal to see the line.`;
      for (const t of TASKS[chapter]) report(t, false, "Not yet: " + why);
      continue;
    }
    try {
      await run(mod);
    } catch (e) {
      for (const t of TASKS[chapter]) report(t, false, `Not yet: the check stopped with ${e.name}: ${e.message}`);
    }
  }
})();
