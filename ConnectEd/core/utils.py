__all__ = [
    'NameCounter',
    'check',
    'getDefaultPath',
    'value2str',
    'copy',
    'toXmlBegin',
    'toXmlEnd',
    'saveBegin',
    'saveEnd'
]

import os
import platform

from collections import namedtuple
from typing      import Any

from PyQt6.QtCore    import Qt, QPointF, QSizeF, QByteArray, \
                            QXmlStreamWriter, QFile, QIODevice
from PyQt6.QtWidgets import QApplication
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
        case 'str'        : valueStr = v
        case 'int'        : valueStr = str(v)
        case 'float'      : valueStr = str(v)
        case 'bool'       : valueStr = str(v)
        case 'MinMax'     : valueStr = f'({v.min},{v.max})'
        case 'QPointF'    : valueStr = f'({v.x()},{v.y()})'
        case 'QRectF'     : valueStr = f'({v.x()},{v.y()},{v.width()},{v.height()})'
        case 'QSize'      : valueStr = f'({v.width()},{v.height()})'
        case 'QSizeF'     : valueStr = f'({v.width()},{v.height()})'
        case 'QColor'     : valueStr = hex(v.rgba())
        case 'PenStyle'   : valueStr = str(v).replace('PenStyle.', '')
        case 'BrushStyle' : valueStr = str(v).replace('BrushStyle.', '')
        case 'KeyPoint'   : valueStr = str(v).replace('KeyPoint.', '')
        case _ :
            raise ValueError(f'Unsupported type: {typeName}')
    return typeName + ':' + valueStr


def str2value(s : str) -> Any:
    """Inverse of value2str."""
    from ..widgets.elements import KeyPoint
    if not isinstance(s, str):
        return s
    try:
        typeName, valueStr = s.split(':', 1)
    except ValueError:
        return s
    match typeName:
        case 'NoneType'   : return None
        case 'bytes'      : return bytes.fromhex(valueStr)
        case 'str'        : return valueStr
        case 'int'        : return int(valueStr)
        case 'float'      : return float(valueStr)
        case 'bool'       : return valueStr == 'True'
        case 'MinMax'     : return MinMax(*map(float, valueStr[1:-1].split(',')))
        case 'QPointF'    : return QPointF(*map(float, valueStr[1:-1].split(',')))
        case 'QSizeF'     : return QSizeF(*map(float, valueStr[1:-1].split(',')))
        case 'QColor'     : return QColor.fromRgba(int(valueStr,0))
        case 'PenStyle'   : return Qt.PenStyle[valueStr]
        case 'BrushStyle' : return Qt.BrushStyle[valueStr]
        case 'KeyPoint'   : return KeyPoint[valueStr]
        case _:
            raise ValueError(f'Unsupported type: {typeName}')

def toXmlBegin(xw : QXmlStreamWriter) -> None:
    xw.setAutoFormatting(True)
    xw.setAutoFormattingIndent(2)
    xw.writeStartDocument()

def toXmlEnd(xw : QXmlStreamWriter) -> None:
    xw.writeEndDocument()

def saveBegin(path : str) -> tuple[QXmlStreamWriter, QFile]:
    file = QFile(path)
    if file.open(QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Text):
        xw = QXmlStreamWriter(file)
        toXmlBegin(xw)
        xw.writeStartElement('ConnectEd') # TODO: version
        return xw, file

def saveEnd(xw : QXmlStreamWriter, file : QFile) -> None:
    xw.writeEndElement() # ConnectEd
    toXmlEnd(xw)
    file.close()

def copy(instance : Any) -> None:
    buffer = QByteArray()
    xw = QXmlStreamWriter(buffer)
    toXmlBegin(xw)
    instance.toXml(xw)
    toXmlEnd(xw)
    clipboard = QApplication.clipboard()
    clipboard.setText(buffer.data().decode('utf-8'))
