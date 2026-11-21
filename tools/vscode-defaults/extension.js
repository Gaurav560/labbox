// LabBox: when the learner switches chapters or reaches a lesson step about a file, the lab page asks
// the backend, which writes /tmp/labbox-open.json in the machine ({path, line, end, at}). Open that
// file, scroll to the line, and select the lines the step talks about (line to end).
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
  const end = Math.max(line, (req.end || req.line || 1) - 1);
  const at = new vscode.Range(line, 0, line, 0);
  vscode.window
    .showTextDocument(vscode.Uri.file("/workspace/" + req.path), { preview: false, selection: at })
    .then((editor) => {
      // A step that names lines: select them whole, so the learner sees exactly what the lesson means.
      const last = Math.min(end, editor.document.lineCount - 1);
      if (req.end) editor.selection = new vscode.Selection(line, 0, last, editor.document.lineAt(last).text.length);
      editor.revealRange(new vscode.Range(line, 0, end, 0), vscode.TextEditorRevealType.AtTop);
    }, () => {});
}

exports.activate = (context) => {
  check(true);
  fs.watchFile(FILE, { interval: 400 }, () => check(false));
  context.subscriptions.push({ dispose: () => fs.unwatchFile(FILE) });
};
exports.deactivate = () => {};
