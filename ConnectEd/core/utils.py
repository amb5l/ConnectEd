__all__ = [
    'NameCounter',
    'check',
    'getDefaultPath',
    'value2str',
    'copy',
    'xmlBegin',
    'xmlEnd',
    'saveBegin',
    'saveEnd'
]

import os
import platform

from typing import Any

from PyQt6.QtCore    import QByteArray, QXmlStreamWriter, QFile, QIODevice
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

def value2str(v : Any) -> str:
    """Convert a Python value to a text representation for QSettings."""
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
        case _ :
            raise ValueError(f'Unsupported type: {typeName}')
    return typeName + ':' + valueStr

def xmlBegin(xw : QXmlStreamWriter) -> None:
    xw.setAutoFormatting(True)
    xw.setAutoFormattingIndent(2)
    xw.writeStartDocument()

def xmlEnd(xw : QXmlStreamWriter) -> None:
    xw.writeEndDocument()

def saveBegin(path : str) -> tuple[QXmlStreamWriter, QFile]:
    file = QFile(path)
    if file.open(QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Text):
        xw = QXmlStreamWriter(file)
        xmlBegin(xw)
        xw.writeStartElement('ConnectEd') # TODO: version
        return xw, file

def saveEnd(xw : QXmlStreamWriter, file : QFile) -> None:
    xw.writeEndElement() # ConnectEd
    xmlEnd(xw)
    file.close()

def copy(instance : Any) -> None:
    buffer = QByteArray()
    xw = QXmlStreamWriter(buffer)
    xmlBegin(xw)
    instance.toXml(xw)
    xmlEnd(xw)
    clipboard = QApplication.clipboard()
    clipboard.setText(buffer.data().decode('utf-8'))
