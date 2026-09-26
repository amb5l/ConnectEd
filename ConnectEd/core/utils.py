import os
import platform
import inspect
import importlib
import re

from typing      import Any
from collections import defaultdict

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor

from .check import checked


def qtItemClass(self : object) -> type[QGraphicsItem]:
    for cls in type(self).__mro__:
        if cls.__module__.startswith("PyQt6.") and issubclass(cls, QGraphicsItem):
            return cls
    raise TypeError("No QGraphicsItem base")


def sign(x):
    """Return -1, 0, or 1 based on sign of x."""
    return -1 if x < 0 else (1 if x > 0 else 0)


@checked
def space2underscore(s : str) -> str:
    """Foo Bar -> Foo_Bar"""
    return s.replace(" ", "_")


@checked
def underscore2space(s : str) -> str:
    """Foo_Bar -> Foo Bar"""
    return s.replace("_", " ")


@checked
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


@checked
def pascal2proper(s : str) -> str:
    """FooBar -> Foo Bar"""
    r = []
    for i, char in enumerate(s):
        if i > 0 and char.isupper():
            r.append(" ")
        r.append(char)
    return "".join(r)


def cleanPath(path: str) -> str:
    path = path.strip()
    if path == "":
        return ""
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))


@checked
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


@checked
def numtrim(n : int | float) -> str:
    """Text form of a number, without a trailing ``.0`` on a whole value."""
    if isinstance(n, float) and n.is_integer():
        return str(int(n))
    return str(n)


@checked
def val2str(v : Any) -> str:
    """Convert a value to its XML / settings text form."""
    t = type(v).__name__
    match t:
        case "NoneType"          : s = "None"
        case "bytes"             : s = v.hex()
        case "str"               : s = v # TODO escape special characters
        case "int"               : s = str(v)
        case "float"             : s = numtrim(v)
        case "bool"              : s = str(v)
        case "QPointF"           : s = f"{numtrim(v.x())},{numtrim(v.y())}"
        case "QRectF"            : s = f"{numtrim(v.x())},{numtrim(v.y())},{numtrim(v.width())},{numtrim(v.height())}"
        case "QSizeF"            : s = f"{numtrim(v.width())},{numtrim(v.height())}"
        case "QColor"            : s = f"#{(v.rgb() & 0xFFFFFF):06X}"
        case "Display"           : s = v.value
        case "PenStyle"          : s = str(v).replace("PenStyle.", "")
        case "BrushStyle"        : s = str(v).replace("BrushStyle.", "")
        case "AlignH"            : s = v.toStr()
        case "AlignV"            : s = v.toStr()
        case "Edge"              : s = v.value
        case "Direction"         : s = v.value
        case "RectHandleId"      : s = v.value
        case "LineHandleId"      : s = v.value
        case "PortHandleId"      : s = v.value
        case "BlockPinHandleId"  : s = v.value
        case "SymbolPinHandleId" : s = v.value
        case "DataKind"          : s = v.value
        case _ :
            raise ValueError(f"Unsupported type: {t}")
    return s


@checked
def str2val(s : str, t : str) -> Any:
    """Parse XML / settings text produced by val2str."""
    from ..core.types import (
        AlignH, AlignV, Edge, Direction, DataKind,
        RectHandleId, LineHandleId, PortHandleId,
        BlockPinHandleId, SymbolPinHandleId
    )
    def strValuesToFloats(s : str) -> list[float]:
        return [float(p) for p in s.strip("()").split(",")]
    if s == "None":
        return None
    match t:
        case "bytes"             : return bytes.fromhex(s)
        case "str"               : return s # TODO unescape special characters
        case "int"               : return int(s)
        case "float"             : return float(s)
        case "bool"              : return s == "True"
        case "QPointF"           : return QPointF(*strValuesToFloats(s))
        case "QRectF"            : return QRectF(*strValuesToFloats(s))
        case "QSizeF"            : return QSizeF(*strValuesToFloats(s))
        case "QColor"            : return QColor.fromRgb(int(s[1:], 16) | 0xFF000000)
        case "PenStyle"          : return Qt.PenStyle[s]
        case "BrushStyle"        : return Qt.BrushStyle[s]
        case "AlignH"            : return AlignH.fromStr(s)
        case "AlignV"            : return AlignV.fromStr(s)
        case "Edge"              : return Edge(s)
        case "Direction"         : return Direction(s)
        case "RectHandleId"      : return RectHandleId(s)
        case "LineHandleId"      : return LineHandleId(s)
        case "PortHandleId"      : return PortHandleId(s)
        case "BlockPinHandleId"  : return BlockPinHandleId(s)
        case "SymbolPinHandleId" : return SymbolPinHandleId(s)
        case "DataKind"          : return DataKind(s)
        case _:
            raise ValueError(f"Unsupported type: {t}")


