import Editor, { type OnMount } from "@monaco-editor/react";
import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { registerAiCompletion, setAiCompletion } from "../aiComplete";
import { registerCompletions } from "../completions";
import { usePersistentState } from "../persist";
import { languageFor, modelUri, monaco } from "../monaco";
import { useTheme } from "../theme";

export interface Tab {
  path: string;
  content: string; // what is in the editor
  saved: string; // what the server has
  status: "idle" | "saving" | "error";
}

interface Props {
  labId: string;
  tabs: Tab[];
  activePath: string | null;
  onSelect: (path: string) => void;
  onClose: (path: string) => void;
  onChange: (path: string, value: string) => void;
  onSave: (path: string) => void;
}

function saveLabel(tab: Tab | undefined): string {
  if (!tab) return "";
  if (tab.status === "saving") return "Saving...";
  if (tab.status === "error") return "Save failed";
  if (tab.content !== tab.saved) return "Unsaved";
  return "Saved ✓";
}

export default function EditorPane({ labId, tabs, activePath, onSelect, onClose, onChange, onSave }: Props) {
  const { theme } = useTheme();
  // AI completion: offered when the server has a code model; the learner can switch it off.
  const [aiAvailable, setAiAvailable] = useState(false);
  const [aiOn, setAiOn] = usePersistentState("aiCompletion", true);
  useEffect(() => {
    api.aiConfig().then((c) => setAiAvailable(c.completion)).catch(() => setAiAvailable(false));
  }, []);
  useEffect(() => setAiCompletion(labId, aiAvailable && aiOn), [labId, aiAvailable, aiOn]);
  const active = tabs.find((t) => t.path === activePath);
  // The editor command is registered once, so it reads the latest values through refs.
  const activeRef = useRef(activePath);
  activeRef.current = activePath;
  const saveRef = useRef(onSave);
  saveRef.current = onSave;

  const onMount: OnMount = (editor) => {
    registerCompletions();
    registerAiCompletion();
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      if (activeRef.current) saveRef.current(activeRef.current);
    });
  };

  return (
    <div className="editor-pane">
      <div className="tabs">
        {tabs.map((t) => (
          <div key={t.path} className={`tab ${t.path === activePath ? "active" : ""}`} onClick={() => onSelect(t.path)} title={t.path}>
            <span>{t.path.split("/").pop()}</span>
            {t.content !== t.saved && <span className="dirty-dot">●</span>}
            <button
              className="tab-close"
              aria-label={`Close ${t.path}`}
              onClick={(e) => {
                e.stopPropagation();
                onClose(t.path);
              }}
            >
              ×
            </button>
          </div>
        ))}
        <span className="spacer" />
        {active && <span className="editor-hint" title="Suggestions also pop up while you type">Ctrl+Space: suggestions</span>}
        {active && aiAvailable && (
          <button
            className={`ai-toggle ${aiOn ? "on" : ""}`}
            onClick={() => setAiOn((v) => !v)}
            aria-pressed={aiOn}
            title={aiOn ? "AI completion is on: grey suggestions appear as you pause, Tab accepts. Click to turn off." : "AI completion is off. Click to turn on."}
          >
            ✦ AI {aiOn ? "on" : "off"}
          </button>
        )}
        <span className={`save-state ${active?.status === "error" ? "fail" : ""}`}>{saveLabel(active)}</span>
      </div>
      <div className="editor-body">
        {active ? (
          <Editor
            path={modelUri(active.path)}
            defaultValue={active.content}
            language={languageFor(active.path)}
            theme={theme === "dark" ? "vs-dark" : "vs"}
            onMount={onMount}
            onChange={(v) => onChange(active.path, v ?? "")}
            options={{
              automaticLayout: true,
              fontFamily: '"JetBrains Mono", ui-monospace, monospace',
              fontSize: 14,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              tabSize: 4,
              // Completion: language keywords, built-ins and snippets (src/completions.ts), plus
              // names from every open file. Offline and instant; no AI.
              quickSuggestions: { other: true, comments: false, strings: false },
              wordBasedSuggestions: "allDocuments",
              snippetSuggestions: "inline",
              suggestOnTriggerCharacters: true,
              tabCompletion: "on",
              inlineSuggest: { enabled: true, mode: "subwordSmart" },
            }}
          />
        ) : (
          <div className="center-fill muted">Open a file from the tree</div>
        )}
      </div>
    </div>
  );
}
