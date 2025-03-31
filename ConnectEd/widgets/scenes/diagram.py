__all__ = ['DiagramScene']

from . import DrawingScene

from ..elements import Paper, Border

class DiagramScene(DrawingScene):
    SYSTEM_ALLOWED_ITEMS = DrawingScene.SYSTEM_ALLOWED_ITEMS + [Paper, Border]
