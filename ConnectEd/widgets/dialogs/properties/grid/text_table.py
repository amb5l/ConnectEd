from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QWidget

from ....table.row   import TableRow
from ....table.model import TableModel
from ....table.view  import TableView

from ....properties import populatePropertyText

from ....graphics.items.property_text import PropertyTextPending, PropertyTextEdit

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....graphics.items.property_text import PropertyTextItem


_COLUMNS = [
    "Visible",
    "Cleat",
    "X",
    "Y",
    "Rotation",
    "Mirror H",
    "Mirror V",
    "Autoflip",
    "Origin",
    "Align H",
    "Align V",
    "Width",
    "Height",
    "Pad Left",
    "Pad Right",
    "Pad Top",
    "Pad Bottom",
    "Color",
    "Font",
    "Size",
    "Bold",
    "Italic",
    "Underline"
]


class PropertyTextTableWidget(TableView):
    """
    Table for displaying/editing property texts.
    """

    _drafts : list[PropertyTextPending]

    def __init__(
        self   : Self,
        drafts : list[PropertyTextPending],
        parent : QWidget | None = None
    ) -> None:
        # store drafts
        self._drafts = drafts
        # create model
        model = TableModel()
        model.setHorizontalHeaderLabels(_COLUMNS)
        # populate rows
        for draft in self._drafts:
            if draft.state is None:
                continue
            row = TableRow(_COLUMNS)
            populatePropertyText(row, draft)
            model.appendRow(row.cells())
        # superclass init
        super().__init__(model, parent)


    def getEdits(self) -> list[PropertyTextEdit]:
        return []  # TODO: implement
