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

export interface User { id: number; username: string; is_admin?: boolean; plan?: "free" | "pro" }
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
/** open: no limit; unlocked: holds a slot; finished: 80% of tasks passed (open for good); locked: course page only. */
export type LabAccess = "open" | "unlocked" | "finished" | "locked";
export interface Slots { limit: number | null; used: number; free: number | null; swap_open: boolean; next_swap: string; labs: Record<string, LabAccess> }
export interface LabSummary extends LabInfo { id: string; title: string; description: string; language: string; chapter_count: number; progress: Progress; access?: LabAccess }
/** The dashboard's first card: continue where the learner left off, or where to start. */
export interface NextStep { kind: "continue" | "start"; lab_id: string; lab_title: string; chapter_id: string; chapter_title: string; chapter_number: number; chapters: number; step: number; steps: number; reason: string | null; track?: string; step_title?: string | null; code?: string[] }
export interface TaskExample { call: string; gives: string; note: string | null }
export interface Task { id: string; title: string; passed: boolean | null; xp: number; hint_count: number; hints_used: number; examples?: TaskExample[] }
export interface Chapter { id: string; title: string; tasks: Task[]; minutes: number | null; part?: string | null; topics?: { title: string; step: number }[]; has_setup: boolean; folder?: string | null }
export interface PreviewPort { name: string; port: number; path: string }
export interface Need { know: string; why: string; lab: string | null; lab_title: string | null; where: string }
export interface BeforeYouStart { summary: string; needs: Need[] }
export interface LabDetail extends LabInfo { before_you_start?: BeforeYouStart | null; preview: PreviewPort[]; services: string[]; check_mode: "fresh" | "live"; id: string; title: string; description: string; language: string; chapters: Chapter[]; progress: Progress; access?: LabAccess }
export type StepType = "story" | "concept" | "example" | "predict" | "try" | "task" | "incident" | "recap" | "deep-dive" | "design" | "history";
// The answer and explanation are not sent with the chapter; they come back once answered correctly.
export interface Predict { question: string; options: { text: string }[] }
export interface XpAward { kind: string; amount: number; label: string }
export interface PredictState { wrong: number[]; solved: boolean; answer: number | null; explain: string | null; xp_awarded?: XpAward[] }
export interface DesignQuestion { id: string; text: string }
export interface DesignCriterion { id: string; score: number; max: number; feedback: string }
export interface DesignQuestionResult { id: string; score: number; max: number; criteria: DesignCriterion[] }
export interface DesignResult { score: number; max: number; questions: DesignQuestionResult[]; xp_awarded?: XpAward[]; created_at: string }
export interface DesignAttempt { answers: Record<string, string>; result: DesignResult }
export interface Step { type: StepType; title: string | null; task: string | null; minutes: number | null; markdown: string; predict: Predict | null; questions?: DesignQuestion[]; file?: string | null; line?: number | null; end_line?: number | null }
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

/** The lines a lesson step talks about, for Read mode (no machine needed). */
export interface StepCode {
  path: string | null;
  first_line: number;
  lines: string[];
  highlight: number[];
}
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
  certificate?: CheckCertificate | null; // set when this check finished the lab (80% of its tasks)
}

// ---------- certificates (owner, 27 November) ----------

export interface Certificate {
  id: string;
  lab_id: string;
  lab_title: string;
  lab_subtitle: string;
  track: string;
  name: string;
  tasks_passed: number;
  tasks_total: number;
  chapters_total: number;
  skills: string[];
  issued_at: string;
  issuer: string;
  hidden: boolean;
  name_corrected: boolean;
  mine: boolean;
}
export interface LabCertificateStatus {
  eligible: boolean;
  tasks_passed: number;
  tasks_total: number;
  tasks_needed: number;
  certificate: Certificate | null;
  saved_name: string | null;
}
export interface CheckCertificate { id: string | null; needs_name: boolean }
/** What the server holds for a certificate id (the QR code's page). */
export interface Verification {
  id: string;
  status: "verified" | "private" | "unknown" | "sample";
  name: string | null;
  lab_id: string | null;
  lab_title: string | null;
  issued_at: string | null;
  tasks_passed: number | null;
  tasks_total: number | null;
  issuer: string;
  checked_at: string;
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
  chapters: { lab_id: string; chapter_id: string; title: string; done: boolean; lab_title?: string; number?: number }[];
  state: NodeState;
}
export interface SkillMap { track: string; title: string; nodes: SkillNode[] }
export interface CatalogLab extends LabInfo { id: string; title: string; chapter_count: number; parts?: string[] }
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
  authOptions: () => request<{ signup: boolean; providers?: string[] }>("GET", "/api/auth/options"),
  /** Google or GitHub sign-in: the one-time code from the callback, swapped once for a login (owner, 27 November). */
  oauthExchange: (code: string) => request<AuthResponse & { new: boolean }>("POST", "/api/auth/oauth/exchange", { code }),
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
  /** The file a chapter is about, or (with step) the file that lesson step talks about. */
  chapterFocus: (labId: string, chapterId: string, ide: boolean, step?: number) =>
    request<{ path: string | null; line: number; end_line: number | null }>("POST", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/focus`, step === undefined ? { ide } : { ide, step }),
  stepCode: (labId: string, chapterId: string, step: number) =>
    request<StepCode>("GET", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/steps/${step}/code`),
  chapterSetup: (labId: string, chapterId: string) =>
    request<SetupResult>("POST", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/setup`),
  previewTicket: (labId: string) => request<{ ports: PreviewPort[] }>("POST", `/api/labs/${q(labId)}/preview/ticket`),
  hint: (labId: string, chapterId: string, taskId: string) =>
    request<HintResponse>("POST", `/api/labs/${q(labId)}/chapters/${q(chapterId)}/tasks/${q(taskId)}/hint`),
  next: (labId?: string) => request<NextStep>("GET", labId ? `/api/me/next?lab=${q(labId)}` : "/api/me/next"),
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
  publicCourse: (labId: string) => request<LabDetail>("GET", `/api/courses/${q(labId)}`), // AI courses only, no login
  stats: () => request<Stats>("GET", "/api/me/stats"),
  saveProfile: (p: Partial<Pick<Profile, "display_name" | "timezone" | "goal">>) => request<Profile>("PUT", "/api/me/profile", p),
  drillToday: () => request<DrillState>("GET", "/api/drill/today"),
  answerDrill: (choice: number) => request<DrillState>("POST", "/api/drill/today/answer", { choice }),
  tracks: () => request<TrackSummary[]>("GET", "/api/tracks"),
  skills: (track: string) => request<SkillMap>("GET", `/api/tracks/${q(track)}/skills`),
  onboarding: () => request<Onboarding>("GET", "/api/onboarding"),
  finishOnboarding: (goal: string, answers: number[]) => request<OnboardingResult>("POST", "/api/onboarding", { goal, answers }),
  skipOnboarding: () => request<Stats>("POST", "/api/onboarding/skip"),

  labCertificate: (labId: string) => request<LabCertificateStatus>("GET", `/api/labs/${q(labId)}/certificate`),
  claimCertificate: (labId: string, name?: string) => request<Certificate>("POST", `/api/labs/${q(labId)}/certificate`, { name: name ?? null }),
  certificates: () => request<Certificate[]>("GET", "/api/certificates"),
  certificate: (id: string) => request<Certificate>("GET", `/api/certificates/${q(id)}`),
  verifyCertificate: (id: string) => request<Verification>("GET", `/api/verify/${q(id)}`),
  changeCertificate: (id: string, body: { name?: string; hidden?: boolean }) => request<Certificate>("PATCH", `/api/certificates/${q(id)}`, body),
  check: (labId: string, chapterId: string) => request<CheckResponse>("POST", `/api/labs/${q(labId)}/check`, { chapter_id: chapterId }),

  slots: () => request<Slots>("GET", "/api/slots"),
  unlock: (labId: string) => request<Slots>("POST", `/api/labs/${q(labId)}/unlock`),
  swap: (labId: string) => request<Slots>("POST", `/api/labs/${q(labId)}/swap`),
};

// ---------- admin (Phase J) ----------

export type AdminWindow = "7d" | "30d" | "90d" | "all";
export interface FunnelStep { key: string; label: string; count: number; of_previous: number | null; of_first: number | null }
export interface AdminLabRow { id: string; title: string; learners: number; chapters_completed: number; pass_rate: number | null; most_confusing_task: string | null }
export interface AdminStep { index: number; title: string; type: string; stopped_here: number; avg_seconds: number | null; views: number }
export interface AdminChapter { id: string; title: string; started: number; completed: number; steps: AdminStep[] }
export interface AdminTask { id: string; title: string; chapter_id: string; attempted: number; passed: number; pass_rate: number | null; failed_checks_per_learner: number; hints_per_learner: number; hint_count: number; confusion: number }
export interface AdminLabReport { id: string; title: string; learners: number; chapters: AdminChapter[]; tasks: AdminTask[] }
export interface AdminLearner { id: number; username: string; joined: string; is_admin: boolean; labs: number; xp: number; checks: number; last_active: string | null; lab_limit?: number | null; plan?: "free" | "pro" }
export interface SpendRow { name: string; requests: number; tokens: number; cost_usd: number }
export interface AdminSpend { days: { day: string; requests: number; tokens: number; cost_usd: number }[]; by_model: SpendRow[]; top_learners: SpendRow[] }
export interface AdminMachine { container: string; user_id: number; username: string; lab_id: string; lab_title: string; started_at: string | null; files_mb: number }
export interface LimitException { id: number; username: string; lab_limit: number }
/** The site's lab limit (null: every lab open) and the learners with their own. */
export interface LabAccessInfo { limit: number | null; exceptions: LimitException[] }
export interface AdminError { at: string; method: string; route: string; status: number; request_id: string; ms: number; error: string }

export const admin = {
  funnel: (w: AdminWindow) => request<FunnelStep[]>("GET", `/api/admin/funnel?window=${w}`),
  labs: () => request<AdminLabRow[]>("GET", "/api/admin/labs"),
  lab: (labId: string) => request<AdminLabReport>("GET", `/api/admin/labs/${q(labId)}`),
  learners: (query: string) => request<AdminLearner[]>("GET", `/api/admin/learners?q=${q(query)}`),
  spend: (days: number) => request<AdminSpend>("GET", `/api/admin/ai-spend?days=${days}`),
  machines: () => request<AdminMachine[]>("GET", "/api/admin/machines"),
  machineAction: (container: string, action: "stop" | "kill") => request<{ ok: boolean }>("POST", `/api/admin/machines/${q(container)}`, { action }),
  errors: () => request<AdminError[]>("GET", "/api/admin/errors"),
  labAccess: () => request<LabAccessInfo>("GET", "/api/admin/lab-access"),
  setLabAccess: (limit: number | null) => request<LabAccessInfo>("PUT", "/api/admin/lab-access", { limit }),
  setLearnerLimit: (userId: number, labLimit: number | null) =>
    request<{ lab_limit: number | null }>("PUT", `/api/admin/learners/${userId}/lab-limit`, { lab_limit: labLimit }),
};

export function terminalUrl(labId: string): string {
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}/ws/terminal/${q(labId)}?token=${q(getToken() ?? "")}`;
}

// ---------- library (owner, 24 November): books, research papers, tech blogs ----------

export type LibraryKind = "book" | "paper" | "blog";
export type LibraryLevel = "" | "beginner" | "intermediate" | "advanced";
export interface LibraryItem {
  id: number; kind: LibraryKind; title: string; authors: string; year: number | null; url: string; note: string; topic: string;
  lab: string; practice: string; level: LibraryLevel; free: boolean; featured: boolean; image: string;
  position: number; updated_at: string;
}
export type LibraryItemIn = Omit<LibraryItem, "id" | "position" | "updated_at" | "image">;
/** A Library picture: stored with LabBox and served by it, never fetched from another site. */
export const libraryImage = (name: string) => `/api/library/images/${encodeURIComponent(name)}`;

export const library = {
  list: () => request<LibraryItem[]>("GET", "/api/library"),
  add: (item: LibraryItemIn) => request<LibraryItem>("POST", "/api/admin/library", item),
  change: (id: number, item: LibraryItemIn) => request<LibraryItem>("PUT", `/api/admin/library/${id}`, item),
  move: (id: number, direction: "up" | "down") => request<LibraryItem[]>("POST", `/api/admin/library/${id}/move`, { direction }),
  remove: (id: number) => request<{ ok: boolean }>("DELETE", `/api/admin/library/${id}`),
  setImage: (id: number, dataUrl: string) => request<LibraryItem>("PUT", `/api/admin/library/${id}/image`, { data: dataUrl }),
  removeImage: (id: number) => request<LibraryItem>("DELETE", `/api/admin/library/${id}/image`),
};

// ---------- Jarvis, the learner's realtime voice assistant (owner, 28 November) ----------
export interface JarvisStatus { enabled: boolean; plan: "free" | "pro"; kind: "pro" | "trial" | "locked"; reason: string; seconds_left: number; trial_used: boolean; mode: JarvisMode; note_seen: boolean; memories: number }
export type JarvisMode = "tap" | "first" | "off";
export interface JarvisCheer { show: boolean; kind: "" | "lab" | "chapter" | "first"; key: string; line: string; link_url: string | null; link_label: string; detail: string }
export interface JarvisSession { session_id: number; client_secret: string; expires_at: number; model: string; kind: "pro" | "trial"; max_seconds: number }
export interface JarvisNudge { nudge: boolean; reason: "" | "fails" | "hints" | "idle"; task_id: string | null; line: string; detail: string }
export interface JarvisWelcome { show: boolean; kind: "" | "new" | "back"; line: string; continue_url: string | null; continue_label: string; detail: string }
export interface JarvisBeat { stop: boolean; reason: string; seconds_left: number; cost_usd: number }
export interface JarvisAdmin {
  today_usd: number; month_usd: number; today_sessions: number; today_minutes: number; trials_today: number; pro_learners: number;
  cost_per_minute_usd: number | null; settings: Record<string, number>;
  recent: { id: number; username: string; kind: string; lab_id: string | null; started_at: string; seconds: number; cost_usd: number }[];
}
export const jarvisApi = {
  status: () => request<JarvisStatus>("GET", "/api/jarvis/status"),
  start: (labId?: string, chapterId?: string, step?: number, reason?: string) =>
    request<JarvisSession>("POST", "/api/jarvis/session", { lab_id: labId ?? null, chapter_id: chapterId ?? null, step: step ?? null, reason: reason || null }),
  nudge: (labId: string, chapterId: string, step: number, idle: number) =>
    request<JarvisNudge>("GET", `/api/jarvis/nudge?lab_id=${encodeURIComponent(labId)}&chapter_id=${encodeURIComponent(chapterId)}&step=${step}&idle=${Math.round(idle)}`),
  welcome: () => request<JarvisWelcome>("GET", "/api/jarvis/welcome"),
  cheer: (labId: string, chapterId: string) =>
    request<JarvisCheer>("GET", `/api/jarvis/cheer?lab_id=${encodeURIComponent(labId)}&chapter_id=${encodeURIComponent(chapterId)}`),
  settings: (s: { mode?: JarvisMode; note_seen?: boolean }) => request<JarvisStatus>("PUT", "/api/jarvis/settings", s),
  forget: () => request<{ forgotten: number }>("DELETE", "/api/jarvis/memory"),
  heartbeat: (id: number, body: { seconds: number; usage: unknown[]; call_id?: string | null; ended?: boolean; summary?: string | null }) =>
    request<JarvisBeat>("POST", `/api/jarvis/session/${id}/heartbeat`, body),
  tool: (id: number, name: string, step?: number) =>
    request<{ output: string }>("POST", `/api/jarvis/session/${id}/tool`, { name, step: step ?? null }),
  admin: () => request<JarvisAdmin>("GET", "/api/admin/jarvis"),
  adminSettings: (s: Record<string, number>) => request<JarvisAdmin>("PUT", "/api/admin/jarvis", s),
  setPlan: (userId: number, plan: "free" | "pro") => request<{ plan: string }>("PUT", `/api/admin/learners/${userId}/plan`, { plan }),
};
