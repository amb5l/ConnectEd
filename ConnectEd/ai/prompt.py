"""System prompt assembly for AI chat sessions."""

from __future__ import annotations

import re

from functools import lru_cache
from pathlib   import Path

from ..app import settings

from .types import ToolSpec

_PROMPT_MD_PATH = Path(__file__).with_name("prompt.md")


def connectionReadyMessage(model : str) -> str:
    """Short greeting shown in the chat when a model connection succeeds."""
    name = model.strip() or "AI"
    return f"{name} is ready."


def _isStructuralLine(line : str) -> bool:
    stripped = line.lstrip()
    return (
        stripped.startswith("#")
        or stripped.startswith("- ")
        or stripped.startswith("{")
        or bool(re.match(r"^\d+\.", stripped))
    )


def _normalizeWrappedText(text : str) -> str:
    """Join hard-wrapped lines; keep blank lines and structural rows."""
    lines = text.splitlines()
    out   : list[str] = []
    i     = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            out.append("")
            i += 1
            continue
        if _isStructuralLine(line):
            block = [line.strip()]
            i += 1
            while (
                i < len(lines)
                and lines[i].startswith((" ", "\t"))
                and lines[i].strip()
            ):
                block.append(lines[i].strip())
                i += 1
            out.append(" ".join(block))
            continue
        parts : list[str] = []
        while (
            i < len(lines)
            and lines[i].strip()
            and not _isStructuralLine(lines[i])
            and not lines[i].startswith((" ", "\t"))
        ):
            parts.append(lines[i].strip())
            i += 1
        if parts:
            out.append(" ".join(parts))
    return "\n".join(out)


@lru_cache(maxsize=1)
def _loadSystemTemplate() -> str:
    raw = _PROMPT_MD_PATH.read_text(encoding="utf-8")
    return _normalizeWrappedText(raw)


def formatToolsForPrompt(
    tools           : list[ToolSpec],
    write_tool_names: frozenset[str] | None = None,
) -> str:
    if not tools:
        return "- (none)"
    write_tool_names = write_tool_names or frozenset()
    return "\n".join(
        f"- **{tool.name}** ({'write' if tool.name in write_tool_names else 'read'})"
        f" — {tool.description}"
        for tool in tools
    )


def buildSystemPrompt(
    tools            : list[ToolSpec],
    write_tool_names : frozenset[str] | None = None,
) -> str:
    body = _loadSystemTemplate().format(
        tool_lines = formatToolsForPrompt(tools, write_tool_names),
    )
    extra = (settings().get("ai/system_prompt_extra") or "").strip()
    if extra:
        body = f"{body}\n\n### User instructions\n{extra}"
    return body
