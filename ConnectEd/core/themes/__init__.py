from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ..check import checked
from .schema import (
    validatePalette,
    validatePresetSources,
    validatePresets,
)


BUILTIN_THEMES : tuple[str, ...] = ("dark", "light_mono")
THEME_NAMES    : frozenset[str]   = frozenset(BUILTIN_THEMES)


@checked
def resolvePresets(
    presets : dict[str, str],
    palette : dict[str, str],
    theme   : str,
) -> dict[str, str]:
    resolved : dict[str, str] = {}
    pending  = dict(presets)
    while pending:
        progress = False
        for name, value in list(pending.items()):
            if value.startswith("#"):
                resolved[name] = value
                del pending[name]
                progress = True
                continue
            if value.startswith("@"):
                token = value[1:]
                if token not in resolved:
                    continue
                resolved[name] = resolved[token]
                del pending[name]
                progress = True
                continue
            if value in palette:
                resolved[name] = palette[value]
                del pending[name]
                progress = True
                continue
            raise ValueError(
                f"Theme {theme!r} preset {name!r} must be #RRGGBB, "
                f"@Preset, or a palette name, got {value!r}"
            )
        if not progress:
            names = sorted(pending)
            raise ValueError(
                f"Theme {theme!r} unresolved preset references: {names}"
            )
    return resolved


@checked
def resolveColor(
    value   : str,
    presets : dict[str, str],
    theme   : str,
) -> QColor:
    if value.startswith("#"):
        return QColor.fromRgb(int(value[1:], 16) | 0xFF000000)
    if value.startswith("@"):
        token = value[1:]
        if token not in presets:
            raise ValueError(
                f"Theme {theme!r}: unknown color token {token!r}"
            )
        hex_color = presets[token]
        return QColor.fromRgb(int(hex_color[1:], 16) | 0xFF000000)
    raise ValueError(
        f"Theme {theme!r}: color must be #RRGGBB or @Token, got {value!r}"
    )


def _coerceThemeValue(
    key        : str,
    value      : Any,
    style_kind : str | None,
    presets    : dict[str, str],
    theme      : str,
) -> Any:
    if isinstance(value, dict):
        child_kind = key if key in ("line", "fill") else style_kind
        return {
            k: _coerceThemeValue(k, v, child_kind, presets, theme)
            for k, v in value.items()
        }
    if isinstance(value, str):
        if key == "color" or (
            value.startswith("@") or value.startswith("#")
        ):
            return resolveColor(value, presets, theme)
        if key == "style":
            if style_kind == "line":
                return Qt.PenStyle[value]
            if style_kind == "fill":
                return Qt.BrushStyle[value]
        return value
    return value


@checked
def coerceTheme(
    raw     : dict[str, Any],
    presets : dict[str, str],
    theme   : str,
) -> dict[str, Any]:
    return {
        k: _coerceThemeValue(k, v, None, presets, theme)
        for k, v in raw.items()
    }


@checked
def loadTheme(
    yaml_path : Path,
    theme_id  : str | None = None,
) -> tuple[str, dict[str, Any]]:
    with yaml_path.open(encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    if not isinstance(doc, dict):
        raise ValueError(f"Theme file {yaml_path} must be a mapping")

    meta = doc.pop("meta", None)
    if not isinstance(meta, dict) or "id" not in meta:
        raise ValueError(f"Theme file {yaml_path} missing meta.id")
    tid = str(meta["id"])
    if theme_id is not None and tid != theme_id:
        raise ValueError(
            f"Theme file {yaml_path}: meta.id {tid!r} != expected {theme_id!r}"
        )

    if (palette := doc.pop("palette", None)) is None:
        palette_str : dict[str, str] = {}
    elif not isinstance(palette, dict):
        raise ValueError(f"Theme {tid!r} palette block must be a mapping")
    else:
        palette_str = {str(k): str(v) for k, v in palette.items()}
        validatePalette(tid, palette_str)

    if not isinstance(presets := doc.pop("presets", None), dict):
        raise ValueError(f"Theme {tid!r} missing presets block")
    presets_str = {str(k): str(v) for k, v in presets.items()}
    validatePresetSources(tid, presets_str, frozenset(palette_str))
    presets_str = resolvePresets(presets_str, palette_str, tid)
    validatePresets(tid, presets_str)

    tree = coerceTheme(doc, presets_str, tid)
    return tid, tree
