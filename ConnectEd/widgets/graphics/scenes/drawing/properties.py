from typing          import Self
from collections.abc import Callable

from ...property   import PropertySpec, Property
from ...properties import PropertiesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..drawing import DrawingScene


class DrawingScenePropertySpec(PropertySpec):
    # owner type = drawing scene
    getter : Callable[["DrawingScene"], str] | str | None  = ""
    setter : Callable[["DrawingScene", str], None] | None  = None


class DrawingScenePropertiesMixin(PropertiesMixin):
    # class attributes
    _PROPERTY_SPECS : dict[str, DrawingScenePropertySpec]

    def initProperties(self : Self) -> None:
        self._properties = {}
        for name, spec in self._PROPERTY_SPECS.items():
            self._properties[name] = Property(
                name,
                spec.getter,
                spec.setter
            )
