"""
One-shot export of FACTORY_SETTINGS to settings.yaml and themes/*.yaml.

Run from repo root:
  .venv\\Scripts\\python.exe scripts/export_factory_settings_yaml.py
"""
from __future__ import annotations

import os
import sys
from dataclasses import fields
from pathlib import Path
from typing import Any

import yaml
from PyQt6.QtCore import Qt, QPointF, QSizeF
from PyQt6.QtGui import QColor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ConnectEd.core.settings import loadFactorySettings  # noqa: E402
from ConnectEd.core.themes.yaml_format import formatThemeDoc  # noqa: E402
from ConnectEd.core.palette import (  # noqa: E402
    ThemePalette,
    palette_dark,
    palette_light_mono,
)
from ConnectEd.core.utils import val2str  # noqa: E402

CORE = ROOT / "ConnectEd" / "core"
THEMES = CORE / "themes"

THEME_META = {
    "dark"       : {"display_name": "Dark"},
    "light_mono" : {"display_name": "Light mono"},
}

THEME_PALETTES = {
    "dark"       : palette_dark,
    "light_mono" : palette_light_mono,
}


def _palettePresets(palette : ThemePalette) -> dict[str, str]:
    return {f.name: val2str(getattr(palette, f.name)) for f in fields(ThemePalette)}


def _colorToken(value : Any, palette : ThemePalette) -> str:
    if not isinstance(value, QColor):
        return value
    for f in fields(ThemePalette):
        if getattr(palette, f.name) == value:
            return f"@{f.name}"
    return val2str(value)


def _exportThemeValue(
    value   : Any,
    palette : ThemePalette,
    parent_key : str | None = None,
) -> Any:
    if isinstance(value, dict):
        return {
            k: _exportThemeValue(v, palette, k)
            for k, v in value.items()
        }
    if isinstance(value, QColor):
        return _colorToken(value, palette)
    t = type(value).__name__
    if t == "PenStyle":
        return str(value).replace("PenStyle.", "")
    if t == "BrushStyle":
        return str(value).replace("BrushStyle.", "")
    if t in ("int", "float", "bool", "str"):
        return value
    return val2str(value)


def _exportAppValue(path : str, value : Any) -> Any:
    if path == "startup/geometry":
        return ""
    if path in ("prefs/file/open/dir", "prefs/file/save/dir"):
        return ""
    if path == "defaults/sheet/size":
        return None  # omit
    if isinstance(value, dict):
        r = {}
        for k, v in value.items():
            child = f"{path}/{k}" if path else k
            exported = _exportAppValue(child, v)
            if exported is not None:
                r[k] = exported
        return r
    t = type(value).__name__
    if t == "QSizeF":
        return [value.width(), value.height()]
    if t == "QPointF":
        return [value.x(), value.y()]
    if t == "PenStyle":
        return str(value).replace("PenStyle.", "")
    if t == "bytes":
        return ""
    if t in ("int", "float", "bool", "str"):
        return value
    return val2str(value)


def _collectLeafKinds(
    d    : dict,
    path : str,
    out  : dict[str, str],
) -> None:
    for k, v in d.items():
        p = f"{path}/{k}" if path else k
        if isinstance(v, dict):
            _collectLeafKinds(v, p, out)
        else:
            out[p] = type(v).__name__


def export() -> None:
    THEMES.mkdir(parents=True, exist_ok=True)

    app : dict[str, Any] = {}
    for group, value in loadFactorySettings().items():
        if group == "themes":
            continue
        app[group] = _exportAppValue(group, value)

    with (CORE / "settings.yaml").open("w", encoding="utf-8") as f:
        yaml.dump(
            app,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

    leaf_kinds : dict[str, str] = {}
    _collectLeafKinds(app, "", leaf_kinds)

    for theme_id, palette in THEME_PALETTES.items():
        tree = loadFactorySettings()["themes"][theme_id]
        doc = {
            "meta": {
                "id"           : theme_id,
                "display_name" : THEME_META[theme_id]["display_name"],
            },
            "presets": _palettePresets(palette),
            **_exportThemeValue(tree, palette),
        }
        path = THEMES / f"{theme_id}.yaml"
        path.write_text(formatThemeDoc(doc), encoding="utf-8")

    kinds_path = CORE / "settings_loader_leaf_kinds.txt"
    with kinds_path.open("w", encoding="utf-8") as f:
        for path in sorted(leaf_kinds):
            f.write(f"{path!r}: {leaf_kinds[path]!r},\n")

    print(f"Wrote {CORE / 'settings.yaml'}")
    for theme_id in THEME_PALETTES:
        print(f"Wrote {THEMES / f'{theme_id}.yaml'}")
    print(f"Wrote leaf kinds ({len(leaf_kinds)} paths)")


if __name__ == "__main__":
    export()
