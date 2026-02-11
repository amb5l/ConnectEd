import os
import platform
import inspect
import importlib
import re

from typing import Any, NamedTuple
from dataclasses import dataclass, fields

from collections import defaultdict

from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtGui  import QColor

from ..app import logger


def sign(x):
    """Return -1, 0, or 1 based on sign of x."""
    return -1 if x < 0 else (1 if x > 0 else 0)


def check(b : bool, s : str) -> bool:
    if not b:
        print(s)
    return b


def trace(
    depth  : int | None = None,
    full   : bool = False,
    module : bool = True,
    indent : bool = False,
    args   : bool = False
) -> None:
    """
    Print the call chain that led to this point.

    Args:
        depth:   Maximum number of frames to show (from caller upward). None = all.
        full:    Show full module path instead of just the last component.
        module:  Include the module name at all.
        indent:  If True, print vertically with increasing indentation instead of " <- ".
        args:    If True, show function arguments and their values.
    """
    stack = inspect.stack()
    # Skip this function itself
    frames = stack[1:depth + 1 if depth is not None else None]

    calls = []
    for frame in frames:                              # deepest call first
        func_name = frame.function
        mod = inspect.getmodule(frame.frame)
        mod_name = mod.__name__ if mod else "<unknown>"

        if not full:
            mod_name = mod_name.split(".")[-1]

        self_obj = frame.frame.f_locals.get("self")
        if self_obj is not None:
            cls_name = self_obj.__class__.__name__
            func_part = f"{cls_name}.{func_name}"
        # e.g. Processor.run
        else:
            func_part = func_name

        if args:
            # Get function arguments (excluding 'self')
            code = frame.frame.f_code
            arg_names = code.co_varnames[:code.co_argcount]
            arg_strs = []
            for name in arg_names:
                if name == "self":
                    continue
                if name in frame.frame.f_locals:
                    val = frame.frame.f_locals[name]
                    val_repr = repr(val)
                    if len(val_repr) > 50:
                        val_repr = val_repr[:47] + "..."
                    arg_strs.append(f"{name}={val_repr}")
            if arg_strs:
                func_part += f"({', '.join(arg_strs)})"
            else:
                func_part += "()"

        if module:
            calls.append(f"{mod_name}.{func_part}")
        else:
            calls.append(func_part)

    if indent:
        for i, call in enumerate(calls):
            print(" " * i + call)
    else:
        print(" <- ".join(calls))


def typeCheck(x : Any, t : type) -> None:
    # get name of calling function/method
    frame = inspect.currentframe().f_back
    func_name = frame.f_code.co_name
    if not isinstance(x, t):
        logger().warning(f"Type {type(x)} does not match {t} ({func_name})")
        return False
    return True


def itemsTypeDict(items : list[Any]) -> dict[type, list[Any]]:
    """Group items by their type."""
    result: defaultdict[type, list[Any]] = defaultdict(list)
    for item in items:
        result[type(item)].append(item)
    return dict(result)


def space2underscore(s : str) -> str:
    """Foo Bar -> Foo_Bar"""
    return s.replace(" ", "_")


def underscore2space(s : str) -> str:
    """Foo_Bar -> Foo Bar"""
    return s.replace("_", " ")


def camel2proper(s : str) -> str:
    """fooBar -> Foo Bar"""
    r = []
    for i, char in enumerate(s):
        if i == 0:
            r.append(char.upper())
        else:
            if char.isupper():
                r.append(" ")
            r.append(char)
    return "".join(r)


def pascal2snake(s : str) -> str:
    """FooBar -> foo_bar"""
    r = []
    for i, char in enumerate(s):
        if i > 0 and char.isupper():
            r.append("_")
        r.append(char.lower())
    return "".join(r)


def proper2snake(s : str) -> str:
    """Foo Bar -> foo_bar"""
    return s.replace(" ", "_").lower()


def snake2proper(s : str) -> str:
    """foo_bar -> Foo Bar"""
    return s.replace("_", " ").title()


def getDefaultPath() -> str:
    if platform.system() == "Windows":
        if "WORK" in os.environ:
            r = os.environ["WORK"]
        elif "USERPROFILE" in os.environ:
            r = os.environ["USERPROFILE"]
        elif "HOMEPATH" in os.environ:
            r = os.environ["HOMEPATH"]
        elif "HOMEDRIVE" in os.environ:
            r = os.environ["HOMEDRIVE"]
        else:
            r = "C:/"
    else:
        if "WORK" in os.environ:
            r = os.environ["WORK"]
        else:
            r = "~"
    return r


def val2str(v : Any) -> str:
    """Convert a Python value to a text representation."""
    t = type(v).__name__
    match t:
        case "NoneType"        : s = "None"
        case "Default"         : s = "default"
        case "bytes"           : s = v.hex()
        case "str"             : s = v # TODO escape special characters
        case "int"             : s = str(v)
        case "float"           : s = str(int(v)) if v.is_integer() else str(v)
        case "bool"            : s = str(v)
        case "QPointF"         : s = f"{v.x()},{v.y()}"
        case "QRectF"          : s = f"{v.x()},{v.y()},{v.width()},{v.height()}"
        case "QSizeF"          : s = f"{v.width()},{v.height()}"
        case "QColor"          : s = f"#{(v.rgb() & 0xFFFFFF):06X}"
        case "PropertyDisplay" : s = v.value
        case "PenStyle"        : s = str(v).replace("PenStyle.", "")
        case "BrushStyle"      : s = str(v).replace("BrushStyle.", "")
        case "AlignH"          : s = v.toStr()
        case "AlignV"          : s = v.toStr()
        case "Edge"            : s = v.value
        case "EdgeLoc"         : s = v.toStr()
        case "SignalDirection" : s = v.value
        case _ :
            raise ValueError(f"Unsupported type: {t}")
    return s


def str2val(s : str, t : str) -> Any:
    """
    Convert a text representation of a Python value to a Python value.
    Note: "subtypes" are substituted here; they exist to facilitate
    table view delegates.
    """
    from ..core.types import DEFAULT, AlignH, AlignV, Edge, EdgeLoc, SignalDirection
    from ..widgets.graphics.properties import PropertyDisplay
    def strValuesToFloats(s : str) -> list[float]:
        return [float(p) for p in s.strip("()").split(",")]
    # handle None
    if s == "None":
        return None
    # handle default
    elif s == "default":
        return DEFAULT
    # handle subtypes
    if t in ["FontFamily"]:
        t = "str"
    if t in ["LineWidth", "FontSize"]:
        t = "float"
    # convert
    match t:
        case "bytes"           : return bytes.fromhex(s)
        case "str"             : return s # TODO unescape special characters
        case "int"             : return int(s)
        case "float"           : return float(s)
        case "bool"            : return s == "True"
        case "QPointF"         : return QPointF(*strValuesToFloats(s))
        case "QRectF"          : return QRectF(*strValuesToFloats(s))
        case "QSizeF"          : return QSizeF(*strValuesToFloats(s))
        case "QColor"          : return QColor.fromRgb(int(s[1:], 16) | 0xFF000000)
        case "PropertyDisplay" : return PropertyDisplay(s)
        case "PenStyle"        : return Qt.PenStyle[s]
        case "BrushStyle"      : return Qt.BrushStyle[s]
        case "AlignH"          : return AlignH.fromStr(s)
        case "AlignV"          : return AlignV.fromStr(s)
        case "Edge"            : return Edge(s)
        case "EdgeLoc"         : return EdgeLoc.fromStr(s)
        case "SignalDirection" : return SignalDirection(s)
        case _:
            raise ValueError(f"Unsupported type: {t}")


def getCurlyBraceVariables(s : str) -> list[str]:
    """
    Get the substitution variables (names in curly braces) from a string.
    Curly braces may be escaped with a backslash; they may not be nested.
    """
    # Match {variable} where { is not escaped
    # The capture group handles escaped } inside by consuming \} as escaped char
    pattern = r'(?<!\\)\{((?:[^}\\]|\\.)+)\}'
    matches = re.findall(pattern, s)
    return matches


def registerClass(
    registry : dict[str, type[Any]],
    cls_name : str,
    mod_name : str | None = None,
    pkg      : str | None = None
) -> type[Any]:
    """Import a class from a module and register it in registry."""
    if mod_name is None:
        mod_name = pascal2snake(cls_name).replace("_item", "")
    if pkg is None:
        caller_frame = inspect.stack()[1].frame
        pkg = caller_frame.f_globals.get('__name__')
    module = importlib.import_module(f".{mod_name}", package=pkg)
    cls = getattr(module, cls_name)
    registry[cls_name] = cls
