// After a browser-test run: remove the lab machines, networks and folders of the test accounts this run signed
// up (scripts/labbox test-accounts cleanup). LABBOX_E2E_KEEP=1 keeps them, to look into a failure. Then the site's
// lab limit goes back to what it was before the run (global-setup.ts switched it off).
import { execFileSync } from "node:child_process";
import { rmSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { LIMIT_FILE } from "./global-setup";

export default function globalTeardown() {
  const cli = fileURLToPath(new URL("../../scripts/labbox", import.meta.url));
  const limit = process.env.LABBOX_E2E_LAB_LIMIT;
  if (limit) {
    try {
      console.log(execFileSync(cli, ["lab-limit", limit], { encoding: "utf8" }).trim());
      rmSync(LIMIT_FILE, { force: true });
    } catch (e) {
      console.warn(`labbox lab-limit ${limit} failed; set it back by hand:`, e);
    }
  }
  const since = process.env.LABBOX_E2E_SINCE_ID;
  if (!since || process.env.LABBOX_E2E_KEEP === "1") return;
  try {
    console.log(execFileSync(cli, ["test-accounts", "cleanup", "--since-id", since], { encoding: "utf8" }).trim());
  } catch (e) {
    console.warn("labbox test-accounts cleanup failed:", e);
  }
}
