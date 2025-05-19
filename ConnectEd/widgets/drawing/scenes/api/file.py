__all__ = ["DrawingApiFileMixin"]

from typing import Optional

from .....core import logger, save, loadItems

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class DrawingApiFileMixin:
    save = save

    @classmethod
    def load(cls, path: str) -> Optional["DrawingScene"]:
        items = loadItems(path)
        for item in items:
            if isinstance(item, cls):
                return item
        logger.warning(f"{cls.__name__} not found in {path}")
        return None
