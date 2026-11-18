import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api, ApiError, type CheckResponse, type FileNode, type LabDetail } from "../api";
import { useAuth } from "../auth";
import ChapterPanel from "../components/ChapterPanel";
import CheckResults from "../components/CheckResults";
import EditorPane, { type Tab } from "../components/EditorPane";
import FileTree from "../components/FileTree";
import Splitter from "../components/Splitter";
import StatusBar, { type UiStatus } from "../components/StatusBar";
import TaskList from "../components/TaskList";
import TerminalPane from "../components/TerminalPane";
import { useToast } from "../components/Toasts";
import { MODEL_PREFIX, monaco } from "../monaco";

const AUTOSAVE_MS = 800;
const TREE_POLL_MS = 5000;
const STATUS_POLL_MS = 10000;

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));
const errMsg = (e: unknown) => (e instanceof Error ? e.message : String(e));

export default function LabPage() {
  const { labId = "" } = useParams();
  const { user } = useAuth();
  const toast = useToast();

  const [lab, setLab] = useState<LabDetail | null>(null);
  const [chapterId, setChapterId] = useState("");
  const [markdown, setMarkdown] = useState<string | null>(null);
  const [status, setStatus] = useState<UiStatus>("starting");
  const [tree, setTree] = useState<FileNode[]>([]);
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [activePath, setActivePath] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);
  const [result, setResult] = useState<CheckResponse | null>(null);
  const [terminalKey, setTerminalKey] = useState(0);

  // Panel sizes in px.
  const [leftW, setLeftW] = useState(340);
  const [treeW, setTreeW] = useState(200);
  const [termH, setTermH] = useState(260);

  // Latest tabs for timers and save chains, which outlive a render.
  const tabsRef = useRef<Tab[]>([]);
  tabsRef.current = tabs;
  const timers = useRef<Map<string, number>>(new Map());
  const saveChains = useRef<Map<string, Promise<void>>>(new Map());

  // ---------- loading ----------

  const loadLab = useCallback(async () => {
    const detail = await api.lab(labId);
    setLab(detail);
    return detail;
  }, [labId]);

  const refreshTree = useCallback(async () => {
    try {
      setTree(await api.tree(labId));
    } catch (e) {
      toast(`Could not load files: ${errMsg(e)}`);
    }
  }, [labId, toast]);

  const startMachine = useCallback(async () => {
    setStatus("starting");
    try {
      await api.startWorkspace(labId);
      setStatus("running");
      setTerminalKey((k) => k + 1);
    } catch (e) {
      setStatus("error");
      toast(`Could not start your machine: ${errMsg(e)}`);
    }
  }, [labId, toast]);

  useEffect(() => {
    loadLab()
      .then((d) => {
        const firstOpen = d.chapters.find((c) => c.tasks.some((t) => !t.passed)) ?? d.chapters[0];
        setChapterId(firstOpen.id);
      })
      .catch((e) => toast(errMsg(e)));
    startMachine().then(refreshTree);
  }, [loadLab, startMachine, refreshTree, toast]);

  useEffect(() => {
    if (!chapterId) return;
    setMarkdown(null);
    setResult(null);
    api.chapter(labId, chapterId).then((c) => setMarkdown(c.markdown)).catch((e) => toast(errMsg(e)));
  }, [labId, chapterId, toast]);

  // Files created in the terminal show up after a poll.
  useEffect(() => {
    const id = window.setInterval(() => document.visibilityState === "visible" && refreshTree(), TREE_POLL_MS);
    return () => window.clearInterval(id);
  }, [refreshTree]);

  // Notice when the idle reaper (or anything else) stopped the machine.
  useEffect(() => {
    const id = window.setInterval(async () => {
      if (document.visibilityState !== "visible") return;
      try {
        const s = await api.workspaceStatus(labId);
        setStatus((cur) => (cur === "running" && s.status !== "running" ? "stopped" : cur));
      } catch {
        /* toast-worthy errors surface elsewhere */
      }
    }, STATUS_POLL_MS);
    return () => window.clearInterval(id);
  }, [labId]);

  // Free Monaco models of closed tabs so reopening a file shows fresh content.
  useEffect(() => {
    const open = new Set(tabs.map((t) => t.path));
    for (const m of monaco.editor.getModels()) {
      const uri = m.uri.toString(true);
      if (uri.startsWith(MODEL_PREFIX) && !open.has(uri.slice(MODEL_PREFIX.length))) m.dispose();
    }
  }, [tabs]);

  // ---------- tabs and saving ----------

  const patchTab = (path: string, patch: (t: Tab) => Partial<Tab>) =>
    setTabs((ts) => ts.map((t) => (t.path === path ? { ...t, ...patch(t) } : t)));

  // Saves for one path run one after another so an older write never lands last.
  const save = useCallback(
    (path: string): Promise<void> => {
      const timer = timers.current.get(path);
      if (timer) window.clearTimeout(timer);
      timers.current.delete(path);
      const run = async () => {
        const tab = tabsRef.current.find((t) => t.path === path);
        if (!tab || tab.content === tab.saved) return;
        const content = tab.content;
        patchTab(path, () => ({ status: "saving" }));
        try {
          await api.writeFile(labId, path, content);
          patchTab(path, () => ({ saved: content, status: "idle" }));
          tabsRef.current = tabsRef.current.map((t) => (t.path === path ? { ...t, saved: content } : t));
        } catch (e) {
          patchTab(path, () => ({ status: "error" }));
          toast(`Could not save ${path}: ${errMsg(e)}`);
        }
      };
      const chain = (saveChains.current.get(path) ?? Promise.resolve()).then(run);
      saveChains.current.set(path, chain);
      return chain;
    },
    [labId, toast],
  );

  const saveAll = useCallback(() => Promise.all(tabsRef.current.map((t) => save(t.path))), [save]);

  function onChange(path: string, value: string) {
    tabsRef.current = tabsRef.current.map((t) => (t.path === path ? { ...t, content: value } : t));
    patchTab(path, () => ({ content: value }));
    const old = timers.current.get(path);
    if (old) window.clearTimeout(old);
    timers.current.set(path, window.setTimeout(() => save(path), AUTOSAVE_MS));
  }

  async function openFile(path: string) {
    if (tabsRef.current.some((t) => t.path === path)) {
      setActivePath(path);
      return;
    }
    try {
      const { content } = await api.readFile(labId, path);
      setTabs((ts) => (ts.some((t) => t.path === path) ? ts : [...ts, { path, content, saved: content, status: "idle" }]));
      setActivePath(path);
    } catch (e) {
      toast(errMsg(e));
    }
  }

  async function closeTab(path: string) {
    await save(path);
    const ts = tabsRef.current;
    const i = ts.findIndex((t) => t.path === path);
    const next = ts.filter((t) => t.path !== path);
    tabsRef.current = next;
    setTabs(next);
    setActivePath((a) => (a === path ? next[Math.min(i, next.length - 1)]?.path ?? null : a));
  }

  function dropTabs(match: (path: string) => boolean) {
    for (const t of tabsRef.current) {
      if (!match(t.path)) continue;
      const timer = timers.current.get(t.path);
      if (timer) window.clearTimeout(timer);
      timers.current.delete(t.path);
    }
    const next = tabsRef.current.filter((t) => !match(t.path));
    tabsRef.current = next;
    setTabs(next);
    setActivePath((a) => (a && match(a) ? next[0]?.path ?? null : a));
  }

  // Ctrl+S / Cmd+S anywhere on the page saves everything (inside Monaco it saves the active tab).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        saveAll();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [saveAll]);

  // Save pending edits when the user leaves the page.
  useEffect(() => () => void saveAll(), [saveAll]);

  // ---------- file tree actions ----------

  async function newEntry(dir: string, type: "file" | "dir") {
    const name = window.prompt(`New ${type === "dir" ? "folder" : "file"} name${dir ? ` in ${dir}/` : ""}:`);
    if (!name?.trim()) return;
    const path = dir ? `${dir}/${name.trim()}` : name.trim();
    try {
      await api.newEntry(labId, path, type);
      await refreshTree();
      if (type === "file") openFile(path);
    } catch (e) {
      toast(errMsg(e));
    }
  }

  async function renameEntry(path: string) {
    const to = window.prompt("Rename to (path inside the workspace):", path);
    if (!to?.trim() || to.trim() === path) return;
    await save(path);
    try {
      await api.rename(labId, path, to.trim());
      dropTabs((p) => p === path || p.startsWith(path + "/"));
      await refreshTree();
    } catch (e) {
      toast(errMsg(e));
    }
  }

  async function deleteEntry(path: string, type: "file" | "dir") {
    if (!window.confirm(`Delete ${type === "dir" ? "folder" : "file"} ${path}?${type === "dir" ? " Everything inside it is deleted too." : ""}`)) return;
    try {
      dropTabs((p) => p === path || p.startsWith(path + "/"));
      await api.deleteEntry(labId, path);
      await refreshTree();
    } catch (e) {
      toast(errMsg(e));
    }
  }

  // ---------- machine actions ----------

  async function stopMachine() {
    try {
      await saveAll();
      await api.stopWorkspace(labId);
      setStatus("stopped");
    } catch (e) {
      toast(errMsg(e));
    }
  }

  async function resetLab() {
    if (!window.confirm("Reset this lab? This deletes your files for this lab and restores the starter files.")) return;
    dropTabs(() => true);
    setStatus("starting");
    try {
      await api.resetWorkspace(labId);
      setStatus("running");
      setTerminalKey((k) => k + 1);
      setResult(null);
      await refreshTree();
      toast("Lab reset to the starter files", "info");
    } catch (e) {
      setStatus("error");
      toast(errMsg(e));
    }
  }

  async function runCheck() {
    setChecking(true);
    try {
      await saveAll();
      setResult(await api.check(labId, chapterId));
      await loadLab();
    } catch (e) {
      toast(e instanceof ApiError && e.status === 429 ? "A check is already running" : `Check failed: ${errMsg(e)}`);
    } finally {
      setChecking(false);
    }
  }

  // ---------- render ----------

  const chapter = lab?.chapters.find((c) => c.id === chapterId);

  if (status === "starting" && tabs.length === 0 && tree.length === 0) {
    return (
      <div className="center-screen">
        <span className="spinner" /> Starting your machine...
      </div>
    );
  }

  return (
    <div className="lab-page">
      <StatusBar
        title={lab?.title ?? labId}
        chapters={lab?.chapters ?? []}
        chapterId={chapterId}
        onChapter={setChapterId}
        status={status}
        username={user?.username ?? ""}
        onStart={startMachine}
        onStop={stopMachine}
        onReset={resetLab}
      />
      <div className="lab-body">
        <aside className="left-panel" style={{ width: leftW }}>
          <ChapterPanel markdown={markdown} />
          <div className="left-footer">
            {chapter && <TaskList tasks={chapter.tasks} />}
            <button className="btn btn-primary btn-check" onClick={runCheck} disabled={checking || !chapterId}>
              {checking ? <><span className="spinner" /> Checking...</> : "Check"}
            </button>
          </div>
        </aside>
        <Splitter direction="vertical" onDrag={(d) => setLeftW((w) => clamp(w + d, 220, 800))} />
        <section className="work-area">
          <div className="files-and-editor">
            <div style={{ width: treeW }} className="tree-wrap">
              <FileTree
                tree={tree}
                activePath={activePath}
                onOpen={openFile}
                onNew={newEntry}
                onRename={renameEntry}
                onDelete={deleteEntry}
                onRefresh={refreshTree}
              />
            </div>
            <Splitter direction="vertical" onDrag={(d) => setTreeW((w) => clamp(w + d, 120, 500))} />
            <EditorPane tabs={tabs} activePath={activePath} onSelect={setActivePath} onClose={closeTab} onChange={onChange} onSave={save} />
          </div>
          <Splitter direction="horizontal" onDrag={(d) => setTermH((h) => clamp(h - d, 80, 800))} />
          <div style={{ height: termH }} className="terminal-wrap">
            <TerminalPane
              labId={labId}
              enabled={status === "running"}
              connectKey={terminalKey}
              onConnected={() => setStatus("running")}
            />
          </div>
        </section>
      </div>
      <CheckResults result={result} running={checking} />
    </div>
  );
}
