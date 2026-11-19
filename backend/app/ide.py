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
    "workbench.colorTheme": "Default Dark Modern",
    "workbench.startupEditor": "none",
    "workbench.tips.enabled": False,
    "workbench.enableExperiments": False,
    "editor.fontFamily": "'JetBrains Mono', 'Cascadia Code', Consolas, 'Courier New', monospace",
    "editor.fontSize": 15,
    "editor.lineHeight": 24,
    "editor.fontLigatures": True,
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


def mounts() -> dict:
    return {str(get_settings().IDE_DIR): {"bind": MOUNT, "mode": "ro"}} if available() else {}


def _command(ws: Workspace) -> list[str]:
    settings_json = json.dumps(SETTINGS, indent=2)
    server = [
        SERVER, "--host", "0.0.0.0", "--port", str(PORT),
        "--connection-token", token(ws.user_id, ws.lab_id),
        "--server-base-path", base_path(ws.lab_id),
        "--extensions-dir", f"{MOUNT}/extensions",
        "--default-folder", "/workspace",
        "--telemetry-level", "off",
    ]
    quoted = " ".join("'" + a.replace("'", "'\\''") + "'" for a in server)
    return [
        "sh", "-c",
        "pgrep -u 1000 -f '[s]erver-main.js' >/dev/null && exit 0; "  # [s]: the pattern must not match this shell itself
        # User settings (workspace trust, layout) and Machine settings (editor) both get the same file.
        "mkdir -p ~/.openvscode-server/data/Machine ~/.openvscode-server/data/User && "
        f"cat > ~/.openvscode-server/data/Machine/settings.json <<'JSON'\n{settings_json}\nJSON\n"
        "cp ~/.openvscode-server/data/Machine/settings.json ~/.openvscode-server/data/User/settings.json; "
        f"setsid nohup {quoted} > /tmp/openvscode.log 2>&1 < /dev/null &",
    ]


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


def inject_defaults(page: str) -> str:
    """Add our SETTINGS as configurationDefaults to VS Code's start page. They are registered before
    the workbench starts, early enough for settings like workspace trust (an extension is too late)."""
    def add(m: re.Match) -> str:
        try:
            config = json.loads(html.unescape(m.group(2)))
        except ValueError:
            return m.group(0)
        config["configurationDefaults"] = {**config.get("configurationDefaults", {}), **SETTINGS}
        return m.group(1) + html.escape(json.dumps(config), quote=True) + m.group(3)

    return _CONFIG.sub(add, page, count=1)
