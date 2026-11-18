// Hidden checks. Prints one @@RESULT line per task; never prints the solution.
function report(task, passed, message, expected, actual) {
  const r = { task, passed, message };
  if (expected !== undefined) Object.assign(r, { expected: String(expected), actual: String(actual) });
  console.log("@@RESULT " + JSON.stringify(r));
}

let mod;
try {
  mod = require("/check/workspace/solution.js");
} catch (e) {
  report("double", false, `solution.js could not be loaded: ${e.message}`);
  process.exit(0);
}

try {
  for (const [n, want] of [[21, 42], [0, 0], [-3, -6]]) {
    const got = mod.double(n);
    if (got !== want) {
      report("double", false, `double(${n}) returned ${JSON.stringify(got)}`, want, JSON.stringify(got));
      process.exit(0);
    }
  }
  report("double", true, "ok");
} catch (e) {
  report("double", false, `double threw ${e.name}: ${e.message}`);
}
