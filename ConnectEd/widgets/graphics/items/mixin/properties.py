from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from .....app import logger

from .....core.properties import PropertiesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..property_text import PropertyTextItem, PropertyTextSpec


class ItemPropertiesMixin(PropertiesMixin):
    _PROPERTY_TEXTS : dict[str, PropertyTextSpec]

    def initProperties(self : Self, live : bool) -> None:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        from ..property_text import PropertyTextItem
        super().initProperties(live)
        # initialize property texts
        if hasattr(self, "_PROPERTY_TEXTS"):
            property_names = self.propertyNames()
            for name, spec in self._PROPERTY_TEXTS.items():
                if name not in property_names:
                    logger().error(f"Property {name} does not exist")
                pt = PropertyTextItem(
                    name       = name,
                    cleat      = spec.cleat,
                    pos        = QPointF(spec.x, spec.y),
                    rotation   = spec.rotation,
                    mirror_h   = spec.mirror_h,
                    mirror_v   = spec.mirror_v,
                    autoflip   = spec.autoflip,
                    origin     = spec.origin,
                    align_h    = spec.align_h,
                    align_v    = spec.align_v,
                    width      = spec.width,
                    height     = spec.height,
                    pad_left   = spec.pad_left,
                    pad_right  = spec.pad_right,
                    pad_top    = spec.pad_top,
                    pad_bottom = spec.pad_bottom,
                    color      = spec.color,
                    font       = spec.font,
                    size       = spec.size,
                    bold       = spec.bold,
                    italic     = spec.italic,
                    underline  = spec.underline,
                    fresh      = True,
                    parent     = self
                )
                self.propertySubscribe(name, pt.onTextChanged)

    def propertyTexts(
        self : Self,
        name : str | None = None
    ) -> list[PropertyTextItem]:
        from ..property_text import PropertyTextItem
        from ..handle        import HandleItem
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        property_texts = []
        for child in self.childItems():
            if isinstance(child, PropertyTextItem):
                if name is not None and child.name() != name:
                    continue
                property_texts.append(child)
            elif isinstance(child, HandleItem):
                for h_child in child.childItems():
                    if isinstance(h_child, PropertyTextItem):
                        if name is not None and h_child.name() != name:
                            continue
                        property_texts.append(h_child)
        return property_texts
