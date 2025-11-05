from typing import Self

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsSimpleTextItem, \
                            QWidget, QStyleOptionGraphicsItem, QStyle, QMenu
from PyQt6.QtGui     import QPainter, QAction

from ..properties import PropertySpec, PropertiesMixin

from .mixin         import ItemMixin
from .mixin.pos     import ItemPosMixin
from .mixin.rotate  import ItemRotateMixin
from .mixin.anchor  import ItemRectAnchorPointsMixin
from .mixin.origin  import ItemOriginMixin
from .mixin.quill   import ItemQuillMixin
from .mixin.outline import ItemOutlineMixin
from .mixin.change  import ItemChangeMixin
from .mixin.clone   import ItemCloneMixin
from .mixin.xml     import ItemXmlMixin
from .mixin.menu    import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView


class BaseText(
    ItemMixin,
    ItemPosMixin,
    ItemRotateMixin,
    ItemRectAnchorPointsMixin,
    ItemOriginMixin,
    ItemQuillMixin,
    ItemOutlineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    QGraphicsSimpleTextItem
):
    # class attributes
    _ORIGIN_NAME = "Top Left"
    _PROPERTY_SPECS_POS = \
        ItemOriginMixin._PROPERTY_SPECS_ORIGIN | \
        ItemPosMixin._PROPERTY_SPECS_POS
    _PROPERTY_SPECS_TEXT = {
        "Text" : PropertySpec(
            type_name = "str",
            getter    = lambda self: self.text(),
            setter    = lambda self, value: self.setText(value)
        )
    }
    _PROPERTY_SPECS_APPEARANCE = \
        ItemQuillMixin._PROPERTY_SPECS_QUILL
    _PROPERTY_SPECS = \
        _PROPERTY_SPECS_POS | \
        _PROPERTY_SPECS_TEXT | \
        _PROPERTY_SPECS_APPEARANCE

    def __init__(
        self : Self,
        pos  : QPointF = QPointF(),
        bare : bool = False
    ) -> None:
        QGraphicsSimpleTextItem.__init__(self, "")
        self.initItem(bare=bare)
        self.setPos(pos)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        if not hasattr(self, "_origin"):
            return
        old_origin_scene_pos = self.getOriginScenePos()
        self.updateAnchorPoints()
        new_origin_scene_pos = self.getOriginScenePos()
        delta = old_origin_scene_pos - new_origin_scene_pos
        self._pos = self.pos() + delta
        self.updateOrigin()

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Edit...", view.ui.editText),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editProperties(self))
        ]

    def setText(self : Self, text : str) -> None:
        super().setText(text)
        self.onGeometryChange()

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(self.outline.pen)
            painter.drawRect(self.boundingRect())

    def anchorPointRect(self : Self) -> QRectF:
        return self.boundingRect()

    def moveAnchorPointBy(self : Self, _ : str, delta : QPointF) -> None:
        """Move the entire Text when any keypoint is dragged."""
        self.setPos(self.pos() + delta)
