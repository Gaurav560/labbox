"""The lab's text size menu reaches real VS Code through the start page (lb_fs / lb_ts)."""

import html
import json

from app import ide

PAGE = ('<html><head><meta id="vscode-workbench-web-configuration" data-settings="'
        + html.escape(json.dumps({"folderUri": "x"}), quote=True) + '"></head><body></body></html>')


def _defaults(page: str) -> dict:
    raw = page.split('data-settings="', 1)[1].split('"', 1)[0]
    return json.loads(html.unescape(raw))["configurationDefaults"]


def test_text_scale_is_clamped_and_forgiving():
    assert ide.text_scale(None) == 100
    assert ide.text_scale("130") == 130
    assert ide.text_scale("500") == 150
    assert ide.text_scale("10") == 80
    assert ide.text_scale("big") == 100


def test_start_page_gets_scaled_fonts():
    d = _defaults(ide.inject_defaults(PAGE, 120, 150))
    assert d["editor.fontSize"] == 18 and d["editor.lineHeight"] == 29
    assert d["terminal.integrated.fontSize"] == 21
    assert d["workbench.colorTheme"] == ide.SETTINGS["workbench.colorTheme"]


def test_default_size_keeps_the_settings():
    d = _defaults(ide.inject_defaults(PAGE))
    assert d["editor.fontSize"] == ide.SETTINGS["editor.fontSize"]
    # The restart stamp ignores text size, so changing it never restarts a running IDE.
    assert ide.SETTINGS["editor.fontSize"] == 15


def test_machine_settings_leave_font_sizes_to_the_start_page():
    # A settings.json value would beat the start page's defaults, so sizes are not written there.
    m = ide.machine_settings()
    assert not set(ide.SIZED) & set(m)
    assert m["workbench.colorTheme"] == ide.SETTINGS["workbench.colorTheme"]
