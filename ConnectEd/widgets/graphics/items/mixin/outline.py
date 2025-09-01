from typing import Self

from .. import OutlinePen


class ElementOutlineMixin:
    outline : OutlinePen

    def initOutline(self : Self):
        self.outline = OutlinePen()