from ...properties import PropertiesMixin

from . import ItemMixin

from .scene        import ItemSceneMixin
from .handle       import ItemHandlesMixin
from .presentation import ItemPresentationMixin
from .select       import ItemSelectMixin
from .change       import ItemChangeMixin
from .clone        import ItemCloneMixin
from .xml          import ItemXmlMixin
from .menu         import ItemMenuMixin


class PrimaryItemMixin(
    ItemSceneMixin,
    ItemMixin,
    ItemHandlesMixin,
    ItemPresentationMixin,
    ItemSelectMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin
):
    pass
