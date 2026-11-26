import confetti from "canvas-confetti";
import { useCallback, useEffect, useRef, useState, type CSSProperties } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api, ApiError, type CheckResponse, type FileNode, type LabDetail, type DesignAttempt, type PredictState, type ServiceStatus, type Step } from "../api";
import { useAuth } from "../auth";
import { usePhone } from "../usePhone";
import ChapterPanel from "../components/ChapterPanel";
import CheckDrawer from "../components/CheckDrawer";
import IdePane from "../components/IdePane";
import EditorPane, { type Tab } from "../components/EditorPane";
import FileTree from "../components/FileTree";
import PreviewPane from "../components/PreviewPane";
import Splitter from "../components/Splitter";
import StatusBar, { type UiStatus } from "../components/StatusBar";
import TaskList from "../components/TaskList";
import TerminalPane, { type TerminalHandle } from "../components/TerminalPane";
import { useToast } from "../components/Toasts";
import LessonPanel from "../lesson/LessonPanel";
import StepCard, { NO_PREDICT } from "../lesson/StepCard";
import TutorBox from "../lesson/TutorBox";
import { labBrand } from "../brand";
import { MODEL_PREFIX, modelUri, monaco } from "../monaco";
import { usePersistentState } from "../persist";
import ReadCode from "../lesson/ReadCode";
import StepOutline, { PanelIcon } from "../lesson/StepOutline";
import { useStats } from "../stats";
import { useTextSizes } from "../textSize";

const AUTOSAVE_MS = 800;
const TREE_POLL_MS = 5000;
const STATUS_POLL_MS = 10000;
const STEP_SAVE_MS = 400;

function firstFile(nodes: FileNode[]): string | null {
  for (const n of nodes) {
    if (n.type === "file") return n.path;
  }
  for (const n of nodes) {
    const inner = n.type === "dir" && n.children ? firstFile(n.children) : null;
    if (inner) return inner;
  }
  return null;
}

const isTyping = (t: EventTarget | null) =>
  t instanceof HTMLElement && (t.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName));

function confettiBurst() {
  // Small and once; canvas-confetti skips it entirely for prefers-reduced-motion.
  confetti({ particleCount: 90, spread: 70, origin: { x: 0.2, y: 0.7 }, disableForReducedMotion: true });
}

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));
const errMsg = (e: unknown) => (e instanceof Error ? e.message : String(e));

/*
 * At most a few labs at a time (owner, 26 November): a locked lab opens nothing but its course page, so the lab
 * page asks first and sends the learner there (with the Unlock button) before any lesson or machine is asked for.
 */
export default function LabPage() {
  const { labId = "" } = useParams();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  useEffect(() => {
    setOpen(false);
    api.slots()
      .then((s) => (s.labs[labId] === "locked" ? navigate(`/courses/${labId}`, { replace: true }) : setOpen(true)))
      .catch(() => setOpen(true));  // the lab's own calls still answer 403 if it is locked
  }, [labId, navigate]);
  return open ? <LabWorkspace /> : null;
}

function LabWorkspace() {
  const { labId = "" } = useParams();
  const { user } = useAuth();
  const toast = useToast();
  const { celebrate } = useStats();

  const [lab, setLab] = useState<LabDetail | null>(null);
  const [chapterId, setChapterId] = useState("");
  const [searchParams] = useSearchParams();
  const phone = usePhone();
  const [markdown, setMarkdown] = useState<string | null>(null);
  const [steps, setSteps] = useState<Step[] | null>(null);
  const [step, setStep] = useState(0);
  const [visited, setVisited] = useState(0);
  const [hints, setHints] = useState<Record<string, string[]>>({});
  const [hintBusy, setHintBusy] = useState(false);
  const [predicts, setPredicts] = useState<Record<number, PredictState>>({});
  const [designs, setDesigns] = useState<Record<number, DesignAttempt>>({});
  const [predictBusy, setPredictBusy] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [bottomTab, setBottomTab] = useState<"terminal" | "preview" | "output">("terminal");
  const [services, setServices] = useState<ServiceStatus[] | undefined>(undefined);
  const [setupState, setSetupState] = useState<"idle" | "running" | "error">("idle");
  const [startedAt, setStartedAt] = useState<string | null>(null);
  const [chapterXp, setChapterXp] = useState(0);
  const autoOpened = useRef(false);
  const chapterFileOpened = useRef(false); // set once chapter focus opened the chapter's own file
  const [status, setStatus] = useState<UiStatus>("starting");
  const [tree, setTree] = useState<FileNode[]>([]);
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [activePath, setActivePath] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);
  const [result, setResult] = useState<CheckResponse | null>(null);
  const [terminalKey, setTerminalKey] = useState(0);

  // Panel sizes in px and focus mode, remembered in this browser.
  const [leftW, setLeftW] = usePersistentState("panel.lesson", 460);
  const sizes = useTextSizes();
  const [treeW, setTreeW] = usePersistentState("panel.tree", 200);
  const [termH, setTermH] = usePersistentState("panel.terminal", 260);
  const [focus, setFocus] = usePersistentState("focus", false);
  // Read mode: the lesson alone, no editor, terminal or machine. Action mode: the lesson beside the editor and
  // terminal, for tasks and practice. The last one used is remembered; a first visit reads (owner, 25 November).
  const [mode, setMode] = usePersistentState<"read" | "action">("mode", "read");
  const reading = phone || mode === "read";
  // Read mode's list of steps on the left; the panel button closes it and brings it back (remembered).
  const [outlineOpen, setOutlineOpen] = usePersistentState("steps-list", false);  // closed until opened (owner)
  const showOutline = reading && !phone;
  // Action mode can hide the whole lesson panel, so the editor and terminal get the page (owner, 25 November).
  const [lessonOpen, setLessonOpen] = usePersistentState("lesson-panel", true);
  const lessonHidden = !reading && !lessonOpen;
  // "vscode": real VS Code in the machine (when the server has it); "classic": our Monaco editor.
  const [editorKind, setEditorKind] = usePersistentState<"vscode" | "classic">("editor", "vscode");
  const [ideError, setIdeError] = useState<string | null>(null);
  // Phones and small windows always get the light editor: the IDE needs a desktop-sized screen.
  const [narrow, setNarrow] = useState(() => window.innerWidth < 900);
  useEffect(() => {
    const onResize = () => setNarrow(window.innerWidth < 900);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  const useIde = editorKind === "vscode" && !ideError && !narrow;
  const onIdeUnavailable = useCallback((why: string) => setIdeError(why), []);
  const switchEditor = (kind: "vscode" | "classic") => {
    if (kind === "classic") {
      // VS Code may have changed files: reopen them fresh instead of showing (or saving) old copies.
      setTabs([]);
      setActivePath(null);
    }
    setIdeError(null);
    setEditorKind(kind);
  };

  // Up to three terminals (Terminal 1 runs a server, Terminal 2 sends it requests); each is its own shell.
  const [terms, setTerms] = useState<number[]>([1]);
  const [activeTerm, setActiveTerm] = useState(1);
  const terminalRefs = useRef(new Map<number, TerminalHandle>());
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

  // A safety limit (session length, stuck CPU, disk, too many running labs) says why it stopped.
  const [stopReason, setStopReason] = useState<string | null>(null);

  const startMachine = useCallback(async () => {
    setStatus("starting");
    setStopReason(null);
    try {
      await api.startWorkspace(labId);
      setStatus("running");
      setTerminalKey((k) => k + 1);
    } catch (e) {
      setStatus("error");
      toast(`Could not start your machine: ${errMsg(e)}`);
    }
  }, [labId, toast]);

  // ?step= (from a skill map subtopic) opens that lesson step of the ?chapter= once, on arrival.
  const arrivalStep = useRef<{ chapter: string; step: number } | null>(
    searchParams.get("chapter") && /^\d+$/.test(searchParams.get("step") ?? "")
      ? { chapter: searchParams.get("chapter")!, step: Number(searchParams.get("step")) }
      : null,
  );

  useEffect(() => {
    loadLab()
      .then((d) => {
        // ?chapter= (from the dashboard's Continue card) wins; otherwise the first unfinished chapter.
        const wanted = d.chapters.find((c) => c.id === searchParams.get("chapter"));
        const firstOpen = wanted ?? d.chapters.find((c) => c.tasks.some((t) => !t.passed)) ?? d.chapters[0];
        setChapterId(firstOpen.id);
      })
      .catch((e) => toast(errMsg(e)));
    // searchParams is read once on arrival: later changes must not reload the lab and move the learner.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loadLab, toast]);

  // The machine starts in Action mode, and in Read mode one step before a task (below), never on a phone. Its own
  // effect, so switching modes or crossing the phone width starts it without reloading the lab or moving the
  // learner to another chapter. Once started it keeps running when the learner switches back to Read.
  const machineAsked = useRef(false);
  const ensureMachine = useCallback(() => {
    if (machineAsked.current) return;
    machineAsked.current = true;
    startMachine().then(refreshTree);
  }, [startMachine, refreshTree]);
  useEffect(() => {
    if (!reading) ensureMachine();
  }, [reading, ensureMachine]);

  useEffect(() => {
    if (!chapterId) return;
    setMarkdown(null);
    setSteps(null);
    setResult(null);
    setDrawerOpen(false);
    setPredicts({});
    Promise.all([api.chapter(labId, chapterId), api.chapterProgress(labId, chapterId)])
      .then(([c, p]) => {
        const jump = arrivalStep.current?.chapter === chapterId ? arrivalStep.current.step : null;
        arrivalStep.current = null;
        const at = Math.min(jump ?? p.current_step, c.steps.length - 1);
        setMarkdown(c.markdown);
        setSteps(c.steps);
        setStep(at);
        setVisited(Math.max(at, Math.min(p.current_step, c.steps.length - 1)));  // a jump back keeps later steps open
        setHints(p.hints);
        setChapterXp(p.xp_earned);
        setPredicts(Object.fromEntries(Object.entries(p.predicts).map(([k, v]) => [Number(k), v])));
        setDesigns(Object.fromEntries(Object.entries(p.designs ?? {}).map(([k, v]) => [Number(k), v])));
      })
      .catch((e) => toast(errMsg(e)));
  }, [labId, chapterId, toast]);

  // Chapter setup: seed data or an injected incident, once per learner. Also starts the incident timer.
  const chapterMeta = lab?.chapters.find((c) => c.id === chapterId);
  // Fetch every photo of this chapter in the background as soon as it opens, so each one is already there when its
  // step comes up (owner, 24 November: "sometimes it fetches, sometimes it does not").
  useEffect(() => {
    if (!steps) return;
    const srcs = new Set<string>();
    for (const st of steps) for (const m of st.markdown.matchAll(/:::photo\{src="([^"]+)"/g)) srcs.add(m[1]);
    const held = [...srcs].map((src) => { const img = new Image(); img.decoding = "async"; img.src = src; return img; });
    return () => { held.length = 0; };
  }, [steps]);

  const needsSetup = !!chapterMeta && (chapterMeta.has_setup || !!steps?.some((s) => s.type === "incident"));
  useEffect(() => {
    if (!needsSetup || status !== "running") return;
    let cancelled = false;
    setSetupState("running");
    api
      .chapterSetup(labId, chapterId)
      .then((r) => {
        if (cancelled) return;
        setStartedAt(r.started_at);
        setSetupState("idle");
        if (r.ran) toast("This chapter's machine is ready", "info");
        api.workspaceStatus(labId).then((s) => !cancelled && setServices(s.services)).catch(() => {});
      })
      .catch((e) => {
        if (cancelled) return;
        setSetupState("error");
        toast(`Could not set up this chapter: ${errMsg(e)}`);
      });
    return () => {
      // Leaving the chapter mid-setup must not leave the banner (and a disabled Check) behind.
      cancelled = true;
      setSetupState("idle");
    };
  }, [needsSetup, status, labId, chapterId, toast]);

  // In Read mode, start the machine quietly when a task is this step or the next one, so the usual wait is
  // mostly over by the time the learner opens Action mode.
  useEffect(() => {
    if (phone || !reading || !steps) return;
    if ([steps[step], steps[step + 1]].some((st) => st && (st.type === "task" || st.type === "incident"))) ensureMachine();
  }, [phone, reading, steps, step, ensureMachine]);

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

  // Answers are checked on the server; the right one and its explanation come back once you get it.
  async function pickPredict(index: number, option: number) {
    if (predicts[index]?.solved) return;
    setPredictBusy(true);
    try {
      const state = await api.predict(labId, chapterId, index, option);
      setPredicts((all) => ({ ...all, [index]: state }));
      if (state.xp_awarded?.length) {
        celebrate(state.xp_awarded);
        setChapterXp((x) => x + state.xp_awarded!.reduce((n, a) => n + a.amount, 0));
      }
    } catch (e) {
      toast(errMsg(e));
    } finally {
      setPredictBusy(false);
    }
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
      if (!terminalRefs.current.get(activeTerm)?.paste(command)) toast("The terminal is not connected yet");
    }, 0);
  }

  // "Run in terminal" in Read mode opens Action mode and pastes the command once the terminal is connected.
  const pendingRun = useRef<string | null>(null);
  function runFromRead(command: string) {
    pendingRun.current = command;
    setMode("action");
  }
  useEffect(() => {
    if (reading || status !== "running" || !pendingRun.current) return;
    let tries = 0;
    const id = window.setInterval(() => {
      const cmd = pendingRun.current;
      if (!cmd) return window.clearInterval(id);
      setBottomTab("terminal");
      if (terminalRefs.current.get(activeTerm)?.paste(cmd) || ++tries > 40) {
        pendingRun.current = null;
        window.clearInterval(id);
      }
    }, 300);
    return () => window.clearInterval(id);
  }, [reading, status, activeTerm]);

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
        setStopReason(s.status !== "running" ? s.stopped_reason ?? null : null);
        setServices(s.services);
      } catch {
        /* toast-worthy errors surface elsewhere */
      }
    }, STATUS_POLL_MS);
    return () => window.clearInterval(id);
  }, [labId]);

  // Open the first file once, so a new learner lands with code in front of them.
  useEffect(() => {
    if (autoOpened.current || tree.length === 0) return;
    autoOpened.current = true;
    // The chapter's own file (chapter focus) beats "the first file": skip it once that file is open.
    // (If the chapter's file is asked for later, it still wins: the last file asked for is shown.)
    if (chapterFileOpened.current) return;
    const first = firstFile(tree);
    if (first && tabsRef.current.length === 0) openFile(first);
    // Only tree is a dependency on purpose: this runs once per page, when the files first arrive.
  }, [tree]);

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

  // Switching chapters opens that chapter's code (in VS Code through the backend, in Lite here).
  // A step that is about a file opens that file instead (the effect below), so the two never race.
  const focusedRef = useRef<string | null>(null);
  useEffect(() => {
    if (status !== "running" || !chapterId || !steps) return;
    const key = `${chapterId}/${useIde}`;
    if (focusedRef.current === key) return;
    focusedRef.current = key;
    if (hasOwnFile(steps[step])) return;
    api.chapterFocus(labId, chapterId, useIde).then((f) => {
      if (!f.path || useIde) return;
      const path = f.path;
      chapterFileOpened.current = true;
      openFile(path).then(() => revealLine(path, f.line));
    }).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, chapterId, useIde, labId, steps]);

  // Each lesson step opens the file it talks about (file= and line= in the lesson), and a task step
  // opens its own task's TODO, so the lesson and the code on the right always match.
  const stepFocusRef = useRef<string | null>(null);
  useEffect(() => {
    if (status !== "running" || !chapterId || !steps || !hasOwnFile(steps[step])) return;
    const key = `${chapterId}/${step}/${useIde}`;
    if (stepFocusRef.current === key) return;
    stepFocusRef.current = key;
    api.chapterFocus(labId, chapterId, useIde, step).then((f) => {
      if (!f.path || useIde) return;
      const path = f.path;
      chapterFileOpened.current = true;
      openFile(path).then(() => revealLine(path, f.line, f.end_line ?? undefined));
    }).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, chapterId, step, steps, useIde, labId]);

  // The file asked for last is the one shown, whatever order the answers arrive in (the first-file
  // open and the chapter's file can both be loading; with several backend workers either may finish first).
  const openSeq = useRef(0);
  async function openFile(path: string) {
    const seq = ++openSeq.current;
    if (tabsRef.current.some((t) => t.path === path)) {
      setActivePath(path);
      return;
    }
    try {
      const { content } = await api.readFile(labId, path);
      setTabs((ts) => (ts.some((t) => t.path === path) ? ts : [...ts, { path, content, saved: content, status: "idle" }]));
      if (seq === openSeq.current) setActivePath(path);
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
      const res = await api.check(labId, chapterId);
      setResult(res);
      celebrate(res.xp_awarded);
      if (res.xp_awarded?.length) {
        api.chapterProgress(labId, chapterId).then((p) => setChapterXp(p.xp_earned)).catch(() => {});
      }
      const detail = await loadLab();
      const now = detail.chapters.find((c) => c.id === chapterId);
      if (!wasDone && now?.tasks.every((t) => t.passed)) {
        confettiBurst();
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
  // Tasks on steps the learner has not reached yet: a check runs them too, but they are "coming up",
  // not failures (shown neutral in the results and the task dots).
  const upcoming: Record<string, number> = Object.fromEntries(
    (steps ?? []).flatMap((st, i) => (st.type === "task" && st.task && i > Math.max(visited, step) ? [[st.task, i + 1]] : [])),
  );
  const tasks = chapter?.tasks ?? [];
  const activeTask = tasks.find((t) => t.id === current?.task) ?? tasks.find((t) => !t.passed);
  const activeHintsLeft = activeTask ? activeTask.hint_count - (hints[activeTask.id]?.length ?? 0) : 0;
  const [tutorOpen, setTutorOpen] = useState(false);
  const brand = labBrand(lab?.cover_credit);

  const stepOfTask = (taskId: string) => steps?.findIndex((s) => s.task === taskId) ?? -1;

  function footerHint() {
    if (!activeTask) return;
    const i = stepOfTask(activeTask.id);
    if (i >= 0) goStep(i); // show the hint where the task is explained
    revealHint(activeTask.id);
  }

  if (!reading && status === "starting" && tabs.length === 0 && tree.length === 0) {
    return (
      <div className="center-screen">
        <span className="spinner" /> Starting your machine...
      </div>
    );
  }

  return (
    <div className={`lab-page ${focus && !reading ? "focus-mode" : ""} ${phone ? "is-phone" : ""} ${reading ? "is-reading" : "is-action"} ${showOutline && outlineOpen ? "has-outline" : ""} ${lessonHidden ? "lesson-hidden" : ""}`} data-lab={labId}>
      <StatusBar
        title={lab?.title ?? labId}
        chapters={lab?.chapters ?? []}
        chapterId={chapterId}
        onChapter={setChapterId}
        progress={lab?.progress ?? null}
        status={status}
        services={services}
        username={user?.username ?? ""}
        focus={focus}
        onFocus={() => setFocus((f) => !f)}
        canFocus={!useIde && !reading}
        mode={reading ? "read" : "action"}
        onMode={phone ? undefined : setMode}
        onStart={startMachine}
        onStop={stopMachine}
        onReset={resetLab}
      />
      <main className="lab-body">
        {lessonHidden && (
          <div className="lesson-rail" aria-label="Lesson (hidden)">
            <button className="panel-toggle" onClick={() => setLessonOpen(true)} aria-label="Show the lesson" title="Show the lesson">
              <PanelIcon />
            </button>
            <button className="panel-toggle lesson-rail-check" onClick={runCheck} disabled={checking || !chapterId || setupState === "running"} aria-label="Check" title="Check your work">
              {checking ? <span className="spinner" /> : "✓"}
            </button>
          </div>
        )}
        <aside
          hidden={lessonHidden}
          className="left-panel"
          style={{ width: leftW, "--ts-lesson": sizes.lesson / 100, "--ts-tasks": sizes.tasks / 100 } as CSSProperties}
        >
          {brand && (
            <div
              className="lesson-watermark"
              aria-hidden="true"
              style={{ "--wm-logo": `url(${brand.logo})`, "--wm-color": brand.color } as CSSProperties}
            />
          )}
          {!reading && (
            <button className="panel-toggle lesson-hide" onClick={() => setLessonOpen(false)} aria-label="Hide the lesson" title="Hide the lesson: the editor and terminal get the whole page">
              <PanelIcon />
            </button>
          )}
          {showOutline && steps && steps.length > 1 && (outlineOpen
            ? <StepOutline steps={steps} current={step} visited={visited} onGo={goStep} onClose={() => setOutlineOpen(false)} />
            : <button className="panel-toggle step-outline-open" onClick={() => setOutlineOpen(true)} aria-label="Show the list of scenes" title="Show the list of scenes"><PanelIcon /></button>)}
          {stopReason && status !== "running" && status !== "starting" && (
            <div className="limit-banner" role="alert">
              <p>{stopReason}</p>
              <button className="btn btn-small" onClick={startMachine}>Start machine</button>
            </div>
          )}
          {setupState === "running" && (
            <div className="setup-banner" role="status">
              <span className="spinner" /> Setting up this chapter on your machine. This can take a few seconds.
            </div>
          )}
          {steps && current ? (
            <LessonPanel steps={steps} current={step} visited={visited} onGo={goStep}>
              {reading && !phone && (current.type === "task" || current.type === "incident") && (
                <div className="read-task-card" role="note">
                  <div>
                    <strong>Your turn: open the lab</strong>
                    <span>The editor and terminal are in Action mode{status === "running" ? ", and your machine is ready" : status === "starting" ? ", and your machine is starting" : ""}.</span>
                  </div>
                  <button className="btn btn-primary" onClick={() => setMode("action")}>Open Action mode</button>
                </div>
              )}
              {steps.length === 1 ? (
                <ChapterPanel markdown={current.markdown} onRun={phone ? undefined : reading ? runFromRead : runInTerminal} />
              ) : (
                <StepCard
                  labId={labId}
                  chapterId={chapterId}
                  stepIndex={step}
                  design={designs[step]}
                  onDesignGraded={(attempt) => {
                    setDesigns((all) => ({ ...all, [step]: attempt }));
                    if (attempt.result.xp_awarded?.length) {
                      celebrate(attempt.result.xp_awarded);
                      setChapterXp((x) => x + attempt.result.xp_awarded!.reduce((n, a) => n + a.amount, 0));
                    }
                  }}
                  step={current}
                  task={tasks.find((t) => t.id === current.task)}
                  hints={current.task ? hints[current.task] ?? [] : []}
                  hintBusy={hintBusy}
                  predict={predicts[step] ?? NO_PREDICT}
                  predictBusy={predictBusy}
                  checking={checking}
                  chapterDone={tasks.length > 0 && tasks.every((t) => t.passed)}
                  tasksLeft={tasks.filter((t) => !t.passed).length}
                  hasNextChapter={!!nextChapter}
                  chapterXp={chapterXp}
                  startedAt={startedAt}
                  checkMode={lab?.check_mode ?? "fresh"}
                  onPredict={(o) => pickPredict(step, o)}
                  onHint={revealHint}
                  onRun={phone ? undefined : reading ? runFromRead : runInTerminal}
                  onCheck={runCheck}
                  onNextChapter={() => nextChapter && setChapterId(nextChapter.id)}
                />
              )}
              {reading && hasOwnFile(current) && <ReadCode labId={labId} chapterId={chapterId} step={step} />}
            </LessonPanel>
          ) : (
            <ChapterPanel markdown={markdown === null ? null : ""} />
          )}
          <div className="left-footer">
            {chapter && (
              <TaskList
                ahead={upcoming}
                tasks={chapter.tasks}
                activeId={activeTask?.id}
                onSelect={(id) => {
                  const i = stepOfTask(id);
                  if (i >= 0) goStep(i);
                }}
              />
            )}
            {tutorOpen && activeTask && (
              <TutorBox key={`${chapterId}/${activeTask.id}/${activeTask.passed}`} labId={labId} chapterId={chapterId} task={activeTask} startOpen onClose={() => setTutorOpen(false)} />
            )}
            {phone ? (
              <p className="phone-note" role="note">
                Reading mode. Writing and checking code works on a laptop or tablet; your place is saved, so you can pick it up there.
              </p>
            ) : reading ? (
              activeTask && !activeTask.passed && (
                <div className="footer-actions">
                  <button className="btn btn-primary read-practice" onClick={() => setMode("action")}>Practice in Action mode</button>
                </div>
              )
            ) : (
            <div className="footer-actions">
              <button className="btn btn-primary btn-check" onClick={runCheck} disabled={checking || !chapterId || setupState === "running"}>
                {checking ? <><span className="spinner" /> Checking...</> : "Check"}
              </button>
              {activeTask && activeTask.hint_count > 0 && !activeTask.passed && (
                <button
                  className="btn btn-ghost btn-icon"
                  onClick={footerHint}
                  disabled={hintBusy || activeHintsLeft === 0}
                  aria-label={activeHintsLeft > 0 ? `Hint (${activeHintsLeft} left)` : "No hints left"}
                  title={activeHintsLeft > 0 ? `Hint (${activeHintsLeft} left)` : "No hints left"}
                >
                  <svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2V16h5v-.1c0-.8.4-1.5 1-2A6 6 0 0 0 12 3z" />
                  </svg>
                  {activeHintsLeft > 0 && <span className="btn-badge">{activeHintsLeft}</span>}
                </button>
              )}
              {activeTask && (
                <button
                  className="btn btn-ghost btn-icon btn-ask-ai"
                  onClick={() => setTutorOpen((o) => !o)}
                  aria-expanded={tutorOpen}
                  aria-label={activeTask.passed ? "Review with the tutor" : "Ask AI"}
                  title={activeTask.passed ? "Review with the tutor" : "Ask the AI tutor"}
                >
                  <span aria-hidden="true">✦</span>
                </button>
              )}
            </div>
            )}
          </div>
        </aside>
        {/* Read mode (and every phone): no editor, VS Code or terminal. */}
        {!reading && (
        <>
        {!lessonHidden && <Splitter direction="vertical" label="Resize lesson panel" onDrag={(d) => setLeftW((w) => clamp(w + d, 280, 900))} />}
        <section className="work-area" aria-label="Workspace">
          <div className="files-and-editor">
            {useIde ? (
              <IdePane labId={labId} onUnavailable={onIdeUnavailable} />
            ) : (
            <>
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
            <EditorPane labId={labId} tabs={tabs} activePath={activePath} onSelect={setActivePath} onClose={closeTab} onChange={onChange} onSave={save} />
            </>
            )}
          </div>
          <Splitter direction="horizontal" label="Resize terminal" onDrag={(d) => setTermH((h) => clamp(h - d, 80, 800))} />
          <div style={{ height: termH }} className="terminal-wrap">
            <div className="bottom-tabs" role="tablist" aria-label="Bottom panel">
              {terms.map((n) => (
                <span key={n} className="bottom-tab-wrap">
                  <button role="tab" aria-selected={bottomTab === "terminal" && activeTerm === n} className="bottom-tab"
                    onClick={() => { setBottomTab("terminal"); setActiveTerm(n); }}>
                    {terms.length === 1 ? "Terminal" : `Terminal ${n}`}
                  </button>
                  {n !== 1 && (
                    <button className="bottom-tab-close" aria-label={`Close terminal ${n}`} title="Close this terminal"
                      onClick={() => { setTerms((ts) => ts.filter((x) => x !== n)); terminalRefs.current.delete(n); if (activeTerm === n) setActiveTerm(1); }}>
                      ×
                    </button>
                  )}
                </span>
              ))}
              {terms.length < 3 && (
                <button className="bottom-tab bottom-tab-add" aria-label="Open another terminal" title="Open another terminal (for example: one runs the server, one sends it requests)"
                  onClick={() => { const n = Math.max(...terms) + 1; setTerms((ts) => [...ts, n]); setActiveTerm(n); setBottomTab("terminal"); }}>
                  +
                </button>
              )}
              {!!lab?.preview.length && (
                <button role="tab" aria-selected={bottomTab === "preview"} className="bottom-tab" onClick={() => setBottomTab("preview")}>
                  Preview
                </button>
              )}
              <button role="tab" aria-selected={bottomTab === "output"} className="bottom-tab" onClick={() => setBottomTab("output")}>
                Output
              </button>
              <span className="spacer" />
              <div className="editor-switch" role="group" aria-label="Editor">
                <button aria-pressed={useIde} disabled={narrow} onClick={() => switchEditor("vscode")} title={narrow ? "The IDE needs a bigger screen" : ideError ?? "A full IDE (OpenVSCode Server) running in your machine"}>IDE</button>
                <button aria-pressed={!useIde} onClick={() => switchEditor("classic")} title="The light built-in editor, with AI completion">Lite</button>
              </div>
            </div>
            {terms.map((n) => (
              <div key={n} className="bottom-body" hidden={bottomTab !== "terminal" || activeTerm !== n}>
                <TerminalPane
                  ref={(h) => { if (h) terminalRefs.current.set(n, h); }}
                  labId={labId}
                  enabled={status === "running"}
                  connectKey={terminalKey}
                  onConnected={() => setStatus("running")}
                />
              </div>
            ))}
            {!!lab?.preview.length && (
              <div className="bottom-body" hidden={bottomTab !== "preview"}>
                <PreviewPane labId={labId} ports={lab.preview} visible={bottomTab === "preview"} />
              </div>
            )}
            <div className="bottom-body" hidden={bottomTab !== "output"}>
              <pre className="output" tabIndex={0}>
                {result ? result.output || "(the check printed nothing)" : "Press Check to see the raw output of the hidden tests here."}
              </pre>
            </div>
          </div>
          <CheckDrawer
            upcoming={upcoming}
            result={result}
            running={checking}
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
            onShowOutput={() => setBottomTab("output")}
          />
        </section>
        </>
        )}
      </main>
    </div>
  );
}

/** Put the Lite editor's cursor on a line, near the top, once the file's editor exists. */
/** A step that talks about a file, or a task step (it opens its own task's TODO). */
function hasOwnFile(s: Step | undefined): boolean {
  return !!s && (!!s.file || ((s.type === "task" || s.type === "incident") && !!s.task));
}

/** Scroll to a line; with end, select those whole lines (a step's line or range) so they stand out. */
function revealLine(path: string, line: number, end?: number, tries = 0) {
  const ed = monaco.editor.getEditors().find((e) => e.getModel()?.uri.toString() === modelUri(path));
  if (!ed) {
    if (tries < 30) setTimeout(() => revealLine(path, line, end, tries + 1), 100);
    return;
  }
  const model = ed.getModel();
  if (end !== undefined && model) {
    const last = Math.min(end, model.getLineCount());
    ed.setSelection({ startLineNumber: line, startColumn: 1, endLineNumber: last, endColumn: model.getLineMaxColumn(last) });
    ed.revealLinesNearTop(line, last);
  } else {
    ed.setPosition({ lineNumber: line, column: 1 });
    ed.revealLineNearTop(line);
  }
}
