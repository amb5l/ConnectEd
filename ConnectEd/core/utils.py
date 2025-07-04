__all__ = [
    "NameCounter",
    "check",
    "camel_to_proper",
    "getDefaultPath",
    "val2str",
    "str2val"
]

import os, platform

from typing import Self, Any

from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtGui  import QColor

class NameCounter:
    counts : dict[str, int]

    def __init__(self : Self) -> None:
        self.counts = {}

    def get(self : Self, name : str) -> str:
        if name not in self.counts:
            self.counts[name] = 0
        self.counts[name] += 1
        return f"{name}{self.counts[name]}"

def check(b : bool, s : str) -> bool:
    if not b:
        print(s)
    return b

def camel_to_proper(s : str) -> str:
    r = []
    for i, char in enumerate(s):
        if i == 0:
            r.append(char.upper())
        else:
            if char.isupper():
                r.append(" ")
            r.append(char)
    return "".join(r)

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
        case "bytes"           : s = v.hex()
        case "str"             : s = v # TODO escape special characters
        case "int"             : s = str(v)
        case "float"           : s = str(v)
        case "bool"            : s = str(v)
        case "QPointF"         : s = f"{v.x()},{v.y()}"
        case "QRectF"          : s = f"{v.x()},{v.y()},{v.width()},{v.height()}"
        case "QSizeF"          : s = f"{v.width()},{v.height()}"
        case "QColor"          : s = hex(v.rgba())
        case "PenStyle"        : s = str(v).replace("PenStyle.", "")
        case "BrushStyle"      : s = str(v).replace("BrushStyle.", "")
        case "LinePref"        : s = v.toStr()
        case "FillPref"        : s = v.toStr()
        case "TextPref"        : s = v.toStr()
        case "PropertyDisplay" : s = v.value
        case "KP"              : s = v.value.name
        case _ :
            raise ValueError(f"Unsupported type: {t}")
    return s

def str2val(s : str, t : str) -> Any:
    """Convert a text representation of a Python value to a Python value."""
    from ..widgets import TextPref, LinePref, FillPref, \
                          PropertyDisplay, KPReverse
    def strValuesToFloats(s : str) -> list[float]:
        return [float(p) for p in s.strip("()").split(",")]
    if s == "None":
        return None
    match t:
        case "NoneType"        : return None
        case "bytes"           : return bytes.fromhex(s)
        case "str"             : return s # TODO unescape special characters
        case "int"             : return int(s)
        case "float"           : return float(s)
        case "bool"            : return s == "True"
        case "QPointF"         : return QPointF(*strValuesToFloats(s))
        case "QRectF"          : return QRectF(*strValuesToFloats(s))
        case "QSizeF"          : return QSizeF(*strValuesToFloats(s))
        case "QColor"          : return QColor.fromRgba(int(s,0))
        case "PenStyle"        : return Qt.PenStyle[s]
        case "BrushStyle"      : return Qt.BrushStyle[s]
        case "TextPref"        : return TextPref.fromStr(s)
        case "LinePref"        : return LinePref.fromStr(s)
        case "FillPref"        : return FillPref.fromStr(s)
        case "PropertyDisplay" : return PropertyDisplay(s)
        case "KP"              : return KPReverse[s]
        case _:
            raise ValueError(f"Unsupported type: {t}")
