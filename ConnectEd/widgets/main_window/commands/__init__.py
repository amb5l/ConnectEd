from .slots         import Slots
from .actions       import Actions
from ....core.utils import connect_actions_to_slots

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....widgets.main_window import MainWindow

class Commands:
    slots   : Slots
    actions : Actions

    def __init__(self : 'Commands', main_window : 'MainWindow'):
        self.slots = Slots(main_window)
        self.actions = Actions(main_window)
        connect_actions_to_slots(self.actions, self.slots)
        pass
