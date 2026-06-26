from __future__ import annotations

import json
import sys

from functools       import wraps
from typing          import TYPE_CHECKING, Any
from collections.abc import Callable
from types           import ModuleType

from ...core.check import checked

from ..types import ToolSpec, ToolEntry
from ..refs  import RefRegistry

if TYPE_CHECKING:
    from ...widgets.window import Window


def _toolsForModule(module : ModuleType) -> list[ToolEntry]:
    tools = getattr(module, "_TOOLS", None)
    if tools is None:
        tools = []
        module._TOOLS = tools
    return tools


def parseToolArgs(
    arguments  : dict[str, Any],
    parameters : dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    """Validate ``required`` keys from an OpenAPI-style tool parameter object."""
    required   = parameters.get("required") or []
    properties = parameters.get("properties") or {}
    values     : dict[str, Any] = {}
    for key in required:
        prop  = properties.get(key, {})
        typ   = prop.get("type", "string")
        value = arguments.get(key)
        if typ == "string":
            if not value or not isinstance(value, str):
                return None, toolError(f"{key} is required")
            values[key] = value
        elif typ == "number":
            if not isinstance(value, (int, float)):
                return None, toolError(f"{key} is required")
            values[key] = float(value)
        elif typ == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                return None, toolError(f"{key} is required")
            values[key] = value
        elif typ == "boolean":
            if not isinstance(value, bool):
                return None, toolError(f"{key} is required")
            values[key] = value
        elif typ == "array":
            if not isinstance(value, list) or not value:
                return None, toolError(f"{key} is required")
            values[key] = value
        elif typ == "object":
            if not isinstance(value, dict):
                return None, toolError(f"{key} is required")
            values[key] = value
        else:
            raise TypeError(f"parseToolArgs: unsupported type {typ!r} for {key!r}")
    for key, prop in properties.items():
        if key in values:
            continue
        if key not in arguments:
            continue
        value = arguments[key]
        if value is None:
            continue
        typ = prop.get("type", "string")
        if typ == "string":
            if not isinstance(value, str) or not value:
                continue
            values[key] = value
        elif typ == "number":
            if not isinstance(value, (int, float)):
                continue
            values[key] = float(value)
        elif typ == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                continue
            values[key] = value
        elif typ == "boolean":
            if not isinstance(value, bool):
                continue
            values[key] = value
        elif typ == "array":
            if not isinstance(value, list):
                return None, toolError(f"{key} must be an array")
            values[key] = value
        elif typ == "object":
            if not isinstance(value, dict):
                continue
            values[key] = value
    return values, None


def aitool(
    description : str,
    parameters  : dict,
    *,
    write       : bool = False,
) -> Callable:
    def decorate(fn : Callable) -> Callable:
        spec = ToolSpec(
            name        = fn.__name__,
            description = description,
            parameters  = parameters,
        )

        @wraps(fn)
        def wrapper(
            window    : Window,
            registry  : RefRegistry,
            arguments : dict[str, Any],
        ) -> str:
            args, err = parseToolArgs(arguments, parameters)
            if err is not None:
                return err
            return fn(window, registry, args)

        module = sys.modules.get(fn.__module__)
        if module is None:
            raise RuntimeError(f"Cannot resolve module for {fn.__name__!r}")
        _toolsForModule(module).append(ToolEntry(spec, wrapper, write=write))
        return wrapper
    return decorate


def toolError(message : str) -> str:
    return json.dumps({
        "ok"    : False,
        "error" : message,
    })


def toolOk(**fields : Any) -> str:
    return json.dumps({
        "ok" : True,
        **fields,
    })


@checked
def callTool(
    name       : str,
    window     : Window,
    registry   : RefRegistry,
    arguments  : dict[str, Any],
) -> str:
    from . import _TOOLS
    for entry in _TOOLS:
        if entry.spec.name == name:
            return entry.fn(window, registry, arguments)
    raise ValueError(f"Unknown AI tool: {name!r}")
