from ...graphics.properties import Property, PropertiesMixin

from ...graphics.items.property_text import PropertyTextItem


@dataclass
class PropertyState:
    name : str



PropertyStore = dict[PropertiesMixin, dict[Property, PropertyTextItem]]
