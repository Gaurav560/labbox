// Before a browser-test run: note the highest account id, so the teardown removes only what this run made.
// Every test signs up a fresh account, so the run switches the site's lab limit off (owner, 26 November: at most a
// few labs at a time) and the teardown puts the owner's setting back. The saved value also goes to a file, so a
// run that was stopped before its teardown still gives the setting back at the start of the next run.
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

export const LIMIT_FILE = join(tmpdir(), "labbox-e2e-lab-limit");

export default function globalSetup() {
  const cli = fileURLToPath(new URL("../../scripts/labbox", import.meta.url));
  try {
    process.env.LABBOX_E2E_SINCE_ID = execFileSync(cli, ["test-accounts", "max-id"], { encoding: "utf8" }).trim();
  } catch (e) {
    console.warn("labbox test-accounts max-id failed; this run's lab machines will not be cleaned up:", e);
  }
  try {
    // A file left by a stopped run holds the owner's setting; otherwise read it now.
    const saved = existsSync(LIMIT_FILE)
      ? readFileSync(LIMIT_FILE, "utf8").trim()
      : execFileSync(cli, ["lab-limit", "--plain"], { encoding: "utf8" }).trim();
    writeFileSync(LIMIT_FILE, saved);
    process.env.LABBOX_E2E_LAB_LIMIT = saved;
    if (saved !== "off") execFileSync(cli, ["lab-limit", "off"], { encoding: "utf8" });
  } catch (e) {
    console.warn("labbox lab-limit failed; tests may find their labs locked:", e);
  }
}
