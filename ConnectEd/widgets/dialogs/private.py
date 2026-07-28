from __future__ import annotations

from typing import Any

from ...core.check import checked
from ...core.types import NO_CHANGE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..graphics.items.mixin.presentation import ItemPresentationMixin


@checked
def _combinedValue(
    items       : list[ItemPresentationMixin],
    method_name : str
) -> Any:
    result = None
    for item in items:
        if (method := getattr(item, method_name, None)) is not None:
            value = method()
            result = \
                value if result is None else \
                result if result == value else \
                NO_CHANGE
    return result


__all__ = ["_combinedValue"]
