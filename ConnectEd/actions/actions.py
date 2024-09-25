from actions_file    import ActionsFileMixin
from actions_edit    import ActionsEditMixin
from actions_view    import ActionsViewMixin
from actions_place   import ActionsPlaceMixin
from actions_options import ActionsOptionsMixin
from actions_help    import ActionsHelpMixin

class Actions(
    ActionsFileMixin,
    ActionsEditMixin,
    ActionsViewMixin,
    ActionsPlaceMixin,
    ActionsOptionsMixin,
    ActionsHelpMixin
):
    def __init__(self, parent):
        self.parent = parent
