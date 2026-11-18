import confetti from "canvas-confetti";
import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api, ApiError, type CheckResponse, type FileNode, type LabDetail, type Step } from "../api";
import { useAuth } from "../auth";
import ChapterPanel from "../components/ChapterPanel";
import CheckDrawer from "../components/CheckDrawer";
import EditorPane, { type Tab } from "../components/EditorPane";
import FileTree from "../components/FileTree";
import Splitter from "../components/Splitter";
import StatusBar, { type UiStatus } from "../components/StatusBar";
import TaskList from "../components/TaskList";
import TerminalPane, { type TerminalHandle } from "../components/TerminalPane";
import { useToast } from "../components/Toasts";
import LessonPanel from "../lesson/LessonPanel";
import StepCard, { type PredictState } from "../lesson/StepCard";
import { MODEL_PREFIX, monaco } from "../monaco";
import { usePersistentState } from "../persist";

const AUTOSAVE_MS = 800;
const TREE_POLL_MS = 5000;
const STATUS_POLL_MS = 10000;
const STEP_SAVE_MS = 400;
const NO_PREDICT: PredictState = { wrong: [], solved: false };

const isTyping = (t: EventTarget | null) =>
  t instanceof HTMLElement && (t.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName));

function celebrate() {
  // Small and once; canvas-confetti skips it entirely for prefers-reduced-motion.
  confetti({ particleCount: 90, spread: 70, origin: { x: 0.2, y: 0.7 }, disableForReducedMotion: true });
}

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));
const errMsg = (e: unknown) => (e instanceof Error ? e.message : String(e));

export default function LabPage() {
  const { labId = "" } = useParams();
  const { user } = useAuth();
  const toast = useToast();

  const [lab, setLab] = useState<LabDetail | null>(null);
  const [chapterId, setChapterId] = useState("");
  const [markdown, setMarkdown] = useState<string | null>(null);
  const [steps, setSteps] = useState<Step[] | null>(null);
  const [step, setStep] = useState(0);
  const [visited, setVisited] = useState(0);
  const [hints, setHints] = useState<Record<string, string[]>>({});
  const [hintBusy, setHintBusy] = useState(false);
  const [predicts, setPredicts] = useState<Record<number, PredictState>>({});
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [bottomTab, setBottomTab] = useState<"terminal" | "output">("terminal");
  const [status, setStatus] = useState<UiStatus>("starting");
  const [tree, setTree] = useState<FileNode[]>([]);
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [activePath, setActivePath] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);
  const [result, setResult] = useState<CheckResponse | null>(null);
  const [terminalKey, setTerminalKey] = useState(0);

  // Panel sizes in px and focus mode, remembered in this browser.
  const [leftW, setLeftW] = usePersistentState("panel.lesson", 460);
  const [treeW, setTreeW] = usePersistentState("panel.tree", 200);
  const [termH, setTermH] = usePersistentState("panel.terminal", 260);
  const [focus, setFocus] = usePersistentState("focus", false);

  const terminalRef = useRef<TerminalHandle>(null);
  const stepTimer = useRef(0);

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
    setSteps(null);
    setResult(null);
    setDrawerOpen(false);
    setPredicts({});
    Promise.all([api.chapter(labId, chapterId), api.chapterProgress(labId, chapterId)])
      .then(([c, p]) => {
        const at = Math.min(p.current_step, c.steps.length - 1);
        setMarkdown(c.markdown);
        setSteps(c.steps);
        setStep(at);
        setVisited(at);
        setHints(p.hints);
      })
      .catch((e) => toast(errMsg(e)));
  }, [labId, chapterId, toast]);

  // ---------- steps ----------

  const goStep = useCallback(
    (i: number) => {
      if (!steps) return;
      const next = Math.max(0, Math.min(i, steps.length - 1));
      setStep(next);
      setVisited((v) => Math.max(v, next));
      // Remember the position on the server (per user), a moment after the last move.
      window.clearTimeout(stepTimer.current);
      stepTimer.current = window.setTimeout(() => {
        api.saveStep(labId, chapterId, next).catch(() => {
          /* not worth a toast: the worst case is resuming one step back */
        });
      }, STEP_SAVE_MS);
    },
    [steps, labId, chapterId],
  );

  // Arrow keys move between steps, except while typing (editor, terminal, inputs).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey || isTyping(e.target)) return;
      if (e.key === "ArrowRight") goStep(step + 1);
      else if (e.key === "ArrowLeft") goStep(step - 1);
      else return;
      e.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [goStep, step]);

  function pickPredict(index: number, option: number) {
    const s = steps?.[index].predict;
    if (!s) return;
    setPredicts((all) => {
      const cur = all[index] ?? NO_PREDICT;
      if (cur.solved) return all;
      return { ...all, [index]: option === s.answer ? { ...cur, solved: true } : { ...cur, wrong: [...cur.wrong, option] } };
    });
  }

  async function revealHint(taskId: string) {
    setHintBusy(true);
    try {
      const r = await api.hint(labId, chapterId, taskId);
      setHints((h) => ({ ...h, [taskId]: r.hints }));
      setLab((l) =>
        l && {
          ...l,
          chapters: l.chapters.map((c) => ({
            ...c,
            tasks: c.tasks.map((t) => (t.id === taskId ? { ...t, xp: r.xp, hints_used: r.hints.length } : t)),
          })),
        },
      );
    } catch (e) {
      toast(errMsg(e));
    } finally {
      setHintBusy(false);
    }
  }

  function runInTerminal(command: string) {
    setBottomTab("terminal");
    // Let the terminal tab become visible first, then paste (no Enter: the learner presses it).
    window.setTimeout(() => {
      if (!terminalRef.current?.paste(command)) toast("The terminal is not connected yet");
    }, 0);
  }

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
      setDrawerOpen(false);
      await refreshTree();
      toast("Lab reset to the starter files", "info");
    } catch (e) {
      setStatus("error");
      toast(errMsg(e));
    }
  }

  async function runCheck() {
    const wasDone = !!chapter && chapter.tasks.every((t) => t.passed);
    setChecking(true);
    setDrawerOpen(true);
    try {
      await saveAll();
      setResult(await api.check(labId, chapterId));
      const detail = await loadLab();
      const now = detail.chapters.find((c) => c.id === chapterId);
      if (!wasDone && now?.tasks.every((t) => t.passed)) {
        celebrate();
        const recap = steps?.findIndex((s) => s.type === "recap") ?? -1;
        if (recap >= 0) goStep(recap);
      }
    } catch (e) {
      setDrawerOpen(false);
      toast(e instanceof ApiError && e.status === 429 ? "A check is already running" : `Check failed: ${errMsg(e)}`);
    } finally {
      setChecking(false);
    }
  }

  // ---------- render ----------

  const chapter = lab?.chapters.find((c) => c.id === chapterId);
  const chapterIndex = lab?.chapters.findIndex((c) => c.id === chapterId) ?? -1;
  const nextChapter = lab && chapterIndex >= 0 ? lab.chapters[chapterIndex + 1] : undefined;
  const current = steps?.[step];
  const tasks = chapter?.tasks ?? [];
  const activeTask = tasks.find((t) => t.id === current?.task) ?? tasks.find((t) => !t.passed);
  const activeHintsLeft = activeTask ? activeTask.hint_count - (hints[activeTask.id]?.length ?? 0) : 0;

  const stepOfTask = (taskId: string) => steps?.findIndex((s) => s.task === taskId) ?? -1;

  function footerHint() {
    if (!activeTask) return;
    const i = stepOfTask(activeTask.id);
    if (i >= 0) goStep(i); // show the hint where the task is explained
    revealHint(activeTask.id);
  }

  if (status === "starting" && tabs.length === 0 && tree.length === 0) {
    return (
      <div className="center-screen">
        <span className="spinner" /> Starting your machine...
      </div>
    );
  }

  return (
    <div className={`lab-page ${focus ? "focus-mode" : ""}`}>
      <StatusBar
        title={lab?.title ?? labId}
        chapters={lab?.chapters ?? []}
        chapterId={chapterId}
        onChapter={setChapterId}
        progress={lab?.progress ?? null}
        status={status}
        username={user?.username ?? ""}
        focus={focus}
        onFocus={() => setFocus((f) => !f)}
        onStart={startMachine}
        onStop={stopMachine}
        onReset={resetLab}
      />
      <main className="lab-body">
        <aside className="left-panel" style={{ width: leftW }}>
          {steps && current ? (
            <LessonPanel steps={steps} current={step} visited={visited} onGo={goStep}>
              {steps.length === 1 ? (
                <ChapterPanel markdown={current.markdown} onRun={runInTerminal} />
              ) : (
                <StepCard
                  step={current}
                  task={tasks.find((t) => t.id === current.task)}
                  hints={current.task ? hints[current.task] ?? [] : []}
                  hintBusy={hintBusy}
                  predict={predicts[step] ?? NO_PREDICT}
                  checking={checking}
                  chapterDone={tasks.length > 0 && tasks.every((t) => t.passed)}
                  tasksLeft={tasks.filter((t) => !t.passed).length}
                  hasNextChapter={!!nextChapter}
                  onPredict={(o) => pickPredict(step, o)}
                  onHint={revealHint}
                  onRun={runInTerminal}
                  onCheck={runCheck}
                  onNextChapter={() => nextChapter && setChapterId(nextChapter.id)}
                />
              )}
            </LessonPanel>
          ) : (
            <ChapterPanel markdown={markdown === null ? null : ""} />
          )}
          <div className="left-footer">
            {chapter && (
              <TaskList
                tasks={chapter.tasks}
                activeId={activeTask?.id}
                onSelect={(id) => {
                  const i = stepOfTask(id);
                  if (i >= 0) goStep(i);
                }}
              />
            )}
            <div className="footer-actions">
              <button className="btn btn-primary btn-check" onClick={runCheck} disabled={checking || !chapterId}>
                {checking ? <><span className="spinner" /> Checking...</> : "Check"}
              </button>
              {activeTask && activeTask.hint_count > 0 && !activeTask.passed && (
                <button className="btn btn-ghost" onClick={footerHint} disabled={hintBusy || activeHintsLeft === 0}>
                  {activeHintsLeft > 0 ? `Hint (${activeHintsLeft} left)` : "No hints left"}
                </button>
              )}
            </div>
          </div>
        </aside>
        <Splitter direction="vertical" label="Resize lesson panel" onDrag={(d) => setLeftW((w) => clamp(w + d, 280, 900))} />
        <section className="work-area" aria-label="Workspace">
          <div className="files-and-editor">
            {!focus && (
              <>
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
                <Splitter direction="vertical" label="Resize file tree" onDrag={(d) => setTreeW((w) => clamp(w + d, 120, 500))} />
              </>
            )}
            <EditorPane tabs={tabs} activePath={activePath} onSelect={setActivePath} onClose={closeTab} onChange={onChange} onSave={save} />
          </div>
          <Splitter direction="horizontal" label="Resize terminal" onDrag={(d) => setTermH((h) => clamp(h - d, 80, 800))} />
          <div style={{ height: termH }} className="terminal-wrap">
            <div className="bottom-tabs" role="tablist" aria-label="Bottom panel">
              <button role="tab" aria-selected={bottomTab === "terminal"} className="bottom-tab" onClick={() => setBottomTab("terminal")}>
                Terminal
              </button>
              <button role="tab" aria-selected={bottomTab === "output"} className="bottom-tab" onClick={() => setBottomTab("output")}>
                Output
              </button>
            </div>
            <div className="bottom-body" hidden={bottomTab !== "terminal"}>
              <TerminalPane
                ref={terminalRef}
                labId={labId}
                enabled={status === "running"}
                connectKey={terminalKey}
                onConnected={() => setStatus("running")}
              />
            </div>
            <div className="bottom-body" hidden={bottomTab !== "output"}>
              <pre className="output" tabIndex={0}>
                {result ? result.output || "(the check printed nothing)" : "Press Check to see the raw output of the hidden tests here."}
              </pre>
            </div>
          </div>
          <CheckDrawer
            result={result}
            running={checking}
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
            onShowOutput={() => setBottomTab("output")}
          />
        </section>
      </main>
    </div>
  );
}
