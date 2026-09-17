from __future__ import annotations

from typing import Self


class ItemNamesMixin:
    @classmethod
    def settingsName(cls : type[Self]) -> str:
        return cls.__name__.removesuffix("Item")

    @classmethod
    def resourcesName(cls : type[Self]) -> str:
        return cls.settingsName()
