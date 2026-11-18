import { useState, type MouseEvent } from "react";
import type { FileNode } from "../api";

interface Props {
  tree: FileNode[];
  activePath: string | null;
  onOpen: (path: string) => void;
  onNew: (parentDir: string, type: "file" | "dir") => void;
  onRename: (path: string) => void;
  onDelete: (path: string, type: "file" | "dir") => void;
  onRefresh: () => void;
}

function parentOf(path: string): string {
  const i = path.lastIndexOf("/");
  return i < 0 ? "" : path.slice(0, i);
}

export default function FileTree(p: Props) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [selectedDir, setSelectedDir] = useState("");

  function toggle(path: string) {
    setSelectedDir(path);
    setExpanded((s) => {
      const n = new Set(s);
      if (n.has(path)) n.delete(path);
      else n.add(path);
      return n;
    });
  }

  function stop(e: MouseEvent, fn: () => void) {
    e.stopPropagation();
    fn();
  }

  function render(nodes: FileNode[], depth: number) {
    return nodes.map((n) => {
      const isDir = n.type === "dir";
      const open = expanded.has(n.path);
      return (
        <div key={n.path}>
          <div
            className={`tree-row ${p.activePath === n.path ? "active" : ""} ${isDir && selectedDir === n.path ? "selected" : ""}`}
            style={{ paddingLeft: 8 + depth * 14 }}
            onClick={() => (isDir ? toggle(n.path) : (setSelectedDir(parentOf(n.path)), p.onOpen(n.path)))}
            title={n.path}
          >
            <span className="tree-icon">{isDir ? (open ? "▾" : "▸") : "·"}</span>
            <span className="tree-name">{n.name}</span>
            <span className="tree-actions">
              <button title="Rename" onClick={(e) => stop(e, () => p.onRename(n.path))}>✎</button>
              <button title="Delete" onClick={(e) => stop(e, () => p.onDelete(n.path, n.type))}>🗑</button>
            </span>
          </div>
          {isDir && open && n.children && render(n.children, depth + 1)}
        </div>
      );
    });
  }

  return (
    <div className="file-tree">
      <div className="pane-header">
        <span onClick={() => setSelectedDir("")} className="clickable" title="Select workspace root">Files</span>
        <span className="spacer" />
        <button className="icon-btn" title="New file" onClick={() => p.onNew(selectedDir, "file")}>+📄</button>
        <button className="icon-btn" title="New folder" onClick={() => p.onNew(selectedDir, "dir")}>+📁</button>
        <button className="icon-btn" title="Refresh" onClick={p.onRefresh}>⟳</button>
      </div>
      <div className="tree-body">
        {p.tree.length === 0 ? <div className="muted small pad">No files yet</div> : render(p.tree, 0)}
      </div>
    </div>
  );
}
