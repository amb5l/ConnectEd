import os, platform

from typing import Any, TypeVar

from collections import defaultdict

from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtGui  import QColor


sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)


def check(b : bool, s : str) -> bool:
    if not b:
        print(s)
    return b


T = TypeVar('T')

def getItemOfType(items: list[Any], types: type[T] | tuple[type[T], ...]) -> T | None:
    """Get the first item of the specified type."""
    types = (types,) if isinstance(types, type) else types
    for t in types:
        item = next((item for item in items if isinstance(item, t)), None)
        if item is not None:
            return item
    return None


def itemsTypeDict(items: list[Any]) -> dict[type, list[Any]]:
    """Group items by their type."""
    result: defaultdict[type, list[Any]] = defaultdict(list)
    for item in items:
        result[type(item)].append(item)
    return dict(result)


def camel2proper(s : str) -> str:
    """FooBar -> Foo Bar"""
    r = []
    for i, char in enumerate(s):
        if i == 0:
            r.append(char.upper())
        else:
            if char.isupper():
                r.append(" ")
            r.append(char)
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
        case "float"           : s = str(v)
        case "bool"            : s = str(v)
        case "QPointF"         : s = f"{v.x()},{v.y()}"
        case "QRectF"          : s = f"{v.x()},{v.y()},{v.width()},{v.height()}"
        case "QSizeF"          : s = f"{v.width()},{v.height()}"
        case "QColor"          : s = f"#{(v.rgb() & 0xFFFFFF):06X}"
        case "PenStyle"        : s = str(v).replace("PenStyle.", "")
        case "BrushStyle"      : s = str(v).replace("BrushStyle.", "")
        case "LinePref"        : s = v.toStr()
        case "FillPref"        : s = v.toStr()
        case "TextPref"        : s = v.toStr()
        case "PropertyDisplay" : s = v.value
        case "APLoc"           : s = v
        case "EdgeLoc"         : s = v.toStr()
        case "SignalDirection" : s = v.value
        case _ :
            raise ValueError(f"Unsupported type: {t}")
    return s


def str2val(s : str, t : str) -> Any:
    """Convert a text representation of a Python value to a Python value."""
    from ..widgets.graphics.items import \
        DEFAULT, EdgeLoc, SignalDirection, LinePref, FillPref, QuillPref
    from ..widgets.graphics.items.property_text import PropertyDisplay
    def strValuesToFloats(s : str) -> list[float]:
        return [float(p) for p in s.strip("()").split(",")]
    if s == "None":
        return None
    elif s == "default":
        return DEFAULT
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
        case "PenStyle"        : return Qt.PenStyle[s]
        case "BrushStyle"      : return Qt.BrushStyle[s]
        case "TextPref"        : return QuillPref.fromStr(s)
        case "LinePref"        : return LinePref.fromStr(s)
        case "FillPref"        : return FillPref.fromStr(s)
        case "PropertyDisplay" : return PropertyDisplay(s)
        case "APLoc"           : return "not implemented"
        case "EdgeLoc"         : return EdgeLoc.fromStr(s)
        case "SignalDirection" : return SignalDirection(s)
        case _:
            raise ValueError(f"Unsupported type: {t}")
