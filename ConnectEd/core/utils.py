__all__ = [
    'NameCounter',
    'check',
    'getDefaultPath',
    'value2str',
    'str2value'
]

import os
import platform

from collections import namedtuple
from typing      import Any

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtGui     import QColor


MinMax = namedtuple('MinMax', ['min', 'max'])

class NameCounter:
    counts : dict[str, int]

    def __init__(self):
        self.counts = {}

    def get(self, name : str) -> str:
        if name not in self.counts:
            self.counts[name] = 0
        self.counts[name] += 1
        return f'{name}{self.counts[name]}'

def check(b : bool, s : str) -> bool:
    if not b:
        print(s)
    return b

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

def value2str(v : Any) -> str:
    """Convert a Python value to a text representation."""
    typeName = type(v).__name__
    match typeName:
        case 'NoneType'   : valueStr = 'None'
        case 'bytes'      : valueStr = v.hex()
        case 'str'        : valueStr = v # TODO escape special characters
        case 'int'        : valueStr = str(v)
        case 'float'      : valueStr = str(v)
        case 'bool'       : valueStr = str(v)
        case 'MinMax'     : valueStr = f'({v.min},{v.max})'
        case 'QPointF'    : valueStr = f'({v.x()},{v.y()})'
        case 'QRectF'     : valueStr = f'({v.x()},{v.y()},{v.width()},{v.height()})'
        case 'QSizeF'     : valueStr = f'({v.width()},{v.height()})'
        case 'QColor'     : valueStr = hex(v.rgba())
        case 'PenStyle'   : valueStr = str(v).replace('PenStyle.', '')
        case 'BrushStyle' : valueStr = str(v).replace('BrushStyle.', '')
        case 'PenSpec'    : valueStr = f'({v.color},{v.width},{v.style})'
        case 'BrushSpec'  : valueStr = f'({v.color},{v.style})'
        case 'TextSpec'   : valueStr = f'({v.color},{v.family},{v.size},{v.weight},{v.italic},{v.underline})'
        case 'KeyPoint'   : valueStr = str(v).replace('KeyPoint.', '')
        case _ :
            raise ValueError(f'Unsupported type: {typeName}')
    return typeName + ':' + valueStr


def str2value(s : str) -> Any:
    """Inverse of value2str."""
    from ..widgets.elements import KeyPoint, PenSpec, BrushSpec, TextSpec
    def strValuesToFloats(s : str) -> list[float]:
        return [float(p) for p in s.strip('()').split(',')]
    if not isinstance(s, str): # TODO review this
        return s
    try:
        typeName, valueStr = s.split(':', 1)
    except ValueError:
        return s
    match typeName:
        case 'NoneType'   : return None
        case 'bytes'      : return bytes.fromhex(valueStr)
        case 'str'        : return valueStr # TODO unescape special characters
        case 'int'        : return int(valueStr)
        case 'float'      : return float(valueStr)
        case 'bool'       : return valueStr == 'True'
        case 'MinMax'     : return MinMax(*strValuesToFloats(valueStr))
        case 'QPointF'    : return QPointF(*strValuesToFloats(valueStr))
        case 'QRectF'     : return QRectF(*strValuesToFloats(valueStr))
        case 'QSizeF'     : return QSizeF(*strValuesToFloats(valueStr))
        case 'QColor'     : return QColor.fromRgba(int(valueStr,0))
        case 'PenStyle'   : return Qt.PenStyle[valueStr]
        case 'BrushStyle' : return Qt.BrushStyle[valueStr]
        case 'PenSpec'    :
            params = valueStr.strip('()').split(',')
            # Handle the case when some params are None
            color = None if params[0] == 'None' else QColor.fromRgba(int(params[0], 0))
            width = None if params[1] == 'None' else float(params[1])
            style = None if params[2] == 'None' else Qt.PenStyle[params[2]]
            return PenSpec(color, width, style)
        case 'BrushSpec'  :
            params = valueStr.strip('()').split(',')
            # Handle the case when some params are None
            color = None if params[0] == 'None' else QColor.fromRgba(int(params[0], 0))
            style = None if params[1] == 'None' else Qt.BrushStyle[params[1]]
            return BrushSpec(color, style)
        case 'TextSpec'   :
            params = valueStr.strip('()').split(',')
            # Handle the case when some params are None
            color     = None if params[0] == 'None' else QColor.fromRgba(int(params[0], 0))
            family    = None if params[1] == 'None' else params[1]
            size      = None if params[2] == 'None' else float(params[2])
            weight    = None if params[3] == 'None' else int(params[3])
            italic    = None if params[4] == 'None' else params[4] == 'True'
            underline = None if params[5] == 'None' else params[5] == 'True'
            return TextSpec(color, family, size, weight, italic, underline)
        case 'KeyPoint'   : return KeyPoint[valueStr]
        case _:
            raise ValueError(f'Unsupported type: {typeName}')

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
        case 'MinMax'     : s = f'({v.min},{v.max})'
        case 'QPointF'    : s = f'({v.x()},{v.y()})'
        case 'QRectF'     : s = f'({v.x()},{v.y()},{v.width()},{v.height()})'
        case 'QSizeF'     : s = f'({v.width()},{v.height()})'
        case 'QColor'     : s = hex(v.rgba())
        case 'PenStyle'   : s = str(v).replace('PenStyle.', '')
        case 'BrushStyle' : s = str(v).replace('BrushStyle.', '')
        case 'PenSpec'    : s = f'({v.color},{v.width},{v.style})'
        case 'BrushSpec'  : s = f'({v.color},{v.style})'
        case 'TextSpec'   : s = f'({v.color},{v.family},{v.size},{v.weight},{v.italic},{v.underline})'
        case 'KeyPoint'   : s = str(v).replace('KeyPoint.', '')
        case _ :
            raise ValueError(f'Unsupported type: {t}')
    return s

def str2val(s : str, t : str) -> Any:
    """Inverse of value2str."""
    from ..widgets.elements import KeyPoint, PenSpec, BrushSpec, TextSpec
    def strValuesToFloats(s : str) -> list[float]:
        return [float(p) for p in s.strip('()').split(',')]
    match t:
        case 'NoneType'   : return None
        case 'bytes'      : return bytes.fromhex(s)
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
            params = s.strip('()').split(',')
            # Handle the case when some params are None
            color = None if params[0] == 'None' else QColor.fromRgba(int(params[0], 0))
            width = None if params[1] == 'None' else float(params[1])
            style = None if params[2] == 'None' else Qt.PenStyle[params[2]]
            return PenSpec(color, width, style)
        case 'BrushSpec'  :
            params = s.strip('()').split(',')
            # Handle the case when some params are None
            color = None if params[0] == 'None' else QColor.fromRgba(int(params[0], 0))
            style = None if params[1] == 'None' else Qt.BrushStyle[params[1]]
            return BrushSpec(color, style)
        case 'TextSpec'   :
            params = s.strip('()').split(',')
            # Handle the case when some params are None
            color     = None if params[0] == 'None' else QColor.fromRgba(int(params[0], 0))
            family    = None if params[1] == 'None' else params[1]
            size      = None if params[2] == 'None' else float(params[2])
            weight    = None if params[3] == 'None' else int(params[3])
            italic    = None if params[4] == 'None' else params[4] == 'True'
            underline = None if params[5] == 'None' else params[5] == 'True'
            return TextSpec(color, family, size, weight, italic, underline)
        case 'KeyPoint'   : return KeyPoint[s]
        case _:
            raise ValueError(f'Unsupported type: {s}')
