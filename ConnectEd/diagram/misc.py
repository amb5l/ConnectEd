from PyQt6.QtCore import QSizeF, QXmlStreamWriter, QXmlStreamReader


class DiagramMiscMixin():
    def fromXml(name, reader: QXmlStreamReader):
        t = reader.attributes().value('type')
        v = reader.readElementText()
        match t:
            case 'int':
                return int(v)
            case 'float':
                return float(v)
            case 'str':
                return v
            case 'QSizeF':
                w, h = v[1:-1].split(',')
                return QSizeF(float(w), float(h))

    def toXml(self, name, value, xw: QXmlStreamWriter):
        t = type(value).__name__
        xw.writeStartElement(name)
        xw.writeAttribute('type', t)
        match t:
            case 'DiagramData':
                for k, v in value.__dict__.items():
                    self.toXml(k, v, xw)
            case 'dict':
                for k, v in value.items():
                    self.toXml(k, v, xw)
            case 'list':
                for n, v in enumerate(value):
                    self.toXml(str(n), v, xw)
            case 'QSizeF':
                xw.writeCharacters(f'({value.width()},{value.height()})')
            case _:
                xw.writeCharacters(str(value))
        xw.writeEndElement()

    def loadXml(self, file):
        xml_reader = QXmlStreamReader(file)
        while not xml_reader.atEnd():
            xml_reader.readNext()
            if xml_reader.isStartElement():
                if xml_reader.name() == f'{APP_NAME} Diagram':
                    self.fromXml(xml_reader)

    def saveXml(self, file):
        # TODO: handle error during XML writing
        xw = QXmlStreamWriter(file)
        xw.setAutoFormatting(True)
        xw.setAutoFormattingIndent(2)
        xw.writeStartDocument()
        for k, v in self.data.__dict__.items():
            self.toXml(k, v, xw)
        xw.writeEndDocument()
        file.close()
