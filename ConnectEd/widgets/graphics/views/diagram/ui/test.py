from ......core.check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DiagramViewUi


class DiagramViewUiTestMixin:
    @checked
    def test(self : "DiagramViewUi") -> None:
        self._scene.test()
