from __future__ import annotations

from typing import Self


class ItemNamesMixin:
    def settingsName(self : Self) -> str:
        return self.__class__.__name__.removesuffix("Item")

    def resourcesName(self : Self) -> str:
        return self.settingsName()
