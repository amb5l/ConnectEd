from PyQt6.QtCore import QDataStream, QXmlStreamWriter
import types

def to_xml(name, value, writer: QXmlStreamWriter):
    t = type(value).__name__
    match t:
        case 'int' | 'float' | 'str':
            writer.writeStartElement(name)
            writer.writeCharacters(str(value))
            writer.writeEndElement()
        case 'QPointF':
            writer.writeStartElement(name)
            to_xml('x', value.x(), writer)
            to_xml('y', value.y(), writer)
            writer.writeEndElement()
        case 'QRectF':
            writer.writeStartElement(name)
            to_xml('topLeft', value.topLeft(), writer)
            to_xml('bottomRight', value.bottomRight(), writer)
            writer.writeEndElement()
        case 'dict':
            writer.writeStartElement(name)
            to_xml('len', len(value), writer)
            for k, v in value.items():
                to_xml(k, v, writer)
            writer.writeEndElement()
