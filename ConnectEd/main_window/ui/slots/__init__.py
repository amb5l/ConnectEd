# build actions from CMD_DEFS and connect to functions in Slots instance
# manage enable/disable state of actions

from inspect         import stack
from functools       import wraps
from PyQt6.QtCore    import pyqtSlot
from PyQt6.QtGui     import QKeySequence
from PyQt6.QtWidgets import QMessageBox

from misc    import getInst
from log     import logger
from canvas  import Canvas
from diagram import Diagram

SK = QKeySequence.StandardKey


def slot(func):
    '''
    Slot function decorator.
    '''
    return pyqtSlot()(func)

def slot_with_main_window(func):
    '''
    Slot function decorator, with main_window.
    '''
    @pyqtSlot()
    @wraps(func)
    def wrapper(self : 'Slots'):
        main_window = self.main_window
        if main_window is None:
            logger.error('No main window')
            return
        r = func(self, main_window)
        main_window.commands.update()
        return r
    return wrapper

def slot_with_sub_window(func):
    '''
    Slot function decorator, with sub_window.
    '''
    @pyqtSlot()
    @wraps(func)
    def wrapper(self : 'Slots'):
        sub_window = getInst(self.main_window.mdi_area.activeSubWindow(), 'SubWindow')
        r = func(self, sub_window)
        self.main_window.commands.update()
        return r
    return wrapper

def slot_with_canvas(func):
    '''
    Slot function decorator, with canvas.
    '''
    @pyqtSlot()
    @wraps(func)
    def wrapper(self : 'Slots'):
        sub_window = getInst(self.main_window.mdi_area.activeSubWindow(), 'SubWindow')
        canvas = getInst(sub_window.canvas, Canvas)
        r = func(self, canvas)
        self.main_window.statusbar.update()
        self.main_window.commands.update()
        return r
    return wrapper

def slot_with_diagram(func):
    '''
    Slot function decorator, with diagram.
    '''
    @pyqtSlot()
    @wraps(func)
    def wrapper(self : 'Slots'):
        sub_window = getInst(self.main_window.mdi_area.activeSubWindow(), 'SubWindow')
        canvas = getInst(sub_window.canvas, Canvas)
        diagram = getInst(canvas.diagram, Diagram)
        r = func(self, diagram)
        self.main_window.commands.update()
        return r
    return wrapper

from .file import SlotsFileMixin
from .view import SlotsViewMixin
from .help import SlotsHelpMixin

'''
Contains all slot functions.
'''
class Slots(
    SlotsFileMixin,
    SlotsViewMixin,
    SlotsHelpMixin
):
    def __init__(self : 'Slots', parent : 'Commands'):
        self.parent = parent # refers to parent Commands instance
        self.main_window = parent.parent

    def todo(self):
        QMessageBox.about(self, "TODO", stack()[1].function)
