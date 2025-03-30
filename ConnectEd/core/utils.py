__all__ = [
    'NameCounter',
    'check',
    'getDefaultPath',
    'value2str',
    'copy',
    'saveBegin',
    'saveEnd',
    'xmlBegin',
    'xmlEnd'
]

import os
import platform

from typing import Any

from PyQt6.QtCore    import QByteArray, QXmlStreamWriter
from PyQt6.QtWidgets import QApplication


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

def value2str(value : Any) -> str:
    """Convert a Python value to a text representation for QSettings."""
    typeName = type(value).__name__
    match typeName:
        case 'NoneType'   : valueStr = 'None'
        case 'bytes'      : valueStr = value.hex()
        case 'str'        : valueStr = value
        case 'int'        : valueStr = str(value)
        case 'float'      : valueStr = str(value)
        case 'bool'       : valueStr = str(value)
        case 'MinMax'     : valueStr = f'({value.min},{value.max})'
        case 'QPointF'    : valueStr = f'({value.x()},{value.y()})'
        case 'QSize'      : valueStr = f'({value.width()},{value.height()})'
        case 'QSizeF'     : valueStr = f'({value.width()},{value.height()})'
        case 'QColor'     : valueStr = hex(value.rgba())
        case 'PenStyle'   : valueStr = str(value).replace('PenStyle.', '')
        case 'BrushStyle' : valueStr = str(value).replace('BrushStyle.', '')
        case _ :
            raise ValueError(f'Unsupported type: {typeName}')
    return typeName + ':' + valueStr

def xmlBegin(xw : QXmlStreamWriter) -> None:
    xw.setAutoFormatting(True)
    xw.setAutoFormattingIndent(2)
    xw.writeStartDocument()

def xmlEnd(xw : QXmlStreamWriter) -> None:
    xw.writeEndDocument()

def copy(instance : Any) -> None:
    buffer = QByteArray()
    xw = QXmlStreamWriter(buffer)
    xmlBegin(xw)
    instance.toXml(xw)
    xmlEnd(xw)
    clipboard = QApplication.clipboard()
    clipboard.setText(buffer.data().decode('utf-8'))

def saveBegin(path : str) -> QXmlStreamWriter:
    xw = QXmlStreamWriter(path)
    xmlBegin(xw)
    return xw

def saveEnd(xw : QXmlStreamWriter) -> None:
    xmlEnd(xw)
