#!/usr/bin/env bash
# Downloads openvscode-server (Gitpod's open-source VS Code, MIT) once, to a folder the backend mounts
# read-only into every lab machine at /opt/openvscode, and adds the free Python extensions from
# Open VSX. Safe to run again: it skips what is there.
set -euo pipefail
VERSION=v1.109.5
DIR="${IDE_DIR:-/srv/labbox/openvscode}"
NAME="openvscode-server-$VERSION-linux-x64"
if [ ! -x "$DIR/$NAME/bin/openvscode-server" ]; then
  mkdir -p "$DIR"
  curl -fL --retry 3 -o "$DIR/$NAME.tar.gz" \
    "https://github.com/gitpod-io/openvscode-server/releases/download/openvscode-server-$VERSION/$NAME.tar.gz"
  tar -xzf "$DIR/$NAME.tar.gz" -C "$DIR"
  rm "$DIR/$NAME.tar.gz"
fi
ln -sfn "$NAME" "$DIR/current"
# Extensions live next to the server, shared read-only by every lab.
EXT="$DIR/extensions"
mkdir -p "$EXT"
for ext in ms-python.python ms-python.debugpy; do
  "$DIR/current/bin/openvscode-server" --extensions-dir "$EXT" --install-extension "$ext" >/dev/null 2>&1 \
    && echo "extension $ext ok" || echo "extension $ext could not be installed (VS Code still works without it)"
done
# LabBox's default settings (no trust prompt, no Copilot chat, fonts, auto-save) as a tiny extension:
# the browser version of VS Code reads defaults from extensions, not from files on the server.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VSIX="$(mktemp -d)/labbox-defaults.vsix"
"$ROOT/backend/.venv/bin/python" "$ROOT/tools/vscode-defaults/pack.py" "$VSIX" >/dev/null
"$DIR/current/bin/openvscode-server" --extensions-dir "$EXT" --install-extension "$VSIX" --force >/dev/null 2>&1 \
  && echo "extension labbox-defaults ok" || echo "extension labbox-defaults could not be installed"
rm -rf "$(dirname "$VSIX")"
echo "openvscode-server ready in $DIR/current"
