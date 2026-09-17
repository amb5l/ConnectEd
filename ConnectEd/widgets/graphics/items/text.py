from __future__ import annotations

from typing      import Self
from dataclasses import dataclass

from ....core.types import NoChange, NO_CHANGE

from .role import DecorativeItem

from .base_text import BaseTextItem, \
                       BaseTextAppearanceState, BaseTextAppearanceChange


class TextItem(DecorativeItem, BaseTextItem):
    pass


@dataclass
class TextState(BaseTextAppearanceState):
    text  : str
    block : bool

    @classmethod
    def fromItem(cls, item : TextItem) -> Self:
        inst = super().fromItem(item)
        inst.text = item.text()
        inst.block = item.block()
        return inst


@dataclass
class TextChange(BaseTextAppearanceChange):
    text  : str           | NoChange = NO_CHANGE
    block : bool          | NoChange = NO_CHANGE
