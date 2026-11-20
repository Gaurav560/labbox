"""VS Code in the lab: openvscode-server (Gitpod's open-source VS Code, MIT) runs inside the learner's
own machine, as the learner, and reaches the browser at /ide/{lab}/ through the same signed-in proxy
as the Preview tab. The server files live on the host (scripts/openvscode.sh) and are mounted
read-only, so no lab image has to be rebuilt.

Each machine's VS Code also needs a connection token: derived from the server secret, the user and
the lab, so it survives restarts and is useless for any other learner's machine.
"""
import hashlib
import hmac
import html
import json
import logging
import re
import time

import httpx

from . import containers, services
from .config import get_settings
from .labs import LabConfig
from .models import Workspace

log = logging.getLogger(__name__)

PORT = 3333
MOUNT = "/opt/openvscode"
SERVER = f"{MOUNT}/current/bin/openvscode-server"
READY_SECONDS = 25

# Machine settings: what makes it feel like a fresh VS Code, minus the parts that do not fit a lab.
SETTINGS = {
    "workbench.colorTheme": "LabBox Dark",  # from the labbox-defaults extension (tools/vscode-defaults)
    "workbench.startupEditor": "none",
    "workbench.tips.enabled": False,
    "workbench.enableExperiments": False,
    "editor.fontFamily": "'JetBrains Mono', 'Cascadia Code', Consolas, 'Courier New', monospace",
    "terminal.integrated.fontFamily": "'JetBrains Mono', monospace",
    "editor.fontSize": 15,
    "editor.lineHeight": 24,
    "editor.fontLigatures": False,  # code shows exactly what to type: `===` stays three characters
    "editor.minimap.renderCharacters": False,
    "editor.bracketPairColorization.enabled": True,
    "editor.stickyScroll.enabled": True,
    "files.autoSave": "afterDelay",  # Check always sees the latest code
    "files.autoSaveDelay": 500,
    "terminal.integrated.fontSize": 14,
    "security.workspace.trust.enabled": False,
    "telemetry.telemetryLevel": "off",
    "update.mode": "none",
    "extensions.autoCheckUpdates": False,
    "extensions.autoUpdate": False,
    # There is no marketplace in labs, so "install the recommended extension" toasts lead nowhere.
    "extensions.ignoreRecommendations": True,
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "git.openRepositoryInParentFolders": "always",
    "workbench.welcomePage.walkthroughs.openOnInstall": False,
    "workbench.secondarySideBar.defaultVisibility": "hidden",
    "chat.disableAIFeatures": True,  # Copilot chat needs a GitHub account; our tutor lives in the lesson panel
    "chat.commandCenter.enabled": False,
    "workbench.layoutControl.enabled": False,
}


def available() -> bool:
    s = get_settings()
    return s.IDE_ENABLED and (s.IDE_DIR / "current" / "bin" / "openvscode-server").exists()


def token(user_id: int, lab_id: str) -> str:
    key = get_settings().JWT_SECRET.encode()
    return hmac.new(key, f"ide:{user_id}:{lab_id}".encode(), hashlib.sha256).hexdigest()[:40]


def base_path(lab_id: str) -> str:
    return f"/ide/{lab_id}"


def workspace_file(lab_id: str) -> str:
    """VS Code remembers open tabs per workspace, and every lab's folder is /workspace on the same
    address, so one lab's tabs used to reopen in the next. A small workspace file named after the lab
    gives each lab its own memory; the folder, paths and terminal stay exactly the same."""
    return f"/home/learner/.labbox/{lab_id}.code-workspace"


def mounts() -> dict:
    return {str(get_settings().IDE_DIR): {"bind": MOUNT, "mode": "ro"}} if available() else {}


# Font sizes follow the learner's text size (the lab's Aa menu): they are only start-page defaults
# (see inject_defaults), because a machine settings.json value would always win over them.
SIZED = ("editor.fontSize", "editor.lineHeight", "terminal.integrated.fontSize")


def machine_settings() -> dict:
    return {k: v for k, v in SETTINGS.items() if k not in SIZED}


def _command(ws: Workspace) -> list[str]:
    settings_json = json.dumps(machine_settings(), indent=2)
    server = [
        SERVER, "--host", "0.0.0.0", "--port", str(PORT),
        "--connection-token", token(ws.user_id, ws.lab_id),
        "--server-base-path", base_path(ws.lab_id),
        "--extensions-dir", f"{MOUNT}/extensions",
        "--default-folder", "/workspace",
        "--telemetry-level", "off",
    ]
    quoted = " ".join("'" + a.replace("'", "'\\''") + "'" for a in server)
    stamp = setup_stamp()
    wsf = workspace_file(ws.lab_id)
    workspace_json = json.dumps({"folders": [{"path": "/workspace"}], "settings": {}})
    return [
        "sh", "-c",
        # First, every time: the lab's workspace file (cheap, and it must exist even when VS Code is
        # already running from an earlier visit).
        f"mkdir -p \"$(dirname '{wsf}')\" && printf '%s' '{workspace_json}' > '{wsf}'; "
        # Already running with the current setup: nothing to do. ([s]: the pattern must not match this
        # shell itself.) Running with an older setup (new extensions or theme): restart it.
        f"[ \"$(cat /tmp/openvscode.stamp 2>/dev/null)\" = '{stamp}' ] && pgrep -u 1000 -f '[s]erver-main.js' >/dev/null && exit 0; "
        "pkill -u 1000 -f '[s]erver-main.js'; sleep 0.3; "
        f"echo '{stamp}' > /tmp/openvscode.stamp; "
        # User settings (workspace trust, layout) and Machine settings (editor) both get the same file.
        "mkdir -p ~/.openvscode-server/data/Machine ~/.openvscode-server/data/User && "
        f"cat > ~/.openvscode-server/data/Machine/settings.json <<'JSON'\n{settings_json}\nJSON\n"
        "cp ~/.openvscode-server/data/Machine/settings.json ~/.openvscode-server/data/User/settings.json; "
        f"setsid nohup {quoted} > /tmp/openvscode.log 2>&1 < /dev/null &",
    ]


def setup_stamp() -> str:
    """Changes when scripts/openvscode.sh installs something new (extensions, theme, product settings
    such as the switched-off marketplace) or SETTINGS change."""
    base = get_settings().IDE_DIR
    files = [base / "extensions" / "extensions.json", base / "current" / "product.json"]
    mtime = ":".join(str(f.stat().st_mtime_ns) if f.exists() else "0" for f in files)
    return hashlib.sha256(f"{mtime}:{json.dumps(machine_settings(), sort_keys=True)}".encode()).hexdigest()[:16]


def start(lab: LabConfig, ws: Workspace) -> None:
    """Start VS Code in the running machine if it is not running yet (cheap when it is). Called when
    the lab page opens VS Code, so learners on the classic editor never pay for it."""
    if not available():
        return
    c = containers.client().containers.get(ws.container_name)
    r = c.exec_run(_command(ws), user=containers.LEARNER_USER, environment={"HOME": "/home/learner"})
    if r.exit_code != 0:
        log.warning("VS Code did not start in %s: %s", ws.container_name, r.output.decode(errors="replace")[-300:])


def wait_ready(lab: LabConfig, ws: Workspace) -> bool:
    net = services.network_name(ws) if lab.uses_lab_network else None
    deadline = time.monotonic() + READY_SECONDS
    while time.monotonic() < deadline:
        ip = services.container_ip(ws.container_name, prefer_network=net)
        if ip:
            try:
                r = httpx.get(f"http://{ip}:{PORT}{base_path(ws.lab_id)}/", timeout=2)
                if r.status_code < 500:
                    return True
            except httpx.HTTPError:
                pass
        time.sleep(0.4)
    return False


_CONFIG = re.compile(r'(id="vscode-workbench-web-configuration"\s+data-settings=")([^"]*)(")')


def is_start_page(lab_id: str, path: str) -> bool:
    return path.rstrip("/") == base_path(lab_id)


def text_scale(value: str | None) -> int:
    """A learner's text size in percent (the lab's Aa menu), clamped to 80..150; 100 if missing or bad."""
    try:
        return min(150, max(80, int(value or 100)))
    except ValueError:
        return 100


def sized_settings(editor_pct: int = 100, terminal_pct: int = 100) -> dict:
    """SETTINGS with the editor and terminal fonts scaled to the learner's text size."""
    return {
        **SETTINGS,
        "editor.fontSize": round(SETTINGS["editor.fontSize"] * editor_pct / 100),
        "editor.lineHeight": round(SETTINGS["editor.lineHeight"] * editor_pct / 100),
        "terminal.integrated.fontSize": round(SETTINGS["terminal.integrated.fontSize"] * terminal_pct / 100),
    }


def inject_defaults(page: str, editor_pct: int = 100, terminal_pct: int = 100) -> str:
    """Add our SETTINGS as configurationDefaults to VS Code's start page. They are registered before
    the workbench starts, early enough for settings like workspace trust (an extension is too late)."""
    settings = sized_settings(editor_pct, terminal_pct)

    def add(m: re.Match) -> str:
        try:
            config = json.loads(html.unescape(m.group(2)))
        except ValueError:
            return m.group(0)
        config["configurationDefaults"] = {**config.get("configurationDefaults", {}), **settings}
        return m.group(1) + html.escape(json.dumps(config), quote=True) + m.group(3)

    page = _CONFIG.sub(add, page, count=1)
    return page.replace("</head>", FONT_FACES + "</head>", 1)


# JetBrains Mono inside VS Code (the files come from scripts/openvscode.sh, served at /ide-fonts/).
FONT_FILES = {f"jetbrains-mono-latin-{w}-{s}.woff2" for w in (400, 700) for s in ("normal", "italic")}
FONT_FACES = "<style>" + "".join(
    f"@font-face{{font-family:'JetBrains Mono';font-style:{s};font-weight:{w};font-display:swap;"
    f"src:url('/ide-fonts/jetbrains-mono-latin-{w}-{s}.woff2') format('woff2')}}"
    for w in (400, 700) for s in ("normal", "italic")
) + "</style>"
