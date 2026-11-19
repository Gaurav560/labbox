// LabBox: when the learner switches chapters, the lab page asks the backend, which writes
// /tmp/labbox-open.json in the machine ({path, line, at}). Open that file at that line.
const fs = require("fs");
const vscode = require("vscode");

const FILE = "/tmp/labbox-open.json";
let last = 0;

function check(startup) {
  let req;
  try {
    req = JSON.parse(fs.readFileSync(FILE, "utf8"));
  } catch {
    return;
  }
  if (!req || typeof req.path !== "string" || !(req.at > last)) return;
  last = req.at;
  if (startup && Date.now() / 1000 - req.at > 120) return; // an old request from an earlier visit
  const line = Math.max(0, (req.line || 1) - 1);
  const at = new vscode.Range(line, 0, line, 0);
  vscode.window
    .showTextDocument(vscode.Uri.file("/workspace/" + req.path), { preview: false, selection: at })
    .then((editor) => editor.revealRange(at, vscode.TextEditorRevealType.AtTop), () => {});
}

exports.activate = (context) => {
  check(true);
  fs.watchFile(FILE, { interval: 400 }, () => check(false));
  context.subscriptions.push({ dispose: () => fs.unwatchFile(FILE) });
};
exports.deactivate = () => {};
