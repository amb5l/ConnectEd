from enum import Flag, auto

from .actions_file    import ActionsFileMixin
from .actions_edit    import ActionsEditMixin
from .actions_view    import ActionsViewMixin
from .actions_place   import ActionsPlaceMixin
from .actions_options import ActionsOptionsMixin
from .actions_help    import ActionsHelpMixin


class Actions(
    ActionsFileMixin,
    ActionsEditMixin,
    ActionsViewMixin,
    ActionsPlaceMixin,
    ActionsOptionsMixin,
    ActionsHelpMixin
):
    class Context(Flag):
        ALWAYS                 = 0
        DIAGRAM_EXISTS         = auto()
        DIAGRAM_ITEMS_SELECTED = auto()

    def __init__(self, parent):
        self.parent = parent
