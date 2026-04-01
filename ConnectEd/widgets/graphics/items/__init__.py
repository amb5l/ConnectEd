from PyQt6.QtWidgets import QGraphicsItem

from ....app import logger

from ....core.utils import registerClass

from .mixin import ItemMixin

# Runtime union so isinstance(..., ItemType) works (e.g. property_text.item()).
ItemType = ItemMixin | QGraphicsItem


def clone(items : list["ItemMixin"]) -> list["ItemMixin"]:
    r = []
    for item in items:
        try:
            r.append(item.clone())
        except Exception as e:
            logger().warning(f"Failed to clone item {item}: {e}")
    return r


_item_classes = {}
registerClass( _item_classes , "SegmentItem"               )
registerClass( _item_classes , "PortItem"                  )
registerClass( _item_classes , "BufGateItem"      , "gate" )
registerClass( _item_classes , "AndGateItem"      , "gate" )
registerClass( _item_classes , "OrGateItem"       , "gate" )
registerClass( _item_classes , "XorGateItem"      , "gate" )
registerClass( _item_classes , "BlockItem"                 )
registerClass( _item_classes , "PropertyTextItem"          )
registerClass( _item_classes , "SymbolPinItem"             )
registerClass( _item_classes , "LineItem"                  )
registerClass( _item_classes , "RectangleItem"             )
registerClass( _item_classes , "EllipseItem"               )
registerClass( _item_classes , "PolylineItem"              )
registerClass( _item_classes , "TextItem"                  )
