"""
Aligned YAML formatting for theme files.

Leaf siblings within each mapping block are written as:
  name : value
with colons vertically aligned per block.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _yamlScalar(value : Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value == int(value) else str(value)
    text = str(value)
    if " " in text or text.startswith("@") or text.startswith("#"):
        return f"'{text}'"
    return text


def _flushLeaves(
    lines     : list[str],
    indent    : int,
    leaf_run  : list[tuple[str, Any]],
) -> None:
    if not leaf_run:
        return
    sp = "  " * indent
    width = max(len(name) for name, _ in leaf_run)
    for name, value in leaf_run:
        lines.append(f"{sp}{name:<{width}} : {_yamlScalar(value)}")
    leaf_run.clear()


def _formatMapping(
    lines  : list[str],
    data   : dict[str, Any],
    indent : int,
) -> None:
    leaf_run : list[tuple[str, Any]] = []
    for name, value in data.items():
        if isinstance(value, dict):
            _flushLeaves(lines, indent, leaf_run)
            sp = "  " * indent
            lines.append(f"{sp}{name}:")
            _formatMapping(lines, value, indent + 1)
        else:
            leaf_run.append((name, value))
    _flushLeaves(lines, indent, leaf_run)


def _formatAlignedBlock(
    block_name : str,
    entries    : dict[str, Any],
) -> list[str]:
    width = max(len(name) for name in entries)
    lines = [f"{block_name}:"]
    for name, value in entries.items():
        lines.append(f"  {name:<{width}} : {_yamlScalar(value)}")
    return lines


def _formatPalette(palette : dict[str, Any]) -> list[str]:
    return _formatAlignedBlock("palette", palette)


def _formatPresets(presets : dict[str, Any]) -> list[str]:
    return _formatAlignedBlock("presets", presets)


def formatThemeDoc(doc : dict[str, Any]) -> str:
    lines : list[str] = []

    meta = doc["meta"]
    meta_width = max(len(name) for name in meta)
    lines.append("meta:")
    for name, value in meta.items():
        lines.append(f"  {name:<{meta_width}} : {_yamlScalar(value)}")

    if "palette" in doc:
        lines.extend(_formatPalette(doc["palette"]))
    lines.extend(_formatPresets(doc["presets"]))

    root_leaves : list[tuple[str, Any]] = []
    for name, value in doc.items():
        if name in ("meta", "palette", "presets"):
            continue
        if isinstance(value, dict):
            _flushLeaves(lines, 0, root_leaves)
            lines.append(f"{name}:")
            _formatMapping(lines, value, 1)
        else:
            root_leaves.append((name, value))
    _flushLeaves(lines, 0, root_leaves)

    return "\n".join(lines) + "\n"


def formatThemeFile(path : Path) -> None:
    with path.open(encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    if not isinstance(doc, dict):
        raise ValueError(f"Theme file {path} must be a mapping")
    path.write_text(formatThemeDoc(doc), encoding="utf-8")
