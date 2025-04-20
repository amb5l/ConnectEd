__all__ = [
    'NameCounter',
    'check',
    'camel_to_proper',
    'getDefaultPath',
    'val2str',
    'str2val'
]

import os
import platform

from collections import namedtuple
from typing      import Self, Any

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtGui     import QColor


MinMax = namedtuple('MinMax', ['min', 'max'])

class NameCounter:
    counts : dict[str, int]

    def __init__(self : Self) -> None:
        self.counts = {}

    def get(self : Self, name : str) -> str:
        if name not in self.counts:
            self.counts[name] = 0
        self.counts[name] += 1
        return f'{name}{self.counts[name]}'

def check(b : bool, s : str) -> bool:
    if not b:
        print(s)
    return b

def camel_to_proper(s : str) -> str:
    r = []
    for i, char in enumerate(s):
        if i > 0 and char.isupper():
            r.append(' ')
        r.append(char)
    return ''.join(r).capitalize()

def getDefaultPath() -> str:
    if platform.system() == 'Windows':
        if 'WORK' in os.environ:
            r = os.environ['WORK']
        elif 'USERPROFILE' in os.environ:
            r = os.environ['USERPROFILE']
        elif 'HOMEPATH' in os.environ:
            r = os.environ['HOMEPATH']
        elif 'HOMEDRIVE' in os.environ:
            r = os.environ['HOMEDRIVE']
        else:
            r = 'C:/'
    else:
        if 'WORK' in os.environ:
            r = os.environ['WORK']
        else:
            r = '~'
    return r

def val2str(v : Any) -> str:
    """Convert a Python value to a text representation."""
    t = type(v).__name__
    match t:
        case 'NoneType'   : s = 'None'
        case 'bytes'      : s = v.hex()
        case 'str'        : s = v # TODO escape special characters
        case 'int'        : s = str(v)
        case 'float'      : s = str(v)
        case 'bool'       : s = str(v)
        case 'MinMax'     : s = f'{v.min},{v.max}'
        case 'QPointF'    : s = f'{v.x()},{v.y()}'
        case 'QRectF'     : s = f'{v.x()},{v.y()},{v.width()},{v.height()}'
        case 'QSizeF'     : s = f'{v.width()},{v.height()}'
        case 'QColor'     : s = hex(v.rgba())
        case 'PenStyle'   : s = str(v).replace('PenStyle.', '')
        case 'BrushStyle' : s = str(v).replace('BrushStyle.', '')
        case 'PenSpec'    : s = f'{v.color},{v.width},{v.style}'
        case 'BrushSpec'  : s = f'{v.color},{v.style}'
        case 'TextSpec'   : s = f'{v.color},{v.family},{v.size},{v.weight},{v.italic},{v.underline}'
        case 'KeyPoint'   : s = str(v).replace('KeyPoint.', '')
        case _ :
            raise ValueError(f'Unsupported type: {t}')
    return s

def str2val(s : str, t : str) -> Any:
    """Convert a text representation of a Python value to a Python value."""
    from ..widgets.elements import KeyPoint, PenSpec, BrushSpec, TextSpec
    def strValuesToFloats(s : str) -> list[float]:
        return [float(p) for p in s.strip('()').split(',')]
    match t:
        case 'NoneType'   : return None
        case 'str'        : return s # TODO unescape special characters
        case 'int'        : return int(s)
        case 'float'      : return float(s)
        case 'bool'       : return s == 'True'
        case 'MinMax'     : return MinMax(*strValuesToFloats(s))
        case 'QPointF'    : return QPointF(*strValuesToFloats(s))
        case 'QRectF'     : return QRectF(*strValuesToFloats(s))
        case 'QSizeF'     : return QSizeF(*strValuesToFloats(s))
        case 'QColor'     : return QColor.fromRgba(int(s,0))
        case 'PenStyle'   : return Qt.PenStyle[s]
        case 'BrushStyle' : return Qt.BrushStyle[s]
        case 'PenSpec'    :
            params = s.split(',')
            color = None if params[0] == 'None' else QColor.fromRgba(int(params[0], 0))
            width = None if params[1] == 'None' else float(params[1])
            style = None if params[2] == 'None' else Qt.PenStyle[params[2]]
            return PenSpec(color, width, style)
        case 'BrushSpec'  :
            params = s.split(',')
            color = None if params[0] == 'None' else QColor.fromRgba(int(params[0], 0))
            style = None if params[1] == 'None' else Qt.BrushStyle[params[1]]
            return BrushSpec(color, style)
        case 'TextSpec'   :
            params = s.split(',')
            family    = None if params[1] == 'None' else params[1]
            size      = None if params[2] == 'None' else float(params[2])
            weight    = None if params[3] == 'None' else int(params[3])
            italic    = None if params[4] == 'None' else params[4] == 'True'
            underline = None if params[5] == 'None' else params[5] == 'True'
            return TextSpec(color, family, size, weight, italic, underline)
        case 'KeyPoint'   : return KeyPoint[s]
        case _:
            raise ValueError(f'Unsupported type: {s}')
