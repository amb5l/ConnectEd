__all__ = ['toXmlBegin', 'toXmlEnd', 'saveBegin', 'saveEnd', 'copy']

from typing import Any

from PyQt6.QtCore    import QByteArray, QXmlStreamWriter, QFile, QIODevice
from PyQt6.QtWidgets import QApplication


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
