# LabBox POC: Build Spec for Claude Code

> **How to use this file:** Put this file in an empty folder, open the folder in VS Code, start Claude Code, and say:
> "Read `labbox-poc-spec.md` and build the project phase by phase. Finish each phase's acceptance checks before starting the next one. Ask me before doing anything on AWS."

---

## 0. What we are building

A small copy of a "hands-on coding labs" platform (like ChaiCode Labs):

- A user logs in and sees a list of **labs** (for example "Python Basics", "Java Basics").
- Opening a lab gives the user **their own Docker container**, made from that lab's image.
- The page has:
  - **Chapter text and task list** on the left
  - **File tree + code editor (Monaco)** in the middle
  - **A real Linux terminal (xterm.js)** at the bottom, connected to the user's container
  - A **Check** button that runs **hidden tests** in a **fresh, throwaway container** and shows pass or fail per task
- The user's files are saved and are still there when they come back.
- Containers that sit idle get stopped automatically and start again when the user comes back.

**Key rule:** one container per **user + lab**. User 42 in "python-basics" gets `lab-u42-python-basics`. The same user in "java-basics" gets a different container with different files.

### Non-goals (do NOT build these in the POC)

- Payments, certificates, leaderboards, streaks
- Multiple servers / Kubernetes (single EC2 host only)
- Real OAuth (a simple username + password login with JWT is enough)
- AI tutor or AI autocomplete (listed as stretch goals at the end)

---

## 1. Tech stack (fixed, do not swap)

| Part | Choice |
|---|---|
| Backend | Python 3.12, **FastAPI**, Uvicorn |
| Docker control | **docker** (docker-py) Python SDK |
| Database | **SQLite** via **SQLModel** (file: `backend/data/labbox.db`) |
| Auth | Username + password (bcrypt via `passlib[bcrypt]`), **JWT** via `python-jose` |
| Config | `pydantic-settings`, values from `.env` |
| Lab definitions | YAML files (`PyYAML`) |
| Frontend | **React 18 + Vite + TypeScript** |
| Editor | `@monaco-editor/react` |
| Terminal | `@xterm/xterm` + `@xterm/addon-fit` |
| Markdown | `react-markdown` |
| Routing | `react-router-dom` |
| Styling | Plain CSS modules or one global CSS file. No UI framework needed. |
| Production | Ubuntu 24.04 on **AWS EC2**, Nginx reverse proxy, systemd service, optional gVisor |

---

## 2. Folder structure

Create exactly this layout:

```
labbox-poc/
├── README.md
├── .gitignore
├── backend/
│   ├── pyproject.toml            # or requirements.txt, your choice, but pin versions
│   ├── .env.example
│   ├── app/
│   │   ├── main.py               # FastAPI app, routers, startup/shutdown, CORS
│   │   ├── config.py             # Settings (pydantic-settings)
│   │   ├── db.py                 # SQLModel engine + session dependency
│   │   ├── models.py             # User, Workspace, CheckRun tables
│   │   ├── auth.py               # hashing, JWT create/verify, get_current_user
│   │   ├── labs.py               # load + validate lab.yaml files into LabConfig objects
│   │   ├── containers.py         # ALL docker logic: ensure, start, stop, exec, check
│   │   ├── workspace_files.py    # safe file list/read/write/create/delete/rename
│   │   ├── terminal.py           # WebSocket <-> docker exec bridge
│   │   ├── checker.py            # runs hidden tests in throwaway container, parses results
│   │   ├── reaper.py             # background task: stop idle containers
│   │   └── routers/
│   │       ├── auth_routes.py
│   │       ├── lab_routes.py
│   │       ├── file_routes.py
│   │       ├── check_routes.py
│   │       └── terminal_routes.py
│   ├── tests/
│   │   ├── test_paths.py         # path traversal tests (no docker needed)
│   │   ├── test_labs.py          # lab.yaml loading tests
│   │   └── test_e2e_docker.py    # marked @pytest.mark.docker, needs Docker running
│   └── data/                     # sqlite db lives here (gitignored)
├── labs/
│   ├── python-basics/
│   │   ├── lab.yaml
│   │   ├── Dockerfile
│   │   ├── chapters/
│   │   │   └── 01-functions.md
│   │   ├── starter/              # copied into a NEW user's workspace once
│   │   │   ├── greet.py
│   │   │   └── math_utils.py
│   │   └── tests/                # HIDDEN, never copied into the user's workspace
│   │       ├── run_checks.sh
│   │       └── test_chapter1.py
│   └── java-basics/
│       ├── lab.yaml
│       ├── Dockerfile
│       ├── chapters/
│       │   └── 01-methods.md
│       ├── starter/
│       │   └── Greeter.java
│       └── tests/
│           ├── run_checks.sh
│           └── CheckGreeter.java
├── scripts/
│   ├── build_lab_images.sh       # docker build every labs/*/Dockerfile
│   └── create_user.py            # CLI: create a user (for testing)
├── deploy/
│   ├── nginx.conf
│   ├── labbox.service            # systemd unit for the backend
│   └── ec2_setup.sh              # installs docker, gvisor, python, node, nginx on Ubuntu
└── frontend/
    ├── package.json
    ├── vite.config.ts            # dev proxy: /api and /ws -> http://localhost:8000
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api.ts                # fetch wrapper that adds the JWT
        ├── auth.tsx              # auth context, token in localStorage
        ├── pages/
        │   ├── LoginPage.tsx
        │   ├── LabsPage.tsx
        │   └── LabPage.tsx
        ├── components/
        │   ├── ChapterPanel.tsx
        │   ├── TaskList.tsx
        │   ├── FileTree.tsx
        │   ├── EditorPane.tsx
        │   ├── TerminalPane.tsx
        │   ├── CheckResults.tsx
        │   └── StatusBar.tsx
        └── styles.css
```

---

## 3. Lab format

Every lab is a folder in `labs/`. The backend reads all of them at startup.

### 3.1 `lab.yaml` schema

```yaml
id: python-basics                  # must equal folder name, lowercase, a-z 0-9 and dashes
title: Python Basics
description: Write your first Python functions and see real tests pass.
language: python
image: labbox/python-basics:v1     # built from this folder's Dockerfile
resources:
  cpus: 0.5                        # -> nano_cpus = 0.5 * 1e9
  memory: 512m
  pids_limit: 256
workspace:
  mount_path: /workspace           # where the user's files appear inside the container
  shell: /bin/bash
  network: bridge                  # "bridge" (internet allowed, for pip install) or "none"
check:
  command: ["bash", "/check/tests/run_checks.sh"]
  timeout_seconds: 30
  network: none                    # checks ALWAYS run with no network
chapters:
  - id: 01-functions
    title: Your first functions
    file: chapters/01-functions.md
    tasks:
      - id: greet
        title: "greet.py: return a greeting"
      - id: add
        title: "math_utils.py: add two numbers"
      - id: is_even
        title: "math_utils.py: check if a number is even"
```

Backend must validate this with a Pydantic model and fail loudly at startup if a lab is invalid (missing image, bad id, task ids duplicated, chapter file missing).

### 3.2 Check result protocol (same for every language)

The lab's `run_checks.sh` must print one line per task to stdout, in this exact format:

```
@@RESULT {"task": "greet", "passed": true, "message": "ok"}
@@RESULT {"task": "add", "passed": false, "message": "add(2, 3) returned 6, expected 5"}
```

- The backend ignores every line that does not start with `@@RESULT `.
- Any task id listed in `lab.yaml` that has no result line counts as **failed** with message `"No result reported (did your code crash?)"`.
- The backend also keeps the last 4000 characters of raw stdout+stderr to show as "Output" in the UI (useful when code crashes).
- Messages must describe what went wrong, never print the expected solution code.

### 3.3 Lab 1: `python-basics`

**Dockerfile**

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends bash git nano less procps \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pytest==8.3.3
RUN useradd -m -u 1000 -s /bin/bash learner
USER learner
WORKDIR /workspace
ENV PS1="\[\e[32m\]learner\[\e[0m\]:\[\e[34m\]\w\[\e[0m\]$ "
CMD ["sleep", "infinity"]
```

**starter/greet.py**

```python
def greet(name: str) -> str:
    # TODO: return "Hello, <name>!"  e.g. greet("Asha") -> "Hello, Asha!"
    pass
```

**starter/math_utils.py**

```python
def add(a: int, b: int) -> int:
    # TODO: return the sum of a and b
    pass


def is_even(n: int) -> bool:
    # TODO: return True if n is even, otherwise False
    pass
```

**tests/test_chapter1.py**: plain pytest tests, grouped so each task can be reported. Simplest approach: do NOT rely on pytest output parsing. Instead write `tests/check.py` that imports the user's modules from `/check/workspace`, runs assertions per task inside try/except, and prints `@@RESULT` lines. Then `run_checks.sh` is:

```bash
#!/usr/bin/env bash
cd /check/workspace
python /check/tests/check.py
```

(Rename `test_chapter1.py` to `check.py` in the folder layout if you take this approach. Keep it simple and robust: one try/except block per task, catch import errors too, so a syntax error in one file does not hide results for the other file.)

**chapters/01-functions.md**: a short friendly lesson (around 200 words) explaining functions, `return`, and how to run `python3 -c "from greet import greet; print(greet('Asha'))"` in the terminal, plus the 3 tasks.

### 3.4 Lab 2: `java-basics`

**Dockerfile**

```dockerfile
FROM eclipse-temurin:21-jdk
RUN apt-get update && apt-get install -y --no-install-recommends bash nano less procps \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 -s /bin/bash learner || true
USER 1000
WORKDIR /workspace
CMD ["sleep", "infinity"]
```

(Note: the temurin image may already have a user with uid 1000 named `ubuntu`. Handle it: if `useradd` fails, just use uid 1000. The important thing is that the container runs as uid 1000, not root.)

**starter/Greeter.java**

```java
public class Greeter {
    // TODO: return "Hello, <name>!"
    public static String greet(String name) {
        return null;
    }

    // TODO: return the length of the longest word in the sentence (words split by spaces)
    public static int longestWord(String sentence) {
        return 0;
    }

    public static void main(String[] args) {
        System.out.println(greet("Asha"));
    }
}
```

**tests/CheckGreeter.java**: a class with `main` that calls `Greeter.greet` and `Greeter.longestWord` in try/catch per task and prints `@@RESULT` JSON lines (build the JSON by hand with proper escaping of quotes in messages).

**tests/run_checks.sh**

```bash
#!/usr/bin/env bash
set -u
mkdir -p /tmp/build
if ! javac -d /tmp/build /check/workspace/*.java 2>/tmp/javac.err; then
  echo "Compile error:"; cat /tmp/javac.err
  # Report every task as failed with a compile message
  for t in greet longest_word; do
    echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"Your code does not compile. See Output.\"}"
  done
  exit 0
fi
javac -cp /tmp/build -d /tmp/build /check/tests/CheckGreeter.java
java -cp /tmp/build CheckGreeter
```

Tasks in `lab.yaml`: `greet`, `longest_word`.

---

## 4. Data model (SQLite via SQLModel)

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime

class Workspace(SQLModel, table=True):
    # one row per (user, lab)
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str = Field(index=True)
    container_name: str = Field(unique=True)   # lab-u{user_id}-{lab_id}
    volume_path: str                           # host path
    seeded: bool = False                       # starter files copied?
    last_active_at: datetime
    created_at: datetime
    # unique constraint on (user_id, lab_id)

class CheckRun(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str
    chapter_id: str
    passed_count: int
    total_count: int
    results_json: str      # list of {task, passed, message}
    output_tail: str
    duration_ms: int
    created_at: datetime
```

---

## 5. Config (`backend/.env.example`)

```
JWT_SECRET=change-me-to-a-long-random-string
JWT_EXPIRE_MINUTES=720
LABS_DIR=../labs
VOLUMES_DIR=/srv/labbox/volumes          # on Mac/Windows dev, use a folder Docker Desktop can share, e.g. ~/labbox-volumes
DATABASE_URL=sqlite:///./data/labbox.db
CONTAINER_RUNTIME=                       # empty = default runc; set "runsc" on EC2 once gVisor is installed
IDLE_STOP_MINUTES=15
REAPER_INTERVAL_SECONDS=60
MAX_FILE_BYTES=1000000
CORS_ORIGINS=http://localhost:5173
ALLOW_SIGNUP=true
```

---

## 6. Container logic (`containers.py`)

Use `docker.from_env()` once (module-level singleton). Every container we create gets labels so we can find them:

```
labels = {
  "labbox": "true",
  "labbox.kind": "workspace" | "check",
  "labbox.user": str(user_id),
  "labbox.lab": lab_id,
}
```

### 6.1 `ensure_workspace(user, lab) -> container`

1. Get or create the `Workspace` row.
2. Host folder: `{VOLUMES_DIR}/u{user_id}/{lab_id}`. Create it if missing. `chown` to uid 1000, gid 1000 (on Linux) so the `learner` user inside can write.
3. If `seeded` is False: copy everything from `labs/{lab_id}/starter/` into the folder, chown, set `seeded=True`. **Never** copy `tests/`.
4. Look up the container by name.
   - Not found: create it.
   - Found but stopped: start it.
   - Found and running: do nothing.
5. Update `last_active_at = now`.

### 6.2 Container create options (security matters, do all of these)

```python
client.containers.run(
    image=lab.image,
    name=container_name,
    detach=True,
    labels=labels,
    hostname=lab.id,
    user="1000:1000",
    working_dir=lab.workspace.mount_path,
    volumes={host_path: {"bind": lab.workspace.mount_path, "mode": "rw"}},
    nano_cpus=int(lab.resources.cpus * 1e9),
    mem_limit=lab.resources.memory,
    memswap_limit=lab.resources.memory,     # no swap
    pids_limit=lab.resources.pids_limit,    # stops fork bombs
    cap_drop=["ALL"],
    security_opt=["no-new-privileges:true"],
    network_mode=lab.workspace.network,     # "bridge" or "none"
    runtime=settings.CONTAINER_RUNTIME or None,
    tty=True,
    stdin_open=True,
    command=["sleep", "infinity"],
    environment={"HOME": "/home/learner", "TERM": "xterm-256color"},
)
```

Never use `privileged=True`. Never mount `/var/run/docker.sock` into a user container.

### 6.3 Other functions

- `stop_workspace(container_name)`: `container.stop(timeout=5)`.
- `container_status(container_name) -> "running" | "stopped" | "missing"`.
- `touch(workspace)`: update `last_active_at` (call on every file API call, every terminal message batch, every check).

All docker-py calls are blocking. In async route handlers, wrap them with `await asyncio.to_thread(...)` (or `run_in_threadpool`) so the event loop is not blocked.

---

## 7. Safe file API (`workspace_files.py`)

All paths from the browser are **relative** to the workspace root. Implement one helper and use it everywhere:

```python
def safe_path(root: Path, rel: str) -> Path:
    root = root.resolve()
    target = (root / rel).resolve()
    if target != root and root not in target.parents:
        raise HTTPException(403, "Path outside workspace")
    return target
```

Rules:
- Reject absolute paths, `..` escapes, and symlinks that point outside the root (the `.resolve()` check handles symlinks).
- Max file size `MAX_FILE_BYTES` for read and write.
- Skip these in the file tree listing: `__pycache__`, `.git`, `node_modules`, `.venv`, `*.class`, files larger than 1 MB.
- Read as UTF-8; if decoding fails return 415 "Binary file, cannot open in editor".
- After writing, chown to 1000:1000 (Linux).
- Writing files from the backend goes straight to the host volume folder. The container sees the change instantly because it is the same folder. Do not use `docker exec` or `docker cp` for the editor.

**Tests (`tests/test_paths.py`) must cover:** `../x`, `a/../../x`, `/etc/passwd`, a symlink inside the workspace pointing to `/etc`, normal nested paths, and the root itself.

---

## 8. REST API

All routes except `/api/auth/*` and `/api/health` require `Authorization: Bearer <jwt>`.

| Method | Path | Body / Query | Response |
|---|---|---|---|
| GET | `/api/health` | | `{"ok": true, "docker": true}` |
| POST | `/api/auth/signup` | `{username, password}` | `{token, user: {id, username}}` (only if `ALLOW_SIGNUP`) |
| POST | `/api/auth/login` | `{username, password}` | `{token, user}` |
| GET | `/api/me` | | `{id, username}` |
| GET | `/api/labs` | | list of `{id, title, description, language, chapter_count, progress: {passed_tasks, total_tasks}}` |
| GET | `/api/labs/{lab_id}` | | full lab info: chapters with tasks, plus each task's latest pass state for this user |
| GET | `/api/labs/{lab_id}/chapters/{chapter_id}` | | `{id, title, markdown}` |
| POST | `/api/labs/{lab_id}/workspace/start` | | `{status: "running", container: "lab-u1-python-basics"}`; calls `ensure_workspace` |
| POST | `/api/labs/{lab_id}/workspace/stop` | | `{status: "stopped"}` |
| POST | `/api/labs/{lab_id}/workspace/reset` | | wipes the folder, re-seeds starter files, recreates container. Frontend must confirm first. |
| GET | `/api/labs/{lab_id}/workspace/status` | | `{status}` |
| GET | `/api/labs/{lab_id}/files` | | tree: `[{path, name, type: "file"|"dir", children?}]` |
| GET | `/api/labs/{lab_id}/files/content?path=greet.py` | | `{path, content}` |
| PUT | `/api/labs/{lab_id}/files/content` | `{path, content}` | `{saved: true, bytes}` |
| POST | `/api/labs/{lab_id}/files/new` | `{path, type: "file"|"dir"}` | `{created: true}` |
| POST | `/api/labs/{lab_id}/files/rename` | `{from, to}` | `{renamed: true}` |
| DELETE | `/api/labs/{lab_id}/files?path=...` | | `{deleted: true}` |
| POST | `/api/labs/{lab_id}/check` | `{chapter_id}` | `{passed_count, total_count, results: [{task, title, passed, message}], output, duration_ms}` |
| GET | `/api/labs/{lab_id}/checks?limit=10` | | recent check runs |

Return clear JSON errors: `{"detail": "..."}` with proper status codes (400, 401, 403, 404, 409, 413, 415, 429, 500).

Rate limit Check to **1 run per user at a time** (return 429 "A check is already running") using an in-memory `set` of user ids plus an `asyncio.Lock`.

---

## 9. Terminal over WebSocket (`terminal.py`): the trickiest part

### 9.1 Protocol

- URL: `ws(s)://<host>/ws/terminal/{lab_id}?token=<jwt>` (browsers cannot set headers on WebSocket, so the token goes in the query string).
- **Browser to server** (text frames, JSON):
  - `{"type": "input", "data": "ls\r"}`
  - `{"type": "resize", "cols": 120, "rows": 30}`
  - `{"type": "ping"}`
- **Server to browser**:
  - **binary frames**: raw terminal output bytes (write straight into xterm)
  - text frames (JSON) for control: `{"type": "status", "message": "connected"}`, `{"type": "exit"}`, `{"type": "error", "message": "..."}`

### 9.2 Flow

1. Verify JWT from query. If invalid, close with code 4401.
2. `await to_thread(ensure_workspace, user, lab)` so the container is running.
3. Create exec with TTY:
   ```python
   exec_id = client.api.exec_create(
       container_name, cmd=[lab.workspace.shell, "-l"],
       stdin=True, stdout=True, stderr=True, tty=True,
       user="1000:1000", workdir=lab.workspace.mount_path,
       environment={"TERM": "xterm-256color"},
   )["Id"]
   sock = client.api.exec_start(exec_id, tty=True, socket=True)
   raw = sock._sock   # the real socket object (docker-py wraps it)
   raw.setblocking(True)
   ```
4. Run two tasks concurrently with `asyncio.gather` / `TaskGroup`:
   - **container to browser**: loop `data = await asyncio.to_thread(raw.recv, 4096)`; if empty bytes, the shell exited, send `{"type":"exit"}` and break; else `await ws.send_bytes(data)`.
   - **browser to container**: loop `msg = await ws.receive_text()`; parse JSON; on `input` call `await asyncio.to_thread(raw.sendall, data.encode())`; on `resize` call `client.api.exec_resize(exec_id, height=rows, width=cols)`; call `touch(workspace)` at most once every 30 seconds.
5. When either side ends (WebSocket disconnect or shell exit), cancel the other task, close the socket, close the WebSocket. Do not leave threads stuck: closing `raw` makes the blocked `recv` return.
6. A user can open the terminal again; each connection is a new `bash` exec in the same container. Files and installed packages persist because the container keeps running.

### 9.3 Must work

- Colors, prompt, arrow keys, tab completion, Ctrl+C, `nano`, `python3` REPL, `top`.
- Resizing the browser window resizes the terminal (fit addon + resize message).
- Closing the tab does not kill the container.

---

## 10. Checker (`checker.py`)

The point: grade the user's code on a **clean machine** they cannot see or tamper with.

1. Create a temp dir on the host, e.g. `/srv/labbox/checks/{uuid}/` with:
   - `workspace/`: a **copy** of the user's workspace folder (`shutil.copytree`, skip ignored folders, cap total size at 20 MB).
   - `tests/`: a copy of `labs/{lab_id}/tests/`.
   - chown both to 1000:1000.
2. Run a **new** container from the same lab image:
   ```python
   c = client.containers.run(
       image=lab.image,
       name=f"check-u{user_id}-{lab_id}-{short_uuid}",
       command=lab.check.command,
       detach=True,
       labels={..., "labbox.kind": "check"},
       user="1000:1000",
       working_dir="/check/workspace",
       volumes={
           tmp/"workspace": {"bind": "/check/workspace", "mode": "rw"},
           tmp/"tests":     {"bind": "/check/tests", "mode": "ro"},
       },
       network_mode="none",
       nano_cpus=..., mem_limit=..., pids_limit=128,
       cap_drop=["ALL"], security_opt=["no-new-privileges:true"],
       runtime=settings.CONTAINER_RUNTIME or None,
   )
   ```
3. `c.wait(timeout=lab.check.timeout_seconds)`. On timeout: `c.kill()` and mark every task failed with "Timed out after N seconds (infinite loop?)".
4. `logs = c.logs(stdout=True, stderr=True).decode(errors="replace")`.
5. **Always** `c.remove(force=True)` and delete the temp dir (use `try/finally`).
6. Parse `@@RESULT` lines, map to the chapter's task list, fill missing tasks as failed, save a `CheckRun` row, return the response.

Target: a Check finishes in under 5 seconds for these simple labs.

---

## 11. Idle reaper (`reaper.py`)

- Started in FastAPI's `lifespan` as an `asyncio.create_task`.
- Every `REAPER_INTERVAL_SECONDS`: for each `Workspace` with `last_active_at` older than `IDLE_STOP_MINUTES` whose container is running, stop it. Log what it stopped.
- Also remove any container labelled `labbox.kind=check` older than 5 minutes (leftovers from crashes).
- On next open, `ensure_workspace` simply starts it again. Files are safe because they live on the host volume.

---

## 12. Frontend

### 12.1 Pages

**LoginPage** (`/login`): username + password, Login and Sign up buttons. Store JWT in `localStorage`. Redirect to `/labs`.

**LabsPage** (`/labs`): cards for each lab: title, language badge, description, progress bar (`passed_tasks / total_tasks`), "Open" button.

**LabPage** (`/labs/:labId`): the main screen. Layout:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ← Labs   Python Basics · Chapter 1  [chapter dropdown]   ● Running  user │  top bar
├──────────────┬───────────────────────────────────────────────────────────┤
│ Chapter text │ Files │ [greet.py ×] [math_utils.py ×]          Saved ✓   │
│ (markdown)   │ tree  │                                                    │
│              │       │          Monaco editor                             │
│ Your tasks   │       │                                                    │
│ ✓ greet      │       │                                                    │
│ ✗ add        ├───────┴────────────────────────────────────────────────────┤
│ ○ is_even    │ Terminal (xterm.js)                                         │
│              │ learner:/workspace$ python3 greet.py                        │
│ [ Check ]    │                                                             │
├──────────────┴─────────────────────────────────────────────────────────────┤
│ Check results: 2 of 3 pass · 1.4 s   [Output ▾]                             │
└────────────────────────────────────────────────────────────────────────────┘
```

Panels should be resizable with simple drag handles (a small custom splitter is fine, or `react-resizable-panels`).

### 12.2 Behaviour

- On LabPage mount: call `POST /workspace/start`, show "Starting your machine..." spinner until it returns, then load file tree and connect terminal.
- **Editor**: open files in tabs. Language from extension (`.py` python, `.java` java, `.js` javascript, `.ts` typescript, `.md` markdown, `.sh` shell, `.json` json, `.yaml` yaml). **Autosave** 800 ms after the user stops typing, plus Ctrl+S / Cmd+S saves immediately. Status shows "Saving..." then "Saved". Unsaved tabs show a dot.
- **File tree**: expand/collapse folders, right-click or small buttons for New file, New folder, Rename, Delete (confirm). A Refresh button (files created in the terminal will not show until refresh; optionally poll the tree every 5 s while the tab is visible).
- **Terminal**: xterm with fit addon, dark theme, font "JetBrains Mono, Menlo, monospace" 14px. On open send a resize message. On window resize, refit and send resize. On socket close, show "Disconnected. [Reconnect]". Auto-reconnect once after 2 s.
- **Check button**: saves all dirty tabs first, then calls `POST /check`. Disable while running, show spinner. Results panel shows each task with ✓ / ✗ and the message, plus collapsible raw Output. Task list on the left updates its icons.
- **Top bar** status dot: green Running, grey Stopped, yellow Starting. Buttons: "Stop machine", "Reset lab" (confirm dialog: "This deletes your files for this lab").
- Any 401 from the API: clear token, redirect to login.

### 12.3 Vite dev proxy (`vite.config.ts`)

```ts
server: {
  proxy: {
    "/api": "http://localhost:8000",
    "/ws": { target: "ws://localhost:8000", ws: true },
  },
},
```

The frontend must build the WebSocket URL from `window.location` (`wss:` when the page is `https:`), so the same code works in dev and on EC2.

---

## 13. Security checklist (must all be true before AWS)

- [ ] User containers run as uid 1000, never root
- [ ] `cap_drop=["ALL"]`, `no-new-privileges`, `pids_limit`, `mem_limit`, `nano_cpus` on every container
- [ ] No `privileged`, no Docker socket mounted into any user container
- [ ] Check containers have `network_mode="none"` and the tests folder mounted read-only
- [ ] Hidden `tests/` never copied into a user's workspace and never served by any API route
- [ ] File API blocks path traversal and symlink escape (unit tests pass)
- [ ] User A cannot touch user B's workspace: every route derives `user_id` from the JWT only, never from the request body or URL
- [ ] WebSocket requires a valid JWT
- [ ] `JWT_SECRET` comes from `.env`, not hard-coded
- [ ] On EC2: `CONTAINER_RUNTIME=runsc` (gVisor) enabled and tested
- [ ] On EC2: block containers from reaching the EC2 metadata service (`169.254.169.254`). Add an iptables rule in `ec2_setup.sh`: `iptables -I DOCKER-USER -d 169.254.169.254 -j DROP`, and make it persistent (`iptables-persistent`). Without this, user code could read the instance's IAM credentials.

---

## 14. Build phases (do them in order)

Claude Code: finish each phase, run its acceptance checks, show me the result, then continue.

### Phase 1: Labs and images
- Create `labs/python-basics` and `labs/java-basics` fully (Dockerfiles, starter, hidden tests, chapters, lab.yaml).
- `scripts/build_lab_images.sh` builds all images.
- **Accept:** both images build. Manually prove the check script works:
  `docker run --rm -v $PWD/labs/python-basics/starter:/check/workspace -v $PWD/labs/python-basics/tests:/check/tests:ro labbox/python-basics:v1 bash /check/tests/run_checks.sh`
  prints 3 `@@RESULT` lines, all failed. Then with a solved copy, all pass. Same for Java.

### Phase 2: Backend skeleton
- FastAPI app, config, SQLite models, signup/login/JWT, `/api/health`, `/api/labs`, lab.yaml loader with validation.
- `tests/test_labs.py`, `tests/test_paths.py`.
- **Accept:** `pytest -m "not docker"` passes; `curl /api/health` works; signup then `GET /api/labs` with token returns both labs.

### Phase 3: Workspaces and files
- `containers.py` ensure/start/stop/reset, `workspace_files.py`, file routes.
- **Accept:** `POST /workspace/start` creates `lab-u1-python-basics` (verify with `docker ps`); the file tree lists `greet.py` and `math_utils.py`; editing via PUT and then `docker exec lab-u1-python-basics cat /workspace/greet.py` shows the new content; traversal requests return 403.

### Phase 4: Checker
- `checker.py`, check routes, CheckRun saving, one-at-a-time lock.
- **Accept:** check on starter code returns 0 of 3; after writing correct code via the file API returns 3 of 3; an infinite loop (`while True: pass`) returns timed out and leaves no container behind (`docker ps -a --filter label=labbox.kind=check` is empty).

### Phase 5: Terminal
- WebSocket bridge.
- **Accept:** a small Python test client (`websockets` lib) connects, sends `echo hello\r`, receives `hello`. Resize message does not error.

### Phase 6: Frontend
- All pages and components from section 12.
- **Accept (manual):** sign up, open Python Basics, edit `greet.py`, run it in the terminal, press Check, see results, refresh the page, files are still there; open Java Basics, `javac Greeter.java && java Greeter` works in the terminal.

### Phase 7: Reaper and polish
- Reaper task, status dot, reset lab, error toasts, README.
- **Accept:** set `IDLE_STOP_MINUTES=1`, wait, container stops; reopening the lab starts it again with files intact.

### Phase 8: Local end-to-end test file
- `tests/test_e2e_docker.py` (marked `docker`) covering: signup, start workspace, write file, check pass, check fail, traversal 403, terminal echo.
- **Accept:** `pytest -m docker` passes with Docker running.

### Phase 9: AWS deploy (ask me before running anything against AWS)
See section 15.

---

## 15. AWS deployment (single EC2 host)

### 15.1 Launch the instance (I will do this in the AWS console, give me exact steps)

- Region: `ap-south-1` (Mumbai)
- AMI: Ubuntu Server 24.04 LTS (x86_64)
- Type: `t3.large` (2 vCPU, 8 GB) is enough for the POC; `m6i.xlarge` for ~30 to 50 concurrent users
- Storage: 40 GB gp3
- Security group inbound: 22 from **my IP only**, 80 and 443 from anywhere
- Key pair: create one, download `.pem`
- Elastic IP: allocate and attach (so the IP does not change)
- **No IAM role** on the instance (so there are no credentials to steal anyway)

### 15.2 `deploy/ec2_setup.sh` (idempotent, run with sudo)

Must:
1. `apt update && apt upgrade -y`
2. Install Docker Engine from Docker's official apt repo; add `ubuntu` user to `docker` group.
3. Install **gVisor** (`runsc`) from the official gVisor apt repo, run `runsc install`, restart Docker. Verify: `docker run --rm --runtime=runsc hello-world`.
4. Install Python 3.12 + venv, Node 20 (NodeSource), Nginx, `iptables-persistent`.
5. Add the metadata-blocking iptables rule from section 13 and save it.
6. Create `/srv/labbox/{volumes,checks}` owned by `ubuntu`; volumes subfolders get chowned to 1000 by the app.
7. Print next steps.

### 15.3 App install on EC2 (document in README)

```bash
git clone <repo> /opt/labbox && cd /opt/labbox
bash scripts/build_lab_images.sh
cd backend && python3.12 -m venv .venv && .venv/bin/pip install -e .   # or -r requirements.txt
cp .env.example .env   # set JWT_SECRET, VOLUMES_DIR=/srv/labbox/volumes, CONTAINER_RUNTIME=runsc, CORS_ORIGINS
cd ../frontend && npm ci && npm run build      # output: frontend/dist
sudo cp ../deploy/labbox.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now labbox
sudo cp ../deploy/nginx.conf /etc/nginx/sites-available/labbox && sudo ln -sf /etc/nginx/sites-available/labbox /etc/nginx/sites-enabled/labbox && sudo rm -f /etc/nginx/sites-enabled/default && sudo nginx -t && sudo systemctl reload nginx
```

### 15.4 `deploy/labbox.service`

- Runs `uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1` from `/opt/labbox/backend` as user `ubuntu`, `Restart=always`, `EnvironmentFile=/opt/labbox/backend/.env`.
- **Use 1 worker** in the POC: the check lock and reaper are in-memory.

### 15.5 `deploy/nginx.conf`

- Serve `frontend/dist` as static files with SPA fallback (`try_files $uri /index.html`).
- Proxy `/api/` to `http://127.0.0.1:8000`.
- Proxy `/ws/` to `http://127.0.0.1:8000` **with WebSocket upgrade headers**:
  ```nginx
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_read_timeout 3600s;
  proxy_send_timeout 3600s;
  ```
- `client_max_body_size 2m;`

### 15.6 HTTPS (optional but recommended)

Point a domain/subdomain A record at the Elastic IP, then `sudo apt install certbot python3-certbot-nginx && sudo certbot --nginx -d labs.example.com`. The frontend automatically switches to `wss://`.

### 15.7 Cost control

- Stop the EC2 instance from the console when not testing (you pay only for storage + Elastic IP while stopped).
- Set an AWS Budget alert (for example $20/month) in Billing.

---

## 16. README.md must contain

1. What this is (3 lines) and an architecture diagram (ASCII):
   ```
   Browser (React: Monaco + xterm)
      │  HTTP /api        │  WebSocket /ws/terminal
      ▼                   ▼
   FastAPI backend ── docker-py ──► Docker (+ gVisor)
      │                              ├─ lab-u1-python-basics  (/workspace = host volume)
      │                              ├─ lab-u2-java-basics
      │                              └─ check-u1-...          (temporary, no network)
      └─ SQLite (users, workspaces, check runs)
   ```
2. Local dev prerequisites: Docker Desktop (Mac/Windows) or Docker Engine (Linux), Python 3.12, Node 20. **Windows note:** run the backend inside WSL2 so host volume paths and chown work.
3. Local run: build images, start backend (`uvicorn app.main:app --reload`), start frontend (`npm run dev`), open `http://localhost:5173`.
4. How to add a new lab (copy a folder, edit lab.yaml, write `run_checks.sh` that prints `@@RESULT` lines, build image, restart backend).
5. AWS deploy steps (section 15).
6. Known POC limits: single host, in-memory locks, no per-user disk quota, SQLite.

---

## 17. Coding standards

- Type hints everywhere in Python; Pydantic models for every request and response body.
- No business logic in routers; routers call `containers.py`, `checker.py`, `workspace_files.py`.
- Log with the `logging` module (container create/start/stop, checks with duration, reaper actions).
- Frontend: TypeScript strict mode, small components, one `api.ts` for all calls.
- Pin all dependency versions.
- Do not use em dashes in any text, comments, docs or UI copy.

---

## 18. Stretch goals (only after everything above works)

1. **Warm pool:** keep 2 pre-started containers per popular lab image; on first open, rename/assign one to the user and attach the volume (requires recreate since volumes cannot be added to a running container; alternative is to keep warm containers with an empty `/workspace` and copy starter files in via `put_archive`).
2. **LLM gateway lab:** add an "ai-basics" lab where the container calls `http://gateway:9000/v1` (an OpenAI-compatible proxy in the backend) with a per-user token, so real API keys never enter the container. Rate-limit per user.
3. **Postgres sidecar:** for a SQL lab, start a `postgres:16` container on a per-user Docker network next to the workspace container.
4. **AI hint button:** when a check fails, send the task, the user's file and the failure message to an LLM and show a hint that does not reveal the full solution.
5. **Multi-host:** store `container_name -> host` in Redis and route terminal/file requests to the right host.
