from typing import Self

from PyQt6.QtGui     import QAction
from PyQt6.QtWidgets import QGraphicsSceneContextMenuEvent

from .....app import logger

from ....menu import Menu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...views.drawing import DrawingView


class ElementMenuMixin:
    def contextMenuEvent(
        self  : Self,
        event : QGraphicsSceneContextMenuEvent
    ) -> None:
        items = self.getMenuItems()  # subclass must provide this method
        if len(items) == 0:
            return
        pos = event.screenPos()
        menu = Menu()
        for item in items:
            if item.startswith("-"):
                menu.addSeparator()
            else:
                from ...views.drawing import getView
                view = getView(pos)
                slot_name = f"ctxMenu{item.replace(' ', '').replace('.', '')}"
                if hasattr(self, slot_name):
                    slot = getattr(self, slot_name)
                    action = QAction(item, menu)
                    action.triggered.connect(
                        lambda checked=False, w=view, s=slot: s(checked, w)
                    )
                    menu.addAction(action)
                else:
                    logger().error(f"{slot_name} missing from {self.__class__.__name__}")
        menu.exec(pos)

    def getMenuItems(self : Self) -> list[str]:
        raise NotImplementedError(f"{self.__class__.__name__} missing getMenuItems method")

    def ctxMenuAppearance(
        self : Self,
        _    : bool,
        view : "DrawingView"
    ) -> None:
        view.editAppearance(self)

    def ctxMenuProperties(
        self : Self,
        _    : bool,
        view : "DrawingView"
    ) -> None:
        view.editProperties(self)
