from typing import Self

from .....core.properties import PropertiesMixin

from .host import asDiagramScene

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...items.property_text import PropertyTextItem


class DiagramScenePropertiesMixin(PropertiesMixin):

    def propertyTexts(
        self : Self,
        name : str | None = None
    ) -> list[PropertyTextItem]:
        host = asDiagramScene(self)
        property_texts = []
        for item in host.items():
            if isinstance(item, PropertyTextItem) \
            and item.parentItem() is None:
                property_texts.append(item)
        return property_texts
