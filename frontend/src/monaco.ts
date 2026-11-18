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
