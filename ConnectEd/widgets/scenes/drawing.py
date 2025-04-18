__all__ = ['DrawingScene']

from typing import Optional

from PyQt6.QtCore    import QPointF, QRectF, QSizeF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem
from PyQt6.QtGui     import QUndoStack

from ...core import logger, val2str, str2val

# TODO move Grip to drawForeground?
from ..elements import Grip, element_class_dict

from ... import hub


class DrawingScene(QGraphicsScene):
    # class variables
    XML_ATTRIBUTES         = {'name' : 'str'}
    SYSTEM_FORBIDDEN_ITEMS = [Grip]
    SYSTEM_ALLOWED_ITEMS   = None
    FORBIDDEN_ITEMS        = None # none
    ALLOWED_ITEMS          = None # any

    # instance variables
    name       : str
    wip        : list[QGraphicsItem]
    undo_stack : QUndoStack

    def __init__(
        self    : 'DrawingScene',
        name    : Optional[str] = None,
        extents : Optional[QSizeF] = None
    ) -> None:
        super().__init__()
        if name is None:
            u = 'Untitled' + self.__class__.__name__.replace('Scene', '')
            name = hub.name_counter.get(u)
        if extents is None:
            extents = hub.settings.defaults.extents
        self.name = name
        self.wip  = []
        self.setSceneRect(QRectF(QPointF(0, 0), extents))
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.undo_stack = QUndoStack(self)

    def addItem(self, item : QGraphicsItem) -> None:
        if item in self.SYSTEM_FORBIDDEN_ITEMS:
            raise ValueError(f'Item {item} is forbidden')
        if self.FORBIDDEN_ITEMS is not None:
            if item in self.FORBIDDEN_ITEMS:
                if item not in self.SYSTEM_ALLOWED_ITEMS:
                    raise ValueError(f'Item {item} is forbidden')
        if self.ALLOWED_ITEMS is not None:
            if item not in self.ALLOWED_ITEMS:
                if item not in self.SYSTEM_ALLOWED_ITEMS:
                    raise ValueError(f'Item {item} is not allowed')
        super().addItem(item)

    def toXml(self : 'DrawingScene', xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__.replace('Scene', ''))
        for attr_name, _ in self.XML_ATTRIBUTES.items():
            attr_value = getattr(self, attr_name)
            xw.writeAttribute(attr_name, val2str(attr_value))
        for item in self.items():
            item.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls, xr : QXmlStreamReader) -> 'DrawingScene':
        cls_name = cls.__name__.replace('Scene', '')
        if xr.name() != cls_name:
            raise ValueError(f'Expected {cls_name} element, got {xr.name()}')
        drawing_scene : DrawingScene = cls()
        attributes = xr.attributes()
        for attribute in attributes:
            attr_name = attribute.name()
            attr_value_str = attribute.value()
            if attr_name in drawing_scene.XML_ATTRIBUTES:
                attr_type_name = drawing_scene.XML_ATTRIBUTES[attr_name]
                setattr(
                    drawing_scene, attr_name,
                    str2val(attr_value_str, attr_type_name)
                )
            else:
                raise ValueError(f'Unexpected attribute: {attr_name} value: {attr_value_str}')
        xr.readNext()
        while not (xr.isEndElement() and xr.name() == cls_name):
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                attr_name = xr.name()
                if attr_name in element_class_dict:
                    cls = element_class_dict[attr_name]
                    element = cls.fromXml(xr)
                    drawing_scene.addItem(element)
                else:
                    logger.warning(f"Unexpected element: {attr_name}")
            xr.readNext()
        return drawing_scene
