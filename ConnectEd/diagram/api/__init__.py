from PyQt6.QtCore import QSizeF


class DiagramApiMixin:
    def extents(self):
        if self.data is None:
            return None
        elif not (self.data.content or self.data.wip):
            return self.data.size
        # TODO calculate extents
        return QSizeF(0.0, 0.0)
