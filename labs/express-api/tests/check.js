// Hidden checks for express-api. Prints one @@RESULT line per task; never prints the solution.
const BASE = "http://127.0.0.1:3000";
const fs = require("node:fs");

function report(task, passed, message, expected, actual) {
  const r = { task, passed, message };
  if (expected !== undefined) Object.assign(r, { expected: String(expected), actual: String(actual) });
  console.log("@@RESULT " + JSON.stringify(r));
}

async function call(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    headers: body === undefined ? {} : { "content-type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  let json = null;
  try { json = await res.json(); } catch { /* not JSON */ }
  return { status: res.status, json };
}

async function waitForServer() {
  for (let i = 0; i < 50; i++) {
    try { await fetch(BASE + "/"); return true; } catch { await new Promise((r) => setTimeout(r, 100)); }
  }
  return false;
}

(async () => {
  if (!(await waitForServer())) {
    const log = fs.existsSync("/tmp/server.log") ? fs.readFileSync("/tmp/server.log", "utf8").slice(-800) : "";
    console.log("Server did not start:\n" + log);
    for (const t of ["get_order", "create_order"]) report(t, false, "server.js did not start. See Output.");
    return;
  }

  let getWorks = false;
  try {
    const one = await call("GET", "/orders/1");
    const missing = await call("GET", "/orders/999");
    if (one.status !== 200 || one.json?.area !== "Baner" || one.json?.id !== 1) {
      report("get_order", false, "GET /orders/1 should answer order 1 as JSON.", "200 with order 1", `${one.status} ${JSON.stringify(one.json)}`);
    } else if (missing.status !== 404 || typeof missing.json?.error !== "string") {
      report("get_order", false, "GET /orders/999 should answer 404 with an error message.", '404 {"error": ...}', `${missing.status} ${JSON.stringify(missing.json)}`);
    } else {
      getWorks = true;
      report("get_order", true, "ok");
    }
  } catch (e) {
    report("get_order", false, `Calling GET /orders failed: ${e.message}`);
  }

  try {
    const bad = [{}, { items: [], area: "Baner" }, { items: "thali", area: "Baner" }, { items: ["thali"] }, { items: [1], area: "Baner" }];
    for (const body of bad) {
      const r = await call("POST", "/orders", body);
      if (r.status !== 400) {
        report("create_order", false, `POST /orders with ${JSON.stringify(body)} should answer 400.`, "400", r.status);
        return;
      }
    }
    const made = await call("POST", "/orders", { items: ["poha", "chai"], area: "Kothrud" });
    if (made.status !== 201 || made.json?.status !== "preparing" || typeof made.json?.id !== "number") {
      report("create_order", false, "A valid order should answer 201 with the new order.", '201 {"id": ..., "status": "preparing"}', `${made.status} ${JSON.stringify(made.json)}`);
      return;
    }
    const back = getWorks ? await call("GET", `/orders/${made.json.id}`) : null;  // only once GET works
    if (back && (back.status !== 200 || back.json?.area !== "Kothrud")) {
      report("create_order", false, "The new order should be there afterwards with GET /orders/:id.", "200", back.status);
      return;
    }
    report("create_order", true, "ok");
  } catch (e) {
    report("create_order", false, `Calling POST /orders failed: ${e.message}`);
  }
})();
