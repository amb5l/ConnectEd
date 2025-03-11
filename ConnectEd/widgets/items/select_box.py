from PyQt6.QtCore    import Qt, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPen, QColor

from ...core import Z_TOP

from . import RectPenOnlyItem


class SelectBox(RectPenOnlyItem):
    Z = Z_TOP

    def __init__(self : 'SelectBox') -> None:
        super().__init__()
        self.setVisible(False)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsMovable                        , False )
        self.setFlag( f.ItemIsSelectable                     , False )
        self.setFlag( f.ItemIsFocusable                      , False )
        self.setFlag( f.ItemClipsToShape                     , False )
        self.setFlag( f.ItemClipsChildrenToShape             , False )
        self.setFlag( f.ItemIgnoresTransformations           , False )
        self.setFlag( f.ItemIgnoresParentOpacity             , False )
        self.setFlag( f.ItemDoesntPropagateOpacityToChildren , False )
        self.setFlag( f.ItemStacksBehindParent               , False )
        self.setFlag( f.ItemUsesExtendedStyleOption          , False )
        self.setFlag( f.ItemHasNoContents                    , False )
        self.setFlag( f.ItemSendsGeometryChanges             , False )
        self.setFlag( f.ItemAcceptsInputMethod               , False )
        self.setFlag( f.ItemNegativeZStacksBehindParent      , False )
        self.setFlag( f.ItemIsPanel                          , False )
        self.setFlag( f.ItemSendsScenePositionChanges        , False )
        self.setFlag( f.ItemContainsChildrenInShape          , False )
        self.setZValue(self.Z)

    def boundingRect(self) -> QRectF:
        return self.rect

    # TODO: Implement marching ants effect
    def paint(
        self    : 'SelectBox',
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setCompositionMode(
            QPainter.CompositionMode.RasterOp_SourceXorDestination
        )
        painter.setPen(QPen(QColor(128, 128, 128), 0, Qt.PenStyle.DotLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect)
