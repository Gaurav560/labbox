// Bundle Monaco locally instead of loading it from a CDN at runtime.
import { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";
import tsWorker from "monaco-editor/esm/vs/language/typescript/ts.worker?worker";

self.MonacoEnvironment = {
  getWorker(_workerId: string, label: string) {
    if (label === "json") return new jsonWorker();
    if (label === "typescript" || label === "javascript") return new tsWorker();
    return new editorWorker();
  },
};

loader.config({ monaco });

// Editor themes on the app's GitHub greys, so editor, panels and terminal read as one surface.
monaco.editor.defineTheme("labbox-dark", {
  base: "vs-dark",
  inherit: true,
  rules: [],
  colors: {
    "editor.background": "#111512",
    "editor.lineHighlightBackground": "#1a1f1b",
    "editorLineNumber.foreground": "#4b544e",
    "editorLineNumber.activeForeground": "#c9d1cb",
    "editorGutter.background": "#111512",
    "editor.selectionBackground": "#3a423c",
    "editorWidget.background": "#161a17",
    "editorWidget.border": "#2c322e",
    "editorSuggestWidget.background": "#161a17",
    "editorSuggestWidget.border": "#2c322e",
    "editorSuggestWidget.selectedBackground": "#252b27",
    "editorGhostText.foreground": "#7d877f",
  },
});
monaco.editor.defineTheme("labbox-light", {
  base: "vs",
  inherit: true,
  rules: [],
  colors: {
    "editor.background": "#ffffff",
    "editor.lineHighlightBackground": "#f6f8fa",
    "editorLineNumber.foreground": "#8c959f",
    "editorWidget.background": "#ffffff",
    "editorSuggestWidget.background": "#ffffff",
    "editorSuggestWidget.border": "#d1d9e0",
  },
});

export { monaco };

export const MODEL_PREFIX = "file:///workspace/";

export function modelUri(path: string): string {
  return MODEL_PREFIX + path;
}

const LANGUAGES: Record<string, string> = {
  py: "python",
  java: "java",
  js: "javascript",
  ts: "typescript",
  go: "go",
  sql: "sql",
  md: "markdown",
  sh: "shell",
  json: "json",
  yaml: "yaml",
  yml: "yaml",
};

export function languageFor(path: string): string {
  const ext = path.split(".").pop()?.toLowerCase() ?? "";
  return LANGUAGES[ext] ?? "plaintext";
}
