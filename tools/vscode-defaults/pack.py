"""Packs the labbox-defaults VS Code extension (a .vsix) from SETTINGS in backend/app/ide.py.
Usage: backend/.venv/bin/python tools/vscode-defaults/pack.py OUT.vsix"""
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.ide import SETTINGS  # noqa: E402

VERSION = "1.0.0"
PACKAGE = {
    "name": "labbox-defaults", "displayName": "LabBox defaults", "publisher": "labbox", "version": VERSION,
    "description": "Default settings for VS Code in LabBox labs: no workspace trust prompt, no Copilot chat, lab fonts, auto-save.",
    "engines": {"vscode": "^1.80.0"}, "categories": ["Other"],
    "contributes": {"configurationDefaults": SETTINGS},
}
MANIFEST = f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="labbox-defaults" Version="{VERSION}" Publisher="labbox" />
    <DisplayName>LabBox defaults</DisplayName>
    <Description xml:space="preserve">Default settings for VS Code in LabBox labs.</Description>
    <Properties><Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.80.0" /></Properties>
  </Metadata>
  <Installation><InstallationTarget Id="Microsoft.VisualStudio.Code" /></Installation>
  <Dependencies />
  <Assets><Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" /></Assets>
</PackageManifest>
"""
TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension=".json" ContentType="application/json"/><Default Extension=".vsixmanifest" ContentType="text/xml"/></Types>
"""

with zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", TYPES)
    z.writestr("extension.vsixmanifest", MANIFEST)
    z.writestr("extension/package.json", json.dumps(PACKAGE, indent=2))
print("packed", sys.argv[1])
