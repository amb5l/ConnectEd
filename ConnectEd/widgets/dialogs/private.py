from typing import Any

from ...core.types import NO_CHANGE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..graphics.items.mixin.line  import ItemLineMixin
    from ..graphics.items.mixin.fill  import ItemFillMixin
    from ..graphics.items.mixin.quill import ItemQuillMixin


def _combinedValue(
    items       : list["ItemLineMixin | ItemFillMixin | ItemQuillMixin"],
    method_name : str
) -> Any:
    result = None
    for item in items:
        method = getattr(item, method_name)
        value = method()
        result = \
            value if result is None else \
            result if result == value else \
            NO_CHANGE
    return result
