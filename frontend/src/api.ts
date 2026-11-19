// All HTTP calls go through here. Adds the JWT and turns errors into ApiError.

const TOKEN_KEY = "labbox.token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";

  let res: Response;
  try {
    res = await fetch(path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  } catch {
    throw new ApiError(0, "Cannot reach the server");
  }
  // An expired login sends you to the login page, except the start-up "who am I" check
  // (public pages like the home page must still load; auth.tsx clears the token itself).
  if (res.status === 401 && !path.startsWith("/api/auth/") && path !== "/api/me") {
    setToken(null);
    window.location.assign("/login");
    throw new ApiError(401, "Session expired, please log in again");
  }
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail;
    const message = typeof detail === "string" ? detail : Array.isArray(detail) ? detail.map((d) => d.msg).join(", ") : res.statusText;
    throw new ApiError(res.status, message || `Request failed (${res.status})`);
  }
  return data as T;
}

const q = encodeURIComponent;

// ---------- types ----------

export interface User { id: number; username: string }
export interface AuthResponse { token: string; user: User }
export interface Progress { passed_tasks: number; total_tasks: number }
export interface LabInfo {
  subtitle: string;
  track: string;
  tags: string[];
  level: string | null;
  estimated_minutes: number | null;
  cover_url: string | null; // the lab's own cover; otherwise LabCover draws one
  cover_credit: { by: string; url: string; source: string } | null;
}
export interface LabSummary extends LabInfo { id: string; title: string; description: string; language: string; chapter_count: number; progress: Progress }
export interface Task { id: string; title: string; passed: boolean | null; xp: number; hint_count: number; hints_used: number }
export interface Chapter { id: string; title: string; tasks: Task[]; minutes: number | null; has_setup: boolean }
export interface PreviewPort { name: string; port: number; path: string }
export interface LabDetail extends LabInfo { preview: PreviewPort[]; services: string[]; check_mode: "fresh" | "live"; id: string; title: string; description: string; language: string; chapters: Chapter[]; progress: Progress }
export type StepType = "story" | "concept" | "example" | "predict" | "try" | "task" | "incident" | "recap" | "deep-dive" | "design";
// The answer and explanation are not sent with the chapter; they come back once answered correctly.
export interface Predict { question: string; options: { text: string }[] }
export interface XpAward { kind: string; amount: number; label: string }
export interface PredictState { wrong: number[]; solved: boolean; answer: number | null; explain: string | null; xp_awarded?: XpAward[] }
export interface DesignQuestion { id: string; text: string }
export interface DesignCriterion { id: string; score: number; max: number; feedback: string }
export interface DesignQuestionResult { id: string; score: number; max: number; criteria: DesignCriterion[] }
export interface DesignResult { score: number; max: number; questions: DesignQuestionResult[]; xp_awarded?: XpAward[]; created_at: string }
export interface DesignAttempt { answers: Record<string, string>; result: DesignResult }
export interface Step { type: StepType; title: string | null; task: string | null; minutes: number | null; markdown: string; predict: Predict | null; questions?: DesignQuestion[] }
export interface ChapterContent { id: string; title: string; markdown: string; steps: Step[] }
export interface ChapterProgress {
  current_step: number;
  step_count: number;
  hints: Record<string, string[]>;
  predicts: Record<string, PredictState>; // keyed by step index
  xp_earned: number;
  designs?: Record<string, DesignAttempt>; // keyed by step index: the last graded attempt
}
export interface TutorReply { reply: string; blocked: boolean; tokens_used_today: number }
export interface HintResponse { task: string; hints: string[]; hints_left: number; xp: number }
export type MachineStatus = "running" | "stopped" | "missing";
export interface ServiceStatus { name: string; status: "running" | "starting" | "stopped" | "missing" }
export interface WorkspaceStatus { status: MachineStatus; container?: string; services?: ServiceStatus[]; stopped_reason?: string }
export interface SetupResult { ran: boolean; setup_done: boolean; started_at: string | null }
export interface FileNode { path: string; name: string; type: "file" | "dir"; children?: FileNode[] }
export interface TaskResult { task: string; title: string; passed: boolean; message: string; expected?: string | null; actual?: string | null }
export interface Metric { name: string; value: number; target: number | null; better: "lower" | "higher" | null }
export interface CheckResponse {
  passed_count: number;
  total_count: number;
  results: TaskResult[];
  output: string;
  duration_ms: number;
  metrics?: Metric[];
  xp_awarded?: XpAward[];
}

// ---------- engagement ----------

export interface Stats {
  xp_total: number;
  level: number;
  level_xp: number;
  next_level_xp: number;
  streak_current: number;
  streak_best: number;
  freeze_available: boolean;
  today_xp: number;
  streak_min_xp: number;
  timezone: string | null;
  goal: string | null;
  needs_onboarding: boolean;
}
export interface Profile { display_name: string | null; timezone: string | null; goal: string | null; placement_level: string | null }
export interface Drill { id: string; kind: "predict" | "bug" | "command"; track: string; question: string; options: string[] }
export interface DrillState {
  day: string;
  drill: Drill | null;
  wrong: number[];
  solved: boolean;
  answer: number | null;
  explain: string | null;
  xp: number;
  xp_awarded: XpAward[];
}
export type NodeState = "done" | "available" | "locked" | "coming_soon";
export interface SkillNode {
  id: string;
  title: string;
  requires: string[];
  chapters: { lab_id: string; chapter_id: string; title: string; done: boolean }[];
  state: NodeState;
}
export interface SkillMap { track: string; title: string; nodes: SkillNode[] }
export interface CatalogLab extends LabInfo { id: string; title: string; chapter_count: number }
export interface TrackSummary { track: string; title: string; nodes: number; done: number }
export interface Onboarding { goals: { id: string; title: string; blurb: string }[]; placement: { question: string; options: string[] }[] }
export interface OnboardingResult {
  score: number;
  level: "beginner" | "intermediate" | "advanced";
  results: { correct: boolean; answer: number; explain: string }[];
  start: { lab_id: string; title: string };
  note: string | null;
}

// ---------- calls ----------

export const api = {
  signup: (username: string, password: string) => request<AuthResponse>("POST", "/api/auth/signup", { username, password }),
  login: (username: string, password: string) => request<AuthResponse>("POST", "/api/auth/login", { username, password }),
  me: () => request<User>("GET", "/api/me"),

  labs: () => request<LabSummary[]>("GET", "/api/labs"),
  lab: (labId: string) => request<LabDetail>("GET", `/api/labs/${q(labId)}`),
  chapter: (labId: string, chapterId: string) => request<ChapterContent>("GET", `/api/labs/${q(labId)}/chapters/${q(chapterId)}`),
  chapterProgress: (labId: string, chapterId: string) =>
    request<ChapterProgress>("GET", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/progress`),
  saveStep: (labId: string, chapterId: string, step: number) =>
    request<ChapterProgress>("PUT", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/progress`, { current_step: step }),
  predict: (labId: string, chapterId: string, step: number, choice: number) =>
    request<PredictState>("POST", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/predict`, { step, choice }),
  chapterFocus: (labId: string, chapterId: string, ide: boolean) =>
    request<{ path: string | null; line: number }>("POST", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/focus`, { ide }),
  chapterSetup: (labId: string, chapterId: string) =>
    request<SetupResult>("POST", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/setup`),
  previewTicket: (labId: string) => request<{ ports: PreviewPort[] }>("POST", `/api/labs/${q(labId)}/preview/ticket`),
  hint: (labId: string, chapterId: string, taskId: string) =>
    request<HintResponse>("POST", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/tasks/${q(taskId)}/hint`),
  openIde: (labId: string) => request<{ available: boolean; ready: boolean; url: string }>("POST", `/api/labs/${q(labId)}/ide`),
  aiConfig: () => request<{ completion: boolean }>("GET", "/api/ai/config"),
  complete: (labId: string, path: string, prefix: string, suffix: string) =>
    request<{ text: string }>("POST", `/api/labs/${q(labId)}/complete`, { path, prefix, suffix }),
  gradeDesign: (labId: string, chapterId: string, step: number, answers: Record<string, string>) =>
    request<DesignResult>("POST", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/design`, { step, answers }),
  tutor: (labId: string, chapterId: string, taskId: string, question: string) =>
    request<TutorReply>("POST", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/tasks/${q(taskId)}/tutor`, { question }),
  review: (labId: string, chapterId: string, taskId: string) =>
    request<TutorReply>("POST", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/tasks/${q(taskId)}/review`),

  startWorkspace: (labId: string) => request<WorkspaceStatus>("POST", `/api/labs/${q(labId)}/workspace/start`),
  stopWorkspace: (labId: string) => request<WorkspaceStatus>("POST", `/api/labs/${q(labId)}/workspace/stop`),
  resetWorkspace: (labId: string) => request<WorkspaceStatus>("POST", `/api/labs/${q(labId)}/workspace/reset`),
  workspaceStatus: (labId: string) => request<WorkspaceStatus>("GET", `/api/labs/${q(labId)}/workspace/status`),

  tree: (labId: string) => request<FileNode[]>("GET", `/api/labs/${q(labId)}/files`),
  readFile: (labId: string, path: string) => request<{ path: string; content: string }>("GET", `/api/labs/${q(labId)}/files/content?path=${q(path)}`),
  writeFile: (labId: string, path: string, content: string) => request<{ saved: boolean; bytes: number }>("PUT", `/api/labs/${q(labId)}/files/content`, { path, content }),
  newEntry: (labId: string, path: string, type: "file" | "dir") => request<{ created: boolean }>("POST", `/api/labs/${q(labId)}/files/new`, { path, type }),
  rename: (labId: string, from: string, to: string) => request<{ renamed: boolean }>("POST", `/api/labs/${q(labId)}/files/rename`, { from, to }),
  deleteEntry: (labId: string, path: string) => request<{ deleted: boolean }>("DELETE", `/api/labs/${q(labId)}/files?path=${q(path)}`),

  catalog: () => request<CatalogLab[]>("GET", "/api/catalog"), // public, no login
  stats: () => request<Stats>("GET", "/api/me/stats"),
  saveProfile: (p: Partial<Pick<Profile, "display_name" | "timezone" | "goal">>) => request<Profile>("PUT", "/api/me/profile", p),
  drillToday: () => request<DrillState>("GET", "/api/drill/today"),
  answerDrill: (choice: number) => request<DrillState>("POST", "/api/drill/today/answer", { choice }),
  tracks: () => request<TrackSummary[]>("GET", "/api/tracks"),
  skills: (track: string) => request<SkillMap>("GET", `/api/tracks/${q(track)}/skills`),
  onboarding: () => request<Onboarding>("GET", "/api/onboarding"),
  finishOnboarding: (goal: string, answers: number[]) => request<OnboardingResult>("POST", "/api/onboarding", { goal, answers }),
  skipOnboarding: () => request<Stats>("POST", "/api/onboarding/skip"),

  check: (labId: string, chapterId: string) => request<CheckResponse>("POST", `/api/labs/${q(labId)}/check`, { chapter_id: chapterId }),
};

export function terminalUrl(labId: string): string {
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}/ws/terminal/${q(labId)}?token=${q(getToken() ?? "")}`;
}
