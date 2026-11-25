// Before a browser-test run: note the highest account id, so the teardown removes only what this run made.
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export default function globalSetup() {
  const cli = fileURLToPath(new URL("../../scripts/labbox", import.meta.url));
  try {
    process.env.LABBOX_E2E_SINCE_ID = execFileSync(cli, ["test-accounts", "max-id"], { encoding: "utf8" }).trim();
  } catch (e) {
    console.warn("labbox test-accounts max-id failed; this run's lab machines will not be cleaned up:", e);
  }
}
