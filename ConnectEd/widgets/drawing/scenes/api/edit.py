from typing import Self

from .... import Element, cmdElements, AppearanceDialog

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class cmdEditAppearance(cmdElements):
    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[Element]
    ):
        super().__init__(scene, elements)
        # to be continued

class DrawingSceneApiEditMixin:
    def editAppearance(self : "DrawingScene", elements : list[Element]) -> None:
        dialog = AppearanceDialog(self, elements)
        if dialog.exec():
            choice = dialog.getChoice()
            # to be continued
