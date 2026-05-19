from typing import Any

from ...core.types import NO_CHANGE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..graphics.items.mixin.presentation import ItemPresentationMixin


def _combinedValue(
    items       : list[ItemPresentationMixin],
    method_name : str
) -> Any:
    result = None
    for item in items:
        method = getattr(item, method_name, None)
        if method is not None:
            value = method()
            result = \
                value if result is None else \
                result if result == value else \
                NO_CHANGE
    return result


__all__ = ["_combinedValue"]
