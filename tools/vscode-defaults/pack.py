"""Packs the labbox-defaults VS Code extension (a .vsix) from SETTINGS in backend/app/ide.py.
Usage: backend/.venv/bin/python tools/vscode-defaults/pack.py OUT.vsix"""
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.ide import machine_settings  # noqa: E402  (font sizes follow the learner, see ide.SIZED)

VERSION = "1.3.0"

# "LabBox Dark": the app's GitHub greys around the code, GitHub's code colours, a green accent.
BG, SIDE, BORDER, TEXT, MUTED, GREEN = "#111512", "#0d100e", "#222824", "#e6edf3", "#9ba39d", "#3fb950"
THEME = {
    "name": "LabBox Dark",
    "type": "dark",
    "semanticHighlighting": True,
    "colors": {
        "foreground": TEXT, "focusBorder": GREEN + "88", "selection.background": "#264f78",
        "editor.background": BG, "editor.foreground": TEXT, "editor.lineHighlightBackground": "#181d19",
        "editor.lineHighlightBorder": "#00000000", "editor.selectionBackground": "#264f78",
        "editorLineNumber.foreground": "#4b544e", "editorLineNumber.activeForeground": TEXT,
        "editorIndentGuide.background1": "#232924", "editorIndentGuide.activeBackground1": "#4b544e",
        "editorBracketHighlight.foreground1": "#ffd700", "editorBracketHighlight.foreground2": "#da70d6",
        "editorBracketHighlight.foreground3": "#179fff", "editorCursor.foreground": TEXT,
        "editorWidget.background": "#161a17", "editorWidget.border": BORDER,
        "editorSuggestWidget.background": "#161a17", "editorSuggestWidget.selectedBackground": "#1f3a5f",
        "editorGroupHeader.tabsBackground": SIDE, "editorGroupHeader.tabsBorder": BORDER, "editorGroup.border": BORDER,
        "tab.activeBackground": BG, "tab.activeForeground": TEXT, "tab.activeBorderTop": GREEN,
        "tab.inactiveBackground": SIDE, "tab.inactiveForeground": MUTED, "tab.border": BORDER, "tab.hoverBackground": "#161a17",
        "activityBar.background": SIDE, "activityBar.foreground": TEXT, "activityBar.inactiveForeground": "#6b736d",
        "activityBar.border": BORDER, "activityBar.activeBorder": GREEN, "activityBarBadge.background": GREEN,
        "activityBarBadge.foreground": "#0a0a0a",
        "sideBar.background": SIDE, "sideBar.foreground": "#c9d1cb", "sideBar.border": BORDER,
        "sideBarSectionHeader.background": SIDE, "sideBarSectionHeader.border": BORDER, "sideBarTitle.foreground": MUTED,
        "list.activeSelectionBackground": "#1f2a22", "list.activeSelectionForeground": TEXT,
        "list.inactiveSelectionBackground": "#1a201b", "list.hoverBackground": "#161a17", "list.focusOutline": GREEN + "66",
        "titleBar.activeBackground": SIDE, "titleBar.activeForeground": MUTED, "titleBar.border": BORDER,
        "commandCenter.background": "#161a17", "commandCenter.border": BORDER,
        "statusBar.background": SIDE, "statusBar.foreground": MUTED, "statusBar.border": BORDER,
        "statusBar.noFolderBackground": SIDE, "statusBarItem.remoteBackground": "#1f2a22", "statusBarItem.remoteForeground": GREEN,
        "panel.background": SIDE, "panel.border": BORDER, "panelTitle.activeBorder": GREEN, "panelTitle.activeForeground": TEXT,
        "terminal.background": SIDE, "terminal.foreground": TEXT,
        "input.background": "#161a17", "input.border": BORDER, "dropdown.background": "#161a17", "dropdown.border": BORDER,
        "button.background": "#f0f3f1", "button.foreground": "#0a0a0a", "button.hoverBackground": "#ffffff",
        "badge.background": GREEN, "badge.foreground": "#0a0a0a", "progressBar.background": GREEN,
        "scrollbarSlider.background": "#ffffff14", "scrollbarSlider.hoverBackground": "#ffffff24",
        "minimap.background": BG, "breadcrumb.foreground": MUTED, "breadcrumb.focusForeground": TEXT,
        "notifications.background": "#161a17", "notifications.border": BORDER, "menu.background": "#161a17", "menu.border": BORDER,
        "textLink.foreground": "#58a6ff", "gitDecoration.modifiedResourceForeground": "#d29922",
        "gitDecoration.untrackedResourceForeground": GREEN, "gitDecoration.deletedResourceForeground": "#f85149",
    },
    "tokenColors": [
        {"scope": ["comment", "punctuation.definition.comment"], "settings": {"foreground": "#8b949e", "fontStyle": "italic"}},
        {"scope": ["keyword", "storage", "storage.type", "keyword.operator.logical", "keyword.control"], "settings": {"foreground": "#ff7b72"}},
        {"scope": ["string", "punctuation.definition.string"], "settings": {"foreground": "#a5d6ff"}},
        {"scope": ["constant.numeric", "constant.language", "constant.character.escape", "support.constant"], "settings": {"foreground": "#79c0ff"}},
        {"scope": ["entity.name.function", "support.function", "meta.function-call.generic"], "settings": {"foreground": "#d2a8ff"}},
        {"scope": ["entity.name.type", "entity.name.class", "support.class", "support.type", "entity.other.inherited-class"], "settings": {"foreground": "#ffa657"}},
        {"scope": ["meta.decorator", "entity.name.function.decorator", "punctuation.definition.decorator", "storage.type.annotation"], "settings": {"foreground": "#d2a8ff"}},
        {"scope": ["variable.parameter"], "settings": {"foreground": "#ffa657"}},
        {"scope": ["variable", "meta.definition.variable"], "settings": {"foreground": TEXT}},
        {"scope": ["entity.name.tag"], "settings": {"foreground": "#7ee787"}},
        {"scope": ["entity.other.attribute-name"], "settings": {"foreground": "#79c0ff"}},
        {"scope": ["markup.heading", "markup.heading entity.name"], "settings": {"foreground": "#79c0ff", "fontStyle": "bold"}},
        {"scope": ["markup.bold"], "settings": {"fontStyle": "bold"}},
        {"scope": ["markup.italic"], "settings": {"fontStyle": "italic"}},
        {"scope": ["markup.inline.raw", "markup.fenced_code"], "settings": {"foreground": "#a5d6ff"}},
    ],
}
PACKAGE = {
    "name": "labbox-defaults", "displayName": "LabBox defaults", "publisher": "labbox", "version": VERSION,
    "description": "Opens each chapter's code, plus the LabBox Dark theme and default settings for VS Code in LabBox labs: no workspace trust prompt, no Copilot chat, lab fonts, auto-save.",
    "engines": {"vscode": "^1.80.0"}, "categories": ["Other"],
    # extension.js runs next to the files (in the machine): it opens a chapter's code on request.
    "main": "./extension.js", "activationEvents": ["onStartupFinished"], "extensionKind": ["workspace"],
    "contributes": {
        "configurationDefaults": machine_settings(),
        "themes": [{"label": "LabBox Dark", "uiTheme": "vs-dark", "path": "./themes/labbox-dark.json"}],
    },
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
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension=".json" ContentType="application/json"/><Default Extension=".vsixmanifest" ContentType="text/xml"/><Default Extension=".js" ContentType="application/javascript"/></Types>
"""

with zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", TYPES)
    z.writestr("extension.vsixmanifest", MANIFEST)
    z.writestr("extension/package.json", json.dumps(PACKAGE, indent=2))
    z.writestr("extension/themes/labbox-dark.json", json.dumps(THEME, indent=2))
    z.write(Path(__file__).with_name("extension.js"), "extension/extension.js")
print("packed", sys.argv[1])
