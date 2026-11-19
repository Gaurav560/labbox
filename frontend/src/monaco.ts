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

// Editor themes: GitHub's code colours on the app's greys, so editor, panels and terminal read as
// one surface. Bracket pairs get VS Code's gold, purple and blue.
const DARK_RULES = [
  { token: "comment", foreground: "8b949e", fontStyle: "italic" },
  { token: "keyword", foreground: "ff7b72" },
  { token: "keyword.flow", foreground: "ff7b72" },
  { token: "string", foreground: "a5d6ff" },
  { token: "string.escape", foreground: "79c0ff" },
  { token: "number", foreground: "79c0ff" },
  { token: "constant", foreground: "79c0ff" },
  { token: "regexp", foreground: "7ee787" },
  { token: "type", foreground: "ffa657" },
  { token: "type.identifier", foreground: "ffa657" },
  { token: "predefined", foreground: "d2a8ff" },
  { token: "annotation", foreground: "d2a8ff" },
  { token: "decorator", foreground: "d2a8ff" },
  { token: "tag", foreground: "7ee787" },
  { token: "attribute.name", foreground: "79c0ff" },
  { token: "attribute.value", foreground: "a5d6ff" },
  { token: "variable", foreground: "ffa657" },
  { token: "variable.predefined", foreground: "79c0ff" },
  { token: "identifier", foreground: "e6edf3" },
  { token: "delimiter", foreground: "c9d1d9" },
  { token: "operator", foreground: "ff7b72" },
  { token: "keyword.md", foreground: "79c0ff", fontStyle: "bold" },
  { token: "strong", fontStyle: "bold" },
  { token: "emphasis", fontStyle: "italic" },
];
const LIGHT_RULES = [
  { token: "comment", foreground: "6e7781", fontStyle: "italic" },
  { token: "keyword", foreground: "cf222e" },
  { token: "string", foreground: "0a3069" },
  { token: "number", foreground: "0550ae" },
  { token: "constant", foreground: "0550ae" },
  { token: "type", foreground: "953800" },
  { token: "type.identifier", foreground: "953800" },
  { token: "predefined", foreground: "8250df" },
  { token: "annotation", foreground: "8250df" },
  { token: "decorator", foreground: "8250df" },
  { token: "tag", foreground: "116329" },
  { token: "attribute.name", foreground: "0550ae" },
  { token: "variable", foreground: "953800" },
  { token: "identifier", foreground: "1f2328" },
  { token: "operator", foreground: "cf222e" },
];

monaco.editor.defineTheme("labbox-dark", {
  base: "vs-dark",
  inherit: true,
  rules: DARK_RULES,
  colors: {
    "editor.background": "#111512",
    "editor.foreground": "#e6edf3",
    "editor.lineHighlightBackground": "#181d19",
    "editor.lineHighlightBorder": "#00000000",
    "editorLineNumber.foreground": "#4b544e",
    "editorLineNumber.activeForeground": "#e6edf3",
    "editorGutter.background": "#111512",
    "editorCursor.foreground": "#e6edf3",
    "editor.selectionBackground": "#264f78",
    "editor.inactiveSelectionBackground": "#264f7855",
    "editor.wordHighlightBackground": "#ffffff14",
    "editorIndentGuide.background1": "#252b27",
    "editorIndentGuide.activeBackground1": "#4b544e",
    "editorBracketHighlight.foreground1": "#ffd700",
    "editorBracketHighlight.foreground2": "#da70d6",
    "editorBracketHighlight.foreground3": "#179fff",
    "editorBracketMatch.background": "#3fb95026",
    "editorBracketMatch.border": "#3fb95066",
    "editorWidget.background": "#161a17",
    "editorWidget.border": "#2c322e",
    "editorSuggestWidget.background": "#161a17",
    "editorSuggestWidget.border": "#2c322e",
    "editorSuggestWidget.selectedBackground": "#1f3a5f",
    "editorSuggestWidget.highlightForeground": "#58a6ff",
    "editorGhostText.foreground": "#7d877f",
    "editorStickyScroll.background": "#141815",
    "editorStickyScrollHover.background": "#1a1f1b",
    "minimap.background": "#111512",
    "scrollbarSlider.background": "#ffffff14",
    "scrollbarSlider.hoverBackground": "#ffffff24",
  },
});
monaco.editor.defineTheme("labbox-light", {
  base: "vs",
  inherit: true,
  rules: LIGHT_RULES,
  colors: {
    "editor.background": "#ffffff",
    "editor.foreground": "#1f2328",
    "editor.lineHighlightBackground": "#f6f8fa",
    "editorLineNumber.foreground": "#8c959f",
    "editorLineNumber.activeForeground": "#1f2328",
    "editorBracketHighlight.foreground1": "#b08800",
    "editorBracketHighlight.foreground2": "#8250df",
    "editorBracketHighlight.foreground3": "#0969da",
    "editorWidget.background": "#ffffff",
    "editorSuggestWidget.background": "#ffffff",
    "editorSuggestWidget.border": "#d1d9e0",
    "editorStickyScroll.background": "#f6f8fa",
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
