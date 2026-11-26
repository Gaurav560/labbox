# The live site on this laptop (Cloudflare Tunnel)

The owner's call (27 November): until a server is affordable, the live site runs on this laptop beside
development, and Cloudflare Tunnel connects it to `labbox.gauravships.systems` with HTTPS and no open ports.
The same scripts work on a rented Linux server later (only the tunnel step changes).

## What runs where

| | Development (unchanged) | Live site |
|---|---|---|
| Code | `~/labs_poc`, `~/labs_poc_ukiyo` | `/srv/labbox/prod/releases/<commit>`, `current` points at the live one |
| Backend | :8000 | :8100 (`labbox-prod`), AI gateway :9100 |
| Worker | `arq` by hand | `labbox-prod-worker` |
| Web | Vite :5173, :5174 | Caddy :8180 (`labbox-prod-caddy`): the built frontend, `/api`, `/ws`, `/preview`, `/ide` |
| Internet | none | `labbox-prod-tunnel` (cloudflared) |
| Database | `labbox` | `labbox_prod` (same Postgres container) |
| Redis | db 0 (tests: 15) | db 2 |
| Lab machines | `lab-u1-...` | `lab-prod-u1-...` (`INSTANCE=prod`) |
| Files | `/srv/labbox/volumes`, `checks`, `backups` | `/srv/labbox/prod/volumes`, `checks`, `backups` |
| Settings | `backend/.env` | `/srv/labbox/prod/shared/.env` (written by `setup.sh`) |

Shared: Docker, the lab images, the Postgres and Redis containers (`scripts/devdb.sh`), VS Code for labs.
All services are systemd user services (`systemctl --user ...`).

## One-time setup

```
deploy/laptop/setup.sh                     # folders, Caddy and cloudflared, database, .env, services
sudo loginctl enable-linger gaurav         # the owner, once: services run after a reboot without a login
deploy/laptop/setup.sh tunnel labbox.gauravships.systems   # opens a Cloudflare login link, then the tunnel
```

`setup.sh --copy-openai-key` copies the `OPENAI_API_KEY` line from `backend/.env` into the live `.env`
without showing it (only with the owner's OK); otherwise the owner adds it to `/srv/labbox/prod/shared/.env`.

## Deploying

GitHub, Actions, **Deploy**, Run workflow, pick the branch (default `design/ukiyo`). The workflow runs the
tests, moves the `production` branch to that commit, and waits until the live site reports it. On this laptop,
`labbox-prod-deploy.timer` looks at `production` every minute and runs `release.sh` when it moved:

1. a fresh copy of the commit in `releases/<commit>` (packages, frontend build, `labbox validate --strict`),
2. lab images rebuilt for labs whose folder changed since the live release,
3. database migrations (additive only), then `current` switches and the services restart,
4. `/api/health` must report the new commit with Docker and the database up, and Caddy must serve the page.

If step 4 fails, `current` switches back and the services restart on the previous release; the commit is
remembered as failed and not tried again until `production` moves on.

## Everyday commands

```
deploy/laptop/prod status          # services, live commit, health
deploy/laptop/prod logs [service]  # backend (default), worker, caddy, tunnel, deploy
deploy/laptop/prod deploy <commit> # deploy by hand (same as the timer)
deploy/laptop/prod rollback        # back to the previous release
deploy/laptop/prod labbox ...      # the labbox CLI against the live database, e.g. `admin grant gaurav`
```

## Rules

- Never run tests, browser tests or `test-accounts cleanup` against the live site. Development tools read
  `backend/.env`; only `deploy/laptop/prod labbox ...` reads the live settings.
- Lab images are shared: building an image in development replaces the live one too. After building images
  from unfinished work, rebuild them from the live release (`deploy/laptop/prod images <lab>`).
- Sign-up is off on the live site (`ALLOW_SIGNUP=false`): learners' code runs on this laptop, so the owner
  creates accounts for invited testers (`deploy/laptop/prod adduser <name>`, which asks for a password).
- The laptop must not sleep (lid closed: do nothing; no automatic suspend), or the site goes down.
