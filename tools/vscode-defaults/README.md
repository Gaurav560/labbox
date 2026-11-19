# labbox-defaults (VS Code extension)

Only contributes default settings for VS Code in labs (`contributes.configurationDefaults`), generated
from `SETTINGS` in `backend/app/ide.py`. The browser version of VS Code reads defaults from extensions,
not from a settings file on the server. `scripts/openvscode.sh` packs and installs it.
