import os
import platform
import inspect
import importlib
import re

from typing import Any, TypeVar

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


def typeCheck(x : Any, t : type) -> None:
    # get name of calling function/method
    frame = inspect.currentframe().f_back
    func_name = frame.f_code.co_name
    if not isinstance(x, t):
        logger().warning(f"Type {type(x)} does not match {t} ({func_name})")
        return False
    return True


T = TypeVar('T')

def getItemOfType(
    items : list[Any],
    types : type[T] | tuple[type[T], ...]
) -> T | None:
    """Get the first item of the specified type."""
    types = (types,) if isinstance(types, type) else types
    for t in types:
        item = next((item for item in items if isinstance(item, t)), None)
        if item is not None:
            return item
    return None


def itemsTypeDict(items : list[Any]) -> dict[type, list[Any]]:
    """Group items by their type."""
    result: defaultdict[type, list[Any]] = defaultdict(list)
    for item in items:
        result[type(item)].append(item)
    return dict(result)


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
        case "DisplayChoice"   : s = v.value
        case "PenStyle"        : s = str(v).replace("PenStyle.", "")
        case "BrushStyle"      : s = str(v).replace("BrushStyle.", "")
        case "LinePref"        : s = v.toStr()
        case "FillPref"        : s = v.toStr()
        case "TextPref"        : s = v.toStr()
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
    from ..widgets.graphics.items import \
        DEFAULT, Edge, EdgeLoc, SignalDirection, LinePref, FillPref, QuillPref
    from ..widgets.dialogs.properties import DisplayChoice
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
        case "DisplayChoice"   : return DisplayChoice(s)
        case "PenStyle"        : return Qt.PenStyle[s]
        case "BrushStyle"      : return Qt.BrushStyle[s]
        case "TextPref"        : return QuillPref.fromStr(s)
        case "LinePref"        : return LinePref.fromStr(s)
        case "FillPref"        : return FillPref.fromStr(s)
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
        mod_name = pascal2snake(cls_name)
    if pkg is None:
        caller_frame = inspect.stack()[1].frame
        pkg = caller_frame.f_globals.get('__name__')
    module = importlib.import_module(f".{mod_name}", package=pkg)
    cls = getattr(module, cls_name)
    registry[cls_name] = cls
