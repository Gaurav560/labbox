// After a browser-test run: remove the lab machines, networks and folders of the test accounts this run signed
// up (scripts/labbox test-accounts cleanup). LABBOX_E2E_KEEP=1 keeps them, to look into a failure.
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export default function globalTeardown() {
  const since = process.env.LABBOX_E2E_SINCE_ID;
  if (!since || process.env.LABBOX_E2E_KEEP === "1") return;
  const cli = fileURLToPath(new URL("../../scripts/labbox", import.meta.url));
  try {
    console.log(execFileSync(cli, ["test-accounts", "cleanup", "--since-id", since], { encoding: "utf8" }).trim());
  } catch (e) {
    console.warn("labbox test-accounts cleanup failed:", e);
  }
}
