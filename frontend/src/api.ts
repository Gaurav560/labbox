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
  if (res.status === 401 && !path.startsWith("/api/auth/")) {
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
export interface LabSummary { id: string; title: string; description: string; language: string; chapter_count: number; progress: Progress }
export interface Task { id: string; title: string; passed: boolean | null }
export interface Chapter { id: string; title: string; tasks: Task[] }
export interface LabDetail { id: string; title: string; description: string; language: string; chapters: Chapter[]; progress: Progress }
export interface ChapterContent { id: string; title: string; markdown: string }
export type MachineStatus = "running" | "stopped" | "missing";
export interface WorkspaceStatus { status: MachineStatus; container?: string }
export interface FileNode { path: string; name: string; type: "file" | "dir"; children?: FileNode[] }
export interface TaskResult { task: string; title: string; passed: boolean; message: string }
export interface CheckResponse { passed_count: number; total_count: number; results: TaskResult[]; output: string; duration_ms: number }

// ---------- calls ----------

export const api = {
  signup: (username: string, password: string) => request<AuthResponse>("POST", "/api/auth/signup", { username, password }),
  login: (username: string, password: string) => request<AuthResponse>("POST", "/api/auth/login", { username, password }),
  me: () => request<User>("GET", "/api/me"),

  labs: () => request<LabSummary[]>("GET", "/api/labs"),
  lab: (labId: string) => request<LabDetail>("GET", `/api/labs/${q(labId)}`),
  chapter: (labId: string, chapterId: string) => request<ChapterContent>("GET", `/api/labs/${q(labId)}/chapters/${q(chapterId)}`),

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

  check: (labId: string, chapterId: string) => request<CheckResponse>("POST", `/api/labs/${q(labId)}/check`, { chapter_id: chapterId }),
};

export function terminalUrl(labId: string): string {
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}/ws/terminal/${q(labId)}?token=${q(getToken() ?? "")}`;
}
