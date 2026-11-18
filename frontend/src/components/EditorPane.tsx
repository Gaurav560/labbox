import Editor, { type OnMount } from "@monaco-editor/react";
import { useRef } from "react";
import { languageFor, modelUri, monaco } from "../monaco";

export interface Tab {
  path: string;
  content: string; // what is in the editor
  saved: string; // what the server has
  status: "idle" | "saving" | "error";
}

interface Props {
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

export default function EditorPane({ tabs, activePath, onSelect, onClose, onChange, onSave }: Props) {
  const active = tabs.find((t) => t.path === activePath);
  // The editor command is registered once, so it reads the latest values through refs.
  const activeRef = useRef(activePath);
  activeRef.current = activePath;
  const saveRef = useRef(onSave);
  saveRef.current = onSave;

  const onMount: OnMount = (editor) => {
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
        <span className={`save-state ${active?.status === "error" ? "fail" : ""}`}>{saveLabel(active)}</span>
      </div>
      <div className="editor-body">
        {active ? (
          <Editor
            path={modelUri(active.path)}
            defaultValue={active.content}
            language={languageFor(active.path)}
            theme="vs-dark"
            onMount={onMount}
            onChange={(v) => onChange(active.path, v ?? "")}
            options={{ automaticLayout: true, fontSize: 14, minimap: { enabled: false }, scrollBeyondLastLine: false, tabSize: 4 }}
          />
        ) : (
          <div className="center-fill muted">Open a file from the tree</div>
        )}
      </div>
    </div>
  );
}
