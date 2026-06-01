from collections.abc import Iterator

from ..types import ToolEntry, ToolSpec

from .utils import callTool

from .get       import _TOOLS as _GET_TOOLS
from .block     import _TOOLS as _BLOCK_TOOLS
from .block_pin import _TOOLS as _BLOCK_PIN_TOOLS

# Aggregate tool modules here (each module defines _TOOLS and registers via @aitool).
_TOOLS : list[ToolEntry] = []

_TOOLS.extend(_GET_TOOLS)
_TOOLS.extend(_BLOCK_TOOLS)
_TOOLS.extend(_BLOCK_PIN_TOOLS)


def allToolSpecs() -> Iterator[ToolSpec]:
    for entry in _TOOLS:
        yield entry.spec


def writeToolNames() -> frozenset[str]:
    return frozenset(
        entry.spec.name
        for entry in _TOOLS
        if entry.write
    )


__all__ = [
    "allToolSpecs",
    "callTool",
    "writeToolNames",
]
