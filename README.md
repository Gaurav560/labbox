# LabBox POC

LabBox is a small "hands-on coding labs" platform. Each user gets their own Docker container per lab,
with a Monaco editor, a real terminal (xterm.js) and a Check button that grades their code with hidden
tests in a fresh, network-less container.

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

- One container per **user + lab**: `lab-u{user_id}-{lab_id}`. Files live on the host in
  `VOLUMES_DIR/u{user_id}/{lab_id}` and are bind-mounted at `/workspace`, so they survive container
  stops, restarts and recreation.
- Idle containers are stopped by a background reaper and started again when the user comes back.
- Check copies the workspace and the lab's hidden `tests/` into a throwaway container
  (`network_mode=none`, tests mounted read-only), runs the lab's check command and parses
  `@@RESULT` lines.

## 1. Local development

### Prerequisites

- **Linux:** Docker Engine. **Mac/Windows:** Docker Desktop.
  **Windows:** run the backend inside WSL2 so host volume paths and `chown` work.
- Python 3.12
- Node 22 (Node 20 also works)
- Your user can run `docker` without sudo.

### Run it

```bash
# 1. Build the lab images (once, and again after changing a lab's Dockerfile)
bash scripts/build_lab_images.sh

# 2. Folders for user files and check runs (Linux; any folder you own works, set it in .env)
sudo mkdir -p /srv/labbox/volumes /srv/labbox/checks && sudo chown -R "$USER" /srv/labbox

# 3. Backend
cd backend
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env            # then set JWT_SECRET to a long random string
.venv/bin/uvicorn app.main:app --reload     # http://localhost:8000

# 4. Frontend (second terminal)
cd frontend
npm ci
npm run dev                     # http://localhost:5173
```

Open http://localhost:5173, sign up, and open a lab. Vite proxies `/api` and `/ws` to the backend.

`scripts/create_user.py <username> [password]` creates a user from the command line (useful when
`ALLOW_SIGNUP=false`).

### Tests

```bash
cd backend
.venv/bin/pytest -m "not docker"   # fast: path safety and lab.yaml validation
.venv/bin/pytest -m docker         # end to end: needs Docker running and the lab images built
```

### Configuration (`backend/.env`)

| Key | Meaning |
|---|---|
| `JWT_SECRET` | Required, at least 16 characters. Never commit it. |
| `JWT_EXPIRE_MINUTES` | Login lifetime (default 720). |
| `LABS_DIR` | Folder with lab definitions (relative paths are relative to `backend/`). |
| `VOLUMES_DIR` | Host folder for user files. |
| `CHECKS_DIR` | Host folder for temporary check copies (default `/srv/labbox/checks`). |
| `DATABASE_URL` | SQLite file (default `backend/data/labbox.db`). |
| `CONTAINER_RUNTIME` | Empty for runc; `runsc` for gVisor. |
| `IDLE_STOP_MINUTES` / `REAPER_INTERVAL_SECONDS` | Idle reaper timing. |
| `MAX_FILE_BYTES` | Max file size for the editor API. |
| `CORS_ORIGINS` | Comma-separated origins. |
| `ALLOW_SIGNUP` | `true` or `false`. |

Keep comments in `.env` on their own lines: systemd's `EnvironmentFile` does not strip inline comments.

## 2. How to add a new lab

1. Copy a lab folder: `cp -r labs/python-basics labs/my-lab`.
2. Edit `labs/my-lab/lab.yaml`:
   - `id` must equal the folder name (lowercase, digits and dashes).
   - Set a new `image` tag, e.g. `labbox/my-lab:v1`.
   - List chapters and tasks. Task ids must be unique within the lab (`a-z`, `0-9`, `_`).
3. Write the `Dockerfile`. The container must work as **uid 1000** and keep running with
   `sleep infinity`. Install everything the checks need: check containers have **no network**.
4. Put starter files in `starter/` (copied once into each new workspace) and chapter text in
   `chapters/*.md`.
5. Put hidden tests in `tests/`. The check command (usually `bash /check/tests/run_checks.sh`) runs
   with the user's files copied to `/check/workspace` (the working dir) and `tests/` mounted read-only
   at `/check/tests`. It must print one line per task:

   ```
   @@RESULT {"task": "greet", "passed": true, "message": "ok"}
   ```

   Missing tasks count as failed. Messages should describe what went wrong without revealing the
   solution. Catch errors per task so one broken file does not hide the other results.
6. `bash scripts/build_lab_images.sh`, then restart the backend. An invalid `lab.yaml` stops the backend
   at start-up with a clear error.

## 3. AWS deploy (single EC2 host)

### 3.1 Launch the instance (AWS console)

1. Region **ap-south-1 (Mumbai)**. EC2 > Launch instance.
2. AMI: **Ubuntu Server 24.04 LTS (x86_64)**.
3. Type: **t3.large** for the POC (m6i.xlarge for roughly 30 to 50 concurrent users).
4. Key pair: create one, download the `.pem` (`chmod 400 labbox.pem`).
5. Network: new security group with inbound **22 from My IP only**, **80** and **443** from anywhere.
6. Storage: **40 GB gp3**.
7. Advanced details: **no IAM instance profile**. Metadata version **V2 only**, and metadata
   response hop limit **1** (a second guard so containers cannot reach instance metadata).
8. Launch. Then Elastic IPs > Allocate > Associate with the instance.

### 3.2 Set up the host

```bash
ssh -i labbox.pem ubuntu@<elastic-ip>
git clone <repo> /tmp/labbox-setup && sudo bash /tmp/labbox-setup/deploy/ec2_setup.sh
exit    # log out and back in so the docker group applies
```

`deploy/ec2_setup.sh` installs Docker, gVisor (`runsc`, verified with hello-world), Python 3.12, Node 22,
Nginx and iptables-persistent, blocks containers from `169.254.169.254`, and creates
`/srv/labbox/{volumes,checks}` and `/opt/labbox` owned by `ubuntu`. It is safe to run again.

### 3.3 Install the app

```bash
git clone <repo> /opt/labbox && cd /opt/labbox
bash scripts/build_lab_images.sh
cd backend && python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # set JWT_SECRET, VOLUMES_DIR=/srv/labbox/volumes, CONTAINER_RUNTIME=runsc, CORS_ORIGINS
cd ../frontend && npm ci && npm run build      # output: frontend/dist
sudo cp ../deploy/labbox.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now labbox
sudo cp ../deploy/nginx.conf /etc/nginx/sites-available/labbox && sudo ln -sf /etc/nginx/sites-available/labbox /etc/nginx/sites-enabled/labbox && sudo rm -f /etc/nginx/sites-enabled/default && sudo nginx -t && sudo systemctl reload nginx
```

Check: `curl http://<elastic-ip>/api/health` returns `{"ok":true,"docker":true}`. Logs:
`journalctl -u labbox -f`.

### 3.4 HTTPS (recommended)

Point a domain's A record at the Elastic IP, then:

```bash
sudo apt install -y certbot python3-certbot-nginx && sudo certbot --nginx -d labs.example.com
```

Add `https://labs.example.com` to `CORS_ORIGINS`. The frontend switches to `wss://` by itself.

### 3.5 Cost control

- Stop the instance in the console when you are not testing (you then pay only for storage and the
  Elastic IP).
- Set an AWS Budget alert (for example $20/month) under Billing.

## 4. Security notes

- User and check containers run as uid 1000 with `cap_drop=ALL`, `no-new-privileges`, pids, memory
  (no swap) and CPU limits. Nothing is privileged and the Docker socket is never mounted.
- Check containers have no network and get the tests read-only. Hidden tests are never copied into a
  workspace or served by the API.
- Every route takes the user id from the JWT only. The terminal WebSocket requires a valid JWT.
- The file API rejects absolute paths, `..` escapes and symlinks that leave the workspace.
  Delete and rename act on a symlink itself, never on its target.
- On EC2: gVisor (`CONTAINER_RUNTIME=runsc`) and the metadata-service block.
- The backend talks to Docker, which is root-equivalent: keep the host for LabBox only.

## 5. Known POC limits

- Single host. Containers, the check lock and the reaper all live on one machine and in one process
  (run uvicorn with **one worker**).
- In-memory locks: "one check per user" is per process.
- No per-user disk quota on workspaces (Check refuses workspaces over 20 MB).
- SQLite: fine for a POC, not for many concurrent writers.
- An open editor tab does not notice when the same file is changed from the terminal. Reopen the file
  to see the new content.
- A determined user can still fake a passing check from inside their own process (for example by
  printing a `@@RESULT` line and exiting before the real checks run). Graders that must be
  tamper-proof should run user code in a separate process from the reporter.
