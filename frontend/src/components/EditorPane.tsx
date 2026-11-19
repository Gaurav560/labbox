import Editor, { type OnMount } from "@monaco-editor/react";
import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { registerAiCompletion, setAiCompletion } from "../aiComplete";
import { registerCompletions } from "../completions";
import { usePersistentState } from "../persist";
import { languageFor, modelUri, monaco } from "../monaco";
import { useTheme } from "../theme";
import FileIcon, { languageName } from "./FileIcon";

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

  const [cursor, setCursor] = useState({ line: 1, col: 1, selected: 0 });

  const onMount: OnMount = (editor) => {
    registerCompletions();
    registerAiCompletion();
    editor.onDidChangeCursorSelection((e) => {
      const sel = e.selection;
      const selected = editor.getModel()?.getValueInRange(sel).length ?? 0;
      setCursor({ line: sel.positionLineNumber, col: sel.positionColumn, selected });
    });
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      if (activeRef.current) saveRef.current(activeRef.current);
    });
  };

  const language = active ? languageFor(active.path) : "plaintext";
  const crumbs = active ? ["workspace", ...active.path.split("/")] : [];

  return (
    <div className="editor-pane">
      <div className="tabs" role="tablist" aria-label="Open files">
        {tabs.map((t) => {
          const name = t.path.split("/").pop() ?? t.path;
          const dirty = t.content !== t.saved;
          return (
            <div key={t.path} role="tab" aria-selected={t.path === activePath} className={`tab ${t.path === activePath ? "active" : ""} ${dirty ? "dirty" : ""}`} onClick={() => onSelect(t.path)} title={t.path}>
              <FileIcon name={name} />
              <span className="tab-name">{name}</span>
              <button
                className="tab-close"
                aria-label={`Close ${t.path}`}
                onClick={(e) => {
                  e.stopPropagation();
                  onClose(t.path);
                }}
              >
                <span className="tab-dot" aria-hidden="true">●</span>
                <span className="tab-x" aria-hidden="true">×</span>
              </button>
            </div>
          );
        })}
      </div>
      {active && (
        <nav className="breadcrumbs" aria-label="Breadcrumbs">
          {crumbs.map((c, i) => (
            <span key={i} className="crumb">
              {i === crumbs.length - 1 && <FileIcon name={c} />}
              {c}
              {i < crumbs.length - 1 && <span className="crumb-sep">›</span>}
            </span>
          ))}
        </nav>
      )}
      <div className="editor-body">
        {active ? (
          <Editor
            path={modelUri(active.path)}
            defaultValue={active.content}
            language={language}
            theme={theme === "dark" ? "labbox-dark" : "labbox-light"}
            onMount={onMount}
            onChange={(v) => onChange(active.path, v ?? "")}
            options={{
              automaticLayout: true,
              fontFamily: '"JetBrains Mono", ui-monospace, monospace',
              fontSize: 15,
              lineHeight: 24,
              fontLigatures: true,
              padding: { top: 12, bottom: 12 },
              lineNumbersMinChars: 3,
              renderLineHighlight: "all",
              cursorBlinking: "smooth",
              cursorSmoothCaretAnimation: "on",
              smoothScrolling: true,
              mouseWheelZoom: true,
              bracketPairColorization: { enabled: true },
              guides: { bracketPairs: "active", indentation: true, highlightActiveIndentation: true },
              stickyScroll: { enabled: true },
              minimap: { enabled: true, renderCharacters: false, maxColumn: 80, showSlider: "mouseover", scale: 1 },
              scrollbar: { verticalScrollbarSize: 10, horizontalScrollbarSize: 10, useShadows: false },
              overviewRulerBorder: false,
              fixedOverflowWidgets: true,
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
          <div className="editor-empty">
            <div className="editor-empty-logo" aria-hidden="true">{"</>"}</div>
            <p>Open a file from the tree on the left.</p>
            <p className="muted small-text"><kbd>Ctrl</kbd> + <kbd>S</kbd> save · <kbd>Ctrl</kbd> + <kbd>Space</kbd> suggestions · <kbd>Tab</kbd> accepts an AI suggestion</p>
          </div>
        )}
      </div>
      {active && (
        <footer className="editor-status" aria-label="Editor status">
          <span className={`status-item ${active.status === "error" ? "fail" : ""}`}>{saveLabel(active)}</span>
          <span className="spacer" />
          <span className="status-item">Ln {cursor.line}, Col {cursor.col}{cursor.selected ? ` (${cursor.selected} selected)` : ""}</span>
          <span className="status-item">Spaces: 4</span>
          <span className="status-item">UTF-8</span>
          <span className="status-item">{languageName(language)}</span>
          <span className="status-item" title="Suggestions also pop up while you type">Ctrl+Space</span>
          {aiAvailable && (
            <button
              className={`status-item ai-toggle ${aiOn ? "on" : ""}`}
              onClick={() => setAiOn((v) => !v)}
              aria-pressed={aiOn}
              title={aiOn ? "AI completion is on: grey suggestions appear as you pause, Tab accepts. Click to turn off." : "AI completion is off. Click to turn on."}
            >
              ✦ AI {aiOn ? "on" : "off"}
            </button>
          )}
        </footer>
      )}
    </div>
  );
}
